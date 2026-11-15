# Data Notes: NASA PSI Combustion Investigations Dataset

**Dataset File:** `data/investigations.csv`  
**Source:** NASA Physical Sciences Informatics (PSI) Repository (`psi.nasa.gov`)  
**Collection Date:** November 14, 2026  
**Last Verified:** November 15, 2026 (oxygen and pressure cells checked against PSI experiment tables; see section 8)  
**Curator:** Maimuna Afrah (data collection and curation)  
**Status:** **Columns Frozen** (19 columns)  

---

## 1. Schema & Column Definitions

Any **blank/empty cell** indicates that the value was **unknown or not reported** in the public PSI documentation. Blanks must **never** be interpreted as zero or assumed values.

| Column | Data Type | Description | Values / Examples |
|---|---|---|---|
| `id` | string | Unique short lowercase identifier | `bass`, `saffire1`, `flex`, `acme_cfig` |
| `name` | string | Full official NASA investigation name | *e.g., Spacecraft Fire Safety Experiment-I* |
| `fuel_type` | enum/string | Primary fuel state | `solid`, `liquid`, `gas`, or blank (for non-burning tests) |
| `fuel_detail` | string | Specific material or chemical fuel formulation | *e.g., SIBAL fabric, n-dodecane, ethylene/CH4* |
| `hardware` | string | Flight apparatus, glovebox, or rack | CIR, MDCA, MSG, Cygnus flow duct |
| `o2_percent` | string | Reported oxygen concentration text for display. Says whether high O2 was in the chamber air (ambient) or only in the burner flow | `12 - 34%`, `17 - 21%`, `12 - 85% (ambient 18-40% in normal flames; burner flow 12-85% in inverse flames)` |
| `pressure_psi` | string | Pressure formatted in PSI (converted from atm, bar or mmHg) | `8.2 - 14.7 psia`, `7.3 - 73.5 psi`, `~14.7 psi (~1 atm)` |
| `airflow` | string | Forced or convective airflow velocity | `20 cm/s`, `30 cm/s`, `quiescent (0 cm/s)` |
| `gravity` | enum/string | Gravity environment of the test | `microgravity` (flight/orbit) or `normal gravity` (ground) |
| `sensors` | string | Diagnostics and instrumentation used | Radiometers, thermocouples, cameras, pyrometry |
| `objective` | string | High-level experimental or modeling objective | Concise summary of scientific goals |
| `what_varied` | string | Parameters systematically varied between test points | Flow speed, fuel dilution, O2 level, geometry |
| `what_same` | string | Parameters held constant across the test matrix | Microgravity, chamber volume, igniter power |
| `topic` | enum/string | Primary spacecraft fire safety relevance | `prevention`, `detection`, or `suppression` |
| `source_link` | URL | Direct link to the NASA PSI investigation record | `https://psi.nasa.gov/physci/repo/...` |
| `o2_min` | float | Lowest oxygen percentage tested in any gas stream (numeric for UI sliders) | `12`, `21.5`, `17` |
| `o2_max` | float | Highest oxygen percentage tested in any gas stream, **including burner-flow O2 in inverse-flame tests**. For chamber air, read `o2_percent` | `85`, `22.1`, `40` |
| `study_type` | enum/string | Nature of the investigation | `flight`, `modeling`, or `ground` |
| `notes` | string | Important scientific caveats and exploration context | High O2 burner flow, per-test pairing unconfirmed, non-combustion |

---

## 2. Unit Conversions & Numerical Filters

- **Pressure (`pressure_psi`):** Pressures reported in other units were converted to PSI:
  $$\text{1 atm} = 14.696\text{ psi} \qquad \text{1 bar} = 14.504\text{ psi} \qquad \text{1 mmHg} = 0.019337\text{ psi}$$
  - `cfi`: $0.5\text{--}5\text{ atm} \approx 7.3\text{--}73.5\text{ psi}$ (flown, per PSI-39 experiment table; the objective text states 0.25–5 atm)
  - `flex`: $526\text{--}2320\text{ mmHg}\ (0.69\text{--}3.05\text{ atm}) \approx 10.2\text{--}44.9\text{ psi}$ (flown, per PSI-69 experiment table; the approach text plans 0.5–1.5 atm for LOI tests)
  - `flex2`: $0.5\text{--}3.0\text{ atm} \approx 7.3\text{--}44.1\text{ psi}$
  - `acme_cfig`: $0.50\text{--}3.31\text{ bar} \approx 7.2\text{--}48.0\text{ psi}$ (PSI-159 experiment tables, column "approx p (bar)")
  - `acme_flamedesign`: $0.42\text{--}3.01\text{ atm} \approx 6.2\text{--}44.2\text{ psi}$ (PSI-10 experiment tables, initial pressure)
  - `acme_sflame`: $\sim 1\text{ atm} \approx 14.7\text{ psi}$ (PSI-23 experiment table note)
  - `psi142`: $\text{up to } 20\text{ atm} \approx 294\text{ psi}$
  - `acme_bre`: natively reported in psia ($8.2\text{--}14.7\text{ psia}$)
- **Numeric $O_2$ & Pressure Coverage (Note for Person 4):**
  - Only **10 of 24** rows contain numeric $O_2$ bounds (`o2_min`, `o2_max`).
  - Only **8 of 24** report pressure, as text (e.g., `"up to 294 psi (20 atm)"`, `"8.2 - 14.7 psia"`).
  - UI sliders and filters must provide a **"Show All / Include Unspecified"** setting to prevent inadvertently filtering out experiments whose exact environmental numbers were unlisted.
  - `o2_max` includes burner-flow oxygen for `acme_cfig` and `acme_flamedesign` (both 85%). A slider labelled "cabin oxygen" should not treat 85% as chamber air.

---

## 3. Study Types: Flight vs. Modeling vs. Ground

- **`flight` (19 rows):** Physical experiments conducted aboard spaceflight platforms:
  - International Space Station (ISS CIR rack, MSG glovebox)
  - Cygnus expendable resupply vehicles (SAFFIRE wind duct)
- **`modeling` (4 rows - `psi117`, `psi62`, `psi60`, `psi115`):** Numerical simulations (CFD, flamelet-generated manifolds) that model and extrapolate flight data. They are vital for fire predictive modeling, but should not be described as flight missions.
- **`ground` (1 row - `psi142`):** Ground-based laboratory counterflow burner investigation with ozone sensitization, operating at elevated pressure (up to 20 atm) to extend FLEX flight data.

---

## 4. Topics (`prevention`, `detection`, `suppression`)

The `topic` column represents **primary operational relevance**, not an absolute physical barrier:
- **`prevention` (12 rows):** Material flammability limits, low-oxygen and high-oxygen flammability boundaries, flame spread over solid fabrics/polymers (NASA-STD-6001 Test 1 & 2 correlation).
- **`detection` (6 rows):** Soot morphology, smoke droplet aggregate growth, particle size distributions, smoke point transitions, and smoke detector sensor verification.
- **`suppression` (6 rows):** Droplet flame extinction, cool flame persistence after hot flame quenching, gaseous fire suppressants ($CO_2, He, SF_6$), counterflow extinction, and electrical quenching.

---

## 5. Gravity Environments & Partial Gravity

- **No Dedicated Partial-Gravity Flight Data in PSI:** NASA's PSI database does not currently contain dedicated lunar ($0.16g$) or Martian ($0.38g$) flight experiments.
- **`acme_efield` (not a partial-gravity test):** The electric field acted on ions in the flame and drove ion-driven convection. Microgravity was used *"for isolating electric field effects from buoyancy forces"* (PSI-22). PSI-22 does not mention partial gravity, and states that the research *"is not being conducted to serve any space applications."* Earlier versions of this dataset (before November 15, 2026) said the field "mimicked partial gravity". That claim was removed because PSI-22 does not support it.
- **`acme_cfig`:** Two kinds of test. Normal-flame tests burned in chamber air of **18–40% O2** at 0.5–3 bar. Inverse-flame tests fed up to **85% O2 through the burner** into a fuel-filled chamber. The 85% figure is burner flow, not chamber air. The 18–40% chamber-air tests are the ones that matter for Moon-base conditions (section 6).
- **`daft` (Non-Combustion Test):** DAFT and DAFT-2 evaluated particulate counter hardware in microgravity using inert Arizona Road Dust (ARD). No fuel was burned; `fuel_type` is left blank.
- **`psi142` (Ground Experiment at High Pressure):** Operated at up to 20 atm in a ground laboratory counterflow burner with `gravity = normal gravity`. Due to extreme non-spacecraft conditions, its relevance score to habitable spacecraft design should be considered low.

---

## 6. What the Data Says About Moon-Base Conditions

Per the challenge brief, a Moon base is expected to run at **30% oxygen or more** and **10.2 psi or less** (70.3 kPa), to shorten prebreathe time before spacewalks.

We checked this in two steps: a range screen on the CSV, then a test-by-test check against the experiment tables PSI publishes with each investigation.

### A. Range Screen (from the CSV)
`python data_report.py` compares each row's reported ranges:
- **6 of 24** experiments have an oxygen range reaching 30% or higher: `acme_cfig`, `acme_flamedesign`, `acme_bre`, `flex`, `flex2`, `acme_sflame`.
- **5 of those 6** also have a pressure range reaching 10.2 psi or lower. The exception is `acme_sflame`, which ran at ~1 atm.
- 14 of 24 rows report no oxygen and 16 of 24 report no pressure, so they cannot be screened at all.

A range overlap does **not** mean high oxygen and low pressure happened in the same test. Section B checks that.

### B. Test-by-Test Check (from the PSI experiment tables)

Only chamber air (ambient O2) counts here, because that is what a Moon-base cabin would be.

| `id` | Ambient O2 ≥ 30% **and** ≤ 10.2 psi in the same test? | Evidence |
|---|---|---|
| `acme_cfig` | **Yes: 20 tests, 17 with hot ignition** | PSI-159 normal-flame table: 33.2–39.3% ambient O2 at 0.5 atm (listed as 0.50665 bar, 7.35 psi), on 3 test days. Fuels: 50% butane, 30% butane, 30% ethane (N2-diluted). The 17 hot flames burned 13–274 s |
| `acme_bre` | Likely, but not confirmed | PSI-20 objectives name **8.2 psia with 34% O2** as a planned atmosphere (with 10.2 psia/26.5% and 14.7 psia/21%). 34% O2 appears on 13 of 18 flight test days, but the log states: *"The chamber pressures were also varied but are not identified in this summary table."* |
| `flex2` | Not confirmed | PSI-68 table lists O2 options (0.17, 0.21, 0.25, 0.30) and pressure options (0.5–3.0 atm) for every fuel, not a per-test log |
| `flex` | No, but within 0.13–0.30 psi | PSI-69 table: 17 methanol and heptane droplet tests at 30% or 34% O2 ran at 10.33–10.50 psi (~0.7 atm). None ended in extinction: 2 burned to completion and 15 ended in "Disruption". 16 have recorded burn times of 4–24 s |
| `acme_flamedesign` | No | PSI-10: ambient O2 reached 40% only at 13.7–19.1 psi. Its low-pressure, high-O2 tests were inverse flames (O2 from the burner) |
| `acme_sflame` | No | PSI-23 table: ~30% O2 tests ran at ~1 atm |

Inverse-flame tests are left out of the count: 28 in `acme_cfig` and 18 in `acme_flamedesign` had ≥ 30% burner O2 at ≤ 10.2 psi, but the chamber was full of fuel, not air.

**What BRE does add:** PSI-20 reports that flames *"in a normal atmosphere of 21% oxygen self-extinguished in a short time"* without airflow, while *"ongoing combustion without air flow was notably seen in elevated-oxygen atmospheres."* Cutting ventilation is a standard step in putting out a spacecraft fire, so this matters for Moon-base atmospheres. PSI calls these results *"still preliminary."*

**What "hot ignition" means in the PSI-159 table.** PSI does not define the column, so this reading comes from the table itself. CFI-G studies cool flames, which PSI-159 describes as peaking at 500–1000 K. "Hot ignition: Yes" marks a test where an ordinary hot flame ignited. Of the 3 "No" rows among the 20 matches:
- 2 are commented *"direct cool - no hot ignition"*, meaning a cool flame formed without a hot flame first.
- 1 (test 21106 F4) is commented *"hot flame"* and burned for 22 s despite the "No".

So 17 is the conservative count of hot flames at Moon-base conditions.

**Caveats on the `acme_cfig` result:**
- The pressure column is labelled "approx p (bar)" in the source.
- O2 values are the chamber reading before each test; O2 drops during a test as the chamber fills with combustion products.
- CFI-G was designed to study cool flames, not cabin fire safety. These are diluted gaseous fuels on a spherical porous burner, not cabin materials.

**The per-test data behind this table is saved in `data/moon_tests.csv`.** It has one row per flight test: 746 tests from 4 investigations (`acme_cfig`, `acme_flamedesign`, `flex`, `cfi`), each with chamber O2, pressure in psi, the pressure as published, the outcome, the burn time, and whether the test falls in the Moon-base zone. Only chamber-air tests are included; inverse-flame tests are left out because their O2 value is burner flow. `acme_bre`, `flex2` and `acme_sflame` can't be included because PSI doesn't publish oxygen and pressure together for each of their tests. Rebuild the file from PSI at any time with `python build_moon_tests.py`. Current result: 20 tests in the zone, all `acme_cfig`, 17 with hot ignition. The closest tests outside it are FLEX's 17 at 10.33–10.50 psi.

### C. Headline (offered to Person 4 and Person 5)
> Of the 24 NASA microgravity combustion investigations in PSI, only one, ACME CFI-G, has test-by-test records of flames burning at likely Moon-base conditions (30% or more oxygen, 10.2 psi or less): 17 hot-flame ignitions at 33–39% oxygen and 7.35 psi, all with gaseous fuels. FLEX came within 0.1–0.3 psi: 17 liquid-droplet tests (methanol and heptane) burned at 30–34% oxygen and 10.3–10.5 psi. No solid-material fire test is confirmed at those conditions, and none was run in partial gravity.

### D. The Partial-Gravity Gap
- **Zero actual partial-gravity ($0.16g$ lunar / $0.38g$ Martian) flight test data** currently exists in NASA's PSI database.
- **No entry in this dataset addresses partial gravity,** not even as an analogue. `acme_efield` was listed here before November 15, 2026; see section 5 for why it was removed.

---

## 7. Data Completeness Summary

Counts come from `python data_report.py`. Re-run it after any edit to the CSV and update this table.

| Column | Filled Count | Completeness | Notes / Handling for UI |
|---|---|---|---|
| `id` | 24 / 24 | **100.0%** | Primary key |
| `name` | 24 / 24 | **100.0%** | Full official title |
| `gravity` | 24 / 24 | **100.0%** | 23 `microgravity`, 1 `normal gravity` (`psi142`) |
| `objective` | 24 / 24 | **100.0%** | Summary of goals |
| `what_varied` | 24 / 24 | **100.0%** | Test matrix parameters |
| `topic` | 24 / 24 | **100.0%** | 12 prevention, 6 detection, 6 suppression |
| `source_link` | 24 / 24 | **100.0%** | Direct PSI URL |
| `study_type` | 24 / 24 | **100.0%** | 19 `flight`, 4 `modeling`, 1 `ground` |
| `fuel_detail` | 23 / 24 | **95.8%** | Blank only for `psi60` (unspecified gas coflow) |
| `sensors` | 22 / 24 | **91.7%** | Blank for pure simulation studies (`psi117`, `psi115`) |
| `fuel_type` | 22 / 24 | **91.7%** | Blank on purpose for `daft` (no fuel burned) and `psi115` (precursor) |
| `what_same` | 21 / 24 | **87.5%** | Controlled parameters |
| `hardware` | 20 / 24 | **83.3%** | Blank for CFD modeling grants without flight hardware |
| `airflow` | 12 / 24 | **50.0%** | Reported for duct/flow experiments; chamber tests are often quiescent |
| `o2_percent` / `o2_min` / `o2_max` | 10 / 24 | **41.7%** | Numeric slider filter **must include 'Show All'** |
| `notes` | 10 / 24 | **41.7%** | Specific scientific caveats and exploration context |
| `pressure_psi` | 8 / 24 | **33.3%** | Reported as text; pressure filter **must include 'Show All'** |

---

## 8. How This Was Checked

All rows were compiled from the PSI investigation overview text (November 14, 2026). The checks since then cover two different things:

- **Oxygen and pressure: checked against PSI's per-test data (November 15, 2026).** Each PSI investigation page has an "Experimental table" CSV listing the actual test conditions. The tables were downloaded through the data service the PSI site itself uses (`psi.nasa.gov/geode-py/ws`). 20 of the 24 investigations have one; the 4 modeling studies (`psi60`, `psi62`, `psi115`, `psi117`) do not. For those 20, the oxygen and pressure values were compared with the tables, including where they appear inside `what_varied` and `notes`. Where a table disagreed with the overview text, the table value was used, because it records what was flown rather than what was planned.
- **Every other column was not re-verified against the tables.** This covers `objective`, `sensors`, `hardware`, `fuel_detail`, `airflow`, `what_same` and the rest of `what_varied`. They come from PSI overview text only.

Rows changed by the table check:

| `id` | Change | Source |
|---|---|---|
| `acme_cfig` | Ambient O2 corrected from "12–21%" to 18–40%; pressure 7.2–48.0 psi added | PSI-159 normal and inverse flame tables |
| `acme_flamedesign` | O2 20.4–20.7% → 19.8–85% (ambient 19.8–40%, burner up to 85%); pressure 6.2–44.2 psi added | PSI-10 normal and inverse flame tables |
| `flex` | O2 21% → 12–34%; pressure 7.3–22.0 → 10.2–44.9 psi | PSI-69 table (273 tests) |
| `cfi` | O2 21% → 17–21%; pressure 3.7–73.5 → 7.3–73.5 psi | PSI-39 table (87 tests) |
| `bass2` | O2 21.8–22.2% → 13.6–22.2% (N2 vitiation) | PSI-25 table, calibrated initial O2 |
| `flex2` | O2 max 40% → 30%; conflict noted (approach text says 0.1–0.4) | PSI-68 table vs. approach text |
| `acme_sflame` | Pressure ~1 atm added | PSI-23 table note |
| `acme_bre` | Note added: per-test pressures not published | PSI-20 table note |
| `acme_efield` | "Mimicked partial gravity" removed from `what_varied` and `notes` (not in PSI-22); fuel concentration in N2 corrected from 40–100% to 25–100% | PSI-22 page text and experiment table (32 rows) |

**PSI coverage (feature check, November 15, 2026).** PSI lists 133 investigations, and 24 are tagged "Combustion Science". All 24 are in this dataset, so no rows were missing. One related non-combustion entry exists: PSI-179, Aerosol Sampling Experiment (ASE), under Complex Fluids. It is passive sampling of ISS cabin particles, not a fire test, so it was not added.
