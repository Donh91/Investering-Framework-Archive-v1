# BlockchainCenter Altcoin Season Daily Shadow Contract v1

**Date:** 2026-08-25

**Status:** ACTIVE_PROSPECTIVE_SHADOW

**Authority:** context and calibration only

**Source id:** `BLOCKCHAINCENTER_ALTCOIN_SEASON_INDEX`

## Decision

BlockchainCenter's Altcoin Season Index is admitted as a failure-isolated companion to the existing Top100 breadth owner. It is not a new engine, a new gate, a trade trigger or a substitute for framework-owned breadth.

Its published state label can be reconstructed from the same captured 49 altcoin returns versus BTC. The framework records both the published score and the underlying distribution, then requires exact score reconciliation before the observation receives `PASS` status. CoinMarketCap's official Top100 index is captured beside it as a lower-grade independent method crosscheck.

## Source methods and retained fields

BlockchainCenter defines Altcoin Season as at least 75 percent of the Top 50 coins outperforming BTC over the selected period. Stablecoins and asset-backed tokens are excluded. The live page exposes 30-day, 90-day and 365-day scores, constituent returns, historical series and season statistics.

The framework records each published and recomputed score, BTC and altcoin returns, outperformance share, median spread, best and worst performers, membership hash, series hash and source state. Its full response is retained as compressed raw evidence.

CoinMarketCap defines a separate daily 90-day index using its Top 100 universe, excluding stablecoins and asset-backed or wrapped tokens. The captured page exposes the published score but not a component-return panel suitable for exact reconciliation. Its raw page, score, state, source build id, methodology hash and Top100-minus-Top50 method spread are retained with `PUBLISHED_LABEL_ONLY` evidence grade.

Neither captured page supplies a separate provider observation time in the normalized payload. Fetch time is recorded explicitly and must not be represented as provider event time.

## Existing automation route

No scheduled workflow is duplicated. The integration reuses existing production owners:

| Layer | Existing workflow | Cadence in `Europe/Copenhagen` | Durable result |
|---|---|---:|---|
| Full shadow evidence | `Research Owner - Top100 Breadth Daily` | Daily 07:15 | Dated raw pages, normalized context and crosscheck, receipt, manifest and owner snapshot under `03_DAILY_CAPTURE_LOGS/breadth_rich/YYYY/MM/YYYY-MM-DD/` |
| Compact market context | `Daily Live Anchor Capture` | 02:13, 06:13, 10:13, 14:13, 18:13 and 22:13 | Compact scores, distribution, method spread, states and hashes under `03_DAILY_CAPTURE_LOGS/captures/` |
| Bounded cold checkpoint | `Daily Live Anchor Capture` | Daily 06:13 | Source-owner evidence in the existing bounded raw checkpoint |
| Weekly calibration | `Weekly Raw Calibration Bridge` | Sunday pre-close and Monday final | Prospective 7-day, 28-day and 56-day windows under `03_DAILY_CAPTURE_LOGS/weekly/` |

Either web companion can degrade without invalidating the primary `C5E_TOP100_BREADTH_OWNER_v1_2` result. Failure is recorded as `UNKNOWN` or `DEGRADED`, never as no rotation or a fabricated score.

## Interpretation firewall

The indices are state labels, not decision motors. They cannot independently change market state, unlock deployment or cause a portfolio action. A high or rising index is specifically treated as a possible false signal when BTC dominance remains high, ETH/BTC remains weak, or independent CoinGecko Top100 breadth does not confirm participation.

The weekly pack exposes observations to the existing `ROTATION_SURVIVAL_FORWARD` learning lane. It does not create retrospective eligible rows, rewrite frozen decisions or change unrelated readiness.

## Prospective evidence rules

- Start only after activation on `main`.
- Do not backfill past dates as prospective observations.
- Do not interpolate or forward-fill missing days.
- Preserve dated raw payloads and hashes.
- Report constituent-universe changes.
- Require 5 passing days for the 7-day window, 21 for 28 days and 42 for 56 days before each can be `READY`.
- Keep the windows separate so short changes are not confused with the 4-to-8-week learning horizon.

## Related-source triage

| Source | Disposition | Reason |
|---|---|---|
| BlockchainCenter Altcoin Season Index | `ACTIVE_SHADOW_COMPANION` | Reproducible score plus component returns, directly relevant to rotation breadth |
| CoinMarketCap Altcoin Season Index | `ACTIVE_LOWER_GRADE_SHADOW_CROSSCHECK` | Independent Top100 label and method dispersion, no component reconciliation or readiness effect |
| BlockchainCenter Crypto Sentiment | `NOT_ADMITTED_REDUNDANT` | Crowd vote duplicates the governed CFGI lane |
| BlockchainCenter Bitcoin Pulse | `NOT_ADMITTED_REDUNDANT` | Duplicates direct venue owners |
| BlockchainCenter BTC and ETH Rainbow Charts | `EXCLUDED_FROM_DECISION_LAYER` | Provider describes them as non-scientific and non-predictive |
| BlockchainCenter Flippening page | `RETIRED_SOURCE_CANDIDATE` | Legacy route lacks a stable documented measurement contract |

Future source admission requires stable machine-readable capture, explicit universe lineage, failure isolation, a named calibration question and non-duplicative information.

## Falsification questions

1. Does a rising 90-day score predict improved 4-to-8-week rotation survival after conditioning on ETH/BTC, BTC dominance and independent breadth?
2. Do 30-day threshold crossings lead or merely echo independent breadth?
3. Does constituent turnover explain apparent index moves?
4. How often does the state label disagree with median alt-minus-BTC spread?
5. Does the context reduce false rotation positives without delaying valid confirmation?

Persistently redundant, unstable or unreconciled sources are downgraded or retired through a governed change while their evidence trail remains intact.
