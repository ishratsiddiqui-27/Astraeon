# Astereon

> Interactive spacecraft fire safety dashboard summarizing NASA's microgravity combustion experiments from the Physical Sciences Informatics (PSI) database.

---

## 📊 Team Roles & Ownership

| Person | Role | Files in this repo | Status |
|---|---|---|---|
| **Person 1** | Data collection and curation; dashboard frontend | `data/investigations.csv`: NASA PSI microgravity combustion experiments (24 experiments across solid, liquid, gas fuels and fire prevention, detection, suppression). **19 columns, frozen.** The app: `app.py`, `app_pages/`, `.streamlit/config.toml`. Docs and scripts listed below. | Data ✅ · App in progress |
| **Person 2** | Rankings, built from `data/investigations.csv` | `data/rankings.csv` (scores for spacecraft, station, Moon and rover), `data/RANKINGS_NOTES.md` (scoring rule and change log) | ✅ Complete (finalized by Person 1) |
| **Person 3** | AI summaries; deployment; research and submission | `data/summaries.json`, `data/glossary.json`, `data/incident_summaries.json`, `data/research_gaps.json`; `requirements.txt` and `data/about.md` (About page text) | Summaries ✅ · Deployment in progress |
| **Person 4** | Dashboard | Handed over to Person 1 (`incidents.csv` replaced by Person 3's `incident_summaries.json`) | Handed over |
| **Person 5** | Research and submission | Handed over to Person 3 | Handed over |

## ▶️ Running the app

```bash
pip install streamlit
streamlit run app.py
```

Eight pages, in the top navigation: **Home** (headline finding and Moon-base chart), **Experiments** (filters, cards, details, CSV download), **Rank by setting**, **Compare**, **Moon-base explorer**, **Fire history & gaps**, **Ask Astraeon** (AI answers with sources), **About**. The theme (dark, fonts, colours) is in `.streamlit/config.toml`. Deployed on Streamlit Community Cloud with `app.py` as the main file.

### Ask Astraeon (RAG)

`astraeon/rag.py` turns the data files into 73 short passages (one per experiment, each section of `DATA_NOTES.md` and `RANKINGS_NOTES.md`, each incident, research gap, atmosphere and glossary term, plus a computed dataset overview). For each question it picks the 8 best passages with BM25 keyword search and sends them to Google Gemini, numbered. Gemini is told to answer only from those passages, cite them as [1], [2], ..., and say when the data doesn't cover a question. The app turns those numbers into the source list under each answer and drops any number that doesn't match a passage.

- **API key (free tier):** get a Gemini API key from Google AI Studio. Never commit it.
  - Locally: put it in `.env` in the project root (git-ignored): `GEMINI_API_KEY=your-key-here`
  - On Streamlit Community Cloud: app ⋯ → Settings → Secrets: `GEMINI_API_KEY = "your-key-here"`
  - Optional: `GEMINI_MODEL` (default `gemini-3.8-flash`, a stable model on the free tier)
- **Without a key** the page still works as a search: it shows the closest passages instead of an answer.
- **Limits:** 20 questions per browser session and 500 characters per question, to stay inside the free quota. On the free tier, Google may use prompts to improve its products (all data here is public NASA data).

### Docs & Scripts

| File | Description | Owner |
|---|---|---|
| `data/DATA_NOTES.md` | Column definitions, unit conversions, Moon-base finding, completeness, and how the data was checked for `investigations.csv` | **Person 1** |
| `validate_csv.py` | Checks `investigations.csv` structure and allowed values | **Person 1** |
| `data_report.py` | Prints completeness counts and the Moon-base screen for `investigations.csv` | **Person 1** |
| `data/moon_tests.csv` | One row per flight test with chamber oxygen and pressure (746 tests from PSI). For the oxygen vs. pressure chart with the Moon-base zone | **Person 1** |
| `build_moon_tests.py` | Rebuilds `data/moon_tests.csv` by downloading the experiment tables from NASA PSI (needs internet) | **Person 1** |
| `astraeon/data.py` | Data layer for the app: `load_all()` joins every file by id into one table; `show()` turns blanks into "Not reported" | **Person 1 + Person 3** |
| `astraeon/charts.py` | Ready-made charts: `moon_chart()` (oxygen vs. pressure with the Moon-base zone), `rank_chart()` (scores for one setting) | **Person 1** |
| `astraeon/ui.py` | Streamlit pieces shared by the pages: cached loaders, badges, experiment cards, the details dialog | **Person 1** |
| `astraeon/rag.py`, `app_pages/ask.py` | Ask Astraeon: passages from the data files, BM25 retrieval, Claude answers with citations | **Person 1** |
| `app.py`, `app_pages/`, `.streamlit/config.toml` | The dashboard: navigation, the seven pages, the theme | **Person 1** |
| `data/moon_evidence.csv` | One Moon-evidence badge per experiment (confirmed, near miss, not confirmed, ...) with a one-line reason | **Person 1** |
| `data/images.csv`, `assets/images/` | Real experiment photos from PSI, only those with a stated license (CC0-1.0) | **Person 1** |
| `data/timeline.csv` | Investigation start and end dates and flight platform from PSI | **Person 1** |
| `data/atmospheres.json` | Preset atmospheres for the explorer: normal air and NASA's 10.2 and 8.2 psia exploration atmospheres (quoted from PSI-20), plus the Moon-base limit (challenge brief) | **Person 1** |
| `build_psi_extras.py` | Rebuilds `images.csv`, `assets/images/` and `timeline.csv` from NASA PSI (needs internet) | **Person 1** |
| `data/summaries.json` | Plain-language summary, why it matters, `moon_status` badge and `moon_takeaway` per experiment | **Person 3** |
| `data/glossary.json` | 24 terms with one-sentence definitions, for hover help | **Person 3** |
| `data/incident_summaries.json` | Apollo 1, Apollo 13 and the Mir fire: date, summary, related experiments, sources | **Person 3** |
| `data/research_gaps.json` | What the data can't tell us yet: 4 gaps with title, summary, evidence and related experiments (`load_research_gaps()`) | **Person 3** |

### Using the data in the Streamlit app

Pages import the data layer instead of reading files themselves, so every page shows the same numbers:

```python
import streamlit as st
from astraeon.data import load_all, load_glossary, show, SCORE_COLUMNS, MOON_NOTE
from astraeon.charts import moon_chart, MOON_CHART_ALT

@st.cache_data
def get_experiments():
    return load_all()        # one row per experiment: data + rankings + summaries + badge + photo

df = get_experiments()
st.vega_lite_chart(moon_chart(), alt=MOON_CHART_ALT)
st.caption(MOON_NOTE)
for _, row in df.iterrows():
    with st.container(border=True):
        if row["image_file"]:
            st.image(row["image_file"], caption=row["image_credit"], alt=f"Photo from {row['short_name']}", width="stretch")
        st.subheader(row["short_name"])
        st.badge(row["moon_status_label"], color=row["moon_status_color"])   # Person 3's moon_status
        st.caption(row["moon_takeaway"])
        st.text(f"Pressure: {show(row['pressure_psi'])}")
```

**Atmosphere explorer:** `tests_near(o2_percent, pressure_psi)` returns the real flight tests within ±3 points of oxygen and ±1.5 psi, and `moon_chart(selected=(o2, psi))` draws that box on the chart. `load_atmospheres()` gives the presets. `preview_data.py` has a working explorer (preset buttons, two sliders, chart, table) to copy into a page.

`load_glossary()` returns Person 3's `{term: definition}` for hover help. `load_incidents()` returns the three incidents oldest first, each with `related_names` for linking to experiment cards.

Notes for the app:
- For an oxygen filter, use the numeric `o2_min` / `o2_max` columns, not `o2_percent` (that one is text). Keep "not reported" experiments visible.
- `o2_max` = 85 for `acme_cfig` and `acme_flamedesign` is burner-flow oxygen, not cabin air.
- Only 4 experiments have photos. Give the others a fallback card (for example the topic colour).
- Streamlit 1.67: `use_container_width` is deprecated (use `width="stretch"`); for multipage apps use `st.navigation` with an `app_pages/` folder, not `pages/`.
- To check the data layer in Streamlit (in GitHub Codespaces): `pip install streamlit`, then `streamlit run preview_data.py`.

---

## 🛠️ Data Validation

Run the dataset validator from the project root:

```bash
python validate_csv.py
```

Run it before every push. It checks every data file together:

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
