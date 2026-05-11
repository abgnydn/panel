# Panel — 5-Minute Demo Script

**Total runtime:** 5:00 (hard cap per rules)
**Audience:** Databricks + AWS judges (technical but not domain experts)
**Languages:** English voiceover, Tagalog on-screen for hero demo
**Setup:** Live screen recording of the deployed app + cuts to the architecture slide + dashboard

---

## 0:00 – 0:30 — Hook (the human cost)

**Voiceover:**
> Ten million Filipinos work abroad. Seven hundred thousand Indonesians leave every year. Most have never read their employment contract in their own language. By the time they understand what they signed, they're in another country — passport with the employer, recruitment debt growing.
>
> We built Panel.

**On screen:** Stock footage / Creative Commons images of departure terminals. Sparse text overlay: `10M+`, `700K/yr`, `$0 legal aid before signing`.

**Cut at 0:30 to the app.**

---

## 0:30 – 2:30 — Walkthrough (the hero case)

**Voiceover:**
> Maria is a domestic worker from Manila bound for Riyadh. She uploads her contract — in Tagalog.

**On screen:** Phone-screen mock. Tagalog UI. Upload a photo of a real (anonymized) PH → SA domestic worker contract from the ILO archive.

**Voiceover:**
> Five specialist agents read her contract in parallel.

**On screen:** All 5 panes light up with "Analyzing..." then settle one-by-one (with the 0.4s stagger from `app.py`).

- ⚖️ **Lawyer** — "3 of 14 clauses unlawful under KSA labor law."
- 🌐 **Translator** — "Translation clear. 1 ambiguity flag on Clause 5."
- 🏛️ **Regulator** — "Below international standard in 5 of 8 ILO core areas."
- 🫱🏽‍🫲🏾 **Peer Advocate** — "47 similar cases. Risk score 7.2 / 10."
- 🚨 **Triage** — "Urgency 8/10. Three trafficking indicators."

**Voiceover (over the panel results):**
> The Lawyer reads the destination's labor code. The Translator renders it in Maria's mother tongue. The Regulator compares it to ILO and ASEAN standards. The Peer Advocate searches twenty-three thousand anonymized real-world cases. Triage detects trafficking signals.

---

## 2:30 – 3:30 — Disagreement reel (the moat)

**Voiceover:**
> This is where Panel earns its name.

**On screen:** Scroll to the disagreement reel section. Slowly walk through the top 2 disagreements.

**Disagreement #1:** Recruitment fees (Clause 4)
- ⚖️ Lawyer: *Lawful in Saudi Arabia.*
- 🏛️ Regulator: *Violates ILO Convention 181. Below international standard.*
- 🫱🏽‍🫲🏾 Peer Advocate: *Twenty-three similar cases. Fourteen ended in early return.*

**Voiceover:**
> Three agents. Three different answers. The contract is legal — *and* historically dangerous. Maria deserves to know both.

**Disagreement #2:** Live-in housing (Clause 7)
- ⚖️ Lawyer: *Lawful. KSA permits employer-provided housing.*
- 🏛️ Regulator: *Silent — ILO has no convention on housing per se.*
- 🫱🏽‍🫲🏾 Peer Advocate: *High historical risk. Look at the case cluster.*

**Voiceover:**
> A single agent would have said "looks fine." Panel doesn't.

---

## 3:30 – 4:30 — NGO view (data storytelling)

**Voiceover:**
> Zoom out from Maria.

**Cut to:** AI/BI Dashboard tab. Heatmap of abuse-pattern clusters across origin → destination → clause type.

**Voiceover:**
> Every contract Panel reviews — with consent — becomes part of the case archive. Within months, NGOs and labor ministries can see where the patterns are. Recruitment fees in this corridor. Passport retention in that one. We turn one worker's contract into systemic intelligence.

**On screen:** Highlight 2-3 hot cells on the heatmap. PH → SA recruitment fees. ID → MY passport retention.

---

## 4:30 – 5:00 — The ask

**Voiceover:**
> Panel is built on Databricks. Agent Bricks runs the five specialists. Genie translates Maria's questions into queries over labor codes. Lakebase holds the case archive. The app is one click to deploy.
>
> We want to put this in front of the International Labor Organization, ASEAN labor ministries, and the Philippine and Indonesian overseas-worker agencies — before the next ten million workers sign contracts they can't read.
>
> Panel.

**On screen:** Closing card. Team name. Project name. Country: Singapore. Contact.

---

## Production notes

- **Recording resolution:** 1920×1080. Phone mock at 2× scale for legibility.
- **Voiceover:** single take, native English. Re-record budget: 2 takes max.
- **Music:** none, or one quiet bed throughout. Subtitles for accessibility.
- **Cuts:** ~12 cuts total. Don't over-edit — judges fatigue on rapid cuts.
- **Aspect ratio:** 16:9 horizontal. (Don't deliver vertical, despite the mobile UI.)

## What gets cut if we run long

In this order:
1. The second disagreement (drop Live-in housing, keep Recruitment fees only)
2. The NGO dashboard segment (collapse to 15s)
3. The hook (cut to 15s with bigger numbers, less footage)

Hard floor: walkthrough + disagreement reel + ask. Never cut those.
