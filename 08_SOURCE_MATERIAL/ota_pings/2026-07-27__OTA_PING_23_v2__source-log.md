# OTA PING #23 v2 — source log

```yaml
run_id: OTA_PING_23_v2
run_at_utc: 2026-07-27T05:39:20Z
run_at_cest: 2026-07-27T07:39:20+02:00
anchor_source: BINANCE_SERVER_TIME
anchor_value_ms: 1785130760412
role: SHADOW_NON_BINDING_EVIDENCE
canonical_authority: NONE
framework_state_change_requested: NO
portfolio_action_requested: NO
```

## New source evidence

### H7 prospective rows, settled CEST

| date_cest | BTCUSDT close | ETHUSDT close | direct ETHBTC close | BTC 1D | ETH 1D | ETH minus BTC | leader |
|---|---:|---:|---:|---:|---:|---:|---|
| 2026-07-22 | 66,072.47 | 1,938.76 | 0.02933 | -0.47% | +0.75% | +1.22 pp | ETH |
| 2026-07-23 | 65,169.81 | 1,882.72 | 0.02889 | -1.37% | -2.89% | -1.52 pp | BTC |
| 2026-07-24 | 64,155.00 | 1,857.51 | 0.02896 | -1.56% | -1.34% | +0.22 pp | ETH |
| 2026-07-25 | 64,344.02 | 1,872.65 | 0.02910 | +0.29% | +0.82% | +0.52 pp | ETH |
| 2026-07-26 | 64,858.02 | 1,925.91 | 0.02969 | +0.80% | +2.84% | +2.05 pp | ETH |

Direct ETH/BTC log increments supplied by the run:

```text
-0.01512, +0.00242, +0.00482, +0.02007
```

The final three increments are positive.

### Row-5 receipt excerpts

```yaml
BTCUSDT:
  receipt_id: OTA23-BTCUSDT-20260726-01
  request: symbol=BTCUSDT&interval=1h&startTime=1785099600000&limit=1
  retrieved_at_utc: 2026-07-27T05:39:21.402Z
  open_time_utc: 2026-07-26T21:00:00Z
  close_time_utc: 2026-07-26T21:59:59.999Z
  raw_close: 64858.02000000
  row_status: SETTLED_PROSPECTIVE_VALID
  session_basis: SETTLED_CEST
ETHUSDT:
  receipt_id: OTA23-ETHUSDT-20260726-02
  raw_close: 1925.91000000
  row_status: SETTLED_PROSPECTIVE_VALID
  session_basis: SETTLED_CEST
ETHBTC:
  receipt_id: OTA23-ETHBTC-20260726-03
  raw_close: 0.02969000
  row_status: SETTLED_PROSPECTIVE_VALID
  session_basis: SETTLED_CEST
```

Full row and response hashes were stated as generated but were not reproduced in the submitted text. This is retained as a receipt-completeness follow-up, not as a silent assumption.

## Source-QA event

The producing code disclosed a run-length defect before final reporting:

```python
runA = max(sum(1 for _ in g) for g in groupby(diffs, key=lambda x: x > 0) if g[0])
```

Because each item yielded by `groupby` is `(key, group)`, the expression iterated the two-item tuple rather than the grouped observations and returned two instead of the true run length.

Manual recomputation supplied:

```text
runs = [(False, 1), (True, 3)]
```

The raw rows and pairwise comparisons remain directly inspectable. The defect is archived separately as a source-QA incident.

## Additional observations supplied

```yaml
ETHBTC_2026_07_26_settled_utc: 0.02989
ETHBTC_2026_07_26_settled_cest: 0.02969
ETHBTC_2026_07_27_in_progress_utc: 0.02998
F1_lowest_settled_close_to_date: 64139.99
F1_lowest_intraday_low_to_date: 63739.75
F1_window_end_utc: 2026-07-28T00:00:00Z
```

The post-F4 movement does not reopen F4. The supplied settled-basis divergence is retained as a requirement that any future 0.0300 test pre-register UTC versus CEST basis.

## Claimed counterweights retained

- the largest H7 increment occurred in the Sunday session;
- ETF flows did not confirm the price-led move;
- the supplied AUM-normalised ETH outflow was larger than BTC's;
- the source's own prior `price-led, not flow-led` assessment remains active as counterevidence.

These caveats affect interpretation, not the mechanical H7 condition calculation.
