# Panel — Submission Spec

## Project

- **Name:** Panel
- **Team name:** _TBD_
- **Country of submission:** Singapore
- **Language track:** English
- **Track:** Track 1 — Social Impact (Open Data)

## Use case

A multi-agent rights advisor for APJ migrant workers. A worker uploads their employment contract (photo, any APJ language) and describes their situation; five Agent Bricks specialists review in parallel, visibly disagree where their views diverge, and synthesize a recommendation in the worker's mother tongue.

Ten million Filipinos abroad. Seven hundred thousand Indonesians leaving per year. Most have never read their contract in their own language. Panel exists to close that gap before they sign.

## Architecture

```
[Worker — mobile, any APJ language]
            │
            ▼
   Databricks Apps (Streamlit)        ← upload + 5-pane view + disagreement reel
            │
            ▼
   Agent Bricks panel of 5            ← Lawyer / Translator / Regulator / Peer Advocate / Triage
   + Moderator orchestrator             parallel run + debate detection + synthesis
       │      │      │      │
       ▼      ▼      ▼      ▼
   Genie  Mosaic AI  Lakebase  AI/BI Dashboards
   NL→SQL  LLM       Postgres  NGO heatmap
   on UC   inference OLTP for  + urgent
   labor   for       case      sessions
   codes   agents    archive   view
                     + sessions
```

## Databricks technologies used

| Pillar | Where it's load-bearing |
|---|---|
| **Databricks Apps** | The Streamlit front-end — worker-facing UI + the disagreement reel component. Deployed via Databricks Asset Bundle. |
| **Agent Bricks** | All 5 specialist personas + the moderator orchestrator. Each agent has its own tool set + eval harness. |
| **Lakebase** | Postgres-compatible OLTP — `workers`, `sessions`, `agent_messages`, `case_archive`, `recommendations`, `embassy_directory`, `ngo_directory`. Powers session memory + Peer Advocate vector search. |
| **Genie** | Natural-language queries over `labor_codes`, `ilo_conventions`, `asean_standard_contract` Delta tables. Used by Lawyer + Regulator agents. |
| **Mosaic AI Model Serving** | LLM inference for all agents. SEA-LION / Sailor models for Tagalog + Bahasa; Claude / GPT-class for English reasoning. |
| **AI/BI Dashboards** | Aggregate "abuse-pattern heatmap" — judges' data-storytelling segment of the demo. |
| **Unity Catalog** | Catalog: `panel_dev`. Schema: `main`. All tables governed under one ACL. |

## Datasets

All public / open-license.

| Dataset | Purpose | License |
|---|---|---|
| ILO labor migration papers (corpus) | Case-archive seed | Public |
| ASEAN Rights-Based Standard Employment Contract | Regulator baseline | Public |
| Philippine RA 11641 + DFA POLO directory | Origin-country reference + embassy contacts | Public |
| Indonesia UU 18/2017 + BP2MI data | Origin-country reference | Public |
| Saudi Arabia Labor Law (Royal Decree M/51 + 2017 amendments) | Destination-country reference | Public |
| Malaysia Employment Act 1955 (2022 consolidated) | Destination-country reference | Public |
| ILO Conventions C97 / C143 / C181 / C189 / C190 | Regulator's international-standards corpus | Public |

Full source list with URLs: see `data/sources.md`.

## Demo corridor scope

- **Primary:** Tagalog → Saudi Arabia (PH → SA)
- **Secondary:** Bahasa Indonesia → Malaysia (ID → MY)

Two corridors only — we don't overpromise 10 languages. SEA-LION / Sailor coverage for both is sufficient for production-quality output.

## Why we win the rubric

| Criterion | Weight | Our edge |
|---|---|---|
| Business Applicability | 20% | 10M+ user base. Real partnership path with ILO + ASEAN labor ministries. Life-altering stakes. |
| Creativity & Innovation | 20% | Visible multi-agent disagreement. No deployed AI rights advisor for APJ migrant workers exists as of May 2026. |
| User Experience | 20% | Mobile-first. Mother-tongue voice + text. Photo upload. Disclaimer everywhere. |
| Technical Capability | 20% | All 4 Databricks pillars (Apps + Genie + Lakebase + Agent Bricks) load-bearing. Bundle-deployable. |
| Data Storytelling | 20% | Disagreement reel + aggregate abuse-pattern heatmap. Two narrative arcs in 5 minutes. |

## Legal posture

Panel provides **informational guidance only.** It is not legal advice. Every output — every agent's findings, every recommendation, every translation — is rendered alongside a disclaimer in the worker's L1. The Triage agent always surfaces at least one **non-employer** contact (embassy, NGO, hotline) for urgent cases.

Worker consent is **opt-in** for any contribution to the case archive. The default is private-session.

## Team

- _Name 1_ — Singapore — Owner — Agent Bricks personas + Lakebase + Genie
- _Name 2_ — Singapore — Co-founder — Streamlit UI + demo video + spec

## Code

- Repo: _link TBD_
- Deploy: `databricks bundle deploy --target dev`
- Live URL: _TBD after deploy_

## Risks acknowledged

1. **Legal liability** — disclaimers on every output, urgent cases routed to humans.
2. **Translation quality** — scope limited to two corridors where model coverage is solid.
3. **Politically sensitive in destination countries** — framing is "empowering workers," not "exposing employers."
4. **Liability if wrong** — Triage agent always defers to a human legal-aid contact for urgent cases.
