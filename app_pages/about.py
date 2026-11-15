"""About: what Astraeon is, data sources, how the data was checked, and the glossary.

Person 3 writes data/about.md (what Astraeon is, Earth applications, team, how we used AI). When that file
exists it is shown at the top of this page; the data sections below are built from the data files.
"""
import streamlit as st

from astraeon import ui
from astraeon.data import DATA_DIR, MOON_O2_MIN, MOON_PSI_MAX

records = ui.experiments()
tests = ui.moon_tests()
about = DATA_DIR / "about.md"

st.title("About Astraeon", anchor=False)

if about.exists():
    st.markdown(about.read_text(encoding="utf-8"))
else:
    st.markdown(
        f"Astraeon summarizes {len(records)} NASA microgravity combustion experiments from the Physical Sciences "
        "Informatics (PSI) database, ranks them for four settings, and checks which ones tested fire at Moon-base "
        f"air: {MOON_O2_MIN:g}% oxygen or more at {MOON_PSI_MAX:g} psi or less, the conditions in the NASA Space "
        "Apps challenge brief."
    )

st.subheader("How the data was checked", anchor=False, icon=":material/fact_check:")
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

st.subheader("Data sources", anchor=False, icon=":material/database:")
with st.expander(f"All {len(records)} experiments on NASA PSI", icon=":material/open_in_new:"):
    for rec in sorted(records, key=lambda r: r["short_name"].lower()):
        if rec["source_link"]:
            st.markdown(f"- [{ui.md(rec['short_name'])}]({rec['source_link']}): {ui.md(rec['name'])}")

glossary = ui.glossary()
if glossary:
    with st.expander(f"Glossary ({len(glossary)} terms)", icon=":material/menu_book:"):
        st.table({term: ui.md(definition) for term, definition in glossary.items()}, border="horizontal",
                 alt="Glossary of fire-science terms used in the app")
