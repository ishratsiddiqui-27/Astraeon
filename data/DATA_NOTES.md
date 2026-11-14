# Data Notes: NASA PSI Combustion Investigations Dataset

**Dataset File:** `data/investigations.csv`  
**Source:** NASA Physical Sciences Informatics (PSI) Repository (`psi.nasa.gov`)  
**Collection Date:** November 14, 2026  
**Curator:** Person 1 (Data Pipeline Owner)  

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

## 2. Unit Conversions & Numerical Filters

- **Pressure (`pressure_psi`):** NASA PSI records report pressure in various units (atm, bar, mmHg, psia). Where explicit numeric values were provided in atmospheres, they have been converted to PSI using standard atmospheric conversion:
  $$\text{1 atm} = 14.696\text{ psi}$$
  - `cfi`: $0.25\text{--}5\text{ atm} \approx 3.7\text{--}73.5\text{ psi}$
  - `flex`: $0.5\text{--}1.5\text{ atm} \approx 7.3\text{--}22.0\text{ psi}$
  - `flex2`: $0.5\text{--}3.0\text{ atm} \approx 7.3\text{--}44.1\text{ psi}$
  - `psi142`: $\text{up to } 20\text{ atm} \approx 294\text{ psi}$
- **Numeric $O_2$ & Pressure Coverage (Note for Person 4):**
  - Only **10 of 24** rows contain numeric $O_2$ bounds (`o2_min`, `o2_max`), and only **5 of 24** have numeric pressure.
  - UI sliders and filters must provide a **"Show All / Include Unspecified"** setting to prevent inadvertently filtering out experiments whose exact environmental numbers were unlisted.

---

## 3. Study Types: Flight vs. Modeling vs. Ground

- **`flight` (19 rows):** Physical experiments conducted aboard spaceflight platforms:
  - International Space Station (ISS CIR rack, MSG glovebox)
  - Cygnus expendable resupply vehicles (SAFFIRE wind duct)
- **`modeling` (4 rows - `psi117`, `psi62`, `psi60`, `psi115`):** Numerical simulations (CFD, flamelet-generated manifolds, DNS) that model and extrapolate flight data. They are vital for fire predictive modeling, but should not be described as flight missions.
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
- **`acme_efield` (Partial-Gravity Analogue):** ACME E-FIELD is the **only investigation** in this dataset directly addressing partial gravity: it used high-voltage electric fields to manipulate flame chemi-ions, inducing ion-driven convection that mimicked partial-gravity buoyant forces.
- **`acme_cfig` (High-$O_2$ Relevance):** ACME CFI-G tested inverse diffusion flames with burner-delivered oxygen concentrations reaching up to **85% $O_2$**, making it critically relevant to exploration atmospheres proposed for pressurized lunar/planetary habitats.
- **`daft` (Non-Combustion Test):** DAFT and DAFT-2 evaluated particulate counter hardware in microgravity using inert Arizona Road Dust (ARD). No fuel was burned; `fuel_type` is left blank.
- **`psi142` (Ground Experiment at High Pressure):** Operated at up to 20 atm in a ground laboratory counterflow burner with `gravity = normal gravity`. Due to extreme non-spacecraft conditions, its relevance score to habitable spacecraft design should be considered low.
