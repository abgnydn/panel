"""Disk-backed result cache.

Hashes (contract_text + situation + dest + origin + l1) → caches the full
panel result as JSON. Massive speedup when iterating on the UI or re-running
the same demo case.

Set PANEL_CACHE=0 to disable.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

CACHE_DIR = Path(__file__).parent.parent / ".panel-cache"
CACHE_DIR.mkdir(exist_ok=True)


def disabled() -> bool:
    return os.environ.get("PANEL_CACHE", "1") == "0"


# Bump SCHEMA_VERSION whenever the moderator response shape changes so stale
# entries from older deploys don't get served to a frontend that expects new fields.
SCHEMA_VERSION = "v4"


def key(contract_text: str, situation: str, destination: str,
        origin: str, worker_l1: str) -> str:
    h = hashlib.sha256()
    h.update(SCHEMA_VERSION.encode("utf-8"))
    h.update(b"\x00")
    for part in (contract_text, situation, destination, origin, worker_l1):
        h.update((part or "").encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()[:24]


def get(cache_key: str) -> dict[str, Any] | None:
    if disabled():
        return None
    path = CACHE_DIR / f"{cache_key}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def put(cache_key: str, result: dict[str, Any]) -> None:
    if disabled():
        return
    path = CACHE_DIR / f"{cache_key}.json"
    try:
        path.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def clear() -> int:
    """Wipe the cache. Returns number of entries removed."""
    n = 0
    for p in CACHE_DIR.glob("*.json"):
        p.unlink()
        n += 1
    return n
