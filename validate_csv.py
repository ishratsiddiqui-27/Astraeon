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
SUMMARY_FIELDS = ["simple_summary", "why_it_matters"]
MOON_COLUMNS = ["id", "psi_id", "test", "fuel", "o2_percent", "pressure_psi", "pressure_as_published",
                "outcome", "burn_time_s", "in_moon_zone", "source_table"]

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
    header, rows = read_csv(MOON)
    if header != MOON_COLUMNS:
        errors.append(f"{MOON}: columns changed; rebuild it with: python build_moon_tests.py")
        return
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
    row_numbers = numbers_in(" ".join(inv_row.values()))
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
    if os.path.exists(MOON) and inv:
        check_moon_tests(inv)
    for path in (RANK, SUMM, MOON):
        if not os.path.exists(path):
            print(f"  {path}: not found, skipped")

    for rid, r in rankings.items():
        if rid in inv:
            check_wording(RANK, rid, r["reason"], inv[rid])
    for rid, entry in summaries.items():
        if rid in inv and isinstance(entry, dict):
            for field in SUMMARY_FIELDS:
                check_wording(f"{SUMM} {field}", rid, str(entry.get(field, "")), inv[rid])

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
