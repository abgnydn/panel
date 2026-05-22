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
import { Store } from "../state";
import { AGENT_BY_ID, agentIconHtml } from "../ui/agents";
import type { AgentId } from "../ui/agents";
import { icon } from "../ui/icons";
import type { SceneCtx } from "./router";

const STANCE: Record<Rebuttal["stance"], { color: string; label: string; iconKey: "concede" | "push_back" | "extend" }> = {
  concede:   { color: "var(--stance-concede)",   label: "Concedes",    iconKey: "concede" },
  push_back: { color: "var(--stance-push_back)", label: "Pushes back", iconKey: "push_back" },
  extend:    { color: "var(--stance-extend)",    label: "Extends",     iconKey: "extend" },
};

export function renderRebuttals(ctx: SceneCtx): void {
  const { root, goto } = ctx;

  const result = Store.get().result ?? MOCK_RESULT;
  const cards = ["lawyer", "translator", "regulator", "peer_advocate", "triage", "negotiator"]
    .map((id) => result.rebuttals[id])
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
        <button class="cta-ghost" id="back">${icon("arrow_left", "icon-sm")}<span>Back to deliberation</span></button>
        <button class="cta" id="continue">
          <span>See where the panel disagrees</span>
          ${icon("arrow_right", "icon-sm")}
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
  const agent = AGENT_BY_ID[r.agent as AgentId];
  const stance = STANCE[r.stance];
  const respondsLabel = r.responds_to.toUpperCase().replace("_", " ");
  const agentTint = agent?.tint ?? "var(--ink-soft)";
  const agentName = agent?.name ?? r.agent;
  return `
    <article class="rebuttal-card" style="--stance:${stance.color};--agent-tint:${agentTint};">
      <header class="rebuttal-card-head">
        <div class="rebuttal-agent">
          <span class="rebuttal-agent-icon" style="color:${agentTint};">${agent ? agentIconHtml(agent.id, "icon-sm") : ""}</span>
          ${agentName}
        </div>
        <span class="rebuttal-stance">${icon(stance.iconKey, "icon-sm")} ${stance.label}</span>
      </header>
      <div class="rebuttal-responds">→ ${respondsLabel}</div>
      <p class="rebuttal-text">${r.rebuttal}</p>
    </article>
  `;
}
