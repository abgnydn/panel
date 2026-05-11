# Panel

A multi-agent rights advisor for APJ migrant workers, built for the Databricks "Building Intelligent Apps" Hackathon (APJ, May 2026).

> A panel of AI specialists reads your contract — in your language — and tells you what's wrong with it.

## What it does

A migrant worker uploads their employment contract (photo, any APJ language) and describes their situation. Five specialist agents review in parallel, **visibly disagree** where their views diverge, and converge on actionable guidance.

- **Lawyer** — maps clauses to destination-country labor law
- **Translator** — renders the contract + advice in the worker's mother tongue
- **Regulator** — compares against ASEAN / ILO standard contracts
- **Peer Advocate** — surfaces similar past cases from the archive
- **Triage** — detects trafficking signals; routes to embassy / NGO

The **disagreement is the product** — single-agent analyzers are commodity; an exposed panel debate is not.

## Architecture

```
[Worker — mobile, any APJ language]
            │
            ▼
   Databricks Apps (Streamlit)        ← upload + 5-pane view
            │
            ▼
   Agent Bricks panel of 5            ← parallel run + debate + synth
       │      │      │      │
       ▼      ▼      ▼      ▼
   Genie  Mosaic AI  Lakebase  AI/BI Dashboard
   (NL→SQL on labor codes)  (case archive + session memory)  (NGO heatmap)
```

## Repo layout

| Path | Purpose |
|---|---|
| `databricks.yml` | Databricks Asset Bundle config — deploys app + jobs |
| `app/` | Streamlit UI deployed via Databricks Apps |
| `agents/` | 5 specialist personas + the moderator orchestrator (one `.md` each) |
| `lakebase/` | Postgres schema for the case archive + session memory |
| `data/` | Ingestion scripts for ILO / ASEAN / labor-code corpora |
| `docs/` | Submission spec, demo script, architecture diagrams |

## Demo corridors (scoped)

- Tagalog → Saudi Arabia (primary, hero case)
- Bahasa Indonesia → Malaysia (secondary, for breadth)

## Run locally

```bash
cd ~/panel
uv pip install --python .venv/bin/python -r app/requirements.txt
.venv/bin/streamlit run app/app.py
```

Open http://localhost:8501 (or whatever port Streamlit picks).

## LLM provider — three modes

| Mode | When | What you do |
|---|---|---|
| `claude_cli` (default) | `claude` CLI installed | Nothing — uses your existing Claude Code auth |
| `anthropic` | You have an API key | `export ANTHROPIC_API_KEY=sk-ant-...` |
| `mock` | No CLI, no key | Demo-quality canned responses |

Force one: `PANEL_LLM_PROVIDER=anthropic streamlit run ...`

**Image OCR requires the `anthropic` SDK** (Claude vision). The `claude_cli` path
handles text/PDF only. If you upload an image without an API key set, OCR falls
back to mock. For full live behaviour with image upload, set `ANTHROPIC_API_KEY`.

## Deploy to Databricks

```bash
databricks bundle deploy --target dev
databricks bundle run panel-app
```

## Status

- **2026-05-11** — project initiated, plan locked, build started
- **2026-05-14** — credits + workspace deadline
- **2026-05-19** — end-to-end smoke test gate
- **2026-05-22** — submission deadline

## Legal

Panel provides **informational guidance only**. It is not legal advice. Urgent cases are routed to a human legal-aid contact via the Triage agent.
