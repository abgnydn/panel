"""Centralised UI styling for Panel.

Approach: minimal CSS, strong typographic rhythm, restrained palette.
Inspired by Stripe / Linear / Notion — confident neutral, semantic accents.

Call `inject()` once at the top of every Streamlit page entry script.
"""
from __future__ import annotations

import streamlit as st

# ---------------------------------------------------------------------------
# Palette  (mirrors .streamlit/config.toml and adds semantic accents)
# ---------------------------------------------------------------------------
COLORS = {
    "ink":          "#0f172a",
    "ink_soft":     "#334155",
    "muted":        "#64748b",
    "border":       "#e2e8f0",
    "surface":      "#ffffff",
    "page":         "#fafaf9",
    "warm_tint":    "#fef3c7",
    # Severity ramp
    "sev_10":       "#b91c1c",   # crimson
    "sev_9":        "#dc2626",   # red
    "sev_8":        "#ea580c",   # deep orange
    "sev_7":        "#f59e0b",   # amber
    "sev_6":        "#eab308",   # yellow
    "sev_5":        "#737373",   # neutral
    # Stance
    "stance_concede":   "#16a34a",
    "stance_push_back": "#dc2626",
    "stance_extend":    "#2563eb",
    # Agent tints
    "agent_lawyer":     "#1e40af",  # navy
    "agent_translator": "#0d9488",  # teal
    "agent_regulator":  "#7c3aed",  # violet
    "agent_peer":       "#0891b2",  # cyan
    "agent_triage":     "#dc2626",  # red
    "agent_negotiator": "#d97706",  # amber
}

AGENT_TINTS = {
    "lawyer":        COLORS["agent_lawyer"],
    "translator":    COLORS["agent_translator"],
    "regulator":     COLORS["agent_regulator"],
    "peer_advocate": COLORS["agent_peer"],
    "triage":        COLORS["agent_triage"],
    "negotiator":    COLORS["agent_negotiator"],
}


_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --ink: #0f172a;
  --ink-soft: #334155;
  --muted: #64748b;
  --border: #e2e8f0;
  --surface: #ffffff;
  --page: #fafaf9;
  --accent: #dc2626;
  --warm-tint: #fef3c7;
}

/* -------------------------------------------------------------------------
   Global typography + spacing
   ------------------------------------------------------------------------- */
html, body, [data-testid="stAppViewContainer"] {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  -webkit-font-smoothing: antialiased;
}
[data-testid="stAppViewContainer"] > .main { padding-top: 0; }
.main .block-container { padding-top: 2rem; padding-bottom: 6rem; max-width: 1180px; }

h1, h2, h3, h4 { font-family: 'Inter', sans-serif; letter-spacing: -0.02em; color: var(--ink); }
h1 { font-weight: 800; }
h2 { font-weight: 700; }
h3 { font-weight: 600; }
p, span, li, div { color: var(--ink); }

code, kbd, samp { font-family: 'JetBrains Mono', monospace; font-size: 0.85em; }

/* -------------------------------------------------------------------------
   Sidebar
   ------------------------------------------------------------------------- */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #ffffff 0%, #fafaf9 100%);
  border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] h3 {
  font-size: 13px !important;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
  font-weight: 700;
  margin-top: 1.5rem;
}

/* -------------------------------------------------------------------------
   Hero header
   ------------------------------------------------------------------------- */
.panel-hero {
  position: relative;
  padding: 36px 40px;
  border-radius: 18px;
  background:
    radial-gradient(ellipse at top right, rgba(220,38,38,0.06) 0%, transparent 60%),
    linear-gradient(135deg, var(--warm-tint) 0%, #ffffff 70%);
  border: 1px solid #fde68a;
  margin-bottom: 28px;
  overflow: hidden;
}
.panel-hero::before {
  content: '';
  position: absolute; top: 0; right: 0;
  width: 280px; height: 280px;
  background: radial-gradient(circle at center, rgba(220,38,38,0.04), transparent 70%);
  pointer-events: none;
}
.panel-hero-row { display: flex; align-items: center; gap: 24px; }
.panel-hero-mark {
  font-size: 64px; line-height: 1;
  filter: drop-shadow(0 4px 12px rgba(15,23,42,0.08));
}
.panel-hero-title {
  font-size: 52px; font-weight: 800; line-height: 1.05; margin: 0;
  letter-spacing: -0.04em; color: var(--ink);
}
.panel-hero-sub {
  font-size: 18px; color: var(--ink-soft); margin: 8px 0 0;
  line-height: 1.5; max-width: 640px;
}
.panel-hero-stats {
  display: flex; flex-wrap: wrap; gap: 10px;
  margin-top: 18px;
}
.panel-hero-stat {
  background: var(--surface);
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 13px; font-weight: 600;
  color: var(--ink-soft);
  border: 1px solid var(--border);
  box-shadow: 0 1px 2px rgba(15,23,42,0.04);
}
.panel-hero-stat b { color: var(--accent); }

/* -------------------------------------------------------------------------
   Section headers
   ------------------------------------------------------------------------- */
.panel-section-eyebrow {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--muted);
  font-weight: 700;
  margin-bottom: 4px;
}
.panel-section-title {
  font-size: 26px;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0 0 8px;
}
.panel-section-lede {
  color: var(--muted);
  font-size: 15px;
  max-width: 680px;
  line-height: 1.5;
  margin-bottom: 20px;
}

/* -------------------------------------------------------------------------
   Agent cards (per-agent reveal during panel run)
   ------------------------------------------------------------------------- */
.agent-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 18px;
  height: 100%;
  display: flex; flex-direction: column;
  gap: 6px;
  transition: all 200ms ease;
  position: relative;
  overflow: hidden;
}
.agent-card-waiting {
  background: linear-gradient(135deg, #fafaf9, #ffffff);
}
.agent-card-done {
  background: var(--surface);
  box-shadow: 0 1px 3px rgba(15,23,42,0.05);
}
.agent-card::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
  background: var(--agent-tint, var(--border));
}
.agent-card-icon { font-size: 24px; line-height: 1; }
.agent-card-name {
  font-size: 15px; font-weight: 700;
  color: var(--ink); margin-top: 2px;
  display: flex; align-items: center; justify-content: space-between; gap: 6px;
}
.agent-card-latency {
  font-size: 11px; font-weight: 500;
  color: var(--muted);
  background: #f1f5f9;
  padding: 2px 8px; border-radius: 999px;
  letter-spacing: 0.02em;
}
.agent-card-tagline {
  font-size: 12px; color: var(--muted);
  margin-bottom: 6px;
}
.agent-card-status {
  display: flex; align-items: center; gap: 8px;
  font-size: 13px; color: var(--ink-soft);
  padding: 8px 12px;
  background: linear-gradient(90deg, rgba(220,38,38,0.04), transparent);
  border-radius: 8px;
}
.agent-card-status .dot {
  width: 7px; height: 7px; border-radius: 999px;
  background: var(--agent-tint, var(--accent));
  animation: pulse 1.4s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%      { opacity: 0.4; transform: scale(0.85); }
}
.agent-card-verdict {
  font-size: 14px; font-weight: 600; line-height: 1.4;
  color: var(--ink); margin-top: 2px;
}
.agent-card-findings {
  margin: 6px 0 0; padding: 0; list-style: none;
}
.agent-card-findings li {
  font-size: 12.5px; color: var(--ink-soft);
  padding: 4px 0 4px 14px;
  position: relative; line-height: 1.45;
}
.agent-card-findings li::before {
  content: '•'; position: absolute; left: 0; color: var(--agent-tint);
  font-weight: 700;
}

/* -------------------------------------------------------------------------
   Disagreement reel — hero #1 and supporting cards
   ------------------------------------------------------------------------- */
.reel-hero {
  position: relative;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 28px 32px;
  margin: 16px 0 20px;
  box-shadow: 0 8px 24px rgba(15,23,42,0.06);
  overflow: hidden;
}
.reel-hero::before {
  content: '';
  position: absolute; left: 0; top: 0; bottom: 0;
  width: 6px; background: var(--reel-tint);
}
.reel-hero::after {
  content: '';
  position: absolute; right: -80px; top: -80px;
  width: 280px; height: 280px;
  background: radial-gradient(circle, var(--reel-tint-soft) 0%, transparent 70%);
  pointer-events: none; opacity: 0.5;
}
.reel-badge {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 11px; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.1em;
  color: var(--reel-tint);
  padding: 4px 10px;
  background: var(--reel-tint-soft);
  border-radius: 999px;
}
.reel-rank {
  font-size: 12px; font-weight: 700;
  color: var(--muted); letter-spacing: 0.06em;
  text-transform: uppercase; margin-bottom: 4px;
}
.reel-topic {
  font-size: 28px; font-weight: 700; letter-spacing: -0.02em;
  color: var(--ink); margin: 4px 0 16px;
  line-height: 1.15;
}
.reel-tensions { display: flex; flex-direction: column; gap: 8px; }
.reel-tension {
  display: flex; gap: 12px; align-items: flex-start;
  padding: 10px 14px;
  background: #f8fafc;
  border-radius: 10px;
  border-left: 3px solid var(--tension-tint, var(--border));
}
.reel-tension-agent {
  font-size: 12px; font-weight: 700;
  color: var(--tension-tint, var(--ink-soft));
  white-space: nowrap;
  min-width: 110px;
}
.reel-tension-verdict {
  font-size: 13.5px; color: var(--ink-soft);
  line-height: 1.5;
}
.reel-meaning {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px dashed var(--border);
  font-size: 13.5px; color: var(--muted);
  font-style: italic;
  line-height: 1.5;
}

/* Compact supporting reel cards (#2, #3) */
.reel-sub {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 18px 22px;
  height: 100%;
  position: relative;
  overflow: hidden;
}
.reel-sub::before {
  content: ''; position: absolute; left: 0; top: 0; bottom: 0;
  width: 4px; background: var(--reel-tint);
}
.reel-sub .reel-topic { font-size: 18px; margin: 4px 0 10px; }
.reel-sub .reel-tensions { gap: 4px; }
.reel-sub .reel-tension { padding: 6px 10px; font-size: 12px; }
.reel-sub .reel-tension-verdict { font-size: 12.5px; }

/* -------------------------------------------------------------------------
   Round 2 rebuttal cards
   ------------------------------------------------------------------------- */
.rebuttal-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 16px;
  height: 100%;
  display: flex; flex-direction: column; gap: 6px;
  position: relative; overflow: hidden;
}
.rebuttal-card::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
  background: var(--stance-tint);
}
.rebuttal-agent { font-size: 14px; font-weight: 700; color: var(--ink); }
.rebuttal-stance {
  font-size: 10px; font-weight: 700;
  letter-spacing: 0.1em; text-transform: uppercase;
  color: var(--stance-tint);
}
.rebuttal-responds {
  font-size: 11px; color: var(--muted);
  margin-bottom: 4px;
}
.rebuttal-text {
  font-size: 13px; color: var(--ink-soft);
  font-style: italic; line-height: 1.5;
}

/* -------------------------------------------------------------------------
   Provenance, ASEAN diff, checklist
   ------------------------------------------------------------------------- */
.panel-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px 20px;
  margin: 8px 0;
}
.panel-card-title { font-weight: 700; font-size: 15px; margin-bottom: 4px; }
.panel-card-caption { font-size: 12px; color: var(--muted); }

/* Severity helpers */
.sev-badge {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 10px; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.1em;
  padding: 3px 8px; border-radius: 999px;
}

/* What-if metric polish */
[data-testid="stMetric"] {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 14px 18px;
}
[data-testid="stMetricLabel"] { color: var(--muted); }

/* -------------------------------------------------------------------------
   Mobile
   ------------------------------------------------------------------------- */
@media (max-width: 720px) {
  .panel-hero { padding: 24px; }
  .panel-hero-row { flex-direction: column; align-items: flex-start; }
  .panel-hero-title { font-size: 36px; }
  .panel-hero-mark { font-size: 48px; }
  .reel-topic { font-size: 22px; }
}
"""


def inject() -> None:
    """Render the global stylesheet. Call once at the top of every page."""
    st.markdown(f"<style>{_CSS}</style>", unsafe_allow_html=True)


def hero(title: str, subtitle: str, stats: list[tuple[str, str]] | None = None,
         icon: str = "⚖️") -> None:
    """Render the page hero. `stats` is a list of (label, value) tuples."""
    stats_html = ""
    if stats:
        chips = "".join(
            f"<span class='panel-hero-stat'><b>{value}</b> &nbsp;{label}</span>"
            for label, value in stats
        )
        stats_html = f"<div class='panel-hero-stats'>{chips}</div>"
    st.markdown(
        f"""
        <div class='panel-hero'>
          <div class='panel-hero-row'>
            <div class='panel-hero-mark'>{icon}</div>
            <div>
              <h1 class='panel-hero-title'>{title}</h1>
              <p class='panel-hero-sub'>{subtitle}</p>
            </div>
          </div>
          {stats_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_heading(eyebrow: str, title: str, lede: str = "") -> None:
    """Three-line section heading used between major page regions."""
    lede_html = f"<p class='panel-section-lede'>{lede}</p>" if lede else ""
    st.markdown(
        f"""
        <div style='margin-top: 24px;'>
          <div class='panel-section-eyebrow'>{eyebrow}</div>
          <div class='panel-section-title'>{title}</div>
          {lede_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def agent_card_waiting(emoji: str, name: str, tagline: str, status_msg: str,
                        agent_tint: str) -> str:
    return f"""
    <div class='agent-card agent-card-waiting' style='--agent-tint: {agent_tint};'>
      <div class='agent-card-icon'>{emoji}</div>
      <div class='agent-card-name'>{name}</div>
      <div class='agent-card-tagline'>{tagline}</div>
      <div class='agent-card-status'>
        <span class='dot'></span>{status_msg}
      </div>
    </div>
    """


def agent_card_done(emoji: str, name: str, latency_s: float | None,
                     verdict: str, findings: list[str], agent_tint: str) -> str:
    latency_html = (
        f"<span class='agent-card-latency'>{latency_s:.1f}s</span>"
        if latency_s and latency_s > 0 else ""
    )
    findings_html = "".join(f"<li>{f}</li>" for f in findings[:4])
    return f"""
    <div class='agent-card agent-card-done' style='--agent-tint: {agent_tint};'>
      <div class='agent-card-icon'>{emoji}</div>
      <div class='agent-card-name'>{name}{latency_html}</div>
      <div class='agent-card-verdict'>{verdict}</div>
      <ul class='agent-card-findings'>{findings_html}</ul>
    </div>
    """
