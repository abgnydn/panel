/**
 * Deliberation scene.
 *
 * Currently driven by mocked data (src/api/mock-result.ts) so the flow plays
 * end-to-end without a backend. When the FastAPI server lands, swap the
 * MOCK_RESULT import for `await fetchPanel(intake)`.
 *
 * Sequence:
 *   0.0s  Eyebrow + heading fade in
 *   0.3s  6 agent panes appear with skeleton shimmer
 *   1.5s+ Agents settle one-by-one with their verdicts, staggered to mimic
 *         the ~30-110s spread we get from real Claude calls
 */
import { gsap } from "gsap";

import { MOCK_RESULT } from "../api/mock-result";
import type { AgentOutput, PanelResult } from "../api/mock-result";
import { runPanelWithFallback } from "../api/panel";
import { Store } from "../state";
import { LANGUAGES } from "../data/samples";
import { AGENTS, agentIconHtml } from "../ui/agents";
import { icon } from "../ui/icons";
import type { SceneCtx } from "./router";

// Reveal cadence (seconds). Spread chosen to mimic the real-claude wall clock
// without being painfully slow. Earliest at 1.5s, latest at 4.5s.
const REVEAL_AT: Record<string, number> = {
  triage:        1.5,
  lawyer:        2.0,
  translator:    2.5,
  peer_advocate: 3.2,
  negotiator:    3.8,
  regulator:     4.5,
};

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

  const panesHtml = AGENTS.map((a) => `
    <div class="agent-pane" data-agent="${a.id}" style="--agent-tint:${a.tint};">
      <div class="agent-pane-head">
        <div class="agent-pane-avatar">${agentIconHtml(a.id, "icon-md")}</div>
        <div>
          <div class="agent-pane-name">${a.name}</div>
          <div class="agent-pane-tagline">${a.tagline}</div>
        </div>
        <div class="agent-pane-latency" data-latency></div>
      </div>
      <div class="agent-pane-body" data-body>
        <div class="agent-pane-status">
          <span class="dot"></span>
          <span class="status-text">Reading the contract…</span>
        </div>
        <div class="skeleton-stack">
          <div class="skeleton-line" style="width:90%;"></div>
          <div class="skeleton-line" style="width:75%;"></div>
          <div class="skeleton-line" style="width:60%;"></div>
        </div>
      </div>
    </div>
  `).join("");

  root.innerHTML = `
    <section class="deliberation">
      <header class="delib-head">
        <div class="eyebrow"><span class="dot"></span>Round 1 · Panel deliberation</div>
        <h1 class="display-heading">The panel <em>convenes</em></h1>
        <div class="delib-meta">
          <span class="meta-chip"><b>Corridor</b> ${corridor}</span>
          <span class="meta-chip"><b>Language</b> ${langName}</span>
          <span class="meta-chip is-pulse"><b>Status</b> <span data-progress>0 / 6</span></span>
        </div>
      </header>

      <div class="agent-grid">${panesHtml}</div>

      <footer class="delib-foot">
        <button class="cta-ghost" id="back">← Back</button>
        <button class="cta" id="continue" disabled>
          <span>See the panel react</span>
          ${icon("arrow_right", "icon-sm")}
        </button>
      </footer>
    </section>
  `;

  root.querySelector<HTMLButtonElement>("#back")!.addEventListener("click", () => goto("intake"));
  const cont = root.querySelector<HTMLButtonElement>("#continue")!;
  cont.addEventListener("click", () => goto("rebuttals"));

  // Entrance
  gsap.fromTo(".delib-head",
    { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.7, ease: "power3.out", clearProps: "transform" });
  gsap.fromTo(".agent-pane",
    { opacity: 0, y: 18 },
    { opacity: 1, y: 0, duration: 0.6, stagger: 0.07, delay: 0.2, ease: "power3.out", clearProps: "transform" });
  gsap.fromTo(".delib-foot",
    { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.5, delay: 0.7, ease: "power3.out", clearProps: "transform" });

  const progressEl = root.querySelector<HTMLSpanElement>("[data-progress]")!;

  // Call backend (Mosaic AI / 6 agents in parallel). Backend is slow
  // (30-60s for live; instant for mock). While waiting, keep skeletons.
  if (sample) {
    const t0 = performance.now();
    runPanelWithFallback({
      sample_id: sample.id,
      situation: intake.situation || "",
      destination_country: sample.destination,
      origin_country: sample.origin,
      worker_l1: intake.language,
    }).then(({ result, source }) => {
      Store.setResult(result, source);
      revealAgentsStaggered(root, result, performance.now() - t0, source, cont, progressEl);
    });
  } else {
    // Upload path — not wired to backend OCR yet, fall back to mock.
    revealAgentsStaggered(root, MOCK_RESULT, 0, "mock", cont, progressEl);
  }
}

/** Stagger-reveal agents from a live (or mock) result, keeping the
 *  cinematic feel even when the backend returned all 6 at once. */
function revealAgentsStaggered(
  root: HTMLElement,
  result: PanelResult,
  totalElapsedMs: number,
  source: "live" | "mock",
  cont: HTMLButtonElement,
  progressEl: HTMLSpanElement,
): void {
  const order = ["triage", "lawyer", "translator", "peer_advocate", "negotiator", "regulator"];
  const baseDelay = source === "mock" ? 1200 : 200;
  const stepDelay = source === "mock" ? 900 : 250;
  let completed = 0;

  order.forEach((agentId, i) => {
    const out = result.agents[agentId] as AgentOutput | undefined;
    if (!out) return;
    window.setTimeout(() => {
      settlePane(root, agentId, out, () => {
        completed += 1;
        progressEl.textContent = `${completed} / 6`;
        if (completed === 6) {
          cont.disabled = false;
          cont.classList.add("is-ready");
          const label = source === "live"
            ? `All agents settled · ${(totalElapsedMs / 1000).toFixed(1)}s on Mosaic AI`
            : "All agents settled · mock fallback";
          progressEl.textContent = label;
        }
      });
    }, baseDelay + i * stepDelay);
  });
}

function settlePane(
  root: HTMLElement,
  agentId: string,
  out: AgentOutput,
  done: () => void,
): void {
  const pane = root.querySelector<HTMLElement>(`.agent-pane[data-agent="${agentId}"]`);
  if (!pane) return;
  const body = pane.querySelector<HTMLDivElement>("[data-body]")!;
  const latencyEl = pane.querySelector<HTMLDivElement>("[data-latency]")!;

  const latencyS = (out.latency_ms || 0) / 1000;
  latencyEl.textContent = latencyS > 0 ? `${latencyS.toFixed(1)}s` : "";

  const findings = (out.key_findings || []).slice(0, 4)
    .map((f) => `<li>${f}</li>`).join("");
  body.innerHTML = `
    <div class="agent-pane-verdict">${out.verdict_summary}</div>
    <ul class="agent-pane-findings">${findings}</ul>
  `;
  pane.classList.add("is-settled");
  gsap.fromTo(pane,
    { scale: 0.985 }, { scale: 1, duration: 0.45, ease: "back.out(2)" });
  gsap.fromTo(body,
    { opacity: 0, y: 6 }, { opacity: 1, y: 0, duration: 0.5, ease: "power3.out", clearProps: "transform" });
  done();
}
