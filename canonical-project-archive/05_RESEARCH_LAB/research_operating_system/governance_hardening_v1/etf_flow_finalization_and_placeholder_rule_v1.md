# ETF Flow Finalization and Placeholder Rule v1

Date: 2026-07-07  
Status: ACTIVE ETF DATA-GOVERNANCE RULE  
Source basis: Custom GPT Sensor Supplement 2026-07-07 + Fable P1b Farside ingestion notes.

---

## 1. Purpose

This file defines how ETF flow rows must be treated in DATA PING, replay and ETF-flow research.

It exists because archive dumps may contain placeholder rows, pending rows or rows later superseded by finalized public Farside values.

The key risk is scoring a placeholder `0.0` row as if it were a finalized ETF flow print.

---

## 2. Core rule

`Pending or placeholder ETF rows are not final ETF flow data.`

A replay or study must distinguish:

- pending row
- placeholder row
- partial row
- finalized row
- revised/superseded row

Missing or pending ETF data must never be treated as neutral.

---

## 3. Source hierarchy

Preferred source hierarchy for ETF flow research:

1. Finalized Farside public table row.
2. Verified archive dump reconciled against finalized Farside row.
3. Cross-check source such as SoSoValue/CoinDesk for validation only.
4. Manual pasted/screenshot row, context only unless reconciled.
5. Placeholder archive dump row, not scoreable.

Farside public table is treated as high-quality public table, not official API.

---

## 4. ETF row status labels

| Label | Meaning | Can score? |
|---|---|---|
| FINALIZED | Completed trading-day row confirmed by public table. | Yes. |
| PENDING | Trading day not yet final or print not complete. | No. |
| PLACEHOLDER_ZERO | Row shows 0.0 or blank because final value not yet populated. | No. |
| PARTIAL | Intra-day or incomplete row. | No, context only. |
| REVISED | Row changed after initial archive capture. | Yes, but log revision. |
| MISSING | No data available. | No; not neutral. |
| CONFLICT | Sources disagree materially. | No until reconciled. |

---

## 5. 06 Jul 2026 case rule

Custom GPT identified a specific issue:

- archive dump row showed 06 Jul placeholder 0.0
- later live Farside row showed BTC ETF +265.7M
- later live Farside row showed ETH ETF +20.7M

Therefore:

`06 Jul 2026 placeholder 0.0 must not be scored as final.`

For replay:

- before finalized row was known: mark PENDING or PLACEHOLDER_ZERO
- after finalized row was known: use FINALIZED value, but only for as-of timestamps after finalization
- if exact finalization timestamp is unknown: mark ASOF_FINALIZATION_UNKNOWN and avoid using row for intraday replay classification

---

## 6. Latest completed trading day rule

ETF flow status in DATA PING should use latest completed and finalized trading day.

If current day is not finalized:

- print: PENDING
- trend: use latest finalized sequence only
- streak: do not include pending/placeholder row
- data quality: PARTIAL or MEDIUM depending on other sources

---

## 7. Flow feature construction rules

Allowed ETF features after finalization:

- latest finalized print
- trailing 3-day net flow
- trailing 5-day net flow
- trailing 7-day net flow
- trailing 10-day net flow
- negative/positive streak
- improvement vs prior window
- BTC ETF / ETH ETF separation

Forbidden:

- using pending row in trailing windows
- using placeholder 0.0 as neutral/no-flow day
- mixing BTC and ETH ETF flows into one status without separate labels
- using future finalized value for earlier as-of row

---

## 8. Replay treatment

Every replay row with ETF data must include:

- etf_source
- etf_row_date
- etf_row_status
- etf_finalization_status
- etf_print_latest
- etf_trailing_window_used
- etf_asof_allowed true/false

If ETF finalization status is unclear:

`ETF_FINALIZATION_UNKNOWN`

If the row is placeholder:

`ETF_PLACEHOLDER_DO_NOT_SCORE`

---

## 9. Conflict handling

If Farside, archive dump and cross-check source disagree:

1. Do not choose the most convenient value.
2. Mark `ETF_SOURCE_CONFLICT`.
3. Prefer finalized Farside public table if as-of timing allows.
4. Preserve old value as archive capture, not final truth.
5. Do not score until conflict is resolved.

---

## 10. Framework language rules

Allowed:

- ETF improving
- ETF pending
- ETF finalized positive/negative
- ETF trend unresolved
- ETF flow context supportive/unsupportive

Not allowed:

- ETF confirmed recovery alone
- ETF confirms rebuy
- ETF confirms rotation
- placeholder row treated as neutral
- pending row treated as trend reset

---

## 11. Governance conclusion

ETF flow is a high-value input, but only when finalization state is explicit.

This rule must be applied before:

- ETF stabilization study
- no-hindsight replay
- DATA PING source scoring
- flow-conditioned persistence tests

No ETF row may drive framework interpretation unless its as-of availability and finalization status are known.
