"""Shared utilities for Panel agents."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from ..llm import complete_json
except ImportError:
    from llm import complete_json  # deployed Databricks App context

DATA_DIR = Path(__file__).parent.parent / "data"


def load_data(name: str) -> Any:
    """Read a JSON seed file from app/data/."""
    path = DATA_DIR / f"{name}.json"
    with path.open() as f:
        return json.load(f)


@dataclass
class AgentResult:
    agent: str
    output: dict[str, Any]
    latency_ms: int


def run_with_timing(agent: str, fn) -> AgentResult:
    """Run an agent function, capture wall-clock latency."""
    start = time.perf_counter()
    output = fn()
    elapsed = int((time.perf_counter() - start) * 1000)
    output.setdefault("agent", agent)
    return AgentResult(agent=agent, output=output, latency_ms=elapsed)


def ask_agent(system_prompt: str, user_prompt: str, *, max_tokens: int = 2000,
              model: str = "haiku") -> dict[str, Any]:
    """Convenience wrapper: complete + parse JSON.

    Default model = haiku for speed during the hackathon demo. Override per-agent
    with model="sonnet" if you need deeper reasoning on a critical agent.
    """
    return complete_json(system=system_prompt, user=user_prompt,
                          max_tokens=max_tokens, model=model)
