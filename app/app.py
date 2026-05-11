"""Panel — Streamlit entry point.

Run locally: streamlit run app/app.py
Deploys to Databricks Apps via `databricks bundle deploy`.

Pages:
- This file: the worker-facing contract review.
- app/pages/2_📊_NGO_Dashboard.py: aggregate abuse-pattern dashboard.
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

# Ensure the project root is on sys.path so `from app import ...` resolves
# regardless of how Streamlit launches us.
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from typing import Any

import streamlit as st

from app import llm, ocr
from app.agents import run_panel


st.set_page_config(
    page_title="Panel",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ----------------------------------------------------------------------------
# Static config
# ----------------------------------------------------------------------------
LANGUAGES = {
    "tl": "Tagalog / Filipino",
    "id": "Bahasa Indonesia",
    "en": "English",
}

DESTINATIONS = {
    "SA": "Saudi Arabia",
    "MY": "Malaysia",
    "SG": "Singapore",
    "HK": "Hong Kong SAR",
    "AE": "United Arab Emirates",
}

ORIGINS = {
    "PH": "Philippines",
    "ID": "Indonesia",
}

UI = {
    "tl": {
        "title": "Panel",
        "subtitle": "Tinitingnan ng panel ng AI ang iyong kontrata — sa iyong wika.",
        "lang_label": "Ang wika mo",
        "origin_label": "Saan ka galing?",
        "dest_label": "Saan ka magtatrabaho?",
        "source_label": "Pagmulan ng kontrata",
        "source_sample": "Halimbawa kontrata (PH → SA)",
        "source_upload": "I-upload ang sarili mong kontrata",
        "upload_label": "I-upload ang kontrata mo (litrato o PDF)",
        "situation_label": "Ilarawan ang sitwasyon mo (opsyonal)",
        "go_button": "Suriin ng panel",
        "reviewing": "Sinusuri ng panel...",
        "disagree_header": "Saan hindi nagkakasundo ang panel",
        "rec_header": "Rekomendasyon",
        "actions_header": "Dapat mong gawin",
        "contacts_header": "Mga kontak",
        "disclaimer": "Ang Panel ay nagbibigay lamang ng impormasyon. Hindi ito legal na payo. Para sa agarang tulong, tumawag sa embahada.",
    },
    "id": {
        "title": "Panel",
        "subtitle": "Panel AI membaca kontrak Anda — dalam bahasa Anda.",
        "lang_label": "Bahasa Anda",
        "origin_label": "Anda dari negara mana?",
        "dest_label": "Di mana Anda akan bekerja?",
        "source_label": "Sumber kontrak",
        "source_sample": "Kontrak contoh (ID → MY)",
        "source_upload": "Unggah kontrak Anda sendiri",
        "upload_label": "Unggah kontrak (foto atau PDF)",
        "situation_label": "Ceritakan situasi Anda (opsional)",
        "go_button": "Tinjauan panel",
        "reviewing": "Panel sedang meninjau...",
        "disagree_header": "Di mana panel tidak sepakat",
        "rec_header": "Rekomendasi",
        "actions_header": "Yang harus Anda lakukan",
        "contacts_header": "Kontak",
        "disclaimer": "Panel hanya memberikan informasi, bukan nasihat hukum. Untuk bantuan darurat, hubungi kedutaan.",
    },
    "en": {
        "title": "Panel",
        "subtitle": "A panel of AI specialists reads your contract — in your language.",
        "lang_label": "Your language",
        "origin_label": "Where are you from?",
        "dest_label": "Where are you going to work?",
        "source_label": "Contract source",
        "source_sample": "Use sample contract (PH → SA)",
        "source_upload": "Upload your own contract",
        "upload_label": "Upload your contract (photo or PDF)",
        "situation_label": "Describe your situation in your own words (optional)",
        "go_button": "Get panel review",
        "reviewing": "Panel reviewing...",
        "disagree_header": "Where the panel disagrees",
        "rec_header": "Recommendation",
        "actions_header": "What to do",
        "contacts_header": "Contacts",
        "disclaimer": "Panel provides information only — not legal advice. For urgent help, contact the embassy.",
    },
}

AGENT_DISPLAY = {
    "lawyer":        ("⚖️", "Lawyer",        "Local labor law"),
    "translator":    ("🌐", "Translator",    "Plain language in your L1"),
    "regulator":     ("🏛️", "Regulator",     "ILO / ASEAN standards"),
    "peer_advocate": ("🫱🏽‍🫲🏾", "Peer Advocate", "Similar past cases"),
    "triage":        ("🚨", "Triage",        "Urgency & contacts"),
}

STANCE_BADGE = {
    "concede":   ("🤝", "#4caf50", "Concedes"),
    "push_back": ("⚔️",  "#d32f2f", "Pushes back"),
    "extend":    ("➕", "#1976d2", "Extends"),
}

PHASE_LABELS = {
    "before_departure":   "Before departure",
    "on_arrival":         "On arrival",
    "during_employment":  "During employment",
    "exit_emergency":     "Exit / emergency",
}

PRIORITY_COLOR = {"critical": "#b71c1c", "high": "#e64a19", "medium": "#fbc02d"}

# In-flight status messages cycled per agent during the wait, to fight dead air.
AGENT_STATUS_CYCLE = {
    "lawyer":        ["Segmenting clauses…", "Querying labor code…", "Cross-referencing statutes…", "Drafting verdicts…"],
    "translator":    ["Detecting source language…", "Translating clauses…", "Flagging ambiguities…", "Composing L1 summary…"],
    "regulator":     ["Loading ILO conventions…", "Comparing to ASEAN standard…", "Scoring 8 core areas…", "Building gap analysis…"],
    "peer_advocate": ["Loading case archive…", "Matching by clause topic…", "Tallying outcomes…", "Looking for patterns…"],
    "triage":        ["Scanning trafficking indicators…", "Cross-referencing situation…", "Scoring urgency…", "Routing to contacts…"],
}

SEVERITY_BADGE = {
    10: ("🚨", "#b71c1c", "CRITICAL — multi-agent convergence on top indicator"),
    9:  ("🚨", "#d32f2f", "EMERGENCY — trafficking indicator + ≥2 agents agree"),
    8:  ("⚠️", "#e64a19", "HIGH — legal but historically dangerous"),
    7:  ("⚠️", "#f57c00", "HIGH — gray area + bad outcomes"),
    6:  ("⚡", "#fbc02d", "MEDIUM — gap with international standard"),
    5:  ("•",  "#757575", "Pre-declared tension"),
}


# ----------------------------------------------------------------------------
# Sample contract loader
# ----------------------------------------------------------------------------
SAMPLES = {
    ("PH", "SA"): Path(__file__).parent / "data" / "demo_contracts" / "ph_sa_domestic_worker.txt",
    ("ID", "MY"): Path(__file__).parent / "data" / "demo_contracts" / "id_my_construction.txt",
}


def load_sample_contract(origin: str, destination: str) -> str:
    path = SAMPLES.get((origin, destination))
    if path and path.exists():
        return path.read_text(encoding="utf-8")
    # Fallback: PH→SA hero case
    fallback = SAMPLES[("PH", "SA")]
    if fallback.exists():
        return fallback.read_text(encoding="utf-8")
    from app.llm import _MOCK_OCR
    return _MOCK_OCR


def has_sample(origin: str, destination: str) -> bool:
    path = SAMPLES.get((origin, destination))
    return bool(path and path.exists())


# ----------------------------------------------------------------------------
# Sidebar — backend status + provider details
# ----------------------------------------------------------------------------
def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("### Backend")
        if llm.is_live():
            st.success(f"LLM: {llm.provider_label()}")
        else:
            st.info("LLM: mock mode\n\n*Install `claude` CLI or set `ANTHROPIC_API_KEY`.*")

        with st.expander("Provider details"):
            st.markdown(
                f"- Active: **`{llm.PROVIDER}`**\n"
                f"- Anthropic API key: {'set' if os.environ.get('ANTHROPIC_API_KEY') else 'not set'}\n"
                f"- `claude` CLI: {'available' if llm._claude_cli_available() else 'not found'}\n"
                f"- Force with `PANEL_LLM_PROVIDER=claude_cli|anthropic|mock`"
            )
            if llm.PROVIDER == "claude_cli" and not os.environ.get("ANTHROPIC_API_KEY"):
                st.caption(
                    "⚠️ Image OCR needs the Anthropic SDK. Without `ANTHROPIC_API_KEY`, "
                    "image uploads will fall back to mock OCR. Use the sample contract "
                    "or upload a PDF for full live behavior."
                )
        st.markdown("### About")
        st.caption(
            "Panel is a multi-agent rights advisor for APJ migrant workers. "
            "5 specialist agents review your contract in parallel, surface where they disagree, "
            "and synthesize a recommendation in your mother tongue."
        )
        st.caption("Built for the Databricks Building Intelligent Apps Hackathon, May 2026.")


# ----------------------------------------------------------------------------
# Intake
# ----------------------------------------------------------------------------
def render_intake() -> dict[str, Any] | None:
    lang_choice = st.selectbox(
        "Language / Wika / Bahasa",
        list(LANGUAGES.keys()),
        format_func=lambda k: LANGUAGES[k],
        index=0,
        key="lang_picker",
    )
    s = UI[lang_choice]

    st.title(s["title"])
    st.caption(s["subtitle"])

    col1, col2 = st.columns(2)
    with col1:
        origin = st.selectbox(
            s["origin_label"],
            list(ORIGINS.keys()),
            format_func=lambda k: ORIGINS[k],
            index=0 if lang_choice == "tl" else (1 if lang_choice == "id" else 0),
        )
    with col2:
        destination = st.selectbox(
            s["dest_label"],
            list(DESTINATIONS.keys()),
            format_func=lambda k: DESTINATIONS[k],
            index=0 if lang_choice == "tl" else 1,
        )

    sample_available = has_sample(origin, destination)
    if not sample_available:
        st.info(f"No sample contract for {ORIGINS[origin]} → {DESTINATIONS[destination]}. "
                f"Switch corridor or upload your own.")

    source_options = (["sample", "upload"] if sample_available else ["upload"])
    source = st.radio(
        s["source_label"],
        source_options,
        format_func=lambda k: s["source_sample"] if k == "sample" else s["source_upload"],
        horizontal=True,
    )

    contract_file = None
    if source == "upload":
        contract_file = st.file_uploader(
            s["upload_label"], type=["jpg", "jpeg", "png", "pdf"], accept_multiple_files=False
        )
        if contract_file and contract_file.type.startswith("image/") and llm.PROVIDER == "claude_cli" \
                and not os.environ.get("ANTHROPIC_API_KEY"):
            st.warning(
                "🔑 Image OCR uses Anthropic vision and needs `ANTHROPIC_API_KEY`. "
                "Without it, mock OCR will be used. Upload a PDF or use the sample contract for full live behavior."
            )

    situation = st.text_area(s["situation_label"], height=100, placeholder="...")

    go = st.button(s["go_button"], type="primary", use_container_width=True)
    if go:
        if source == "upload" and not contract_file:
            st.warning(s["upload_label"])
            return None
        return {
            "lang": lang_choice,
            "origin": origin,
            "destination": destination,
            "source": source,
            "contract_file": contract_file,
            "contract_mime": contract_file.type if contract_file else None,
            "situation": situation,
        }
    return None


# ----------------------------------------------------------------------------
# Panel review (with progressive reveal + per-agent timing)
# ----------------------------------------------------------------------------
def render_panel_review(intake: dict[str, Any]) -> dict[str, Any]:
    s = UI[intake["lang"]]

    # ----- Step 1: OCR / load contract -----
    with st.status("📄 Reading contract…", expanded=True) as status:
        if intake["source"] == "sample":
            contract_text = load_sample_contract(intake["origin"], intake["destination"])
            source_label = "sample"
        else:
            raw = intake["contract_file"].getvalue()
            contract_text, source_label = ocr.extract_text(raw, mime_hint=intake["contract_mime"])
        status.update(label=f"📄 Contract loaded ({source_label}, {len(contract_text)} chars)", state="complete")

    with st.expander("📋 Extracted contract text", expanded=False):
        st.text(contract_text[:3000] + ("…" if len(contract_text) > 3000 else ""))

    # ----- Step 2: launch panel with progress UI -----
    st.subheader(s["reviewing"])
    progress = st.progress(0.0, text="0 / 5 agents completed")
    panes = st.columns(5)
    placeholders: dict[str, Any] = {}
    start_times: dict[str, float] = {}

    for pane, key in zip(panes, AGENT_DISPLAY.keys()):
        emoji, name, tagline = AGENT_DISPLAY[key]
        with pane:
            st.markdown(f"### {emoji} {name}")
            st.caption(tagline)
            placeholders[key] = st.empty()
            cycle = AGENT_STATUS_CYCLE.get(key, ["Working…"])
            placeholders[key].info(f"⏳ {cycle[0]}")
            start_times[key] = time.time()

    completed: dict[str, dict] = {}
    completed_count = [0]  # mutable closure target

    def on_done(name: str, output: dict) -> None:
        completed[name] = output
        completed_count[0] += 1
        progress.progress(
            completed_count[0] / 5,
            text=f"{completed_count[0]} / 5 agents completed",
        )
        elapsed = (output.get("_latency_ms") or 0) / 1000.0
        with placeholders[name].container():
            head = f"✓ **{output.get('verdict_summary', '(no summary)')}**"
            if elapsed > 0:
                head += f"  \n*completed in {elapsed:.1f}s*"
            st.markdown(head)
            for finding in (output.get("key_findings") or [])[:4]:
                st.markdown(f"- {finding}")

    # Run the panel
    result = run_panel(
        contract_text=contract_text,
        situation=intake["situation"],
        destination_country=intake["destination"],
        origin_country=intake["origin"],
        worker_l1=intake["lang"],
        on_agent_done=on_done,
    )

    # Defensive: render any agent that didn't fire the callback (rare race).
    for key in AGENT_DISPLAY:
        if key not in completed:
            output = result["agents"].get(key, {})
            with placeholders[key].container():
                st.markdown(f"**{output.get('verdict_summary', '(no summary)')}**")
                for finding in (output.get("key_findings") or [])[:4]:
                    st.markdown(f"- {finding}")

    progress.empty()
    return result


# ----------------------------------------------------------------------------
# Disagreement reel — visual hierarchy: #1 hero, #2/#3 supporting
# ----------------------------------------------------------------------------
def render_disagreement_reel(result: dict[str, Any], lang: str) -> None:
    s = UI[lang]
    st.divider()
    st.subheader(s["disagree_header"])

    reel = result["disagreement_reel"]
    if not reel:
        st.info("The panel reached consensus — no significant disagreements detected.")
        return

    # Hero (#1) — colored container, large header
    hero = reel[0]
    badge_emoji, badge_color, badge_label = _badge_for(hero.get("severity", 5))
    with st.container(border=True):
        st.markdown(
            f"<div style='border-left:6px solid {badge_color};padding:8px 16px;background:rgba(211,47,47,0.05);'>"
            f"<div style='font-size:11px;letter-spacing:1px;color:{badge_color};font-weight:700;'>"
            f"{badge_emoji} #{hero['rank']} · {badge_label}</div>"
            f"<div style='font-size:22px;font-weight:600;margin-top:4px;'>{hero['topic']}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.write("")
        for tension in hero["tensions"]:
            _render_tension(tension)
        st.caption(f"_{hero['why_it_matters']}_")

    # Supporting (#2, #3) — side by side
    if len(reel) >= 2:
        st.write("")
        cols = st.columns(min(2, len(reel) - 1))
        for col, item in zip(cols, reel[1:3]):
            badge_emoji, badge_color, badge_label = _badge_for(item.get("severity", 5))
            with col:
                with st.container(border=True):
                    st.markdown(
                        f"<div style='font-size:10px;letter-spacing:1px;color:{badge_color};font-weight:700;'>"
                        f"{badge_emoji} #{item['rank']} · {badge_label}</div>"
                        f"<div style='font-size:16px;font-weight:600;margin-top:2px;'>{item['topic']}</div>",
                        unsafe_allow_html=True,
                    )
                    st.write("")
                    for tension in item["tensions"][:3]:
                        _render_tension(tension, compact=True)
                    st.caption(f"_{item['why_it_matters']}_")


def _badge_for(severity: int) -> tuple[str, str, str]:
    return SEVERITY_BADGE.get(severity, SEVERITY_BADGE[5])


def _render_tension(tension: dict, *, compact: bool = False) -> None:
    agent_key = tension["agent"]
    display = AGENT_DISPLAY.get(agent_key)
    verdict = tension.get("verdict") or "(no verdict)"
    if display:
        emoji, name, _ = display
        label = f"{emoji} **{name}:**"
    else:
        label = f"**{agent_key}:**"
    if compact and len(verdict) > 140:
        verdict = verdict[:137] + "…"
    st.markdown(f"- {label} {verdict}")


# ----------------------------------------------------------------------------
# Recommendation
# ----------------------------------------------------------------------------
def render_recommendation(result: dict[str, Any], lang: str) -> None:
    s = UI[lang]
    st.divider()
    st.subheader(s["rec_header"])

    rec = result["recommendation"]
    urgency = result["final_urgency_score"]

    if urgency >= 7:
        st.error(f"⚠️ Urgency: {urgency}/10")
    elif urgency >= 4:
        st.warning(f"Urgency: {urgency}/10")
    else:
        st.success(f"Urgency: {urgency}/10")

    st.markdown(f"**{rec['tldr']}**")

    if rec.get("action_items"):
        st.markdown(f"**{s['actions_header']}:**")
        for item in rec["action_items"]:
            st.markdown(f"- {item}")

    if rec.get("contacts"):
        st.markdown(f"**{s['contacts_header']}:**")
        for contact in rec["contacts"]:
            line = f"- **{contact.get('name', '')}**"
            if contact.get("phone"):
                line += f" — `{contact['phone']}`"
            if contact.get("whatsapp"):
                line += f" — WhatsApp `{contact['whatsapp']}`"
            st.markdown(line)

    st.caption(s["disclaimer"])

    with st.expander("🔍 Full panel output (debug)"):
        st.json(result)


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def render_rebuttals(result: dict[str, Any]) -> None:
    """Round 2: each agent's reaction to the other four."""
    rebuttals = result.get("rebuttals") or {}
    if not rebuttals or rebuttals.get("_error"):
        return
    st.divider()
    st.subheader("🎙️ Round 2 · Panel reacts to itself")
    st.caption(
        "After Round 1, each agent saw the others' findings. "
        "Here's where they concede, push back, or extend the panel's analysis."
    )
    cols = st.columns(len(AGENT_DISPLAY))
    for col, agent_key in zip(cols, AGENT_DISPLAY.keys()):
        out = rebuttals.get(agent_key)
        if not isinstance(out, dict):
            continue
        emoji, name, _ = AGENT_DISPLAY[agent_key]
        stance = (out.get("stance") or "extend").lower()
        s_emoji, s_color, s_label = STANCE_BADGE.get(stance, STANCE_BADGE["extend"])
        responds_to = (out.get("responds_to") or "").strip()
        rebuttal_text = (out.get("rebuttal") or "").strip()
        with col:
            with st.container(border=True):
                st.markdown(f"**{emoji} {name}**")
                st.markdown(
                    f"<span style='color:{s_color};font-size:11px;letter-spacing:1px;font-weight:700;'>"
                    f"{s_emoji} {s_label.upper()}</span>",
                    unsafe_allow_html=True,
                )
                if responds_to:
                    st.caption(f"→ {responds_to}")
                if rebuttal_text:
                    st.markdown(f"*{rebuttal_text}*")


def render_checklist(result: dict[str, Any], lang: str) -> None:
    """Concrete printable checklist for the worker, in their L1."""
    cl = result.get("checklist") or {}
    if not cl or cl.get("_error"):
        return
    st.divider()
    st.subheader("📋 Pre-departure checklist")
    st.caption("Save these items offline before you fly. Print or screenshot.")

    phases = cl.get("phases") or {}
    if phases:
        tabs = st.tabs([PHASE_LABELS.get(k, k.replace('_', ' ').title()) for k in phases.keys()])
        for tab, (phase_key, items) in zip(tabs, phases.items()):
            with tab:
                if not items:
                    st.info("No items for this phase.")
                    continue
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    pr = (item.get("priority") or "medium").lower()
                    color = PRIORITY_COLOR.get(pr, "#757575")
                    action = item.get("action", "")
                    details = item.get("details", "")
                    st.markdown(
                        f"<div style='border-left:4px solid {color};padding:4px 12px;margin:6px 0;'>"
                        f"<div style='font-weight:600;'>{action}</div>"
                        f"<div style='font-size:13px;color:#555;'>{details}</div>"
                        f"<div style='font-size:10px;letter-spacing:1px;color:{color};font-weight:700;text-transform:uppercase;'>{pr}</div>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

    refuse = cl.get("things_to_refuse") or []
    if refuse:
        st.markdown("**🛑 Do NOT agree to:**")
        for item in refuse:
            if isinstance(item, dict):
                st.markdown(f"- **{item.get('refusal', '')}** — {item.get('reason_short', '')}")

    pushback = cl.get("recruiter_pushback") or []
    if pushback:
        st.markdown("**📝 Ask the recruiter to change before signing:**")
        for item in pushback:
            if isinstance(item, dict):
                cnum = item.get("clause_number", "")
                ask = item.get("ask", "")
                suggested = item.get("suggested_text", "")
                with st.container(border=True):
                    st.markdown(f"**Clause {cnum}:** {ask}")
                    if suggested:
                        st.caption(f"Suggested replacement: _{suggested}_")


def main() -> None:
    render_sidebar()
    intake = render_intake()
    if intake is None:
        return
    result = render_panel_review(intake)
    render_disagreement_reel(result, intake["lang"])
    render_rebuttals(result)
    render_checklist(result, intake["lang"])
    render_recommendation(result, intake["lang"])


if __name__ == "__main__":
    main()
