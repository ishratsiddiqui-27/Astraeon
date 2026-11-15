"""About: what Astraeon is, the evidence policy, the source register, how the data was checked, and the glossary.

Person 3 writes data/about.md (Earth applications, team, how we used AI). When that file exists it is shown in
"From the team"; everything else on this page is built from the data files.
"""
from urllib.parse import urlparse

import streamlit as st

from astraeon import style, ui
from astraeon.data import DATA_DIR, MOON_O2_MIN, MOON_PSI_MAX, NOT_REPORTED, show

records = ui.experiments()
tests = ui.moon_tests()
zone = [t for t in tests if t["in_zone"]]
neither = sum(1 for r in records if show(r["o2_percent"]) == NOT_REPORTED and show(r["pressure_psi"]) == NOT_REPORTED)
about = DATA_DIR / "about.md"

intro_col, policy_col = st.columns([1.3, 1], gap="large")
with intro_col:
    style.page_header("About Astraeon", "A clearer view of fire. Beyond Earth.",
                      f"Astraeon brings {len(records)} NASA microgravity combustion experiments into one view for "
                      "spacecraft and lunar-habitat questions. Its purpose is to show the evidence, and to make its "
                      "limits visible.")
    st.markdown(f"The NASA Space Apps challenge brief expects a Moon base to run at {MOON_O2_MIN:g}% oxygen or more "
                f"and {MOON_PSI_MAX:g} psi or less, to shorten prebreathe time before spacewalks. Astraeon checks "
                "which experiments actually tested fire there, test by test.")
    style.note("Research, not certification", "This dashboard doesn't replace mission-specific testing, "
                                               "engineering judgment or operational safety requirements.")
with policy_col:
    with ui.card("about_policy", kind="cardaccent"):
        style.card_title("The evidence policy")
        st.markdown("**Keep claims traceable**")
        st.caption("Experiment values come from NASA PSI pages and experiment tables, incidents cite their "
                   "sources, and every AI answer lists the passages it used.")
        st.markdown("**Keep missing data visible**")
        st.caption("Unknown is not zero. Not reported is not safe.")
        st.markdown("**Keep comparisons honest**")
        st.caption("Every score has a written rubric, and the Moon-base check goes test by test, not by ranges.")

if about.exists():
    with ui.card("about_team"):
        style.card_title("From the team")
        st.markdown(about.read_text(encoding="utf-8"))

# --- Source register ---------------------------------------------------------------------------------------
st.subheader("Source register", anchor=False)
sources = [("NASA Physical Sciences Informatics (PSI)", f"{len(records)} combustion investigations and their "
            "experiment tables", "https://psi.nasa.gov")]
for inc in ui.incidents():
    for url in inc.get("sources", []):
        sources.append((inc["name"], urlparse(url).netloc.removeprefix("www."), url))
sources.append(("NASA Space Apps challenge brief", f"Moon-base atmosphere: {MOON_O2_MIN:g}% oxygen or more, "
                f"{MOON_PSI_MAX:g} psi or less", ""))
with st.grid(2, gap="small", min_column_width=280):
    for i, (title, detail, url) in enumerate(sources):
        with ui.card(f"about_src_{i}", height="stretch"):
            st.markdown(f"**[{ui.md(title)}]({url})** :material/north_east:" if url else f"**{ui.md(title)}**")
            st.caption(ui.md(detail))

style.note("Project scope", f"{len(records)} experiments · {len(tests)} flight tests with oxygen and pressure · "
                            f"{len(zone)} in the Moon-base zone · {neither} report no oxygen or pressure")

# --- How the data was checked, all sources, glossary --------------------------------------------------------
st.subheader("How the data was checked", anchor=False)
tested = sorted({r["short_name"] for r in records if r["id"] in {t["id"] for t in tests}})
st.markdown(
    "- Every value comes from the experiment's NASA PSI page or its experiment table. A blank means the source "
    "doesn't report it, never zero.\n"
    f"- The Moon-base check goes test by test: {len(tests)} flight tests from {len(tested)} experiments "
    f"({', '.join(tested)}) record chamber oxygen and pressure for each test.\n"
    "- `validate_csv.py` checks every data file before each push: ids match across files, values are allowed, and "
    "numbers in the summaries trace back to the data.\n"
    "- Photos are shown only where PSI states a license (CC0-1.0)."
)
with st.expander(f"All {len(records)} experiments on NASA PSI", icon=":material/open_in_new:"):
    for rec in sorted(records, key=lambda r: r["short_name"].lower()):
        if rec["source_link"]:
            st.markdown(f"- [{ui.md(rec['short_name'])}]({rec['source_link']}): {ui.md(rec['name'])}")
glossary = ui.glossary()
if glossary:
    with st.expander(f"Glossary ({len(glossary)} terms)", icon=":material/menu_book:"):
        st.table({term: ui.md(definition) for term, definition in glossary.items()}, border="horizontal",
                 alt="Glossary of fire-science terms used in the app")
