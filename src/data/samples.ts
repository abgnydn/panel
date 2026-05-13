/**
 * Sample contract registry — metadata only.
 *
 * Mirrors panel/app/samples.py so the v2 frontend stays in sync with the
 * Python backend. When the FastAPI backend lands, this can be fetched
 * dynamically; for now it's static.
 */
export type Tier = "clean" | "mild" | "bad" | "trafficking";

export type Sample = {
  id: string;
  label: string;
  origin: string;
  origin_label: string;
  destination: string;
  destination_label: string;
  description: string;
  tier: Tier;
  emoji: string;
};

export const SAMPLES: Sample[] = [
  {
    id: "ph_sa_domestic",
    label: "Domestic worker · Manila → Riyadh",
    origin: "PH",
    origin_label: "Philippines",
    destination: "SA",
    destination_label: "Saudi Arabia",
    description:
      "Live-in domestic worker, 2-year contract, SAR 1,400/month. Passport retention, SAR 12K recruitment debt, unlimited hours. Built for the disagreement reel.",
    tier: "bad",
    emoji: "🏠",
  },
  {
    id: "id_my_construction",
    label: "Construction worker · Surabaya → Selangor",
    origin: "ID",
    origin_label: "Indonesia",
    destination: "MY",
    destination_label: "Malaysia",
    description:
      "Bilingual ID/EN, RM 1,200/month, 12-hour days, dormitory housing, passport retention, RM 8.5K recruitment debt. Common SEA corridor.",
    tier: "bad",
    emoji: "🏗️",
  },
  {
    id: "ph_hk_domestic",
    label: "Domestic helper · Manila → Hong Kong",
    origin: "PH",
    origin_label: "Philippines",
    destination: "HK",
    destination_label: "Hong Kong",
    description:
      "Standard HK contract variant. HKD 4,870/month, 2-week rule on termination, agency fees exceeding 10% statutory cap, mandatory live-in.",
    tier: "mild",
    emoji: "🏙️",
  },
  {
    id: "id_sg_construction",
    label: "Construction worker · Surabaya → Singapore",
    origin: "ID",
    origin_label: "Indonesia",
    destination: "SG",
    destination_label: "Singapore",
    description:
      "Work-permit captive at Employer, SGD 700/month, dormitory living, training-cost claw-back, SGD 1,500 early-resignation penalty.",
    tier: "bad",
    emoji: "🏢",
  },
  {
    id: "ph_ae_hotel",
    label: "Hotel housekeeper · Cebu → Dubai",
    origin: "PH",
    origin_label: "Philippines",
    destination: "AE",
    destination_label: "UAE",
    description:
      "Post-Federal-Decree-Law 33/2021 contract. WPS wage protection, employer bears recruitment, worker keeps passport. Mostly compliant.",
    tier: "mild",
    emoji: "🏨",
  },
  {
    id: "clean",
    label: "Clean reference contract · PH → SA",
    origin: "PH",
    origin_label: "Philippines",
    destination: "SA",
    destination_label: "Saudi Arabia",
    description:
      "Compliant reference — full ILO alignment, employer-paid recruitment, 30-day notice both ways. Used to verify Panel doesn't false-alarm.",
    tier: "clean",
    emoji: "✅",
  },
  {
    id: "mild",
    label: "Driver contract · PH → SA",
    origin: "PH",
    origin_label: "Philippines",
    destination: "SA",
    destination_label: "Saudi Arabia",
    description:
      "Driver contract with capped deductions and 1.5× overtime. Some gray areas around rest days and shared repatriation costs.",
    tier: "mild",
    emoji: "🚗",
  },
  {
    id: "trafficking",
    label: "Extreme trafficking contract · composite",
    origin: "PH",
    origin_label: "Philippines",
    destination: "SA",
    destination_label: "Saudi Arabia",
    description:
      "Pathological composite: passport surrender, 24-hr availability, debt bondage, movement restriction. Used to verify Panel escalates.",
    tier: "trafficking",
    emoji: "🚨",
  },
];

export const TIER_BADGE: Record<Tier, { fg: string; bg: string; label: string }> = {
  clean: { fg: "#15803d", bg: "rgba(22,163,74,0.10)", label: "CLEAN" },
  mild: { fg: "#b45309", bg: "rgba(245,158,11,0.12)", label: "MILD" },
  bad: { fg: "#c2410c", bg: "rgba(234,88,12,0.12)", label: "BAD" },
  trafficking: { fg: "#b91c1c", bg: "rgba(185,28,28,0.10)", label: "TRAFFICKING" },
};

export const LANGUAGES: Record<string, string> = {
  tl: "Tagalog / Filipino",
  id: "Bahasa Indonesia",
  en: "English",
};

export function sampleById(id: string): Sample | undefined {
  return SAMPLES.find((s) => s.id === id);
}
