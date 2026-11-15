"""Data preview: checks that astraeon/ and data/ work inside Streamlit.

This is a developer check, not the dashboard (the dashboard is Person 4's app).
Run it in GitHub Codespaces (Streamlit is blocked on Person 1's laptop):
    pip install streamlit
    streamlit run preview_data.py
"""
import streamlit as st

from astraeon.charts import MOON_CHART_ALT, moon_chart
from astraeon.data import MOON_NOTE, load_all, load_glossary, show

st.set_page_config(page_title="Astraeon data preview", page_icon=":material/local_fire_department:", layout="wide")


@st.cache_data
def get_experiments():
    return load_all()


df = get_experiments()

st.title("Astraeon data preview")
st.caption("Developer check of astraeon/ and data/. The real dashboard is Person 4's app.")

st.vega_lite_chart(moon_chart(), alt=MOON_CHART_ALT)
st.caption(MOON_NOTE)

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
