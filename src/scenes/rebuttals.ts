/**
 * Round 2 — the panel reacts to itself.
 *
 * Six rebuttal cards arranged in a 3×2 grid (responsive). Each card shows
 * stance (concede / push_back / extend) as a colour-tinted top border + pill,
 * the agent being addressed, and a 2-3 sentence quote rendered with a
 * faint serif quotation-mark watermark.
 */
import { gsap } from "gsap";

import { MOCK_RESULT } from "../api/mock-result";
import type { Rebuttal } from "../api/mock-result";
import type { SceneCtx } from "./router";

const AGENT_DISPLAY: Record<string, { emoji: string; name: string; tint: string }> = {
  lawyer:        { emoji: "⚖️",   name: "Lawyer",        tint: "var(--agent-lawyer)" },
  translator:    { emoji: "🌐",   name: "Translator",    tint: "var(--agent-translator)" },
  regulator:     { emoji: "🏛️",  name: "Regulator",     tint: "var(--agent-regulator)" },
  peer_advocate: { emoji: "🫱🏽‍🫲🏾", name: "Peer Advocate", tint: "var(--agent-peer)" },
  triage:        { emoji: "🚨",   name: "Triage",        tint: "var(--agent-triage)" },
  negotiator:    { emoji: "💬",   name: "Negotiator",    tint: "var(--agent-negotiator)" },
};

const STANCE: Record<Rebuttal["stance"], { color: string; label: string; icon: string }> = {
  concede:   { color: "var(--stance-concede)",   label: "Concedes",    icon: "🤝" },
  push_back: { color: "var(--stance-push_back)", label: "Pushes back", icon: "⚔️" },
  extend:    { color: "var(--stance-extend)",    label: "Extends",     icon: "➕" },
};

export function renderRebuttals(ctx: SceneCtx): void {
  const { root, goto } = ctx;

  const cards = ["lawyer", "translator", "regulator", "peer_advocate", "triage", "negotiator"]
    .map((id) => MOCK_RESULT.rebuttals[id])
    .filter((r): r is Rebuttal => !!r)
    .map(rebuttalCardHtml)
    .join("");

  root.innerHTML = `
    <section class="rebuttals">
      <header class="rebuttals-head">
        <div class="eyebrow"><span class="dot"></span>Round 2 · The panel deliberates again</div>
        <h1 class="display-heading">Now they <em>react to each other</em></h1>
        <p class="lede">After Round 1, every agent saw the other five's findings.
          Here is the moment Panel stops being six monologues and becomes a
          conversation — concessions, pushbacks, and one extension at a time.</p>
      </header>

      <div class="rebuttal-grid">${cards}</div>

      <footer class="delib-foot">
        <button class="cta-ghost" id="back">← Back to deliberation</button>
        <button class="cta" id="continue">
          <span>See where the panel disagrees</span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="2"
                  stroke-linecap="round" stroke-linejoin="round"/></svg>
        </button>
      </footer>
    </section>
  `;

  root.querySelector<HTMLButtonElement>("#back")!.addEventListener("click", () => goto("deliberation"));
  root.querySelector<HTMLButtonElement>("#continue")!.addEventListener("click", () => goto("reel"));

  gsap.fromTo(".rebuttals-head",
    { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.7, ease: "power3.out", clearProps: "transform" });
  gsap.fromTo(".rebuttal-card",
    { opacity: 0, y: 18, scale: 0.985 },
    { opacity: 1, y: 0, scale: 1, duration: 0.55, stagger: 0.07, delay: 0.2, ease: "power3.out", clearProps: "transform" });
  gsap.fromTo(".delib-foot",
    { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.5, delay: 0.7, ease: "power3.out", clearProps: "transform" });
}

function rebuttalCardHtml(r: Rebuttal): string {
  const agent = AGENT_DISPLAY[r.agent] ?? { emoji: "", name: r.agent, tint: "var(--ink-soft)" };
  const stance = STANCE[r.stance];
  const respondsLabel = r.responds_to.toUpperCase().replace("_", " ");
  return `
    <article class="rebuttal-card" style="--stance:${stance.color};--agent-tint:${agent.tint};">
      <header class="rebuttal-card-head">
        <div class="rebuttal-agent">${agent.emoji} ${agent.name}</div>
        <span class="rebuttal-stance"><span class="dot"></span>${stance.icon} ${stance.label}</span>
      </header>
      <div class="rebuttal-responds">→ ${respondsLabel}</div>
      <p class="rebuttal-text">${r.rebuttal}</p>
    </article>
  `;
}
