# Rankings Notes

**File:** `data/rankings.csv` (one row per experiment in `data/investigations.csv`, matched by `id`)
**Owner:** Person 2 (scores and reasons)
**Edited:** November 15, 2026, by Person 1, while Person 2 was unavailable. Every change is listed below. Person 2 can revise any of them.

---

## What the scores mean

Each score runs from **0 to 10**: how directly the experiment's findings apply to fire safety in that setting. 10 means the data applies directly; 0 means it does not apply.

| Column | Setting |
|---|---|
| `score_spacecraft` | A crewed spacecraft in microgravity |
| `score_station` | A space station such as the ISS |
| `score_moon` | A Moon base, which the challenge brief expects to run at **30% oxygen or more and 10.2 psi or less** |
| `score_rover` | A crewed rover |
| `reason` | One sentence on why the experiment matters |

### Rule for `score_moon`

1. **Start from general relevance.** Moon scores usually sit 1–2 points below `score_spacecraft`, because microgravity results don't carry over to lunar gravity, and no PSI experiment ran in partial gravity.
2. **Then adjust for oxygen and pressure evidence**, using `data/DATA_NOTES.md` section 6B:

| Evidence | Moon score | Rows |
|---|---|---|
| Burned at ≥ 30% chamber O2 and ≤ 10.2 psi **in the same test** | 10 | `acme_cfig` |
| Within 0.3 psi of that, or designed around those atmospheres but the pressure of each test isn't recorded | 9 | `flex`, `acme_bre` |
| Oxygen and pressure *ranges* overlap Moon conditions, but nothing ties them to the same test | No bonus (general relevance) | `flex2` |
| High oxygen only at ~1 atm, or oxygen lowered rather than raised | No bonus (general relevance) | `acme_sflame`, `acme_flamedesign`, `bass2` |

---

## Changes from Person 2's original sheet

| `id` | Column | Before → After | Why |
|---|---|---|---|
| `acme_cfig` | `score_moon` | 8 → 10 | Only confirmed test-by-test match to Moon conditions |
| `acme_bre` | `score_moon` | 10 → 9 | Targeted 8.2 psia / 34% O2, but the pressure of each test isn't recorded |
| `flex` | `score_moon` | 10 → 9 | Near miss: 17 tests at 30–34% O2 ran at 10.3–10.5 psi |
| `flex2` | `score_moon` | 10 → 8 | Ranges overlap only, so no evidence bonus (spacecraft score − 1) |
| `acme_sflame` | `score_moon` | 9 → 8 | ~30% O2 tests ran at ~1 atm, so no evidence bonus (spacecraft score − 1) |
| `bass2` | `score_moon` | 9 → 8 | Oxygen was lowered (13.6–22.2%), so no oxygen bonus; now equal to `bass` |
| `acme_efield` | all four scores | 9 / 10 / 9 / 8 → 8 / 9 / 6 / 6 | It was scored as a partial-gravity analogue, which PSI-22 doesn't support; PSI-22 says it "is not being conducted to serve any space applications." It used the same coflow burner as `acme_cld` (PSI-22), so it now has the same scores as `acme_cld` |
| `acme_cfig` | `reason` | rewritten | Now mentions the Moon-condition tests and that they used gas fuels |
| `acme_bre` | `reason` | rewritten | Now says the pressure of each test isn't recorded |
| `flex` | `reason` | rewritten | Now mentions the 0.3 psi near miss |
| `saffire1` | `reason` | "realistic crew-habitat materials" → "SIBAL cotton-fiberglass fabric" | Matches `investigations.csv` |

All other scores and reasons are Person 2's originals, unchanged.

---

## Open questions for Person 2

- **Spacecraft vs. station vs. rover:** the setting descriptions above are inferred from the column names. Please confirm or correct them.
- **`daft`:** rover 8 but Moon 5. Is that deliberate (for example, rover air sampling vs. lunar dust)? If so, add it to the reason.
