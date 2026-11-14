# Astereon

> Interactive spacecraft fire safety dashboard summarizing NASA's microgravity combustion experiments from the Physical Sciences Informatics (PSI) database.

---

## 📊 Team Data Files & Ownership

| Data File | Description | Owner | Status |
|---|---|---|---|
| `data/investigations.csv` | NASA PSI microgravity combustion experiments dataset (24 experiments across solid, liquid, gas fuels and fire prevention, detection, suppression). | **Person 1** | ✅ Complete & Verified |
| `data/materials.csv` | Spacecraft material flammability metrics and NASA-STD-6001 standard screening test data. | **Person 2** | In Progress |
| `data/hardware.csv` | Spacecraft combustion research facilities (CIR, MSG, Cygnus flow duct) and sensor diagnostics. | **Person 3** | In Progress |
| `data/incidents.csv` | Spacecraft fire safety scenarios, suppression standards, and dashboard configuration parameters. | **Person 4** | In Progress |

---

## 🛠️ Data Validation

Run the dataset validator from the project root:

```bash
python validate_csv.py
```

This verifies that all required schema columns, valid gravity environments, and standardized fire safety topics (`prevention`, `detection`, `suppression`) are 100% aligned.
