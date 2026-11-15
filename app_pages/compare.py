"""Compare: 2 or 3 experiments side by side, one row per attribute."""
import streamlit as st

from astraeon import ui
from astraeon.data import SCORE_COLUMNS

records = ui.experiments()
by_id = {r["id"]: r for r in records}

st.title("Compare", anchor=False)
st.caption("Put 2 or 3 experiments side by side. Blank values mean the source doesn't report them.")

default = [i for i in ("acme_cfig", "flex", "acme_bre") if i in by_id]
chosen = st.multiselect("Experiments", list(by_id), default=default, max_selections=3, key="compare_ids",
                        format_func=lambda i: by_id[i]["short_name"], placeholder="Choose 2 or 3 experiments")

if len(chosen) < 2:
    st.info("Choose at least 2 experiments to compare.", icon=":material/compare_arrows:")
    st.stop()

picked = [by_id[i] for i in chosen]
rows = [
    ("Moon status", ui.status_badge_md),
    ("Moon evidence", lambda r: ui.md(r["evidence_detail"])),
    ("Topic", lambda r: ui.md(ui.TOPIC_LABELS.get(r["topic"], r["topic"]))),
    ("Study type", lambda r: ui.md(ui.STUDY_LABELS.get(r["study_type"], r["study_type"]))),
    ("Fuel", lambda r: ui.md(r["fuel_detail"])),
    ("Hardware", lambda r: ui.md(r["hardware"])),
    ("Oxygen", lambda r: ui.md(r["o2_percent"])),
    ("Pressure", lambda r: ui.md(r["pressure_psi"])),
    ("Gravity", lambda r: ui.md(r["gravity"])),
    ("Airflow", lambda r: ui.md(r["airflow"])),
    ("What was varied", lambda r: ui.md(r["what_varied"])),
    ("What stayed the same", lambda r: ui.md(r["what_same"])),
    ("Sensors", lambda r: ui.md(r["sensors"])),
    *[(f"{label} score", lambda r, c=column: ui.score_text(r[c])) for label, column in SCORE_COLUMNS.items()],
    ("Flight platform", lambda r: ui.md(r["flight_platform"])),
    ("Source", lambda r: f"[NASA PSI]({r['source_link']})" if r["source_link"] else ui.md("")),
]

table = {"Attribute": [f"**{label}**" for label, _ in rows]}
for rec in picked:
    table[rec["short_name"]] = [cell(rec) for _, cell in rows]
st.table(table, hide_index=True, alt="Side-by-side comparison of " + ", ".join(r["short_name"] for r in picked))

with st.container(horizontal=True):
    for rec in picked:
        if st.button(f"{rec['short_name']} details", key=f"compare_details_{rec['id']}", icon=":material/open_in_full:"):
            ui.experiment_details(rec)
