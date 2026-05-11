"""Persistence layer for Panel.

Local dev: SQLite at ~/panel/.panel.db (auto-created).
Production: would point to Lakebase Postgres via psycopg.

Schema mirrors lakebase/001_schema.sql, simplified for SQLite (no vector,
no pgvector — Peer Advocate uses keyword/category matching locally).
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

DB_PATH = Path(__file__).parent.parent / ".panel.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS workers (
    id TEXT PRIMARY KEY,
    country_of_origin TEXT NOT NULL,
    destination_country TEXT,
    native_language TEXT NOT NULL,
    age_range TEXT,
    consent_archive INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    worker_id TEXT REFERENCES workers(id),
    started_at TEXT DEFAULT CURRENT_TIMESTAMP,
    ended_at TEXT,
    contract_text TEXT,
    detected_language TEXT,
    situation_text TEXT
);

CREATE TABLE IF NOT EXISTS agent_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT REFERENCES sessions(id),
    agent TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    confidence REAL,
    latency_ms INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recommendations (
    id TEXT PRIMARY KEY,
    session_id TEXT REFERENCES sessions(id),
    urgency_score INTEGER,
    summary_l1 TEXT NOT NULL,
    summary_en TEXT NOT NULL,
    action_items TEXT NOT NULL,
    contacts TEXT,
    disagreements TEXT,
    legal_disclaimer_l1 TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sessions_started ON sessions(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_messages_session ON agent_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_urgency ON recommendations(urgency_score DESC);
"""


@contextmanager
def conn() -> Iterator[sqlite3.Connection]:
    c = sqlite3.connect(str(DB_PATH))
    c.row_factory = sqlite3.Row
    try:
        yield c
        c.commit()
    finally:
        c.close()


def init() -> None:
    with conn() as c:
        c.executescript(_SCHEMA)


def create_worker(country_of_origin: str, destination_country: str,
                  native_language: str) -> str:
    wid = str(uuid.uuid4())
    with conn() as c:
        c.execute(
            "INSERT INTO workers(id, country_of_origin, destination_country, native_language) VALUES(?,?,?,?)",
            (wid, country_of_origin, destination_country, native_language),
        )
    return wid


def create_session(worker_id: str, contract_text: str, situation_text: str,
                   detected_language: str | None = None) -> str:
    sid = str(uuid.uuid4())
    with conn() as c:
        c.execute(
            "INSERT INTO sessions(id, worker_id, contract_text, situation_text, detected_language) VALUES(?,?,?,?,?)",
            (sid, worker_id, contract_text, situation_text, detected_language),
        )
    return sid


def log_agent(session_id: str, agent: str, role: str, content: dict[str, Any],
              confidence: float | None = None, latency_ms: int | None = None) -> None:
    with conn() as c:
        c.execute(
            "INSERT INTO agent_messages(session_id, agent, role, content, confidence, latency_ms) VALUES(?,?,?,?,?,?)",
            (session_id, agent, role, json.dumps(content), confidence, latency_ms),
        )


def save_recommendation(session_id: str, urgency_score: int, summary_l1: str,
                        summary_en: str, action_items: list, contacts: list,
                        disagreements: list, disclaimer_l1: str) -> str:
    rid = str(uuid.uuid4())
    with conn() as c:
        c.execute(
            """INSERT INTO recommendations(id, session_id, urgency_score, summary_l1, summary_en,
               action_items, contacts, disagreements, legal_disclaimer_l1) VALUES(?,?,?,?,?,?,?,?,?)""",
            (rid, session_id, urgency_score, summary_l1, summary_en,
             json.dumps(action_items), json.dumps(contacts),
             json.dumps(disagreements), disclaimer_l1),
        )
    return rid


def end_session(session_id: str) -> None:
    with conn() as c:
        c.execute("UPDATE sessions SET ended_at=? WHERE id=?",
                  (datetime.utcnow().isoformat(), session_id))


def recent_sessions(limit: int = 100) -> list[dict[str, Any]]:
    with conn() as c:
        rows = c.execute(
            """SELECT s.id, s.started_at, w.country_of_origin, w.destination_country,
                      w.native_language, r.urgency_score, r.summary_en
               FROM sessions s
               LEFT JOIN workers w ON s.worker_id = w.id
               LEFT JOIN recommendations r ON r.session_id = s.id
               ORDER BY s.started_at DESC LIMIT ?""",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def urgent_sessions_24h() -> list[dict[str, Any]]:
    with conn() as c:
        rows = c.execute(
            """SELECT s.id, s.started_at, w.country_of_origin, w.destination_country,
                      w.native_language, r.urgency_score, r.summary_en
               FROM sessions s
               JOIN workers w ON s.worker_id = w.id
               JOIN recommendations r ON r.session_id = s.id
               WHERE r.urgency_score >= 7
                 AND datetime(s.started_at) >= datetime('now', '-1 day')
               ORDER BY r.urgency_score DESC, s.started_at DESC""",
        ).fetchall()
    return [dict(r) for r in rows]


# Initialize on import
init()
