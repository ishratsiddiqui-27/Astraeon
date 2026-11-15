"""Moon-base explorer: pick an atmosphere (or set oxygen and pressure) and see which real flight tests ran nearby."""
import streamlit as st

from astraeon import style, ui
from astraeon.charts import MOON_CHART_ALT
from astraeon.data import MOON_NOTE, MOON_O2_MIN, MOON_PSI_MAX

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


style.page_header("Lunar atmosphere lab", "Explore the Moon-base boundary.",
                  "Move the atmosphere, not the evidence. Pick a condition, then see which real flight tests ran "
                  "there before drawing a conclusion.")

st.segmented_control("Atmosphere", [*ATMOSPHERES, CUSTOM], key="moon_atmosphere", on_change=apply_preset,
                     required=True, label_visibility="collapsed",
                     format_func=lambda name: name.replace("NASA exploration", "Exploration"))
preset = ATMOSPHERES.get(st.session_state.moon_atmosphere)
if preset:
    st.caption(f"{ui.md(preset['note'])} Source: {ui.md(preset['source'])}")

psi_col, o2_col = st.columns(2, gap="medium")
with psi_col:
    with ui.card("moon_psi"):
        with st.container(horizontal=True, vertical_alignment="center"):
            st.markdown("**Pressure**")
            st.space("stretch")
            st.markdown(f"### {st.session_state.moon_psi:.1f} psi")
        st.slider("Pressure (psi)", 0.0, 50.0, step=0.1, format="%.1f psi", key="moon_psi", on_change=mark_custom,
                  label_visibility="collapsed")
with o2_col:
    with ui.card("moon_o2"):
        with st.container(horizontal=True, vertical_alignment="center"):
            st.markdown("**Oxygen concentration**")
            st.space("stretch")
            st.markdown(f"### {st.session_state.moon_o2:.1f}%")
        st.slider("Chamber oxygen (%)", 10.0, 46.0, step=0.5, format="%.1f%%", key="moon_o2", on_change=mark_custom,
                  label_visibility="collapsed")

o2, psi = st.session_state.moon_o2, st.session_state.moon_psi
near = ui.tests_near(o2, psi)
within = near["within"]
in_zone = o2 >= MOON_O2_MIN and psi <= MOON_PSI_MAX

chart_col, info_col = st.columns([1.9, 1], gap="medium")
with chart_col:
    with ui.card("moon_chart", height="stretch"):
        style.card_title("Pressure × oxygen")
        st.caption("The dashed box marks what counts as nearby: ±3 points of oxygen and ±1.5 psi.")
        st.vega_lite_chart(ui.moon_chart((o2, psi)), alt=MOON_CHART_ALT)
with info_col:
    with ui.card("moon_info", kind="cardaccent", height="stretch"):
        if in_zone:
            style.card_title("A condition match. Not a prediction.", "Inside the Moon-base zone")
        else:
            style.card_title("Outside the Moon-base zone.", "Selected atmosphere")
        st.markdown("Pressure and oxygen alone don't describe the fuel, airflow, gravity or ignition source. "
                    + MOON_NOTE.split(". ", 1)[0] + ".")
        st.metric("Flight tests nearby", len(within), border=True)
        st.metric("Experiments", len(near["by_experiment"]), border=True)
        st.space("stretch")
        if st.button("Explore the uncertainties", key="moon_gaps", icon=":material/north_east:",
                     icon_position="right", type="tertiary"):
            st.switch_page("app_pages/history.py")

with ui.card("moon_table"):
    if within:
        style.card_title("Evidence at this boundary")
        st.caption("By experiment: " + ", ".join(f"{name} ({count})" for name, count in near["by_experiment"].items()))
        rows = within
    else:
        style.card_title("Closest flight tests")
        st.warning("No flight test in PSI's per-test records ran this close. That means untested, not safe.",
                   title="Untested here", icon=":material/warning:")
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
    st.caption(f"Only {len(tested)} experiments ({', '.join(tested)}) record oxygen and pressure for every test, "
               f"so the other {len(records) - len(tested)} can't appear here.")
