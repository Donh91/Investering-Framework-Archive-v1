# Claude OTA source record — H7 row 11 and settled F1 boundary stress

```yaml
source_run_timestamp_utc: 2026-08-02T06:14:13.076Z
operating_mode: STANDALONE_OTA
reference_bridge_present: NO
reference_data_ping_run_id: NOT_PROVIDED
source_authority: NONCANONICAL_RESEARCH_AND_EXPERIMENT_EVIDENCE
matured_source_experiment_count: 1
canonical_effect_claimed_by_source: NONE
portfolio_effect_claimed_by_source: NONE
```

## H7 row 11 supplied evidence

```yaml
CEST_date: 2026-08-01
BTCUSDT_close: 62812.75
ETHUSDT_close: 1845.78
ETHBTC_close: 0.02938
BTC_1D_pct: -0.21
ETH_1D_pct: -0.86
ETH_minus_BTC_pp: -0.65
relative_leader: BTC
COND2_last_3_ETH_lead_count: 0
COND2_status: NOT_MET
rolling_5_session_OLS_pct_per_session: -0.517
prior_rolling_slope_pct_per_session: -0.395
```

Raw-row receipts supplied:

```json
{
  "BTCUSDT": {
    "raw_close": "62812.75000000",
    "raw_row_sha256": "0e21d707cfb10fd59e9d3824587caa98d19620f9f71f8b96dcc321278daf3b4a"
  },
  "ETHUSDT": {
    "raw_close": "1845.78000000",
    "raw_row_sha256": "e77df860bd15b0bd5711d2220ebfd6196ec5de75b40ca3ca0e7c04b651f17f5e"
  },
  "ETHBTC": {
    "raw_close": "0.02938000",
    "raw_row_sha256": "b63507b5e0957eea9041ffa78dbc3a1feb504af4b717cd4fa76b1808da564dc0"
  }
}
```

The source describes this as a third maturity with a fallen signal. Framework reconciliation must instead apply the frozen experiment governance: the original five-row maturity has already occurred, so row 11 is a post-maturity extension observation and cannot create a new canonical maturity or rescore the historical result.

## H7 arc-derived feature

```yaml
first_settled_CEST_close_supplied: 0.02933
row_11_settled_CEST_close: 0.02938
endpoint_change_pct_arithmetic_check: 0.1705
source_reported_change_pct: 0.17
source_reported_arc_min: 0.02889
source_reported_arc_max: 0.03007
```

The endpoint arithmetic is internally consistent. The complete eleven-row series was not included in this source record, so the arc minimum and maximum remain source-supplied derived metadata rather than independently reconstructed framework values.

## F1 settled boundary-stress evidence

```yaml
session_date_UTC: 2026-08-01
settled_close: 62823.64
intraday_low: 62275.00
higher_candidate: 62342
lower_candidate: 62200
close_vs_higher_pct: 0.77
low_vs_higher_pct: -0.11
low_vs_lower_pct: 0.12
window_status: CLOSED
rule_basis: SETTLED_CLOSES
score_changed: NO
```

The prior in-progress observation is now settled. Price breached the higher candidate intraday but closed above both candidates. F1 remains final at `NOT_FAILED`; H-WIN-01 remains `UNPROVEN` with `LOW_MODERATE` source confidence.

## ETHBTC threshold sequence

```yaml
2026_07_31_UTC_settled_close: 0.02962
2026_08_01_UTC_settled_close: 0.02937
2026_08_02_UTC_status: IN_PROGRESS
2026_08_02_running_value_supplied: 0.02957
2026_08_02_high_supplied: 0.02965
2026_08_02_low_supplied: 0.02934
threshold_0_0300: NOT_TOUCHED_IN_REPORTED_ROWS
load_bearing_0_0275: NOT_TOUCHED
lowest_low_in_arc_supplied: 0.02923
margin_above_0_0275_supplied: 6.3_PERCENT
```

The source reports five observed sessions without a 0.0300 touch. Governance distinction: four are settled sessions and the fifth is the current in-progress session. The settled sequence remains terminated; the in-progress row has no settled threshold status.

## Source QA

- Cache guard: reported PASS.
- OKX HTTP 503: recorded as an executed failure.
- Four 503 events across six runs are distributed across Kraken, Coinbase and OKX. No venue-specific or egress hypothesis is accepted at this sample size.

## ETF and provenance boundaries

No new ETF session was available over the weekend. Carried-forward evidence remains:

```yaml
BTC_ETF_last_known_session: 2026-07-29
BTC_ETF_last_known_flow_usd_m: 32.1
ETH_ETF_last_known_session: 2026-07-30
ETH_ETF_last_known_flow_usd_m: 12.8
ETH_ETF_7_session_sum_usd_m: -0.7
```

Open items remain BTC ETF 30–31 July, ETH ETF 31 July, prospective H7 lapse/retire/retrigger semantics, ETF AUM denominators, ETHB issuer metadata verification and reference-bridge provenance items.

## Required framework corrections

```yaml
ROW_11_IS_POST_MATURITY_EXTENSION_NOT_THIRD_NEW_MATURITY: REQUIRED
H7_HISTORICAL_SCORE_REMAINS_FROZEN: REQUIRED
NO_FORMAL_LAPSE_RETIREMENT_OR_RETRIGGER_RULE_INVENTED: REQUIRED
FOUR_SETTLED_PLUS_ONE_IN_PROGRESS_SESSION_WITHOUT_0030_TOUCH: REQUIRED
F1_SCORE_REMAINS_NOT_FAILED: REQUIRED
IN_PROGRESS_2026_08_02_ETHBTC_HAS_NO_SETTLED_THRESHOLD_EFFECT: REQUIRED
```
