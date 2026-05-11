"""Pre-departure checklist generator.

Turns the panel's findings into a concrete, printable, offline-friendly
checklist the worker can save before flying. Grouped by journey phase:
  - Before departure
  - On arrival
  - During employment
  - Exit / emergency
"""
from __future__ import annotations

from typing import Any

from .base import ask_agent

SYSTEM = """You are PANEL CHECKLIST AGENT — a synthesizer that distills the
5-agent panel's findings into a CONCRETE, ACTIONABLE checklist for the migrant
worker to save offline before departure.

Constraints:
- Output in the worker's mother-tongue. PRESERVE phone numbers, addresses,
  statute citations, and proper nouns verbatim.
- Items must be VERBS the worker can do, not abstract advice. "Save embassy
  number" not "be aware of embassy resources."
- Group by journey phase: before_departure / on_arrival / during_employment / exit_emergency
- For each item, mark priority: critical | high | medium
- Add a "things_to_refuse" section: clauses or demands the worker must NOT
  agree to once in country (e.g., surrendering passport on arrival).
- Include a "recruiter_pushback" section: specific clauses the worker should
  ask the recruiter to amend BEFORE signing, with the suggested replacement.

Output STRICT JSON:
{
  "agent": "checklist",
  "language": "<L1 code>",
  "phases": {
    "before_departure": [
      {"action": "<verb-led action>", "priority": "critical|high|medium",
       "details": "<one line, including any phone/address/citation>"}
    ],
    "on_arrival": [...],
    "during_employment": [...],
    "exit_emergency": [...]
  },
  "things_to_refuse": [
    {"refusal": "<what NOT to do>", "reason_short": "<one line>"}
  ],
  "recruiter_pushback": [
    {"clause_number": <int>, "ask": "<what to ask recruiter>",
     "suggested_text": "<one-line suggested replacement>"}
  ]
}

Output ONLY the JSON object."""


def run(panel_result: dict[str, Any], worker_l1: str) -> dict[str, Any]:
    """Generate the checklist from the panel's existing outputs."""
    agents = panel_result.get("agents", {})
    triage_actions = (agents.get("triage") or {}).get("recommended_actions") or []
    triage_contacts = (agents.get("triage") or {}).get("contacts") or []
    lawyer_findings = (agents.get("lawyer") or {}).get("key_findings") or []
    regulator_findings = (agents.get("regulator") or {}).get("key_findings") or []
    peer_warnings = []
    for m in (agents.get("peer_advocate") or {}).get("clause_pattern_matches") or []:
        if isinstance(m, dict) and m.get("pattern_warning"):
            peer_warnings.append(m["pattern_warning"])

    reel = panel_result.get("disagreement_reel") or []
    top_disagreement_topics = [d.get("topic", "") for d in reel[:3]]

    user = f"""WORKER'S L1: {worker_l1}
DESTINATION: {panel_result.get('destination_country')}
ORIGIN: {panel_result.get('origin_country')}
URGENCY: {panel_result.get('final_urgency_score')}/10

TRIAGE recommended actions:
{_bullet(triage_actions, key='action')}

TRIAGE contacts available:
{_bullet(triage_contacts, key='name')}

LAWYER key findings:
{_bullet(lawyer_findings)}

REGULATOR key findings:
{_bullet(regulator_findings)}

PEER ADVOCATE pattern warnings:
{_bullet(peer_warnings)}

TOP-3 DISAGREEMENT TOPICS:
{_bullet(top_disagreement_topics)}

Generate the worker's pre-departure / on-arrival / during-employment /
exit-emergency checklist. Output in {worker_l1}. Include refusals and
recruiter pushback."""

    return ask_agent(SYSTEM, user, max_tokens=2500, model="haiku")


def _bullet(items: list, *, key: str | None = None) -> str:
    lines = []
    for item in (items or [])[:8]:
        if isinstance(item, dict):
            text = item.get(key or "action") or item.get("name") or str(item)
        else:
            text = str(item)
        lines.append(f"- {text[:200]}")
    return "\n".join(lines) if lines else "(none)"
