# Panel — Project Spec

**Databricks "Building Intelligent Apps" Hackathon, APJ — Track 1 (Social Impact)**

---

## Project

| | |
|---|---|
| **Name** | Panel |
| **Tagline** | A panel of AI specialists that reads your contract, in your language, and tells you what's wrong with it. |
| **Team** | Marketing Delphi (Singapore) |
| **Members** | Baris Günaydin (owner), Anne Günaydin (co-founder) |
| **Country of submission** | Singapore |
| **Track** | Track 1 — Social Impact, open data |
| **Live URL** | https://panel-7474659131504222.aws.databricksapps.com |
| **Repo** | _link inserted at submission time_ |

---

## Problem

Ten million Filipinos work abroad. Seven hundred thousand Indonesians leave each year. Most sign their employment contract — in English or Arabic, drafted by the destination employer — without ever reading it in their own language. Recruitment fees, passport confiscation, unlimited working hours, and one-sided termination clauses are buried in the same legalese as the wage and rest-day provisions, and a worker in a recruitment office has no realistic way to spot which lines are statutorily unlawful, which are below the international floor, and which have empirically broken returnees before.

Once they fly, the asymmetry hardens: kafala-tier visa systems tie their status to the employer; embassy hotlines are unfamiliar; their phone, passport, and movement may not be theirs.

**The intervention has to happen before signing.** That is the slot Panel is built for.

---

## Solution

A worker uploads their employment contract — photo, PDF, or paste — selects their mother tongue, and describes their situation in one sentence. Six specialist AI agents read the contract **in parallel** and then **publicly disagree** before synthesizing a single recommendation in the worker's L1.

### The agents

| Agent | Role |
|---|---|
| **Lawyer** | Maps each clause to the destination-country labor code. Verdict per clause: lawful / gray-area / unlawful, with statute citation. |
| **Translator** | Renders both the contract and the panel's findings in the worker's mother tongue. Flags semantic ambiguities in the translation itself. |
| **Regulator** | Scores the contract against ILO C97/C143/C181/C189/C190 and the ASEAN Rights-Based Standard Employment Contract. Verdict per core area: meets / below standard / prohibited. |
| **Peer Advocate** | Pattern-matches each clause against a Lakebase archive of past cases. Surfaces outcome distributions for similar contracts ("3 cases with this rest-day phrasing, 2 ended badly"). |
| **Triage** | Detects ILO trafficking indicators. Produces an urgency score and routes urgent cases to embassy/NGO contacts. |
| **Negotiator** | Coaches the worker for the pre-signing conversation: priority pushback, six questions to ask (in L1 + EN), red-flag recruiter responses, walk-away threshold. |

### The disagreement is the product

After Round 1, the moderator runs **disagreement detection** across all six outputs and assembles a "tension reel" — the three clauses where the agents diverge most strongly, ranked by severity and convergence. Each agent then gets a **Round 2 rebuttal turn** where they see the others' outputs and can extend, agree, or push back.

The output isn't a single verdict. It's a structured debate. Workers see the *Lawyer says X / Regulator says Y / Peer Advocate has seen Z happen* tensions explicitly — because a single-agent "this contract is fine" or "this contract is awful" is a commodity output. A panel that visibly contests its own conclusions is what makes the recommendation trustworthy.

### What the worker walks away with

1. **A letter in their mother tongue** — TL;DR + urgency score 0–10.
2. **A negotiation script** — what to say, in L1 and EN, for the priority clause.
3. **A four-phase checklist** — before departure / on arrival / during employment / exit-emergency, each item priority-tagged.
4. **Concrete refusals + pushbacks** — clauses to refuse outright, clauses to ask the recruiter to amend, with suggested replacement language.
5. **A what-if simulator** — toggle which amendments the recruiter accepts; see how the urgency score drops.
6. **Offline-takeable artifacts** — Markdown / PDF download, WhatsApp share, QR code that encodes the embassy contact as a vCard for one-tap save.
7. **The systemic view** — an NGO-facing aggregate dashboard, plus a multi-turn Genie chat for follow-up questions over the open-data corpus.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│              Worker (mobile-first, any APJ language)                 │
└──────────────────────────────────────────────────────────────────────┘
                                    │
                  ▼ HTTPS, same-origin (Databricks Apps)
┌──────────────────────────────────────────────────────────────────────┐
│   Frontend  ·  Vanilla TypeScript + Vite + Three.js + GSAP           │
│   8 cinematic scenes — intake, deliberation, reel, rebuttals,        │
│   negotiation, recommendation, dashboard, genie-chat                 │
└──────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│   Backend  ·  FastAPI on Databricks Apps (uvicorn)                   │
│                                                                       │
│   POST /api/panel/run     → moderator orchestrator (6 agents //)     │
│   POST /api/genie/query   → multi-turn Genie chat + AI follow-ups    │
│   GET  /api/genie/seed-questions                                     │
│   GET  /api/samples                                                  │
│   GET  /api/health                                                   │
└──────────────────────────────────────────────────────────────────────┘
        │                  │                    │                │
        ▼                  ▼                    ▼                ▼
┌───────────────┐  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐
│  Mosaic AI    │  │   Lakebase     │  │     Genie      │  │ Unity Catalog│
│  Foundation   │  │  Postgres 16   │  │  Space (NL→SQL)│  │  panel.main  │
│   Models      │  │     OLTP       │  │                │  │              │
│               │  │                │  │  labor_codes   │  │  Delta tables│
│ qwen3-next-80b│  │  workers       │  │  ilo_standards │  │  governed    │
│ llama-3-3-70b │  │  sessions      │  │  case_archive  │  │  under one   │
│               │  │  agent_msgs    │  │  embassy_dir   │  │  ACL         │
│               │  │  recommends    │  │                │  │              │
└───────────────┘  └────────────────┘  └────────────────┘  └──────────────┘
```

### Single-deploy on Databricks Apps

The FastAPI server and the static Vite-built frontend ship together in a single Databricks Asset Bundle. Deploy command:

```bash
databricks bundle deploy --target dev
```

The bundle config (`databricks.yml`) provisions five resources: the app itself, the Lakebase instance, a SQL warehouse, two serving-endpoint references (qwen3-next-80b for fast agents, llama-3-3-70b for legal reasoning), and the Genie space.

---

## Databricks pillars — how each is load-bearing

| Pillar | Where it's used | What breaks if removed |
|---|---|---|
| **Databricks Apps** | The whole product. FastAPI + static frontend deployed as one app. Authenticated via the workspace OAuth flow. | The user has no way to reach the system. |
| **Mosaic AI Model Serving** | All six agents + the rebuttal turn + the follow-up-question generator for Genie chat. Provider abstraction supports Mosaic / Anthropic / OpenAI / Gemini / LM Studio / Claude CLI / mock, but **mosaic is the production provider on the deployed app**. | No agent outputs. The product is empty. |
| **Lakebase (Postgres 16)** | Session persistence, worker records, per-agent message log, final recommendations. Powers the NGO-aggregate dashboard. Future: vector search for the Peer Advocate. | No memory across the conversation; no NGO dashboard; no audit trail. |
| **Genie** | The "Ask the lawbook" scene — multi-turn natural-language queries over `labor_codes`, `ilo_standards`, `case_archive`, `embassy_directory`. Each Genie response is paired with three AI-generated follow-up suggestions from a Mosaic AI Qwen 80B call. | The systemic-view scene goes silent. The worker can still get the per-contract recommendation but loses the ability to ask "is this normal for my corridor?" |
| **Unity Catalog** | All four Genie-backed tables governed under `panel.main`. App service principal granted `USE_CATALOG` + `USE_SCHEMA` + `SELECT` per-table. | No data access for Genie; the chat returns a permissions error. |

---

## Datasets

All public / open-license. Loaded as Delta tables under `panel.main` in Unity Catalog.

| Table | Source | Purpose |
|---|---|---|
| `labor_codes` | KSA Royal Decree M/51 + 2017 amendments, Malaysia Employment Act 1955 (2022 consolidated), Philippine Labor Code, Indonesia UU 18/2017, UAE Federal Decree-Law 33/2021, HK / SG domestic-worker regs | Lawyer's destination-country reference |
| `ilo_standards` | ILO Conventions C97 / C143 / C181 / C189 / C190 + ASEAN Rights-Based Standard Employment Contract | Regulator's international-floor reference |
| `case_archive` | Anonymised returnee-case patterns synthesised from ILO casework corpus | Peer Advocate's pattern-matching base |
| `embassy_directory` | PH DFA POLO directory, BP2MI Indonesia, plus NGO contacts (Migrante, HOME, etc.) | Triage's contact-routing pool |

Full source list with URLs: `data/sources.md`.

---

## Demo corridor scope

| Direction | Worker L1 | Status |
|---|---|---|
| Philippines → Saudi Arabia | Tagalog | **Primary demo** (hero sample: domestic worker, passport retention + recruitment fee debt) |
| Indonesia → Malaysia | Bahasa Indonesia | Secondary |
| Philippines → Hong Kong | Tagalog | Sample loaded |
| Indonesia → Singapore | Bahasa | Sample loaded |
| Philippines → UAE | Tagalog | Sample loaded |
| (Plus three contrived cases) | EN | Clean / Mild / Trafficking — for the "what does it look like across the severity spectrum" demo segment |

Two corridors only for the live judge demo. We don't overpromise broad language coverage we haven't validated.

---

## Demo flow (5 minutes)

| Time | Scene | What the judge sees |
|---|---|---|
| 0:00 | **Cold-open** | Three.js fluid simulation + the tagline. Sets the tone — this is a cinematic product, not a Streamlit dashboard. |
| 0:20 | **Intake** | Worker selects sample contract (hero case: PH→SA, Tagalog), language picker, situation sentence. |
| 0:50 | **Deliberation** | Six agent panes light up in parallel, latency-stamped, verdicts arriving as they complete. ~12 s end-to-end. |
| 1:50 | **The reel** | The three biggest disagreements, ranked, with severity tints and per-agent tension rows. The moat. |
| 2:30 | **Rebuttals** | Round 2 — agents extend or push back on each other's findings. |
| 3:00 | **Negotiation coach** | Six questions to ask (L1 + EN), the priority pushback, red-flag recruiter responses. |
| 3:40 | **Recommendation** | A letter to the worker. Urgency gauge, 4-phase checklist, refusals, pushbacks, what-if simulator. |
| 4:20 | **Genie chat** | "How many cases in the archive ended with the worker returning early?" → SQL + 9 rows + AI-suggested follow-up. The systemic view. |
| 4:50 | **NGO Dashboard** | The aggregate heatmap. Closes on data storytelling. |

---

## Rubric-by-rubric

| Criterion | Weight | Our edge |
|---|---|---|
| **Business Applicability** | 20% | 10M+ Filipinos abroad, 700K+ Indonesians/year leaving. Real partnership path with ILO + ASEAN labor ministries + Migrante / HOME networks. Pre-signing intervention is the highest-leverage moment. |
| **Creativity & Innovation** | 20% | Visible multi-agent disagreement + rebuttal turn. Negotiation coach (Anne's contribution) is the genuinely novel piece — every other contract analyzer outputs a verdict; Panel outputs a *script*. No deployed AI rights advisor for APJ migrant workers exists as of May 2026. |
| **User Experience** | 20% | Mobile-first responsive design with horizontal-scroll tabs, 48 px tap targets, no hover effects on touch. Mother-tongue rendering throughout. Photo-upload friendly. Disclaimer in worker's L1 on every artifact. |
| **Technical Capability** | 20% | All four Databricks pillars load-bearing. Single-bundle deploy. Sensible failure surfaces — Genie errors are translated to plain-language reasons, agent failures show per-pane error states without taking down the rest of the panel. |
| **Data Storytelling** | 20% | Three narrative arcs in five minutes: the worker's recommendation, the systemic Genie-chat exploration, and the NGO heatmap. Each leans on a different Databricks data primitive. |

---

## Legal posture

Panel provides **informational guidance only.** It is not legal advice.

- Every output — every agent's findings, every recommendation, every translation — is rendered alongside a disclaimer in the worker's L1.
- The Triage agent always surfaces at least one **non-employer** contact (embassy 24-hour hotline, NGO, in-country legal aid) for urgent cases.
- Worker consent is **opt-in** for any contribution to the case archive. The default is private-session — the response is stored under a per-session UUID, not under the worker's name.
- No personally identifying details (name, passport number, exact addresses) are sent to the LLM providers. The contract text is sent verbatim because that's what the agents read; sample contracts in the demo are anonymised.

---

## Risks acknowledged

1. **Legal liability.** Disclaimers on every output. Urgent cases routed to humans. Framing is consistently "this is what the panel found — verify with a lawyer / embassy / NGO before acting."
2. **Translation quality.** Demo scope is limited to two corridors where SEA-LION / Sailor / Llama 3.3 Tagalog and Bahasa output is solid. We don't overpromise coverage we haven't validated.
3. **Politically sensitive in destination countries.** Framing is empowering workers, not exposing employers. The product is positioned as a "second opinion before signing," not as an enforcement tool.
4. **LLM hallucination.** Six agents + a rebuttal round are a hedge — if one agent fabricates a clause or a citation, the others either contradict it (which shows up in the reel) or fail to corroborate it. Genie's SQL grounding gives the systemic-view scene a verifiable data path.
5. **Single point of failure: Mosaic endpoints.** The provider abstraction allows a hot-swap to Anthropic / OpenAI / Gemini / LM Studio without code changes — only an env var.

---

## Stack

### Backend

- **FastAPI** + **uvicorn** on Databricks Apps
- **Python 3.11**
- **databricks-sdk** ≥ 0.108 — Genie + Lakebase + Mosaic AI clients
- **psycopg** 3 — Lakebase Postgres driver
- Six agent modules + moderator + checklist + rebuttal orchestrator
- Provider abstraction: Mosaic / Anthropic / OpenAI / Gemini / LM Studio / Claude CLI / mock

### Frontend

- **Vanilla TypeScript** (no framework) + **Vite 8** + **Three.js** + **GSAP**
- Eight cinematic scenes wired through a tiny scene router
- Offline export pipeline: Markdown / PDF (jsPDF) / WhatsApp share / QR code (vCard-encoded embassy contact)
- Mobile-first responsive — phone, tablet, desktop breakpoints

### Infrastructure

- **Databricks Asset Bundle** — `databricks.yml` provisions Lakebase, SQL warehouse, two serving-endpoint references, Genie space, app
- **Unity Catalog** — `panel.main` schema, four Delta tables
- **Single-command deploy** — `./scripts/build_and_deploy.sh` runs the Vite build, copies the static dist into the app's `static/` directory, validates the bundle, deploys, and restarts the app

---

## What's submitted

| Artifact | Location |
|---|---|
| Live deployed app | https://panel-7474659131504222.aws.databricksapps.com |
| 5-minute demo video | _link inserted at submission_ |
| This spec | `docs/spec.md` in the repo |
| Source code | _repo link inserted at submission_ |
| Datasets manifest | `data/sources.md` |

---

## Conversations to preserve

- The Negotiator was added late, on Anne's observation that "telling someone their contract is bad is useless unless you also tell them what to say." It's the single most differentiating piece of the panel — every other agent produces a verdict; the Negotiator produces a script.
- The product was originally a Streamlit dashboard. The current vanilla-TS / Three.js / GSAP cinematic frontend is a complete rewrite — the Streamlit version remains in the repo as the local-dev fallback at `app/streamlit_app.py`, but the deployed surface is the cinematic v2.
- All six agents producing in parallel through a `ThreadPoolExecutor` (latency ~12 s end-to-end) is a deliberate UX choice — judges and workers should see the panel composing itself, not stare at a single loading spinner.
