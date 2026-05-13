/**
 * Recommendation — the final dignity scene.
 *
 * Sections, in order:
 *   1. Urgency gauge (animated fill)
 *   2. Letter-style tldr (serif italic with paragraph-mark watermark)
 *   3. What to do (action items)
 *   4. Save offline contacts
 *   5. Pre-departure checklist (4-phase tabs)
 *   6. Do NOT agree to / Ask the recruiter to change (refusals + pushbacks)
 *   7. What-if simulator (interactive — toggles + urgency delta)
 *   8. Take it with you (Markdown download + QR placeholder)
 *   9. Disclaimer
 */
import { gsap } from "gsap";

import { MOCK_RESULT } from "../api/mock-result";
import type { ChecklistItem } from "../api/mock-result";
import { Store } from "../state";
import { LANGUAGES } from "../data/samples";
import type { SceneCtx } from "./router";

const PHASE_LABEL: Record<keyof typeof MOCK_RESULT.checklist, string> = {
  before_departure: "Before departure",
  on_arrival: "On arrival",
  during_employment: "During employment",
  exit_emergency: "Exit / emergency",
};
const PRIORITY_COLOR: Record<ChecklistItem["priority"], string> = {
  critical: "#b91c1c",
  high: "#ea580c",
  medium: "#eab308",
};

export function renderRecommendation(ctx: SceneCtx): void {
  const { root, goto } = ctx;
  const r = MOCK_RESULT.recommendation;
  const urgency = MOCK_RESULT.final_urgency_score;
  const intake = Store.get().intake;
  const langName = LANGUAGES[intake.language] || intake.language;

  root.innerHTML = `
    <section class="recommendation">
      <header class="rec-head">
        <div class="eyebrow"><span class="dot"></span>The verdict · For you · ${langName}</div>
        <h1 class="display-heading">A letter, <em>to you</em></h1>
        <p class="lede">Synthesised across all six agents and Round 2. This is the
          page you save offline before flying.</p>
      </header>

      ${urgencyGaugeHtml(urgency)}

      <article class="rec-letter">
        <div class="rec-letter-mark">¶</div>
        <p class="rec-tldr">${escape(r.tldr)}</p>
      </article>

      <section class="rec-block">
        <h3 class="rec-block-title">What to do</h3>
        <ul class="rec-action-list">${r.action_items.map((a) => `<li>${escape(a)}</li>`).join("")}</ul>
      </section>

      <section class="rec-block">
        <h3 class="rec-block-title">Save these contacts offline</h3>
        <div class="rec-contacts">${r.contacts.map(contactHtml).join("")}</div>
      </section>

      ${checklistSectionHtml()}

      ${refusalsSectionHtml()}

      ${pushbacksSectionHtml()}

      ${whatIfSectionHtml(urgency)}

      ${exportSectionHtml()}

      <p class="rec-disclaimer">
        Panel provides information only — not legal advice.
        For urgent help, contact your embassy.
      </p>

      <footer class="delib-foot">
        <button class="cta-ghost" id="back">← Back to negotiation coach</button>
        <button class="cta" id="restart"><span>Review another contract</span></button>
      </footer>
    </section>
  `;

  // ---- Navigation ---------------------------------------------------------
  root.querySelector<HTMLButtonElement>("#back")!.addEventListener("click", () => goto("negotiation"));
  root.querySelector<HTMLButtonElement>("#restart")!.addEventListener("click", () => goto("intake"));

  // ---- Checklist tabs -----------------------------------------------------
  const tabs = root.querySelectorAll<HTMLButtonElement>(".chk-tab");
  const panels = root.querySelectorAll<HTMLElement>(".chk-panel");
  tabs.forEach((t) =>
    t.addEventListener("click", () => {
      tabs.forEach((x) => x.classList.toggle("is-active", x === t));
      const k = t.dataset.phase!;
      panels.forEach((p) => p.classList.toggle("is-hidden", p.dataset.phase !== k));
    }),
  );

  // ---- What-if simulator --------------------------------------------------
  const whatifBoxes = root.querySelectorAll<HTMLInputElement>(".whatif-check");
  const sim = root.querySelector<HTMLButtonElement>("#whatif-sim")!;
  const before = root.querySelector<HTMLSpanElement>("#whatif-before")!;
  const after = root.querySelector<HTMLSpanElement>("#whatif-after")!;
  const verdict = root.querySelector<HTMLSpanElement>("#whatif-verdict")!;
  const fillBar = root.querySelector<HTMLDivElement>("#whatif-fill")!;

  before.textContent = `${urgency}`;
  after.textContent = `${urgency}`;
  sim.addEventListener("click", () => {
    const selected = [...whatifBoxes].filter((b) => b.checked).length;
    const drop = Math.min(urgency, selected * 2);
    const newUrgency = Math.max(0, urgency - drop);
    after.textContent = `${newUrgency}`;
    verdict.textContent = verdictLabel(urgency, newUrgency);
    gsap.fromTo(fillBar, { width: `${urgency * 10}%` }, { width: `${newUrgency * 10}%`, duration: 0.9, ease: "power3.out" });
    gsap.fromTo(after, { scale: 1.3, color: "#dc2626" }, { scale: 1, color: "#0f172a", duration: 0.6, ease: "back.out(2)" });
  });

  // ---- Export -------------------------------------------------------------
  root.querySelector<HTMLButtonElement>("#export-md")!.addEventListener("click", () => downloadMarkdown());

  // ---- Entrance animations ------------------------------------------------
  gsap.fromTo(".rec-head",        { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.7, ease: "power3.out", clearProps: "transform" });
  gsap.fromTo(".urgency-gauge",   { opacity: 0, y: 18 }, { opacity: 1, y: 0, duration: 0.7, delay: 0.15, ease: "power3.out", clearProps: "transform" });
  gsap.fromTo(".urgency-fill",    { width: "0%" }, { width: `${urgency * 10}%`, duration: 1.2, delay: 0.35, ease: "power3.out" });
  gsap.fromTo(".rec-letter",      { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.8, delay: 0.45, ease: "power3.out", clearProps: "transform" });
  gsap.fromTo(".rec-block",       { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.6, stagger: 0.08, delay: 0.7, ease: "power3.out", clearProps: "transform" });
  gsap.fromTo(".rec-disclaimer",  { opacity: 0 }, { opacity: 0.7, duration: 0.5, delay: 1.2, ease: "power2.out" });
  gsap.fromTo(".delib-foot",      { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.5, delay: 1.3, ease: "power3.out", clearProps: "transform" });
}

// ---------------------------------------------------------------------------
// Section builders
// ---------------------------------------------------------------------------
function urgencyGaugeHtml(score: number): string {
  let color: string;
  let v: string;
  if (score >= 8)      { color = "#dc2626"; v = "Critical — act before signing"; }
  else if (score >= 5) { color = "#ea580c"; v = "Elevated — significant concerns"; }
  else if (score >= 3) { color = "#f59e0b"; v = "Moderate — proceed with eyes open"; }
  else                 { color = "#15803d"; v = "Low — contract largely compliant"; }
  return `
    <div class="urgency-gauge" style="--urgency-fg:${color};">
      <div class="urgency-number">
        <span class="urgency-value">${score}</span><span class="urgency-of">/10</span>
      </div>
      <div class="urgency-bar-wrap">
        <div class="urgency-label">Urgency</div>
        <div class="urgency-bar"><div class="urgency-fill"></div></div>
        <div class="urgency-verdict">${v}</div>
      </div>
    </div>
  `;
}

function contactHtml(c: { name: string; phone?: string; whatsapp?: string }): string {
  const phone = c.phone ? `<span class="contact-phone tabular">${c.phone}</span>` : "";
  const wa = c.whatsapp ? `<span class="contact-wa tabular">WhatsApp · ${c.whatsapp}</span>` : "";
  return `
    <div class="contact-card">
      <div class="contact-name">${escape(c.name)}</div>
      <div class="contact-lines">${phone}${wa}</div>
    </div>
  `;
}

function checklistSectionHtml(): string {
  const phases = Object.entries(MOCK_RESULT.checklist) as [keyof typeof MOCK_RESULT.checklist, ChecklistItem[]][];
  const tabsHtml = phases.map(([k], i) =>
    `<button class="chk-tab ${i === 0 ? "is-active" : ""}" data-phase="${k}">${PHASE_LABEL[k]}</button>`,
  ).join("");
  const panelsHtml = phases.map(([k, items], i) => `
    <div class="chk-panel ${i === 0 ? "" : "is-hidden"}" data-phase="${k}">
      ${items.map(checklistItemHtml).join("")}
    </div>
  `).join("");

  return `
    <section class="rec-block rec-checklist">
      <h3 class="rec-block-title">📋 Pre-departure checklist · save offline</h3>
      <div class="chk-tabs">${tabsHtml}</div>
      <div class="chk-panels">${panelsHtml}</div>
    </section>
  `;
}

function checklistItemHtml(it: ChecklistItem): string {
  const color = PRIORITY_COLOR[it.priority] || "#64748b";
  return `
    <div class="chk-item" style="--prio:${color};">
      <div class="chk-item-row">
        <span class="chk-item-prio">${it.priority.toUpperCase()}</span>
        <span class="chk-item-action">${escape(it.action)}</span>
      </div>
      ${it.details ? `<div class="chk-item-details">${escape(it.details)}</div>` : ""}
    </div>
  `;
}

function refusalsSectionHtml(): string {
  if (!MOCK_RESULT.refusals.length) return "";
  return `
    <section class="rec-block rec-refusals">
      <h3 class="rec-block-title">🛑 Do NOT agree to</h3>
      <div class="refusal-list">
        ${MOCK_RESULT.refusals.map((r) => `
          <article class="refusal-card">
            <div class="refusal-text">${escape(r.refusal)}</div>
            <div class="refusal-reason">${escape(r.reason)}</div>
          </article>
        `).join("")}
      </div>
    </section>
  `;
}

function pushbacksSectionHtml(): string {
  if (!MOCK_RESULT.pushbacks.length) return "";
  return `
    <section class="rec-block rec-pushbacks">
      <h3 class="rec-block-title">📝 Ask the recruiter to change before signing</h3>
      <div class="pushback-list">
        ${MOCK_RESULT.pushbacks.map((p) => `
          <article class="pushback-card">
            <header class="pushback-card-head">
              <span class="pushback-clause">Clause ${p.clause_number}</span>
              <span class="pushback-ask">${escape(p.ask)}</span>
            </header>
            <div class="pushback-suggested">
              <span class="pushback-suggested-tag">Suggested replacement</span>
              <em>${escape(p.suggested)}</em>
            </div>
          </article>
        `).join("")}
      </div>
    </section>
  `;
}

function whatIfSectionHtml(urgency: number): string {
  const checks = MOCK_RESULT.pushbacks.map((p, i) => `
    <label class="whatif-row">
      <input type="checkbox" class="whatif-check" data-i="${i}">
      <span class="whatif-clause">Clause ${p.clause_number}</span>
      <span class="whatif-ask">${escape(p.ask)}</span>
    </label>
  `).join("");
  return `
    <section class="rec-block rec-whatif">
      <h3 class="rec-block-title">🪄 What if the recruiter agrees?</h3>
      <p class="rec-block-lede">Tick the amendments you'd ask for, then simulate.
        See how your urgency score drops as each one is accepted.</p>
      <div class="whatif-controls">${checks}</div>
      <button class="cta" id="whatif-sim" style="margin-top:14px;">
        <span>Simulate amendments</span>
      </button>
      <div class="whatif-result">
        <div class="whatif-metrics">
          <div class="whatif-metric">
            <span class="whatif-label">Before</span>
            <span class="whatif-num tabular" id="whatif-before">${urgency}</span><span class="whatif-of">/10</span>
          </div>
          <div class="whatif-arrow">→</div>
          <div class="whatif-metric whatif-metric-after">
            <span class="whatif-label">After</span>
            <span class="whatif-num tabular" id="whatif-after">${urgency}</span><span class="whatif-of">/10</span>
          </div>
        </div>
        <div class="whatif-bar"><div class="whatif-fill" id="whatif-fill" style="width:${urgency * 10}%;"></div></div>
        <p class="whatif-verdict" id="whatif-verdict">Tick at least one amendment, then click Simulate.</p>
      </div>
    </section>
  `;
}

function exportSectionHtml(): string {
  return `
    <section class="rec-block rec-export">
      <h3 class="rec-block-title">📥 Take it with you</h3>
      <p class="rec-block-lede">Save this letter offline before you fly. Print, screenshot, share via WhatsApp.</p>
      <div class="export-row">
        <button class="cta-ghost" id="export-md">
          <span>↓ Download Markdown</span>
        </button>
        <button class="cta-ghost" id="export-qr-stub" disabled>
          <span>↓ Generate QR (coming soon)</span>
        </button>
        <button class="cta-ghost" id="export-pdf-stub" disabled>
          <span>↓ Generate PDF (coming soon)</span>
        </button>
      </div>
    </section>
  `;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function verdictLabel(before: number, after: number): string {
  const drop = before - after;
  if (drop >= 4) return "Dramatic improvement — worker is meaningfully safer.";
  if (drop >= 2) return "Real improvement, but residual risk remains.";
  if (drop >= 1) return "Modest improvement — most risks unaddressed.";
  if (drop === 0) return "No improvement — these amendments don't move the needle.";
  return "Counter-intuitive: amended contract scored worse.";
}

function downloadMarkdown(): void {
  const md = toMarkdown(MOCK_RESULT);
  const blob = new Blob([md], { type: "text/markdown" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "panel-review.md";
  a.click();
  URL.revokeObjectURL(a.href);
}

function toMarkdown(r: typeof MOCK_RESULT): string {
  const intake = Store.get().intake;
  const lang = LANGUAGES[intake.language] || intake.language;
  return [
    "# Panel — Your Contract Review",
    "",
    `**Urgency:** ${r.final_urgency_score}/10`,
    `**Language:** ${lang}`,
    "",
    "## Summary",
    "",
    r.recommendation.tldr,
    "",
    "## What to do",
    "",
    ...r.recommendation.action_items.map((a) => `- ${a}`),
    "",
    "## Save these contacts",
    "",
    ...r.recommendation.contacts.map((c) =>
      `- **${c.name}**${c.phone ? ` — ${c.phone}` : ""}${c.whatsapp ? ` — WhatsApp ${c.whatsapp}` : ""}`,
    ),
    "",
    "## Do NOT agree to",
    "",
    ...r.refusals.map((x) => `- **${x.refusal}** — ${x.reason}`),
    "",
    "## Ask the recruiter to change",
    "",
    ...r.pushbacks.map((p) => `- Clause ${p.clause_number}: ${p.ask}\n  - Suggested: _${p.suggested}_`),
    "",
    "## Where the panel disagrees",
    "",
    ...r.disagreement_reel.flatMap((d) => [
      `### #${d.rank} · ${d.topic}`,
      ...d.tensions.map((t) => `- **${t.agent}:** ${t.verdict}`),
      `_${d.why_it_matters}_`,
      "",
    ]),
    "",
    "_Panel provides information only — not legal advice._",
  ].join("\n");
}

function escape(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}
