"""Home: the headline finding, key numbers, the Moon-base chart and the evidence summary."""
import streamlit as st

from astraeon import ui
from astraeon.charts import MOON_CHART_ALT
from astraeon.data import MOON_NOTE, MOON_O2_MIN, MOON_PSI_MAX, MOON_STATUSES, NOT_REPORTED, show

records = ui.experiments()
tests = ui.moon_tests()
zone = [t for t in tests if t["in_zone"]]
hot = sum(1 for t in zone if t["outcome"].startswith("Hot ignition: Yes"))
names = {r["id"]: r["short_name"] for r in records}
zone_ids = sorted({t["id"] for t in zone})
neither = sum(1 for r in records if show(r["o2_percent"]) == NOT_REPORTED and show(r["pressure_psi"]) == NOT_REPORTED)
zone_rule = f"{MOON_O2_MIN:g}% oxygen or more and {MOON_PSI_MAX:g} psi or less"

st.title("Astraeon", anchor=False)
st.caption(f"{len(records)} NASA microgravity combustion experiments, checked against Moon-base air ({zone_rule}).")

# --- Headline ----------------------------------------------------------------------------------------------
with st.container(border=True):
    if len(zone_ids) == 1:
        st.subheader(f"Only {names.get(zone_ids[0], zone_ids[0])} recorded flames at Moon-base conditions test by test.",
                     anchor=False, icon=":material/verified:")
    elif zone_ids:
        st.subheader(f"{len(zone_ids)} experiments recorded flames at Moon-base conditions test by test.",
                     anchor=False, icon=":material/verified:")
    else:
        st.subheader("No experiment recorded a flame at Moon-base conditions test by test.", anchor=False)
    body = f"{len(zone)} of {len(tests)} flight tests ran at {zone_rule}. {hot} ignited a hot flame."
    if zone_ids == ["acme_cfig"]:
        body += " They burned gas fuels on a burner, not cabin materials."
    st.markdown(body)
    for rec in records:
        if rec["moon_status"] == "near_miss":
            st.caption(f"**{ui.md(rec['short_name'])}** · {ui.md(rec['moon_takeaway'])}")

# --- Key numbers -------------------------------------------------------------------------------------------
glossary = ui.glossary()
with st.grid(4, gap="medium", min_column_width=200):
    st.metric("Experiments", len(records), border=True, height="stretch",
              help="NASA PSI investigations in the Combustion Science category.")
    st.metric("Flight tests with oxygen and pressure", len(tests), border=True, height="stretch",
              help="Tests whose chamber oxygen and pressure PSI records one by one (4 experiments).")
    st.metric("Tests in the Moon-base zone", len(zone), border=True, height="stretch",
              help=glossary.get("Moon-base zone") or zone_rule)
    st.metric("Report neither oxygen nor pressure", neither, border=True, height="stretch",
              help="Experiments that can't be checked against Moon-base air at all.")

# --- Chart -------------------------------------------------------------------------------------------------
with st.container(border=True):
    st.vega_lite_chart(ui.moon_chart(), alt=MOON_CHART_ALT)
    st.caption(MOON_NOTE)

# --- Evidence summary --------------------------------------------------------------------------------------
st.subheader(f"Moon evidence across all {len(records)} experiments", anchor=False)
with st.container(horizontal=True, gap="small"):
    for status, look in MOON_STATUSES.items():
        count = sum(1 for r in records if r["moon_status"] == status)
        st.badge(f"{look['label']} · {count}", color=look["color"])
st.caption("Each experiment's badge comes from its oxygen and pressure records. Open Experiments to see why.")

# --- Photos ------------------------------------------------------------------------------------------------
photos = [r for r in records if r["image_file"]]
if photos:
    st.subheader("Inside the experiments", anchor=False)
    with st.grid(len(photos), gap="medium", min_column_width=180):
        for rec in photos:
            st.image(rec["image_file"], caption=f"{rec['short_name']} · {rec['image_credit']}",
                     alt=f"Photo from {rec['short_name']}", width="stretch")

# --- Next steps --------------------------------------------------------------------------------------------
with st.container(horizontal=True):
    st.page_link("app_pages/moon_explorer.py", label="Try the Moon-base explorer", icon=":material/nightlight:")
    st.page_link("app_pages/experiments.py", label="Browse the experiments", icon=":material/science:")
    st.page_link("app_pages/history.py", label="Fire history & gaps", icon=":material/history:")
