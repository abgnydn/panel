/**
 * Scene router — fade-through transitions between top-level scenes.
 *
 * No real history support yet; we only ever move forward through the flow.
 * Each scene's render function takes `{ root, goto }` so it can invoke the
 * next scene when its CTA fires.
 */
import { gsap } from "gsap";

import { renderColdOpen } from "./cold-open";
import { renderIntake } from "./intake";
import { renderDeliberation } from "./deliberation";
import { renderRebuttals } from "./rebuttals";
import { renderReel } from "./reel";
import { renderNegotiation } from "./negotiation";
import { renderRecommendation } from "./recommendation";

export type SceneId =
  | "cold-open"
  | "intake"
  | "deliberation"
  | "rebuttals"
  | "reel"
  | "negotiation"
  | "recommendation";

export type SceneCtx = {
  root: HTMLElement;
  goto: (next: SceneId) => void;
};

export function mountRouter(root: HTMLElement): void {
  const ctx: SceneCtx = {
    root,
    goto: (next) => transition(next),
  };
  renderColdOpen(ctx);

  function transition(next: SceneId): void {
    gsap.to(root, {
      opacity: 0,
      y: -8,
      duration: 0.32,
      ease: "power2.in",
      onComplete: () => {
        if (next === "cold-open") renderColdOpen(ctx);
        else if (next === "intake") renderIntake(ctx);
        else if (next === "deliberation") renderDeliberation(ctx);
        else if (next === "rebuttals") renderRebuttals(ctx);
        else if (next === "reel") renderReel(ctx);
        else if (next === "negotiation") renderNegotiation(ctx);
        else if (next === "recommendation") renderRecommendation(ctx);
        gsap.fromTo(
          root,
          { opacity: 0, y: 8 },
          { opacity: 1, y: 0, duration: 0.55, ease: "power3.out" },
        );
      },
    });
  }
}
