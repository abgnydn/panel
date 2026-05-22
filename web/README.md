# Panel — web/ (cinematic frontend)

The cinematic frontend for [Panel](../). Vanilla TypeScript + Three.js + GSAP — no framework runtime.

This is what's deployed on Databricks Apps (built into `../app/static/` and served by the FastAPI backend in `../app/`).

## Stack

| Layer | Choice |
|---|---|
| Build | Vite 8 |
| Language | TypeScript 5 (strict) |
| 3D / WebGL | Three.js — custom shaders |
| Animation | GSAP 3 |
| Typography | Inter + Instrument Serif + JetBrains Mono (Google Fonts) |
| State | Module-level signals (`src/state.ts`) |
| Backend | FastAPI-wrapped agents from `../app/` |
| Deploy | Static bundle → `../app/static/` → Databricks Apps |

## Run

```bash
cd web
npm install
npm run dev
```

Opens at http://127.0.0.1:5173. The dev server proxies API calls to a local FastAPI (run `uvicorn api.server:app --reload` from `../app/`).

## Build + deploy

From the repo root:

```bash
./scripts/build_and_deploy.sh
```

That runs `vite build` here, copies `dist/` into `../app/static/`, validates the Databricks Asset Bundle, deploys to the workspace, and restarts the app.

## Scenes

Full end-to-end flow, in router order:

```
src/scenes/
├── cold-open.ts        Fluid WebGL background + title reveal + magnetic CTA
├── intake.ts           Sample picker + PDF/paste, language + situation
├── deliberation.ts     Six agent panes — parallel "thinking" + verdict stamps
├── reel.ts             Disagreement-tension hero cards
├── rebuttals.ts        Round-2 agent push-back/extend cards
├── negotiation.ts      L1 + EN coaching script, six questions, red flags
├── recommendation.ts   Tagalog letter + 4-phase checklist + what-if simulator
├── genie.ts            NL→SQL multi-turn chat against the Databricks Genie Space
├── dashboard.ts        NGO aggregate heatmap + KPIs
└── router.ts           Scene-id state machine + crossfade transitions
```

## Performance budget

- Initial paint: < 100ms
- Time to interactive: < 500ms
- Frame budget during scenes: 16ms (60fps), gracefully degrades
- Bundle: ~430KB gzipped (three + html2canvas + jspdf dominate)
- Respects `prefers-reduced-motion: reduce` — static fallback

## Why vanilla, not Next.js

- One experience, no routing. No SEO target.
- React reconciliation fights animation loops.
- ~150KB lighter than Next.js + R3F equivalent.
- Static deploy is one `cp -r dist/. ../app/static/`.
