"""Astraeon: fire safety for spacecraft and a Moon base, from NASA's microgravity combustion experiments.

Run locally (or in GitHub Codespaces):   streamlit run app.py
Pages live in app_pages/. Data comes only from data/ through astraeon/ (see README).
The look (starfield, glass cards, animations) is in astraeon/style.py; colours and fonts in .streamlit/config.toml.
"""
import streamlit as st

from astraeon import style
from astraeon.data import ROOT

st.set_page_config(page_title="Astraeon", page_icon=":material/local_fire_department:", layout="wide")
st.logo(str(ROOT / "assets" / "logo.svg"), icon_image=str(ROOT / "assets" / "logo_icon.svg"), size="large")
style.inject()

page = st.navigation(
    [
        st.Page("app_pages/home.py", title="Home", icon=":material/home:", default=True,
                help="The headline finding: which NASA fire tests ran at Moon-base air, on one chart."),
        st.Page("app_pages/experiments.py", title="Experiments", icon=":material/science:",
                help="All 24 NASA PSI combustion experiments. Filter by topic, fuel and reporting, open the full "
                     "record, or download the data."),
        st.Page("app_pages/rankings.py", title="Rank", icon=":material/leaderboard:",
                help="Experiments ranked by how directly they apply to a spacecraft, space station, Moon base or "
                     "rover, with the scoring method."),
        st.Page("app_pages/compare.py", title="Compare", icon=":material/compare_arrows:",
                help="Put up to 3 experiments side by side."),
        st.Page("app_pages/moon_explorer.py", title="Moon-base", icon=":material/nightlight:",
                help="Pick an atmosphere, or set oxygen and pressure yourself, and see which real flight tests "
                     "ran nearby."),
        st.Page("app_pages/history.py", title="Fire history", icon=":material/history:",
                help="Apollo 1, Apollo 13 and the Mir fire, and what the data can't tell us yet."),
        st.Page("app_pages/ask.py", title="Ask Astraeon", icon=":material/forum:",
                help="Ask a question in plain words. Answers come only from Astraeon's data, with numbered "
                     "sources."),
        st.Page("app_pages/about.py", title="About", icon=":material/info:",
                help="What Astraeon is, the evidence policy, sources, how the data was checked, and a glossary."),
    ],
    position="top",
)

page.run()
style.footer()
