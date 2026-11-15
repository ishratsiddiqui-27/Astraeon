"""Rank by setting: experiments sorted by their 0-10 score for one setting, with the reason for each."""
import streamlit as st

from astraeon import ui
from astraeon.charts import rank_chart, rank_chart_alt
from astraeon.data import MOON_NOTE, SCORE_COLUMNS

records = ui.experiments()

st.title("Rank by setting", anchor=False)
st.caption("How directly each experiment's findings apply to fire safety in one setting, from 0 to 10.")

setting = st.segmented_control("Setting", list(SCORE_COLUMNS), default="Moon base", required=True, key="rank_setting")
column = SCORE_COLUMNS[setting]

st.info("PSI has no partial-gravity data yet; Moon relevance is inferred. " + MOON_NOTE.split(". ", 1)[-1],
        icon=":material/info:")

scored = sorted((r for r in records if r[column] is not None), key=lambda r: (-r[column], r["short_name"].lower()))

# Competition ranking: equal scores share a rank (1, 2, 2, 4, ...).
ranks, previous = [], None
for position, rec in enumerate(scored, start=1):
    if rec[column] != previous:
        rank, previous = position, rec[column]
    ranks.append(rank)

chart_col, list_col = st.columns([1.1, 1], gap="large")
with chart_col:
    with st.container(border=True):
        st.vega_lite_chart(rank_chart(scored, column, setting), alt=rank_chart_alt(scored, column, setting))

with list_col:
    st.subheader("Top of the list", anchor=False)
    for rank, rec in list(zip(ranks, scored))[:5]:
        with st.container(border=True):
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown(f"**#{rank} {ui.md(rec['short_name'])}**")
                st.space("stretch")
                st.badge(f"{rec[column]}/10", color="orange")
            ui.badges(rec, show_fuel=False)
            st.caption(ui.md(rec["reason"]))
            if st.button("Details", key=f"rank_details_{rec['id']}", icon=":material/open_in_full:", type="tertiary"):
                ui.experiment_details(rec)

st.subheader(f"All {len(scored)} experiments", anchor=False)
st.dataframe(
    [{
        "rank": rank,
        "experiment": rec["short_name"],
        "score": rec[column],
        "moon_status": rec["moon_status_label"],
        "reason": rec["reason"],
    } for rank, rec in zip(ranks, scored)],
    hide_index=True,
    alt=f"All experiments ranked by {setting.lower()} score, with the reason for each",
    column_config={
        "rank": st.column_config.NumberColumn("Rank", format="%d", width="small"),
        "experiment": st.column_config.TextColumn("Experiment", pinned=True),
        "score": st.column_config.ProgressColumn(f"{setting} score", min_value=0, max_value=10, format="%d"),
        "moon_status": "Moon status",
        "reason": st.column_config.TextColumn("Why", width="large"),
    },
)
st.caption("Scores follow the rubric in data/RANKINGS_NOTES.md. Moon-base scores also reflect the oxygen and "
           "pressure evidence.")
