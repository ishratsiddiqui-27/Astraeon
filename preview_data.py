"""Data preview: checks that astraeon/ and data/ work inside Streamlit, including the atmosphere explorer.

This is a developer check, not the dashboard (the dashboard is Person 4's app). Person 4 can copy the
explorer section into a page. Run it in GitHub Codespaces (Streamlit is blocked on Person 1's laptop):
    pip install streamlit
    streamlit run preview_data.py
"""
import pandas as pd
import streamlit as st

from astraeon.charts import MOON_CHART_ALT, moon_chart
from astraeon.data import MOON_NOTE, load_all, load_atmospheres, load_glossary, show, tests_near

st.set_page_config(page_title="Astraeon data preview", page_icon=":material/local_fire_department:", layout="wide")

ATMOSPHERES = {a["name"]: a for a in load_atmospheres()}
CUSTOM = "Custom"
DEFAULT = "NASA exploration: 8.2 psia, 34%"

# The preset picker sets both sliders; moving a slider switches the picker to "Custom".
if "o2" not in st.session_state:
    start = ATMOSPHERES.get(DEFAULT, {"o2_percent": 30, "pressure_psi": 10.2})
    st.session_state.atmosphere = DEFAULT if DEFAULT in ATMOSPHERES else CUSTOM
    st.session_state.o2 = float(start["o2_percent"])
    st.session_state.psi = float(start["pressure_psi"])


def apply_preset():
    preset = ATMOSPHERES.get(st.session_state.atmosphere)
    if preset:
        st.session_state.o2 = float(preset["o2_percent"])
        st.session_state.psi = float(preset["pressure_psi"])


def mark_custom():
    st.session_state.atmosphere = CUSTOM


@st.cache_data
def get_experiments():
    return load_all()


st.title("Astraeon data preview")
st.caption("Developer check of astraeon/ and data/. The real dashboard is Person 4's app.")

# --- Atmosphere explorer -----------------------------------------------------------------------------
st.subheader("Atmosphere explorer")
st.caption("Pick an atmosphere, or move the sliders, to see which real flight tests ran nearby.")
st.segmented_control("Atmosphere", [*ATMOSPHERES, CUSTOM], key="atmosphere", on_change=apply_preset)
left, right = st.columns(2)
with left:
    st.slider("Chamber oxygen (%)", 10.0, 46.0, step=0.5, key="o2", on_change=mark_custom)
with right:
    st.slider("Pressure (psi)", 0.0, 50.0, step=0.1, key="psi", on_change=mark_custom)
o2, psi = st.session_state.o2, st.session_state.psi

preset = ATMOSPHERES.get(st.session_state.atmosphere)
if preset:
    st.caption(f"{preset['note']} Source: {preset['source']}")

near = tests_near(o2, psi)
st.vega_lite_chart(moon_chart(selected=(o2, psi)), alt=MOON_CHART_ALT)
st.caption(MOON_NOTE)

within = near["within"]
c1, c2, c3 = st.columns(3)
c1.metric("Flight tests nearby", len(within))
c2.metric("Experiments", len(near["by_experiment"]))
c3.metric("Nearby means within", f"±{near['o2_tol']:g} pts O2, ±{near['psi_tol']:g} psi")
if within:
    st.caption("By experiment: " + ", ".join(f"{name} ({count})" for name, count in near["by_experiment"].items()))
    rows = within
else:
    st.warning("No flight test in PSI's per-test records ran this close. That means untested, not safe. "
               "The closest tests are listed instead.")
    rows = near["closest"]
table = pd.DataFrame(rows)[["experiment", "test", "fuel", "o2_percent", "pressure_psi", "outcome", "burn_time_s"]]
st.dataframe(
    table,
    hide_index=True,
    alt="Flight tests closest to the selected atmosphere",
    column_config={
        "experiment": "Experiment",
        "test": "Test",
        "fuel": "Fuel",
        "o2_percent": st.column_config.NumberColumn("Oxygen (%)", format="%.1f"),
        "pressure_psi": st.column_config.NumberColumn("Pressure (psi)", format="%.2f"),
        "outcome": "Outcome",
        "burn_time_s": "Burn time (s)",
    },
)
st.caption("Only 4 experiments (ACME CFI-G, ACME Flame Design, FLEX, CFI) record oxygen and pressure for every "
           "test, so the other 20 can't appear here.")

# --- Experiment cards --------------------------------------------------------------------------------
df = get_experiments()
st.subheader(f"{len(df)} experiments, strongest Moon evidence first")
order = {"confirmed": 0, "near_miss": 1, "unconfirmed": 2, "not_a_match": 3, "cannot_check": 4, "not_applicable": 5}
ranked = df.assign(_order=df["moon_status"].map(order)).sort_values(["_order", "score_moon"], ascending=[True, False])

cols = st.columns(3)
for i, (_, row) in enumerate(ranked.iterrows()):
    with cols[i % 3].container(border=True):
        if row["image_file"]:
            st.image(row["image_file"], caption=row["image_credit"], alt=f"Photo from {row['short_name']}", width="stretch")
        st.markdown(f"**{row['short_name']}**")
        st.badge(row["moon_status_label"], color=row["moon_status_color"])
        st.caption(row["moon_takeaway"])
        st.text(f"Oxygen: {show(row['o2_percent'])}\nPressure: {show(row['pressure_psi'])}\nMoon score: {show(row['score_moon'])}/10")

glossary = load_glossary()
with st.expander(f"Glossary ({len(glossary)} terms)"):
    for term, definition in glossary.items():
        st.markdown(f"**{term}**: {definition}")
