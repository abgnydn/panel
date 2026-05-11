"""Round 2: each agent sees the others' outputs and pushes back or concedes.

This is the "boardroom debate" piece — agents no longer just run in parallel,
they react to one another. We pass each agent a compressed snapshot of the
other four's findings and ask one question: *what do you most want to add or
push back on, given what others said?*

Kept short on purpose: 2-3 sentences per agent, structured for UI rendering.
"""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable

from .base import ask_agent, run_with_timing

ROLE_TAGLINES = {
    "lawyer":        "labor lawyer in destination country",
    "translator":    "sworn legal translator (worker's L1)",
    "regulator":     "ILO labor-standards specialist",
    "peer_advocate": "community advocate working with returnees",
    "triage":        "anti-trafficking NGO triage worker",
    "negotiator":    "labor negotiator coaching the worker",
}

SYSTEM_TMPL = """You are the {tagline} on a panel reviewing a migrant worker's employment contract.

Round 1 has just completed. You see compact summaries of what the other four
panel members said. Your job in Round 2 is to give ONE short reaction — 2 to 3
sentences — that either:
  - Pushes back on a specific claim from another panelist
  - Concedes a point you initially missed
  - Adds a critical caveat the others overlooked

Be direct. Quote the agent you're responding to by name. Stay in your lane —
do not adopt another agent's expertise.

Output STRICT JSON:
{{
  "agent": "<your name>",
  "rebuttal": "<2-3 sentence response>",
  "responds_to": "<which agent you primarily address>",
  "stance": "concede" | "push_back" | "extend"
}}

Output ONLY the JSON object."""


def _other_agents_summary(others: dict[str, dict]) -> str:
    """Compress the other 4 agents' outputs to a single block to feed back in."""
    parts = []
    for name, out in others.items():
        if not isinstance(out, dict):
            continue
        summary = out.get("verdict_summary") or "(no summary)"
        findings = out.get("key_findings") or []
        flags = []
        for f in (out.get("disagreement_flags") or [])[:2]:
            if isinstance(f, dict):
                topic = f.get("topic", "")
                if topic:
                    flags.append(topic)
            elif isinstance(f, str):
                flags.append(f[:80])
        block = f"{name.upper()}: {summary}"
        if findings:
            block += "\n  findings:"
            for f in findings[:3]:
                block += f"\n    - {f}"
        if flags:
            block += f"\n  flagged tensions: {', '.join(flags)}"
        parts.append(block)
    return "\n\n".join(parts)


def run_rebuttals(
    round1_outputs: dict[str, dict],
    *,
    on_agent_done: Callable[[str, dict], None] | None = None,
) -> dict[str, dict]:
    """For each of the 5 agents, generate a 2-3 sentence Round 2 rebuttal."""
    agent_names = ["lawyer", "translator", "regulator", "peer_advocate", "triage", "negotiator"]

    def task_for(name: str):
        others = {k: v for k, v in round1_outputs.items() if k != name}
        others_summary = _other_agents_summary(others)
        own_summary = round1_outputs.get(name, {}).get("verdict_summary", "")
        system = SYSTEM_TMPL.format(tagline=ROLE_TAGLINES[name])
        user = (
            f"YOUR ROUND-1 SUMMARY: {own_summary}\n\n"
            f"OTHER PANELISTS' ROUND-1 OUTPUTS:\n{others_summary}\n\n"
            "Give your Round 2 reaction. One agent to respond to. 2-3 sentences."
        )
        return lambda: ask_agent(system, user, max_tokens=600, model="haiku")

    rebuttals: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = {pool.submit(run_with_timing, name, task_for(name)): name
                   for name in agent_names}
        for fut in as_completed(futures, timeout=180):
            name = futures[fut]
            try:
                result = fut.result()
                result.output["_latency_ms"] = result.latency_ms
                rebuttals[name] = result.output
                if on_agent_done:
                    on_agent_done(name, result.output)
            except Exception as exc:
                rebuttals[name] = {
                    "agent": name,
                    "rebuttal": f"(skipped: {exc})",
                    "stance": "extend",
                    "_latency_ms": 0,
                }
                if on_agent_done:
                    on_agent_done(name, rebuttals[name])
    return rebuttals
