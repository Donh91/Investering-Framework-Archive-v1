# BTC Sep 3 Pre-Breakout Forensic Learning Audit — Shadow

status: RESEARCH_ONLY_NON_CANONICAL
authority: NONE
canonical_market_state_change: false
market_rule_change: false
portfolio_execution: false
automatic_reweighting: false
created_for: forward-learning and calibration integrity

## Purpose

Preserve a hindsight-controlled reconstruction of what the framework had actually captured and frozen before the 2026-09-03 BTC acceleration. This artifact must not rewrite historical predictions, infer missing evidence, or promote thresholds from one event.

## Event window

Primary reconstruction window: 2026-09-03T00:00:00Z through 2026-09-03T16:00:00Z.

Observed BTC sequence from the permanent hourly owner CSV:
- 09:00Z observation area: BTC 77,843.34
- 11:00Z close: BTC 77,948.39 (+0.273% 1h)
- 12:00Z close: BTC 78,652.38 (+0.903% 1h)
- 14:00Z close: BTC 80,549.97 (+2.168% 1h)
- 15:00Z close: BTC 81,348.00 (+0.991% 1h)

The important audit question is not whether the later rally can be explained after the fact. It is whether evidence and forecasts were frozen before the move.

## Hindsight-control checkpoints

### Checkpoint A — 04:17Z: no valid claim that the framework anticipated the later BTC breakout

Frozen intraday prediction issued 2026-09-03T04:17:31Z from a 04:00Z source cutoff and BTC start value 77,708.00.

BTC direction:
- 1H: DOWN, 4/6 evidence families
- 4H: DOWN, 4/6 evidence families
- 24H: DOWN, 4/6 evidence families
- calibration status: WARMUP
- calibrated probability: unavailable

ETH direction was UP at 5/8 agreement.

Interpretation: the framework had not yet identified the later BTC ignition at this checkpoint. This negative finding is preserved because it is scientifically as important as the later successful flip.

### Checkpoint B — 04:40Z to 06:31Z: breadth improved before BTC acceleration, but rotation remained unconfirmed

Immutable rich-breadth capture around 04:40Z recorded:
- top-100 advance ratio: 0.55
- equal-weight mean 24h return: +0.421045%
- median 24h return: +0.015105%
- BTC 24h: +0.11547%
- ETH 24h: -0.69026%
- 45/100 constituents outperforming BTC
- 70/100 outperforming ETH

The entry-signal observer later materialized this as WAIT / NO_PATTERN. That was not a failure to see BTC direction; the observer's mandate is altcoin-entry/rotation evidence and it correctly withheld promotion while ETH leadership was absent and breadth remained proxy-only.

### Checkpoint C — 09:38Z: genuine ex-ante directional flip before major acceleration

Frozen intraday prediction issued 2026-09-03T09:38:58Z from a 09:00Z source cutoff and BTC start value 77,843.34.

BTC:
- 4H: UP
- 24H: UP
- evidence agreement: 5/6 = 83.33%
- UP families: return_1h, return_4h, session_vwap, momentum_acceleration, taker_balance
- opposing family: taker_change
- calibration status: WARMUP
- calibrated probability: unavailable

ETH:
- 4H: UP
- 24H: UP
- evidence agreement: 6/8 = 75%
- ETHBTC_1h was an opposing DOWN vote

This checkpoint predates the large 12Z–15Z BTC acceleration and therefore qualifies as genuine prospective evidence, not retrospective interpretation.

### Checkpoint D — 09:51Z / 11:45Z: participation broadened before ignition, while relative ETH leadership remained weak

The research breadth owner package preserved raw payloads, owner snapshot, source receipts and hashes. It recorded approximately:
- advance ratio: 0.75
- equal-weight mean return: +1.479661%
- median return: +1.20374%
- BTC 24h: +1.24635%
- ETH 24h: +0.85566%
- 48/100 outperforming BTC
- 55/100 outperforming ETH

The entry-signal observer still remained WAIT / NO_PATTERN because ETHBTC was weak and only a minority of the top-100 was outperforming BTC. This distinction is valuable: market participation broadened, but the move was still BTC-led rather than confirmed BTC -> ETH -> alt rotation.

## Forward outcome already mature

For the 09:38Z BTC 4H UP prediction:
- exact due: 2026-09-03T13:00:00Z
- start: 77,843.34
- end: 78,652.38
- return: +1.0393182%
- actual direction: UP
- result: HIT
- evidence semantics: EXACT_DUE_CLOSED_1H_OWNER_CANDLE

Aligned families were return_1h, return_4h, session_vwap, momentum_acceleration and taker_balance. Taker_change opposed the outcome.

Do not infer the later 80.5k/81.3k move into this 4H score; the official score is bound only to the exact due candle.

## Outcomes not yet eligible at audit creation

The 24H predictions must remain unresolved until their exact registered due times. No early maturation or retrospective replacement is permitted.

## Logging coverage assessment

### Hourly owner — STRONG
Permanent 2026-09-03 CSV contains BTC/ETH/ETHBTC OHLC, volume, taker flow, OI, long/short, funding and price/OI state. Scheduled materializations throughout the day preserve the pre-move, ignition and post-ignition sequence.

### Intraday direction predictions/outcomes — STRONG
Frozen prediction files, exact source cutoffs, due times, evidence votes, immutable hashes and exact-due outcome files exist. This is the primary hindsight-safe learning lane for this event.

### Rich breadth — STRONG
Pre-move breadth captures are immutable. The research owner package also preserves raw source payloads and provenance hashes, allowing later replay and membership-aware analysis.

### Entry-signal / Shadow Registry — USEFUL WITH ROLE LIMITS
The observer correctly remained non-canonical and WAIT / NO_PATTERN during a BTC-led move. Its value in this event is separating participation from genuine altcoin rotation, not predicting BTC direction.

### CFGI — SOURCE GAP
Week 36 weekly CFGI derived output reports SOURCE_UNAVAILABLE / capture_count=0 under the current provider lifecycle. Therefore no claim may be made that CFGI captured or anticipated the Sep 3 move. This is a genuine sensor-coverage gap, not permission to backfill synthetic contemporaneous evidence.

### DATA PING chat packets — ARCHIVE PERSISTENCE NOT PROVEN BY THIS AUDIT
Exact Sep 3 chat snapshot timestamps searched in repository code did not resolve to a persisted payload. Underlying owner evidence is preserved, but this audit does not claim that every user-delivered accepted DATA PING packet itself is independently archived in GitHub.

## What the framework actually understood before the rise

The correct hindsight-controlled conclusion is layered:

1. At 04:17Z it did not yet anticipate a BTC breakout; BTC shadow direction was DOWN.
2. Breadth then improved from a marginally supportive 0.55 state toward 0.75 before the large move.
3. By 09:38Z the intraday directional engine had flipped BTC to UP with 5/6 evidence-family agreement before the major acceleration.
4. The altcoin-entry/rotation observer remained WAIT because ETH relative leadership and BTC-outperformance breadth were insufficient.
5. That split was informative: BTC-directional ignition was detected without falsely declaring alt rotation.

## Candidate learning hypothesis — NOT PROMOTED

Candidate only: a BTC-led ignition regime may be characterized by simultaneous improvement in absolute breadth plus BTC momentum/session-VWAP/taker support, while ETHBTC remains weak and BTC-relative breadth does not confirm broad rotation. Such a regime may favor BTC continuation while requiring caution on aggressive microcap deployment.

This is a single event. It must be tested prospectively across additional independent events before any rule, threshold, weight, confidence display, or portfolio action is changed.

## Required follow-up

- Mature the frozen 24H forecasts only at exact due times.
- Preserve subsequent pullback/retest rows with the same hourly owner semantics.
- Evaluate whether the 09:38 pre-ignition feature combination recurs in future independent events.
- Keep BTC-direction prediction and alt-rotation confirmation as separate questions.
- Treat CFGI as unavailable for this event unless a separately governed future source-recovery process is approved; never backfill it as if contemporaneously observed.
