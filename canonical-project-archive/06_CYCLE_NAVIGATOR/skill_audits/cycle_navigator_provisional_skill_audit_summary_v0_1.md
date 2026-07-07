# Cycle Navigator Provisional Skill Audit Summary v0.1

Date: 2026-07-07  
Status: PROVISIONAL_SOURCE_BACKED_SUBSET_NOT_FINAL_TRACK_RECORD  
Scope: CN #2 to CN #7, plus CN #8 as not-scoreable forecast-only row.

---

## 1. Executive conclusion

The source-backed subset shows that Cycle Navigator had meaningful early directional/regime usefulness, especially on phase and rotation, but price-range skill is mixed and must not be overclaimed.

The strongest rows are:

- CN #4: full BTC containment, efficient range, strong phase/rotation match.
- CN #6: strong BTC overlap, efficient width, phase/rotation match.
- CN #7: strongest source-backed BTC+ETH row, but both BTC and ETH had low-side breaches.

This is not a final track record.

Current permission:

`PROVISIONAL_CANONICAL_ACTUALS_ONLY / NOT_FOR_PUBLIC_TRACK_RECORD`

---

## 2. Scoreable subset

Rows provisionally assessed:

- CN #2
- CN #3
- CN #4
- CN #5
- CN #6
- CN #7

Not scored:

- CN #1: tracking begins next week / independent actual missing
- CN #8: forecast exists, but next-week evaluation or actuals missing
- Master Monday W28: actuals not yet available

---

## 3. BTC range audit snapshot

| Row | Forecast | Actual | Containment | Breach | Jaccard | Width ratio | Displayed score |
|---|---:|---:|---|---|---:|---:|---:|
| CN #2 | 65K-72K | 66K-71K | FULL | None | 0.714 | 1.400 | 88 |
| CN #3 | 66K-73K | 69K-76K | PARTIAL | High-side | 0.400 | 1.000 | 83 |
| CN #4 | 73K-79K | 74K-78.5K | FULL | None | 0.750 | 1.333 | 86 |
| CN #5 | 76.5K-83.5K | 75.4K-80.3K | PARTIAL | Low-side | 0.469 | 1.429 | 85 |
| CN #6 | 79K-83.5K | 78.5K-82.5K | PARTIAL | Low-side | 0.700 | 1.125 | 92 |
| CN #7 | 79.5K-84K | 77.6K-82.3K | PARTIAL | Low-side | 0.438 | 0.957 | 91 |

Preliminary read:

- BTC full containment: 2 / 6 rows.
- BTC partial breach: 4 / 6 rows.
- No full miss in this subset.
- Most misses after CN #5 are low-side breaches, meaning forecasts were somewhat too high during BTC-led absorption/chop.
- Range widths are generally efficient, not merely huge bands.

---

## 4. ETH range audit snapshot

Only CN #7 is currently scoreable with both ETH forecast and ETH actual.

CN #7 ETH:

- Forecast: 2.28K-2.48K
- Actual: 2.16K-2.37K
- Containment: PARTIAL_BREACH
- Breach: LOW_SIDE_BREACH
- Jaccard: 0.281
- Width ratio: 0.952

Interpretation:

ETH forecast was too high in CN #7, but width efficiency was not inflated. The issue was level/center, not band width.

---

## 5. Phase / rotation audit snapshot

Phase/rotation performance appears stronger than pure price-range performance.

Observed:

- CN #3 to CN #7 mostly match Early Bull Attempt / Early Bull BTC-led structure.
- Rotation calls stayed conservative: No Rotation / no sustained rotation.
- CN #7 correctly kept No Rotation despite ETH stabilization attempts.

This supports the framework’s known strength:

`structure/regime calls > exact price range precision`

But this remains provisional and must be tested against a broader sample.

---

## 6. Displayed score vs independent audit caveat

Displayed public scores are not identical to independent range-skill.

Displayed scores likely include:

- weekly range
- intraday blocks
- phase call
- rotation call
- qualitative regime fit

Independent audit must not treat an 88-92% displayed score as pure price-range accuracy.

Early provisional interpretation:

- public scores are directionally defensible for regime/rotation
- pure price-range score should probably be lower/more nuanced than public displayed score in some rows
- CN #7 is a clear example: displayed 91% overall, but BTC/ETH range both had low-side breach

---

## 7. What Fable should test next

Fable should not merely recompute these rows.

It should audit:

1. Whether displayed CN scores are inflated relative to independent range-skill.
2. Whether phase/rotation accuracy explains high displayed scores despite price breaches.
3. Whether BTC range skill beats dumb baselines.
4. Whether low-side breach clustering after CN #5 reveals systematic bullish bias.
5. Whether CN #12 scoring upgrade should be back-tested on CN #2-#11 as independent overlay only.
6. Whether source-backed X posts and GitHub archive rows are internally consistent.

---

## 8. Governance conclusion

Cycle Navigator now has enough source-backed rows for a Fable research pass.

Do not publish a final track record yet.

Best next step:

`FABLE_CYCLE_NAVIGATOR_SKILL_AUDIT_V0_1`

No market call.
No portfolio action.
No rule ratification.
