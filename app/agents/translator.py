"""Translator agent — renders contract + analyses in worker's mother tongue."""
from __future__ import annotations

from typing import Any

from .base import ask_agent

LANG_NAMES = {
    "tl": "Tagalog / Filipino (use conversational Filipino, not academic Tagalog)",
    "id": "Bahasa Indonesia (use Bahasa Indonesia, not Bahasa Malaysia)",
    "en": "English",
}

SYSTEM = """You are the TRANSLATOR AGENT in a panel reviewing a migrant worker's employment contract.

Persona: sworn legal translator. You translate faithfully. You do NOT interpret legally.
But you DO flag translation ambiguities that change legal meaning.

You will receive:
- The contract text in canonical English
- The worker's L1 (mother tongue)

Output STRICT JSON matching:
{
  "agent": "translator",
  "source_language": "en",
  "target_language": "<L1 code>",
  "verdict_summary": "<one sentence>",
  "key_findings": ["<3-5 bullets about translation challenges, in English>"],
  "ambiguity_flags": [
    {"clause_number": <int>, "issue": "<one sentence describing the translation ambiguity>"}
  ],
  "plain_language_summary_in_target": "<3-5 sentence plain-language summary IN THE TARGET LANGUAGE>",
  "disagreement_flags": []
}

Output ONLY the JSON object."""


def run(contract_text: str, target_language: str) -> dict[str, Any]:
    lang_label = LANG_NAMES.get(target_language, target_language)
    user = f"""TARGET LANGUAGE: {lang_label}

CONTRACT TEXT (English):
{contract_text}

1. Identify any clauses where translation into the target language introduces ambiguity that affects legal meaning.
2. Produce a plain-language summary of the contract in the target language (3-5 sentences max).
3. Never substitute approximations for legal terms — preserve them with a translator's note."""

    return ask_agent(SYSTEM, user, max_tokens=2000)
