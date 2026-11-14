# Data Notes: NASA PSI Combustion Investigations Dataset

**Dataset File:** `data/investigations.csv`  
**Source:** NASA Physical Sciences Informatics (PSI) Repository (`psi.nasa.gov`)  
**Collection Date:** November 14, 2026  
**Curator:** Person 1 (Data Pipeline Owner)  
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
| `o2_percent` | string | Reported oxygen concentration text for display | `21%`, `12 - 85%`, `21.5 - 22.1%` |
| `pressure_psi` | string | Pressure formatted in PSI (converted from atm/bar) | `8.2 - 14.7 psia`, `3.7 - 73.5 psi` |
| `airflow` | string | Forced or convective airflow velocity | `20 cm/s`, `30 cm/s`, `quiescent (0 cm/s)` |
| `gravity` | enum/string | Gravity environment of the test | `microgravity` (flight/orbit) or `normal gravity` (ground) |
| `sensors` | string | Diagnostics and instrumentation used | Radiometers, thermocouples, cameras, pyrometry |
| `objective` | string | High-level experimental or modeling objective | Concise summary of scientific goals |
| `what_varied` | string | Parameters systematically varied between test points | Flow speed, fuel dilution, O2 level, geometry |
| `what_same` | string | Parameters held constant across the test matrix | Microgravity, chamber volume, igniter power |
| `topic` | enum/string | Primary spacecraft fire safety relevance | `prevention`, `detection`, or `suppression` |
| `source_link` | URL | Direct link to the NASA PSI investigation record | `https://psi.nasa.gov/physci/repo/...` |
| `o2_min` | float | Minimum oxygen percentage (numeric for UI sliders) | `12`, `21.5`, `17` |
| `o2_max` | float | Maximum oxygen percentage (numeric for UI sliders) | `85`, `22.1`, `40` |
| `study_type` | enum/string | Nature of the investigation | `flight`, `modeling`, or `ground` |
| `notes` | string | Important scientific caveats and exploration context | High O2 burner flow, partial gravity, non-combustion |

---

## 2. What the Data Says About Moon-Base Conditions

Future lunar exploration habitats (e.g., Artemis base camps) are slated to operate under **reduced pressure and elevated oxygen** (typically $\ge 30\%\text{ } O_2$ and $\le 10.2\text{ psi}$ / $70.3\text{ kPa}$) to reduce EVA prebreathe times while preventing hypoxia.

Querying `data/investigations.csv` reveals critical coverage insights and gaps:

### A. Oxygen Coverage ($\ge 30\%\text{ } O_2$)
Only **4 of 24** investigations evaluated oxygen concentrations reaching 30% or higher:
1. **`acme_cfig`:** Reached up to **85% $O_2$** burner-flow in inverse diffusion flame tests.
2. **`acme_bre`:** Tested ambient $O_2$ concentrations from **21% up to 40%**.
3. **`flex2`:** Tested ambient oxygen mole fractions from **17% up to 40%**.
4. **`acme_sflame`:** Evaluated enriched atmospheres up to **~30% $O_2$**.

### B. Pressure Coverage ($\le 10.2\text{ psi}$)
Only **2 of the 4 elevated-oxygen investigations** also evaluated pressures within the lunar habitat regime ($\le 10.2\text{ psi}$):
1. **`acme_bre` (Direct Match):** Explicitly designed around NASA Exploration Atmospheres. It simultaneously evaluated:
   - **$8.2\text{ psia}$ with $34\%\text{ } O_2$**
   - **$10.2\text{ psia}$ with $26.5\%\text{ } O_2$**
   - *Key finding:* Flames that self-extinguished in normal air (21% $O_2$) sustained ongoing combustion in elevated-oxygen atmospheres even without ventilation!
2. **`flex2` (Parametric Overlap):** Evaluated pressures down to $0.5\text{ atm}$ ($7.3\text{ psi}$) and $O_2$ up to 40% across its droplet matrix, although tests were conducted as parametric sweeps.

### C. The Partial-Gravity Gap
- **Zero actual partial-gravity ($0.16g$ lunar / $0.38g$ Martian) flight test data** currently exists in NASA's PSI database.
- **`acme_efield`** is the only entry that addresses this gap, using electro-hydrodynamic ion-driven convection to emulate partial-gravity buoyant forces.

> **Headline for Dashboard Team (Persons 4 & 5):**  
> *"NASA's microgravity database contains only one flight experiment (`acme_bre`) that tested simultaneous lunar-habitat conditions (8.2 psia at 34% O₂), and zero actual lunar-g flight tests—highlighting a critical research gap for Artemis fire safety."*

---

## 3. Data Completeness Summary

To ensure honest visualization and avoid user misinterpretation, the completeness of each field across all 24 records is documented below:

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
| `hardware` | 20 / 24 | **83.3%** | Blank for CFD modeling grants with no dedicated hardware |
| `airflow` | 12 / 24 | **50.0%** | Reported for duct/flow experiments; chamber tests are often quiescent |
| `o2_percent` / `o2_min` / `o2_max` | 10 / 24 | **41.7%** | Numeric slider filter **must include 'Show All'** |
| `pressure_psi` | 5 / 24 | **20.8%** | Pressure filter **must include 'Show All'** |
| `notes` | 5 / 24 | **20.8%** | Specific scientific caveats and exploration context |

---

## 4. Pressure Conversions

Where explicit numeric pressure values were reported in atmospheres, they have been converted to PSI using standard atmospheric conversion:
$$\text{1 atm} = 14.696\text{ psi}$$
- `cfi`: $0.25\text{--}5\text{ atm} \approx 3.7\text{--}73.5\text{ psi}$
- `flex`: $0.5\text{--}1.5\text{ atm} \approx 7.3\text{--}22.0\text{ psi}$
- `flex2`: $0.5\text{--}3.0\text{ atm} \approx 7.3\text{--}44.1\text{ psi}$
- `psi142`: $\text{up to } 20\text{ atm} \approx 294\text{ psi}$
- `acme_bre`: natively reported in psia ($8.2\text{--}14.7\text{ psia}$)

---

## 5. Topics (`prevention`, `detection`, `suppression`)

The `topic` column represents **primary operational relevance**, not an absolute physical barrier:
- **`prevention` (12 rows):** Material flammability limits, low-oxygen and high-oxygen flammability boundaries, flame spread over solid fabrics/polymers (NASA-STD-6001 Test 1 & 2 correlation).
- **`detection` (6 rows):** Soot morphology, smoke droplet aggregate growth, particle size distributions, smoke point transitions, and smoke detector sensor verification.
- **`suppression` (6 rows):** Droplet flame extinction, cool flame persistence after hot flame quenching, gaseous fire suppressants ($CO_2, He, SF_6$), counterflow extinction, and electrical quenching.
