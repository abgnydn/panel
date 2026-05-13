/**
 * Intake scene — pick a sample or upload your own contract, then go.
 *
 * Layout:
 *   - Eyebrow + display heading
 *   - Tab switcher: Sample · Upload
 *   - Sample grid: 8 cards (tier badge + corridor + description)
 *   - Upload drop zone (drag/drop + file input)
 *   - Sticky footer: language picker + Review CTA
 */
import { gsap } from "gsap";

import type { Sample } from "../data/samples";
import { LANGUAGES, SAMPLES, TIER_BADGE } from "../data/samples";
import { Store } from "../state";
import type { SceneCtx } from "./router";

export function renderIntake(ctx: SceneCtx): void {
  const { root, goto } = ctx;

  const sampleCards = SAMPLES.map((s) => sampleCardHtml(s)).join("");
  const langOptions = Object.entries(LANGUAGES)
    .map(([k, v]) => `<option value="${k}">${v}</option>`)
    .join("");

  root.innerHTML = `
    <section class="intake">
      <header class="intake-head">
        <div class="eyebrow"><span class="dot"></span>Intake</div>
        <h1 class="display-heading">Whose <em>contract</em>?</h1>
        <p class="lede">Pick a sample to see Panel work, or upload your own.
          The reading happens in your <em>mother tongue</em>.</p>
      </header>

      <div class="tabs" role="tablist">
        <button class="tab is-active" role="tab" data-tab="sample">Sample contracts</button>
        <button class="tab"             role="tab" data-tab="upload">Upload your own</button>
      </div>

      <div class="tab-panel" data-panel="sample">
        <div class="sample-grid">${sampleCards}</div>
      </div>

      <div class="tab-panel is-hidden" data-panel="upload">
        <label class="drop-zone" id="drop">
          <input type="file" id="file" accept=".pdf,.png,.jpg,.jpeg" hidden />
          <div class="drop-zone-inner">
            <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke-width="1.5"
                 stroke="currentColor" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="17 8 12 3 7 8"/>
              <line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
            <div class="drop-zone-title">Drop your contract here</div>
            <div class="drop-zone-sub">PDF, PNG, JPG · &lt; 10MB</div>
          </div>
        </label>
        <div class="upload-state" id="upload-state"></div>
      </div>

      <footer class="intake-foot">
        <div class="lang">
          <span class="lang-label">Your language</span>
          <select id="lang">${langOptions}</select>
        </div>
        <button class="cta" id="review" disabled>
          <span>Review</span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M5 12h14M13 6l6 6-6 6"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </button>
      </footer>
    </section>
  `;

  // ---- Tabs ---------------------------------------------------------------
  const tabs = root.querySelectorAll<HTMLButtonElement>(".tab");
  const panels = root.querySelectorAll<HTMLElement>(".tab-panel");
  tabs.forEach((t) =>
    t.addEventListener("click", () => {
      tabs.forEach((x) => x.classList.toggle("is-active", x === t));
      const which = t.dataset.tab;
      panels.forEach((p) => p.classList.toggle("is-hidden", p.dataset.panel !== which));
    }),
  );

  // ---- Sample cards -------------------------------------------------------
  const review = root.querySelector<HTMLButtonElement>("#review")!;
  const cards = root.querySelectorAll<HTMLButtonElement>(".sample-card");
  cards.forEach((c) =>
    c.addEventListener("click", () => {
      cards.forEach((x) => x.classList.toggle("is-selected", x === c));
      const id = c.dataset.sampleId!;
      const sample = SAMPLES.find((s) => s.id === id);
      if (sample) {
        Store.setIntake({ sample, file: undefined });
        review.disabled = false;
        review.classList.add("is-ready");
      }
    }),
  );

  // ---- Upload -------------------------------------------------------------
  const drop = root.querySelector<HTMLLabelElement>("#drop")!;
  const fileInput = root.querySelector<HTMLInputElement>("#file")!;
  const uploadState = root.querySelector<HTMLDivElement>("#upload-state")!;

  const onFile = (file: File) => {
    Store.setIntake({ file, sample: undefined });
    uploadState.innerHTML =
      `<div class="upload-pill"><b>${file.name}</b> · ${(file.size / 1024).toFixed(0)} KB</div>`;
    review.disabled = false;
    review.classList.add("is-ready");
  };

  fileInput.addEventListener("change", () => {
    if (fileInput.files && fileInput.files[0]) onFile(fileInput.files[0]);
  });
  ["dragenter", "dragover"].forEach((ev) =>
    drop.addEventListener(ev, (e) => {
      e.preventDefault();
      drop.classList.add("is-over");
    }),
  );
  ["dragleave", "drop"].forEach((ev) =>
    drop.addEventListener(ev, (e) => {
      e.preventDefault();
      drop.classList.remove("is-over");
    }),
  );
  drop.addEventListener("drop", (e: DragEvent) => {
    e.preventDefault();
    const f = e.dataTransfer?.files?.[0];
    if (f) onFile(f);
  });

  // ---- Language + review --------------------------------------------------
  const lang = root.querySelector<HTMLSelectElement>("#lang")!;
  lang.value = Store.get().intake.language;
  lang.addEventListener("change", () => Store.setIntake({ language: lang.value }));

  review.addEventListener("click", () => {
    if (review.disabled) return;
    goto("deliberation");
  });

  // Entrance animations are handled by CSS keyframes — GSAP `.from` was racing
  // with the router's scene-fade and leaving cards at opacity:0.
}

function sampleCardHtml(s: Sample): string {
  const t = TIER_BADGE[s.tier];
  return `
    <button class="sample-card" data-sample-id="${s.id}">
      <div class="sample-card-head">
        <span class="tier-badge" style="--tier-fg:${t.fg};--tier-bg:${t.bg};">
          <span class="dot"></span>${t.label}
        </span>
        <span class="sample-emoji">${s.emoji}</span>
      </div>
      <div class="sample-corridor">${s.origin_label} <span class="arrow">→</span> ${s.destination_label}</div>
      <div class="sample-label">${s.label.replace(/^.*?·\s*/, "")}</div>
      <p class="sample-desc">${s.description}</p>
    </button>
  `;
}
