"""Genie Space client.

Thin wrapper over the Databricks SDK's Genie surface. Drives a "Conversation
Manager" pattern: each /api/genie/query call gets a fresh conversation,
fires one question, polls for completion, returns the natural-language
answer + the SQL it ran + the result rows.

The Space ID is fixed at deploy time via the GENIE_SPACE_ID env var so the
FastAPI server doesn't need to know about workspace URLs or auth keys.
"""
from __future__ import annotations

import os
import time
from typing import Any

GENIE_SPACE_ID = os.environ.get("GENIE_SPACE_ID", "01f15002d16915548191d84deb5267ed")
MAX_POLL_S = 60
POLL_INTERVAL_S = 1.5


def ask(question: str) -> dict[str, Any]:
    """Send `question` to the Genie Space and return a structured answer.

    Return shape:
      {
        "question":       "<the input>",
        "text":           "<Genie's natural-language answer>",
        "sql":            "<the SQL Genie generated, if any>",
        "columns":        ["...", "..."],
        "rows":           [[...], [...]],
        "conversation_id":"...",
        "message_id":     "...",
        "latency_ms":     1234
      }
    """
    from databricks.sdk import WorkspaceClient

    t0 = time.time()
    w = WorkspaceClient()

    # 1. Start conversation + first message
    conv = w.genie.start_conversation_and_wait(
        space_id=GENIE_SPACE_ID,
        content=question,
        timeout=__import__("datetime").timedelta(seconds=MAX_POLL_S),
    )

    # `conv` is a GenieMessage when wait completes
    msg = conv
    text_parts: list[str] = []
    sql = ""
    columns: list[str] = []
    rows: list[list[Any]] = []

    for att in (msg.attachments or []):
        # text attachment
        if att.text and att.text.content:
            text_parts.append(att.text.content)
        # query attachment
        if att.query:
            sql = att.query.query or ""
            # Fetch query result
            try:
                qr = w.genie.get_message_attachment_query_result(
                    space_id=GENIE_SPACE_ID,
                    conversation_id=msg.conversation_id,
                    message_id=msg.message_id,
                    attachment_id=att.attachment_id,
                )
                if qr.statement_response and qr.statement_response.result:
                    manifest = qr.statement_response.manifest
                    if manifest and manifest.schema and manifest.schema.columns:
                        columns = [c.name for c in manifest.schema.columns]
                    data = qr.statement_response.result.data_array or []
                    rows = data
            except Exception as e:
                text_parts.append(f"(query result fetch failed: {e})")

    return {
        "question": question,
        "text": "\n\n".join(text_parts) or "(Genie returned no text.)",
        "sql": sql,
        "columns": columns,
        "rows": rows,
        "conversation_id": msg.conversation_id,
        "message_id": msg.message_id,
        "latency_ms": int((time.time() - t0) * 1000),
    }
