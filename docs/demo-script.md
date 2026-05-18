# Panel — 5-Minute Demo Script

**Total runtime target:** 5:00. Real ceiling: 5:30. Each scene block lists **VO** (voiceover, what you say), **SHOW** (what's on screen), and **TIMING**.

Recommended setup:
- 1920×1080 capture. Browser zoom 100%. No extensions toolbar visible.
- Hide bookmarks bar. Plain `chrome://newtab` between scenes if needed.
- Voiceover recorded in one take after the video is edited — easier than syncing live.

---

## 0:00 — 0:25 · COLD OPEN

**SHOW:**
- Three.js fluid cold-open scene playing.
- The tagline fades in over the simulation: *"A panel of AI specialists that reads your contract, in your language, and tells you what's wrong with it."*

**VO:**
> Every year, ten million Filipinos work abroad. Seven hundred thousand Indonesians leave the country for work.
>
> Most of them sign their employment contract — in English or Arabic — without ever reading it in their own language.
>
> Panel is what they read it with.

**TIMING:** 25 seconds. Let the simulation breathe for 2-3 seconds before VO starts.

---

## 0:25 — 0:55 · MEET MARIA

**SHOW:**
- Click into intake scene.
- Scroll the sample list. Hover the hero card: *"Philippines → Saudi Arabia · Maria, 23, domestic worker (HERO)"*. Click it.
- The sample text auto-fills. The description sidebar shows: *"3-yr live-in, SAR 750/mo probation, SAR 15K recruitment debt + SAR 5K performance bond, passport surrendered on arrival, explicit ban on contacting the embassy."*
- Language selector: Tagalog. Situation box: *"I'm flying to Riyadh in two weeks. The recruiter wants me to sign tomorrow."*

**VO:**
> Maria is twenty-three. She's flying to Riyadh in two weeks to work as a domestic helper. Her recruiter wants her to sign tomorrow.
>
> The contract is in front of her, in English. She speaks Tagalog. She paid fifteen thousand riyals — about four thousand US dollars — to get this placement, money her family borrowed.
>
> She has one question: *should I sign?*

**TIMING:** 30 seconds. End with cursor hovering over the green "Convene the panel" button.

---

## 0:55 — 1:55 · DELIBERATION

**SHOW:**
- Click "Convene the panel."
- Six agent panes light up. Each shows its avatar + tagline, then status "thinking…", then a latency stamp + verdict summary as each completes.
- They DO NOT finish in order — Triage and Translator come back fast (~5-6 s), Lawyer and Regulator slower (~10-12 s). Stagger gives the scene its drama.

**VO (over the 12-second run):**
> Six AI specialists read the contract in parallel.
>
> The Lawyer maps every clause to Saudi labor law.
> The Translator renders the contract in Maria's Tagalog.
> The Regulator scores it against the ILO conventions and the ASEAN standard contract.
> The Peer Advocate pattern-matches against an archive of past cases.
> The Triage agent looks for trafficking indicators.
> And the Negotiator — added by my co-founder Anne — coaches Maria for the conversation she's about to have.
>
> Twelve seconds. Six specialist verdicts.

**TIMING:** 60 seconds. Wait for all six to complete before continuing. The Continue button will pulse.

---

## 1:55 — 2:35 · THE REEL

**SHOW:**
- Click Continue → Reel scene.
- Hero card animates in: **#1 · CRITICAL · severity 10 · Embassy Gag Clause**. Tension rows show Triage, Lawyer, Regulator, Peer Advocate all flagging Clause 10.
- Scroll. **#2 · Passport + Phone Surrender**. **#3 · Substitution Clause**.

**VO:**
> But the verdict isn't a single answer. The panel disagrees.
>
> The strongest disagreement is on Clause 10. The contract literally prohibits Maria from contacting the embassy without the recruiter's written consent.
>
> The Lawyer calls it unenforceable. The Regulator calls it a violation of ILO Convention 189. The Peer Advocate has seen this exact clause used to silence two workers in the archive who tried to call for help.
>
> *That's* the product. Not a verdict. A debate.

**TIMING:** 40 seconds.

---

## 2:35 — 3:00 · REBUTTALS

**SHOW:**
- Click into rebuttals scene.
- Six rebuttal cards animate in. Highlight the Lawyer's pushback on the Regulator's reading of the recruitment fee, and the Peer Advocate extending the Triage agent on the isolation triad.

**VO:**
> Round two. Each agent sees the others' findings and can push back, extend, or agree. The Lawyer pushes back on the Regulator. The Peer Advocate extends the Triage agent. The disagreement isn't smoothed over — it's surfaced.

**TIMING:** 25 seconds.

---

## 3:00 — 3:40 · NEGOTIATION COACH

**SHOW:**
- Click Continue → Negotiation scene.
- Priority pushback card shows up first: **Clause 10 · what to say in L1**, with the Tagalog phrase and the English translation below.
- Scroll the six questions. Highlight Q1 (the embassy-contact question) and Q4 (the passport return question).
- Scroll to red flags: "If the recruiter says *'The passport is just at the office for visa purposes'* — that means they're lying. Your move: …"

**VO:**
> Telling Maria her contract is bad doesn't help her.
>
> The Negotiator gives her the script. The priority pushback in Tagalog with the English fallback. Six questions to ask the recruiter, ranked by clause severity, in her language and in English. Red flags to listen for. A walk-away threshold.
>
> No other contract analyzer outputs a script. This is the thing that actually changes what happens at the recruiter's office tomorrow morning.

**TIMING:** 40 seconds.

---

## 3:40 — 4:20 · RECOMMENDATION

**SHOW:**
- Click Continue → Recommendation scene.
- Urgency gauge animates to **10/10 · Critical — act before signing**.
- Scroll the letter (Tagalog).
- 4-phase checklist tabs: tap "Before departure" — 6 items. Tap "Exit / emergency" — 5 items.
- Scroll: "Do NOT agree to" (six refusals). "Ask the recruiter to change before signing" (five suggested rewrites).
- What-if simulator: tick three pushbacks, click "Simulate amendments". Urgency drops from 10 → 4. The bar animates.

**VO:**
> A letter, in Tagalog. Urgency ten out of ten. Critical — act before signing.
>
> A four-phase checklist she can save offline. The clauses to refuse outright. The clauses to ask the recruiter to amend, with the exact replacement language.
>
> And a what-if simulator — if the recruiter agrees to remove the embassy gag, return the passport, and drop the performance bond, her urgency score drops from ten to four. She can see, before she signs, exactly what each amendment is worth.

**TIMING:** 40 seconds.

---

## 4:20 — 4:50 · GENIE CHAT — THE SYSTEMIC VIEW

**SHOW:**
- Scroll to "Take it with you" footer. Click **Ask the lawbook · Genie chat**.
- Genie chat scene loads with three seed questions as chips.
- Click: *"How many cases in the archive ended with the worker returning early?"*
- Genie thinks (~12-15 s). Answer appears: *"There are 9 cases in the archive where the worker returned early."* SQL details expand below.
- Click the AI-suggested follow-up chip: *"Show all 24-hour embassy hotlines for Philippine workers."*
- Genie thinks again. Returns a table.

**VO:**
> One more layer. Maria can now ask the data directly. Nine cases in the archive ended with the worker returning early. Genie ran the SQL, translated the answer, and suggested the next question to ask.
>
> Same Databricks workspace. Same Unity Catalog. Same conversation.

**TIMING:** 30 seconds.

---

## 4:50 — 5:00 · CLOSE

**SHOW:**
- Click Continue → NGO Dashboard scene.
- Aggregate heatmap renders: corridors × abuse-pattern counts. KPIs at the top.
- Hold for 4-5 seconds.
- Fade to title card: **Panel · marketingdelphi.com · Built on Databricks Apps, Mosaic AI, Lakebase, Genie**

**VO:**
> Per worker, before they sign. Per corridor, across thousands of workers. Built on Databricks Apps, Mosaic AI, Lakebase, and Genie — all four pillars, all load-bearing.
>
> Panel.

**TIMING:** 10 seconds. Cut.

---

## Recording notes

- **One take per scene.** Don't try to do all five minutes live — capture each scene's screen recording separately and stitch.
- **Click confidence.** Hover over buttons for a beat before clicking — gives the viewer time to read the label.
- **The deliberation scene is the most important.** Make sure all six agents complete cleanly before you cut. If the deliberation stalls, retry until it's clean. This is the moat shot.
- **Tagalog rendering.** Make sure the Recommendation letter is visibly in Tagalog when you scroll it. Frame the English subtitle line clearly too — judges should see *both*.
- **Voiceover last.** Edit the silent video first to nail timing, then record the voiceover against the edit. Free yourself from sync stress.
- **Anne's name.** Say it in the deliberation scene VO. The Negotiator is the differentiator and the human story.

---

## Backup talking points (if a scene undershoots)

- *"The provider is swappable — same code runs against Anthropic, OpenAI, Gemini, or a local LM Studio. We default to Mosaic AI in production."*
- *"The contract Maria is reading is built from real recruitment-office contracts surfaced by Migrante and HRW reports. Names redacted, structure intact."*
- *"All four datasets — labor codes, ILO standards, case archive, embassy directory — are in Unity Catalog. Genie reads them through one ACL."*
- *"The whole product ships as a single Databricks Asset Bundle. One command — `databricks bundle deploy` — provisions the Lakebase instance, the SQL warehouse, the serving endpoints, the Genie space, and the app."*
