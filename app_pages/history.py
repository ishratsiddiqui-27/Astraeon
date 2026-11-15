"""Fire history & gaps: real spacecraft fires, and what the PSI data can't tell us yet."""
import streamlit as st

from astraeon import ui
from urllib.parse import urlparse

st.title("Fire history & gaps", anchor=False)
st.caption("Why spacecraft fire safety matters, and what the experiments in this dataset don't cover yet.")

# --- Incidents ---------------------------------------------------------------------------------------------
st.subheader("Fires in crewed spaceflight", anchor=False, icon=":material/history:")
for incident in ui.incidents():
    with st.container(border=True):
        date_col, text_col = st.columns([1, 4], gap="medium")
        with date_col:
            st.markdown(f"### {incident.get('date', '')[:4]}")
            st.caption(ui.long_date(incident.get("date", "")))
        with text_col:
            st.markdown(f"**{ui.md(incident['name'])}**")
            st.markdown(ui.md(incident.get("summary", "")))
            if incident.get("related_names"):
                st.caption("Related experiments")
                ui.name_badges(incident["related_names"])
            if incident.get("data_note"):
                st.caption(ui.md(incident["data_note"]))
            sources = incident.get("sources", [])
            if sources:
                links = " · ".join(f"[{urlparse(url).netloc.removeprefix('www.')}]({url})" for url in sources)
                st.caption(f"Sources: {links}")

# --- Research gaps -----------------------------------------------------------------------------------------
gaps = ui.research_gaps()
if gaps:
    st.subheader("What we don't know yet", anchor=False, icon=":material/help_outline:")
    with st.grid(2, gap="medium", min_column_width=320):
        for gap in gaps:
            with st.container(border=True, height="stretch"):
                st.markdown(f"**{ui.md(gap['title'])}**")
                st.markdown(ui.md(gap.get("summary", "")))
                if gap.get("evidence"):
                    st.caption(ui.md(gap["evidence"]))
                if gap.get("related_names"):
                    ui.name_badges(gap["related_names"])
                if gap.get("source"):
                    st.caption(f"Source: {ui.md(gap['source'])}")
