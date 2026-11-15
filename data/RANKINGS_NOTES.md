# Rankings Notes

**File:** `data/rankings.csv` (one row per experiment in `data/investigations.csv`, matched by `id`)
**Owner:** Person 2 (original scores and reasons)
**Finalized:** November 15, 2026, by Person 1, while Person 2 was unavailable. Every change is listed below with the original value. Person 2 can revise any of them.

---

## What the scores mean

Each score runs from **0 to 10**: how directly the experiment's findings apply to fire safety in that setting. 10 means the data applies directly; 0 means it does not apply.

| Column | Setting |
|---|---|
| `score_spacecraft` | A crewed vehicle in transit (capsule or cargo vehicle) in microgravity |
| `score_station` | A long-duration microgravity station such as the ISS, where most of these experiments flew. This is why `score_station` is never lower than `score_spacecraft` |
| `score_moon` | A Moon base, which the challenge brief expects to run at **30% oxygen or more and 10.2 psi or less** |
| `score_rover` | A small crewed pressurized rover cabin. Rover scores stay within 1 point of Moon scores. They were not adjusted for oxygen and pressure evidence, because the brief gives no rover cabin atmosphere |
| `reason` | One sentence on why the experiment matters |

These setting descriptions were worked out from the pattern of Person 2's original scores.

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
| `acme_cfig` | `reason` | Was: "Explores cool-flame behavior across a wide range of oxygen concentrations in microgravity environments." | Now mentions the Moon-condition tests and that they used gas fuels |
| `acme_bre` | `reason` | Was: "Studies combustion under elevated oxygen concentrations in microgravity, including conditions relevant to future lunar habitats." | Now says the pressure of each test isn't recorded |
| `flex` | `reason` | Was: "Maps flammability limits and evaluates fire-suppression effectiveness across oxygen concentrations in microgravity." | Now mentions the near miss (10.3–10.5 psi vs. the 10.2 psi limit) |
| `saffire1` | `reason` | "realistic crew-habitat materials" → "SIBAL cotton-fiberglass fabric" | Matches `investigations.csv` |
| `daft` | `score_moon` | 5 → 7 | Rover 8 / Moon 5 was the only row breaking the pattern. Same rule as the other detection rows (`same`, `samer`): spacecraft score − 1 |

All other scores and reasons are Person 2's originals, unchanged.
