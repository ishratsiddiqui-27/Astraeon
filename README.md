# Astereon

> Interactive spacecraft fire safety dashboard summarizing NASA's microgravity combustion experiments from the Physical Sciences Informatics (PSI) database.

---

## 📊 Team Roles & Ownership

| Person | Role | Files in this repo | Status |
|---|---|---|---|
| **Person 1** | Data collection and curation | `data/investigations.csv`: NASA PSI microgravity combustion experiments (24 experiments across solid, liquid, gas fuels and fire prevention, detection, suppression). **19 columns, frozen.** Docs and scripts listed below. | ✅ Complete & Verified |
| **Person 2** | Rankings, built from `data/investigations.csv` | None yet | In Progress |
| **Person 3** | AI summaries, built from `data/investigations.csv` | None yet | In Progress |
| **Person 4** | Spacecraft fire safety scenarios, suppression standards, and dashboard configuration parameters | `data/incidents.csv` (not in repo yet) | In Progress |
| **Person 5** | Research and submission | None yet | In Progress |

### Docs & Scripts

| File | Description | Owner |
|---|---|---|
| `data/DATA_NOTES.md` | Column definitions, unit conversions, Moon-base finding, completeness, and how the data was checked for `investigations.csv` | **Person 1** |
| `validate_csv.py` | Checks `investigations.csv` structure and allowed values | **Person 1** |
| `data_report.py` | Prints completeness counts and the Moon-base screen for `investigations.csv` | **Person 1** |

---

## 🛠️ Data Validation

Run the dataset validator from the project root:

```bash
python validate_csv.py
```

This verifies that all required schema columns, valid gravity environments, and standardized fire safety topics (`prevention`, `detection`, `suppression`) are 100% aligned.

## 📋 Data Report

```bash
python data_report.py
```

Prints, as Markdown:
- how many experiments fill each column (for example, 10 of 24 report oxygen and 8 of 24 report pressure)
- counts by topic, study type, gravity and fuel type
- a Moon-base screen listing which experiments' ranges reach 30% O2 or more and 10.2 psi or less

The screen compares ranges only. The test-by-test result is in `data/DATA_NOTES.md`, section 6.
