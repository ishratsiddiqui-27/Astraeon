"""Compare: up to 3 experiments side by side, as aligned cards."""
import streamlit as st

from astraeon import style, ui
from astraeon.data import SCORE_COLUMNS

records = ui.experiments()
by_id = {r["id"]: r for r in records}

# Start with three contrasting experiments; "Add to comparison" in a details dialog changes this list.
if ui.COMPARE_KEY not in st.session_state:
    st.session_state[ui.COMPARE_KEY] = [i for i in ("acme_cfig", "flex", "acme_bre") if i in by_id]

style.page_header("Side-by-side evidence", "Same question. Different experiments.",
                  "Compare research context without mistaking missing data for a negative result.")

with ui.card("compare_picker"):
    chosen = st.multiselect("Comparing", list(by_id), key=ui.COMPARE_KEY, max_selections=ui.MAX_COMPARE,
                            format_func=lambda i: by_id[i]["short_name"], placeholder="Add an experiment",
                            help=f"Choose up to {ui.MAX_COMPARE} experiments.")

picked = [by_id[i] for i in chosen if i in by_id]
ROWS = [
    ("Research focus", lambda r: ui.md(ui.first_sentence(r["objective"], 220))),
    ("Moon-base relevance", lambda r: f"{ui.status_badge_md(r)}  \n{ui.md(r['moon_takeaway'])}"),
    ("Pressure / oxygen", lambda r: f"{ui.md(r['pressure_psi'])}  \n{ui.md(r['o2_percent'])}"),
    ("Flight-test records", lambda r: ui.md(ui.test_summary(r["id"]))),
    ("Fuel", lambda r: ui.md(r["fuel_detail"] or ui.FUEL_LABELS.get(r["fuel_type"], ""))),
    ("Gravity", lambda r: ui.md(r["gravity"])),
    ("What was varied", lambda r: ui.md(r["what_varied"])),
    ("Scores (0-10)", lambda r: " · ".join(f"{label} {ui.score_text(r[col])}" for label, col in SCORE_COLUMNS.items())),
    ("Evidence source", lambda r: f"[NASA {ui.psi_id(r)}]({r['source_link']})" if r["source_link"] else ui.md("")),
]

columns = st.columns(ui.MAX_COMPARE, gap="medium")
for slot, col in enumerate(columns):
    with col:
        if slot < len(picked):
            rec = picked[slot]
            with ui.card(f"compare_{rec['id']}", height="stretch"):
                style.eyebrow(f"NASA PSI · {ui.psi_id(rec)}")
                st.markdown(f"### {ui.md(rec['short_name'])}")
                st.caption(ui.md(ui.subtitle(rec)))
                for label, cell in ROWS:
                    st.caption(label.upper())
                    st.markdown(cell(rec))
                st.space("stretch")
                if st.button("View details", key=f"compare_details_{rec['id']}", icon=":material/north_east:",
                             icon_position="right", type="tertiary"):
                    ui.experiment_details(rec)
        else:
            with ui.card(f"compare_add_{slot}", kind="carddashed", height="stretch"):
                st.space("large")
                st.markdown("### :material/add:", text_alignment="center")
                st.markdown("**Widen the comparison**", text_alignment="center")
                st.caption("Add another experiment with the picker above to compare it on the same rows.",
                           text_alignment="center")
                st.space("large")

style.note("Reading note", "\"Not reported\" means the source is silent: the value is unknown, not zero and not "
                           "a negative result.")
