"""Moderator — orchestrates the 5 agents in parallel, detects disagreements, synthesizes."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable

try:
    from .. import cache, store
except ImportError:
    import cache, store  # deployed Databricks App context (sys.path includes app/)
from . import (checklist, disagreement, lawyer, negotiator, peer_advocate,
               rebuttal, regulator, translator, triage)
from .base import AgentResult, run_with_timing


L1_DISCLAIMERS = {
    "tl": "Ang Panel ay nagbibigay lamang ng impormasyon, hindi legal na payo. Para sa agarang tulong, tumawag sa embahada o NGO.",
    "id": "Panel hanya memberikan informasi, bukan nasihat hukum. Untuk bantuan darurat, hubungi kedutaan atau LSM.",
    "en": "Panel provides information only — not legal advice. For urgent help, contact the embassy or an NGO.",
}


def run_panel(
    contract_text: str,
    situation: str,
    destination_country: str,
    origin_country: str,
    worker_l1: str,
    *,
    on_agent_done: Callable[[str, dict], None] | None = None,
    on_rebuttal_done: Callable[[str, dict], None] | None = None,
    persist: bool = True,
    use_cache: bool = True,
    run_round2: bool = True,
    run_checklist: bool = True,
) -> dict[str, Any]:
    """Run the 5-agent panel + optional Round-2 rebuttals + checklist synthesis.

    Returns a structured response with: per-agent outputs, the disagreement reel,
    Round-2 rebuttals, the worker checklist, and a synthesized recommendation
    in the worker's L1.
    """
    # Cache hit? Return immediately and fire callbacks synchronously for UI continuity.
    cache_key = cache.key(contract_text, situation, destination_country,
                          origin_country, worker_l1) if use_cache else None
    if cache_key:
        cached = cache.get(cache_key)
        if cached:
            cached["_cache_hit"] = True
            if on_agent_done:
                for name in ("lawyer", "translator", "regulator", "peer_advocate", "triage", "negotiator"):
                    out = cached.get("agents", {}).get(name)
                    if out:
                        on_agent_done(name, out)
            if on_rebuttal_done:
                for name, reb in (cached.get("rebuttals") or {}).items():
                    on_rebuttal_done(name, reb)
            return cached

    # Persistence (best-effort; if SQLite is locked, skip)
    session_id: str | None = None
    if persist:
        try:
            worker_id = store.create_worker(origin_country, destination_country, worker_l1)
            session_id = store.create_session(worker_id, contract_text, situation, "en")
        except Exception:
            session_id = None

    tasks = {
        "lawyer": lambda: lawyer.run(contract_text, destination_country),
        "translator": lambda: translator.run(contract_text, worker_l1),
        "regulator": lambda: regulator.run(contract_text, destination_country, origin_country),
        "peer_advocate": lambda: peer_advocate.run(contract_text, situation, destination_country, origin_country),
        "triage": lambda: triage.run(contract_text, situation, destination_country, origin_country),
        "negotiator": lambda: negotiator.run(
            contract_text, situation, destination_country, origin_country, worker_l1,
        ),
    }

    outputs: dict[str, dict[str, Any]] = {}
    errors: dict[str, str] = {}

    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {
            pool.submit(run_with_timing, name, fn): name
            for name, fn in tasks.items()
        }
        for fut in as_completed(futures, timeout=300):
            name = futures[fut]
            try:
                result: AgentResult = fut.result()
                # Stamp the latency onto the output so the UI can render it.
                result.output["_latency_ms"] = result.latency_ms
                outputs[name] = result.output
                if session_id:
                    try:
                        store.log_agent(session_id, name, "analysis",
                                        result.output, latency_ms=result.latency_ms)
                    except Exception:
                        pass
                if on_agent_done:
                    on_agent_done(name, result.output)
            except Exception as exc:
                errors[name] = str(exc)
                outputs[name] = {"agent": name, "error": str(exc),
                                 "verdict_summary": f"(agent failed: {exc})",
                                 "key_findings": [],
                                 "_latency_ms": 0}
                if on_agent_done:
                    on_agent_done(name, outputs[name])

    # Disagreement detection
    reel = disagreement.detect(outputs)

    # Round 2: rebuttals — agents see each other's outputs and respond
    rebuttals: dict[str, dict] = {}
    if run_round2 and not errors:
        try:
            rebuttals = rebuttal.run_rebuttals(outputs, on_agent_done=on_rebuttal_done)
        except Exception as exc:
            rebuttals = {"_error": str(exc)}

    # Checklist synthesis — pre-departure / arrival / employment / exit
    checklist_out: dict[str, Any] = {}
    if run_checklist and not errors:
        try:
            checklist_out = checklist.run(
                {
                    "agents": outputs,
                    "disagreement_reel": reel,
                    "final_urgency_score": int((outputs.get("triage") or {}).get("urgency_score", 5)),
                    "destination_country": destination_country,
                    "origin_country": origin_country,
                },
                worker_l1=worker_l1,
            )
        except Exception as exc:
            checklist_out = {"_error": str(exc)}

    # Synthesis
    urgency = int((outputs.get("triage") or {}).get("urgency_score", 5))
    synth = _synthesize(outputs, reel, urgency, worker_l1, destination_country, origin_country)

    # Persist final recommendation
    if session_id:
        try:
            store.save_recommendation(
                session_id=session_id,
                urgency_score=urgency,
                summary_l1=synth["tldr"],
                summary_en=synth.get("tldr_en", synth["tldr"]),
                action_items=synth["action_items"],
                contacts=synth["contacts"],
                disagreements=reel,
                disclaimer_l1=L1_DISCLAIMERS.get(worker_l1, L1_DISCLAIMERS["en"]),
            )
            store.end_session(session_id)
        except Exception:
            pass

    # LLM outputs can be lossy. Coerce shapes here so the frontend never
    # sees a string where it expects a list, etc.
    def _as_list(v: Any) -> list:
        if isinstance(v, list):
            return [x for x in v if isinstance(x, dict)] if v and isinstance(v[0], dict) else v
        return []

    def _as_dict(v: Any) -> dict:
        return v if isinstance(v, dict) else {}

    def _as_str(v: Any) -> str:
        return v if isinstance(v, str) else ""

    negotiator_out = outputs.get("negotiator") or {}

    # Normalise negotiator field names. The agent prompt produces snake_case
    # names with `question_in_l1`, `clause_reference`, etc.; the frontend reads
    # `question_l1`, `clause`. Map them here so the contract stays stable
    # regardless of what the agent emits.
    def _norm_question(q: dict) -> dict:
        if not isinstance(q, dict):
            return {}
        return {
            "clause":      q.get("clause") or q.get("clause_reference") or "",
            "question_l1": q.get("question_l1") or q.get("question_in_l1") or "",
            "question_en": q.get("question_en") or q.get("question_in_english") or "",
            "why_ask":     q.get("why_ask") or "",
            "listen_for":  q.get("listen_for") or q.get("what_to_listen_for") or "",
        }

    def _norm_redflag(r: dict) -> dict:
        if not isinstance(r, dict):
            return {}
        return {
            "if_recruiter_says": r.get("if_recruiter_says") or "",
            "what_it_means":     r.get("what_it_means") or r.get("what_it_actually_means") or r.get("what_it_actual_means") or "",
            "your_move":         r.get("your_move") or "",
        }

    def _norm_priority(p: dict) -> dict:
        if not isinstance(p, dict):
            return {}
        return {
            "clause_number":          p.get("clause_number") or p.get("clause") or "",
            "topic":                  p.get("topic") or "",
            "what_to_say_in_l1":      p.get("what_to_say_in_l1") or "",
            "what_to_say_in_english": p.get("what_to_say_in_english") or "",
            "fallback_if_refused":    p.get("fallback_if_refused") or "",
            "walk_away_threshold":    p.get("walk_away_threshold") or "",
        }

    negotiation_block = {
        "strategy":          _as_str(negotiator_out.get("negotiation_strategy")),
        "priority_pushback": _norm_priority(_as_dict(negotiator_out.get("priority_pushback"))),
        "questions":         [_norm_question(q) for q in _as_list(negotiator_out.get("questions_to_ask"))],
        "red_flags":         [_norm_redflag(r) for r in _as_list(negotiator_out.get("red_flag_responses"))],
    }

    def _norm_refusal(r: dict) -> dict:
        if not isinstance(r, dict):
            return {"refusal": "", "reason": ""}
        return {
            "refusal": r.get("refusal") or "",
            "reason":  r.get("reason") or r.get("reason_short") or "",
        }

    def _norm_pushback(p: dict) -> dict:
        if not isinstance(p, dict):
            return {"clause_number": "", "ask": "", "suggested": ""}
        return {
            "clause_number": p.get("clause_number") or p.get("clause") or "",
            "ask":           p.get("ask") or "",
            "suggested":     p.get("suggested") or p.get("suggested_text") or "",
        }

    def _norm_checklist_item(it: dict) -> dict:
        if not isinstance(it, dict):
            return {"priority": "medium", "action": "", "details": ""}
        return {
            "priority": it.get("priority") or "medium",
            "action":   it.get("action") or "",
            "details":  it.get("details") or "",
        }

    if isinstance(checklist_out, dict) and not checklist_out.get("_error"):
        phases = _as_dict(checklist_out.get("phases"))
        refusals  = [_norm_refusal(r) for r in _as_list(checklist_out.get("things_to_refuse"))]
        pushbacks = [_norm_pushback(p) for p in _as_list(checklist_out.get("recruiter_pushback"))]
        checklist_phases = {
            "before_departure":  [_norm_checklist_item(x) for x in _as_list(phases.get("before_departure"))],
            "on_arrival":        [_norm_checklist_item(x) for x in _as_list(phases.get("on_arrival"))],
            "during_employment": [_norm_checklist_item(x) for x in _as_list(phases.get("during_employment"))],
            "exit_emergency":    [_norm_checklist_item(x) for x in _as_list(phases.get("exit_emergency"))],
        }
    else:
        refusals = []
        pushbacks = []
        checklist_phases = {
            "before_departure":  [],
            "on_arrival":        [],
            "during_employment": [],
            "exit_emergency":    [],
        }

    final = {
        "session_id": session_id,
        "worker_l1": worker_l1,
        "destination_country": destination_country,
        "origin_country": origin_country,
        "agents_completed": list(outputs.keys()),
        "agents_failed": list(errors.keys()),
        "agents": outputs,
        "final_urgency_score": urgency,
        "disagreement_reel": reel,
        "rebuttals": rebuttals,
        "negotiation": negotiation_block,
        "checklist": checklist_phases,
        "refusals": refusals,
        "pushbacks": pushbacks,
        "recommendation": synth,
        "_cache_hit": False,
    }
    if cache_key and not errors:
        cache.put(cache_key, final)
    return final


def _synthesize(outputs: dict[str, dict], reel: list[dict],
                urgency: int, worker_l1: str,
                destination: str, origin: str) -> dict[str, Any]:
    """Combine agent outputs into a single recommendation for the worker."""
    translator_out = outputs.get("translator") or {}
    triage_out = outputs.get("triage") or {}

    # Action items: prefer Triage's recommended_actions, deduped
    action_items = []
    seen_actions = set()
    for item in (triage_out.get("recommended_actions") or []):
        text = item.get("action", "").strip()
        if text and text not in seen_actions:
            action_items.append(text)
            seen_actions.add(text)

    contacts = triage_out.get("contacts") or []

    # Plain-language summary: prefer translator's L1 summary
    tldr = translator_out.get("plain_language_summary_in_target") or (
        f"Suriin ng panel ang kontrata mo. May {len(reel)} mahalagang isyu na dapat mong malaman."
        if worker_l1 == "tl"
        else f"Panel reviewed your contract. {len(reel)} key issues to consider."
    )

    tldr_en = _english_summary(outputs, urgency, reel)

    return {
        "tldr": tldr,
        "tldr_en": tldr_en,
        "action_items": action_items,
        "contacts": contacts,
        "legal_disclaimer": L1_DISCLAIMERS.get(worker_l1, L1_DISCLAIMERS["en"]),
    }


def _english_summary(outputs: dict[str, dict], urgency: int, reel: list[dict]) -> str:
    lawyer_out = outputs.get("lawyer", {})
    regulator_out = outputs.get("regulator", {})
    lines = []
    if v := lawyer_out.get("verdict_summary"):
        lines.append(f"Lawyer: {v}")
    if v := regulator_out.get("verdict_summary"):
        lines.append(f"Regulator: {v}")
    lines.append(f"Urgency: {urgency}/10. {len(reel)} panel disagreements identified.")
    return " · ".join(lines)
