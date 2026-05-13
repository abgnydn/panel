/**
 * Mocked panel result — same shape the FastAPI backend will return.
 *
 * Values match what the Streamlit version produces on the PH→SA hero
 * sample with all six agents on Claude haiku via claude -p. When the
 * real backend lands, this file is the contract.
 */
export type AgentOutput = {
  agent: string;
  verdict_summary: string;
  key_findings: string[];
  latency_ms?: number;
};

export type ReelItem = {
  rank: number;
  topic: string;
  severity: number;
  source: string;
  why_it_matters: string;
  tensions: Array<{ agent: string; verdict: string }>;
};

export type Rebuttal = {
  agent: string;
  responds_to: string;
  stance: "concede" | "push_back" | "extend";
  rebuttal: string;
};

export type ChecklistItem = {
  action: string;
  priority: "critical" | "high" | "medium";
  details?: string;
};

export type Checklist = {
  before_departure: ChecklistItem[];
  on_arrival: ChecklistItem[];
  during_employment: ChecklistItem[];
  exit_emergency: ChecklistItem[];
};

export type Refusal = { refusal: string; reason: string };
export type Pushback = { clause_number: number; ask: string; suggested: string };

export type NegotiationCoach = {
  strategy: string;
  priority_pushback: {
    clause_number: number;
    topic: string;
    what_to_say_in_l1: string;
    what_to_say_in_english: string;
    fallback_if_refused: string;
    walk_away_threshold: string;
  };
  questions: Array<{
    clause: string;
    question_l1: string;
    question_en: string;
    why_ask: string;
    listen_for: string;
  }>;
  red_flags: Array<{
    if_recruiter_says: string;
    what_it_means: string;
    your_move: string;
  }>;
};

export type PanelResult = {
  agents: Record<string, AgentOutput>;
  disagreement_reel: ReelItem[];
  rebuttals: Record<string, Rebuttal>;
  negotiation: NegotiationCoach;
  checklist: Checklist;
  refusals: Refusal[];
  pushbacks: Pushback[];
  final_urgency_score: number;
  recommendation: {
    tldr: string;
    action_items: string[];
    contacts: Array<{ name: string; phone?: string; whatsapp?: string }>;
  };
};

export const MOCK_RESULT: PanelResult = {
  agents: {
    lawyer: {
      agent: "lawyer",
      verdict_summary:
        "3 of 14 clauses unlawful under KSA labor law; passport retention, open-ended deductions, and unlimited hours all explicitly prohibited.",
      key_findings: [
        "Clause 12 (passport retention) violates KSA Labor Law Art. 6 + MoHRSD Decision 166/2017.",
        "Clause 5 (open-ended employer-discretion deductions) exceeds the statutory limits of Art. 92.",
        "Clause 6 (no fixed working-hours limit) contradicts the 48-hour weekly max in Art. 98.",
        "Recruitment fee (Clause 4) is technically lawful in KSA but borderline.",
      ],
      latency_ms: 39_600,
    },
    translator: {
      agent: "translator",
      verdict_summary:
        "Translation is broadly clear; one ambiguity flag on Clause 5 — 'kaltas' could read as lawful payroll deduction or wage withholding.",
      key_findings: [
        "Clause 5 'deductions at Employer's discretion' renders ambiguously in Tagalog.",
        "Clause 12 'retain the passport for safekeeping' is unambiguous — clearly denotes employer custody.",
        "Plain-language summary rendered in conversational Filipino, ~5 sentences.",
      ],
      latency_ms: 55_100,
    },
    regulator: {
      agent: "regulator",
      verdict_summary:
        "Contract sits below international standards on 5 of 8 ILO core areas, most severely on recruitment fees, working hours, and rest days.",
      key_findings: [
        "Worker-paid SAR 12K recruitment fee violates ILO C181.",
        "No fixed working hours contradicts ILO C189 (Domestic Workers Convention).",
        "No guaranteed weekly rest day violates C189 Art. 10(2).",
        "KSA has not ratified C181 or C189 — local law and standards diverge here intentionally.",
      ],
      latency_ms: 87_100,
    },
    peer_advocate: {
      agent: "peer_advocate",
      verdict_summary:
        "47 similar cases in the archive; passport-retention + recruitment-debt + live-in-isolation patterns cluster strongly with bad outcomes.",
      key_findings: [
        "Live-in housing + no off-day clause: 14 of 23 similar cases ended in early return.",
        "Recruitment debt + low wage: 9 of 19 returned early, 5 unresolved.",
        "Passport retention: 13 of 31 cases involved reported abuse.",
        "Worker situation flags wage-promise discrepancy — Top-3 abuse precursor.",
      ],
      latency_ms: 94_000,
    },
    triage: {
      agent: "triage",
      verdict_summary:
        "Urgency 8/10. Three ILO trafficking indicators converge: passport confiscation, recruitment-fee debt bondage, live-in isolation.",
      key_findings: [
        "Three trafficking indicators present.",
        "Save Philippine Embassy Riyadh 24h hotline before departure.",
        "Save Migrante Saudi Arabia WhatsApp before departure.",
        "Do NOT surrender passport on arrival — illegal in KSA since 2017.",
      ],
      latency_ms: 30_100,
    },
    negotiator: {
      agent: "negotiator",
      verdict_summary:
        "Lead with the wage discrepancy — documented, testable, and the strongest single leverage point. Walk away if the recruiter won't put it in writing.",
      key_findings: [
        "Priority pushback: Clause 3 wage discrepancy (SAR 1,400 vs promised 1,800).",
        "Question 1: 'Boss, SAR 1,800 ang sinabi mo sa akin dati. Pero ang kontrata dito ay SAR 1,400 lang. Alin ang tama?'",
        "Red flag: 'That's the standard contract. Everyone gets the same one.'",
        "Walk-away: refuse to sign if recruiter won't explain the wage gap in writing.",
      ],
      latency_ms: 92_300,
    },
  },
  disagreement_reel: [
    {
      rank: 1,
      topic: "Passport",
      severity: 10,
      source: "implicit_triage_convergence",
      why_it_matters:
        "Three agents converge on this clause from three different lenses — strongest signal in the contract.",
      tensions: [
        { agent: "triage", verdict: "ILO trafficking indicator: passport confiscation." },
        { agent: "lawyer", verdict: "Unlawful — KSA Labor Law Art. 6 + MoHRSD 166/2017." },
        { agent: "regulator", verdict: "Prohibited Clause — C189 §4(d) (workers keep personal documents)." },
      ],
    },
    {
      rank: 2,
      topic: "Recruitment Fees",
      severity: 9,
      source: "implicit_triage_convergence",
      why_it_matters:
        "Local law and international standards diverge — the worker should know both, and that the empirical outcomes are bad.",
      tensions: [
        { agent: "lawyer", verdict: "Gray-area — KSA hasn't ratified C181; locally tolerated." },
        { agent: "regulator", verdict: "Prohibited Clause — C181 §7(a) (no fees to workers)." },
        { agent: "peer_advocate", verdict: "19 similar cases; 14 returned early." },
      ],
    },
    {
      rank: 3,
      topic: "Housing",
      severity: 8,
      source: "implicit_lawyer_peer",
      why_it_matters:
        "The contract is legal AND empirically dangerous — the kind of disagreement Panel was built to surface.",
      tensions: [
        { agent: "lawyer", verdict: "Lawful (KSA general labor law)." },
        { agent: "peer_advocate", verdict: "23 similar cases; 14 ended in early return (61%)." },
      ],
    },
  ],
  rebuttals: {
    lawyer: {
      agent: "lawyer",
      responds_to: "peer_advocate",
      stance: "concede",
      rebuttal:
        "Peer Advocate correctly highlights what I treated too briefly: while Article 6 prohibits passport retention, the documented pattern of employer non-compliance matters as much as the statute.",
    },
    translator: {
      agent: "translator",
      responds_to: "triage",
      stance: "extend",
      rebuttal:
        "Triage raises the wage discrepancy as urgent. As translator I'd flag that the contract itself uses 'kaltas' in a way that could obscure this when read aloud — worth clarifying in writing.",
    },
    regulator: {
      agent: "regulator",
      responds_to: "lawyer",
      stance: "push_back",
      rebuttal:
        "Lawyer's framing of nine 'compliant' clauses risks implying partial acceptability. ILO standards routinely exceed Saudi law, and the recruitment fee is a clear example where local lawfulness isn't enough.",
    },
    peer_advocate: {
      agent: "peer_advocate",
      responds_to: "lawyer",
      stance: "push_back",
      rebuttal:
        "Categorising clauses as 'compliant' obscures a critical point: passport control, discretionary deductions, and rest-day manipulation don't violate the letter of any single statute, but they cluster in our archive with the worst outcomes.",
    },
    triage: {
      agent: "triage",
      responds_to: "lawyer",
      stance: "push_back",
      rebuttal:
        "Lawyer, the violation mapping is precise — but Peer Advocate's case data reveals the gap: these Saudi-law violations become nearly unenforceable once the worker is in-country. The pre-departure window is the leverage point.",
    },
    negotiator: {
      agent: "negotiator",
      responds_to: "regulator",
      stance: "extend",
      rebuttal:
        "Regulator is right that local-and-international diverge — and that's exactly what gives the worker leverage. Frame the recruiter conversation around the international floor, not Saudi law, because the recruiter cares about reputational, not legal, risk.",
    },
  },
  negotiation: {
    strategy:
      "Frame the conversation as seeking clarification, not as accusation. Start with the wage discrepancy — it's documented and testable. If the recruiter admits it was SAR 1,800, use that to leverage the other amendments. Stay information-gathering. Workers who push back too hard get replaced; workers who ask precise questions get treated as informed.",
    priority_pushback: {
      clause_number: 3,
      topic: "wage_discrepancy",
      what_to_say_in_l1:
        "Ma'am/Sir, SAR 1,800 ang sinabi mo sa akin dati. Yan ang promised mo. Pero ang kontrata dito ay SAR 1,400 lang. Kailangan nating ayusin ito bago ako mag-sign. Pwede ba i-correct sa kontrata?",
      what_to_say_in_english:
        "Ma'am/Sir, you told me SAR 1,800 earlier — that was your promise. But the contract says SAR 1,400. We need to fix this before I sign. Can you correct it in writing?",
      fallback_if_refused:
        "If they refuse the SAR 1,800 in writing but offer a written 'bonus' of SAR 400/month, accept only if it's binding and unconditional.",
      walk_away_threshold:
        "If the recruiter insists the wage is SAR 1,400 and refuses to explain the discrepancy or provide written clarification — do not sign. The pattern of unilateral changes is a Top-3 abuse precursor.",
    },
    questions: [
      {
        clause: "Clause 3 (Salary)",
        question_l1: "Boss, SAR 1,800 ang sinabi mo sa akin dati. Pero ang kontrata dito ay SAR 1,400 lang. Alin ang tama?",
        question_en: "Boss, you told me SAR 1,800 before. But the contract says SAR 1,400. Which is correct?",
        why_ask: "Exposes whether the recruiter lied, changed terms, or made an error — documented and testable.",
        listen_for: "Green flag: 'Let me correct it in writing.' Red flag: 'It's the same thing.'",
      },
      {
        clause: "Clause 4 (Recruitment Fee) + Clause 3 (Salary)",
        question_l1: "Ang SAR 12,000 na bayad — ilalabas ba ito sa 1,400 ko bawat buwan? Magkano talaga ang natitira sa akin?",
        question_en: "The SAR 12,000 fee — will it come out of my 1,400/month? What's actually left for me?",
        why_ask: "Worker may not have calculated that the fee reduces her net to ~SAR 733/month (or 1,133 if corrected).",
        listen_for: "Green flag: clear arithmetic in writing. Red flag: 'You can pay over a longer period.'",
      },
      {
        clause: "Clause 6 (Working Hours)",
        question_l1: "Walang limit sa oras ng trabaho. Anong oras ako matutulog?",
        question_en: "There's no limit on working hours. When am I supposed to sleep?",
        why_ask: "Forces concrete daily schedule discussion — KSA Art. 98 caps at 48h/week.",
        listen_for: "Green flag: specific written hours. Red flag: 'Don't worry, the family is reasonable.'",
      },
      {
        clause: "Clause 12 (Passport)",
        question_l1: "Pinapanatili daw ng employer ang passport ko. Pero illegal yan sa Saudi simula 2017. Pwede bang alisin ang clause na ito?",
        question_en: "The employer is to keep my passport. But that's been illegal in Saudi Arabia since 2017. Can we remove this clause?",
        why_ask: "Cites the specific law — shows you're informed. Removes the cleanest trafficking indicator.",
        listen_for: "Green flag: 'You're right, we'll remove it.' Red flag: 'Everyone signs this.'",
      },
      {
        clause: "Clause 7-8 (Housing + Rest Days)",
        question_l1: "Pwede ba akong lumabas tuwing Linggo, kahit limited?",
        question_en: "Can I go out on Sundays, even with limits?",
        why_ask: "Live-in + no-off-day clusters with the worst archive outcomes. Establishing an off-day matters.",
        listen_for: "Green flag: 'Yes, every Friday after lunch.' Red flag: 'Depends on the family.'",
      },
    ],
    red_flags: [
      {
        if_recruiter_says: "That's the standard contract. Everyone gets the same one. You can't change it.",
        what_it_means:
          "The recruiter doesn't want the hassle of going back to the employer with a change request, even though the wage discrepancy and passport clause may be in violation of Saudi law and ILO standards.",
        your_move:
          "Politely ask, 'Could you call the employer and ask? I'm not refusing — I just want it to match what you told me.' Frame it as the recruiter's professional credibility, not your accusation.",
      },
      {
        if_recruiter_says: "The 1,400 is confirmed. The 1,800 was just an estimate.",
        what_it_means:
          "The recruiter bait-and-switched you. 'Bonuses and gifts' are not contractual — they can be withheld as punishment or incentive.",
        your_move:
          "Ask for the bonus structure in writing as part of the contract. If they can't write it down, it doesn't exist.",
      },
      {
        if_recruiter_says: "You can sort it out when you arrive.",
        what_it_means:
          "Once you're in Saudi Arabia under this employer's sponsorship, you have very little leverage. This is the recruiter trying to close the deal.",
        your_move:
          "Do not sign. The pre-departure window is the worker's leverage; after departure it's gone. Walk away if needed.",
      },
      {
        if_recruiter_says: "All Filipinas in the Gulf accept this. Are you better than them?",
        what_it_means:
          "Manipulation. Many Filipinas accept these contracts because they have no choice — that doesn't make the contract fair.",
        your_move:
          "Stay neutral. 'I'm just asking for the contract to match what you told me. That's not too much.'",
      },
    ],
  },
  checklist: {
    before_departure: [
      { action: "Save Philippine Embassy Riyadh POLO 24h hotline offline", priority: "critical", details: "+966 11 488 0888 · WhatsApp +966 50 230 9388" },
      { action: "Save Migrante Saudi Arabia WhatsApp before departure", priority: "critical", details: "+966 53 818 6644" },
      { action: "Take photos of the contract — keep copies on encrypted cloud", priority: "high" },
      { action: "Ask the recruiter for the SAR 1,800 wage in writing", priority: "high" },
      { action: "Brief one family member: which clauses, which numbers, when to escalate", priority: "high" },
      { action: "Memorize the embassy's address in Arabic", priority: "medium" },
    ],
    on_arrival: [
      { action: "Do NOT surrender your passport to the employer", priority: "critical", details: "KSA Labor Law Art. 6 explicitly prohibits retention since 2017" },
      { action: "Register with the Philippine Embassy POLO within 24 hours", priority: "critical" },
      { action: "Confirm address with embassy + give to family", priority: "high" },
      { action: "Take a photo of yourself with the date visible at the airport", priority: "medium" },
    ],
    during_employment: [
      { action: "Keep a daily record of working hours", priority: "critical" },
      { action: "Keep a copy of every payslip / salary receipt", priority: "critical" },
      { action: "If wage deduction exceeds SAR 400/month, contact POLO immediately", priority: "critical" },
      { action: "Weekly check-ins with family — agreed signal if something's wrong", priority: "high" },
      { action: "Save photo of contract on a private email — accessible if employer takes phone", priority: "high" },
    ],
    exit_emergency: [
      { action: "Contact POLO 24h hotline if no wages for 1+ month", priority: "critical" },
      { action: "Contact POLO immediately if physical abuse or threats", priority: "critical" },
      { action: "Contact POLO if employer still holds passport at exit", priority: "critical" },
      { action: "If trapped, ask any sympathetic outsider to call the embassy on your behalf", priority: "critical" },
    ],
  },
  refusals: [
    { refusal: "Don't surrender your passport or any identity document to the employer", reason: "Illegal under KSA Art. 6 since 2017 + ILO trafficking indicator." },
    { refusal: "Don't sign any contract amendment not present in the original", reason: "Verbal promises and side agreements don't survive a dispute." },
    { refusal: "Don't agree to 'unlimited' or 'as required' working hours", reason: "Violates KSA Art. 98 (48-hour cap) and ILO C189." },
    { refusal: "Don't agree to recruitment-fee deductions exceeding 25% of monthly wage", reason: "Bad-outcome cluster: 14 of 19 similar cases ended in early return." },
    { refusal: "Don't accept salary 'partly in goods or accommodation' beyond what's pre-agreed", reason: "Used to obscure wage withholding." },
  ],
  pushbacks: [
    { clause_number: 3, ask: "Wage must be SAR 1,800 as verbally promised", suggested: "Monthly wage of SAR 1,800, paid via bank transfer to Employee's named account on or before the 5th of each Gregorian month." },
    { clause_number: 4, ask: "Recruitment fees borne by Employer per ILO C181", suggested: "All recruitment, placement, visa, and travel costs are borne entirely by the Employer." },
    { clause_number: 6, ask: "Working hours capped at 8/day, 48/week", suggested: "Working hours: 8 hours per day, 6 days per week, with one weekly rest day of 24 consecutive hours (Friday)." },
    { clause_number: 12, ask: "Employee retains custody of passport at all times", suggested: "The Employee retains custody of her passport and all personal identity documents at all times." },
  ],
  final_urgency_score: 8,
  recommendation: {
    tldr:
      "Huwag muna pumirma hanggang sa malinaw ang Clause 3, 7, at 12. May 3 mahalagang isyu — pasaporte, biaya ng recruitment, at tirahan. Kontakin ang Philippine Embassy POLO bago ka umalis.",
    action_items: [
      "Do NOT surrender your passport on arrival — illegal in KSA since 2017.",
      "Save Philippine Embassy Riyadh 24h hotline before departure: +966 11 488 0888.",
      "Save Migrante Saudi Arabia WhatsApp before departure.",
      "Ask the recruiter to put the SAR 1,800 wage in writing before you sign.",
      "If passport is demanded on arrival, contact embassy POLO immediately.",
      "Register with the Philippine Embassy website as OFW within 24h of arrival.",
    ],
    contacts: [
      { name: "Philippine Embassy Riyadh — POLO 24h", phone: "+966 11 488 0888" },
      { name: "Migrante Saudi Arabia", whatsapp: "+966 53 818 6644" },
      { name: "DFA OFW Assistance (Manila)", phone: "1348" },
    ],
  },
} as PanelResult;
