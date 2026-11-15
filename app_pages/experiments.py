"""Experiments: every experiment as a card or a table, with filters, details and CSV download."""
import streamlit as st

from astraeon import style, ui
from astraeon.data import MOON_STATUSES, NOT_REPORTED, show

records = ui.experiments()
REPORTING = ["Oxygen and pressure", "Oxygen only", "Pressure only", "Neither"]


def reporting(rec: dict) -> str:
    o2, psi = show(rec["o2_percent"]) != NOT_REPORTED, show(rec["pressure_psi"]) != NOT_REPORTED
    return REPORTING[0] if o2 and psi else REPORTING[1] if o2 else REPORTING[2] if psi else REPORTING[3]


style.page_header("Experiment library", "Follow the flame. Find the evidence.",
                  "Browse NASA combustion research by topic, fuel, Moon-base evidence and how completely each "
                  "experiment reports oxygen and pressure.", pill=f"{len(records)} experiments in scope")

# --- Filters -----------------------------------------------------------------------------------------------
fuel_options = sorted({r["fuel_type"] for r in records}, key=lambda f: (f == "", f))
topic_options = [t for t in ui.TOPIC_LABELS if any(r["topic"] == t for r in records)]
status_options = [s for s in MOON_STATUSES if any(r["moon_status"] == s for r in records)]

with ui.card("exp_filters"):
    search_col, topic_col, fuel_col, status_col, report_col, more_col = st.columns(
        [2.2, 1, 1, 1.2, 1.2, 0.9], vertical_alignment="center")
    with search_col:
        query = st.text_input("Search", key="exp_query", type="search", live="300ms", label_visibility="collapsed",
                              placeholder="Search name, fuel, hardware or research question", icon=":material/search:")
    with topic_col:
        topics = st.multiselect("Topic", topic_options, key="exp_topic", placeholder="Topic",
                                label_visibility="collapsed", format_func=lambda t: ui.TOPIC_LABELS.get(t, t))
    with fuel_col:
        fuels = st.multiselect("Fuel", fuel_options, key="exp_fuel", placeholder="Fuel",
                               label_visibility="collapsed", format_func=lambda f: ui.FUEL_LABELS.get(f, f))
    with status_col:
        statuses = st.multiselect("Moon-base evidence", status_options, key="exp_status", placeholder="Moon evidence",
                                  label_visibility="collapsed", format_func=lambda s: MOON_STATUSES[s]["label"])
    with report_col:
        reports = st.multiselect("Reporting", REPORTING, key="exp_reporting", placeholder="Reporting",
                                 label_visibility="collapsed")
    with more_col:
        with st.popover("Oxygen", icon=":material/tune:", width="stretch"):
            o2_low, o2_high = st.slider("Oxygen reported (%)", 0, 100, (0, 100), key="exp_o2",
                                        help="Keeps experiments whose oxygen range overlaps this range.")
            include_blank = st.toggle("Include experiments that don't report oxygen", value=True, key="exp_blank")


def matches(rec: dict) -> bool:
    if topics and rec["topic"] not in topics:
        return False
    if fuels and rec["fuel_type"] not in fuels:
        return False
    if statuses and rec["moon_status"] not in statuses:
        return False
    if reports and reporting(rec) not in reports:
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
    st.markdown(f"**Showing {len(shown)} of {len(records)}** · strongest Moon-base evidence first")
    st.space("stretch")
    view = st.segmented_control("View", ["Cards", "Table"], default="Cards", required=True, key="exp_view",
                                label_visibility="collapsed")
    raw = ui.raw_investigations()
    st.download_button("Download CSV", ui.csv_bytes([raw[r["id"]] for r in shown if r["id"] in raw]),
                       file_name="astraeon_experiments.csv", mime="text/csv", icon=":material/download:",
                       on_click="ignore", disabled=not shown, key="exp_download")

if not shown:
    st.info("No experiments match these filters. Clear a filter or widen the oxygen range.",
            icon=":material/filter_alt_off:")
elif view == "Table":
    with ui.card("exp_table"):
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

neither = sum(1 for r in records if reporting(r) == "Neither")
style.note("Evidence note", f"A blank value means NASA PSI doesn't report it, not zero. {neither} of {len(records)} "
                            "experiments report neither oxygen nor pressure, so they can't be checked against "
                            "Moon-base air.")
