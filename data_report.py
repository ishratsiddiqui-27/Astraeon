"""Summarize data/investigations.csv: completeness per column and a Moon-base screen.

Run from the project root:
    python data_report.py

Output is Markdown, so tables can be pasted into data/DATA_NOTES.md.
The Moon-base screen only compares ranges. It cannot show that high O2 and
low pressure happened in the same test; DATA_NOTES.md section 6 has the
per-test check against the PSI experiment tables.
"""
import csv
import os
import re
import sys
from collections import Counter

MOON_O2_MIN = 30.0      # percent O2, "30% or more"
MOON_PSI_MAX = 10.2     # psi, "10.2 psi or less"


def load(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def filled(value):
    return bool(value and value.strip())


def pressure_low_psi(text):
    """Lowest pressure in a pressure_psi cell, or None if it can't be read.

    "8.2 - 14.7 psia" -> 8.2, "~14.7 psi (~1 atm)" -> 14.7,
    "up to 294 psi (20 atm)" -> None (no lower bound given).
    """
    m = re.search(r"(up to\s*)?~?\s*(\d+(?:\.\d+)?)\s*(?:-\s*~?\s*\d+(?:\.\d+)?)?\s*psia?\b", text or "", re.I)
    if not m or m.group(1):
        return None
    return float(m.group(2))


def as_float(text):
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def completeness(rows, columns):
    n = len(rows)
    counts = sorted(((sum(filled(r[c]) for r in rows), c) for c in columns), key=lambda x: (-x[0], columns.index(x[1])))
    print(f"## Completeness ({n} experiments)\n")
    print("| Column | Filled | Completeness |")
    print("|---|---|---|")
    for k, c in counts:
        print(f"| `{c}` | {k} / {n} | {100 * k / n:.1f}% |")
    print()


def breakdowns(rows):
    print("## Category counts\n")
    for c in ("topic", "study_type", "gravity", "fuel_type"):
        parts = ", ".join(f"{v or '(blank)'}: {k}" for v, k in Counter(r[c] for r in rows).most_common())
        print(f"- `{c}`: {parts}")
    print()


def moon_screen(rows):
    n = len(rows)
    high_o2 = [r for r in rows if (as_float(r["o2_max"]) or 0) >= MOON_O2_MIN]
    both = [r for r in high_o2
            if pressure_low_psi(r["pressure_psi"]) is not None
            and pressure_low_psi(r["pressure_psi"]) <= MOON_PSI_MAX]
    no_o2 = sum(not filled(r["o2_max"]) for r in rows)
    no_p = sum(not filled(r["pressure_psi"]) for r in rows)

    print(f"## Moon-base screen (O2 >= {MOON_O2_MIN:g}%, pressure <= {MOON_PSI_MAX:g} psi)\n")
    print(f"- Oxygen range reaches {MOON_O2_MIN:g}% or more: **{len(high_o2)} of {n}**")
    for r in high_o2:
        print(f"  - `{r['id']}`: O2 {r['o2_percent']}; pressure {r['pressure_psi'] or '(not reported)'}")
    print(f"- Of those, pressure range also reaches {MOON_PSI_MAX:g} psi or less: **{len(both)} of {len(high_o2)}**")
    for r in both:
        print(f"  - `{r['id']}`: {r['pressure_psi']}")
    print(f"- Not screenable: {no_o2} of {n} rows report no oxygen, {no_p} of {n} report no pressure.")
    print("- Ranges only: this does not show high O2 and low pressure in the same test.")
    print()


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join("data", "investigations.csv")
    if not os.path.exists(path):
        sys.exit(f"Error: file '{path}' not found.")
    rows = load(path)
    columns = list(rows[0].keys())
    completeness(rows, columns)
    breakdowns(rows)
    moon_screen(rows)


if __name__ == "__main__":
    main()
