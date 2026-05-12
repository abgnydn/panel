"""NGO aggregate dashboard — abuse-pattern heatmap + urgent sessions feed.

Sources:
- panel.db sessions + recommendations (real, populated as workers use Panel)
- case_archive.json (seed; what NGOs see today)

For demo purposes, falls back to case_archive aggregation when no real
sessions exist yet.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import pandas as pd
import plotly.express as px
import streamlit as st

from app import store, style
from app.agents.base import load_data


st.set_page_config(page_title="Panel · NGO Dashboard", page_icon="📊", layout="wide")
style.inject()

style.hero(
    title="NGO Dashboard",
    subtitle="Aggregate view across every Panel session. With each worker's consent, "
             "anonymized findings join the case archive — turning one contract review "
             "into systemic intelligence.",
    icon="📊",
)

# ----------------------------------------------------------------------------
# Pull data
# ----------------------------------------------------------------------------
recent = store.recent_sessions(500)
urgent = store.urgent_sessions_24h()
case_archive = load_data("case_archive")

# Combined view: archive cases tagged as "archive", real sessions tagged as "live"
all_records = []
for c in case_archive:
    all_records.append({
        "source": "archive",
        "origin": c["country_of_origin"],
        "destination": c["destination_country"],
        "clause_category": c["clause_category"],
        "outcome": c["outcome"],
        "year": c.get("year"),
    })

for s in recent:
    all_records.append({
        "source": "live",
        "origin": s.get("country_of_origin"),
        "destination": s.get("destination_country"),
        "clause_category": "session",
        "outcome": "urgent" if (s.get("urgency_score") or 0) >= 7 else "reviewed",
        "year": None,
    })

df = pd.DataFrame(all_records)

# ----------------------------------------------------------------------------
# KPI strip
# ----------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Cases in archive", len(case_archive))
col2.metric("Live sessions (all-time)", len(recent))
col3.metric("Urgent (last 24h)", len(urgent))
col4.metric("Corridors covered", df[["origin", "destination"]].drop_duplicates().shape[0] if not df.empty else 0)

st.divider()

# ----------------------------------------------------------------------------
# Heatmap: clause_category × destination, color = % bad outcome
# ----------------------------------------------------------------------------
st.subheader("Abuse-pattern heatmap")
st.caption("Clause types vs destination countries. Color = % of cases ending in early return, abuse report, or unresolved.")

archive_df = df[df["source"] == "archive"].copy()
if not archive_df.empty:
    archive_df["bad"] = archive_df["outcome"].isin(
        ["worker_returned_early", "abuse_reported", "unresolved"]
    )
    grouped = archive_df.groupby(["destination", "clause_category"]).agg(
        cases=("bad", "size"),
        bad_count=("bad", "sum"),
    ).reset_index()
    grouped["pct_bad"] = (grouped["bad_count"] / grouped["cases"] * 100).round(1)

    heatmap = grouped.pivot(index="clause_category", columns="destination", values="pct_bad").fillna(0)
    fig = px.imshow(
        heatmap,
        labels=dict(x="Destination", y="Clause type", color="% bad outcome"),
        color_continuous_scale="Reds",
        aspect="auto",
        text_auto=".0f",
    )
    fig.update_layout(height=400, margin=dict(l=40, r=20, t=30, b=40))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No archive data yet.")

# ----------------------------------------------------------------------------
# Outcome breakdown bar chart
# ----------------------------------------------------------------------------
st.subheader("Outcomes by clause type")
if not archive_df.empty:
    outcome_counts = archive_df.groupby(["clause_category", "outcome"]).size().reset_index(name="count")
    fig2 = px.bar(
        outcome_counts,
        x="clause_category",
        y="count",
        color="outcome",
        barmode="stack",
        labels={"clause_category": "Clause type", "count": "Cases"},
        color_discrete_map={
            "resolved_favorably": "#4caf50",
            "worker_returned_early": "#ff9800",
            "abuse_reported": "#d32f2f",
            "unresolved": "#9e9e9e",
        },
    )
    fig2.update_layout(height=400, margin=dict(l=40, r=20, t=30, b=40))
    st.plotly_chart(fig2, use_container_width=True)

# ----------------------------------------------------------------------------
# Urgent sessions feed
# ----------------------------------------------------------------------------
st.subheader("Urgent sessions (last 24h)")
if urgent:
    urgent_df = pd.DataFrame(urgent)
    st.dataframe(
        urgent_df[["started_at", "country_of_origin", "destination_country",
                   "native_language", "urgency_score", "summary_en"]],
        hide_index=True,
        use_container_width=True,
    )
else:
    st.info("No urgent sessions in the last 24 hours. (When workers use Panel and trigger ≥7 urgency, they appear here for NGO partners.)")

# ----------------------------------------------------------------------------
# Corridor summary
# ----------------------------------------------------------------------------
st.subheader("Activity by corridor")
if not df.empty:
    corridor = df.groupby(["origin", "destination", "source"]).size().reset_index(name="count")
    fig3 = px.bar(
        corridor,
        x="destination",
        y="count",
        color="source",
        facet_col="origin",
        labels={"destination": "Destination", "count": "Cases / sessions"},
    )
    fig3.update_layout(height=350, margin=dict(l=40, r=20, t=40, b=40))
    st.plotly_chart(fig3, use_container_width=True)
