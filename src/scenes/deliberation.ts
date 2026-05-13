/**
 * Deliberation scene — PLACEHOLDER.
 *
 * The full version mounts six 3D agent panes around the contract in R3F-style
 * scene graph and streams agent verdicts as they come back from the FastAPI
 * backend. For now we render a static representation so the cold-open → intake
 * → deliberation flow has a destination during development.
 */
import { gsap } from "gsap";

import { Store } from "../state";
import { LANGUAGES } from "../data/samples";
import type { SceneCtx } from "./router";

const AGENTS = [
  { id: "lawyer",        emoji: "⚖️",   name: "Lawyer",         tagline: "Local labor law",              tint: "var(--agent-lawyer)" },
  { id: "translator",    emoji: "🌐",   name: "Translator",     tagline: "Plain language in your L1",    tint: "var(--agent-translator)" },
  { id: "regulator",     emoji: "🏛️",  name: "Regulator",      tagline: "ILO / ASEAN standards",        tint: "var(--agent-regulator)" },
  { id: "peer_advocate", emoji: "🫱🏽‍🫲🏾", name: "Peer Advocate",  tagline: "Similar past cases",          tint: "var(--agent-peer)" },
  { id: "triage",        emoji: "🚨",   name: "Triage",         tagline: "Urgency & contacts",           tint: "var(--agent-triage)" },
  { id: "negotiator",    emoji: "💬",   name: "Negotiator",     tagline: "What to say before signing",   tint: "var(--agent-negotiator)" },
];

export function renderDeliberation(ctx: SceneCtx): void {
  const { root, goto } = ctx;
  const intake = Store.get().intake;
  const sample = intake.sample;
  const file = intake.file;
  const langName = LANGUAGES[intake.language] || intake.language;

  const corridor = sample
    ? `${sample.origin_label} → ${sample.destination_label}`
    : file
      ? `Uploaded · ${file.name}`
      : "—";

  const agentsHtml = AGENTS.map(
    (a) => `
      <div class="agent-pane" style="--agent-tint:${a.tint};">
        <div class="agent-pane-head">
          <div class="agent-pane-avatar">${a.emoji}</div>
          <div>
            <div class="agent-pane-name">${a.name}</div>
            <div class="agent-pane-tagline">${a.tagline}</div>
          </div>
        </div>
        <div class="agent-pane-status">
          <span class="dot"></span>
          <span class="status-text">Boarding the panel…</span>
        </div>
        <div class="skeleton-stack">
          <div class="skeleton-line" style="width:90%;"></div>
          <div class="skeleton-line" style="width:75%;"></div>
          <div class="skeleton-line" style="width:60%;"></div>
        </div>
      </div>
    `,
  ).join("");

  root.innerHTML = `
    <section class="deliberation">
      <header class="delib-head">
        <div class="eyebrow"><span class="dot"></span>Round 1 · Panel deliberation</header>
        <h1 class="display-heading">The panel <em>convenes</em></h1>
        <div class="delib-meta">
          <span class="meta-chip"><b>Corridor</b> ${corridor}</span>
          <span class="meta-chip"><b>Language</b> ${langName}</span>
        </div>
        <p class="lede">Six specialists read your contract in parallel.
          When the FastAPI backend lands, each pane will fill with its verdict
          as it streams back. For now you're looking at the layout primitive.</p>
      </header>

      <div class="agent-grid">${agentsHtml}</div>

      <footer class="delib-foot">
        <button class="cta-ghost" id="back">← Back</button>
        <p class="hint">Backend not wired yet — agent verdicts arrive in the next scene drop.</p>
      </footer>
    </section>
  `;

  root.querySelector<HTMLButtonElement>("#back")!.addEventListener("click", () => {
    goto("intake");
  });

  gsap.from(".delib-head",  { opacity: 0, y: 20, duration: 0.7, ease: "power3.out" });
  gsap.from(".agent-pane",  {
    opacity: 0, y: 18,
    duration: 0.6, stagger: 0.07, delay: 0.2, ease: "power3.out",
  });
  gsap.from(".delib-foot",  { opacity: 0, y: 10, duration: 0.5, delay: 0.7, ease: "power3.out" });
}
