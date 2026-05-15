"""Mosaic AI Foundation Models provider.

Calls Databricks serving endpoints directly. The 12 endpoints available in
the panel us-west-2 Express workspace cover the latency / quality trade-off:

  qwen3-next-80b-a3b-instruct   — recommended default (1-2s, strong reasoning)
  llama-3.3-70b-instruct        — alt large model
  gpt-oss-20b                   — fast small model for low-stakes agents
  gemma-3-12b                   — fastest, simplest agents
  llama-3.1-405b-instruct       — slowest, deepest reasoning

Resolves at runtime — no extra config needed when the FastAPI server runs
inside a Databricks App (the SDK auto-picks up the workspace identity).
"""
from __future__ import annotations

import os
from typing import Any

try:
    from .providers import CompletionResult
except ImportError:
    from providers import CompletionResult  # deployed Databricks App context

# Model aliases — same shape as the rest of the provider registry uses
MODEL_ALIASES = {
    "haiku":  "databricks-qwen3-next-80b-a3b-instruct",
    "sonnet": "databricks-llama-3-3-70b-instruct",
    "opus":   "databricks-meta-llama-3.1-405b-instruct",
}


def _resolve(model: str) -> str:
    if model in MODEL_ALIASES:
        return MODEL_ALIASES[model]
    if model.startswith("databricks-"):
        return model
    # Some shorthand
    for alias, full in MODEL_ALIASES.items():
        if alias in model.lower():
            return full
    # Pass through — assume user knows what they're doing
    return model if model.startswith("databricks-") else MODEL_ALIASES["haiku"]


def mosaic_complete(system: str, user: str, *, model: str, max_tokens: int,
                    image_bytes: bytes | None = None, image_mime: str = "image/jpeg",
                    key: str | None = None) -> CompletionResult:
    """Call a Mosaic AI Foundation Model endpoint."""
    if image_bytes is not None:
        raise RuntimeError("Mosaic AI Foundation Models don't accept image input here. "
                           "Route OCR through a separate model.")

    from databricks.sdk import WorkspaceClient
    from databricks.sdk.service.serving import ChatMessage, ChatMessageRole

    endpoint_name = _resolve(model)
    w = WorkspaceClient()
    resp = w.serving_endpoints.query(
        name=endpoint_name,
        messages=[
            ChatMessage(role=ChatMessageRole.SYSTEM, content=system),
            ChatMessage(role=ChatMessageRole.USER,   content=user),
        ],
        max_tokens=max_tokens,
        temperature=0.0,
    )
    text = (resp.choices[0].message.content if resp.choices and resp.choices[0].message
            else "")
    usage = {
        "input_tokens":  getattr(resp.usage, "prompt_tokens", 0) if resp.usage else 0,
        "output_tokens": getattr(resp.usage, "completion_tokens", 0) if resp.usage else 0,
    }
    return CompletionResult(text=text, usage=usage, provider=f"mosaic:{endpoint_name}")


def mosaic_test(*, key: str | None = None, model: str = "haiku") -> tuple[bool, str]:
    try:
        r = mosaic_complete("Return only the literal text: ok",
                            "Say ok.", model=model, max_tokens=8)
        return True, f"endpoint ok ({r.text.strip()[:20]})"
    except Exception as e:
        return False, str(e)[:200]


def is_databricks_runtime() -> bool:
    """True when running inside a Databricks workspace or app."""
    return bool(
        os.environ.get("DATABRICKS_HOST")
        or os.environ.get("DATABRICKS_RUNTIME_VERSION")
        or os.environ.get("DB_HOME")
    )
