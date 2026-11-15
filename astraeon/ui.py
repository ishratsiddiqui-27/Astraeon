"""Streamlit pieces shared by the app pages: cached data, badges, experiment cards and the details dialog.

data.py and charts.py work without Streamlit; this module is the only one in astraeon/ that imports it.
"""
from __future__ import annotations

import csv
import io
from datetime import date

import streamlit as st

from . import charts, data
from .data import MOON_STATUSES, NOT_REPORTED, SCORE_COLUMNS, show

STATUS_ORDER = list(MOON_STATUSES)          # strongest Moon evidence first
TOPIC_LABELS = {"prevention": "Prevention", "detection": "Detection", "suppression": "Suppression"}
TOPIC_ICONS = {"prevention": ":material/local_fire_department:", "detection": ":material/sensors:",
               "suppression": ":material/fire_extinguisher:"}
FUEL_LABELS = {"gas": "Gas", "liquid": "Liquid", "solid": "Solid", "": "Not reported"}
STUDY_LABELS = {"flight": "Flight experiment", "modeling": "Modeling study", "ground": "Ground study"}


# --- Cached data (files only change on a new deploy) ---------------------------------------------------
@st.cache_data
def experiments() -> list[dict]:
    """One dict per experiment, strongest Moon evidence first, then by Moon score."""
    records = data.load_all_records()
    rank = {s: i for i, s in enumerate(STATUS_ORDER)}
    return sorted(records, key=lambda r: (rank.get(r["moon_status"], len(rank)), -(r["score_moon"] or 0),
                                          r["short_name"].lower()))


@st.cache_data
def raw_investigations() -> dict[str, dict]:
    """investigations.csv exactly as stored (all text), by id. Used for CSV downloads."""
    return {r["id"]: r for r in data._read_csv("investigations.csv")}


@st.cache_data
def moon_tests() -> list[dict]:
    return data.load_moon_tests()


@st.cache_data
def incidents() -> list[dict]:
    return data.load_incidents()


@st.cache_data
def research_gaps() -> list[dict]:
    return data.load_research_gaps()


@st.cache_data
def glossary() -> dict:
    return data.load_glossary()


@st.cache_data
def atmospheres() -> list[dict]:
    return data.load_atmospheres()


@st.cache_data
def moon_chart(selected: tuple[float, float] | None = None) -> dict:
    return charts.moon_chart(selected=selected)


@st.cache_data
def tests_near(o2_percent: float, pressure_psi: float) -> dict:
    return data.tests_near(o2_percent, pressure_psi)


# --- Text helpers ---------------------------------------------------------------------------------------
_MD_SPECIAL = "\\`*_[]<>#|~$"


def md(text) -> str:
    """Escape a data value for st.markdown, and show blanks as a muted 'Not reported'."""
    value = show(text)
    if value == NOT_REPORTED:
        return f":gray[*{NOT_REPORTED}*]"
    return "".join("\\" + ch if ch in _MD_SPECIAL else ch for ch in value)


def long_date(iso: str) -> str:
    """'1997-02-24' -> 'February 24, 1997'. Returns the text unchanged if it isn't a date."""
    try:
        d = date.fromisoformat(iso)
    except (TypeError, ValueError):
        return iso
    return f"{d:%B} {d.day}, {d.year}"


def date_range(rec: dict) -> str:
    start, end = rec.get("investigation_start", ""), rec.get("investigation_end", "")
    if start and end:
        return f"{long_date(start)} to {long_date(end)}"
    return long_date(start) if start else NOT_REPORTED


def score_text(value) -> str:
    return NOT_REPORTED if value is None else f"{value}/10"


def csv_bytes(rows: list[dict]) -> bytes:
    """Rows -> CSV file contents (UTF-8 with BOM so Excel opens it correctly)."""
    if not rows:
        return b""
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8-sig")


def status_badge_md(rec: dict) -> str:
    """Inline Markdown badge for st.markdown / st.table cells."""
    return f":{rec['moon_status_color']}-badge[{rec['moon_status_label']}]"


# --- Small UI pieces ------------------------------------------------------------------------------------
def badges(rec: dict, show_fuel: bool = True) -> None:
    """Topic, fuel and Moon-status badges in one row."""
    with st.container(horizontal=True, gap="small"):
        topic = rec["topic"]
        st.badge(TOPIC_LABELS.get(topic, topic or NOT_REPORTED), icon=TOPIC_ICONS.get(topic), color="gray")
        if show_fuel:
            st.badge(f"Fuel: {FUEL_LABELS.get(rec['fuel_type'], rec['fuel_type'])}", color="gray")
        st.badge(rec["moon_status_label"], color=rec["moon_status_color"])


def name_badges(names: list[str]) -> None:
    """A row of gray badges, e.g. related experiments."""
    if names:
        with st.container(horizontal=True, gap="small"):
            for name in names:
                st.badge(name, color="gray")


def experiment_card(rec: dict, key_prefix: str) -> None:
    """Bordered card with the essentials and a Details button that opens the full record."""
    with st.container(border=True, height="stretch"):
        badges(rec)
        st.subheader(rec["short_name"], anchor=False)
        st.caption(md(rec["moon_takeaway"]))
        st.markdown(f"**Oxygen:** {md(rec['o2_percent'])}  \n**Pressure:** {md(rec['pressure_psi'])}")
        st.space("stretch")
        if st.button("Details", key=f"{key_prefix}_details_{rec['id']}", icon=":material/open_in_full:",
                     width="stretch"):
            experiment_details(rec)


@st.dialog("Experiment details", width="large")
def experiment_details(rec: dict) -> None:
    st.subheader(rec["short_name"], anchor=False)
    st.caption(md(rec["name"]))
    badges(rec)
    if rec["image_file"]:
        credit = " · ".join(part for part in (rec["image_credit"], rec["image_license"]) if part)
        st.image(rec["image_file"], caption=credit, alt=f"Photo from {rec['short_name']}", width="stretch")

    st.markdown(md(rec["simple_summary"]))
    st.markdown("**Why it matters**")
    st.markdown(md(rec["why_it_matters"]))

    with st.container(border=True):
        st.markdown(f"**Moon-base evidence** :{rec['evidence_color']}-badge[{rec['evidence_label']}]")
        st.caption(md(rec["evidence_detail"] or rec["moon_takeaway"]))

    varied, same = st.columns(2)
    with varied:
        st.markdown("**What was varied**")
        st.markdown(md(rec["what_varied"]))
    with same:
        st.markdown("**What stayed the same**")
        st.markdown(md(rec["what_same"]))

    st.table(
        {
            ":material/science: Study type": md(STUDY_LABELS.get(rec["study_type"], rec["study_type"])),
            ":material/build: Hardware": md(rec["hardware"]),
            ":material/local_fire_department: Fuel": md(rec["fuel_detail"]),
            ":material/air: Oxygen": md(rec["o2_percent"]),
            ":material/compress: Pressure": md(rec["pressure_psi"]),
            ":material/wind_power: Airflow": md(rec["airflow"]),
            ":material/public: Gravity": md(rec["gravity"]),
            ":material/sensors: Sensors": md(rec["sensors"]),
            ":material/rocket_launch: Flight platform": md(rec["flight_platform"]),
            ":material/calendar_today: Investigation dates": md(date_range(rec)),
        },
        border="horizontal",
        alt=f"Key facts for {rec['short_name']}",
    )

    st.markdown("**Relevance scores** (0 to 10)")
    with st.container(horizontal=True):
        for label, column in SCORE_COLUMNS.items():
            st.metric(label, score_text(rec[column]), border=True)
    if rec["reason"]:
        st.caption(md(rec["reason"]))

    with st.container(horizontal=True):
        if rec["source_link"]:
            st.link_button("Open on NASA PSI", rec["source_link"], icon=":material/open_in_new:")
        raw = raw_investigations().get(rec["id"])
        if raw:
            st.download_button("Download CSV", csv_bytes([raw]), file_name=f"astraeon_{rec['id']}.csv",
                               mime="text/csv", icon=":material/download:", on_click="ignore",
                               key=f"download_{rec['id']}")
