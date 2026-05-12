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

from app import amendments, export, llm, ocr, providers, samples, style
from app.agents import run_panel


st.set_page_config(
    page_title="Panel",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

style.inject()


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
    "negotiator":    ("💬", "Negotiator",    "What to say before signing"),
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
    "negotiator":    ["Reading other agents' findings…", "Drafting questions in your language…", "Anticipating recruiter deflections…", "Picking the priority pushback…"],
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
def load_sample_contract(sample_id: str) -> str:
    text = samples.load(sample_id)
    if text:
        return text
    from app.llm import _MOCK_OCR
    return _MOCK_OCR


# ----------------------------------------------------------------------------
# Sidebar — backend status + provider details
# ----------------------------------------------------------------------------
def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("### 🔌 Backend")

        provider_ids = list(providers.PROVIDERS.keys())
        labels = {pid: spec["label"] for pid, spec in providers.PROVIDERS.items()}

        current = st.session_state.get("panel_provider") or providers.default_provider()
        choice = st.selectbox(
            "Provider",
            provider_ids,
            index=provider_ids.index(current) if current in provider_ids else 0,
            format_func=lambda pid: labels[pid],
            key="panel_provider",
        )
        spec = providers.PROVIDERS[choice]
        st.caption(spec["description"])

        keys = st.session_state.setdefault("panel_keys", {})
        models = st.session_state.setdefault("panel_models", {})

        if spec.get("needs_key"):
            env_value = os.environ.get(spec.get("env_key") or "")
            placeholder = "stored in session only — never written to disk"
            help_text = ""
            if env_value:
                help_text = f"_(env var `{spec['env_key']}` is set — leave blank to use it)_"
            keys[choice] = st.text_input(
                f"{spec['label']} API key",
                value=keys.get(choice, ""),
                type="password",
                placeholder=placeholder,
                help=help_text or None,
                key=f"key_input_{choice}",
            )

        if spec.get("needs_url"):
            st.session_state["panel_lmstudio_url"] = st.text_input(
                "Server URL",
                value=st.session_state.get("panel_lmstudio_url",
                                            "http://localhost:1234/v1/chat/completions"),
                key=f"url_input_{choice}",
            )

        if spec["models"]:
            current_model = models.get(choice) or spec["default_model"]
            models[choice] = st.selectbox(
                "Model",
                spec["models"],
                index=spec["models"].index(current_model) if current_model in spec["models"] else 0,
                key=f"model_input_{choice}",
            )
        elif spec.get("needs_url"):
            models[choice] = st.text_input(
                "Model name",
                value=models.get(choice, spec["default_model"]),
                help="The ID of the currently-loaded model in LM Studio (e.g. `qwen3-14b-mlx`).",
                key=f"model_freeform_{choice}",
            )

        if st.button("🔍 Test connection", use_container_width=True):
            with st.spinner("Pinging…"):
                ok, msg = providers.test(
                    choice,
                    key=keys.get(choice),
                    model=models.get(choice) or spec["default_model"],
                    url=st.session_state.get("panel_lmstudio_url"),
                )
            (st.success if ok else st.error)(msg)

        st.divider()

        if llm.is_live():
            st.success(f"Active: {llm.provider_label()}")
        else:
            st.info("Active: mock (no live backend)")

        st.markdown("### About")
        st.caption(
            "Panel is a multi-agent rights advisor for APJ migrant workers. "
            "6 specialist agents review your contract in parallel, surface where they disagree, "
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

    style.hero(
        title=s["title"],
        subtitle=s["subtitle"],
        stats=[
            ("Filipinos working abroad", "10M+"),
            ("Indonesians leaving / year", "700K"),
            ("legal aid before signing", "$0"),
        ],
        icon="⚖️",
    )

    # Source — registry sample vs upload your own.
    source = st.radio(
        s["source_label"],
        ["sample", "upload"],
        format_func=lambda k: s["source_sample"] if k == "sample" else s["source_upload"],
        horizontal=True,
    )

    contract_file = None
    sample_id: str | None = None
    origin: str
    destination: str

    if source == "sample":
        sample_ids = samples.all_ids()
        sample_id = st.selectbox(
            "Sample contract",
            sample_ids,
            format_func=lambda sid: f"{samples.SAMPLES[sid]['emoji']}  {samples.SAMPLES[sid]['label']}",
            key="sample_picker",
        )
        info = samples.SAMPLES[sample_id]
        tier_color, tier_label = samples.TIER_BADGE.get(info["tier"], ("#64748b", info["tier"].upper()))
        st.markdown(
            f"""
            <div style='display:flex;gap:8px;align-items:center;margin:4px 0 8px;'>
              <span class='sev-badge' style='background:{tier_color}1a;color:{tier_color};'>{tier_label}</span>
              <span style='font-size:13px;color:#64748b;'>{ORIGINS.get(info['origin'], info['origin'])} → {DESTINATIONS.get(info['destination'], info['destination'])}</span>
            </div>
            <div style='font-size:13px;color:#334155;line-height:1.5;margin-bottom:12px;'>{info['description']}</div>
            """,
            unsafe_allow_html=True,
        )
        origin = info["origin"]
        destination = info["destination"]
    else:
        col1, col2 = st.columns(2)
        with col1:
            origin = st.selectbox(
                s["origin_label"],
                list(ORIGINS.keys()),
                format_func=lambda k: ORIGINS[k],
            )
        with col2:
            destination = st.selectbox(
                s["dest_label"],
                list(DESTINATIONS.keys()),
                format_func=lambda k: DESTINATIONS[k],
            )
        contract_file = st.file_uploader(
            s["upload_label"], type=["jpg", "jpeg", "png", "pdf"], accept_multiple_files=False
        )
        if contract_file and contract_file.type.startswith("image/") \
                and providers.default_provider() == "claude_cli" \
                and not os.environ.get("ANTHROPIC_API_KEY"):
            st.warning(
                "🔑 Image OCR uses Anthropic vision and needs `ANTHROPIC_API_KEY`. "
                "Without it, mock OCR will be used. Upload a PDF or pick a sample for full live behaviour."
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
            "sample_id": sample_id,
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
            contract_text = load_sample_contract(intake.get("sample_id") or "ph_sa_domestic")
            source_label = f"sample · {intake.get('sample_id')}"
        else:
            raw = intake["contract_file"].getvalue()
            contract_text, source_label = ocr.extract_text(raw, mime_hint=intake["contract_mime"])
        status.update(label=f"📄 Contract loaded ({source_label}, {len(contract_text)} chars)", state="complete")

    # Stash for what-if simulator
    st.session_state["__last_contract_text"] = contract_text

    with st.expander("📋 Extracted contract text", expanded=False):
        st.text(contract_text[:3000] + ("…" if len(contract_text) > 3000 else ""))

    # ----- Step 2: launch panel with progress UI -----
    style.section_heading(
        eyebrow="Round 1 · Panel review",
        title=s["reviewing"],
        lede="6 specialist agents analyse the contract in parallel. Each lights up "
             "when its verdict lands. The slowest agent sets the wall clock.",
    )
    n_agents = len(AGENT_DISPLAY)
    progress = st.progress(0.0, text=f"0 / {n_agents} agents completed")
    panes = st.columns(n_agents)
    placeholders: dict[str, Any] = {}
    start_times: dict[str, float] = {}

    for pane, key in zip(panes, AGENT_DISPLAY.keys()):
        emoji, name, tagline = AGENT_DISPLAY[key]
        tint = style.AGENT_TINTS.get(key, "#64748b")
        with pane:
            placeholders[key] = st.empty()
            cycle = AGENT_STATUS_CYCLE.get(key, ["Working…"])
            placeholders[key].markdown(
                style.agent_card_waiting(emoji, name, tagline, cycle[0], tint),
                unsafe_allow_html=True,
            )
            start_times[key] = time.time()

    completed: dict[str, dict] = {}
    completed_count = [0]  # mutable closure target

    def on_done(name: str, output: dict) -> None:
        completed[name] = output
        completed_count[0] += 1
        progress.progress(
            completed_count[0] / n_agents,
            text=f"{completed_count[0]} / {n_agents} agents completed",
        )
        elapsed = (output.get("_latency_ms") or 0) / 1000.0
        emoji, label, _tagline = AGENT_DISPLAY[name]
        tint = style.AGENT_TINTS.get(name, "#64748b")
        verdict = output.get("verdict_summary", "(no summary)")
        findings = (output.get("key_findings") or [])[:4]
        placeholders[name].markdown(
            style.agent_card_done(emoji, label, elapsed, verdict, findings, tint),
            unsafe_allow_html=True,
        )

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
            emoji, label, _tagline = AGENT_DISPLAY[key]
            tint = style.AGENT_TINTS.get(key, "#64748b")
            verdict = output.get("verdict_summary", "(no summary)")
            findings = (output.get("key_findings") or [])[:4]
            placeholders[key].markdown(
                style.agent_card_done(emoji, label, None, verdict, findings, tint),
                unsafe_allow_html=True,
            )

    progress.empty()
    return result


# ----------------------------------------------------------------------------
# Disagreement reel — visual hierarchy: #1 hero, #2/#3 supporting
# ----------------------------------------------------------------------------
def render_disagreement_reel(result: dict[str, Any], lang: str) -> None:
    s = UI[lang]
    reel = result["disagreement_reel"]

    style.section_heading(
        eyebrow="The moat",
        title=s["disagree_header"],
        lede="Top tensions where the panel diverges. Differentiated by severity. "
             "The hero card is the strongest signal in the contract.",
    )

    if not reel:
        st.info("The panel reached consensus — no significant disagreements detected.")
        return

    hero = reel[0]
    sev = hero.get("severity", 5)
    tint, tint_soft, badge_label = _sev_palette(sev)
    badge_emoji, _, _ = _badge_for(sev)
    tensions_html = _tensions_html(hero["tensions"], compact=False)
    st.markdown(
        f"""
        <div class='reel-hero' style='--reel-tint: {tint}; --reel-tint-soft: {tint_soft};'>
          <div class='reel-rank'>#{hero['rank']} of {len(reel)}</div>
          <div class='reel-badge'>{badge_emoji} {badge_label}</div>
          <div class='reel-topic'>{hero['topic']}</div>
          <div class='reel-tensions'>{tensions_html}</div>
          <div class='reel-meaning'>{hero.get('why_it_matters', '')}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if len(reel) >= 2:
        sub = reel[1:3]
        cols = st.columns(len(sub))
        for col, item in zip(cols, sub):
            sev = item.get("severity", 5)
            tint, tint_soft, badge_label = _sev_palette(sev)
            badge_emoji, _, _ = _badge_for(sev)
            tensions_html = _tensions_html(item["tensions"][:3], compact=True)
            with col:
                st.markdown(
                    f"""
                    <div class='reel-sub' style='--reel-tint: {tint}; --reel-tint-soft: {tint_soft};'>
                      <div class='reel-rank'>#{item['rank']}</div>
                      <div class='reel-badge'>{badge_emoji} {badge_label}</div>
                      <div class='reel-topic'>{item['topic']}</div>
                      <div class='reel-tensions'>{tensions_html}</div>
                      <div class='reel-meaning'>{item.get('why_it_matters', '')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def _sev_palette(severity: int) -> tuple[str, str, str]:
    """Return (tint, tint_soft, label) for a severity tier."""
    key = max(5, min(10, int(severity)))
    color_map = {
        10: (style.COLORS["sev_10"], "#fee2e2", "CRITICAL"),
        9:  (style.COLORS["sev_9"],  "#fee2e2", "EMERGENCY"),
        8:  (style.COLORS["sev_8"],  "#ffedd5", "HIGH · legal but dangerous"),
        7:  (style.COLORS["sev_7"],  "#fef3c7", "HIGH · gray area"),
        6:  (style.COLORS["sev_6"],  "#fef9c3", "MEDIUM · international gap"),
        5:  (style.COLORS["sev_5"],  "#f1f5f9", "PRE-DECLARED"),
    }
    return color_map.get(key, color_map[5])


def _badge_for(severity: int) -> tuple[str, str, str]:
    return SEVERITY_BADGE.get(severity, SEVERITY_BADGE[5])


def _tensions_html(tensions: list, *, compact: bool) -> str:
    pieces: list[str] = []
    for t in tensions:
        if not isinstance(t, dict):
            continue
        agent_key = t.get("agent", "")
        display = AGENT_DISPLAY.get(agent_key)
        verdict = t.get("verdict") or "(no verdict)"
        if compact and len(verdict) > 140:
            verdict = verdict[:137] + "…"
        if display:
            emoji, name, _ = display
            tint = style.AGENT_TINTS.get(agent_key, "#64748b")
            agent_html = f"{emoji} {name}"
        else:
            tint = "#64748b"
            agent_html = agent_key
        pieces.append(
            f"<div class='reel-tension' style='--tension-tint: {tint};'>"
            f"<div class='reel-tension-agent'>{agent_html}</div>"
            f"<div class='reel-tension-verdict'>{verdict}</div></div>"
        )
    return "".join(pieces)


def _render_tension(tension: dict, *, compact: bool = False) -> None:
    """Legacy fallback for non-reel tension rendering."""
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
    style.section_heading(
        eyebrow="The verdict",
        title=s["rec_header"],
        lede="Synthesised across all six agents and Round 2 rebuttals. "
             "Read in your mother tongue, take with you.",
    )

    rec = result["recommendation"]
    urgency = result["final_urgency_score"]
    style.urgency_gauge(urgency)
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
    style.section_heading(
        eyebrow="Round 2 · The panel debates",
        title="🎙️ Where the panel pushes back",
        lede="After Round 1, each agent saw the others' findings and reacted. "
             "Watch the Lawyer concede to the Peer Advocate — that's the moment "
             "Panel earns its name.",
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
        responds_html = (
            f"<div class='rebuttal-responds'>→ {responds_to}</div>" if responds_to else ""
        )
        rebuttal_html = f"<div class='rebuttal-text'>{rebuttal_text}</div>" if rebuttal_text else ""
        with col:
            st.markdown(
                f"""
                <div class='rebuttal-card' style='--stance-tint: {s_color};'>
                  <div class='rebuttal-agent'>{emoji} {name}</div>
                  <div class='rebuttal-stance'>{s_emoji} {s_label}</div>
                  {responds_html}
                  {rebuttal_html}
                </div>
                """,
                unsafe_allow_html=True,
            )


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


def render_provenance(result: dict[str, Any]) -> None:
    """Per-reel-item drilldown showing the exact statute / case / clause cited."""
    reel = result.get("disagreement_reel") or []
    if not reel:
        return
    st.divider()
    st.subheader("🔍 Provenance — why the panel decided this")
    st.caption(
        "Every verdict in the reel above is backed by a specific statute, "
        "international convention, or archived case. Click to inspect."
    )
    agents = result.get("agents") or {}
    for item in reel:
        with st.expander(f"#{item.get('rank', '?')} · {item.get('topic', '')}"):
            topic = (item.get("topic") or "").lower().replace(" ", "_")
            citations: list[str] = []

            for c in (agents.get("lawyer") or {}).get("clause_analyses") or []:
                if not isinstance(c, dict):
                    continue
                ct = (c.get("clause_topic") or "").lower().replace(" ", "_")
                if ct and (ct in topic or topic in ct):
                    citations.append(
                        f"⚖️ **Lawyer** — *{c.get('verdict', '?')}*  \n"
                        f"&nbsp;&nbsp;**Statute:** `{c.get('statute', '?')}`  \n"
                        f"&nbsp;&nbsp;**Reasoning:** {c.get('reasoning', '?')}  \n"
                        f"&nbsp;&nbsp;**Clause excerpt:** _{c.get('clause_excerpt', '')[:200]}_"
                    )

            for area in (agents.get("regulator") or {}).get("core_area_analysis") or []:
                if not isinstance(area, dict):
                    continue
                at = (area.get("area") or "").lower().replace(" ", "_")
                if at and (at in topic or topic in at):
                    citations.append(
                        f"🏛️ **Regulator** — *{area.get('verdict', '?')}*  \n"
                        f"&nbsp;&nbsp;**ILO standard:** `{area.get('ilo_standard', '?')}`  \n"
                        f"&nbsp;&nbsp;**ASEAN standard:** `{area.get('asean_standard', '—')}`  \n"
                        f"&nbsp;&nbsp;**Ratification status:** {area.get('ratification_status', '?')}"
                    )

            for m in (agents.get("peer_advocate") or {}).get("clause_pattern_matches") or []:
                if not isinstance(m, dict):
                    continue
                pt = (m.get("clause_topic") or "").lower().replace(" ", "_")
                if pt and (pt in topic or topic in pt):
                    od = m.get("outcome_distribution") or {}
                    citations.append(
                        f"🫱🏽‍🫲🏾 **Peer Advocate** — *{m.get('similar_cases_count', '?')} similar cases*  \n"
                        f"&nbsp;&nbsp;**Resolved favorably:** {od.get('resolved_favorably', 0)}  \n"
                        f"&nbsp;&nbsp;**Returned early:** {od.get('worker_returned_early', 0)}  \n"
                        f"&nbsp;&nbsp;**Abuse reported:** {od.get('abuse_reported', 0)}  \n"
                        f"&nbsp;&nbsp;**Pattern warning:** {m.get('pattern_warning', '?')}"
                    )

            if citations:
                for cit in citations:
                    st.markdown(cit)
                    st.write("")
            else:
                st.info("No structured citations matched this topic — see agent summaries.")


def render_asean_diff(result: dict[str, Any]) -> None:
    """Side-by-side: contract clauses vs ASEAN / ILO standard."""
    regulator = (result.get("agents") or {}).get("regulator") or {}
    areas = regulator.get("core_area_analysis") or []
    if not areas:
        return
    st.divider()
    st.subheader("📊 This contract vs the ASEAN standard")
    st.caption(
        "Side-by-side comparison of each ILO core area. The Regulator agent's "
        "gap analysis, rendered as a diff."
    )

    VERDICT_COLORS = {
        "meets_standard":    ("#2e7d32", "Meets standard"),
        "below_standard":    ("#e64a19", "Below standard"),
        "prohibited_clause": ("#b71c1c", "Prohibited clause"),
        "silent":            ("#9e9e9e", "Silent"),
    }
    for area in areas:
        if not isinstance(area, dict):
            continue
        verdict_key = area.get("verdict", "silent")
        color, label = VERDICT_COLORS.get(verdict_key, ("#9e9e9e", verdict_key))
        with st.container(border=True):
            cols = st.columns([2, 4, 4])
            with cols[0]:
                st.markdown(
                    f"<div style='font-size:13px;color:{color};font-weight:700;'>{label.upper()}</div>"
                    f"<div style='font-size:16px;font-weight:600;'>{area.get('area', '?').replace('_', ' ').title()}</div>",
                    unsafe_allow_html=True,
                )
                if area.get("severity"):
                    st.caption(f"severity: {area['severity']}")
            with cols[1]:
                st.markdown("**This contract**")
                st.caption(area.get("contract_position", "(no extract)"))
            with cols[2]:
                st.markdown("**ASEAN / ILO standard**")
                ilo = area.get("ilo_standard", "")
                asean = area.get("asean_standard", "")
                if ilo:
                    st.caption(f"**ILO:** {ilo}")
                if asean:
                    st.caption(f"**ASEAN:** {asean}")
                if area.get("ratification_status"):
                    st.caption(f"_{area['ratification_status']}_")


def render_what_if(result: dict[str, Any], intake: dict[str, Any]) -> None:
    """Worker selects pushback items; simulate the recruiter agreeing; show urgency delta."""
    cl = result.get("checklist") or {}
    pushback = cl.get("recruiter_pushback") or []
    if not pushback:
        return
    st.divider()
    st.subheader("🪄 What if the recruiter agrees?")
    st.caption(
        "Select which pushback items you'd ask the recruiter to accept, then run "
        "the panel again on the amended contract. See how your urgency changes."
    )

    # Save the original contract text for replay
    contract_text = st.session_state.get("contract_text_for_replay")
    if not contract_text:
        st.info("Run the panel review above first to enable what-if simulation.")
        return

    selected_ids: list[int] = []
    for i, item in enumerate(pushback):
        if not isinstance(item, dict):
            continue
        cnum = item.get("clause_number", "?")
        ask = item.get("ask", "")
        if st.checkbox(f"**Clause {cnum}:** {ask}", key=f"whatif_{i}"):
            selected_ids.append(i)

    if not selected_ids:
        st.info("Select one or more amendments above to simulate.")
        return

    if not st.button("Simulate amendments", type="primary"):
        return

    selected = [pushback[i] for i in selected_ids]
    amended = amendments.amend_contract(contract_text, selected)

    with st.spinner(f"Re-running panel on amended contract ({len(selected)} changes)..."):
        amended_result = run_panel(
            contract_text=amended,
            situation=intake.get("situation", ""),
            destination_country=intake["destination"],
            origin_country=intake["origin"],
            worker_l1=intake["lang"],
            persist=False,
            run_round2=False,    # speed: skip Round 2 on simulation
            run_checklist=False, # speed: skip checklist on simulation
        )

    delta = amendments.urgency_delta(result, amended_result)
    cols = st.columns(3)
    with cols[0]:
        st.metric("Urgency before", f"{delta['urgency_before']}/10")
    with cols[1]:
        st.metric("Urgency after", f"{delta['urgency_after']}/10",
                  delta=f"-{delta['urgency_drop']}" if delta["urgency_drop"] > 0 else "0")
    with cols[2]:
        st.metric("Reel items", f"{delta['reel_after']}",
                  delta=f"{delta['reel_after'] - delta['reel_before']}")
    st.success(delta["verdict"])

    new_reel = amended_result.get("disagreement_reel") or []
    if new_reel:
        st.markdown("**Remaining tensions:**")
        for d in new_reel:
            st.markdown(f"- **#{d.get('rank', '?')} · sev {d.get('severity', '?')}** · {d.get('topic', '')}")
    else:
        st.success("No remaining tensions detected — panel reached consensus on the amended contract.")


def render_export(result: dict[str, Any]) -> None:
    """Download buttons + QR for the recommendation."""
    st.divider()
    st.subheader("📥 Take it with you")
    st.caption("Save this offline before flying. Print, screenshot, or share via WhatsApp.")

    cols = st.columns(3)
    with cols[0]:
        md_bytes = export.to_markdown(result).encode("utf-8")
        st.download_button(
            "Download Markdown",
            data=md_bytes,
            file_name="panel_review.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with cols[1]:
        try:
            pdf_bytes = export.to_pdf(result)
            st.download_button(
                "Download PDF",
                data=pdf_bytes,
                file_name="panel_review.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as exc:
            st.caption(f"PDF unavailable: {exc}")
    with cols[2]:
        # QR encodes a compact summary so peers can scan & save
        urg = result.get("final_urgency_score", "?")
        dest = result.get("destination_country", "?")
        orig = result.get("origin_country", "?")
        contacts = (result.get("recommendation") or {}).get("contacts") or []
        first_contact = contacts[0] if contacts else {}
        payload = (
            f"PANEL REVIEW\n"
            f"Urgency: {urg}/10\n"
            f"Corridor: {orig} -> {dest}\n"
            f"Embassy: {first_contact.get('name', '?')} {first_contact.get('phone', '')}\n"
        )
        try:
            qr_bytes = export.to_qr_png(payload)
            st.image(qr_bytes, caption="Scan to save offline", width=200)
        except Exception as exc:
            st.caption(f"QR unavailable: {exc}")


def render_negotiation(result: dict[str, Any], lang: str) -> None:
    """The Negotiator agent's output — conversation script for the recruiter meeting."""
    neg = (result.get("agents") or {}).get("negotiator") or {}
    if not isinstance(neg, dict) or neg.get("error"):
        return
    questions = neg.get("questions_to_ask") or []
    red_flags = neg.get("red_flag_responses") or []
    pushback = neg.get("priority_pushback") or {}
    strategy = neg.get("negotiation_strategy") or ""

    if not (questions or red_flags or pushback or strategy):
        return

    st.divider()
    st.subheader("💬 Negotiation coach — what to say before signing")
    st.caption(
        "Other agents diagnosed. This one coaches. Use these in your conversation "
        "with the recruiter or employer — information-gathering, not confrontation."
    )

    if strategy:
        with st.container(border=True):
            st.markdown(f"**Strategy:** {strategy}")

    if pushback and isinstance(pushback, dict) and pushback.get("what_to_say_in_l1"):
        st.markdown("### 🎯 Your priority pushback")
        with st.container(border=True):
            cnum = pushback.get("clause_number", "?")
            topic = pushback.get("topic", "")
            l1_text = pushback.get("what_to_say_in_l1", "")
            en_text = pushback.get("what_to_say_in_english", "")
            fallback = pushback.get("fallback_if_refused", "")
            walkaway = pushback.get("walk_away_threshold", "")
            st.markdown(
                f"<div style='font-size:11px;letter-spacing:1px;color:#b71c1c;font-weight:700;'>"
                f"CLAUSE {cnum} · {topic.upper()}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(f"**Say this:** _{l1_text}_")
            if en_text and lang != "en":
                st.caption(f"English: {en_text}")
            if fallback:
                st.markdown(f"**If they refuse:** {fallback}")
            if walkaway:
                st.error(f"🛑 **Walk away if:** {walkaway}")

    if questions:
        st.markdown("### ❓ Questions to ask")
        for i, q in enumerate(questions, 1):
            if not isinstance(q, dict):
                continue
            with st.container(border=True):
                cref = q.get("clause_reference", "general")
                why = q.get("why_ask", "")
                listen = q.get("what_to_listen_for", "")
                q_l1 = q.get("question_in_l1", "")
                q_en = q.get("question_in_english", "")
                st.markdown(
                    f"<div style='font-size:11px;letter-spacing:1px;color:#1976d2;font-weight:700;'>"
                    f"Q{i} · CLAUSE {cref}</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(f"**{q_l1}**")
                if q_en and lang != "en":
                    st.caption(f"English: _{q_en}_")
                if why:
                    st.markdown(f"_Why ask:_ {why}")
                if listen:
                    st.markdown(f"_Listen for:_ {listen}")

    if red_flags:
        st.markdown("### 🚩 Red-flag responses to listen for")
        for rf in red_flags:
            if not isinstance(rf, dict):
                continue
            with st.container(border=True):
                says = rf.get("if_recruiter_says", "")
                means = rf.get("what_it_actually_means", "")
                move = rf.get("your_move", "")
                st.markdown(f'**If the recruiter says:** _"{says}"_')
                st.markdown(f"**It actually means:** {means}")
                if move:
                    st.markdown(f"**Your move:** {move}")


def _topbar_for_intake(intake: dict[str, Any] | None) -> None:
    if not intake:
        crumb = "Pick a sample or upload a contract"
    else:
        orig = ORIGINS.get(intake.get("origin", ""), intake.get("origin", ""))
        dest = DESTINATIONS.get(intake.get("destination", ""), intake.get("destination", ""))
        lang = LANGUAGES.get(intake.get("lang", "en"), "")
        crumb = f"{orig} → {dest}  ·  {lang}"
    status_label = llm.provider_label() if llm.is_live() else "MOCK"
    tone = "ok" if llm.is_live() else "warn"
    style.top_bar(brand="Panel", crumb=crumb, status_label=status_label, status_tone=tone)


def main() -> None:
    render_sidebar()
    _topbar_for_intake(None)
    intake = render_intake()
    if intake is None:
        return
    result = render_panel_review(intake)
    # Stash for what-if replay
    st.session_state["contract_text_for_replay"] = result.get("agents", {}).get(
        "translator", {}
    ).get("__contract_text") or _last_contract_text()
    render_disagreement_reel(result, intake["lang"])
    render_provenance(result)
    render_rebuttals(result)
    render_asean_diff(result)
    render_checklist(result, intake["lang"])
    render_negotiation(result, intake["lang"])
    render_what_if(result, intake)
    render_recommendation(result, intake["lang"])
    render_export(result)


def _last_contract_text() -> str:
    """Fallback: pull from session state if render_panel_review stashed it."""
    return st.session_state.get("__last_contract_text", "")


if __name__ == "__main__":
    main()
