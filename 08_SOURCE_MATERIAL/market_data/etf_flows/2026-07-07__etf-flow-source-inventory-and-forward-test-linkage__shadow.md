# ETF Flow Source Inventory + Forward Test Linkage

**Dato:** 2026-07-07  
**Status:** SHADOW_SOURCE_INVENTORY / FORWARD_TEST_LINKAGE  
**Område:** ETF flows, DATA PING, price range backtest linkage, GATE-BTC-PARTIAL FT-1, Gradueret Deployment v1.1  
**Primær arkivplacering:** `08_SOURCE_MATERIAL/market_data/etf_flows/`  

---

## 1. Executive verdict

**READY_WITH_MISSING_DATA**

Dette er ikke en gemt prompt.

Dette er en eksekveret source-inventory og arkivplaceringsvurdering for ETF-flow data i relation til forward-testen:

- GATE-BTC-PARTIAL FT-1
- GRADUERET DEPLOYMENT v1.1

Konklusion:

ETF-flow-data er allerede korrekt forankret som DATA PING source integration via Farside-ledgeren.
Denne mappe, `08_SOURCE_MATERIAL/market_data/etf_flows/`, skal bruges til raw/source-material, API extracts, historical ETF-flow dumps og datagrundlag.

Custom-filerne fra price range extractor hører ikke direkte i `etf_flows`, fordi de ikke er ETF-flow data. De er arkiveret under:

```text
08_SOURCE_MATERIAL/market_data/price_ranges/
```

De supplerer ETF-flow forward-testen som pris-, range-, ETH/BTC- og benchmarklag.

---

## 2. Correct archive placement map

### A. ETF flow data

Placering:

```text
08_SOURCE_MATERIAL/market_data/etf_flows/
```

Indholdstype:

- raw BTC ETF-flow extracts
- raw ETH ETF-flow extracts
- raw SOL ETF-flow extracts
- Farside / SoSoValue / cross-check dumps
- CSV / JSON / markdown source tables
- source snapshots used for backtests or forward tests

Governance:

ETF-flow data er DATA_ONLY.

Det må understøtte:

- DATA PING ETF-flow block
- RAW 1–3D confidence
- RAW 5–7D confidence
- Master Monday flow calibration
- Early Rotation Watch diagnostics
- FNP opportunity-cost visibility

Det må ikke alene bestemme:

- recovery confirmed
- rotation confirmed
- rebuy unlocked
- deployment
- official row
- Cycle Navigator score

---

### B. ETF flow source-integration policy

Placering:

```text
02_DATA_PING/source_integrations/
```

Aktiv canonical fil:

```text
02_DATA_PING/source_integrations/2026-07-06__farside-etf-flow-ledger-data-ping-integration__canonical.md
```

Formål:

Denne fil fastlægger Farside som primær machine-readable ETF-flow source og definerer print-vs-trend, BTC/ETH/SOL flow-blocks, cross-check, market calendar rules og governance boundary.

---

### C. Price range / OHLC backtest data

Placering:

```text
08_SOURCE_MATERIAL/market_data/price_ranges/
```

Arkiverede Custom-filer:

```text
08_SOURCE_MATERIAL/market_data/price_ranges/DATA_PING_BACKTEST_PRICE_RANGE_EXTRACTOR_v1.py
08_SOURCE_MATERIAL/market_data/price_ranges/DATA_PING_BACKTEST_PRICE_RANGE_EXTRACTOR_README.md
```

Formål:

Disse filer supplerer ETF-flow forward-testen med:

- BTC daily price ranges
- ETH daily price ranges
- ETH/BTC direct ledger
- BTC/ETH relative strength
- reclaim/failure counting
- ATR / range / close persistence
- forward outcome windows for supervised backtests

Boundary:

Price range extractoren er DATA_ONLY.
Den må ikke selv afgøre recovery, rotation, rebuy, deployment, official row eller portfolio action.

---

## 3. Source inventory

### ETF-flow source status

Current canonical ETF-flow integration:

```yaml
ETF_FLOW_PRIMARY_SOURCE:
  provider: Farside API
  status: PRIMARY_MACHINE_READABLE_SOURCE
  use_case: ETF flow ledger / print-vs-trend / persistence
```

Latest archived ETF-flow context as of 2026-07-06:

```yaml
BTC_ETF:
  latest_print_date: 2026-07-02
  latest_print: +223.5M
  W27_net: -526.1M
  trailing_3D: -295.1M
  trailing_5D: -970.6M
  trailing_7D: -2131.3M
  read: POSITIVE_PRINT_BUT_TREND_NOT_CONFIRMED

ETH_ETF:
  latest_print_date: 2026-07-02
  latest_print: +29.0M
  W27_net: -13.7M
  latest_2D: +43.8M
  latest_3D: +16.2M
  latest_5D: -26.5M
  latest_7D: -138.7M
  read: RELATIVELY_STRONGER_THAN_BTC_BUT_NOT_ROTATION_CONFIRMED

SOL_ETF:
  W27_net: +5.7M
  read: SMALL_POSITIVE_SELECTIVE_L1_SHADOW_ONLY
```

Framework state from ETF-flow archive:

```text
Validated de-escalation candidate.
Not confirmed recovery.
Not confirmed rotation.
Rebuy locked pending persistence.
```

---

## 4. Forward-test readiness

### Test 1 — GATE-BTC-PARTIAL FT-1

Readiness:

```yaml
status: READY_WITH_MISSING_DAILY_ROWS
reason: ETF source integration exists, price extractor exists, but full daily forward-test rows from 2026-07-06 onward are not yet present in this source folder.
```

Hypothesis to test:

```text
When STATE = BTC Dominant and ROTATION = No Rotation, maintaining a minimum 10% BTC or BTC/stable tranche may reduce false-negative opportunity cost without meaningfully increasing drawdown versus full WAIT.
```

Required daily fields:

```text
date
BTC price
ETH price
ETH/BTC
BTC dominance
BTC ETF print
BTC ETF 3D/5D/7D trend
ETH ETF print
ETH ETF relative flow read
breadth state
rotation state
DATA PING state
CHIEF state
BTC allocation
stable allocation
alt allocation
cf_state
action taken
reason
no-hindsight evidence used
days_saved_vs_framework_wait
opportunity_cost_vs_wait
running return vs pure BTC
running drawdown
data_quality
missing_fields
```

---

### Test 2 — Gradueret Deployment v1.1

Readiness:

```yaml
status: DESIGN_READY_BUT_RETURN_SCORING_REQUIRES_PRICE_PROXY
reason: Price extractor can provide BTC/ETH/ETHBTC benchmark data, but alt basket proxy must be explicitly selected before return comparison is valid.
```

Tier logic for forward test:

```yaml
TIER_0_WAIT:
  alt_allocation: 0%
  condition: No Rotation / ETH-BTC weak / breadth weak / BTC.D elevated or rising

TIER_1_FIRST_CONFIRMATION:
  alt_allocation: 10%
  bucket: Large caps only
  requires:
    - ETH/BTC stabilization or improvement
    - breadth not deteriorating
    - BTC.D not aggressively reclaiming
    - ETF flow trend not worsening materially
    - no obvious fake-rotation signature

TIER_2_SECOND_CONFIRMATION:
  total_alt_allocation: 35%
  bucket: Large + Mid caps
  requires:
    - ETH/BTC persistence, not spike
    - breadth survival across large + partial mid caps
    - BTC.D deceleration or decline
    - stablecoin deployment / liquidity transmission improving if available
    - post-flush reclaim quality improving if relevant

TIER_3_FULL_CONFIRMATION:
  max_alt_allocation: 65%
  bucket: Large + Mid + selected Small caps
  requires_3_of_3:
    - ETH/BTC persistence
    - breadth survival
    - deployment / flow congruence
  extra_rules:
    - BTC.D must not be in defensive reclaim
    - fake rotation density must be low or falling
    - microcaps excluded unless broad altseason / parabolic phase is confirmed
```

---

## 5. First row status

No new verified 2026-07-06 daily DATA PING row was provided inside this specific archive execution package.

Therefore first forward-test row must be initialized as DATA_MISSING, not simulated.

```text
Date | BTC Price | ETH/BTC | Breadth | Rotation | ETF BTC Trend | BTC Alloc | Stable Alloc | Alt Alloc | cf_state | Action | Notes | Data Quality
2026-07-06 | DATA_MISSING | DATA_MISSING | DATA_MISSING | DATA_MISSING | DATA_MISSING | DATA_MISSING | DATA_MISSING | DATA_MISSING | DATA_MISSING | NO_ACTION | Await verified DATA PING + ETF flow row. Do not simulate. | MISSING
```

---

## 6. Ledger schemas

### Daily forward-test ledger

| Field | Required | Source | Notes |
|---|---:|---|---|
| date | yes | DATA PING / market source | YYYY-MM-DD |
| source_timestamp | yes | DATA PING | no hindsight |
| btc_price | yes | DATA PING / price range extractor | live row or verified daily close |
| eth_price | yes | DATA PING / price range extractor | if unavailable mark missing |
| ethbtc | yes | DATA PING / ETHBTC extractor | direct ETHBTC preferred |
| btc_dominance | yes | DATA PING | do not infer |
| btc_etf_print | yes | ETF flow source | latest verified trading day |
| btc_etf_trend_3d_5d_7d | yes | ETF flow source | print vs trend separation |
| eth_etf_print | optional but preferred | ETF flow source | rotation support only |
| eth_vs_btc_flow_read | yes | ETF flow source | relative support, not confirmation |
| breadth_state | yes | DATA PING | if unavailable mark UNAVAILABLE |
| rotation_state | yes | DATA PING / framework | No Rotation / Watch / Confirmed |
| btc_alloc | yes | test engine | percent |
| stable_alloc | yes | test engine | percent |
| alt_alloc | yes | test engine | percent |
| cf_state | yes | test engine | PENDING / ARMED / ENTERED / HELD / EXPIRED / FAILED / DATA_MISSING |
| action | yes | test engine | NO_ACTION / ENTER / HOLD / SCALE / EXPIRE / FAIL |
| notes | yes | analyst | concise, evidence-linked |
| data_quality | yes | governance | HIGH / MEDIUM / LOW / MISSING |

### Weekly summary ledger

| Field | Notes |
|---|---|
| week_id | ISO week |
| rows_count | number of daily rows |
| rows_scorable | daily rows with all required data |
| gate_btc_partial_days_active | days with 10% BTC tranche active |
| grad_deployment_tier_max | highest tier reached |
| max_drawdown_test | test strategy drawdown |
| max_drawdown_default | default framework drawdown |
| return_vs_pure_btc | relative return |
| return_vs_framework_wait | relative return |
| fnp_events | count |
| false_positive_events | count |
| decision_divergence | yes/no |
| learning | 1-3 lines |

### FNP / opportunity-cost ledger

| Field | Notes |
|---|---|
| fnp_id | unique row |
| event_start | date |
| default_framework_action | e.g. WAIT |
| test_action | e.g. 10% BTC / 10% large alts |
| divergence_type | BTC_PARTIAL / ALT_TIER / BOTH |
| days_saved_vs_wait | days between test entry and default entry |
| move_captured_pct | percent return captured |
| move_missed_pct | percent return missed by default |
| drawdown_cost_pct | max adverse move from test entry |
| justified_caution | yes/no |
| final_classification | TRUE_FNP / JUSTIFIED_WAIT / UNSCORABLE |

---

## 7. Kill criteria

Retire or suspend the forward test if any of the following occur:

1. Fewer than 10 scorable rows after 21 calendar days.
2. No decision divergence versus default framework after 30 scorable rows.
3. Return comparison remains unscorable because no valid alt proxy is selected.
4. Repeated Tier 1 alt entries fail within 5-12 days due to BTC.D reclaim + breadth failure.
5. Test drawdown exceeds default framework drawdown by more than the pre-defined tolerance without reducing FNP.
6. ETF-flow rows remain unavailable or stale for more than 5 consecutive trading days.
7. Rules require discretionary interpretation in more than 25% of rows.
8. Test begins explaining outcomes without creating ledger rows.

---

## 8. Promotion criteria

No operational promotion is allowed until all of the following exist:

1. Minimum 30 completed daily rows.
2. Minimum 3 actual decision divergences versus default framework.
3. At least 1 completed weekly summary with scorable return comparison.
4. FNP/opportunity-cost rows created where relevant.
5. Drawdown not materially worse than default framework.
6. Opportunity-cost reduction visible in at least one completed sequence.
7. No violation of ETH/BTC + breadth + deployment gates for full alt exposure.
8. Explicit Research Lab review after rows exist.

---

## 9. What not to do

Do not:

- simulate future 30-day rows
- invent missing BTC price, ETH/BTC, breadth or ETF flow values
- treat a single positive ETF print as recovery
- treat ETH ETF relative strength as rotation confirmation
- weaken ETH/BTC or breadth gates for full alt deployment
- mix CEST-like Binance candles with UTC fallback candles without `time_basis`
- use forward-looking outcome columns in live decision logic without shifting
- promote the test before ledger rows exist

---

## 10. Final archive conclusion

ETF-flow data belongs in:

```text
08_SOURCE_MATERIAL/market_data/etf_flows/
```

Price-range extractor data belongs in:

```text
08_SOURCE_MATERIAL/market_data/price_ranges/
```

The current forward-test package is ready as a shadow protocol, but not ready for performance evaluation until live DATA PING rows and ETF-flow rows from 2026-07-06 onward are added.
