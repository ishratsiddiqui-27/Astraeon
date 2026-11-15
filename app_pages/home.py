"""Home: the headline finding, key numbers, the Moon-base chart and the evidence summary."""
import streamlit as st

from astraeon import style, ui
from astraeon.charts import MOON_CHART_ALT
from astraeon.data import MOON_NOTE, MOON_O2_MIN, MOON_PSI_MAX, MOON_STATUSES, NOT_REPORTED, show

records = ui.experiments()
tests = ui.moon_tests()
zone = [t for t in tests if t["in_zone"]]
hot = sum(1 for t in zone if t["outcome"].startswith("Hot ignition: Yes"))
names = {r["id"]: r["short_name"] for r in records}
zone_ids = sorted({t["id"] for t in zone})
neither = sum(1 for r in records if show(r["o2_percent"]) == NOT_REPORTED and show(r["pressure_psi"]) == NOT_REPORTED)
zone_rule = f"{MOON_O2_MIN:g}% oxygen or more at {MOON_PSI_MAX:g} psi or less"

if len(zone_ids) == 1:
    headline = f"Only {names.get(zone_ids[0], zone_ids[0])} recorded flames at Moon-base conditions test by test."
elif zone_ids:
    headline = f"{len(zone_ids)} experiments recorded flames at Moon-base conditions test by test."
else:
    headline = "No experiment recorded a flame at Moon-base conditions test by test."

# --- Hero --------------------------------------------------------------------------------------------------
text_col, art_col = st.columns([1.35, 1], vertical_alignment="center", gap="large")
with text_col:
    style.page_header("Fire science / The next habitat", headline,
                      "Explore what NASA's fire experiments reveal about safer spacecraft and lunar habitats. "
                      "See the evidence. Understand its limits.", hero=True)
    with st.container(horizontal=True):
        if st.button("Explore experiments", key="ctaprimary_home_experiments", icon=":material/north_east:",
                     icon_position="right"):
            st.switch_page("app_pages/experiments.py")
        if st.button("Moon-base explorer", key="ctasecondary_home_moon", icon=":material/arrow_forward:",
                     icon_position="right"):
            st.switch_page("app_pages/moon_explorer.py")
    st.caption("A research lens, not a fire-safety certification.")
with art_col:
    style.moon_art("Lunar research lens", "Lower pressure. Higher oxygen. A different fire environment.")

# --- Key numbers -------------------------------------------------------------------------------------------
style.stat_tiles([
    (len(records), "NASA experiments"),
    (len(tests), "Flight tests with oxygen and pressure"),
    (len(zone), "Tests in the Moon-base zone"),
    (neither, "Report no oxygen or pressure"),
])
st.space("small")

# --- Chart and the evidence gap ----------------------------------------------------------------------------
chart_col, gap_col = st.columns([1.9, 1], gap="medium")
with chart_col:
    with ui.card("home_chart", height="stretch"):
        style.card_title("Where does the evidence reach?")
        st.caption("Every flight test PSI records with chamber oxygen and pressure. The shaded box is the "
                   "Moon-base zone.")
        st.vega_lite_chart(ui.moon_chart(), alt=MOON_CHART_ALT)
        st.caption(MOON_NOTE)
with gap_col:
    with ui.card("home_gap", kind="cardaccent", height="stretch"):
        style.card_title("A zone is not a safety verdict.", "The lunar evidence gap")
        if zone_ids:
            names_text = ", ".join(names.get(i, i) for i in zone_ids)
            st.markdown(f"Our test-by-test check found {len(zone)} flight tests at {zone_rule}, all from "
                        f"**{ui.md(names_text)}**; {hot} ignited a hot flame.")
        if zone_ids == ["acme_cfig"]:
            st.markdown("They burned gas fuels on a burner, not cabin materials, and none ran in partial "
                        "gravity. So the data shows where flames were tested, not that a Moon base is safe.")
        for rec in records:
            if rec["moon_status"] == "near_miss":
                st.caption(f"**{ui.md(rec['short_name'])}**: {ui.md(rec['moon_takeaway'])}")
        st.space("stretch")
        if st.button("Open Moon-base explorer", key="home_gap_explore", icon=":material/north_east:",
                     icon_position="right", type="tertiary"):
            st.switch_page("app_pages/moon_explorer.py")

# --- Evidence summary --------------------------------------------------------------------------------------
with ui.card("home_status"):
    style.card_title(f"Moon evidence across all {len(records)} experiments")
    with st.container(horizontal=True, gap="small"):
        for status, look in MOON_STATUSES.items():
            count = sum(1 for r in records if r["moon_status"] == status)
            st.badge(f"{look['label']} · {count}", color=look["color"])
    st.caption("Each badge comes from the experiment's oxygen and pressure records. Open Experiments to see why.")
