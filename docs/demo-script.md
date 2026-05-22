# Panel — 5-Minute Demo Script

**Total runtime target:** 5:00. Real ceiling: 5:30. Each scene block lists **VO** (voiceover, what you say), **SHOW** (what's on screen), and **TIMING**.

Recommended setup:
- 1920×1080 capture. Browser zoom 100%. No extensions toolbar visible.
- Hide bookmarks bar. Plain `chrome://newtab` between scenes if needed.
- Voiceover recorded in one take after the video is edited — easier than syncing live.

**Submission alignment.** The hackathon form requires: (1) team + problem intro, (2) architecture walkthrough, (3) working demo showing the Databricks product stack. This script hits each in order: 0:00–0:20 (team + hook), 0:20–0:45 (architecture), 0:45–4:50 (working demo).

---

## 0:00 — 0:20 · COLD OPEN + TEAM

**SHOW:**
- Three.js fluid cold-open scene playing.
- Title fades in over the simulation: *"A panel of AI specialists that reads your contract, in your language, and tells you what's wrong with it."*

**VO:**
> I'm Baris Gunaydin. With my co-founder Anne Lazarakis, building out of Marketing Delphi in Singapore.
>
> Every year, ten million Filipinos work abroad. Seven hundred thousand Indonesians leave the country for work. Most of them sign their employment contract — in English or Arabic — without ever reading it in their own language.
>
> Panel is what they read it with.

**TIMING:** 20 seconds. Let the simulation breathe for 2 seconds before VO. Punch "Panel is what they read it with" on the last frame.

---

## 0:20 — 0:45 · ARCHITECTURE

**SHOW:**
- Cut to a single static slide of the architecture diagram (the mermaid block from `docs/spec.md`, rendered as a clean PNG).
- Highlight, in sequence as VO names each: **Databricks Apps**, **Mosaic AI Model Serving**, **Lakebase**, **Genie Space**, **Unity Catalog**.

**VO:**
> Panel ships as a single Databricks Asset Bundle. One command provisions everything.
>
> The frontend and FastAPI moderator run inside Databricks Apps. Six specialist agents call Mosaic AI Model Serving — qwen3-next-80b and llama-3-3-70b. Lakebase Postgres holds sessions, recommendations, and the case archive the Peer Advocate reads from. A Genie Space sits on top of Unity Catalog — labor codes, ILO standards, the case archive, an embassy directory — for multi-turn natural-language SQL.
>
> All four Databricks pillars. All load-bearing.

**TIMING:** 25 seconds. Crossfade out of the diagram on the last word.

---

## 0:45 — 1:10 · MEET MARIA

**SHOW:**
- Click into intake scene.
- Scroll the sample list. Hover the hero card: *"Philippines → Saudi Arabia · Maria, 23, domestic worker (HERO)"*. Click it.
- Sample text auto-fills. Sidebar shows: *"3-yr live-in, SAR 750/mo probation, SAR 15K recruitment debt + SAR 5K performance bond, passport surrendered on arrival, explicit ban on contacting the embassy."*
- Language selector: Tagalog. Situation box: *"I'm flying to Riyadh in two weeks. The recruiter wants me to sign tomorrow."*

**VO:**
> Maria is twenty-three. She's flying to Riyadh in two weeks to work as a domestic helper. The contract is in English. She speaks Tagalog. She paid four thousand US dollars to get this placement — money her family borrowed.
>
> The recruiter wants her to sign tomorrow. She has one question: *should I sign?*

**TIMING:** 25 seconds. End with cursor hovering over the green "Convene the panel" button.

---

## 1:10 — 2:05 · DELIBERATION

**SHOW:**
- Click "Convene the panel."
- Six agent panes light up. Each shows its avatar + tagline, then status "thinking…", then a latency stamp + verdict summary as each completes.
- They DO NOT finish in order — Triage and Translator come back fast (~5–6 s), Lawyer and Regulator slower (~10–12 s). The stagger gives the scene its drama.

**VO (over the run):**
> Six specialists, in parallel, against Mosaic AI Model Serving.
>
> The Lawyer maps every clause to Saudi labor law. The Translator renders the contract in Maria's Tagalog. The Regulator scores it against ILO Conventions 97, 143, 181, 189, 190 and the ASEAN standard. The Peer Advocate pattern-matches against the case archive in Lakebase. The Triage agent looks for ILO trafficking indicators. The Negotiator — added by my co-founder Anne — coaches Maria for the conversation she's about to have.
>
> Twelve seconds. Six specialist verdicts.

**TIMING:** 55 seconds. Wait for all six to complete before continuing. The Continue button will pulse.

---

## 2:05 — 2:40 · THE REEL

**SHOW:**
- Click Continue → Reel scene.
- Hero card animates in: **#1 · CRITICAL · severity 10 · Embassy Gag Clause**. Tension rows show Triage, Lawyer, Regulator, Peer Advocate all flagging Clause 10.
- Scroll. **#2 · Passport + Phone Surrender**. **#3 · Substitution Clause**.

**VO:**
> The verdict isn't a single answer. The panel disagrees.
>
> The strongest tension is on Clause 10 — the contract literally prohibits Maria from contacting the embassy without the recruiter's written consent. The Lawyer calls it unenforceable. The Regulator calls it a violation of ILO Convention 189. The Peer Advocate has seen this exact clause silence two workers in the archive who tried to call for help.
>
> That's the product. Not a verdict. A debate.

**TIMING:** 35 seconds.

---

## 2:40 — 3:00 · REBUTTALS

**SHOW:**
- Click into rebuttals scene.
- Six rebuttal cards animate in. Highlight the Lawyer's pushback on the Regulator's reading of the recruitment fee, and the Peer Advocate extending the Triage agent on the isolation triad.

**VO:**
> Round two. Each agent sees the others' findings and can push back, extend, or agree. Lawyer pushes back on Regulator. Peer Advocate extends Triage. The disagreement isn't smoothed — it's surfaced.

**TIMING:** 20 seconds.

---

## 3:00 — 3:35 · NEGOTIATION COACH

**SHOW:**
- Click Continue → Negotiation scene.
- Priority pushback card: **Clause 10 · what to say in L1**, Tagalog phrase with English translation below.
- Scroll the six questions. Highlight Q1 (embassy-contact) and Q4 (passport return).
- Scroll to red flags: *"If the recruiter says 'The passport is just at the office for visa purposes' — that means they're lying. Your move: …"*

**VO:**
> Telling Maria her contract is bad doesn't help her. The Negotiator gives her the script.
>
> Priority pushback in Tagalog with the English fallback. Six questions to ask the recruiter, ranked by clause severity. Red flags to listen for. A walk-away threshold.
>
> No other contract analyzer outputs a script. This is the thing that actually changes what happens at the recruiter's office tomorrow morning.

**TIMING:** 35 seconds.

---

## 3:35 — 4:10 · RECOMMENDATION

**SHOW:**
- Click Continue → Recommendation scene.
- Urgency gauge animates to **10/10 · Critical — act before signing**.
- Scroll the letter (Tagalog).
- 4-phase checklist tabs: tap "Before departure" — 6 items. Tap "Exit / emergency" — 5 items.
- "Do NOT agree to" (six refusals) → "Ask the recruiter to change before signing" (five suggested rewrites).
- What-if simulator: tick three pushbacks, click "Simulate amendments". Urgency drops 10 → 4. Bar animates.

**VO:**
> A letter, in Tagalog. Urgency ten out of ten. A four-phase checklist she can save offline. The clauses to refuse outright. The clauses to ask the recruiter to amend — with the exact replacement language.
>
> And a what-if simulator — if the recruiter agrees to remove the embassy gag, return the passport, and drop the performance bond, urgency drops from ten to four. She sees, *before she signs*, what each amendment is worth.

**TIMING:** 35 seconds.

---

## 4:10 — 4:40 · GENIE CHAT — THE SYSTEMIC VIEW

**SHOW:**
- Scroll to "Take it with you" footer. Click **Ask the lawbook · Genie chat**.
- Genie chat scene loads with three seed questions as chips.
- Click: *"How many cases in the archive ended with the worker returning early?"*
- Genie thinks (~12–15 s). Answer appears: *"There are 9 cases in the archive where the worker returned early."* SQL details expand below.
- Click the AI-suggested follow-up chip: *"Show all 24-hour embassy hotlines for Philippine workers."*
- Genie returns a table.

**VO:**
> One more layer. Maria asks the data directly.
>
> Genie Space — multi-turn natural-language SQL over our Unity Catalog corpus: labor codes, ILO standards, case archive, embassy directory. Nine cases in the archive ended with the worker returning early. Genie ran the SQL, translated the answer back, and suggested the next question.
>
> Same workspace. Same catalog. Same conversation.

**TIMING:** 30 seconds.

---

## 4:40 — 5:00 · NGO DASHBOARD + CLOSE

**SHOW:**
- Click Continue → NGO Dashboard scene.
- Aggregate heatmap renders: corridors × abuse-pattern counts. KPIs at top: total cases triaged, % critical, top abuse pattern, top corridor.
- Hold 5–6 seconds — let the eye track across the heatmap.
- Fade to title card: **Panel · marketingdelphi.com · Built on Databricks Apps · Mosaic AI · Lakebase · Genie · Unity Catalog**

**VO:**
> Per worker, before they sign. Per corridor, across thousands of workers — for the NGOs that act on the aggregate.
>
> Databricks Apps, Mosaic AI Model Serving, Lakebase, Genie, Unity Catalog. All load-bearing. All shipped.
>
> Panel.

**TIMING:** 20 seconds. Cut on "Panel."

---

## Recording notes

- **One take per scene.** Don't try to do all five minutes live — capture each scene's screen recording separately and stitch.
- **Click confidence.** Hover over buttons for a beat before clicking — gives the viewer time to read the label.
- **The deliberation scene is the most important.** Make sure all six agents complete cleanly before you cut. If the deliberation stalls, retry until it's clean. This is the moat shot.
- **The architecture slide is the second-most important.** Judges grading on Databricks integration coverage want to *see* the stack named. Render the mermaid in `docs/spec.md` to a PNG at 1920×1080 ahead of time.
- **Tagalog rendering.** Make sure the Recommendation letter is visibly in Tagalog when you scroll it. Frame the English subtitle line clearly too — judges should see *both*.
- **Voiceover last.** Edit the silent video first to nail timing, then record the voiceover against the edit. Free yourself from sync stress.
- **Product names matter.** Say "Mosaic AI Model Serving," "Lakebase," "Genie Space," "Unity Catalog," "Databricks Apps" — not just "Databricks." Judges score on stack coverage.

---

## Backup talking points (if a scene undershoots)

- *"The provider is swappable — same code runs against Anthropic, OpenAI, Gemini, or a local LM Studio. We default to Mosaic AI in production."*
- *"The contract Maria is reading is built from real recruitment-office contracts surfaced by Migrante and HRW reports. Names redacted, structure intact."*
- *"All four datasets — labor codes, ILO standards, case archive, embassy directory — are in Unity Catalog. Genie reads them through one ACL."*
- *"The whole product ships as a single Databricks Asset Bundle. One command — `databricks bundle deploy` — provisions the Lakebase instance, the SQL warehouse, the serving endpoints, the Genie space, and the app."*

---

## Pre-flight checklist before you hit record

- [ ] App is up at https://panel-7474659131504222.aws.databricksapps.com — click through cold-open → deliberation → recommendation once. No errors.
- [ ] Architecture diagram exported to PNG at 1920×1080 (use `docs/spec.md` mermaid as source).
- [ ] Browser at 100% zoom, no extension toolbar, bookmarks hidden.
- [ ] Audio: mic input picked, room quiet, no fan.
- [ ] Recording tool ready: OBS / ScreenStudio / QuickTime — 1920×1080 @ 30fps minimum.
- [ ] One test deliberation run end-to-end to confirm latencies are clean before the real take.
