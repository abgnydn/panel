"""Export utilities — PDF + QR code + Markdown bundle.

The worker gets a self-contained artifact to save offline before flying:
- Their recommendation + checklist as a printable PDF
- A QR code pointing to the local session URL (so peers can scan)
- A Markdown text-only fallback for low-bandwidth share
"""
from __future__ import annotations

import io
from typing import Any


def to_markdown(result: dict[str, Any]) -> str:
    """Render a panel result as Markdown — printable, paste-able, low-bandwidth."""
    lines: list[str] = []
    lines.append("# Panel — Your Contract Review")
    lines.append("")
    urg = result.get("final_urgency_score", "?")
    lines.append(f"**Urgency:** {urg}/10  ")
    lines.append(f"**Corridor:** {result.get('origin_country', '?')} → {result.get('destination_country', '?')}  ")
    lines.append(f"**Language:** {result.get('worker_l1', '?')}")
    lines.append("")

    rec = result.get("recommendation") or {}
    if rec.get("tldr"):
        lines.append("## Summary")
        lines.append("")
        lines.append(rec["tldr"])
        lines.append("")

    reel = result.get("disagreement_reel") or []
    if reel:
        lines.append("## Where the panel disagrees")
        lines.append("")
        for item in reel:
            lines.append(f"### #{item.get('rank', '?')} · {item.get('topic', '')}")
            for tension in item.get("tensions", []):
                lines.append(f"- **{tension.get('agent', '')}:** {tension.get('verdict', '')}")
            lines.append(f"_{item.get('why_it_matters', '')}_")
            lines.append("")

    cl = result.get("checklist") or {}
    if cl:
        lines.append("## Pre-departure checklist")
        lines.append("")
        for phase, items in (cl.get("phases") or {}).items():
            if not items:
                continue
            lines.append(f"### {phase.replace('_', ' ').title()}")
            for item in items:
                if isinstance(item, dict):
                    pr = (item.get("priority") or "").upper()
                    lines.append(f"- **[{pr}]** {item.get('action', '')}")
                    if item.get("details"):
                        lines.append(f"  - _{item['details']}_")
            lines.append("")

        refuse = cl.get("things_to_refuse") or []
        if refuse:
            lines.append("### Do NOT agree to")
            for r in refuse:
                if isinstance(r, dict):
                    lines.append(f"- **{r.get('refusal', '')}** — {r.get('reason_short', '')}")
            lines.append("")

        pushback = cl.get("recruiter_pushback") or []
        if pushback:
            lines.append("### Ask the recruiter to change")
            for p in pushback:
                if isinstance(p, dict):
                    lines.append(f"- Clause {p.get('clause_number', '?')}: {p.get('ask', '')}")
                    if p.get("suggested_text"):
                        lines.append(f"  - Suggested: _{p['suggested_text']}_")
            lines.append("")

    contacts = rec.get("contacts") or []
    if contacts:
        lines.append("## Contacts (save offline)")
        lines.append("")
        for c in contacts:
            line = f"- **{c.get('name', '')}**"
            if c.get("phone"):
                line += f" · {c['phone']}"
            if c.get("whatsapp"):
                line += f" · WhatsApp {c['whatsapp']}"
            lines.append(line)
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("_Panel provides information only — not legal advice. For urgent help, contact the embassy._")
    return "\n".join(lines)


def to_pdf(result: dict[str, Any]) -> bytes:
    """Render the panel result as a printable PDF."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import (Paragraph, SimpleDocTemplate, Spacer,
                                     Table, TableStyle)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=18 * mm, bottomMargin=18 * mm,
    )
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1p", parent=styles["Heading1"], textColor=colors.HexColor("#b71c1c"))
    h2 = styles["Heading2"]
    body = styles["BodyText"]

    story: list = []
    story.append(Paragraph("Panel — Your Contract Review", h1))

    urg = result.get("final_urgency_score", "?")
    story.append(Paragraph(
        f"<b>Urgency:</b> {urg}/10  &nbsp;&nbsp;"
        f"<b>Corridor:</b> {result.get('origin_country', '?')} → {result.get('destination_country', '?')}  &nbsp;&nbsp;"
        f"<b>Language:</b> {result.get('worker_l1', '?')}",
        body,
    ))
    story.append(Spacer(1, 6 * mm))

    rec = result.get("recommendation") or {}
    if rec.get("tldr"):
        story.append(Paragraph("Summary", h2))
        story.append(Paragraph(_escape(rec["tldr"]), body))
        story.append(Spacer(1, 4 * mm))

    reel = result.get("disagreement_reel") or []
    if reel:
        story.append(Paragraph("Where the panel disagrees", h2))
        for item in reel:
            story.append(Paragraph(
                f"<b>#{item.get('rank', '?')} — {_escape(item.get('topic', ''))}</b>", body,
            ))
            for t in item.get("tensions", []):
                story.append(Paragraph(
                    f"&bull; <b>{_escape(t.get('agent', ''))}:</b> {_escape(t.get('verdict', ''))}",
                    body,
                ))
            story.append(Paragraph(f"<i>{_escape(item.get('why_it_matters', ''))}</i>", body))
            story.append(Spacer(1, 3 * mm))

    cl = result.get("checklist") or {}
    phases = cl.get("phases") or {}
    if phases:
        story.append(Paragraph("Pre-departure checklist", h2))
        for phase, items in phases.items():
            if not items:
                continue
            story.append(Paragraph(f"<b>{phase.replace('_', ' ').title()}</b>", body))
            for it in items:
                if isinstance(it, dict):
                    pr = (it.get("priority") or "").upper()
                    story.append(Paragraph(
                        f"&bull; <b>[{pr}]</b> {_escape(it.get('action', ''))}",
                        body,
                    ))
            story.append(Spacer(1, 2 * mm))

    contacts = rec.get("contacts") or []
    if contacts:
        story.append(Paragraph("Contacts (save offline)", h2))
        for c in contacts:
            line = f"<b>{_escape(c.get('name', ''))}</b>"
            if c.get("phone"):
                line += f" · {_escape(c['phone'])}"
            if c.get("whatsapp"):
                line += f" · WhatsApp {_escape(c['whatsapp'])}"
            story.append(Paragraph(line, body))

    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph(
        "<i>Panel provides information only — not legal advice. "
        "For urgent help, contact the embassy.</i>",
        body,
    ))

    doc.build(story)
    return buf.getvalue()


def to_qr_png(payload: str) -> bytes:
    """Render a QR code as PNG bytes."""
    import qrcode
    img = qrcode.make(payload)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _escape(s: str) -> str:
    if not s:
        return ""
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
