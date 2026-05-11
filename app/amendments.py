"""Contract amendment + what-if simulator.

Given the recruiter_pushback items from the checklist, generate an "amended"
contract by inserting an addendum that replaces or removes the offending
clauses. Then re-run the panel and compare urgency.
"""
from __future__ import annotations

from typing import Any


def amend_contract(original_text: str, amendments: list[dict[str, Any]]) -> str:
    """Append an addendum that replaces or removes specific clauses.

    Each amendment is a dict like:
      {"clause_number": 12, "ask": "Remove passport-retention clause",
       "suggested_text": "Worker retains custody of passport"}

    We don't try to edit the original text — we append an unambiguous
    ADDENDUM section. LLMs read this naturally as a contract revision.
    """
    if not amendments:
        return original_text

    lines = ["", "", "── ADDENDUM (worker pre-signing requests) ──", ""]
    for a in amendments:
        if not isinstance(a, dict):
            continue
        cnum = a.get("clause_number", "?")
        ask = a.get("ask", "").strip()
        suggested = a.get("suggested_text", "").strip()
        lines.append(f"Clause {cnum}: WORKER REQUESTS REVISION.")
        if ask:
            lines.append(f"  Request: {ask}")
        if suggested:
            lines.append(f"  Replace with: \"{suggested}\"")
        lines.append("")
    lines.append("Assume the Employer has agreed to all of the above amendments.")
    lines.append("Treat the revised clauses as authoritative; the original clauses")
    lines.append("are superseded where conflicts arise.")
    lines.append("")
    return original_text + "\n".join(lines)


def urgency_delta(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    """Compute a comparison summary for the UI."""
    u_before = int(before.get("final_urgency_score", 0))
    u_after = int(after.get("final_urgency_score", 0))
    reel_before = len(before.get("disagreement_reel") or [])
    reel_after = len(after.get("disagreement_reel") or [])
    return {
        "urgency_before": u_before,
        "urgency_after": u_after,
        "urgency_drop": u_before - u_after,
        "reel_before": reel_before,
        "reel_after": reel_after,
        "verdict": _verdict_label(u_before, u_after),
    }


def _verdict_label(before: int, after: int) -> str:
    drop = before - after
    if drop >= 4:
        return "Dramatic improvement — worker is meaningfully safer."
    if drop >= 2:
        return "Real improvement, but residual risk remains."
    if drop >= 1:
        return "Modest improvement — most risks unaddressed."
    if drop == 0:
        return "No improvement — these amendments don't move the needle."
    return "Counter-intuitive: amended contract scored worse (verify)."
