"""Astraeon: fire safety for spacecraft and a Moon base, from NASA's microgravity combustion experiments.

Run locally (or in GitHub Codespaces):   streamlit run app.py
Pages live in app_pages/. Data comes only from data/ through astraeon/ (see README).
"""
import streamlit as st

st.set_page_config(page_title="Astraeon", page_icon=":material/local_fire_department:", layout="wide")

page = st.navigation(
    [
        st.Page("app_pages/home.py", title="Home", icon=":material/home:", default=True,
                help="The headline finding: which NASA fire tests ran at Moon-base air, on one chart."),
        st.Page("app_pages/experiments.py", title="Experiments", icon=":material/science:",
                help="All 24 NASA PSI combustion experiments. Filter by fuel, topic and oxygen, open the full "
                     "record, or download the data."),
        st.Page("app_pages/rankings.py", title="Rank by setting", icon=":material/leaderboard:",
                help="Experiments ranked by how directly they apply to a spacecraft, space station, Moon base or "
                     "rover."),
        st.Page("app_pages/compare.py", title="Compare", icon=":material/compare_arrows:",
                help="Put 2 or 3 experiments side by side, row by row."),
        st.Page("app_pages/moon_explorer.py", title="Moon-base explorer", icon=":material/nightlight:",
                help="Pick an atmosphere, or set oxygen and pressure yourself, and see which real flight tests "
                     "ran nearby."),
        st.Page("app_pages/history.py", title="Fire history & gaps", icon=":material/history:",
                help="Apollo 1, Apollo 13 and the Mir fire, and what the data can't tell us yet."),
        st.Page("app_pages/about.py", title="About", icon=":material/info:",
                help="What Astraeon is, where the data comes from, how it was checked, and a glossary."),
    ],
    position="top",
)

page.run()

st.caption("Data: NASA Physical Sciences Informatics (PSI) database. A blank value means the source doesn't "
           "report it, not zero.")
