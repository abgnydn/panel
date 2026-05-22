# Panel — v2 (cinematic)

A vanilla TypeScript + Three.js + GSAP rewrite of [Panel](../panel/) for the demo / portfolio
register. Same agent backend, completely different presentation.

> The Streamlit version is the hackathon submission. This is what Panel looks
> like when there are no framework constraints — the version we'd put in front
> of an ILO partner or an actual migrant worker.

## Stack

| Layer | Choice |
|---|---|
| Build | Vite 5 |
| Language | TypeScript 5 (strict) |
| 3D / WebGL | Three.js 0.169 — custom shaders |
| Animation | GSAP 3 |
| Typography | Inter + Instrument Serif + JetBrains Mono (Google Fonts) |
| State | Module-level signals (~30 lines, when needed) |
| Backend | reuses the FastAPI-wrapped agents from `../panel/app/` |
| Deploy | Static bundle → Cloudflare Pages OR served by FastAPI from Databricks Apps |

Total bundle target: **~200KB gzipped**. No framework runtime.

## Run

```bash
cd panel-v2
npm install
npm run dev
```

Opens at http://127.0.0.1:5173.

## Status

- [x] **Cold open** — fluid WebGL background, letter-by-letter title reveal,
      subtitle typewriter, stat counter tweens, magnetic CTA
- [ ] Intake — PDF fly-in + scanning laser
- [ ] Deliberation — 6 agent panes in a 3D semicircle
- [ ] Disagreement reel — quote-collision sequence
- [ ] Recommendation — handwriting reveal of the worker's letter
- [ ] Aggregate — R3F globe + corridor arcs

## Architecture sketch

```
src/
├── main.ts                  entry
├── style.css                design system (tokens + base + cold-open)
├── three/
│   ├── fluid-background.ts  full-bleed WebGL fluid noise
│   ├── agent-card.ts        3D pane primitive (next)
│   └── camera-rig.ts        scene-to-scene camera choreography (next)
├── scenes/
│   ├── cold-open.ts         ✓
│   ├── intake.ts            (next)
│   ├── deliberation.ts      (next)
│   ├── reel.ts              (next)
│   └── recommendation.ts    (next)
├── ui/
│   └── overlays.ts          HTML overlay components (next)
└── api/
    └── panel.ts             talks to FastAPI backend (next)
```

## Why vanilla, not Next.js

- One experience, no routing. No SEO target.
- React reconciliation fights animation loops.
- ~150KB lighter than Next.js + R3F equivalent.
- Static deploy works on Cloudflare Pages with `cf-deploy`.

## Performance budget

- Initial paint: < 100ms
- Time to interactive: < 500ms
- Frame budget during scenes: 16ms (60fps), gracefully degrades to 30fps
- Total JS: < 250KB gzipped
- Respects `prefers-reduced-motion: reduce` — full static fallback
