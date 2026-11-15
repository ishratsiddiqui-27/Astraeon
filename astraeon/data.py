"""Load every data file once, joined by experiment id, with blanks handled the same way everywhere.

Use it in a Streamlit page:

    import streamlit as st
    from astraeon.data import load_all, show, SCORE_COLUMNS

    @st.cache_data
    def get_experiments():
        return load_all()          # pandas DataFrame, one row per experiment (24 rows)

    df = get_experiments()
    row = df[df["id"] == "acme_cfig"].iloc[0]
    st.write("Pressure:", show(row["pressure_psi"]))   # prints "Not reported" when blank

load_all() and load_moon_tests_df() return pandas DataFrames. Every other loader returns plain
Python lists or dicts, so this file also works where pandas can't be installed.
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

NOT_REPORTED = "Not reported"
MOON_O2_MIN = 30.0      # percent, challenge brief: "30% or more"
MOON_PSI_MAX = 10.2     # psi, challenge brief: "10.2 psi or less"
MOON_NOTE = ("PSI has no partial-gravity data, so Moon relevance is inferred from oxygen and pressure. "
             "Only ACME CFI-G recorded flames at Moon-base conditions test by test.")

# Dropdown label -> column in rankings.csv
SCORE_COLUMNS = {
    "Spacecraft": "score_spacecraft",
    "Space station": "score_station",
    "Moon base": "score_moon",
    "Rover": "score_rover",
}

# Person 3's moon_status in summaries.json: the badge on each card. Colours are st.badge colour names:
#   st.badge(row["moon_status_label"], color=row["moon_status_color"])
MOON_STATUSES = {
    "confirmed": {"label": "Confirmed match", "color": "blue"},
    "near_miss": {"label": "Near miss", "color": "orange"},
    "unconfirmed": {"label": "Unconfirmed", "color": "gray"},
    "not_a_match": {"label": "Not a match", "color": "gray"},
    "cannot_check": {"label": "Can't check: not reported", "color": "gray"},
    "not_applicable": {"label": "Not a fire test", "color": "gray"},
}

# data/moon_evidence.csv levels (more detailed than moon_status), strongest evidence first.
EVIDENCE_LEVELS = {
    "confirmed": {"label": "Confirmed at Moon-base conditions", "color": "blue"},
    "near_miss": {"label": "Near miss", "color": "orange"},
    "unconfirmed": {"label": "Not confirmed", "color": "gray"},
    "high_oxygen_normal_pressure": {"label": "High oxygen, normal pressure only", "color": "gray"},
    "below_moon_oxygen": {"label": "Oxygen below Moon-base levels", "color": "gray"},
    "not_reported": {"label": "Oxygen not reported", "color": "gray"},
    "not_a_fire_test": {"label": "Not a fire test", "color": "gray"},
}


def show(value, unit: str = "") -> str:
    """Text for display: 'Not reported' for blanks, None and NaN; otherwise the value (+ unit)."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return NOT_REPORTED
    text = str(value).strip()
    if not text or text.lower() in ("nan", "<na>", "none"):
        return NOT_REPORTED
    return f"{text}{unit}"


def short_name(name: str, source_link: str = "") -> str:
    """Card-sized name: the acronym in the last brackets ('... (ACME CFI-G)' -> 'ACME CFI-G'),
    else the PSI number from the source link ('PSI-117')."""
    name = (name or "").strip()
    if name.endswith(")") and "(" in name:
        return name[name.rfind("(") + 1:-1].strip()
    return source_link.rstrip("/").rsplit("/", 1)[-1] if source_link else name


def _read_csv(file_name: str, required: bool = True) -> list[dict]:
    path = DATA_DIR / file_name
    if not path.exists():
        if required:
            raise FileNotFoundError(f"{path} is missing")
        return []
    with open(path, encoding="utf-8-sig", newline="") as f:
        return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def _number(text):
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def load_investigations() -> list[dict]:
    """data/investigations.csv. o2_min and o2_max become numbers (None when blank)."""
    rows = _read_csv("investigations.csv")
    for r in rows:
        r["o2_min"], r["o2_max"] = _number(r["o2_min"]), _number(r["o2_max"])
    return rows


def load_rankings() -> list[dict]:
    """data/rankings.csv. Scores become whole numbers."""
    rows = _read_csv("rankings.csv", required=False)
    for r in rows:
        for col in SCORE_COLUMNS.values():
            r[col] = int(r[col]) if r.get(col, "").isdigit() else None
    return rows


def load_summaries() -> dict:
    """data/summaries.json: {id: {simple_summary, why_it_matters, ...}}."""
    path = DATA_DIR / "summaries.json"
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_moon_tests() -> list[dict]:
    """data/moon_tests.csv: one row per flight test. Adds in_zone (True/False)."""
    rows = _read_csv("moon_tests.csv", required=False)
    for r in rows:
        r["o2_percent"], r["pressure_psi"] = _number(r["o2_percent"]), _number(r["pressure_psi"])
        r["in_zone"] = r["in_moon_zone"] == "yes"
    return rows


def load_moon_evidence() -> list[dict]:
    """data/moon_evidence.csv. Adds evidence_label and evidence_color."""
    rows = _read_csv("moon_evidence.csv", required=False)
    for r in rows:
        level = EVIDENCE_LEVELS.get(r["evidence_level"], {})
        r["evidence_label"] = level.get("label", r["evidence_level"])
        r["evidence_color"] = level.get("color", "gray")
    return rows


def load_images() -> list[dict]:
    """data/images.csv. Adds image_file (full path for st.image); skips images whose file is missing."""
    rows = []
    for r in _read_csv("images.csv", required=False):
        path = ROOT / r["image_path"]
        if path.exists():
            r["image_file"] = str(path)
            rows.append(r)
    return rows


def load_timeline() -> list[dict]:
    """data/timeline.csv: investigation start/end dates as YYYY-MM-DD ('' when PSI lists none)."""
    return _read_csv("timeline.csv", required=False)


def load_glossary() -> dict:
    """data/glossary.json: {term: plain-language definition}. Empty if the file doesn't exist yet."""
    path = DATA_DIR / "glossary.json"
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_atmospheres() -> list[dict]:
    """data/atmospheres.json: preset atmospheres (id, name, o2_percent, pressure_psi, note, source)."""
    path = DATA_DIR / "atmospheres.json"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return [{"id": key, **value} for key, value in json.load(f).items()]


def tests_near(o2_percent: float, pressure_psi: float, o2_tol: float = 3.0, psi_tol: float = 1.5,
               closest: int = 10) -> dict:
    """Flight tests from data/moon_tests.csv that ran near a given atmosphere.

    "Near" = within +/- o2_tol percentage points of oxygen AND +/- psi_tol psi (a box around the point).
    Returns a dict:
      within         tests inside the box, closest first
      closest        the `closest` nearest tests, even when none are inside the box
      by_experiment  {experiment short name: number of tests inside the box}
    Each test gets `experiment` (short name) and `distance` (0 = exact match, 1 = edge of the box).
    Only 4 experiments record oxygen and pressure per test, so "no tests" means "not tested in PSI's
    per-test records", not "safe".
    """
    names = {r["id"]: short_name(r["name"], r["source_link"]) for r in load_investigations()}
    scored = []
    for t in load_moon_tests():
        distance = max(abs(t["o2_percent"] - o2_percent) / o2_tol, abs(t["pressure_psi"] - pressure_psi) / psi_tol)
        scored.append({**t, "experiment": names.get(t["id"], t["id"]), "distance": round(distance, 3)})
    scored.sort(key=lambda t: t["distance"])
    within = [t for t in scored if t["distance"] <= 1]
    by_experiment = {}
    for t in within:
        by_experiment[t["experiment"]] = by_experiment.get(t["experiment"], 0) + 1
    return {"within": within, "closest": scored[:closest], "by_experiment": by_experiment,
            "o2_tol": o2_tol, "psi_tol": psi_tol}


def load_research_gaps() -> list[dict]:
    """data/research_gaps.json (Person 3): what the data can't tell us yet. Each gap gets its id and
    related_names (card-sized names of its related experiments). Empty if the file doesn't exist."""
    path = DATA_DIR / "research_gaps.json"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    names = {r["id"]: short_name(r["name"], r["source_link"]) for r in load_investigations()}
    return [{"id": key, **gap, "related_names": [names.get(rid, rid) for rid in gap.get("related_experiments", [])]}
            for key, gap in data.items()]


def load_incidents() -> list[dict]:
    """data/incident_summaries.json (Person 3) as a list, oldest first. Each incident gets its id and
    related_names (card-sized names of its related experiments). Empty if the file doesn't exist."""
    path = DATA_DIR / "incident_summaries.json"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    names = {r["id"]: short_name(r["name"], r["source_link"]) for r in load_investigations()}
    incidents = []
    for key, entry in data.items():
        item = {"id": key, **entry}
        item["related_names"] = [names.get(rid, rid) for rid in entry.get("related_experiments", [])]
        incidents.append(item)
    return sorted(incidents, key=lambda i: i.get("date", ""))


def load_all_records() -> list[dict]:
    """One dict per experiment: investigations + rankings + summaries + Moon evidence + timeline
    + primary image. Missing optional files leave their fields blank instead of failing."""
    rankings = {r["id"]: r for r in load_rankings()}
    summaries = load_summaries()
    evidence = {r["id"]: r for r in load_moon_evidence()}
    timeline = {r["id"]: r for r in load_timeline()}
    images = {r["id"]: r for r in load_images() if r["is_primary"] == "yes"}

    records = []
    for inv in load_investigations():
        rid = inv["id"]
        rec = dict(inv)
        rec["short_name"] = short_name(inv["name"], inv["source_link"])

        rank = rankings.get(rid, {})
        for col in SCORE_COLUMNS.values():
            rec[col] = rank.get(col)
        rec["reason"] = rank.get("reason", "")

        summary = summaries.get(rid, {})
        rec["simple_summary"] = summary.get("simple_summary", "")
        rec["why_it_matters"] = summary.get("why_it_matters", "")
        rec["moon_status"] = summary.get("moon_status", "cannot_check")
        rec["moon_takeaway"] = summary.get("moon_takeaway", "")
        status = MOON_STATUSES.get(rec["moon_status"], MOON_STATUSES["cannot_check"])
        rec["moon_status_label"], rec["moon_status_color"] = status["label"], status["color"]
        for key, value in summary.items():      # any further fields Person 3 adds later
            rec.setdefault(key, value)

        ev = evidence.get(rid, {})
        rec["evidence_level"] = ev.get("evidence_level", "not_reported")
        rec["evidence_label"] = ev.get("evidence_label", EVIDENCE_LEVELS["not_reported"]["label"])
        rec["evidence_color"] = ev.get("evidence_color", "gray")
        rec["evidence_detail"] = ev.get("evidence_detail", "")

        tl = timeline.get(rid, {})
        for key in ("investigation_start", "investigation_end", "flight_platform"):
            rec[key] = tl.get(key, "")

        img = images.get(rid, {})
        rec["image_file"] = img.get("image_file", "")
        rec["image_credit"] = img.get("credit", "")
        rec["image_license"] = img.get("license", "")
        records.append(rec)
    return records


def load_all():
    """pandas DataFrame of load_all_records(): one row per experiment."""
    import pandas as pd
    return pd.DataFrame(load_all_records())


def load_moon_tests_df():
    """pandas DataFrame of load_moon_tests()."""
    import pandas as pd
    return pd.DataFrame(load_moon_tests())
