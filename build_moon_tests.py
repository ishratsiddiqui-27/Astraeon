"""Build data/moon_tests.csv: one row per flight test with chamber oxygen and pressure.

Run from the project root (needs internet):
    python build_moon_tests.py

It downloads the "Experimental table" CSVs that NASA PSI publishes for the four
investigations that record chamber oxygen AND pressure for every test, through the
same data service the PSI website uses (psi.nasa.gov/geode-py/ws). It then writes them
as one table that the dashboard can plot (oxygen vs. pressure, with the Moon-base zone).

Only chamber-air tests are included. Inverse-flame tests are left out on purpose:
their oxygen value is the burner flow, not the air in the chamber.
"""
import csv
import io
import json
import os
import sys
import urllib.parse
import urllib.request

OUT = os.path.join("data", "moon_tests.csv")
API = "https://psi.nasa.gov/geode-py/ws"
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

MOON_O2_MIN = 30.0    # percent, challenge brief: "30% or more"
MOON_PSI_MAX = 10.2   # psi, challenge brief: "10.2 psi or less"
TO_PSI = {"atm": 14.696, "bar": 14.5038, "mmHg": 14.696 / 760}

# One entry per experiment table. Column names are exactly as PSI publishes them.
SOURCES = [
    {"id": "acme_cfig", "psi": "PSI-159", "file": "PSI-159_Experimental table_CFI-G_Normal Flames.csv",
     "test": "Test", "fuel": "Fuel", "o2": "XO2 before test", "p": "approx p (bar)", "unit": "bar",
     "outcome": lambda r: f"Hot ignition: {r['Hot ignition']}; end: {r['Self-ext or flow term']}",
     "burn": "burn time (sec)"},
    {"id": "acme_flamedesign", "psi": "PSI-10", "file": "PSI-10_Experimental table_Flame Design_Normal Flame.csv",
     "test": "Test", "fuel": "Fuel", "o2": "XO2 (init)", "p": "pinit (atm)", "unit": "atm",
     "outcome": None, "burn": None},
    {"id": "flex", "psi": "PSI-69", "file": "PSI-69_Experimental table_FLEX.csv",
     "test": "FLEX Test #", "fuel": "Fuel", "o2": "O initial ambient composition; mole fraction",
     "p": "Ambient pressure; mmHg", "unit": "mmHg",
     "outcome": lambda r: r["Test end"], "burn": "Burn time; s"},
    {"id": "cfi", "psi": "PSI-39", "file": "PSI-39_Experimental table_CFI.csv",
     "test": "Flex Number", "fuel": "Fuel", "o2": "Oxygen", "p": "Pressure", "unit": "atm",
     "outcome": None, "burn": None},
]

COLUMNS = ["id", "psi_id", "test", "fuel", "o2_percent", "pressure_psi", "pressure_as_published",
           "outcome", "burn_time_s", "in_moon_zone", "source_table"]


def get(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=90) as resp:
        return resp.read().decode("utf-8-sig", "replace")


def download_table(psi_id, file_name):
    query = urllib.parse.urlencode({"file": file_name, "version": 1, "redirect": "false"})
    signed_url = get(f"{API}/studies/{psi_id}/download?{query}").strip().strip('"')
    return get(signed_url)


def number(text):
    text = (text or "").strip()
    for unit in ("atm", "bar", "mmHg", "%"):
        text = text.replace(unit, "")
    try:
        return float(text)
    except ValueError:
        return None


def main():
    out_rows, skipped = [], {}
    for s in SOURCES:
        text = download_table(s["psi"], s["file"])
        rows = [{(k or "").strip(): (v or "").strip() for k, v in r.items()}
                for r in csv.DictReader(io.StringIO(text))]
        for r in rows:
            o2, p = number(r.get(s["o2"])), number(r.get(s["p"]))
            if o2 is None or p is None or p <= 0:
                skipped[s["id"]] = skipped.get(s["id"], 0) + 1
                continue
            o2_pct, psi = o2 * 100, p * TO_PSI[s["unit"]]
            out_rows.append({
                "id": s["id"], "psi_id": s["psi"], "test": r[s["test"]], "fuel": r[s["fuel"]],
                "o2_percent": f"{o2_pct:.2f}", "pressure_psi": f"{psi:.2f}",
                "pressure_as_published": f"{r[s['p']].replace(s['unit'], '').strip()} {s['unit']}",
                "outcome": s["outcome"](r) if s["outcome"] else "",
                "burn_time_s": r.get(s["burn"], "") if s["burn"] else "",
                "in_moon_zone": "yes" if o2_pct >= MOON_O2_MIN and psi <= MOON_PSI_MAX else "no",
                "source_table": s["file"],
            })

    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\r\n")
        w.writeheader()
        w.writerows(out_rows)

    print(f"Wrote {OUT}: {len(out_rows)} tests")
    for s in SOURCES:
        mine = [r for r in out_rows if r["id"] == s["id"]]
        zone = [r for r in mine if r["in_moon_zone"] == "yes"]
        line = f"  {s['id']:<17} {len(mine):>3} tests, {len(zone):>2} in Moon zone"
        if s["id"] == "acme_cfig":
            line += f" ({sum('Hot ignition: Yes' in r['outcome'] for r in zone)} with hot ignition)"
        if skipped.get(s["id"]):
            line += f"; skipped {skipped[s['id']]} row(s) with no usable O2/pressure"
        print(line)


if __name__ == "__main__":
    try:
        main()
    except OSError as e:
        sys.exit(f"Download failed ({e}). Check your internet connection and try again.")
