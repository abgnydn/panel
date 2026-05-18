"""Genie Space chat client.

Multi-turn conversation against the panel Genie Space (`labor_codes`,
`ilo_standards`, `case_archive`, `embassy_directory`). Each call returns
not just the answer but a 3-element list of AI-generated follow-ups so
the v2 chat UI can suggest the next question.

Flow:
  - First call: pass question only. Server creates a new conversation,
    fires the question, polls until done, returns answer + a fresh
    conversation_id.
  - Subsequent calls: pass {question, conversation_id}. Genie keeps the
    earlier turns as context.

Follow-up suggestions come from a small Mosaic AI call that takes the
last exchange and asks a Qwen 80B model to propose three short, plausible
next questions a worker would ask.
"""
from __future__ import annotations

import json
import os
import time
from datetime import timedelta
from typing import Any

GENIE_SPACE_ID = os.environ.get("GENIE_SPACE_ID", "01f15002d16915548191d84deb5267ed")
MAX_POLL = timedelta(seconds=60)
SUGGEST_MODEL = "databricks-qwen3-next-80b-a3b-instruct"

SUGGESTION_PROMPT = """You suggest follow-up questions for a migrant worker
chatting with an AI that has access to:
- Destination-country labor codes (passport / hours / deductions / rest days / etc.)
- ILO conventions C97/C143/C181/C189/C190 + ASEAN standard contract
- An anonymised case archive (which clauses cluster with bad outcomes)
- Embassy and NGO contact directory

Given the last exchange below, propose THREE specific, useful follow-up
questions the worker might ask next. Each should be a single sentence and
answerable from the data above. Return ONLY a JSON array of three strings.
No prose, no markdown.

Example output:
["What if the recruiter refuses?", "Compare with Malaysia.", "Show me cases that ended badly."]"""


def ask(question: str, conversation_id: str | None = None) -> dict[str, Any]:
    """Single turn against the Genie Space.

    Returns:
      {
        "question":         "<input>",
        "text":             "<Genie's NL answer>",
        "sql":              "<SQL Genie ran, if any>",
        "columns":          ["...", "..."],
        "rows":             [[...], [...]],
        "conversation_id":  "...",   # reuse on next call to continue
        "message_id":       "...",
        "suggested_questions": ["...", "...", "..."],
        "latency_ms":       1234
      }
    """
    from databricks.sdk import WorkspaceClient

    from databricks.sdk.service.dashboards import MessageStatus

    t0 = time.time()
    w = WorkspaceClient()

    def _id_of(obj) -> str:
        # Older SDK exposes only `.id`; newer also has `.message_id`. Use either.
        return getattr(obj, "message_id", None) or getattr(obj, "id", None) or ""

    # Start the request without using *_and_wait — the wait helpers raise an
    # OperationFailed on MessageStatus.FAILED, which discards the real
    # error.error / error.type fields we need to show the user.
    if conversation_id:
        waiter = w.genie.create_message(
            space_id=GENIE_SPACE_ID,
            conversation_id=conversation_id,
            content=question,
        )
        conv_id = conversation_id
        resp = getattr(waiter, "response", waiter)
        message_id = _id_of(resp) or _id_of(waiter)
    else:
        waiter = w.genie.start_conversation(space_id=GENIE_SPACE_ID, content=question)
        resp = getattr(waiter, "response", waiter)
        conv_id = (getattr(resp, "conversation_id", None)
                   or getattr(waiter, "conversation_id", None) or "")
        message_id = _id_of(resp) or _id_of(waiter)

    # Poll manually until we hit a terminal state.
    TERMINAL = {MessageStatus.COMPLETED, MessageStatus.FAILED,
                MessageStatus.CANCELLED, MessageStatus.QUERY_RESULT_EXPIRED}
    deadline = time.time() + MAX_POLL.total_seconds()
    msg = None
    while time.time() < deadline:
        msg = w.genie.get_message(
            space_id=GENIE_SPACE_ID,
            conversation_id=conv_id,
            message_id=message_id,
        )
        if msg.status in TERMINAL:
            break
        time.sleep(0.8)

    if msg is None or msg.status != MessageStatus.COMPLETED:
        # Surface the real error so the user (and future-us) knows what to fix.
        err_type = getattr(msg.error, "type", None) if msg and msg.error else None
        err_text = getattr(msg.error, "error", None) if msg and msg.error else None
        friendly = _friendly_error(msg.status if msg else None, err_type, err_text)
        return {
            "question": question,
            "text": friendly,
            "sql": "",
            "columns": [],
            "rows": [],
            "conversation_id": conv_id,
            "message_id": message_id,
            "suggested_questions": _default_suggestions(),
            "latency_ms": int((time.time() - t0) * 1000),
            "error": True,
            "error_type": str(err_type) if err_type else None,
            "status": str(msg.status) if msg else "timeout",
        }

    text_parts: list[str] = []
    sql = ""
    columns: list[str] = []
    rows: list[list[Any]] = []

    for att in (msg.attachments or []):
        if att.text and att.text.content:
            text_parts.append(att.text.content)
        if att.query:
            sql = att.query.query or ""
            try:
                qr = w.genie.get_message_attachment_query_result(
                    space_id=GENIE_SPACE_ID,
                    conversation_id=getattr(msg, "conversation_id", conv_id),
                    message_id=_id_of(msg) or message_id,
                    attachment_id=getattr(att, "attachment_id", None) or getattr(att, "id", None),
                )
                if qr.statement_response:
                    sr = qr.statement_response
                    if sr.manifest and sr.manifest.schema and sr.manifest.schema.columns:
                        columns = [c.name for c in sr.manifest.schema.columns]
                    if sr.result and sr.result.data_array:
                        rows = sr.result.data_array
            except Exception as e:  # noqa: BLE001
                text_parts.append(f"(query result fetch failed: {e})")

    answer_text = "\n\n".join(text_parts) or "(Genie returned no text.)"
    suggestions = _suggest_follow_ups(question, answer_text, w)

    return {
        "question": question,
        "text": answer_text,
        "sql": sql,
        "columns": columns,
        "rows": rows,
        "conversation_id": msg.conversation_id,
        "message_id": msg.message_id,
        "suggested_questions": suggestions,
        "latency_ms": int((time.time() - t0) * 1000),
    }


def _suggest_follow_ups(question: str, answer_text: str, w) -> list[str]:
    """Tiny Mosaic AI call: give it the last exchange, get 3 plausible
    follow-ups. Returns a default set if the call or parsing fails."""
    from databricks.sdk.service.serving import ChatMessage, ChatMessageRole

    user_msg = (
        f"WORKER ASKED:\n{question}\n\n"
        f"ASSISTANT ANSWERED:\n{answer_text[:1200]}\n\n"
        "Suggest 3 follow-ups as a JSON array of three strings, nothing else."
    )
    try:
        resp = w.serving_endpoints.query(
            name=SUGGEST_MODEL,
            messages=[
                ChatMessage(role=ChatMessageRole.SYSTEM, content=SUGGESTION_PROMPT),
                ChatMessage(role=ChatMessageRole.USER, content=user_msg),
            ],
            max_tokens=300,
            temperature=0.4,
        )
        text = (resp.choices[0].message.content if resp.choices and resp.choices[0].message
                else "[]")
        text = text.strip()
        # Strip ``` fences if present
        if text.startswith("```"):
            text = text.strip("`")
            if text.lower().startswith("json"):
                text = text[4:]
            text = text.strip()
        parsed = json.loads(text)
        if isinstance(parsed, list) and all(isinstance(x, str) for x in parsed):
            return [s.strip() for s in parsed[:3] if s.strip()]
    except Exception:
        pass
    return _default_suggestions()


def _default_suggestions() -> list[str]:
    return [
        "How many cases in the archive ended with the worker returning early?",
        "Show all 24-hour embassy hotlines for Philippine workers.",
        "Which destination countries have the highest abuse-report rate?",
    ]


def _friendly_error(status, err_type, err_text: str | None) -> str:
    """Translate Genie's error envelope into something useful in the chat."""
    type_str = str(err_type) if err_type else ""
    detail = f"\n\nDetails: {err_text}" if err_text else ""

    if "NO_TABLES_TO_QUERY" in type_str:
        return ("Genie says it has no tables to query in this Space. "
                "Open the Genie Space settings and add the panel tables "
                "(labor_codes, ilo_standards, case_archive, embassy_directory)." + detail)
    if "INVALID_SQL_UNKNOWN_TABLE" in type_str or "INVALID_TABLE_IDENTIFIER" in type_str:
        return ("Genie tried to query a table that doesn't exist in this Space's catalog/schema. "
                "Check the Space's data sources." + detail)
    if "UC_SCHEMA" in type_str:
        return ("Genie couldn't read the Unity Catalog schema. "
                "Verify the Space has read permission on the panel schema." + detail)
    if "CONTEXT_EXCEEDED" in type_str or "EXCEEDED_MAX_TOKEN" in type_str:
        return ("That question is too long for Genie's context window. "
                "Try a shorter, more focused question." + detail)
    if "RATE_LIMIT" in type_str:
        return ("Genie is rate-limited right now — wait 30 seconds and try again." + detail)
    if "GENERATED_SQL_QUERY_TOO_LONG" in type_str or "DESCRIBE_QUERY" in type_str:
        return ("Genie generated SQL but couldn't validate it against the schema. "
                "Try rephrasing — fewer joins or aggregations." + detail)
    if str(status).endswith("CANCELLED"):
        return ("Genie cancelled the request." + detail)
    if str(status) == "timeout":
        return ("Genie didn't respond within 60 seconds. Try again or rephrase." + detail)

    return (f"Genie couldn't complete this question (status: {status}, error: {type_str}). "
            "Try a simpler, more data-shaped question — counts, lists, or comparisons "
            "across rows in labor_codes / ilo_standards / case_archive / embassy_directory." + detail)
