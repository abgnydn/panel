/**
 * Recommendation scene — the dignity moment.
 *
 * Urgency gauge (animated fill), worker tldr in their L1, action items,
 * contacts, export buttons. Pacing slows down here — this is the "letter
 * to the worker" register.
 */
import { gsap } from "gsap";

import { MOCK_RESULT } from "../api/mock-result";
import { Store } from "../state";
import { LANGUAGES } from "../data/samples";
import type { SceneCtx } from "./router";

export function renderRecommendation(ctx: SceneCtx): void {
  const { root, goto } = ctx;
  const r = MOCK_RESULT.recommendation;
  const urgency = MOCK_RESULT.final_urgency_score;
  const intake = Store.get().intake;
  const langName = LANGUAGES[intake.language] || intake.language;

  const gauge = urgencyGaugeHtml(urgency);
  const actions = r.action_items.map((a) => `<li>${a}</li>`).join("");
  const contacts = r.contacts.map(contactHtml).join("");

  root.innerHTML = `
    <section class="recommendation">
      <header class="rec-head">
        <div class="eyebrow"><span class="dot"></span>The verdict · For you</div>
        <h1 class="display-heading">A letter, <em>to you</em></h1>
        <p class="lede">Synthesised across all six agents and Round 2. Saved offline,
          this is what you carry into the recruiter's office and onto the plane.
          Rendered in <em>${langName}</em>.</p>
      </header>

      ${gauge}

      <article class="rec-letter">
        <div class="rec-letter-mark">¶</div>
        <p class="rec-tldr">${r.tldr}</p>
      </article>

      <section class="rec-block">
        <h3 class="rec-block-title">What to do</h3>
        <ul class="rec-action-list">${actions}</ul>
      </section>

      <section class="rec-block">
        <h3 class="rec-block-title">Save these contacts offline</h3>
        <div class="rec-contacts">${contacts}</div>
      </section>

      <p class="rec-disclaimer">
        Panel provides information only — not legal advice. For urgent help,
        contact your embassy.
      </p>

      <footer class="delib-foot">
        <button class="cta-ghost" id="back">← Back to reel</button>
        <button class="cta" id="restart">
          <span>Review another contract</span>
        </button>
      </footer>
    </section>
  `;

  root.querySelector<HTMLButtonElement>("#back")!.addEventListener("click", () => goto("reel" as never));
  root.querySelector<HTMLButtonElement>("#restart")!.addEventListener("click", () => goto("intake"));

  gsap.fromTo(".rec-head",
    { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.7, ease: "power3.out", clearProps: "transform" });
  gsap.fromTo(".urgency-gauge",
    { opacity: 0, y: 18 }, { opacity: 1, y: 0, duration: 0.7, delay: 0.15, ease: "power3.out", clearProps: "transform" });
  gsap.fromTo(".urgency-fill",
    { width: "0%" }, { width: `${urgency * 10}%`, duration: 1.2, delay: 0.35, ease: "power3.out" });
  gsap.fromTo(".rec-letter",
    { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.8, delay: 0.45, ease: "power3.out", clearProps: "transform" });
  gsap.fromTo(".rec-block",
    { opacity: 0, y: 18 },
    { opacity: 1, y: 0, duration: 0.6, stagger: 0.12, delay: 0.7, ease: "power3.out", clearProps: "transform" });
  gsap.fromTo(".rec-disclaimer",
    { opacity: 0 }, { opacity: 0.7, duration: 0.5, delay: 1.1, ease: "power2.out" });
  gsap.fromTo(".delib-foot",
    { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.5, delay: 1.2, ease: "power3.out", clearProps: "transform" });
}

function urgencyGaugeHtml(score: number): string {
  let color: string;
  let verdict: string;
  if (score >= 8) {
    color = "#dc2626";
    verdict = "Critical — act before signing";
  } else if (score >= 5) {
    color = "#ea580c";
    verdict = "Elevated — significant concerns";
  } else if (score >= 3) {
    color = "#f59e0b";
    verdict = "Moderate — proceed with eyes open";
  } else {
    color = "#15803d";
    verdict = "Low — contract largely compliant";
  }
  return `
    <div class="urgency-gauge" style="--urgency-fg:${color};">
      <div class="urgency-number">
        <span class="urgency-value">${score}</span><span class="urgency-of">/10</span>
      </div>
      <div class="urgency-bar-wrap">
        <div class="urgency-label">Urgency</div>
        <div class="urgency-bar"><div class="urgency-fill"></div></div>
        <div class="urgency-verdict">${verdict}</div>
      </div>
    </div>
  `;
}

function contactHtml(c: { name: string; phone?: string; whatsapp?: string }): string {
  const phone = c.phone ? `<span class="contact-phone tabular">${c.phone}</span>` : "";
  const wa = c.whatsapp
    ? `<span class="contact-wa tabular">WhatsApp · ${c.whatsapp}</span>`
    : "";
  return `
    <div class="contact-card">
      <div class="contact-name">${c.name}</div>
      <div class="contact-lines">${phone}${wa}</div>
    </div>
  `;
}
