"""LLM provider registry — multi-backend support inspired by wonder/.

Each provider declares:
  id, label, description, needs_key, default_model, models, supports_vision
plus two callables — `complete()` returning text, `test()` returning (ok, msg).

The active provider + key + model is resolved per-call from:
  1. Streamlit session_state (UI-entered values)
  2. Environment variables
  3. Sensible defaults

Keys entered via the UI never touch disk — they live in session_state for
the lifetime of the browser session only.
"""
from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class CompletionResult:
    text: str
    usage: dict[str, int]
    provider: str


# ----------------------------------------------------------------------------
# Per-provider implementations
# ----------------------------------------------------------------------------
def _anthropic_complete(
    system: str, user: str, *, model: str, max_tokens: int,
    image_bytes: bytes | None = None, image_mime: str = "image/jpeg",
    key: str | None = None,
) -> CompletionResult:
    import anthropic
    api_key = key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("Anthropic API key not set")
    client = anthropic.Anthropic(api_key=api_key)
    content: list[dict[str, Any]]
    if image_bytes:
        content = [
            {"type": "image", "source": {
                "type": "base64", "media_type": image_mime,
                "data": base64.b64encode(image_bytes).decode("ascii"),
            }},
            {"type": "text", "text": user},
        ]
    else:
        content = [{"type": "text", "text": user}]
    msg = client.messages.create(
        model=_canon_anthropic_model(model),
        max_tokens=max_tokens, system=system,
        messages=[{"role": "user", "content": content}],
    )
    text = "".join(b.text for b in msg.content if b.type == "text")
    return CompletionResult(
        text=text,
        usage={"input_tokens": msg.usage.input_tokens, "output_tokens": msg.usage.output_tokens},
        provider="anthropic",
    )


def _canon_anthropic_model(model: str) -> str:
    aliases = {"sonnet": "claude-sonnet-4-6", "haiku": "claude-haiku-4-5", "opus": "claude-opus-4-7"}
    return aliases.get(model, model)


def _anthropic_test(*, key: str | None = None, model: str = "claude-haiku-4-5") -> tuple[bool, str]:
    try:
        r = _anthropic_complete("You return only 'ok'.", "Say ok",
                                 model=model, max_tokens=8, key=key)
        return (True, f"auth ok ({r.text.strip()[:20]})")
    except Exception as e:
        return (False, str(e)[:200])


# ----------------------------------------------------------------------------
def _openai_compat_complete(
    *, endpoint: str, system: str, user: str, model: str, max_tokens: int,
    key: str,
) -> CompletionResult:
    """Shared client for any OpenAI-compatible chat completions endpoint
    (OpenAI, Gemini's OpenAI compat layer, LM Studio, etc.)."""
    import urllib.request
    body = json.dumps({
        "model": model,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
    }).encode("utf-8")
    req = urllib.request.Request(endpoint, data=body, method="POST",
                                  headers={"Content-Type": "application/json",
                                           "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=90) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    choice = (data.get("choices") or [{}])[0]
    text = (choice.get("message") or {}).get("content") or ""
    usage = data.get("usage") or {}
    return CompletionResult(
        text=text,
        usage={
            "input_tokens": usage.get("prompt_tokens", 0),
            "output_tokens": usage.get("completion_tokens", 0),
        },
        provider=endpoint,
    )


def _openai_complete(system: str, user: str, *, model: str, max_tokens: int,
                     image_bytes: bytes | None = None, image_mime: str = "image/jpeg",
                     key: str | None = None) -> CompletionResult:
    api_key = key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OpenAI API key not set")
    return _openai_compat_complete(
        endpoint="https://api.openai.com/v1/chat/completions",
        system=system, user=user, model=model, max_tokens=max_tokens, key=api_key,
    )


def _openai_test(*, key: str | None = None, model: str = "gpt-4o-mini") -> tuple[bool, str]:
    try:
        r = _openai_complete("You return only 'ok'.", "Say ok",
                              model=model, max_tokens=8, key=key)
        return (True, f"auth ok ({r.text.strip()[:20]})")
    except Exception as e:
        return (False, str(e)[:200])


# ----------------------------------------------------------------------------
def _gemini_complete(system: str, user: str, *, model: str, max_tokens: int,
                     image_bytes: bytes | None = None, image_mime: str = "image/jpeg",
                     key: str | None = None) -> CompletionResult:
    api_key = key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Gemini API key not set")
    return _openai_compat_complete(
        endpoint="https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        system=system, user=user, model=model, max_tokens=max_tokens, key=api_key,
    )


def _gemini_test(*, key: str | None = None, model: str = "gemini-2.5-flash") -> tuple[bool, str]:
    try:
        r = _gemini_complete("You return only 'ok'.", "Say ok",
                              model=model, max_tokens=8, key=key)
        return (True, f"auth ok ({r.text.strip()[:20]})")
    except Exception as e:
        return (False, str(e)[:200])


# ----------------------------------------------------------------------------
def _lmstudio_complete(system: str, user: str, *, model: str, max_tokens: int,
                       image_bytes: bytes | None = None, image_mime: str = "image/jpeg",
                       key: str | None = None, url: str | None = None) -> CompletionResult:
    base = (url or os.environ.get("LMSTUDIO_URL")
            or "http://localhost:1234/v1/chat/completions")
    return _openai_compat_complete(
        endpoint=base, system=system, user=user,
        model=model, max_tokens=max_tokens, key=key or "lm-studio",
    )


def _lmstudio_test(*, key: str | None = None, model: str = "", url: str | None = None) -> tuple[bool, str]:
    try:
        r = _lmstudio_complete("You return only 'ok'.", "Say ok",
                                model=model or "loaded-model",
                                max_tokens=8, key=key, url=url)
        return (True, f"server reachable ({r.text.strip()[:20]})")
    except Exception as e:
        return (False, str(e)[:200])


# ----------------------------------------------------------------------------
def _claude_cli_complete(system: str, user: str, *, model: str, max_tokens: int,
                         image_bytes: bytes | None = None, image_mime: str = "image/jpeg",
                         key: str | None = None) -> CompletionResult:
    """Local Claude CLI — uses your existing auth, no key needed."""
    model_arg = {"claude-sonnet-4-6": "sonnet", "claude-haiku-4-5": "haiku",
                 "claude-opus-4-7": "opus"}.get(model, model)
    if model_arg not in {"sonnet", "haiku", "opus"} and "sonnet" not in model_arg \
            and "haiku" not in model_arg and "opus" not in model_arg:
        model_arg = "haiku"
    cmd = ["claude", "-p",
           "--system-prompt", system, "--tools", "",
           "--no-session-persistence", "--permission-mode", "bypassPermissions",
           "--output-format", "text", "--model", model_arg]
    try:
        proc = subprocess.run(cmd, input=user, capture_output=True, text=True,
                              timeout=240, check=False)
    except subprocess.TimeoutExpired:
        raise RuntimeError("claude -p timed out after 240s")
    if proc.returncode != 0:
        raise RuntimeError(f"claude -p exit {proc.returncode}: {proc.stderr.strip()[:200]}")
    return CompletionResult(text=proc.stdout, usage={"input_tokens": 0, "output_tokens": 0},
                            provider="claude_cli")


def _claude_cli_test(*, key: str | None = None, model: str = "haiku") -> tuple[bool, str]:
    if not shutil.which("claude"):
        return (False, "claude CLI not installed")
    try:
        r = _claude_cli_complete("You return only 'ok'.", "Say ok",
                                  model=model, max_tokens=8)
        return (True, f"CLI ok ({r.text.strip()[:20]})")
    except Exception as e:
        return (False, str(e)[:200])


# ----------------------------------------------------------------------------
def _mock_complete(system: str, user: str, *, model: str, max_tokens: int,
                   image_bytes: bytes | None = None, image_mime: str = "image/jpeg",
                   key: str | None = None) -> CompletionResult:
    from .llm import _mock as _llm_mock
    return CompletionResult(text=_llm_mock(system, user, image_bytes).text,
                            usage={"input_tokens": 0, "output_tokens": 0},
                            provider="mock")


# ----------------------------------------------------------------------------
# Registry
# ----------------------------------------------------------------------------
PROVIDERS: dict[str, dict[str, Any]] = {
    "claude_cli": {
        "label": "Claude CLI (local auth)",
        "description": "Uses your installed `claude` CLI — no API key needed.",
        "needs_key": False,
        "needs_url": False,
        "supports_vision": False,
        "default_model": "haiku",
        "models": ["haiku", "sonnet", "opus"],
        "env_key": None,
        "complete": _claude_cli_complete,
        "test": _claude_cli_test,
    },
    "anthropic": {
        "label": "Anthropic (Claude)",
        "description": "Direct API — bring your own ANTHROPIC_API_KEY. Supports image OCR.",
        "needs_key": True,
        "needs_url": False,
        "supports_vision": True,
        "default_model": "claude-haiku-4-5",
        "models": ["claude-haiku-4-5", "claude-sonnet-4-6", "claude-opus-4-7"],
        "env_key": "ANTHROPIC_API_KEY",
        "complete": _anthropic_complete,
        "test": _anthropic_test,
    },
    "openai": {
        "label": "OpenAI",
        "description": "Direct API — bring your own OPENAI_API_KEY.",
        "needs_key": True,
        "needs_url": False,
        "supports_vision": True,
        "default_model": "gpt-4o-mini",
        "models": ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "gpt-4.1"],
        "env_key": "OPENAI_API_KEY",
        "complete": _openai_complete,
        "test": _openai_test,
    },
    "gemini": {
        "label": "Gemini (Google AI Studio)",
        "description": "Free tier, no card. Bring your AI Studio key.",
        "needs_key": True,
        "needs_url": False,
        "supports_vision": True,
        "default_model": "gemini-2.5-flash",
        "models": ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro"],
        "env_key": "GEMINI_API_KEY",
        "complete": _gemini_complete,
        "test": _gemini_test,
    },
    "lmstudio": {
        "label": "LM Studio (local)",
        "description": "Local OpenAI-compatible server. Set the URL if non-default.",
        "needs_key": False,
        "needs_url": True,
        "supports_vision": False,
        "default_model": "qwen3-14b-mlx",
        "models": [],  # populated dynamically; user picks any loaded model
        "env_key": None,
        "complete": _lmstudio_complete,
        "test": _lmstudio_test,
    },
    "mock": {
        "label": "Mock (offline)",
        "description": "Canned responses for offline demo.",
        "needs_key": False,
        "needs_url": False,
        "supports_vision": False,
        "default_model": "mock-1",
        "models": ["mock-1"],
        "env_key": None,
        "complete": _mock_complete,
        "test": lambda **_: (True, "mock always ok"),
    },
}


# ----------------------------------------------------------------------------
# Resolution helpers
# ----------------------------------------------------------------------------
def list_providers() -> list[tuple[str, dict[str, Any]]]:
    return list(PROVIDERS.items())


def default_provider() -> str:
    """Pick a sensible default at boot."""
    forced = os.environ.get("PANEL_LLM_PROVIDER", "").lower().strip()
    if forced and forced in PROVIDERS:
        return forced
    if shutil.which("claude"):
        return "claude_cli"
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.environ.get("GEMINI_API_KEY"):
        return "gemini"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    return "mock"


def get_config() -> dict[str, Any]:
    """Resolve active provider + key + model from session_state or env.

    Streamlit is optional — if not available (e.g. CLI script), falls back to env.
    """
    provider = default_provider()
    key: str | None = None
    model: str | None = None
    url: str | None = None
    try:
        import streamlit as st
        provider = st.session_state.get("panel_provider", provider)
        spec = PROVIDERS.get(provider, {})
        keys = st.session_state.get("panel_keys", {}) or {}
        models = st.session_state.get("panel_models", {}) or {}
        key = keys.get(provider) or (os.environ.get(spec.get("env_key")) if spec.get("env_key") else None)
        model = models.get(provider) or spec.get("default_model")
        if spec.get("needs_url"):
            url = st.session_state.get("panel_lmstudio_url") or os.environ.get("LMSTUDIO_URL")
    except Exception:
        spec = PROVIDERS.get(provider, {})
        if spec.get("env_key"):
            key = os.environ.get(spec["env_key"])
        model = spec.get("default_model")
    return {"provider": provider, "key": key, "model": model, "url": url}


def complete(system: str, user: str, *, max_tokens: int = 2000,
             image_bytes: bytes | None = None, image_mime: str = "image/jpeg",
             model: str | None = None) -> CompletionResult:
    cfg = get_config()
    provider = cfg["provider"]
    spec = PROVIDERS[provider]
    use_model = model or cfg["model"] or spec["default_model"]

    # Image fallback: if active provider doesn't support vision, route to anthropic
    # when a key is available, else mock.
    if image_bytes is not None and not spec.get("supports_vision"):
        if os.environ.get("ANTHROPIC_API_KEY"):
            return PROVIDERS["anthropic"]["complete"](
                system, user, model="claude-haiku-4-5", max_tokens=max_tokens,
                image_bytes=image_bytes, image_mime=image_mime,
                key=os.environ["ANTHROPIC_API_KEY"],
            )
        return PROVIDERS["mock"]["complete"](system, user, model="mock-1", max_tokens=max_tokens)

    kwargs: dict[str, Any] = {
        "model": use_model, "max_tokens": max_tokens,
        "image_bytes": image_bytes, "image_mime": image_mime,
        "key": cfg.get("key"),
    }
    if spec.get("needs_url"):
        kwargs["url"] = cfg.get("url")
    return spec["complete"](system, user, **kwargs)


def test(provider_id: str, *, key: str | None = None, model: str | None = None,
         url: str | None = None) -> tuple[bool, str]:
    spec = PROVIDERS.get(provider_id)
    if not spec:
        return (False, f"unknown provider: {provider_id}")
    kwargs: dict[str, Any] = {"key": key, "model": model or spec.get("default_model")}
    if spec.get("needs_url"):
        kwargs["url"] = url
    try:
        return spec["test"](**kwargs)
    except Exception as e:
        return (False, str(e)[:200])
