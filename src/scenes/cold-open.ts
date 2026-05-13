/**
 * Cold open — the landing experience.
 *
 * Sequence:
 *   0.0s  Brand mark fades up + slow float begins
 *   0.3s  "Panel" letters stagger-rise from below
 *   1.6s  Subtitle typewriter at ~33ms/char
 *   2.2s  Stat counters tween from 0 → target with custom formatter
 *   3.8s  CTA fades in with magnetic-hover wiring
 */
import { gsap } from "gsap";

import type { SceneCtx } from "./router";

const BRAND_MARK_SVG = `
<svg width="72" height="72" viewBox="0 0 72 72" xmlns="http://www.w3.org/2000/svg">
  <rect x="4"  y="34" width="7" height="34" rx="2" fill="var(--agent-lawyer)"/>
  <rect x="14" y="26" width="7" height="42" rx="2" fill="var(--agent-translator)"/>
  <rect x="24" y="38" width="7" height="30" rx="2" fill="var(--agent-regulator)"/>
  <rect x="34" y="20" width="7" height="48" rx="2" fill="var(--agent-peer)"/>
  <rect x="44" y="30" width="7" height="38" rx="2" fill="var(--agent-triage)"/>
  <rect x="54" y="14" width="7" height="54" rx="2" fill="var(--agent-negotiator)"/>
</svg>`;

const SUBTITLE = "A panel of AI specialists reads your contract — in your language.";

const STATS: Array<{ target: number; suffix: string; label: string; format?: (n: number) => string }> = [
  {
    target: 10_000_000,
    suffix: "+",
    label: "Filipinos working abroad",
    format: (n) => `${(n / 1_000_000).toFixed(0)}M+`,
  },
  {
    target: 700_000,
    suffix: "",
    label: "Indonesians leaving / year",
    format: (n) => `${Math.round(n / 1_000)}K`,
  },
  {
    target: 0,
    suffix: "",
    label: "legal aid before signing",
    format: () => "$0",
  },
];

export function renderColdOpen(ctx: SceneCtx): void {
  const { root, goto } = ctx;
  const letters = [..."Panel"]
    .map((ch) => `<span class="letter">${ch}</span>`)
    .join("");

  const statHtml = STATS.map(
    (s, i) =>
      `<div class="stat" data-i="${i}">
         <b class="counter tabular">0</b>
         <span>${s.label}</span>
       </div>`,
  ).join("");

  root.innerHTML = `
    <section class="cold-open">
      <div class="cold-open-inner">
        <div class="brand-mark">${BRAND_MARK_SVG}</div>
        <h1 class="display-title" aria-label="Panel">${letters}</h1>
        <p class="subtitle"><span class="typed"></span><span class="caret"></span></p>
        <div class="stats">${statHtml}</div>
        <button class="cta" id="begin">
          <span>Begin · Review a contract</span>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="2"
                  stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </section>
  `;

  // --- Brand mark ----------------------------------------------------------
  gsap.from(".brand-mark", { opacity: 0, y: 20, duration: 1.2, ease: "power3.out" });

  // --- Letter reveal -------------------------------------------------------
  gsap.from(".display-title .letter", {
    y: 80,
    opacity: 0,
    duration: 1.1,
    stagger: 0.08,
    ease: "power4.out",
    delay: 0.3,
  });

  // --- Subtitle typewriter -------------------------------------------------
  const typed = root.querySelector<HTMLSpanElement>(".typed");
  const caret = root.querySelector<HTMLSpanElement>(".caret");
  if (typed && caret) {
    let i = 0;
    const begin = () => {
      const id = window.setInterval(() => {
        i += 1;
        typed.innerHTML = decorate(SUBTITLE.slice(0, i));
        if (i >= SUBTITLE.length) {
          window.clearInterval(id);
        }
      }, 32);
    };
    window.setTimeout(begin, 1600);
  }

  // --- Stat counters -------------------------------------------------------
  root.querySelectorAll<HTMLElement>(".stat").forEach((statEl, idx) => {
    const cfg = STATS[idx];
    if (!cfg) return;
    const counter = statEl.querySelector<HTMLElement>(".counter");
    if (!counter) return;

    if (cfg.target === 0) {
      gsap.to(counter, {
        opacity: 1,
        delay: 2.2 + idx * 0.12,
        duration: 0.5,
        onStart: () => {
          counter.textContent = cfg.format ? cfg.format(0) : "0";
        },
      });
      return;
    }
    const obj = { v: 0 };
    gsap.to(obj, {
      v: cfg.target,
      duration: 1.8,
      delay: 2.2 + idx * 0.12,
      ease: "power3.out",
      onUpdate() {
        counter.textContent = cfg.format ? cfg.format(obj.v) : Math.round(obj.v).toString();
      },
    });
  });

  // --- CTA fade + magnetic hover ------------------------------------------
  const cta = root.querySelector<HTMLButtonElement>(".cta");
  if (cta) {
    gsap.from(cta, { opacity: 0, y: 16, duration: 0.9, delay: 3.8, ease: "power3.out" });

    let raf = 0;
    let tx = 0, ty = 0;
    let cx = 0, cy = 0;

    cta.addEventListener("mousemove", (e) => {
      const r = cta.getBoundingClientRect();
      tx = (e.clientX - r.left - r.width / 2) * 0.25;
      ty = (e.clientY - r.top - r.height / 2) * 0.45;
      if (!raf) raf = requestAnimationFrame(animate);
    });
    cta.addEventListener("mouseleave", () => {
      tx = 0; ty = 0;
      if (!raf) raf = requestAnimationFrame(animate);
    });

    function animate() {
      cx += (tx - cx) * 0.18;
      cy += (ty - cy) * 0.18;
      cta!.style.transform = `translate3d(${cx.toFixed(2)}px, ${cy.toFixed(2)}px, 0)`;
      if (Math.abs(tx - cx) > 0.1 || Math.abs(ty - cy) > 0.1) {
        raf = requestAnimationFrame(animate);
      } else {
        raf = 0;
      }
    }

    cta.addEventListener("click", () => goto("intake"));
  }
}

/** Render <em>...</em> for the "in your language" accent inside the typed string. */
function decorate(text: string): string {
  return text.replace(
    /— in your language\.?$/,
    (m) => `— <em>${m.slice(2)}</em>`,
  );
}
