"""LLM provider abstraction.

Three providers, in priority order:
  1. `claude_cli` — uses the local `claude -p` CLI (Claude Code). Best default
     when the CLI is installed: no API key needed, uses your existing auth.
  2. `anthropic` — direct Anthropic SDK calls. Required for image input (OCR).
  3. `mock` — deterministic seed responses. Used when neither is available.

Override with PANEL_LLM_PROVIDER=claude_cli|anthropic|mock.
"""
from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from typing import Any


@dataclass
class LLMResponse:
    text: str
    usage: dict[str, int]
    provider: str


def _claude_cli_available() -> bool:
    return shutil.which("claude") is not None


def _provider() -> str:
    forced = os.environ.get("PANEL_LLM_PROVIDER", "").lower().strip()
    if forced in {"anthropic", "mock", "claude_cli"}:
        return forced
    if _claude_cli_available():
        return "claude_cli"
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    return "mock"


PROVIDER = _provider()


def is_live() -> bool:
    return PROVIDER in {"anthropic", "claude_cli"}


def provider_label() -> str:
    return {
        "claude_cli": "live (Claude CLI)",
        "anthropic": "live (Anthropic SDK)",
        "mock": "mock mode",
    }.get(PROVIDER, PROVIDER)


def complete(
    system: str,
    user: str,
    *,
    image_bytes: bytes | None = None,
    image_mime: str = "image/jpeg",
    max_tokens: int = 2000,
    model: str = "claude-sonnet-4-6",
) -> LLMResponse:
    """Single-turn completion. Optional image input for contract OCR.

    Returns LLMResponse with the model's text output.

    Image input is only supported by the Anthropic SDK path. If the active
    provider is claude_cli and an image is supplied, falls back to anthropic
    if a key is available, otherwise mock.
    """
    if image_bytes is not None:
        # Vision path: claude_cli doesn't accept raw image bytes via stdin,
        # so route to anthropic if possible, else mock.
        if os.environ.get("ANTHROPIC_API_KEY"):
            return _anthropic(system=system, user=user, image_bytes=image_bytes,
                              image_mime=image_mime, max_tokens=max_tokens, model=model)
        return _mock(system=system, user=user, image_bytes=image_bytes)

    if PROVIDER == "claude_cli":
        return _claude_cli(system=system, user=user, max_tokens=max_tokens, model=model)
    if PROVIDER == "anthropic":
        return _anthropic(system=system, user=user, image_bytes=None,
                          image_mime=image_mime, max_tokens=max_tokens, model=model)
    return _mock(system=system, user=user, image_bytes=None)


# ----------------------------------------------------------------------------
# Claude CLI backend (claude -p)
# ----------------------------------------------------------------------------
def _claude_cli(system: str, user: str, max_tokens: int, model: str) -> LLMResponse:
    """Call `claude -p` with the user prompt on stdin.

    Uses the CLI's existing auth (OAuth / keychain / ANTHROPIC_API_KEY) — no
    extra setup required when `claude` is installed.
    """
    # Normalize model alias: full names work as-is; SDK names need a short alias.
    model_arg = _model_alias_for_cli(model)
    cmd = [
        "claude", "-p",
        "--system-prompt", system,
        "--tools", "",
        "--no-session-persistence",
        "--permission-mode", "bypassPermissions",
        "--output-format", "text",
        "--model", model_arg,
    ]
    try:
        proc = subprocess.run(
            cmd,
            input=user,
            capture_output=True,
            text=True,
            timeout=240,
            check=False,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("claude -p timed out after 240s")
    if proc.returncode != 0:
        raise RuntimeError(
            f"claude -p exited {proc.returncode}: {proc.stderr.strip()[:400]}"
        )
    return LLMResponse(
        text=proc.stdout,
        usage={"input_tokens": 0, "output_tokens": 0},  # CLI doesn't expose usage in text mode
        provider="claude_cli",
    )


def _model_alias_for_cli(model: str) -> str:
    """Map SDK model IDs to CLI-friendly aliases."""
    if model in {"sonnet", "opus", "haiku"}:
        return model
    if "sonnet" in model:
        return "sonnet"
    if "haiku" in model:
        return "haiku"
    if "opus" in model:
        return "opus"
    return model


def complete_json(
    system: str,
    user: str,
    *,
    image_bytes: bytes | None = None,
    image_mime: str = "image/jpeg",
    max_tokens: int = 2000,
    model: str = "claude-sonnet-4-6",
) -> dict[str, Any]:
    """Like complete(), but parses the model's output as JSON.

    Tolerant: strips ```json fences, finds the first {...} block if needed.
    """
    resp = complete(system, user, image_bytes=image_bytes, image_mime=image_mime,
                    max_tokens=max_tokens, model=model)
    return _parse_json_lenient(resp.text)


# ----------------------------------------------------------------------------
# Anthropic backend
# ----------------------------------------------------------------------------
def _anthropic(
    system: str,
    user: str,
    image_bytes: bytes | None,
    image_mime: str,
    max_tokens: int,
    model: str,
) -> LLMResponse:
    import anthropic

    client = anthropic.Anthropic()
    content: list[dict[str, Any]]
    if image_bytes:
        content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": image_mime,
                    "data": base64.b64encode(image_bytes).decode("ascii"),
                },
            },
            {"type": "text", "text": user},
        ]
    else:
        content = [{"type": "text", "text": user}]

    msg = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": content}],
    )
    text = "".join(block.text for block in msg.content if block.type == "text")
    return LLMResponse(
        text=text,
        usage={
            "input_tokens": msg.usage.input_tokens,
            "output_tokens": msg.usage.output_tokens,
        },
        provider="anthropic",
    )


# ----------------------------------------------------------------------------
# Mock backend — deterministic, fast, demo-quality output
# ----------------------------------------------------------------------------
def _mock(system: str, user: str, image_bytes: bytes | None) -> LLMResponse:
    """Return mock output based on which agent's system prompt this is.

    Detects the agent by matching the first 80 chars of system against
    known persona signatures. Falls back to a generic JSON envelope.
    """
    sig = (system or "")[:200].lower()
    if "ocr" in user.lower() or "extract" in user.lower()[:60]:
        text = _MOCK_OCR
    elif "lawyer agent" in sig or "you are a labor lawyer" in sig:
        text = json.dumps(_MOCK_LAWYER)
    elif "translator agent" in sig:
        text = json.dumps(_MOCK_TRANSLATOR)
    elif "regulator agent" in sig:
        text = json.dumps(_MOCK_REGULATOR)
    elif "peer advocate" in sig:
        text = json.dumps(_MOCK_PEER)
    elif "triage agent" in sig:
        text = json.dumps(_MOCK_TRIAGE)
    else:
        text = json.dumps({"mock": True, "echo": user[:120]})
    return LLMResponse(text=text, usage={"input_tokens": 0, "output_tokens": 0}, provider="mock")


def _parse_json_lenient(text: str) -> dict[str, Any]:
    s = text.strip()
    if s.startswith("```"):
        s = s.strip("`")
        if s.lower().startswith("json"):
            s = s[4:]
        s = s.strip()
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        start = s.find("{")
        end = s.rfind("}")
        if start >= 0 and end > start:
            return json.loads(s[start:end + 1])
        raise


# ----------------------------------------------------------------------------
# Mock data — designed to look real in the demo, including pre-baked
# disagreements between agents. Keep aligned with the live agents' schemas.
# ----------------------------------------------------------------------------
_MOCK_OCR = """\
EMPLOYMENT CONTRACT
Between: Al-Mansouri Household Services LLC (Riyadh, KSA) — "Employer"
And: <REDACTED> (Manila, Philippines) — "Employee"

1. Position: Domestic Worker (live-in).
2. Term: Two (2) years renewable.
3. Salary: SAR 1,400 per month.
4. The Employee shall pay a recruitment fee of SAR 12,000, deducted from
   wages over the first 18 months (SAR 666.66 / month).
5. Deductions may be made from salary for damages, breakages, or absences,
   at the Employer's discretion.
6. Working hours: as required by household demands; no fixed limit.
7. The Employee shall reside in housing provided by the Employer.
8. Off-days: at the Employer's discretion.
9. Annual leave: 14 days after one year of service.
10. Medical: Employer covers basic medical care.
11. Repatriation: cost borne by Employee if contract terminated by Employee.
12. Identity documents: The Employer shall retain the Employee's passport
    during the period of employment for safekeeping.
13. Communications: phone and contact subject to Employer's house rules.
14. Termination: Employer may terminate with no notice for breach.
"""

_MOCK_LAWYER = {
    "agent": "lawyer",
    "verdict_summary": "3 of 14 clauses unlawful under KSA law; 2 gray-area.",
    "destination_country": "SA",
    "clause_analyses": [
        {"clause_number": 12, "clause_topic": "passport_custody",
         "verdict": "unlawful",
         "statute": "KSA Labor Law Art. 6 + MoHRSD Decision 166/2017",
         "reasoning": "KSA has explicitly prohibited employer retention of worker passports since 2017."},
        {"clause_number": 4, "clause_topic": "recruitment_fees",
         "verdict": "lawful",
         "statute": "KSA Labor Law silent — C181 not ratified",
         "reasoning": "Worker-paid recruitment fees remain legal in KSA under current law."},
        {"clause_number": 5, "clause_topic": "wage_deductions",
         "verdict": "unlawful",
         "statute": "KSA Labor Law Art. 92",
         "reasoning": "Open-ended deductions at employer discretion exceed the statutory deduction limits."},
        {"clause_number": 6, "clause_topic": "working_hours",
         "verdict": "unlawful",
         "statute": "KSA Labor Law Art. 98",
         "reasoning": "No fixed limit on working hours contradicts the 48-hour maximum (40 in Ramadan)."},
        {"clause_number": 8, "clause_topic": "rest_days",
         "verdict": "gray-area",
         "statute": "KSA Labor Law Art. 104 (domestic worker carve-out)",
         "reasoning": "Domestic workers are not covered by standard rest-day rules; weak enforcement."},
    ],
    "key_findings": [
        "Clause 12 (passport retention) violates KSA Article 6 + MoHRSD 166/2017.",
        "Clause 5 (unbounded deductions) and Clause 6 (no hours limit) are unlawful.",
        "Clause 4 (recruitment fee) is technically lawful in KSA but borderline.",
    ],
    "disagreement_flags": [
        {"with_agent": "regulator", "topic": "recruitment_fees",
         "lawyer_position": "Lawful under SA — C181 unratified.",
         "anticipated_disagreement": "Regulator will flag as violating ILO C181."},
    ],
}

_MOCK_TRANSLATOR = {
    "agent": "translator",
    "verdict_summary": "Translation clear. 1 ambiguity flag.",
    "source_language": "en",
    "target_language": "tl",
    "key_findings": [
        "Clause 5 'deductions ... at Employer's discretion' renders as 'kaltas sa pasya ng amo' — ambiguous between lawful payroll adjustment and wage withholding. Recommend clarification.",
        "Clause 12 'retain the passport for safekeeping' is unambiguous in Tagalog: 'pinanghahawakan' clearly denotes employer custody.",
    ],
    "ambiguity_flags": [{"clause_number": 5, "issue": "kaltas: lawful deduction vs wage withholding"}],
    "disagreement_flags": [],
}

_MOCK_REGULATOR = {
    "agent": "regulator",
    "verdict_summary": "Below international standard in 5 of 8 ILO core areas.",
    "country_pair": "PH_to_SA",
    "core_area_analysis": [
        {"area": "recruitment_fees", "verdict": "below_standard", "severity": "high",
         "ilo_standard": "ILO C181 + Fair Recruitment Initiative",
         "asean_standard": "ASEAN Standard Contract Art. 4.2 — employer bears cost",
         "ratification_status": "SA has not ratified C181"},
        {"area": "passport_custody", "verdict": "below_standard", "severity": "high",
         "ilo_standard": "ILO C97 + General Principles", "ratification_status": "C97 not ratified by SA"},
        {"area": "working_hours", "verdict": "below_standard", "severity": "high",
         "ilo_standard": "ILO C189 (Domestic Workers) Art. 10"},
        {"area": "wages", "verdict": "below_standard", "severity": "medium",
         "ilo_standard": "ILO C95 — wage protection"},
        {"area": "rest_days", "verdict": "below_standard", "severity": "high",
         "ilo_standard": "ILO C189 Art. 10(2) — at least 24h consecutive weekly rest"},
        {"area": "wages_min", "verdict": "silent", "severity": "n/a"},
        {"area": "health_safety", "verdict": "meets_standard", "severity": "n/a"},
        {"area": "freedom_of_association", "verdict": "silent", "severity": "n/a"},
    ],
    "overall_alignment_score": 0.38,
    "key_findings": [
        "Worker pays SAR 12K recruitment fee — violates ILO C181.",
        "No fixed working hours — violates ILO C189 (Domestic Workers Convention).",
        "No guaranteed weekly rest day — violates C189 Art. 10(2).",
    ],
    "disagreement_flags": [
        {"with_agent": "lawyer", "topic": "recruitment_fees",
         "regulator_position": "Below ILO standard regardless of local law.",
         "anticipated_disagreement": "Lawyer correctly marks as lawful locally — disagreement is the point."},
    ],
}

_MOCK_PEER = {
    "agent": "peer_advocate",
    "verdict_summary": "47 similar cases. Risk score 7.2/10.",
    "overall_risk_score": 7.2,
    "clause_pattern_matches": [
        {"clause_number": 7, "clause_topic": "live_in_isolation",
         "similar_cases_count": 23,
         "outcome_distribution": {"resolved_favorably": 4, "worker_returned_early": 14, "abuse_reported": 5},
         "pattern_warning": "Live-in housing without an off-day clause clusters with isolation + wage-dispute outcomes."},
        {"clause_number": 4, "clause_topic": "recruitment_fees",
         "similar_cases_count": 19,
         "outcome_distribution": {"resolved_favorably": 5, "worker_returned_early": 9, "unresolved": 5},
         "pattern_warning": "SAR 12K+ recruitment debt strongly correlates with workers staying in abusive situations to repay."},
        {"clause_number": 12, "clause_topic": "passport_retention",
         "similar_cases_count": 31,
         "outcome_distribution": {"resolved_favorably": 6, "worker_returned_early": 12, "abuse_reported": 13},
         "pattern_warning": "Passport retention is the #1 trafficking precursor in our archive."},
    ],
    "situation_triggers": [
        {"trigger": "Worker described recruiter promising higher salary than contract — Top-3 abuse precursor."},
    ],
    "key_findings": [
        "Live-in housing + no off-day: 14 of 23 similar cases ended in early return.",
        "Recruitment debt + low wage: 9 of 19 returned early; 5 unresolved.",
        "Passport retention: 13 of 31 cases involved reported abuse.",
    ],
    "disagreement_flags": [
        {"with_agent": "lawyer", "topic": "live_in_isolation",
         "peer_position": "Lawful clauses cluster with bad outcomes — empirics matter.",
         "anticipated_disagreement": "Lawyer rates clause 7 as lawful; we rate the pattern as high-risk."},
    ],
}

_MOCK_TRIAGE = {
    "agent": "triage",
    "urgency_score": 8,
    "verdict_summary": "Urgency 8/10. Three trafficking indicators present.",
    "trafficking_indicators_detected": [
        "passport_confiscation",
        "recruitment_fee_debt",
        "live_in_isolation_no_off_day",
    ],
    "indicators_explained": "ILO trafficking indicators: passport retention (Cl.12), debt bondage via SAR 12K recruitment fee (Cl.4), live-in housing with employer-controlled off-days (Cl.7-8).",
    "recommended_actions": [
        {"action": "Do NOT surrender passport on arrival — illegal in KSA since 2017.", "priority": "before_departure"},
        {"action": "Save Philippine Embassy Riyadh 24h hotline offline before departure.", "priority": "before_departure"},
        {"action": "Save Migrante Saudi Arabia WhatsApp before departure.", "priority": "before_departure"},
        {"action": "If passport demanded on arrival, contact embassy POLO immediately.", "priority": "on_arrival"},
    ],
    "contacts": [
        {"name": "Philippine Embassy Riyadh — POLO 24h hotline", "phone": "+966 11 488 0888", "country": "SA"},
        {"name": "Migrante Saudi Arabia", "whatsapp": "+966 50 XXX XXXX", "country": "SA"},
        {"name": "DFA OFW Assistance (Manila)", "phone": "1348", "country": "PH"},
    ],
    "key_findings": [
        "Three ILO trafficking indicators converge in this contract.",
        "Score 8/10 — urgent action required before departure.",
        "Embassy + NGO contacts must be saved offline.",
    ],
    "disagreement_flags": [],
}
