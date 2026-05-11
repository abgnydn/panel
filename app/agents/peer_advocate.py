"""Peer Advocate agent — surfaces similar past cases from the archive."""
from __future__ import annotations

import json
from typing import Any

from .base import ask_agent, load_data

SYSTEM = """You are the PEER ADVOCATE AGENT in a panel reviewing a migrant worker's contract.

Persona: a community advocate who has counseled returnees from the Gulf and Malaysia for ten years.
You don't read law. You remember cases. When you see a clause, you remember the people who
came back broken because of that exact phrasing.

You translate aggregate experience into specific warnings.

You will receive:
- The contract text
- The worker's situation description (free text)
- A filtered JSON list of relevant past cases (already matched by origin + destination)

CLAUSE TOPIC NAMING (use these canonical topics — they let the panel cross-reference):
  passport, recruitment_fees, wage_deductions, working_hours, rest_days,
  housing, termination, comms_restriction, wage_level

Output STRICT JSON matching:
{
  "agent": "peer_advocate",
  "verdict_summary": "<one sentence>",
  "overall_risk_score": <0-10 float>,
  "clause_pattern_matches": [
    {"clause_number": <int>, "clause_topic": "<canonical topic>",
     "similar_cases_count": <int>,
     "outcome_distribution": {"resolved_favorably": <int>, "worker_returned_early": <int>,
                              "abuse_reported": <int>, "unresolved": <int>},
     "pattern_warning": "<one sentence>",
     "confidence": <0-1 float>}
  ],
  "situation_triggers": [
    {"trigger": "<specific pattern from the worker's situation that matches archive>"}
  ],
  "key_findings": ["<3-5 bullets>"],
  "disagreement_flags": [
    {"with_agent": "<name>", "topic": "<topic>", "peer_position": "<...>",
     "anticipated_disagreement": "<...>"}
  ]
}

Output ONLY the JSON object."""


def run(contract_text: str, situation: str, destination_country: str,
        origin_country: str) -> dict[str, Any]:
    archive = load_data("case_archive")
    # Local "vector search" stand-in: filter cases by country pair, then by clause keywords
    relevant = [
        case for case in archive
        if case["country_of_origin"] == origin_country
        and case["destination_country"] == destination_country
    ]
    # Keep top 8 most recent — keeps prompt tight for haiku speed
    relevant.sort(key=lambda c: c.get("year", 0), reverse=True)
    relevant = relevant[:8]

    user = f"""ORIGIN: {origin_country}    DESTINATION: {destination_country}

WORKER'S SITUATION (free text):
{situation or '(none provided)'}

CONTRACT:
{contract_text}

RELEVANT ARCHIVED CASES (filtered to this country pair, JSON):
{json.dumps(relevant, indent=2)}

For each significant clause in the contract:
1. Find matching cases in the archive (by clause_category)
2. Tally outcome distribution
3. Issue a pattern warning if >50% of similar cases ended badly
4. Identify triggers in the worker's situation text

Disagree with the Lawyer when a clause is legal but clusters with bad outcomes."""

    return ask_agent(SYSTEM, user, max_tokens=2500)
