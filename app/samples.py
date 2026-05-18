"""Sample contract registry.

Each entry carries its own metadata (corridor, tier, description) so the
intake UI can offer a single browse-able list rather than deriving the path
from (origin, destination). Worker language is independent — any sample can
be analysed in any supported L1.
"""
from __future__ import annotations

from pathlib import Path
from typing import TypedDict

_DEMO_DIR = Path(__file__).parent / "data" / "demo_contracts"


class Sample(TypedDict):
    label: str
    path: Path
    origin: str
    destination: str
    description: str
    tier: str  # "clean" | "mild" | "bad" | "trafficking"
    emoji: str


# Order matters for the UI dropdown — hero case first, references at the end.
SAMPLES: dict[str, Sample] = {
    "ph_sa_hero": {
        "label": "Philippines → Saudi Arabia · Maria, 23, domestic worker (HERO)",
        "path": _DEMO_DIR / "ph_sa_domestic_hero.txt",
        "origin": "PH",
        "destination": "SA",
        "description": "3-yr live-in, SAR 750/mo probation then SAR 1,200. SAR 15K recruitment debt + "
                       "SAR 5K performance bond. Passport + phone surrendered on arrival. Explicit "
                       "embassy-contact ban (Clause 10). Substitution clause (Clause 14). Arabic "
                       "version prevails. Built to push every agent to maximum and trigger the "
                       "rebuttal turn hardest.",
        "tier": "trafficking",
        "emoji": "🚨",
    },
    "ph_sa_domestic": {
        "label": "Philippines → Saudi Arabia · Domestic worker (alt)",
        "path": _DEMO_DIR / "ph_sa_domestic_worker.txt",
        "origin": "PH",
        "destination": "SA",
        "description": "Live-in domestic worker, 2-yr contract, SAR 1,400/mo. Passport retention, "
                       "SAR 12K recruitment debt, unlimited hours. Original demo case.",
        "tier": "bad",
        "emoji": "🏠",
    },
    "id_my_construction": {
        "label": "Indonesia → Malaysia · Construction worker",
        "path": _DEMO_DIR / "id_my_construction.txt",
        "origin": "ID",
        "destination": "MY",
        "description": "Bilingual ID/EN, RM 1,200/mo, 12-hr days, dormitory housing, passport "
                       "retention, RM 8.5K recruitment debt. Common SEA corridor.",
        "tier": "bad",
        "emoji": "🏗️",
    },
    "ph_hk_domestic": {
        "label": "Philippines → Hong Kong · Domestic helper",
        "path": _DEMO_DIR / "ph_hk_domestic.txt",
        "origin": "PH",
        "destination": "HK",
        "description": "Standard HK contract variant. HKD 4,870/mo, 2-week rule on termination, "
                       "agency fees exceeding 10% statutory cap, mandatory live-in.",
        "tier": "mild",
        "emoji": "🏙️",
    },
    "id_sg_construction": {
        "label": "Indonesia → Singapore · Construction worker",
        "path": _DEMO_DIR / "id_sg_construction.txt",
        "origin": "ID",
        "destination": "SG",
        "description": "Work-permit captive at Employer, SGD 700/mo, dormitory living, "
                       "training-cost claw-back, SGD 1,500 early-resignation penalty.",
        "tier": "bad",
        "emoji": "🏢",
    },
    "ph_ae_hotel": {
        "label": "Philippines → UAE · Hotel housekeeper (post-2021 reform)",
        "path": _DEMO_DIR / "ph_ae_hotel.txt",
        "origin": "PH",
        "destination": "AE",
        "description": "Post-Federal-Decree-Law 33/2021 contract. WPS wage protection, employer "
                       "bears recruitment, worker keeps passport. Mostly compliant.",
        "tier": "mild",
        "emoji": "🏨",
    },
    "clean": {
        "label": "Clean reference contract (PH → SA)",
        "path": _DEMO_DIR / "clean.txt",
        "origin": "PH",
        "destination": "SA",
        "description": "Compliant reference — full ILO alignment, employer-paid recruitment, "
                       "30-day notice both ways. Used to verify Panel doesn't false-alarm.",
        "tier": "clean",
        "emoji": "✅",
    },
    "mild": {
        "label": "Mild gray-area (PH → SA driver)",
        "path": _DEMO_DIR / "mild.txt",
        "origin": "PH",
        "destination": "SA",
        "description": "Driver contract with capped deductions and 1.5× overtime. Some gray "
                       "areas around rest days and shared repatriation costs.",
        "tier": "mild",
        "emoji": "🚗",
    },
    "trafficking": {
        "label": "Extreme trafficking contract (composite)",
        "path": _DEMO_DIR / "trafficking.txt",
        "origin": "PH",
        "destination": "SA",
        "description": "Pathological composite: passport surrender, 24-hr availability, debt "
                       "bondage, movement restriction. Used to verify Panel escalates.",
        "tier": "trafficking",
        "emoji": "🚨",
    },
}


TIER_BADGE: dict[str, tuple[str, str]] = {
    "clean":        ("#16a34a", "CLEAN"),
    "mild":         ("#f59e0b", "MILD"),
    "bad":          ("#ea580c", "BAD"),
    "trafficking":  ("#b91c1c", "TRAFFICKING"),
}


def load(sample_id: str) -> str:
    s = SAMPLES.get(sample_id)
    if not s:
        return ""
    path = s["path"]
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def all_ids() -> list[str]:
    return list(SAMPLES.keys())


def info(sample_id: str) -> Sample | None:
    return SAMPLES.get(sample_id)
