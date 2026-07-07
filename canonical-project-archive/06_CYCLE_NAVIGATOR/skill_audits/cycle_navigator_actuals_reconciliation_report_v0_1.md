# Cycle Navigator Actuals Reconciliation Report v0.1

Date: 2026-07-07  
Status: ACTIVE RECONCILIATION RULE / PARTIAL SOURCE CONFLICT RESOLVED BY CANONICAL POLICY  
Scope: W22, W23, W24, W25, W27 actual weekly ranges for Cycle Navigator / Master Monday skill audit.

---

## 1. Executive decision

Actual-range conflicts are fixed by separating **canonical framework actuals** from **source-basis variants**.

Going forward:

1. User-verified final framework runs are canonical for framework/Cycle Navigator scoring.
2. Alternative Yahoo / Binance CEST / CoinGecko / custom extraction values are preserved as source-basis variants.
3. Different source/time-basis values are not overwritten and not treated as errors by default.
4. If no user-verified final framework run exists, the row remains `ACTUALS_UNRESOLVED`.
5. Final public track-record updates must cite which actual basis was used.

This removes the blocking conflict for internal provisional scoring while preserving audit transparency.

---

## 2. Canonical actuals policy

### 2.1 Canonical framework actual

Use label:

`CANONICAL_FRAMEWORK_ACTUAL_USER_VERIFIED`

This means:

- user explicitly verified or corrected the range
- run ID exists in project memory/context
- row is intended as framework actual for Forecast Ledger / Weekly RAW / Cycle Navigator audit

### 2.2 Source-basis variant

Use label:

`SOURCE_BASIS_VARIANT`

This means:

- value may be valid for a different source or time basis
- value must be preserved
- value does not overwrite canonical framework actual

Examples:

- Yahoo weekly range
- Binance CEST daily klines
- CoinGecko 7D range
- FMP composite OHLC

### 2.3 True conflict

Use label:

`TRUE_CONFLICT_REQUIRES_SOURCE_FILE`

Only when two values both claim to be the same final framework run and cannot be separated by source/time basis.

---

## 3. Reconciled actuals table

| Week | Date span | Canonical BTC low | Canonical BTC high | Canonical ETH low | Canonical ETH high | Canonical source/run | Alternative variants | Reconciliation status | Scoring permission |
|---|---|---:|---:|---:|---:|---|---|---|---|
| W22 | 2026-05-25 to 2026-05-31 | 72,785.65 | 77,664.65 | 1,974.80 | 2,134.24 | USER_VERIFIED_MEMORY / Cycle Navigator actuals | Yahoo CSV variant: BTC 72,435.63–77,990.87; ETH not independently reconciled here | CANONICAL_ACCEPTED_WITH_VARIANT | PROVISIONAL_SCORE_OK_CANONICAL_ONLY |
| W23 | 2026-06-01 to 2026-06-07 | 59,353.42 | 73,797.23 | 1,522.58 | 2,012.52 | WEEKLY_RANGE_2026_23_20260607_2359 / CoinGecko user-verified | Possible BTC high 73,876.61; Yahoo CSV variant 59,108.92–73,969.57 | CANONICAL_ACCEPTED_WITH_VARIANT | PROVISIONAL_SCORE_OK_CANONICAL_ONLY |
| W24 | 2026-06-08 to 2026-06-14 | 60,756.69 | 65,248.23 | 1,613.83 | 1,716.82 | WEEKLY_RANGE_2026_24_20260614_2155 / CoinGecko-Yahoo final user verified | Yahoo CSV BTC high variant 64,700.88; BTC low matches | CANONICAL_ACCEPTED_WITH_VARIANT | PROVISIONAL_SCORE_OK_CANONICAL_ONLY |
| W25 | 2026-06-15 to 2026-06-21 | 62,201.14 | 67,248.13 | 1,670.10 | 1,847.77 | WEEKLY_RANGE_2026_25_20260622_0845 / Yahoo Finance corrected final user verified | Earlier CoinGecko snapshot WEEKLY_RANGE_2026_25_20260621_0600: BTC 62,303.96–67,203.74; ETH 1,677.17–1,843.46 | CANONICAL_FINAL_SUPERSEDES_EARLIER_SNAPSHOT | PROVISIONAL_SCORE_OK_CANONICAL_ONLY |
| W27 | 2026-06-29 to 2026-07-05 | 57,778.72 | 63,403.77 | 1,549.83 | 1,802.38 | WEEKLY_RANGE_2026_27_20260705_2010 / CoinGecko 7D Range / CoinGecko-Yahoo OHLC user verified | Binance CEST pack: BTC 57,800.19–63,461.99; ETH 1,548.37–1,807.65 | CANONICAL_ACCEPTED_WITH_CEST_VARIANT | PROVISIONAL_SCORE_OK_CANONICAL_ONLY |

---

## 4. Week-by-week notes

### W22

Canonical row:

- BTC low: 72,785.65
- BTC high: 77,664.65
- ETH low: 1,974.80
- ETH high: 2,134.24

Alternative:

- Yahoo BTC variant: 72,435.63–77,990.87

Decision:

Use user-verified memory/CN actuals as canonical for framework scoring. Preserve Yahoo variant as different extraction basis.

Status:

`CANONICAL_ACCEPTED_WITH_VARIANT`

---

### W23

Canonical row:

- BTC low: 59,353.42
- BTC high: 73,797.23
- ETH low: 1,522.58
- ETH high: 2,012.52
- Run ID: WEEKLY_RANGE_2026_23_20260607_2359

Alternative variants:

- possible BTC high: 73,876.61
- Yahoo BTC variant: 59,108.92–73,969.57

Decision:

Use user-verified CoinGecko run as canonical. Preserve alternative highs as source-basis variants.

Status:

`CANONICAL_ACCEPTED_WITH_VARIANT`

---

### W24

Canonical row:

- BTC low: 60,756.69
- BTC high: 65,248.23
- ETH low: 1,613.83
- ETH high: 1,716.82
- Run ID: WEEKLY_RANGE_2026_24_20260614_2155

Alternative:

- Yahoo CSV BTC high: 64,700.88
- BTC low matches at 60,756.69

Decision:

Use user-verified CoinGecko/Yahoo final row as canonical. Mark Yahoo high as extraction/time-basis variant unless original row proves same-basis conflict.

Status:

`CANONICAL_ACCEPTED_WITH_VARIANT`

---

### W25

Canonical row:

- BTC low: 62,201.14
- BTC high: 67,248.13
- ETH low: 1,670.10
- ETH high: 1,847.77
- Run ID: WEEKLY_RANGE_2026_25_20260622_0845
- Source basis: Yahoo Finance corrected final user-verified

Earlier snapshot:

- Run ID: WEEKLY_RANGE_2026_25_20260621_0600
- BTC: 62,303.96–67,203.74
- ETH: 1,677.17–1,843.46

Decision:

Use 2026-06-22 08:45 corrected final as canonical. The 2026-06-21 06:00 CoinGecko row is an earlier snapshot and is superseded.

Status:

`CANONICAL_FINAL_SUPERSEDES_EARLIER_SNAPSHOT`

---

### W27

Canonical row:

- BTC low: 57,778.72
- BTC high: 63,403.77
- ETH low: 1,549.83
- ETH high: 1,802.38
- Run ID: WEEKLY_RANGE_2026_27_20260705_2010

Alternative:

- Binance CEST pack: BTC 57,800.19–63,461.99; ETH 1,548.37–1,807.65
- FRED_MARKET_WEEKLY_BACKTEST_W27_20260706 / Binance CEST daily klines context

Decision:

Use user-verified CoinGecko/CoinGecko-Yahoo row as canonical for framework scoring. Preserve Binance CEST as an exchange/time-basis variant.

Status:

`CANONICAL_ACCEPTED_WITH_CEST_VARIANT`

---

## 5. Updated scoring rule

For provisional Cycle Navigator skill audit:

- use only canonical framework actuals listed above
- include `actual_basis = CANONICAL_FRAMEWORK_ACTUAL_USER_VERIFIED`
- include `variant_actuals_available = TRUE` if alternatives exist
- include `variant_note` in audit row
- do not mix canonical and variant values in one score

If a public post used a different time basis at publication, create a separate scoring row:

- `SCORE_CANONICAL_FRAMEWORK_ACTUAL`
- `SCORE_SOURCE_VARIANT_ACTUAL`

But do not average them.

---

## 6. Rows now unblocked for provisional audit

Using canonical framework actuals, the following can be provisionally scored if forecast/evaluation source is also sufficient:

- CN #2
- CN #3
- CN #4
- CN #5
- CN #6
- CN #7
- Master Monday W25 reconstructed/canonical actual comparison where source row permits

Still blocked:

- final public track record update
- any row without exact forecast window
- any row relying only on memory-only forecast
- CN #8 until next-week evaluation or actuals for May 18–24 are found
- MM W28 until W28 actuals are final

---

## 7. Required fields for audit rows

Every scored row must state:

- forecast_source
- evaluation_source if used
- actual_basis
- actual_run_id
- actual_source_type
- variant_actuals_available
- variant_values
- scoreable_status
- scoring_scope

Allowed scoring scope labels:

- PROVISIONAL_CANONICAL_ACTUALS_ONLY
- SOURCE_VARIANT_COMPARISON_ONLY
- NOT_FOR_PUBLIC_TRACK_RECORD
- FINAL_PUBLIC_TRACK_RECORD_READY

Current global status:

`PROVISIONAL_CANONICAL_ACTUALS_ONLY / NOT_FOR_PUBLIC_TRACK_RECORD`

---

## 8. Governance conclusion

The actuals conflict is fixed enough for provisional internal audit.

It is not fixed enough for final public track-record update.

The correct path is now:

1. Run provisional CN skill audit on source-backed subset using canonical framework actuals.
2. Preserve all variants in notes.
3. Do not update public track record until actual basis and forecast source basis are both explicit.

No market call.
No portfolio action.
No rule ratification.
