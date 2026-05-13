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

export type PanelResult = {
  agents: Record<string, AgentOutput>;
  disagreement_reel: ReelItem[];
  rebuttals: Record<string, Rebuttal>;
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
};
