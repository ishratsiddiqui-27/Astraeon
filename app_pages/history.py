"""Fire history & gaps: real spacecraft fires, and what the PSI data can't tell us yet."""
from urllib.parse import urlparse

import streamlit as st

from astraeon import style, ui

incidents = ui.incidents()
gaps = ui.research_gaps()

style.page_header("Lessons from flight", "Fire changed the mission.",
                  "Different failures, one shared lesson: understand ignition, containment and escape before "
                  "people live with fire risk.")

# --- Incidents ---------------------------------------------------------------------------------------------
if incidents:
    style.timeline([inc.get("date", "")[:4] for inc in incidents])
    for col, inc in zip(st.columns(len(incidents), gap="medium"), incidents):
        with col:
            with ui.card(f"incident_{inc['id']}", height="stretch"):
                style.card_title(inc["name"])
                st.caption(ui.long_date(inc.get("date", "")))
                st.markdown(ui.md(inc.get("summary", "")))
                if inc.get("related_names"):
                    st.caption("RELATED EXPERIMENTS")
                    ui.name_badges(inc["related_names"])
                if inc.get("data_note"):
                    st.caption(ui.md(inc["data_note"]))
                st.space("stretch")
                sources = inc.get("sources", [])
                if sources:
                    links = " · ".join(f"[{urlparse(u).netloc.removeprefix('www.')}]({u})" for u in sources)
                    st.caption(f"Sources: {links}")

# --- Research gaps -----------------------------------------------------------------------------------------
if gaps:
    st.space("medium")
    with st.container(horizontal=True, vertical_alignment="bottom"):
        st.subheader("What we don't know", anchor=False)
        st.space("stretch")
        st.caption("History raises the questions. This data doesn't answer them yet.")
    with st.grid(len(gaps), gap="medium", min_column_width=230):
        for gap in gaps:
            with ui.card(f"gap_{gap['id']}", height="stretch"):
                style.eyebrow("Open question")
                st.markdown(f"**{ui.md(gap['title'])}**")
                st.caption(ui.md(gap.get("summary", "")))
                if gap.get("evidence"):
                    st.caption(ui.md(gap["evidence"]))
                st.space("stretch")
                if gap.get("related_names") and len(gap["related_names"]) <= 4:
                    ui.name_badges(gap["related_names"])
                elif gap.get("related_names"):
                    st.caption(f"{len(gap['related_names'])} related experiments")

style.note("Note", "Incident summaries are written from NASA and other public accounts. The events are separate; "
                   "this timeline is not a common-cause model.")
