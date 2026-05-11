"""Contract text extraction.

Two paths:
  1. PDFs → pypdf (deterministic, fast)
  2. Images → LLM vision (Claude can read scanned contracts directly)

Falls back to a mock OCR string in mock mode so the demo flows without keys.
"""
from __future__ import annotations

import io
from typing import Literal

from .llm import PROVIDER, complete


SYSTEM_OCR = """You are an OCR transcriber for migrant worker employment contracts.
Read the image and output the contract text verbatim. Preserve clause numbering.
Do not interpret, summarize, or translate. Do not add commentary.
If the contract has multiple languages, output both in the order they appear."""


def extract_text(blob: bytes, *, mime_hint: str | None = None) -> tuple[str, Literal["pdf", "image", "mock"]]:
    """Return (text, source) from a contract upload."""
    if not blob:
        return ("", "mock")

    if blob[:4] == b"%PDF" or (mime_hint == "application/pdf"):
        return (_pdf_to_text(blob), "pdf")

    if PROVIDER == "mock":
        from .llm import _MOCK_OCR
        return (_MOCK_OCR, "mock")

    image_mime = mime_hint or "image/jpeg"
    resp = complete(
        system=SYSTEM_OCR,
        user="Extract the full contract text from this image.",
        image_bytes=blob,
        image_mime=image_mime,
        max_tokens=4000,
    )
    return (resp.text, "image")


def _pdf_to_text(blob: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        return ""
    reader = PdfReader(io.BytesIO(blob))
    return "\n\n".join(page.extract_text() or "" for page in reader.pages).strip()
