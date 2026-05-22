/**
 * Negotiation coach — the conversation script.
 *
 * After the reel surfaces the problems, this scene gives the worker the
 * concrete pre-conversation script: priority pushback, 4-6 questions
 * (in L1 + EN), red-flag recruiter responses.
 */
import { gsap } from "gsap";

import { MOCK_RESULT } from "../api/mock-result";
import { LANGUAGES } from "../data/samples";
import { Store } from "../state";
import type { SceneCtx } from "./router";

export function renderNegotiation(ctx: SceneCtx): void {
  const { root, goto } = ctx;
  const result = Store.get().result ?? MOCK_RESULT;
  const n = result.negotiation || MOCK_RESULT.negotiation;
  if (!n || !n.priority_pushback) {
    // Defensive — back to recommendation
    goto("recommendation");
    return;
  }
  const intake = Store.get().intake;
  const showEnglish = intake.language !== "en";
  const langName = LANGUAGES[intake.language] || intake.language;

  const pb: any = (n.priority_pushback && typeof n.priority_pushback === "object") ? n.priority_pushback : {};
  const pbClause = pb.clause_number ?? "—";
  const pbTopic = typeof pb.topic === "string" ? pb.topic.replace(/_/g, " ") : "general";
  const pbL1 = pb.what_to_say_in_l1 ?? "";
  const pbEn = pb.what_to_say_in_english ?? "";
  const pbFallback = pb.fallback_if_refused ?? "";
  const pbWalkaway = pb.walk_away_threshold ?? "";
  const hasPriority = pbL1 || pbEn || pb.topic;
  const questions = Array.isArray(n.questions) ? n.questions : [];
  const redFlags  = Array.isArray(n.red_flags) ? n.red_flags : [];
  const questionsHtml = questions.map((q: any, i: number) => `
    <article class="neg-question" style="--idx:'${i + 1}';">
      <header class="neg-question-head">
        <span class="neg-question-num">Q${i + 1}</span>
        <span class="neg-question-clause">${q.clause}</span>
      </header>
      <p class="neg-question-l1">${escape(q.question_l1)}</p>
      ${showEnglish ? `<p class="neg-question-en"><em>EN ·</em> ${escape(q.question_en)}</p>` : ""}
      <div class="neg-question-foot">
        <div class="neg-meta"><b>Why ask</b>${escape(q.why_ask)}</div>
        <div class="neg-meta"><b>Listen for</b>${escape(q.listen_for)}</div>
      </div>
    </article>
  `).join("");

  const redFlagsHtml = redFlags.map((r: any) => `
    <article class="neg-redflag">
      <div class="neg-redflag-says">
        <span class="neg-redflag-tag">If the recruiter says</span>
        <p>“${escape(r.if_recruiter_says)}”</p>
      </div>
      <div class="neg-redflag-means">
        <span class="neg-redflag-tag">It actually means</span>
        <p>${escape(r.what_it_means)}</p>
      </div>
      <div class="neg-redflag-move">
        <span class="neg-redflag-tag">Your move</span>
        <p>${escape(r.your_move)}</p>
      </div>
    </article>
  `).join("");

  root.innerHTML = `
    <section class="negotiation">
      <header class="neg-head">
        <div class="eyebrow"><span class="dot"></span>Negotiation coach · ${langName}</div>
        <h1 class="display-heading">What to <em>say</em> before signing</h1>
        <p class="lede">Other agents diagnosed. The Negotiator coaches.
          Information-gathering, never confrontation — workers who push back
          too hard get replaced; workers who ask precise questions get treated
          as informed.</p>
      </header>

      <article class="neg-strategy">
        <span class="neg-card-eyebrow">Strategy</span>
        <p>${escape(n.strategy)}</p>
      </article>

      ${hasPriority ? `<article class="neg-priority">
        <header class="neg-priority-head">
          <span class="neg-priority-tag"><span class="dot"></span>Priority pushback · Clause ${pbClause} · ${pbTopic}</span>
        </header>
        <p class="neg-priority-l1">${escape(pbL1)}</p>
        ${showEnglish && pbEn ? `<p class="neg-priority-en"><em>EN ·</em> ${escape(pbEn)}</p>` : ""}
        <div class="neg-priority-foot">
          ${pbFallback ? `<div class="neg-meta"><b>If refused</b>${escape(pbFallback)}</div>` : ""}
          ${pbWalkaway ? `<div class="neg-meta neg-walkaway"><b>Walk away if</b>${escape(pbWalkaway)}</div>` : ""}
        </div>
      </article>` : ""}

      <section class="neg-section">
        <h3 class="neg-section-title">Questions to ask · ${questions.length} of them</h3>
        <div class="neg-questions">${questionsHtml}</div>
      </section>

      <section class="neg-section">
        <h3 class="neg-section-title">Red-flag responses to listen for</h3>
        <div class="neg-redflags">${redFlagsHtml}</div>
      </section>

      <footer class="delib-foot">
        <button class="cta-ghost" id="back">← Back to disagreements</button>
        <button class="cta" id="continue">
          <span>See your recommendation</span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="2"
                  stroke-linecap="round" stroke-linejoin="round"/></svg>
        </button>
      </footer>
    </section>
  `;

  root.querySelector<HTMLButtonElement>("#back")!.addEventListener("click", () => goto("reel"));
  root.querySelector<HTMLButtonElement>("#continue")!.addEventListener("click", () => goto("recommendation"));

  gsap.fromTo(".neg-head",
    { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.7, ease: "power3.out", clearProps: "transform" });
  gsap.fromTo(".neg-strategy",
    { opacity: 0, y: 18 }, { opacity: 1, y: 0, duration: 0.6, delay: 0.2, ease: "power3.out", clearProps: "transform" });
  gsap.fromTo(".neg-priority",
    { opacity: 0, y: 18, scale: 0.99 },
    { opacity: 1, y: 0, scale: 1, duration: 0.7, delay: 0.35, ease: "power3.out", clearProps: "transform" });
  gsap.fromTo(".neg-question",
    { opacity: 0, y: 16 },
    { opacity: 1, y: 0, duration: 0.5, stagger: 0.05, delay: 0.55, ease: "power3.out", clearProps: "transform" });
  gsap.fromTo(".neg-redflag",
    { opacity: 0, y: 16 },
    { opacity: 1, y: 0, duration: 0.5, stagger: 0.07, delay: 0.8, ease: "power3.out", clearProps: "transform" });
  gsap.fromTo(".delib-foot",
    { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.5, delay: 1.0, ease: "power3.out", clearProps: "transform" });
}

function escape(s: any): string {
  if (s === null || s === undefined) return "";
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}
