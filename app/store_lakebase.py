"""Lakebase-backed store — drop-in replacement for app/store.py when running
inside the Databricks workspace.

Same interface as store.py (create_worker, create_session, log_agent,
save_recommendation, end_session, recent_sessions, urgent_sessions_24h),
so the agent moderator and dashboard code call either one with no diff.

Connection uses Databricks OAuth (WorkspaceClient.database.generate_database_credential)
as the Postgres password — token refreshes hourly. A small wrapper caches
the token and rotates before expiry.
"""
from __future__ import annotations

import json
import os
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Iterator

import psycopg
from databricks.sdk import WorkspaceClient

INSTANCE_NAME = os.environ.get("PANEL_LAKEBASE", "panel-db")
DB_NAME = os.environ.get("PANEL_LAKEBASE_DB", "databricks_postgres")

_TOKEN: dict[str, Any] = {"token": None, "expires_at": 0.0, "host": None, "user": None}


def _refresh_credentials() -> None:
    """Generate / rotate a Lakebase OAuth credential (~1h lifetime)."""
    w = WorkspaceClient()
    inst = w.database.get_database_instance(name=INSTANCE_NAME)
    cred = w.database.generate_database_credential(
        instance_names=[INSTANCE_NAME],
        request_id=f"panel-{int(time.time())}",
    )
    _TOKEN["token"] = cred.token
    _TOKEN["expires_at"] = time.time() + 50 * 60   # rotate ~10 min before token TTL
    _TOKEN["host"] = inst.read_write_dns
    _TOKEN["user"] = w.current_user.me().user_name


def _dsn() -> str:
    if not _TOKEN["token"] or time.time() > _TOKEN["expires_at"]:
        _refresh_credentials()
    return (
        f"host={_TOKEN['host']} "
        f"dbname={DB_NAME} "
        f"user={_TOKEN['user']} "
        f"password={_TOKEN['token']} "
        f"sslmode=require"
    )


@contextmanager
def conn() -> Iterator[psycopg.Connection]:
    c = psycopg.connect(_dsn(), autocommit=True)
    try:
        yield c
    finally:
        c.close()


# ---------------------------------------------------------------------------
# Public API — mirrors store.py
# ---------------------------------------------------------------------------
def init() -> None:
    """Lakebase schema is applied by scripts/lakebase_setup.py separately —
    this is a no-op so the import-time .init() call in store.py is safe."""
    pass


def create_worker(country_of_origin: str, destination_country: str,
                  native_language: str) -> str:
    wid = str(uuid.uuid4())
    with conn() as c, c.cursor() as cur:
        cur.execute(
            "INSERT INTO workers(id, country_of_origin, destination_country, native_language) "
            "VALUES (%s, %s, %s, %s)",
            (wid, country_of_origin, destination_country, native_language),
        )
    return wid


def create_session(worker_id: str, contract_text: str, situation_text: str,
                   detected_language: str | None = None) -> str:
    sid = str(uuid.uuid4())
    with conn() as c, c.cursor() as cur:
        cur.execute(
            "INSERT INTO sessions(id, worker_id, contract_text, situation_text, detected_language) "
            "VALUES (%s, %s, %s, %s, %s)",
            (sid, worker_id, contract_text, situation_text, detected_language),
        )
    return sid


def log_agent(session_id: str, agent: str, role: str, content: dict[str, Any],
              confidence: float | None = None, latency_ms: int | None = None) -> None:
    with conn() as c, c.cursor() as cur:
        cur.execute(
            "INSERT INTO agent_messages(session_id, agent, role, content, confidence, latency_ms) "
            "VALUES (%s, %s, %s, %s::jsonb, %s, %s)",
            (session_id, agent, role, json.dumps(content), confidence, latency_ms),
        )


def save_recommendation(session_id: str, urgency_score: int, summary_l1: str,
                        summary_en: str, action_items: list, contacts: list,
                        disagreements: list, disclaimer_l1: str) -> str:
    rid = str(uuid.uuid4())
    with conn() as c, c.cursor() as cur:
        cur.execute(
            """INSERT INTO recommendations(id, session_id, urgency_score, summary_l1,
                summary_en, action_items, contacts, disagreements, legal_disclaimer_l1)
               VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb, %s)""",
            (rid, session_id, urgency_score, summary_l1, summary_en,
             json.dumps(action_items), json.dumps(contacts),
             json.dumps(disagreements), disclaimer_l1),
        )
    return rid


def end_session(session_id: str) -> None:
    with conn() as c, c.cursor() as cur:
        cur.execute("UPDATE sessions SET ended_at=%s WHERE id=%s",
                    (datetime.now(timezone.utc), session_id))


def recent_sessions(limit: int = 100) -> list[dict[str, Any]]:
    with conn() as c, c.cursor() as cur:
        cur.execute(
            """SELECT s.id, s.started_at, w.country_of_origin, w.destination_country,
                      w.native_language, r.urgency_score, r.summary_en
               FROM sessions s
               LEFT JOIN workers w ON s.worker_id = w.id
               LEFT JOIN recommendations r ON r.session_id = s.id
               ORDER BY s.started_at DESC LIMIT %s""",
            (limit,),
        )
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def urgent_sessions_24h() -> list[dict[str, Any]]:
    with conn() as c, c.cursor() as cur:
        cur.execute("SELECT * FROM v_urgent_sessions_24h")
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]
