"""Streamlit pieces shared by the app pages: cached data, badges, cards and the experiment details dialog.

data.py, charts.py and rag.py work without Streamlit; this module and style.py are the only ones in astraeon/
that import it.
"""
from __future__ import annotations

import csv
import io
from datetime import date

import streamlit as st

from . import charts, data, style
from .data import MOON_STATUSES, NOT_REPORTED, SCORE_COLUMNS, show

STATUS_ORDER = list(MOON_STATUSES)          # strongest Moon evidence first
TOPIC_LABELS = {"prevention": "Prevention", "detection": "Detection", "suppression": "Suppression"}
TOPIC_ICONS = {"prevention": ":material/local_fire_department:", "detection": ":material/sensors:",
               "suppression": ":material/fire_extinguisher:"}
FUEL_LABELS = {"gas": "Gas", "liquid": "Liquid", "solid": "Solid", "": "Not reported"}
STUDY_LABELS = {"flight": "Flight experiment", "modeling": "Modeling study", "ground": "Ground study"}
COMPARE_KEY = "compare_ids"
MAX_COMPARE = 3


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


def first_sentence(text: str, limit: int = 170) -> str:
    text = (text or "").strip()
    cut = text.find(". ")
    sentence = text if cut == -1 else text[:cut + 1]
    return sentence if len(sentence) <= limit else sentence[:limit].rsplit(" ", 1)[0] + "…"


def subtitle(rec: dict) -> str:
    """Full name without the acronym in brackets: 'Cool Flames Investigation with Gases'."""
    name = rec["name"]
    if name.endswith(")") and "(" in name:
        name = name[:name.rfind("(")].strip()
    return name.split(" / ")[-1].strip() if " / " in name else name


def psi_id(rec: dict) -> str:
    link = rec.get("source_link") or ""
    return link.rstrip("/").rsplit("/", 1)[-1] if link else ""


def test_summary(rec_id: str) -> str:
    """Per-test records in PSI for one experiment, in one line."""
    runs = [t for t in moon_tests() if t["id"] == rec_id]
    if not runs:
        return "No per-test oxygen and pressure records in PSI"
    zone = [t for t in runs if t["in_zone"]]
    hot = sum(1 for t in zone if t["outcome"].startswith("Hot ignition: Yes"))
    text = f"{len(runs)} flight tests with oxygen and pressure; {len(zone)} in the Moon-base zone"
    return text + (f", {hot} with hot ignition" if zone else "")


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
def card(key: str, kind: str = "card", height: str | int = "content"):
    """A glass card: a keyed container styled by astraeon/style.py. kind: card, cardaccent or carddashed."""
    return st.container(key=f"{kind}_{key}", height=height)


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


def compare_ids() -> list[str]:
    return list(st.session_state.get(COMPARE_KEY, []))


def add_to_compare(rec_id: str) -> None:
    ids = [i for i in compare_ids() if i != rec_id]
    st.session_state[COMPARE_KEY] = (ids + [rec_id])[-MAX_COMPARE:]


def experiment_card(rec: dict, key_prefix: str) -> None:
    """Library card: badges, name, full name, one-line summary, Details link and PSI id."""
    with card(f"{key_prefix}_{rec['id']}", height="stretch"):
        badges(rec, show_fuel=False)
        st.markdown(f"#### {md(rec['short_name'])}")
        st.caption(md(subtitle(rec)))
        st.markdown(md(first_sentence(rec["simple_summary"])))
        st.space("stretch")
        with st.container(horizontal=True, vertical_alignment="center"):
            if st.button("View details", key=f"{key_prefix}_details_{rec['id']}", icon=":material/north_east:",
                         icon_position="right", type="tertiary"):
                experiment_details(rec)
            st.space("stretch")
            st.caption(f"NASA · {psi_id(rec)}")


@st.dialog("Experiment details", width="large")
def experiment_details(rec: dict) -> None:
    style.eyebrow(f"Experiment details / NASA {psi_id(rec)}")
    st.subheader(rec["short_name"], anchor=False)
    st.caption(md(subtitle(rec)))
    badges(rec)
    if rec["image_file"]:
        credit = " · ".join(part for part in (rec["image_credit"], rec["image_license"]) if part)
        st.image(rec["image_file"], caption=credit, alt=f"Photo from {rec['short_name']}", width="stretch")

    st.markdown("**The research question**")
    st.markdown(md(rec["objective"]))
    st.markdown("**In plain words**")
    st.markdown(md(rec["simple_summary"]))

    with card(f"dialog_facts_{rec['id']}"):
        pressure_col, oxygen_col, tests_col = st.columns(3)
        with pressure_col:
            st.caption("PRESSURE")
            st.markdown(md(rec["pressure_psi"]))
        with oxygen_col:
            st.caption("OXYGEN")
            st.markdown(md(rec["o2_percent"]))
        with tests_col:
            st.caption("FLIGHT-TEST RECORDS")
            st.markdown(md(test_summary(rec["id"])))

    with card(f"dialog_moon_{rec['id']}", kind="cardaccent"):
        style.eyebrow("Moon-base evidence")
        st.markdown(f":{rec['evidence_color']}-badge[{rec['evidence_label']}]")
        st.markdown(md(rec["moon_takeaway"] or rec["evidence_detail"]))
        if rec["evidence_detail"]:
            st.caption(md(rec["evidence_detail"]))

    st.markdown("**Why it matters**")
    st.markdown(md(rec["why_it_matters"]))
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
            ":material/air: Airflow": md(rec["airflow"]),
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

    with st.container(horizontal=True, vertical_alignment="center"):
        if st.button("Add to comparison", key=f"ctaprimary_compare_{rec['id']}", icon=":material/add:"):
            add_to_compare(rec["id"])
            st.switch_page("app_pages/compare.py")
        if rec["source_link"]:
            st.link_button("Open on NASA PSI", rec["source_link"], icon=":material/open_in_new:")
        raw = raw_investigations().get(rec["id"])
        if raw:
            st.download_button("Download CSV", csv_bytes([raw]), file_name=f"astraeon_{rec['id']}.csv",
                               mime="text/csv", icon=":material/download:", on_click="ignore",
                               key=f"download_{rec['id']}")
        st.space("stretch")
        if st.button("Close", key=f"close_{rec['id']}", type="tertiary"):
            st.rerun()
