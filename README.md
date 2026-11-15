# Astereon

> Interactive spacecraft fire safety dashboard summarizing NASA's microgravity combustion experiments from the Physical Sciences Informatics (PSI) database.

---

## 📊 Team Roles & Ownership

| Person | Role | Files in this repo | Status |
|---|---|---|---|
| **Person 1** | Data collection and curation | `data/investigations.csv`: NASA PSI microgravity combustion experiments (24 experiments across solid, liquid, gas fuels and fire prevention, detection, suppression). **19 columns, frozen.** Docs and scripts listed below. | ✅ Complete & Verified |
| **Person 2** | Rankings, built from `data/investigations.csv` | `data/rankings.csv` (scores for spacecraft, station, Moon and rover), `data/RANKINGS_NOTES.md` (scoring rule and change log) | ✅ Complete (finalized by Person 1) |
| **Person 3** | AI summaries, built from `data/investigations.csv` | None yet | In Progress |
| **Person 4** | Spacecraft fire safety scenarios, suppression standards, and dashboard configuration parameters | `data/incidents.csv` (not in repo yet) | In Progress |
| **Person 5** | Research and submission | None yet | In Progress |

### Docs & Scripts

| File | Description | Owner |
|---|---|---|
| `data/DATA_NOTES.md` | Column definitions, unit conversions, Moon-base finding, completeness, and how the data was checked for `investigations.csv` | **Person 1** |
| `validate_csv.py` | Checks `investigations.csv` structure and allowed values | **Person 1** |
| `data_report.py` | Prints completeness counts and the Moon-base screen for `investigations.csv` | **Person 1** |
| `data/moon_tests.csv` | One row per flight test with chamber oxygen and pressure (746 tests from PSI). For the oxygen vs. pressure chart with the Moon-base zone | **Person 1** |
| `build_moon_tests.py` | Rebuilds `data/moon_tests.csv` by downloading the experiment tables from NASA PSI (needs internet) | **Person 1** |

---

## 🛠️ Data Validation

Run the dataset validator from the project root:

```bash
python validate_csv.py
```

Run it before every push. It checks all four data files together:

- **Errors (must fix):**
  - `investigations.csv` keeps its 19 frozen columns and allowed values.
  - `rankings.csv` and `summaries.json` have exactly the same 24 ids as `investigations.csv`.
  - Scores are whole numbers from 0 to 10, and no summary or reason is blank.
  - `moon_tests.csv` marks the Moon-base zone correctly.
- **Warnings (review):**
  - Numbers in summaries or ranking reasons that aren't in that experiment's row of `investigations.csv`.
  - Claims that were already corrected once, such as "partial gravity", or "85%" without "burner".

## 📋 Data Report

```bash
python data_report.py
```

Prints, as Markdown:
- how many experiments fill each column (for example, 10 of 24 report oxygen and 8 of 24 report pressure)
- counts by topic, study type, gravity and fuel type
- a Moon-base screen listing which experiments' ranges reach 30% O2 or more and 10.2 psi or less

The screen compares ranges only. The test-by-test result is in `data/DATA_NOTES.md`, section 6.
