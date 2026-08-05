# Extended 72H DATA PING Source Record

```yaml
received_local: 2026-08-05T11:59:00+02:00
run_id: run-d0fe59090ade0770962af29d
snapshot_id: snap-8e255215436f5e4f0b3e7fa2
snapshot_utc: 2026-08-05T09:12:51.935761Z
collector_version: 15.2.0
serialization_profile: DATA_PING_COMPACT_ROWSET_v2_EXTENDED_72H
source_authority: USER_SUPPLIED_PACKET_JSON
source_packet_sha256: bc7bf93acc0a88e2f3fbfff446c578e3ff9a3ecc1fc4c768c62fd2230bd8e1fc
source_packet_size_bytes: 240609
requested_window_utc: 2026-08-02T08:42:05.629659Z/2026-08-05T08:42:05.629659Z
requested_window_copenhagen: 2026-08-02T10:42:05.629659+02:00/2026-08-05T10:42:05.629659+02:00
valid_settled_hourly_rows: 71
extension_receipts: 14
invocation_records: 75
framework_interpretation_in_source: DEFERRED_TO_MAIN_FRAMEWORK
```

## Collection and validation

- All 60 core actions were attempted and resolved.
- Core results: 57 PASS, two PARTIAL and one STALE; the optional total-DeFi action was UNAVAILABLE.
- Execution order, invocation/receipt integrity, settled-candle filtering, breadth transform, freeze invariants and strict ASCII validation passed.
- Freeze count was one and post-freeze call count was zero.
- Open or partial boundary candles were excluded; no synthetic or interpolated values were created.
- The exact 72-hour realized-volatility output was correctly left unavailable because the valid interior contains 71 settled candles and 72 close-to-close returns require 73 closes.

## Current owner snapshot

```yaml
BTCUSDT: 64142.97
ETHUSDT: 1871.13
ETHBTC: 0.02917
BTC_open_interest: 107460.261
ETH_open_interest: 2317408.499
BTC_binance_basis_bps: -4.437853
ETH_binance_basis_bps: -4.646153
BTC_binance_minus_OKX_mark_bps: 2.496010
ETH_binance_minus_OKX_mark_bps: 6.791303
```

The direct snapshot is effectively contemporaneous with the existing bounded owner run `run-4e87515bde8846aa9c51`; it is therefore not treated as an independent market-state transition.

## Valid settled-hour sequence

| measure | BTC | ETH | ETH/BTC |
|---|---:|---:|---:|
| first valid hourly open | 63,194.00 | 1,868.19 | 0.02957 |
| last valid hourly close | 64,163.99 | 1,872.20 | 0.02917 |
| sequence return | +1.5349% | +0.2146% | -1.3527% |
| observed low | 62,300.00 | 1,828.62 | 0.02906 |
| observed high | 64,549.16 | 1,898.50 | 0.02978 |
| full high/low range | 3.6102% | 3.8215% | 2.4776% |
| rebound from observed low to final settled close | +2.9920% | +2.3832% | +0.3785% |

Sequence landmarks:

- BTC and ETH printed their window lows during the 2026-08-03 08:00Z hour.
- BTC subsequently repaired almost 3% from its low and finished near the upper part of its window.
- ETH repaired in USD but materially underperformed BTC across the complete sequence.
- ETH/BTC peaked at 0.02978, fell to 0.02906 and ended at 0.02917; the final rebound was small relative to the preceding decline.
- Settled Copenhagen closes progressed from ETH/BTC 0.02973 to 0.02931 to 0.02917.

## Spot taker participation

| measure | BTC | ETH | ETH/BTC |
|---|---:|---:|---:|
| full-window mean buy share | 51.46% | 49.00% | 48.97% |
| hours above 50% | 43/71 | 30/71 | 33/71 |
| last 24h mean | 52.99% | 47.62% | 47.97% |
| last 12h mean | 51.75% | 46.58% | 49.44% |
| last 6h mean | 51.98% | 46.19% | 57.14% |

The final ETH/BTC burst is a short-window rebound. It is not a persistent 12- or 24-hour transmission signal.

## Leverage and positioning sequence

```yaml
BTC_contract_OI_start: 109030.831
BTC_contract_OI_last_settled_hour: 107742.930
BTC_contract_OI_change_pct: -1.1812
BTC_global_long_short_start: 1.8944
BTC_global_long_short_end: 1.2722
BTC_top_account_long_short_start: 1.9326
BTC_top_account_long_short_end: 1.3294

ETH_contract_OI_start: 2302841.160
ETH_contract_OI_last_settled_hour: 2311277.666
ETH_contract_OI_change_pct: +0.3664
ETH_global_long_short_start: 2.3568
ETH_global_long_short_end: 2.3841
ETH_top_account_long_short_start: 1.8620
ETH_top_account_long_short_end: 1.8969
```

BTC repaired while contract OI and long crowding declined. ETH repaired less while OI and long-heavy positioning did not clear. The latest futures taker ratio was 0.9621 for BTC and 0.6986 for ETH.

## Funding and volatility

- Nine settled funding events were retained per asset.
- Latest settled funding: BTC 0.00001015; ETH 0.00000613.
- Latest-three mean funding: BTC 0.0000345767; ETH 0.0000379633.
- Latest 24h/48h annualized realized volatility: BTC 25.32% / 31.31%; ETH 28.31% / 33.43%; ETH/BTC 13.00% / 13.65%.
- The lower 24h readings relative to 48h show recent volatility cooling, not a rotation confirmation.

## ETF, breadth and macro context

```yaml
BTC_ETF_2026_08_03_usd_m: 170.1
BTC_ETF_2026_08_04_usd_m: 211.5
BTC_ETF_two_session_net_usd_m: 381.6
ETH_ETF_2026_08_03_usd_m: -11.9
ETH_ETF_2026_08_04_usd_m: 53.1
ETH_ETF_two_session_net_usd_m: 41.2
BTC_to_ETH_two_session_net_ratio: 9.2621
breadth_membership_hash: db981da7d5002ac7742419b4bcf7d9c022a5b2ab88165ab971228d587aa6a739
breadth_included: 89
breadth_advancers: 36
breadth_decliners: 39
breadth_unchanged: 14
breadth_median_24h_pct: 0.0
breadth_equal_weight_mean_24h_pct: 0.035955
DGS10_minus_DGS2_pct_points: 0.45
VIX_latest: 15.86
broad_dollar_four_observation_change: -1.0705
```

The ETF sequence is positive for both assets but strongly BTC-dominant. Breadth is neutral-fragile rather than expansionary and remains method-incompatible with the locked v1.1 scoring owner.

## Source limitations

- Stablecoin global total remains unresolved; tertiary chain structure is not a valid global-total substitute.
- Optional total DeFi TVL was unavailable due to response size.
- BTC CFGI was stale relative to the requested window.
- Historical Binance mark/index was not registered; hourly Binance-minus-OKX mark differences were not fabricated.
- GeckoTerminal retained two low-reserve anomalies and is diagnostic only.

## Evidence boundary

This record preserves the packet identity, validation result and material 72-hour sequence metrics without claiming a canonical transition. The uploaded `packet.json` remains the raw source authority identified by its SHA-256. The repository record is a relevance-compressed evidence representation, not a replacement or reinterpretation of missing source fields.