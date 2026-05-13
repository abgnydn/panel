/**
 * Disagreement reel — the moat.
 *
 * Hero card for the strongest disagreement, two supporting cards below.
 * Severity-tinted left bar, agent-tinted tension rows, italic "why it
 * matters" callout.
 */
import { gsap } from "gsap";

import { MOCK_RESULT } from "../api/mock-result";
import type { ReelItem } from "../api/mock-result";
import type { SceneCtx } from "./router";

const SEVERITY_LABEL: Record<number, string> = {
  10: "CRITICAL",
  9: "EMERGENCY",
  8: "HIGH · legal but dangerous",
  7: "HIGH · gray area",
  6: "MEDIUM · international gap",
  5: "PRE-DECLARED",
};

const SEVERITY_TINT: Record<number, [string, string]> = {
  10: ["#b91c1c", "#fee2e2"],
  9:  ["#dc2626", "#fee2e2"],
  8:  ["#ea580c", "#ffedd5"],
  7:  ["#f59e0b", "#fef3c7"],
  6:  ["#eab308", "#fef9c3"],
  5:  ["#737373", "#f1f5f9"],
};

const AGENT_DISPLAY: Record<string, { emoji: string; name: string; tint: string }> = {
  lawyer:        { emoji: "⚖️",   name: "Lawyer",        tint: "var(--agent-lawyer)" },
  translator:    { emoji: "🌐",   name: "Translator",    tint: "var(--agent-translator)" },
  regulator:     { emoji: "🏛️",  name: "Regulator",     tint: "var(--agent-regulator)" },
  peer_advocate: { emoji: "🫱🏽‍🫲🏾", name: "Peer Advocate", tint: "var(--agent-peer)" },
  triage:        { emoji: "🚨",   name: "Triage",        tint: "var(--agent-triage)" },
  negotiator:    { emoji: "💬",   name: "Negotiator",    tint: "var(--agent-negotiator)" },
};

export function renderReel(ctx: SceneCtx): void {
  const { root, goto } = ctx;
  const reel = MOCK_RESULT.disagreement_reel;
  const hero = reel[0];
  const sub = reel.slice(1, 3);

  root.innerHTML = `
    <section class="reel">
      <header class="reel-head">
        <div class="eyebrow"><span class="dot"></span>The moat · Where the panel disagrees</div>
        <h1 class="display-heading">Three tensions <em>worth knowing</em></h1>
        <p class="lede">The panel rarely agrees on everything. The contract you signed
          is often <em>legal AND dangerous</em>, or <em>locally lawful but globally below
          the floor</em>. Here's where the six agents diverge — ranked by what matters.</p>
      </header>

      ${heroCardHtml(hero)}

      <div class="reel-sub-grid">${sub.map(subCardHtml).join("")}</div>

      <footer class="delib-foot">
        <button class="cta-ghost" id="back">← Back</button>
        <button class="cta" id="continue">
          <span>See your recommendation</span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="2"
                  stroke-linecap="round" stroke-linejoin="round"/></svg>
        </button>
      </footer>
    </section>
  `;

  root.querySelector<HTMLButtonElement>("#back")!.addEventListener("click", () => goto("deliberation"));
  root.querySelector<HTMLButtonElement>("#continue")!.addEventListener("click", () => goto("recommendation" as never));

  gsap.fromTo(".reel-head",
    { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.7, ease: "power3.out", clearProps: "transform" });
  gsap.fromTo(".reel-hero",
    { opacity: 0, y: 24, scale: 0.985 },
    { opacity: 1, y: 0, scale: 1, duration: 0.75, delay: 0.2, ease: "power3.out", clearProps: "transform" });
  gsap.fromTo(".reel-sub-card",
    { opacity: 0, y: 18 },
    { opacity: 1, y: 0, duration: 0.6, stagger: 0.08, delay: 0.45, ease: "power3.out", clearProps: "transform" });
  gsap.fromTo(".reel-tension",
    { opacity: 0, x: -12 },
    { opacity: 1, x: 0, duration: 0.45, stagger: 0.06, delay: 0.5, ease: "power3.out", clearProps: "transform" });
  gsap.fromTo(".delib-foot",
    { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.5, delay: 0.9, ease: "power3.out", clearProps: "transform" });
}

function heroCardHtml(item: ReelItem): string {
  const [fg, bg] = SEVERITY_TINT[item.severity] || SEVERITY_TINT[5];
  const label = SEVERITY_LABEL[item.severity] || "DECLARED";
  return `
    <div class="reel-hero" style="--reel-fg:${fg};--reel-bg:${bg};">
      <div class="reel-hero-grid">
        <div class="reel-rank-big">#${item.rank}</div>
        <div class="reel-hero-main">
          <span class="reel-sev-pill"><span class="dot"></span>${label} · sev ${item.severity}</span>
          <h2 class="reel-topic">${item.topic}</h2>
          <div class="reel-tensions">${item.tensions.map(tensionHtml).join("")}</div>
          <div class="reel-meaning">${item.why_it_matters}</div>
        </div>
      </div>
    </div>
  `;
}

function subCardHtml(item: ReelItem): string {
  const [fg, bg] = SEVERITY_TINT[item.severity] || SEVERITY_TINT[5];
  const label = SEVERITY_LABEL[item.severity] || "DECLARED";
  return `
    <div class="reel-sub-card" style="--reel-fg:${fg};--reel-bg:${bg};">
      <span class="reel-sev-pill"><span class="dot"></span>${label} · sev ${item.severity}</span>
      <div class="reel-rank-small">#${item.rank}</div>
      <h3 class="reel-topic-sm">${item.topic}</h3>
      <div class="reel-tensions">${item.tensions.slice(0, 3).map(tensionHtml).join("")}</div>
      <div class="reel-meaning-sm">${item.why_it_matters}</div>
    </div>
  `;
}

function tensionHtml(t: { agent: string; verdict: string }): string {
  const d = AGENT_DISPLAY[t.agent];
  if (!d) {
    return `<div class="reel-tension" style="--t-tint:#64748b;">
      <div class="reel-tension-agent">${t.agent}</div>
      <div class="reel-tension-verdict">${t.verdict}</div>
    </div>`;
  }
  return `
    <div class="reel-tension" style="--t-tint:${d.tint};">
      <div class="reel-tension-agent">${d.emoji} ${d.name}</div>
      <div class="reel-tension-verdict">${t.verdict}</div>
    </div>
  `;
}
