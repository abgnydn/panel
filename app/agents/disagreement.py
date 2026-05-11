"""Disagreement detector — finds tensions between agent outputs.

The disagreement reel is Panel's signature UI moment. This module turns the
5 agents' structured outputs into a ranked list of tensions for the UI to render.

Detection strategy:
1. Cross-agent implicit tensions (the IP — Lawyer↔Peer, Lawyer↔Regulator, Triage convergence)
   are PREFERRED — these are the unique moat.
2. Explicit pre-declared `disagreement_flags` are FALLBACK — used only when implicit
   detection yields fewer than 3 items.
3. Ranked by source priority + severity. Top-3 returned.

Severity tiers:
  9 — triage_convergence (multiple agents flag the same trafficking indicator)
  8 — implicit_lawyer_peer (legal but historically dangerous)
  7 — implicit_lawyer_regulator with reg.severity=high
  6 — implicit_lawyer_regulator with reg.severity=medium
  5 — explicit pre-declared
"""
from __future__ import annotations

from typing import Any

AGENT_NAMES = ["lawyer", "translator", "regulator", "peer_advocate", "triage"]

MAX_REEL = 3  # what the UI renders

# Canonical topic categories. Agents return free-text topics like "Passport retention
# clause legality" — we normalize to these so cross-agent matching actually fires.
CANONICAL_TOPICS = {
    "passport":         ["passport", "identity document", "document custody", "document retention"],
    "recruitment_fees": ["recruitment fee", "recruitment cost", "placement fee", "agency fee", "debt bondage", "debt-trap"],
    "wage_deductions":  ["wage deduction", "salary deduction", "withholding", "garnish"],
    "working_hours":    ["working hour", "work hour", "hours of work", "overtime", "unlimited hour"],
    "rest_days":        ["rest day", "off day", "off-day", "weekly rest", "leave"],
    "housing":          ["live-in", "live in", "housing", "isolation", "residence", "accommodation"],
    "termination":      ["termination", "dismiss", "notice period"],
    "wage_level":       ["wage promise", "salary promise", "wage discrepancy", "promised salary", "salary mismatch"],
    "comms_restriction": ["communication", "phone", "contact restriction", "social media"],
}


def canonical_topic(text: str) -> str:
    """Map a free-text topic to a canonical category, or return the topic as-is."""
    if not text:
        return ""
    t = str(text).lower()
    for canon, keywords in CANONICAL_TOPICS.items():
        if any(kw in t for kw in keywords):
            return canon
    return t[:40]


def detect(agent_outputs: dict[str, dict]) -> list[dict[str, Any]]:
    """Return a ranked list of disagreements suitable for the UI reel.

    Implicit detections (the IP) are always preferred. We also enforce DIVERSITY —
    no single source type takes more than 2 of the 3 reel slots, so the
    "legal but dangerous" (lawyer↔peer) tension always gets a chance to surface
    alongside convergence items.
    """
    implicit = _collect_implicit(agent_outputs)
    implicit = _dedupe_by_topic(implicit)
    implicit.sort(key=_rank_score, reverse=True)

    pool = list(implicit)
    if len(pool) < MAX_REEL:
        explicit = _collect_explicit_flags(agent_outputs)
        explicit = _dedupe_by_topic(explicit)
        implicit_topics = {_normalize_topic(i["topic"]) for i in implicit}
        explicit = [e for e in explicit if _normalize_topic(e["topic"]) not in implicit_topics]
        explicit.sort(key=_rank_score, reverse=True)
        pool.extend(explicit)

    # Diversity cap: at most 2 items from the same source.
    chosen: list[dict[str, Any]] = []
    source_counts: dict[str, int] = {}
    for item in pool:
        src = item.get("source", "explicit")
        if source_counts.get(src, 0) >= 2:
            continue
        chosen.append(item)
        source_counts[src] = source_counts.get(src, 0) + 1
        if len(chosen) == MAX_REEL:
            break

    # If diversity-capping starved us, top up with whatever's left
    if len(chosen) < MAX_REEL:
        for item in pool:
            if item in chosen:
                continue
            chosen.append(item)
            if len(chosen) == MAX_REEL:
                break

    for i, item in enumerate(chosen, 1):
        item["rank"] = i
    return chosen


def _collect_explicit_flags(outputs: dict[str, dict]) -> list[dict[str, Any]]:
    """Pull pre-declared disagreements from each agent's `disagreement_flags`.

    LLMs are inconsistent in how they fill structured arrays — some return
    strings, some return malformed dicts. Be tolerant of all shapes.
    """
    result = []
    for agent, out in outputs.items():
        if not isinstance(out, dict):
            continue
        flags = out.get("disagreement_flags") or []
        if not isinstance(flags, list):
            continue
        for flag in flags:
            if flag is None:
                continue
            if isinstance(flag, str):
                # The model returned a free-text disagreement string.
                result.append({
                    "topic": flag[:80],
                    "tensions": [
                        {"agent": agent, "verdict": flag},
                    ],
                    "why_it_matters": "Flagged by the agent as a point of disagreement.",
                    "source": "explicit_str",
                    "severity": 5,
                })
                continue
            if not isinstance(flag, dict):
                continue
            other = flag.get("with_agent", "") or ""
            topic = flag.get("topic", "general") or "general"
            this_pos = flag.get(f"{agent}_position") or flag.get("position")
            their_anticipated = flag.get("anticipated_disagreement", "") or ""
            result.append({
                "topic": str(topic),
                "tensions": [
                    {"agent": agent, "verdict": this_pos or _summary_of(outputs[agent])},
                    {"agent": str(other), "verdict": their_anticipated or _summary_of(outputs.get(other, {}))},
                ],
                "why_it_matters": _why_matters(str(topic), [agent, str(other)]),
                "source": "explicit",
                "severity": _severity_for(str(topic), outputs),
            })
    return result


def _collect_implicit(outputs: dict[str, dict]) -> list[dict[str, Any]]:
    """Find clauses where Lawyer + Peer Advocate verdicts diverge (legal but dangerous,
    or unlawful but rare). Lawyer + Regulator divergence on the same topic also surfaces."""
    result = []
    lawyer = outputs.get("lawyer") or {}
    regulator = outputs.get("regulator") or {}
    peer = outputs.get("peer_advocate") or {}
    triage = outputs.get("triage") or {}

    # Build canonical-topic indexes so free-text topics still match.
    lawyer_topics: dict[str, dict] = {}
    for c in (lawyer.get("clause_analyses") or []):
        if not isinstance(c, dict):
            continue
        canon = canonical_topic(c.get("clause_topic") or c.get("clause_excerpt") or "")
        if canon:
            lawyer_topics.setdefault(canon, c)

    peer_topics: dict[str, dict] = {}
    for m in (peer.get("clause_pattern_matches") or []):
        if not isinstance(m, dict):
            continue
        canon = canonical_topic(m.get("clause_topic") or m.get("pattern_warning") or "")
        if canon:
            peer_topics.setdefault(canon, m)

    regulator_topics: dict[str, dict] = {}
    for c in (regulator.get("core_area_analysis") or []):
        if not isinstance(c, dict):
            continue
        canon = canonical_topic(c.get("area") or c.get("ilo_standard") or "")
        if canon:
            regulator_topics.setdefault(canon, c)

    # Lawyer vs Peer Advocate — legal/gray but historically dangerous
    for topic, lawyer_clause in lawyer_topics.items():
        if topic not in peer_topics:
            continue
        peer_match = peer_topics[topic]
        l_verdict = (lawyer_clause.get("verdict") or "").lower()
        bad = peer_match.get("outcome_distribution") or {}
        bad_count = (bad.get("worker_returned_early", 0)
                     + bad.get("abuse_reported", 0)
                     + bad.get("unresolved", 0))
        total = sum(bad.values()) or 1
        # Fire on both "lawful" AND "gray-area" — both are tensions with Peer's empirics
        if l_verdict in {"lawful", "gray-area", "gray"} and (bad_count / total) >= 0.5:
            verdict_label = "Lawful" if l_verdict == "lawful" else "Gray area"
            sev = 8 if l_verdict == "lawful" else 7
            result.append({
                "topic": _humanize(topic),
                "tensions": [
                    {"agent": "lawyer",
                     "verdict": f"{verdict_label} ({lawyer_clause.get('statute', 'destination law')})"},
                    {"agent": "peer_advocate",
                     "verdict": f"{peer_match.get('similar_cases_count', '?')} similar cases, {bad_count} ended badly ({int(100 * bad_count/total)}%)."},
                ],
                "why_it_matters": (
                    "The contract is legal AND empirically dangerous. The worker should know both."
                    if l_verdict == "lawful" else
                    "Lawful enforcement is patchy AND historical outcomes are bad. Worth flagging."
                ),
                "source": "implicit_lawyer_peer",
                "severity": sev,
            })

    # Lawyer vs Regulator — legal locally, below international standard
    for topic, reg_area in regulator_topics.items():
        if reg_area.get("verdict") != "below_standard":
            continue
        l = lawyer_topics.get(topic)
        if l and l.get("verdict") == "lawful":
            result.append({
                "topic": _humanize(topic),
                "tensions": [
                    {"agent": "lawyer", "verdict": f"Lawful ({l.get('statute', 'destination law')})"},
                    {"agent": "regulator",
                     "verdict": f"Below {reg_area.get('ilo_standard', 'international standard')}, severity {reg_area.get('severity', 'medium')}."},
                ],
                "why_it_matters": "Local law and international standards diverge. Both views matter.",
                "source": "implicit_lawyer_regulator",
                "severity": 7 if reg_area.get("severity") == "high" else 5,
            })

    # Triage convergence — when 2+ agents flag the same canonical topic.
    # Severity differentiates by indicator weight + number of converging agents.
    indicators = triage.get("trafficking_indicators_detected") or []
    seen_convergence = set()
    for indicator in indicators:
        canon = canonical_topic(indicator)
        if not canon or canon in seen_convergence:
            continue
        agents_flagging = []
        if canon in lawyer_topics and lawyer_topics[canon].get("verdict") in {"unlawful", "gray-area"}:
            agents_flagging.append("lawyer")
        if canon in regulator_topics and regulator_topics[canon].get("verdict") in {"below_standard", "prohibited_clause"}:
            agents_flagging.append("regulator")
        if canon in peer_topics:
            agents_flagging.append("peer_advocate")
        if len(agents_flagging) >= 2:
            seen_convergence.add(canon)
            tensions = [
                {"agent": "triage", "verdict": f"ILO trafficking indicator: {_humanize(canon)}."}
            ]
            for ag in agents_flagging:
                tensions.append({"agent": ag, "verdict": _verdict_for(outputs[ag], canon)})
            result.append({
                "topic": _humanize(canon),
                "tensions": tensions,
                "why_it_matters": f"{len(agents_flagging) + 1} agents converge on this clause — strongest signal in the contract.",
                "source": "implicit_triage_convergence",
                "severity": _severity_for_convergence(canon, agents_flagging),
            })

    return result


# Indicator weights: passport > debt bondage > isolation > hours > wages
_INDICATOR_WEIGHT = {
    "passport":          9,   # ILO #1 trafficking precursor
    "recruitment_fees":  8,   # debt bondage
    "housing":           8,   # isolation
    "comms_restriction": 8,
    "working_hours":     7,   # excessive overtime indicator
    "wage_deductions":   7,
    "rest_days":         6,
    "wage_level":        6,
    "termination":       5,
}


def _severity_for_convergence(canon: str, agents: list[str]) -> int:
    """Differentiate severity by indicator weight + count of converging agents."""
    base = _INDICATOR_WEIGHT.get(canon, 7)
    # +1 if 3+ agents converge (rarest, most damning signal)
    if len(agents) >= 3:
        return min(base + 1, 10)
    return base


def _topic_in_output(out: dict, topic: str) -> bool:
    blob = str(out).lower()
    return topic.lower().replace("_", " ") in blob or topic.lower() in blob


def _verdict_for(out: dict, topic: str) -> str:
    """Best-effort: pull a one-line verdict from an agent output for a canonical topic."""
    if not isinstance(out, dict):
        return "(no comment)"
    canon = canonical_topic(topic)
    # Lawyer
    for c in (out.get("clause_analyses") or []):
        if isinstance(c, dict) and canonical_topic(c.get("clause_topic") or c.get("clause_excerpt") or "") == canon:
            return f"{(c.get('verdict') or '?').title()} — {c.get('statute', '')}"
    # Regulator
    for area in (out.get("core_area_analysis") or []):
        if isinstance(area, dict) and canonical_topic(area.get("area") or "") == canon:
            return f"{(area.get('verdict') or '?').replace('_', ' ').title()} ({area.get('ilo_standard', '')})"
    # Peer
    for m in (out.get("clause_pattern_matches") or []):
        if isinstance(m, dict) and canonical_topic(m.get("clause_topic") or m.get("pattern_warning") or "") == canon:
            return m.get("pattern_warning") or "(pattern flagged)"
    return out.get("verdict_summary", "") or "(no comment)"


def _summary_of(out: dict) -> str:
    return out.get("verdict_summary") or "(no summary)"


def _humanize(s: str) -> str:
    return s.replace("_", " ").title()


def _why_matters(topic: str, agents: list[str]) -> str:
    if "lawyer" in agents and "regulator" in agents:
        return "Local law and international standards diverge — the worker should know both."
    if "lawyer" in agents and "peer_advocate" in agents:
        return "The contract is legal AND empirically dangerous."
    return "Two agents reach different conclusions — this clause deserves scrutiny."


def _severity_for(topic: str, outputs: dict[str, dict]) -> int:
    # High severity: trafficking, passport, recruitment debt
    high = {"passport_custody", "passport_retention", "passport_confiscation",
            "recruitment_fees", "live_in_isolation", "wage_deduction", "working_hours"}
    if any(h in topic.lower() for h in high):
        return 7
    return 5


def _normalize_topic(topic: str) -> str:
    """Lowercase + strip + collapse separators so 'Recruitment Fees' == 'recruitment_fees'."""
    return topic.lower().strip().replace("_", " ").replace("-", " ")


def _dedupe_by_topic(items: list[dict]) -> list[dict]:
    seen: dict[str, dict] = {}
    for item in items:
        key = _normalize_topic(item["topic"])
        if key not in seen or item["severity"] > seen[key]["severity"]:
            # Prefer humanized display form (Title Case)
            if "_" in item["topic"]:
                item["topic"] = _humanize(item["topic"])
            seen[key] = item
    return list(seen.values())


def _rank_score(item: dict) -> float:
    severity = item.get("severity", 5)
    n_tensions = len(item.get("tensions", []))
    return severity + 0.5 * n_tensions
