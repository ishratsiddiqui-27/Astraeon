"""Experiments: every experiment as a card or a table, with filters, details and CSV download."""
import streamlit as st

from astraeon import ui
from astraeon.data import show

records = ui.experiments()

st.title("Experiments", anchor=False)
st.caption(f"All {len(records)} NASA PSI combustion experiments, strongest Moon-base evidence first. "
           "Open Details for the full record.")

# --- Filters -----------------------------------------------------------------------------------------------
fuel_options = sorted({r["fuel_type"] for r in records}, key=lambda f: (f == "", f))
topic_options = [t for t in ui.TOPIC_LABELS if any(r["topic"] == t for r in records)]

with st.container(border=True):
    fuel_col, topic_col, o2_col = st.columns([1, 1.3, 1.4])
    with fuel_col:
        fuels = st.pills("Fuel type", fuel_options, selection_mode="multi", key="exp_fuel", wrap=True,
                         format_func=lambda f: ui.FUEL_LABELS.get(f, f))
    with topic_col:
        topics = st.pills("Topic", topic_options, selection_mode="multi", key="exp_topic", wrap=True,
                          format_func=lambda t: ui.TOPIC_LABELS.get(t, t))
    with o2_col:
        o2_low, o2_high = st.slider("Oxygen reported (%)", 0, 100, (0, 100), key="exp_o2",
                                    help="Keeps experiments whose oxygen range overlaps this range.")
    search_col, toggle_col = st.columns([2, 1.4], vertical_alignment="bottom")
    with search_col:
        query = st.text_input("Search", key="exp_query", type="search", live="300ms",
                              placeholder="Name, fuel, hardware or objective", icon=":material/search:")
    with toggle_col:
        include_blank = st.toggle("Include experiments that don't report oxygen", value=True, key="exp_blank")


def matches(rec: dict) -> bool:
    if fuels and rec["fuel_type"] not in fuels:
        return False
    if topics and rec["topic"] not in topics:
        return False
    if rec["o2_min"] is None or rec["o2_max"] is None:
        if not include_blank:
            return False
    elif rec["o2_max"] < o2_low or rec["o2_min"] > o2_high:
        return False
    text = query.strip().lower()
    if text:
        haystack = " ".join(str(rec.get(k, "")) for k in ("name", "short_name", "fuel_detail", "hardware", "objective"))
        if text not in haystack.lower():
            return False
    return True


shown = [r for r in records if matches(r)]

# --- Toolbar -----------------------------------------------------------------------------------------------
with st.container(horizontal=True, vertical_alignment="center"):
    st.markdown(f"Showing **{len(shown)}** of {len(records)}")
    st.space("stretch")
    view = st.segmented_control("View", ["Cards", "Table"], default="Cards", required=True, key="exp_view",
                                label_visibility="collapsed")
    raw = ui.raw_investigations()
    st.download_button("Download CSV", ui.csv_bytes([raw[r["id"]] for r in shown if r["id"] in raw]),
                       file_name="astraeon_experiments.csv", mime="text/csv", icon=":material/download:",
                       on_click="ignore", disabled=not shown, key="exp_download")

if not shown:
    st.info("No experiments match these filters. Clear a filter or turn on the toggle above.",
            icon=":material/filter_alt_off:")
elif view == "Table":
    st.dataframe(
        [{
            "experiment": r["short_name"],
            "moon_status": r["moon_status_label"],
            "topic": ui.TOPIC_LABELS.get(r["topic"], r["topic"]),
            "fuel": ui.FUEL_LABELS.get(r["fuel_type"], r["fuel_type"]),
            "oxygen": show(r["o2_percent"]),
            "pressure": show(r["pressure_psi"]),
            "gravity": show(r["gravity"]),
            "study": ui.STUDY_LABELS.get(r["study_type"], show(r["study_type"])),
            "score_moon": r["score_moon"],
            "source": r["source_link"],
        } for r in shown],
        hide_index=True,
        alt="Experiments matching the filters, with Moon status, oxygen, pressure and source",
        column_config={
            "experiment": st.column_config.TextColumn("Experiment", pinned=True),
            "moon_status": "Moon status",
            "topic": "Topic",
            "fuel": "Fuel",
            "oxygen": "Oxygen",
            "pressure": "Pressure",
            "gravity": "Gravity",
            "study": "Study type",
            "score_moon": st.column_config.ProgressColumn("Moon score", min_value=0, max_value=10, format="%d"),
            "source": st.column_config.LinkColumn("Source", display_text="NASA PSI"),
        },
    )
    st.caption("Switch to Cards to open the full record of an experiment.")
else:
    with st.grid(3, gap="medium", min_column_width=300):
        for rec in shown:
            ui.experiment_card(rec, key_prefix="exp")
