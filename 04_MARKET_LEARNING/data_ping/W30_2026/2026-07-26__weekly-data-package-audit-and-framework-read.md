# DATA PING W30 weekly package — audit and framework read

**Package generated:** 2026-07-26T19:41:38Z / 21:41:38 CEST  
**Audit status:** `PASS_WITH_EXPLICIT_BOUNDARIES`  
**Backtest eligibility:** `ELIGIBLE_FOR_VENUE_TAGGED_OKX_HOURLY_REPLAY`  
**Full-week finality:** `NO — PARTIAL_TO_COLLECTION_TIME`  
**Canonical market-state effect:** `NONE`

## 1. Package identity

```yaml
zip_sha256: c0745b6c0b961fd3765ffa051dc6f2d07db611c86654871122e59e6d4f6abe98
zip_bytes: 702169
xlsx_sha256: 8d6727ab3a4a4f6247e34071fa7542b4f53e39794eb4dc324e2bbc8a6cd3b33d
source_file_count: 30
manifest_payload_entries: 29
manifest_exclusion: manifest.json itself
```

The separately supplied workbook is byte-identical to the workbook embedded in the ZIP.

## 2. Structural validation

The package passed the following checks:

- all 29 payload files listed by the manifest exist;
- every listed byte count and SHA-256 matches;
- BTC and ETH each contain 166 hourly rows;
- each series contains 165 settled rows and one partial row;
- timestamps are unique and continuous at exactly one-hour intervals;
- coverage runs from 2026-07-20 00:00 CEST through the 2026-07-26 21:00 CEST bar;
- the last settled bar is 2026-07-26 20:00 CEST;
- raw OKX payload rows reconcile exactly to normalized OHLC and settled flags;
- workbook headline values reconcile to the CSV and JSON files;
- workbook formula-error scan returns zero matches;
- the reported 0.8687927054 hourly-return correlation recomputes exactly from 164 paired settled transitions;
- all five BTC and ETH ETF session totals reconcile, including weekly totals.

Verdict:

```text
STRUCTURE_VALIDATED
+
RAW_NORMALIZED_PARITY_PASS
+
DETERMINISTIC_AGGREGATE_PARITY_PASS
```

## 3. Important boundary: this is not the finished W30 close

The package was generated Sunday at 21:41 CEST.

The latest included bar is the 21:00 CEST bar and is explicitly marked `settled=false`. Statistics use settled rows only and therefore stop at 20:00 CEST.

The package is correctly classified as:

```text
W30_PARTIAL_TO_COLLECTION_TIME
```

It must not later be presented as the complete Sunday close or the final full W30 weekly candle.

## 4. Instrument and venue boundary

Hourly history comes from:

```yaml
venue: OKX
instruments:
  - BTC-USDT-SWAP
  - ETH-USDT-SWAP
bar: 1H
```

This provides high-quality path, range, volatility and relative-performance evidence. It does not become interchangeable with:

- Binance spot history;
- Binance futures history;
- direct ETH/BTC market history;
- spot settlement authority.

Canonical use:

```text
VENUE_TAG_REQUIRED
+
PERPETUAL_SWAP_SERIES
+
NO_SILENT_JOIN_TO_SPOT_OR_BINANCE
```

## 5. W30 price and volatility results

| Metric | BTC | ETH |
|---|---:|---:|
| Week open | 64,385.80 | 1,861.02 |
| Last settled close | 64,709.20 | 1,913.63 |
| Return | +0.50% | +2.83% |
| Full observed range / open | 5.01% | 6.23% |
| Hourly return stdev | 0.302% | 0.384% |
| Maximum close drawdown | -4.43% | -4.91% |
| Distance from observed high at last settlement | -3.32% | -2.21% |
| Recovery from observed low | +1.58% | +3.95% |

ETH outperformed BTC by approximately 2.32 percentage points over the settled package window.

Derived from the two OKX swap series:

```yaml
ethbtc_derived_start: 0.0289042
ethbtc_derived_last_settled: 0.0295728
ethbtc_derived_change: +2.31%
direct_ethbtc_feed: false
```

The high BTC/ETH hourly-return correlation of 0.8688 means ETH leadership remained strongly beta-linked rather than independent broad rotation.

## 6. Path interpretation

The week had three distinct phases:

1. Early-week expansion, with BTC peaking Tuesday and ETH peaking Wednesday.
2. Mid-to-late-week drawdown, with both assets reaching their maximum close drawdown by Saturday morning.
3. A Sunday repair in which ETH recovered more strongly than BTC.

The stronger ETH rebound is real within the OKX series, but it is accompanied by higher realized volatility and remains below the week's ETH high.

Classification:

```text
ETH_RELATIVE_REPAIR
NOT_ETH_TREND_CONFIRMATION
NOT_ROTATION_CONFIRMATION
```

## 7. Flow evidence

Weekly settled US ETF totals:

```yaml
BTC_ETF_W30_USD_M: +33.9
ETH_ETF_W30_USD_M: +103.8
```

The path deteriorated late in the week:

```yaml
BTC_first_3_sessions_USD_M: +499.1
BTC_last_2_sessions_USD_M: -465.2
ETH_first_4_sessions_USD_M: +174.5
ETH_last_session_USD_M: -70.7
```

Therefore both statements are true:

- the full weekly ETF sum remained positive;
- the latest flow impulse ended negative.

Weekend sessions are `NON_SESSION`, never zero-filled.

## 8. Sentiment, breadth and macro

CFGI historical observations stayed in Fear or Extreme Fear from 20–25 July. The 26 July Data Ping snapshot was retained separately at 26 / Fear because the historical endpoint had not published the row at collection time.

The two late Data Ping snapshots show breadth weakening from 54.44% to 46.07%, while the median 24-hour return moved to 0.00%. Membership changed by one included asset, so the exact delta is not perfectly apples-to-apples, but the narrowing signal remains material.

Macro evidence through the latest published observations shows:

- DGS2 rising from 4.21% to 4.37%;
- DGS10 rising from 4.60% to 4.71%;
- VIX falling through Wednesday, then rising to 18.70 Thursday;
- DTWEXBGS only available as a 17 July carry-in.

This is not a clean risk-on confirmation.

## 9. H7 relevance

The package provides a useful secondary reconstruction of the existing H7 path.

Derived OKX swap ratios at the last settled local hour for 22–25 July are approximately:

```text
22 Jul 0.02934
23 Jul 0.02889
24 Jul 0.02896
25 Jul 0.02910
```

These align with the previously preserved rounded H7 sequence.

At the final settled package hour on 26 July, the derived ratio is approximately 0.02957. However:

- the H7 row-5 settlement had not occurred;
- the package lacks a direct ETH/BTC feed;
- two additional full local hourly bars and completion of the partial 21:00 bar were still absent before midnight CEST;
- the derived ratio is not hard-score authority.

H7 treatment:

```yaml
secondary_reconstruction_value: HIGH
condition_1_live_indication: FAVORABLE
condition_1_final: PENDING
hard_score_eligible: NO
```

## 10. Stablecoin and ancillary evidence

The package correctly preserves the stablecoin fallback boundary:

- chain distribution is available;
- a global stablecoin total is unavailable;
- no historical global total is fabricated.

Chain TVL, DEX pools and current OKX snapshots are preserved as point-in-time context. They do not constitute a weekly longitudinal series by themselves.

## 11. Framework verdict

```yaml
market_substate: ETH_LED_REPAIR_WITH_WEAK_PARTICIPATION
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
portfolio_action: NONE
stage1: GOVERNANCE_PENDING
recovery_upgrade: NONE
altseason_confirmation: NONE
canonical_state_change: NONE
```

The package materially improves W30 replay capability, especially for intraday path, range and relative-strength analysis. It does not unlock deployment or prove rotation.

## 12. Backtest use unlocked

Permitted:

- hourly path reconstruction;
- realized range and volatility features;
- BTC/ETH return correlation;
- derived relative-performance research;
- event-window joins to ETF, CFGI, macro, breadth and forecast ledgers;
- venue-tagged replay of the W30 pullback and Sunday repair.

Not permitted without additional histories:

- treating this seven-day slice as a statistically sufficient strategy backtest;
- replacing direct ETH/BTC gates with a derived swap ratio;
- mixing OKX and Binance OI/funding/price series without normalization;
- using the incomplete Sunday as the final weekly close;
- claiming a full framework backtest from this package alone.
