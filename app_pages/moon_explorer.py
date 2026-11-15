"""Moon-base explorer: pick an atmosphere (or set oxygen and pressure) and see which real flight tests ran nearby."""
import streamlit as st

from astraeon import ui
from astraeon.charts import MOON_CHART_ALT
from astraeon.data import MOON_NOTE

ATMOSPHERES = {a["name"]: a for a in ui.atmospheres()}
CUSTOM = "Custom"
DEFAULT = "NASA exploration: 8.2 psia, 34%"

# The atmosphere picker sets both sliders; moving a slider switches the picker to "Custom".
if "moon_o2" not in st.session_state:
    start = ATMOSPHERES.get(DEFAULT, {"o2_percent": 30, "pressure_psi": 10.2})
    st.session_state.moon_atmosphere = DEFAULT if DEFAULT in ATMOSPHERES else CUSTOM
    st.session_state.moon_o2 = float(start["o2_percent"])
    st.session_state.moon_psi = float(start["pressure_psi"])


def apply_preset() -> None:
    preset = ATMOSPHERES.get(st.session_state.moon_atmosphere)
    if preset:
        st.session_state.moon_o2 = float(preset["o2_percent"])
        st.session_state.moon_psi = float(preset["pressure_psi"])


def mark_custom() -> None:
    st.session_state.moon_atmosphere = CUSTOM


st.title("Moon-base explorer", anchor=False)
st.caption("Pick an atmosphere, or move the sliders, to see which real flight tests ran nearby.")

with st.container(border=True):
    st.segmented_control("Atmosphere", [*ATMOSPHERES, CUSTOM], key="moon_atmosphere", on_change=apply_preset,
                         required=True)
    o2_col, psi_col = st.columns(2, gap="large")
    with o2_col:
        st.slider("Chamber oxygen (%)", 10.0, 46.0, step=0.5, format="%.1f", key="moon_o2", on_change=mark_custom)
    with psi_col:
        st.slider("Pressure (psi)", 0.0, 50.0, step=0.1, format="%.1f", key="moon_psi", on_change=mark_custom)
    preset = ATMOSPHERES.get(st.session_state.moon_atmosphere)
    if preset:
        st.caption(f"{ui.md(preset['note'])} Source: {ui.md(preset['source'])}")

o2, psi = st.session_state.moon_o2, st.session_state.moon_psi
near = ui.tests_near(o2, psi)
within = near["within"]

with st.grid(3, gap="medium", min_column_width=200):
    st.metric("Flight tests nearby", len(within), border=True, height="stretch")
    st.metric("Experiments", len(near["by_experiment"]), border=True, height="stretch")
    st.metric("Nearby means within", f"±{near['o2_tol']:g} pts O2, ±{near['psi_tol']:g} psi", border=True,
              height="stretch")

with st.container(border=True):
    st.vega_lite_chart(ui.moon_chart((o2, psi)), alt=MOON_CHART_ALT)
    st.caption(MOON_NOTE)

if within:
    st.subheader("Flight tests nearby", anchor=False)
    st.caption("By experiment: " + ", ".join(f"{name} ({count})" for name, count in near["by_experiment"].items()))
    rows = within
else:
    st.warning("No flight test in PSI's per-test records ran this close. That means untested, not safe. "
               "The closest tests are listed instead.", title="Untested here", icon=":material/warning:")
    st.subheader("Closest flight tests", anchor=False)
    rows = near["closest"]

st.dataframe(
    [{k: t[k] for k in ("experiment", "test", "fuel", "o2_percent", "pressure_psi", "outcome", "burn_time_s")}
     for t in rows],
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
records = ui.experiments()
tested_ids = {t["id"] for t in ui.moon_tests()}
tested = sorted(r["short_name"] for r in records if r["id"] in tested_ids)
st.caption(f"Only {len(tested)} experiments ({', '.join(tested)}) record oxygen and pressure for every test, so the "
           f"other {len(records) - len(tested)} can't appear here.")
