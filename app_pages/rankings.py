"""Rank: experiments sorted by their 0-10 score for one setting, with the method and the reason for each."""
import streamlit as st

from astraeon import style, ui
from astraeon.charts import rank_chart, rank_chart_alt
from astraeon.data import MOON_O2_MIN, MOON_PSI_MAX, SCORE_COLUMNS

records = ui.experiments()
by_id = {r["id"]: r["short_name"] for r in records}

# What each setting means (data/RANKINGS_NOTES.md, "What the scores mean").
SETTINGS = {
    "Spacecraft": "A crewed vehicle in transit, such as a capsule or cargo vehicle, in microgravity.",
    "Space station": "A long-duration microgravity station such as the ISS, where most of these experiments "
                     "flew. Station scores are never lower than spacecraft scores.",
    "Moon base": f"A Moon base, which the challenge brief expects to run at {MOON_O2_MIN:g}% oxygen or more and "
                 f"{MOON_PSI_MAX:g} psi or less.",
    "Rover": "A small crewed pressurized rover cabin. Rover scores stay within 1 point of Moon scores and aren't "
             "adjusted for oxygen and pressure, because the brief gives no rover cabin atmosphere.",
}

style.page_header("Mission fit", "Rank evidence, not assumptions.",
                  "Choose a habitat. See how directly each experiment's findings apply there, and why.")

setting = st.segmented_control("Setting", list(SCORE_COLUMNS), default="Moon base", required=True,
                               key="rank_setting", label_visibility="collapsed")
column = SCORE_COLUMNS[setting]
scored = sorted((r for r in records if r[column] is not None), key=lambda r: (-r[column], r["short_name"].lower()))

# Competition ranking: equal scores share a rank (1, 2, 2, 4, ...).
ranks, previous = [], None
for position, rec in enumerate(scored, start=1):
    if rec[column] != previous:
        rank, previous = position, rec[column]
    ranks.append(rank)

chart_col, method_col = st.columns([1.9, 1], gap="medium")
with chart_col:
    with ui.card("rank_chart", height="stretch"):
        style.card_title(f"{setting} relevance")
        st.vega_lite_chart(rank_chart(scored, column, setting), alt=rank_chart_alt(scored, column, setting))
with method_col:
    with ui.card("rank_method", kind="cardaccent", height="stretch"):
        style.card_title("A score with a method.", "How the score works")
        st.markdown("Each score runs from **0 to 10**: how directly the experiment's findings apply to fire "
                    "safety in this setting. 10 means the data applies directly; 0 means it doesn't apply.")
        st.markdown(f"**{setting}:** {SETTINGS[setting]}")
        st.caption("PSI has no partial-gravity data yet, so Moon relevance is inferred from oxygen and pressure. "
                   "Full rubric and every change: data/RANKINGS_NOTES.md.")
        top = [r["short_name"] for r, rank in zip(scored, ranks) if rank == 1]
        if top:
            st.space("stretch")
            st.markdown(f"Top score: **{ui.md(', '.join(top))}** at {scored[0][column]}/10")

if setting == "Moon base":
    with ui.card("rank_moon_rule"):
        style.card_title("What moves a Moon-base score")
        st.caption("Start from general relevance, usually 1 to 2 points below the spacecraft score, because "
                   "microgravity results don't carry over to lunar gravity. Then adjust for oxygen and pressure "
                   "evidence.")
        same, near, ranges = st.columns(3, gap="medium")
        with same:
            st.markdown("**Same-test evidence → 10**")
            st.caption(f"Burned at {MOON_O2_MIN:g}% oxygen or more and {MOON_PSI_MAX:g} psi or less in the same "
                       f"test. {by_id.get('acme_cfig', 'ACME CFI-G')}.")
        with near:
            st.markdown("**Near miss or built for it → 9**")
            st.caption("Within 0.3 psi of the zone, or designed around those atmospheres without per-test "
                       f"pressure records. {by_id.get('flex', 'FLEX')}, {by_id.get('acme_bre', 'ACME BRE')}.")
        with ranges:
            st.markdown("**No same-test match → no bonus**")
            st.caption("Oxygen and pressure ranges overlap Moon conditions, but no single test ties them together, "
                       f"or high oxygen only at about 1 atm. {by_id.get('flex2', 'FLEX-2')}, "
                       f"{by_id.get('acme_sflame', 'ACME s-Flame')}.")

st.subheader("Top of the list", anchor=False)
with st.grid(3, gap="medium", min_column_width=280):
    for rank, rec in list(zip(ranks, scored))[:6]:
        with ui.card(f"rank_top_{rec['id']}", height="stretch"):
            with st.container(horizontal=True, vertical_alignment="center"):
                st.markdown(f"**#{rank} {ui.md(rec['short_name'])}**")
                st.space("stretch")
                st.badge(f"{rec[column]}/10", color="orange")
            ui.badges(rec, show_fuel=False)
            st.caption(ui.md(rec["reason"]))
            st.space("stretch")
            if st.button("View details", key=f"rank_details_{rec['id']}", icon=":material/north_east:",
                         icon_position="right", type="tertiary"):
                ui.experiment_details(rec)

with st.expander(f"All {len(scored)} experiments with reasons", icon=":material/table_rows:"):
    st.dataframe(
        [{"rank": rank, "experiment": rec["short_name"], "score": rec[column],
          "moon_status": rec["moon_status_label"], "reason": rec["reason"]} for rank, rec in zip(ranks, scored)],
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
