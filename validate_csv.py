"""Check the team's data files before pushing.

Run from the project root:
    python validate_csv.py

ERRORS (exit code 1): structural problems that would break the dashboard, such as
wrong columns, ids that don't match across files, or scores outside 0-10.
WARNINGS (exit code 0): wording a person should look at, such as numbers in summaries or
ranking reasons that aren't in data/investigations.csv, or claims we've already had to
correct once (see data/DATA_NOTES.md sections 5 and 6).
Files that don't exist yet are skipped.
"""
import csv
import json
import os
import re
import sys

INV = os.path.join("data", "investigations.csv")
RANK = os.path.join("data", "rankings.csv")
SUMM = os.path.join("data", "summaries.json")
MOON = os.path.join("data", "moon_tests.csv")
EVIDENCE = os.path.join("data", "moon_evidence.csv")
IMAGES = os.path.join("data", "images.csv")
TIMELINE = os.path.join("data", "timeline.csv")
GLOSSARY = os.path.join("data", "glossary.json")
INCIDENTS = os.path.join("data", "incident_summaries.json")
INCIDENT_FIELDS = ["name", "date", "summary", "related_experiments", "data_note", "sources"]

INV_COLUMNS = ["id", "name", "fuel_type", "fuel_detail", "hardware", "o2_percent", "pressure_psi",
               "airflow", "gravity", "sensors", "objective", "what_varied", "what_same", "topic",
               "source_link", "o2_min", "o2_max", "study_type", "notes"]  # frozen: 19 columns
ALLOWED = {
    "gravity": {"microgravity", "normal gravity"},
    "topic": {"prevention", "detection", "suppression"},
    "study_type": {"flight", "modeling", "ground"},
    "fuel_type": {"solid", "liquid", "gas", ""},
}
RANK_COLUMNS = ["id", "score_spacecraft", "score_station", "score_moon", "score_rover", "reason"]
SUMMARY_FIELDS = ["simple_summary", "why_it_matters", "moon_status", "moon_takeaway"]
# Person 3's moon_status in summaries.json -> the matching levels in data/moon_evidence.csv
MOON_STATUS_TO_EVIDENCE = {
    "confirmed": {"confirmed"},
    "near_miss": {"near_miss"},
    "unconfirmed": {"unconfirmed"},
    "not_a_match": {"high_oxygen_normal_pressure", "below_moon_oxygen"},
    "cannot_check": {"not_reported"},
    "not_applicable": {"not_a_fire_test"},
}
# The Moon-base limits from the challenge brief may appear in any text.
THRESHOLD_NUMBERS = {30.0, 10.2}
MOON_COLUMNS = ["id", "psi_id", "test", "fuel", "o2_percent", "pressure_psi", "pressure_as_published",
                "outcome", "burn_time_s", "in_moon_zone", "source_table"]
EVIDENCE_COLUMNS = ["id", "evidence_level", "evidence_detail"]
EVIDENCE_LEVELS = {"confirmed", "near_miss", "unconfirmed", "high_oxygen_normal_pressure",
                   "below_moon_oxygen", "not_reported", "not_a_fire_test"}
HIGH_O2_LEVELS = {"confirmed", "near_miss", "unconfirmed", "high_oxygen_normal_pressure"}
IMAGE_COLUMNS = ["id", "psi_id", "image_path", "original_file", "is_primary", "license", "credit", "source_page"]
TIMELINE_COLUMNS = ["id", "psi_id", "investigation_start", "investigation_end", "flight_platform", "source_page"]

# A number not glued to letters, so "CO2" or "C2H4" don't count. Accepts ".33".
NUMBER = re.compile(r"(?<![A-Za-z0-9.])(\d+(?:\.\d+)?|\.\d+)")
NEGATION = re.compile(r"\b(not|no|never|isn't|wasn't|doesn't)\b", re.I)

errors, warnings = [], []


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    return rows[0], rows[1:]


def numbers_in(text):
    return {float(n) for n in NUMBER.findall(text or "")}


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text or "") if s.strip()]


def check_investigations():
    header, rows = read_csv(INV)
    if header != INV_COLUMNS:
        errors.append(f"{INV}: columns changed. Expected the 19 frozen columns: {', '.join(INV_COLUMNS)}")
        return {}
    col = {h: i for i, h in enumerate(header)}
    by_id = {}
    for line_no, row in enumerate(rows, start=2):
        if len(row) != len(header):
            errors.append(f"{INV} line {line_no} ({row[0] if row else 'empty'}): {len(row)} fields instead of {len(header)}")
            continue
        rid = row[0]
        if not re.fullmatch(r"[a-z0-9_]+", rid):
            errors.append(f"{INV} line {line_no}: id '{rid}' must be short lowercase (letters, digits, _)")
        if rid in by_id:
            errors.append(f"{INV} line {line_no}: duplicate id '{rid}'")
        for c, allowed in ALLOWED.items():
            if row[col[c]] not in allowed:
                shown = ", ".join(sorted(a or "(blank)" for a in allowed))
                errors.append(f"{INV} line {line_no} ({rid}): {c} is '{row[col[c]]}', must be one of: {shown}")
        by_id[rid] = dict(zip(header, row))
    print(f"  {INV}: {len(rows)} rows, {len(header)} columns")
    return by_id


def check_rankings(inv):
    header, rows = read_csv(RANK)
    if header != RANK_COLUMNS:
        errors.append(f"{RANK}: columns should be {', '.join(RANK_COLUMNS)}")
        return {}
    ids = [r[0] for r in rows]
    compare_ids(RANK, ids, inv)
    out = {}
    for line_no, row in enumerate(rows, start=2):
        if len(row) != len(header):
            errors.append(f"{RANK} line {line_no}: {len(row)} fields instead of {len(header)}")
            continue
        r = dict(zip(header, row))
        for c in RANK_COLUMNS[1:5]:
            if not r[c].strip().isdigit() or not 0 <= int(r[c]) <= 10:
                errors.append(f"{RANK} line {line_no} ({r['id']}): {c} is '{r[c]}', must be a whole number 0-10")
        if not r["reason"].strip():
            errors.append(f"{RANK} line {line_no} ({r['id']}): reason is blank")
        out[r["id"]] = r
    print(f"  {RANK}: {len(rows)} rows")
    return out


def check_summaries(inv):
    try:
        with open(SUMM, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"{SUMM}: not valid JSON ({e})")
        return {}
    compare_ids(SUMM, list(data), inv)
    for rid, entry in data.items():
        for field in SUMMARY_FIELDS:
            if not isinstance(entry, dict) or not str(entry.get(field, "")).strip():
                errors.append(f"{SUMM} ({rid}): '{field}' is missing or blank")
    print(f"  {SUMM}: {len(data)} entries")
    return data


def check_moon_tests(inv):
    """Returns the set of ids that have at least one test inside the Moon-base zone."""
    header, rows = read_csv(MOON)
    if header != MOON_COLUMNS:
        errors.append(f"{MOON}: columns changed; rebuild it with: python build_moon_tests.py")
        return set()
    zone_ids = {row[0] for row in rows if len(row) == len(header) and row[header.index("in_moon_zone")] == "yes"}
    for line_no, row in enumerate(rows, start=2):
        r = dict(zip(header, row))
        if r["id"] not in inv:
            errors.append(f"{MOON} line {line_no}: id '{r['id']}' is not in {INV}")
        try:
            o2, psi = float(r["o2_percent"]), float(r["pressure_psi"])
        except ValueError:
            errors.append(f"{MOON} line {line_no}: o2_percent/pressure_psi must be numbers")
            continue
        zone = "yes" if o2 >= 30 and psi <= 10.2 else "no"
        if r["in_moon_zone"] != zone:
            errors.append(f"{MOON} line {line_no} ({r['id']} {r['test']}): in_moon_zone is '{r['in_moon_zone']}' but O2 {o2}% / {psi} psi gives '{zone}'")
    print(f"  {MOON}: {len(rows)} tests")
    return zone_ids


def check_moon_evidence(inv, zone_ids):
    """Each level must agree with the oxygen in investigations.csv and with moon_tests.csv."""
    header, rows = read_csv(EVIDENCE)
    if header != EVIDENCE_COLUMNS:
        errors.append(f"{EVIDENCE}: columns should be {', '.join(EVIDENCE_COLUMNS)}")
        return {}
    compare_ids(EVIDENCE, [r[0] for r in rows], inv)
    out = {}
    for line_no, row in enumerate(rows, start=2):
        r = dict(zip(header, row))
        rid, level = r["id"], r["evidence_level"]
        out[rid] = r
        if level not in EVIDENCE_LEVELS:
            errors.append(f"{EVIDENCE} line {line_no} ({rid}): level '{level}' must be one of: {', '.join(sorted(EVIDENCE_LEVELS))}")
            continue
        if not r["evidence_detail"].strip():
            errors.append(f"{EVIDENCE} line {line_no} ({rid}): evidence_detail is blank")
        if rid not in inv:
            continue
        o2_max = inv[rid]["o2_max"].strip()
        o2 = float(o2_max) if o2_max else None
        if zone_ids is not None and (level == "confirmed") != (rid in zone_ids):
            errors.append(f"{EVIDENCE} ({rid}): 'confirmed' must match {MOON}: this id "
                          f"{'has' if rid in zone_ids else 'has no'} tests inside the Moon-base zone")
        if level in HIGH_O2_LEVELS and (o2 is None or o2 < 30):
            errors.append(f"{EVIDENCE} ({rid}): level '{level}' needs o2_max of 30 or more in {INV}, found '{o2_max}'")
        if level == "below_moon_oxygen" and (o2 is None or o2 >= 30):
            errors.append(f"{EVIDENCE} ({rid}): 'below_moon_oxygen' needs o2_max below 30 in {INV}, found '{o2_max}'")
        if level in ("not_reported", "not_a_fire_test") and o2 is not None:
            errors.append(f"{EVIDENCE} ({rid}): '{level}' but {INV} reports o2_max {o2_max}")
    print(f"  {EVIDENCE}: {len(rows)} rows")
    return out


def check_moon_status(summaries, evidence, zone_ids):
    """summaries.json moon_status: allowed values, 'confirmed' must match moon_tests.csv (error),
    and it should agree with moon_evidence.csv (warning, since both are judgment calls)."""
    for rid, entry in summaries.items():
        if not isinstance(entry, dict) or "moon_status" not in entry:
            continue
        status = entry["moon_status"]
        if status not in MOON_STATUS_TO_EVIDENCE:
            errors.append(f"{SUMM} ({rid}): moon_status '{status}' must be one of: {', '.join(MOON_STATUS_TO_EVIDENCE)}")
            continue
        if zone_ids is not None and (status == "confirmed") != (rid in zone_ids):
            errors.append(f"{SUMM} ({rid}): moon_status 'confirmed' must match {MOON}: this id "
                          f"{'has' if rid in zone_ids else 'has no'} tests inside the Moon-base zone")
        level = evidence.get(rid, {}).get("evidence_level")
        if level and level not in MOON_STATUS_TO_EVIDENCE[status]:
            warnings.append(f"{SUMM} ({rid}): moon_status '{status}' disagrees with {EVIDENCE} level '{level}' "
                            f"(expected moon_status '{next(s for s, lv in MOON_STATUS_TO_EVIDENCE.items() if level in lv)}'). "
                            f"Agree on one and update the other.")


def check_images(inv):
    header, rows = read_csv(IMAGES)
    if header != IMAGE_COLUMNS:
        errors.append(f"{IMAGES}: columns changed; rebuild it with: python build_psi_extras.py")
        return
    primaries = {}
    for line_no, row in enumerate(rows, start=2):
        r = dict(zip(header, row))
        if r["id"] not in inv:
            errors.append(f"{IMAGES} line {line_no}: id '{r['id']}' is not in {INV}")
        if not os.path.exists(r["image_path"]):
            errors.append(f"{IMAGES} line {line_no} ({r['id']}): file '{r['image_path']}' not found")
        if not r["license"].strip():
            errors.append(f"{IMAGES} line {line_no} ({r['id']}): license is blank; only use images with a stated license")
        if r["is_primary"] not in ("yes", "no"):
            errors.append(f"{IMAGES} line {line_no} ({r['id']}): is_primary must be yes or no")
        primaries[r["id"]] = primaries.get(r["id"], 0) + (r["is_primary"] == "yes")
    for rid, n in primaries.items():
        if n != 1:
            errors.append(f"{IMAGES} ({rid}): needs exactly one is_primary = yes, found {n}")
    print(f"  {IMAGES}: {len(rows)} images for {len(primaries)} experiments")


def check_timeline(inv):
    header, rows = read_csv(TIMELINE)
    if header != TIMELINE_COLUMNS:
        errors.append(f"{TIMELINE}: columns changed; rebuild it with: python build_psi_extras.py")
        return
    compare_ids(TIMELINE, [r[0] for r in rows], inv)
    for line_no, row in enumerate(rows, start=2):
        r = dict(zip(header, row))
        dates = {}
        for c in ("investigation_start", "investigation_end"):
            if r[c] and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", r[c]):
                errors.append(f"{TIMELINE} line {line_no} ({r['id']}): {c} '{r[c]}' must be YYYY-MM-DD or blank")
            dates[c] = r[c]
        if dates["investigation_start"] and dates["investigation_end"] and dates["investigation_start"] > dates["investigation_end"]:
            errors.append(f"{TIMELINE} line {line_no} ({r['id']}): start date is after end date")
    print(f"  {TIMELINE}: {len(rows)} rows")


def check_incidents(inv):
    """data/incident_summaries.json: {incident_id: {name, date, summary, related_experiments, data_note, sources}}."""
    try:
        with open(INCIDENTS, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"{INCIDENTS}: not valid JSON ({e})")
        return
    if not isinstance(data, dict):
        errors.append(f"{INCIDENTS}: should be an object keyed by incident id")
        return
    for key, entry in data.items():
        where = f"{INCIDENTS} ({key})"
        if not isinstance(entry, dict):
            errors.append(f"{where}: should be an object with {', '.join(INCIDENT_FIELDS)}")
            continue
        missing = [f for f in INCIDENT_FIELDS if f not in entry]
        if missing:
            errors.append(f"{where}: missing {', '.join(missing)}")
            continue
        for field in ("name", "summary", "data_note"):
            if not isinstance(entry[field], str) or not entry[field].strip():
                errors.append(f"{where}: '{field}' is blank")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(entry["date"])):
            errors.append(f"{where}: date '{entry['date']}' must be YYYY-MM-DD")
        related = entry["related_experiments"]
        if not isinstance(related, list):
            errors.append(f"{where}: related_experiments must be a list of ids (it can be empty)")
        else:
            unknown = [rid for rid in related if rid not in inv]
            if unknown:
                errors.append(f"{where}: related_experiments not in {INV}: {', '.join(map(str, unknown))}")
        sources = entry["sources"]
        if not isinstance(sources, list) or not sources or not all(str(s).startswith("http") for s in sources):
            errors.append(f"{where}: sources must be a non-empty list of links")
        for s in sentences(str(entry.get("summary", "")) + " " + str(entry.get("data_note", ""))):
            if re.search(r"partial[- ]gravity", s, re.I) and not NEGATION.search(s):
                warnings.append(f"{where}: no PSI experiment ran in partial gravity: \"{s[:140]}\"")
    print(f"  {INCIDENTS}: {len(data)} incidents")


def check_glossary():
    try:
        with open(GLOSSARY, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"{GLOSSARY}: not valid JSON ({e})")
        return
    if not isinstance(data, dict):
        errors.append(f'{GLOSSARY}: should be an object like {{"cool flame": "A flame that burns at ..."}}')
        return
    for term, definition in data.items():
        if not str(term).strip() or not isinstance(definition, str) or not definition.strip():
            errors.append(f"{GLOSSARY}: term '{term}' needs a non-empty text definition")
    print(f"  {GLOSSARY}: {len(data)} terms")


def compare_ids(path, ids, inv):
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    missing = sorted(set(inv) - set(ids))
    extra = sorted(set(ids) - set(inv))
    if dupes:
        errors.append(f"{path}: duplicate ids: {', '.join(dupes)}")
    if missing:
        errors.append(f"{path}: missing ids that are in {INV}: {', '.join(missing)}")
    if extra:
        errors.append(f"{path}: ids not in {INV}: {', '.join(extra)}")


def check_wording(where, rid, text, inv_row):
    """Warn about numbers not in the CSV row, and about claims already corrected once."""
    row_numbers = numbers_in(" ".join(inv_row.values())) | THRESHOLD_NUMBERS
    for s in sentences(text):
        quote = s if len(s) <= 140 else s[:137] + "..."
        missing = sorted(numbers_in(s) - row_numbers)
        if missing:
            shown = ", ".join(f"{n:g}" for n in missing)
            warnings.append(f"{where} ({rid}): number(s) {shown} not in the {INV} row: \"{quote}\"")
        low = s.lower()
        if re.search(r"partial[- ]gravity", low) and not NEGATION.search(s):
            warnings.append(f"{where} ({rid}): no PSI experiment ran in partial gravity, and acme_efield is not a "
                            f"partial-gravity test (DATA_NOTES section 5): \"{quote}\"")
        if re.search(r"\b85\s*%", s) and "burner" not in low:
            warnings.append(f"{where} ({rid}): 85% oxygen was burner flow, not chamber air; say 'burner': \"{quote}\"")
        if rid == "acme_cfig" and "moon" in low and re.search(r"\bnear\b", low):
            warnings.append(f"{where} ({rid}): CFI-G ran AT Moon-base conditions; 'near' describes FLEX, "
                            f"so it would make 'only' untrue: \"{quote}\"")
        if "moon-base atmospher" in low:
            warnings.append(f"{where} ({rid}): PSI calls these planned exploration atmospheres, not Moon-base "
                            f"atmospheres, and per-test pressure is unconfirmed: \"{quote}\"")
        if rid == "acme_flamedesign" and "6.2" in s and "40%" in s and "1 atm" not in low:
            warnings.append(f"{where} ({rid}): chamber O2 reached 40% only at ~1 atm; the 6.2 psi tests were "
                            f"inverse flames. Give each flame type its own pressure: \"{quote}\"")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    if not os.path.exists(INV):
        sys.exit(f"Error: '{INV}' not found. Run this from the project root.")
    print("Checking files:")
    inv = check_investigations()
    rankings = check_rankings(inv) if os.path.exists(RANK) and inv else {}
    summaries = check_summaries(inv) if os.path.exists(SUMM) and inv else {}
    zone_ids = check_moon_tests(inv) if os.path.exists(MOON) and inv else None
    evidence = check_moon_evidence(inv, zone_ids) if os.path.exists(EVIDENCE) and inv else {}
    if summaries:
        check_moon_status(summaries, evidence, zone_ids)
    if os.path.exists(IMAGES) and inv:
        check_images(inv)
    if os.path.exists(TIMELINE) and inv:
        check_timeline(inv)
    if os.path.exists(GLOSSARY):
        check_glossary()
    if os.path.exists(INCIDENTS) and inv:
        check_incidents(inv)
    for path in (RANK, SUMM, MOON, EVIDENCE, IMAGES, TIMELINE, GLOSSARY, INCIDENTS):
        if not os.path.exists(path):
            print(f"  {path}: not found, skipped")

    for rid, r in rankings.items():
        if rid in inv:
            check_wording(RANK, rid, r["reason"], inv[rid])
    for rid, r in evidence.items():
        if rid in inv:
            check_wording(EVIDENCE, rid, r["evidence_detail"], inv[rid])
    for rid, entry in summaries.items():
        if rid in inv and isinstance(entry, dict):
            for field, value in entry.items():      # every text field, including ones added later
                if isinstance(value, str):
                    check_wording(f"{SUMM} {field}", rid, value, inv[rid])

    for label, items in (("ERRORS", errors), ("WARNINGS (review, not blocking)", warnings)):
        if items:
            print(f"\n{label}:")
            for item in items:
                print(f" - {item}")
    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s).")
    if errors:
        print("Validation FAILED.")
        sys.exit(1)
    print("ALL CHECKS PASSED." if not warnings else "Structure OK. Please review the warnings.")


if __name__ == "__main__":
    main()
