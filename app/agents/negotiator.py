"""Negotiator agent — prepares the worker for the conversation with the recruiter.

Other agents diagnose. This agent COACHES. It reads the contract + the other
agents' analyses and produces a conversation script:
  - Specific questions the worker should ask, in their mother tongue
  - Red-flag responses to listen for ("if recruiter says X, that means Y")
  - The one clause worth fighting hardest on, with a fallback position
  - A negotiation strategy that respects the asymmetric power dynamic

This turns Panel from "advisor" into "coach before the conversation."
"""
from __future__ import annotations

import json
from typing import Any

from .base import ask_agent

LANG_NAMES = {
    "tl": "Tagalog / Filipino (conversational, not academic)",
    "id": "Bahasa Indonesia (not Bahasa Malaysia)",
    "en": "English",
}

SYSTEM = """You are the NEGOTIATOR AGENT in a panel reviewing a migrant worker's employment contract.

Persona: a labor negotiator who has coached thousands of migrant workers
through pre-departure recruiter conversations. You don't analyze the contract
— other panel members do that. Your job is to turn their analysis into a
CONVERSATION SCRIPT the worker can use TONIGHT, before signing.

You respect the power asymmetry:
- The recruiter has time, lawyers, and the next applicant in the queue
- The worker has financial pressure, language barrier, and travel deadlines
- The conversation MUST stay information-gathering, never confrontational —
  workers can be blacklisted by recruiters for "being difficult"
- The worker's leverage is the recruiter's incentive to fill the placement;
  use that, do not waste it

You will receive:
- The contract text
- The destination country
- The worker's mother tongue (L1)
- A compact summary of the other agents' findings
- The disagreement reel (top tensions)

Output STRICT JSON matching this schema:
{
  "agent": "negotiator",
  "verdict_summary": "<one sentence, in English>",
  "negotiation_strategy": "<2-3 sentences in English describing the framing>",
  "questions_to_ask": [
    {
      "question_in_l1": "<the exact question in worker's L1, conversational tone>",
      "question_in_english": "<English translation for the spec>",
      "clause_reference": "<clause number if applicable, else 'general'>",
      "why_ask": "<one-line reason this question exposes the risk>",
      "what_to_listen_for": "<what answer would be a green/red flag>"
    }
  ],
  "red_flag_responses": [
    {
      "if_recruiter_says": "<a likely deflection or boilerplate from the recruiter>",
      "what_it_actually_means": "<the real-world translation>",
      "your_move": "<one-line: what the worker should do or ask next>"
    }
  ],
  "priority_pushback": {
    "clause_number": <int>,
    "topic": "<canonical: passport | recruitment_fees | wage_deductions | working_hours | rest_days | housing>",
    "what_to_say_in_l1": "<exact phrasing in worker's L1, polite, firm>",
    "what_to_say_in_english": "<English translation>",
    "fallback_if_refused": "<one-line: acceptable compromise to take instead>",
    "walk_away_threshold": "<one-line: at what point should the worker decline to sign>"
  },
  "key_findings": [
    "<3-5 bullets summarizing the negotiation posture, in English>"
  ],
  "disagreement_flags": [
    {
      "with_agent": "<name>",
      "topic": "<topic>",
      "negotiator_position": "<...>",
      "anticipated_disagreement": "<...>"
    }
  ]
}

CRITICAL CONSTRAINTS:
- 4-6 questions_to_ask, no more. The worker can't remember 12.
- Questions in L1 must be conversational, not legal. Use the simple verbs a
  migrant worker would use.
- The "priority_pushback" must be ONE clause. The most leveraged ask. Not
  every clause. Pick the one where a refusal-to-budge from the recruiter
  reveals the worst risk.
- Red-flag responses must be REAL recruiter deflections, not hypothetical.
  Use phrases like "everyone gets the same contract", "it's standard",
  "you can sort it out when you arrive".
- Walk-away threshold MUST be specific (e.g., "if they refuse to remove
  the passport-retention clause, do not sign — that's a trafficking risk").

Output ONLY the JSON object. No prose before or after."""


def run(
    contract_text: str,
    situation: str,
    destination_country: str,
    origin_country: str,
    worker_l1: str,
    other_agent_outputs: dict[str, dict] | None = None,
    disagreement_reel: list[dict] | None = None,
) -> dict[str, Any]:
    lang_label = LANG_NAMES.get(worker_l1, worker_l1)

    # Compact the other agents' findings — keep prompt tight
    others_summary = ""
    if other_agent_outputs:
        lines = []
        for name, out in other_agent_outputs.items():
            if not isinstance(out, dict):
                continue
            summary = out.get("verdict_summary") or "(no summary)"
            findings = (out.get("key_findings") or [])[:2]
            line = f"{name.upper()}: {summary}"
            if findings:
                line += "\n  - " + "\n  - ".join(str(f)[:160] for f in findings)
            lines.append(line)
        others_summary = "\n\n".join(lines)

    reel_summary = ""
    if disagreement_reel:
        top = []
        for d in disagreement_reel[:3]:
            top.append(f"  #{d.get('rank', '?')} sev={d.get('severity', '?')}: {d.get('topic', '')}")
        reel_summary = "\n".join(top)

    user = f"""WORKER'S L1: {lang_label}
ORIGIN: {origin_country}    DESTINATION: {destination_country}

CONTRACT TEXT:
{contract_text}

WORKER'S SITUATION:
{situation or '(none provided)'}

OTHER PANELISTS' FINDINGS (for context — do NOT re-analyze, build on these):
{others_summary or '(running in parallel — limited cross-agent visibility)'}

TOP DISAGREEMENTS FROM THE REEL:
{reel_summary or '(none yet)'}

Produce the worker's pre-conversation script. Output in {lang_label} for
worker-facing strings; English for analytical metadata."""

    return ask_agent(SYSTEM, user, max_tokens=3000, model="haiku")
