"""Quality / battery mode.

Run Panel on a battery of contracts spanning the quality spectrum to show
the system's behavioral range. Answers the natural skeptical question:
*"Is this hardcoded to the demo case?"*

Each contract is cached on first run; the page loads instantly after that.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import pandas as pd
import streamlit as st

from app.agents import run_panel

st.set_page_config(page_title="Panel · Quality Battery", page_icon="🧪", layout="wide")

st.title("🧪 Quality Battery")
st.caption(
    "Panel run on four contracts spanning the quality spectrum. "
    "Demonstrates the system's behavioral range — not hardcoded to one demo case."
)

BATTERY = [
    {
        "name": "Clean (compliant reference)",
        "path": "app/data/demo_contracts/clean.txt",
        "origin": "PH", "destination": "SA", "lang": "tl",
        "expected": "0-2 urgency, 0-1 reel items, mostly consensus",
    },
    {
        "name": "Mild (driver, 1-2 gray-areas)",
        "path": "app/data/demo_contracts/mild.txt",
        "origin": "PH", "destination": "SA", "lang": "tl",
        "expected": "3-5 urgency, 1-2 reel items, lawyer-peer tension on rest days",
    },
    {
        "name": "Bad (domestic worker, hero demo)",
        "path": "app/data/demo_contracts/ph_sa_domestic_worker.txt",
        "origin": "PH", "destination": "SA", "lang": "tl",
        "expected": "6-8 urgency, 3 reel items, convergence on passport/fees",
    },
    {
        "name": "Trafficking (extreme)",
        "path": "app/data/demo_contracts/trafficking.txt",
        "origin": "PH", "destination": "SA", "lang": "tl",
        "expected": "9-10 urgency, 3 reel items, max severity, emergency contacts",
    },
]


def load(rel: str) -> str:
    return (_ROOT / rel).read_text(encoding="utf-8")


run_battery = st.button("Run battery", type="primary",
                         help="First run takes a few minutes per contract. Cached after.")

if not run_battery and "battery_results" not in st.session_state:
    st.info("Click **Run battery** to execute Panel on all 4 contracts. "
            "Results are cached — subsequent runs are instant.")
    st.subheader("Test set")
    st.dataframe(
        pd.DataFrame([{"contract": b["name"], "expected_behavior": b["expected"]} for b in BATTERY]),
        hide_index=True, use_container_width=True,
    )
    st.stop()

if run_battery:
    results = []
    progress = st.progress(0.0, text=f"0 / {len(BATTERY)} contracts")
    for i, case in enumerate(BATTERY, 1):
        with st.spinner(f"Running on: {case['name']}..."):
            text = load(case["path"])
            r = run_panel(
                contract_text=text,
                situation="",
                destination_country=case["destination"],
                origin_country=case["origin"],
                worker_l1=case["lang"],
                persist=False,
            )
            results.append({"case": case, "result": r})
        progress.progress(i / len(BATTERY), text=f"{i} / {len(BATTERY)} contracts")
    progress.empty()
    st.session_state["battery_results"] = results

results = st.session_state.get("battery_results") or []

# ----------------------------------------------------------------------------
# Summary table
# ----------------------------------------------------------------------------
st.subheader("Behavioral range")
rows = []
for entry in results:
    r = entry["result"]
    reel = r.get("disagreement_reel") or []
    rows.append({
        "Contract": entry["case"]["name"],
        "Urgency": f"{r.get('final_urgency_score', '?')}/10",
        "Reel items": len(reel),
        "Top severity": max([d.get("severity", 0) for d in reel] or [0]),
        "Top topic": reel[0]["topic"] if reel else "(consensus)",
        "Expected": entry["case"]["expected"],
    })
st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

# ----------------------------------------------------------------------------
# Per-contract detail tabs
# ----------------------------------------------------------------------------
tabs = st.tabs([entry["case"]["name"] for entry in results])
for tab, entry in zip(tabs, results):
    with tab:
        r = entry["result"]
        urg = r.get("final_urgency_score", "?")
        if isinstance(urg, int) and urg >= 7:
            st.error(f"⚠️ Urgency {urg}/10")
        elif isinstance(urg, int) and urg >= 4:
            st.warning(f"Urgency {urg}/10")
        else:
            st.success(f"Urgency {urg}/10")

        st.markdown(f"**Expected:** _{entry['case']['expected']}_")
        st.divider()

        reel = r.get("disagreement_reel") or []
        st.markdown(f"**Disagreement reel ({len(reel)} items):**")
        if reel:
            for d in reel:
                st.markdown(f"- **#{d.get('rank', '?')} · sev {d.get('severity', '?')} · "
                            f"{d.get('topic', '')}** ({d.get('source', '')})")
        else:
            st.info("No significant disagreements — panel reached consensus.")

        with st.expander("All agent summaries"):
            for name, out in (r.get("agents") or {}).items():
                if isinstance(out, dict):
                    st.markdown(f"**{name}**: {out.get('verdict_summary', '')}")
