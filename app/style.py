"""Panel — design system + Streamlit CSS injection.

Late-2025 visual language: confident neutrals, restrained accent, generous
whitespace, soft elevation, motion only where it earns its weight.

Influences: Linear, Stripe, Vercel, Notion. Avoids: gradients-for-the-sake-of-it,
glassmorphism, busy neon.

Public API:
    inject()                      — global stylesheet
    top_bar(brand, crumb, status) — slim contextual header
    hero(title, subtitle, ...)    — page hero with stat chips + optional corridor
    section_heading(eyebrow, title, lede)
    agent_card_waiting(...)       — pulsing skeleton card
    agent_card_done(...)          — settled card with verdict + findings
    urgency_gauge(score)          — animated 0-10 gauge
    sev_pill(severity)            — pill badge with dot
    corridor_chip(origin, dest)   — origin → destination chip pair
"""
from __future__ import annotations

import streamlit as st

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
COLORS = {
    "ink":          "#0f172a",
    "ink_soft":     "#334155",
    "muted":        "#64748b",
    "border":       "#e2e8f0",
    "border_strong":"#cbd5e1",
    "surface":      "#ffffff",
    "surface_alt":  "#f8fafc",
    "page":         "#fafaf9",
    "warm_tint":    "#fef3c7",
    "accent":       "#dc2626",
    # Severity ramp
    "sev_10":       "#b91c1c",
    "sev_9":        "#dc2626",
    "sev_8":        "#ea580c",
    "sev_7":        "#f59e0b",
    "sev_6":        "#eab308",
    "sev_5":        "#737373",
    # Stance
    "stance_concede":   "#16a34a",
    "stance_push_back": "#dc2626",
    "stance_extend":    "#2563eb",
    # Agent tints
    "agent_lawyer":     "#1e40af",
    "agent_translator": "#0d9488",
    "agent_regulator":  "#7c3aed",
    "agent_peer":       "#0891b2",
    "agent_triage":     "#dc2626",
    "agent_negotiator": "#d97706",
    # Status
    "status_ok":        "#15803d",
    "status_ok_bg":     "#f0fdf4",
    "status_warn":      "#b45309",
    "status_warn_bg":   "#fefce8",
}

AGENT_TINTS = {
    "lawyer":        COLORS["agent_lawyer"],
    "translator":    COLORS["agent_translator"],
    "regulator":     COLORS["agent_regulator"],
    "peer_advocate": COLORS["agent_peer"],
    "triage":        COLORS["agent_triage"],
    "negotiator":    COLORS["agent_negotiator"],
}

SEVERITY_PALETTE = {
    10: (COLORS["sev_10"], "#fee2e2", "CRITICAL"),
    9:  (COLORS["sev_9"],  "#fee2e2", "EMERGENCY"),
    8:  (COLORS["sev_8"],  "#ffedd5", "HIGH"),
    7:  (COLORS["sev_7"],  "#fef3c7", "HIGH"),
    6:  (COLORS["sev_6"],  "#fef9c3", "MEDIUM"),
    5:  (COLORS["sev_5"],  "#f1f5f9", "DECLARED"),
}


_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  --ink: #0f172a;
  --ink-soft: #334155;
  --muted: #64748b;
  --border: #e2e8f0;
  --border-strong: #cbd5e1;
  --surface: #ffffff;
  --surface-alt: #f8fafc;
  --page: #fafaf9;
  --accent: #dc2626;
  --warm-tint: #fef3c7;

  --shadow-xs: 0 1px 2px rgba(15,23,42,0.04);
  --shadow-sm: 0 1px 3px rgba(15,23,42,0.06), 0 1px 2px rgba(15,23,42,0.04);
  --shadow-md: 0 4px 14px rgba(15,23,42,0.08), 0 1px 3px rgba(15,23,42,0.05);
  --shadow-lg: 0 24px 50px rgba(15,23,42,0.10), 0 4px 14px rgba(15,23,42,0.06);

  --radius-sm: 8px;
  --radius-md: 14px;
  --radius-lg: 20px;

  --easing: cubic-bezier(0.16, 1, 0.3, 1);
  --easing-snap: cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* ---------------------------------------------------------------------------
   GLOBAL
   --------------------------------------------------------------------------- */
html, body, [data-testid="stAppViewContainer"] {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  -webkit-font-smoothing: antialiased;
  font-feature-settings: 'cv11', 'ss01';
}
.main .block-container {
  padding-top: 1.25rem;
  padding-bottom: 6rem;
  max-width: 1200px;
}

h1, h2, h3, h4 {
  font-family: 'Inter', sans-serif;
  letter-spacing: -0.022em;
  color: var(--ink);
  font-feature-settings: 'cv11', 'ss01';
}
h1 { font-weight: 800; }
h2 { font-weight: 700; letter-spacing: -0.025em; }
h3 { font-weight: 700; letter-spacing: -0.02em; }
p, span, li, div { color: var(--ink); }

code, kbd, samp { font-family: 'JetBrains Mono', monospace; font-size: 0.86em; }

.tabular {
  font-variant-numeric: tabular-nums;
  font-feature-settings: 'tnum', 'ss01';
}

/* ---------------------------------------------------------------------------
   SIDEBAR
   --------------------------------------------------------------------------- */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #ffffff 0%, #fafaf9 100%);
  border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] h3 {
  font-size: 11px !important;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--muted);
  font-weight: 700;
  margin-top: 1.5rem;
}

/* Streamlit native primary button */
button[kind="primary"] {
  background: var(--ink) !important;
  border: none !important;
  color: white !important;
  font-weight: 600 !important;
  border-radius: var(--radius-sm) !important;
  padding: 10px 20px !important;
  box-shadow: var(--shadow-sm) !important;
  transition: all 200ms var(--easing) !important;
}
button[kind="primary"]:hover {
  background: #1e293b !important;
  transform: translateY(-1px);
  box-shadow: var(--shadow-md) !important;
}

/* ---------------------------------------------------------------------------
   TOP BAR
   --------------------------------------------------------------------------- */
.panel-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 18px;
  background: rgba(255,255,255,0.72);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  margin-bottom: 16px;
  font-size: 13px;
}
.panel-topbar-left {
  display: flex; align-items: center; gap: 14px;
}
.panel-topbar-brand {
  display: inline-flex; align-items: center; gap: 8px;
  font-weight: 700; letter-spacing: -0.01em; color: var(--ink);
  font-size: 14px;
}
.panel-topbar-brand .dot {
  width: 8px; height: 8px; background: var(--accent); border-radius: 999px;
}
.panel-topbar-crumb {
  color: var(--muted); font-size: 12px;
  padding-left: 14px;
  border-left: 1px solid var(--border);
}
.panel-topbar-status {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 12px;
  background: var(--status-bg, #f0fdf4);
  color: var(--status-fg, #15803d);
  border-radius: 999px;
  font-size: 11px; font-weight: 700;
  letter-spacing: 0.04em;
}
.panel-topbar-status .pulse {
  width: 6px; height: 6px;
  background: var(--status-fg, #22c55e);
  border-radius: 999px;
  animation: pulse 1.4s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%      { opacity: 0.35; transform: scale(0.7); }
}

/* ---------------------------------------------------------------------------
   HERO
   --------------------------------------------------------------------------- */
.panel-hero {
  position: relative;
  padding: 40px 44px;
  border-radius: var(--radius-lg);
  background:
    radial-gradient(ellipse 600px 300px at top right, rgba(220,38,38,0.05) 0%, transparent 70%),
    radial-gradient(ellipse 400px 400px at bottom left, rgba(253,224,71,0.10) 0%, transparent 70%),
    linear-gradient(180deg, #ffffff 0%, var(--warm-tint) 100%);
  border: 1px solid #fde68a;
  margin-bottom: 24px;
  overflow: hidden;
  box-shadow: var(--shadow-md);
}
.panel-hero::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 4px;
  background: linear-gradient(90deg, var(--accent) 0%, #f59e0b 100%);
}
.panel-hero-row { display: flex; align-items: center; gap: 28px; }
.panel-hero-mark {
  font-size: 56px; line-height: 1;
  filter: drop-shadow(0 6px 16px rgba(15,23,42,0.10));
  flex-shrink: 0;
}
.panel-hero-title {
  font-size: 56px; font-weight: 800; line-height: 1.0; margin: 0;
  letter-spacing: -0.045em; color: var(--ink);
}
.panel-hero-sub {
  font-size: 19px; color: var(--ink-soft); margin: 10px 0 0;
  line-height: 1.5; max-width: 640px; font-weight: 450;
}
.panel-hero-stats {
  display: flex; flex-wrap: wrap; gap: 8px;
  margin-top: 22px;
}
.panel-hero-stat {
  background: var(--surface);
  padding: 8px 14px;
  border-radius: 999px;
  font-size: 12px; font-weight: 600;
  color: var(--ink-soft);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-xs);
  display: inline-flex; align-items: baseline; gap: 6px;
  font-variant-numeric: tabular-nums;
}
.panel-hero-stat b {
  color: var(--accent);
  font-weight: 800;
  font-size: 13px;
}

/* ---------------------------------------------------------------------------
   SECTION HEADERS
   --------------------------------------------------------------------------- */
.panel-section { margin-top: 36px; }
.panel-section-eyebrow {
  display: inline-flex; align-items: center; gap: 8px;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: var(--muted);
  font-weight: 700;
  margin-bottom: 6px;
}
.panel-section-eyebrow .dot {
  width: 6px; height: 6px;
  background: var(--accent);
  border-radius: 999px;
}
.panel-section-title {
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.025em;
  margin: 0 0 8px;
  color: var(--ink);
}
.panel-section-lede {
  color: var(--muted);
  font-size: 15px;
  max-width: 700px;
  line-height: 1.55;
  margin-bottom: 22px;
}

/* ---------------------------------------------------------------------------
   CORRIDOR CHIP
   --------------------------------------------------------------------------- */
.corridor-row {
  display: inline-flex; align-items: center; gap: 10px;
  font-size: 14px; font-weight: 600;
}
.corridor-chip {
  background: rgba(255,255,255,0.92);
  border: 1px solid var(--border);
  padding: 7px 16px;
  border-radius: 999px;
  display: inline-flex; align-items: center; gap: 8px;
  box-shadow: var(--shadow-xs);
  color: var(--ink);
}
.corridor-arrow {
  color: var(--accent);
  font-weight: 800;
  font-size: 18px;
}

/* ---------------------------------------------------------------------------
   AGENT CARDS — waiting / done states
   --------------------------------------------------------------------------- */
.agent-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 18px;
  height: 100%;
  min-height: 200px;
  display: flex; flex-direction: column;
  gap: 8px;
  transition: all 320ms var(--easing);
  position: relative;
  overflow: hidden;
  box-shadow: var(--shadow-xs);
}
.agent-card::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
  background: var(--agent-tint, var(--border));
}
.agent-card-waiting {
  background: linear-gradient(180deg, #ffffff, #fafaf9);
}
.agent-card-done {
  background: var(--surface);
  box-shadow: var(--shadow-sm);
  animation: cardLand 420ms var(--easing-snap);
}
.agent-card-done:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}
@keyframes cardLand {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}
.agent-card-header { display: flex; align-items: center; gap: 10px; }
.agent-card-avatar {
  width: 36px; height: 36px;
  border-radius: 10px;
  background: var(--agent-tint-soft, #f1f5f9);
  display: flex; align-items: center; justify-content: center;
  font-size: 20px; line-height: 1;
  flex-shrink: 0;
}
.agent-card-meta { flex: 1; }
.agent-card-name {
  font-size: 14.5px; font-weight: 700;
  color: var(--ink); line-height: 1.2;
}
.agent-card-tagline {
  font-size: 11px; color: var(--muted);
  text-transform: uppercase; letter-spacing: 0.06em;
  font-weight: 600;
}
.agent-card-latency {
  font-size: 10.5px; font-weight: 600;
  color: var(--muted);
  background: #f1f5f9;
  padding: 3px 8px; border-radius: 999px;
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.02em;
}
.agent-card-status {
  display: flex; align-items: center; gap: 8px;
  font-size: 12.5px; color: var(--ink-soft);
  font-weight: 500;
}
.agent-card-status .dot {
  width: 7px; height: 7px; border-radius: 999px;
  background: var(--agent-tint, var(--accent));
  animation: pulse 1.4s ease-in-out infinite;
  flex-shrink: 0;
}
.agent-card-verdict {
  font-size: 13.5px; font-weight: 600; line-height: 1.45;
  color: var(--ink); margin-top: 2px;
}
.agent-card-findings {
  margin: 4px 0 0; padding: 0; list-style: none;
}
.agent-card-findings li {
  font-size: 12px; color: var(--ink-soft);
  padding: 4px 0 4px 14px;
  position: relative; line-height: 1.45;
}
.agent-card-findings li::before {
  content: '•'; position: absolute; left: 0;
  color: var(--agent-tint); font-weight: 700;
}

/* Skeleton shimmer (waiting state body) */
.skeleton-stack { margin-top: 4px; }
.skeleton-line {
  background: linear-gradient(90deg, #f1f5f9 0%, #e2e8f0 50%, #f1f5f9 100%);
  background-size: 200% 100%;
  animation: shimmer 1.6s linear infinite;
  border-radius: 4px;
  height: 10px;
  margin: 8px 0;
}
.skeleton-line.s { width: 50%; }
.skeleton-line.m { width: 80%; }
.skeleton-line.l { width: 100%; }
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* ---------------------------------------------------------------------------
   URGENCY GAUGE
   --------------------------------------------------------------------------- */
.urgency-gauge {
  display: flex; align-items: center; gap: 22px;
  padding: 20px 24px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  margin: 16px 0 12px;
}
.urgency-gauge-number-wrap {
  display: flex; align-items: baseline; gap: 4px;
  min-width: 110px;
}
.urgency-gauge-number {
  font-size: 56px; font-weight: 800;
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.05em;
  color: var(--gauge-color);
  line-height: 0.9;
}
.urgency-gauge-suffix {
  font-size: 18px; color: var(--muted);
  font-weight: 600;
}
.urgency-gauge-bar-wrap { flex: 1; }
.urgency-gauge-label {
  font-size: 11px; text-transform: uppercase;
  letter-spacing: 0.12em; color: var(--muted);
  font-weight: 700; margin-bottom: 8px;
}
.urgency-gauge-bar {
  width: 100%; height: 12px;
  background: #f1f5f9;
  border-radius: 999px; overflow: hidden;
  position: relative;
}
.urgency-gauge-fill {
  height: 100%;
  width: var(--gauge-pct);
  background: linear-gradient(90deg, #84cc16 0%, #fbbf24 40%, #f97316 70%, #dc2626 100%);
  border-radius: 999px;
  transition: width 900ms var(--easing);
  animation: gaugeFill 900ms var(--easing);
}
@keyframes gaugeFill {
  from { width: 0; }
  to   { width: var(--gauge-pct); }
}
.urgency-gauge-verdict {
  font-size: 14px; font-weight: 600;
  color: var(--gauge-color);
  margin-top: 6px;
}

/* ---------------------------------------------------------------------------
   DISAGREEMENT REEL
   --------------------------------------------------------------------------- */
.reel-hero {
  position: relative;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 32px 36px;
  margin: 18px 0 22px;
  box-shadow: var(--shadow-md);
  overflow: hidden;
  animation: cardLand 500ms var(--easing-snap);
}
.reel-hero::before {
  content: '';
  position: absolute; left: 0; top: 0; bottom: 0;
  width: 6px; background: var(--reel-tint);
}
.reel-hero::after {
  content: '';
  position: absolute; right: -120px; top: -120px;
  width: 360px; height: 360px;
  background: radial-gradient(circle, var(--reel-tint-soft) 0%, transparent 70%);
  pointer-events: none; opacity: 0.6;
}
.reel-hero-header {
  display: flex; align-items: flex-start; justify-content: space-between; gap: 16px;
  margin-bottom: 12px;
}
.reel-rank {
  font-size: 11px; font-weight: 700;
  color: var(--muted); letter-spacing: 0.12em;
  text-transform: uppercase; margin-bottom: 6px;
}
.reel-topic {
  font-size: 32px; font-weight: 800; letter-spacing: -0.03em;
  color: var(--ink); margin: 4px 0 18px;
  line-height: 1.1;
}
.reel-tensions { display: flex; flex-direction: column; gap: 8px; }
.reel-tension {
  display: flex; gap: 14px; align-items: flex-start;
  padding: 12px 16px;
  background: #f8fafc;
  border-radius: var(--radius-sm);
  border-left: 3px solid var(--tension-tint, var(--border));
}
.reel-tension-agent {
  font-size: 12px; font-weight: 700;
  color: var(--tension-tint, var(--ink-soft));
  white-space: nowrap;
  min-width: 120px;
  letter-spacing: -0.005em;
}
.reel-tension-verdict {
  font-size: 13.5px; color: var(--ink-soft);
  line-height: 1.5;
}
.reel-meaning {
  margin-top: 18px;
  padding: 14px 16px;
  background: #fafaf9;
  border-radius: var(--radius-sm);
  font-size: 13.5px; color: var(--ink-soft);
  font-style: italic;
  line-height: 1.5;
  border-left: 3px solid var(--border-strong);
}

/* Compact supporting reel cards */
.reel-sub {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 20px 24px;
  height: 100%;
  position: relative;
  overflow: hidden;
  box-shadow: var(--shadow-xs);
  transition: all 320ms var(--easing);
  animation: cardLand 500ms var(--easing-snap);
}
.reel-sub:hover { transform: translateY(-2px); box-shadow: var(--shadow-sm); }
.reel-sub::before {
  content: ''; position: absolute; left: 0; top: 0; bottom: 0;
  width: 4px; background: var(--reel-tint);
}
.reel-sub .reel-topic { font-size: 19px; margin: 6px 0 12px; line-height: 1.2; }
.reel-sub .reel-tensions { gap: 6px; }
.reel-sub .reel-tension { padding: 8px 12px; }
.reel-sub .reel-tension-verdict { font-size: 12.5px; }
.reel-sub .reel-tension-agent { min-width: 100px; font-size: 11px; }
.reel-sub .reel-meaning { font-size: 12.5px; padding: 10px 12px; margin-top: 12px; }

/* ---------------------------------------------------------------------------
   SEVERITY PILL
   --------------------------------------------------------------------------- */
.sev-pill {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 10.5px; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.1em;
  background: var(--pill-bg);
  color: var(--pill-fg);
}
.sev-pill .dot {
  width: 6px; height: 6px; border-radius: 999px;
  background: currentColor;
}
.sev-badge {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 10.5px; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.1em;
  padding: 4px 10px; border-radius: 999px;
}

/* ---------------------------------------------------------------------------
   REBUTTAL CARDS
   --------------------------------------------------------------------------- */
.rebuttal-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 16px 18px;
  height: 100%;
  display: flex; flex-direction: column; gap: 8px;
  position: relative; overflow: hidden;
  box-shadow: var(--shadow-xs);
  transition: all 280ms var(--easing);
  animation: cardLand 480ms var(--easing-snap);
}
.rebuttal-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-sm); }
.rebuttal-card::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
  background: var(--stance-tint);
}
.rebuttal-card-head {
  display: flex; align-items: center; justify-content: space-between; gap: 8px;
}
.rebuttal-agent { font-size: 13.5px; font-weight: 700; color: var(--ink); }
.rebuttal-stance {
  font-size: 9.5px; font-weight: 700;
  letter-spacing: 0.1em; text-transform: uppercase;
  color: var(--stance-tint);
  background: var(--stance-tint-soft, transparent);
  padding: 3px 8px; border-radius: 999px;
}
.rebuttal-responds {
  font-size: 11px; color: var(--muted);
  display: inline-flex; align-items: center; gap: 4px;
}
.rebuttal-text {
  font-size: 12.5px; color: var(--ink-soft);
  line-height: 1.55;
  position: relative;
  padding-top: 4px;
}
.rebuttal-text::before {
  content: '"';
  position: absolute; top: -8px; left: -4px;
  font-size: 32px; color: var(--stance-tint);
  font-family: 'Inter', serif;
  font-weight: 700; opacity: 0.25;
  line-height: 1;
}

/* ---------------------------------------------------------------------------
   PANEL CARDS (generic surfaces)
   --------------------------------------------------------------------------- */
.panel-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 18px 22px;
  margin: 8px 0;
  box-shadow: var(--shadow-xs);
}
.panel-card-title { font-weight: 700; font-size: 15px; margin-bottom: 4px; }
.panel-card-caption { font-size: 12px; color: var(--muted); }

[data-testid="stMetric"] {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 14px 18px;
  box-shadow: var(--shadow-xs);
}
[data-testid="stMetricLabel"] {
  color: var(--muted) !important;
  font-size: 11px !important;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 700 !important;
}
[data-testid="stMetricValue"] {
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.02em;
  font-weight: 800 !important;
}

/* ---------------------------------------------------------------------------
   FORMS — text inputs, selects
   --------------------------------------------------------------------------- */
[data-baseweb="select"] > div, .stTextInput input, .stTextArea textarea {
  border-radius: var(--radius-sm) !important;
}

/* ---------------------------------------------------------------------------
   MOBILE
   --------------------------------------------------------------------------- */
@media (max-width: 768px) {
  .main .block-container { padding-left: 1rem; padding-right: 1rem; }
  .panel-hero { padding: 28px; }
  .panel-hero-row { flex-direction: column; align-items: flex-start; gap: 16px; }
  .panel-hero-title { font-size: 38px; }
  .panel-hero-mark { font-size: 44px; }
  .reel-hero { padding: 22px; }
  .reel-topic { font-size: 24px; }
  .urgency-gauge { flex-direction: column; align-items: stretch; gap: 14px; }
  .urgency-gauge-number-wrap { justify-content: center; }
}
"""


def inject() -> None:
    """Render the global stylesheet. Call once at the top of every page."""
    st.markdown(f"<style>{_CSS}</style>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Component helpers
# ---------------------------------------------------------------------------
def top_bar(brand: str, crumb: str = "", status_label: str = "",
            status_tone: str = "ok") -> None:
    """Slim contextual header at the top of the page."""
    if status_tone == "ok":
        bg, fg = COLORS["status_ok_bg"], COLORS["status_ok"]
    elif status_tone == "warn":
        bg, fg = COLORS["status_warn_bg"], COLORS["status_warn"]
    else:
        bg, fg = "#f1f5f9", COLORS["muted"]
    crumb_html = f"<span class='panel-topbar-crumb'>{crumb}</span>" if crumb else ""
    status_html = (
        f"<span class='panel-topbar-status' style='--status-bg: {bg}; --status-fg: {fg};'>"
        f"<span class='pulse'></span>{status_label}</span>"
        if status_label else ""
    )
    st.markdown(
        f"""
        <div class='panel-topbar'>
          <div class='panel-topbar-left'>
            <span class='panel-topbar-brand'><span class='dot'></span>Panel</span>
            {crumb_html}
          </div>
          {status_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str, stats: list[tuple[str, str]] | None = None,
         icon: str = "⚖️", corridor: tuple[str, str] | None = None) -> None:
    """Hero header. `stats` is [(label, value), ...]. `corridor` is (origin, destination)."""
    stats_html = ""
    if stats:
        chips = "".join(
            f"<span class='panel-hero-stat'><b class='tabular'>{value}</b> {label}</span>"
            for label, value in stats
        )
        stats_html = f"<div class='panel-hero-stats'>{chips}</div>"
    corridor_html = ""
    if corridor:
        origin, destination = corridor
        corridor_html = (
            f"<div class='corridor-row' style='margin-top:16px;'>"
            f"<span class='corridor-chip'>{origin}</span>"
            f"<span class='corridor-arrow'>→</span>"
            f"<span class='corridor-chip'>{destination}</span>"
            f"</div>"
        )
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
          {corridor_html}
          {stats_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_heading(eyebrow: str, title: str, lede: str = "") -> None:
    lede_html = f"<p class='panel-section-lede'>{lede}</p>" if lede else ""
    st.markdown(
        f"""
        <div class='panel-section'>
          <div class='panel-section-eyebrow'><span class='dot'></span>{eyebrow}</div>
          <div class='panel-section-title'>{title}</div>
          {lede_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def agent_card_waiting(emoji: str, name: str, tagline: str, status_msg: str,
                        agent_tint: str) -> str:
    tint_soft = _hex_to_rgba(agent_tint, 0.10)
    return f"""
    <div class='agent-card agent-card-waiting'
         style='--agent-tint: {agent_tint}; --agent-tint-soft: {tint_soft};'>
      <div class='agent-card-header'>
        <div class='agent-card-avatar'>{emoji}</div>
        <div class='agent-card-meta'>
          <div class='agent-card-name'>{name}</div>
          <div class='agent-card-tagline'>{tagline}</div>
        </div>
      </div>
      <div class='agent-card-status'>
        <span class='dot'></span>{status_msg}
      </div>
      <div class='skeleton-stack'>
        <div class='skeleton-line l'></div>
        <div class='skeleton-line m'></div>
        <div class='skeleton-line s'></div>
      </div>
    </div>
    """


def agent_card_done(emoji: str, name: str, latency_s: float | None,
                     verdict: str, findings: list[str], agent_tint: str) -> str:
    tint_soft = _hex_to_rgba(agent_tint, 0.10)
    latency_html = (
        f"<span class='agent-card-latency tabular'>{latency_s:.1f}s</span>"
        if latency_s and latency_s > 0 else ""
    )
    findings_html = "".join(f"<li>{f}</li>" for f in findings[:4])
    return f"""
    <div class='agent-card agent-card-done'
         style='--agent-tint: {agent_tint}; --agent-tint-soft: {tint_soft};'>
      <div class='agent-card-header'>
        <div class='agent-card-avatar'>{emoji}</div>
        <div class='agent-card-meta'>
          <div class='agent-card-name'>{name}</div>
          <div class='agent-card-tagline'>{latency_html}</div>
        </div>
      </div>
      <div class='agent-card-verdict'>{verdict}</div>
      <ul class='agent-card-findings'>{findings_html}</ul>
    </div>
    """


def urgency_gauge(score: int, *, label: str = "Urgency",
                   max_value: int = 10) -> None:
    """Animated 0–10 gauge with color-shifting fill."""
    pct = max(0, min(100, int(score / max_value * 100)))
    if score >= 8:
        color = COLORS["sev_9"]
        verdict = "Critical — act before signing"
    elif score >= 5:
        color = COLORS["sev_8"]
        verdict = "Elevated — significant concerns"
    elif score >= 3:
        color = COLORS["sev_7"]
        verdict = "Moderate — proceed with eyes open"
    else:
        color = COLORS["status_ok"]
        verdict = "Low — contract is largely compliant"
    st.markdown(
        f"""
        <div class='urgency-gauge'
             style='--gauge-color: {color}; --gauge-pct: {pct}%;'>
          <div class='urgency-gauge-number-wrap'>
            <span class='urgency-gauge-number'>{score}</span>
            <span class='urgency-gauge-suffix'>/{max_value}</span>
          </div>
          <div class='urgency-gauge-bar-wrap'>
            <div class='urgency-gauge-label'>{label}</div>
            <div class='urgency-gauge-bar'><div class='urgency-gauge-fill'></div></div>
            <div class='urgency-gauge-verdict'>{verdict}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sev_pill(severity: int) -> str:
    """Return HTML for a severity pill badge."""
    if severity not in SEVERITY_PALETTE:
        severity = max(5, min(10, severity))
    fg, bg, label = SEVERITY_PALETTE.get(severity, SEVERITY_PALETTE[5])
    return (
        f"<span class='sev-pill' style='--pill-bg: {bg}; --pill-fg: {fg};'>"
        f"<span class='dot'></span>{label} · sev {severity}</span>"
    )


def corridor_chip(origin_label: str, destination_label: str) -> str:
    return (
        f"<div class='corridor-row'>"
        f"<span class='corridor-chip'>{origin_label}</span>"
        f"<span class='corridor-arrow'>→</span>"
        f"<span class='corridor-chip'>{destination_label}</span>"
        f"</div>"
    )


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    """#1e40af → rgba(30,64,175,0.10) for tinted backgrounds."""
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return f"rgba(15,23,42,{alpha})"
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha:.2f})"
