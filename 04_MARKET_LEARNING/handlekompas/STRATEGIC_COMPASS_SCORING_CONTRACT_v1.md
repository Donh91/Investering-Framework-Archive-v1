# Strategic Compass Scoring Contract v1

Status: PRE-REGISTERED BEFORE FIRST STRATEGIC OUTCOME
Contract ID: `STRATEGIC_COMPASS_SCORING_v1`
Effective: 2026-09-30

## Purpose

Extend Compass accountability beyond the existing 12h / 72h / 168h tactical horizons without creating a parallel market-state engine or rewriting Cycle Navigator.

The strategic layer answers two different questions:
- `21-30D`: where the current market process is likely to lead over roughly one month;
- `4-8W`: what cycle/regime destination is most plausible, using Cycle Navigator as the structural prior.

Existing `OFFICIAL_DAILY_COMPASS_SCORING_v1` remains unchanged and authoritative for 12h / 72h / 168h.

## Architecture

```
12h Tactical Compass
  -> 72h Tactical Compass
  -> 168h Weekly Compass
  -> 21-30D Strategic Compass
  -> 4-8W Cycle Navigator Strategic Overlay
  -> Cross-Horizon Alignment
```

No new independent forecast engine is authorized.

### 21-30D

A strategic anchor is immutable after issuance. It may be refreshed prospectively as a new anchor, never edited in place.

Preferred issuance cadence: weekly, after the completed Master Monday calibration. This produces rolling strategic anchors while retaining each prior anchor for accountability.

The anchor must freeze:
- reference timestamp and eligible evidence lineage;
- base / bull / bear scenarios with probabilities summing to 100%;
- expected BTC and ETH direction;
- expected ordered path;
- expected regime destination;
- expected pullback class and timing window where supportable;
- ETH/BTC and BTC-dominance direction;
- expected rotation / transmission state;
- distribution-risk posture;
- action posture within existing authority;
- explicit falsification conditions;
- confidence and missingness.

Do not fabricate numeric price ranges when evidence does not support them.

### 4-8W

This is NOT a second long-cycle engine.

Cycle Navigator remains the structural owner. Strategic Compass consumes the prospectively frozen CN 4-8W projection and exposes it as a typed strategic overlay.

The 4-8W freeze must preserve:
- exact CN source identity and immutable SHA/lineage;
- expected cycle/regime destination;
- expected rotation stage;
- breadth/transmission expectation;
- pullback/distribution posture;
- high-level action posture within existing authority;
- explicit falsification conditions.

A later CN issue is a new forecast, not a rewrite of the earlier 4-8W anchor.

## Thesis-state monitoring

Between anchor issuance and maturity, the framework may classify the frozen thesis:

`ON_TRACK | ACCELERATING | WEAKENING | INVALIDATED | DATA_DEGRADED`

This status is a live readback only. It must never mutate the frozen anchor.

Every state transition must preserve timestamp, evidence lineage and reason codes.

## Cross-horizon alignment

The framework should compare the current eligible states of 12h, 72h, 168h, 21-30D and 4-8W without forcing them to agree.

Examples of descriptive alignment classes:
- `FULL_BULL_ALIGNMENT`
- `TACTICAL_PULLBACK_STRUCTURAL_BULL`
- `TRANSITION_WARNING`
- `DISTRIBUTION_ALIGNMENT`
- `MIXED_OR_NO_EDGE`

These are navigation labels, not new market thresholds and not portfolio-execution authority.

The system must preserve disagreement. A bearish 12h/72h signal inside a bullish 4-8W regime can be valid and may be especially useful for pullback/re-entry navigation.

## Outcome checkpoints

For 21-30D anchors:
- T+7: checkpoint only;
- T+14: checkpoint only;
- T+21: eligible strategic checkpoint;
- T+30: final maturity.

For 4-8W anchors:
- T+14 and T+28: checkpoints;
- T+42: six-week checkpoint;
- T+56: final maturity.

Checkpoints never rewrite the forecast and are not silently promoted into final outcomes.

## Multidimensional scoring

Do NOT create one flattering aggregate accuracy score.

Score/report separately where governed evidence exists:
1. BTC direction;
2. ETH direction;
3. path/sequence accuracy;
4. BTC/ETH MFE and MAE;
5. regime destination;
6. pullback class/timing;
7. ETH/BTC direction;
8. BTC-dominance direction;
9. breadth/transmission;
10. rotation ladder;
11. distribution-risk warning;
12. action utility;
13. falsification timing;
14. abstention/missingness quality.

Rotation or breadth components remain `UNAVAILABLE` until governed outcome series exist. Never substitute unrelated proxies merely to obtain a score.

## Transition timing learning

Record when shorter horizons first contradicted a still-bullish or still-bearish strategic anchor.

After sufficient samples, report:
- lead time from first qualified tactical deterioration/confirmation to strategic invalidation/confirmation;
- false tactical alarms that correctly failed to overturn the strategic thesis;
- missed strategic transitions;
- false-negative opportunity cost.

This is intended to improve Pullback / Distribution / Re-entry warning quality without hindsight.

## Scenario calibration

Base/bull/bear scenario probabilities are frozen at issuance.

After sufficient matured, non-overlapping evidence, assess probability calibration. Do not infer calibration from a handful of overlapping rolling anchors.

Rolling weekly 21-30D anchors are serially correlated. Aggregate reporting must disclose overlap and must not count overlapping anchors as independent trials.

## Master Monday integration

Master Monday is the calibration/orchestration point, not a new forecast engine.

Each completed run should:
1. score newly matured 12h/72h/168h outcomes under the existing contract;
2. inspect recurring forecast errors, including premature stabilization->continuation upgrades, false negatives, rotation timing and pullback underestimation;
3. read the existing strategic anchor without rewriting it;
4. update thesis-state readback if evidence warrants;
5. freeze a new rolling 21-30D anchor prospectively;
6. bind the 4-8W overlay to the current eligible Cycle Navigator projection;
7. preserve all prior anchors/outcomes immutably.

## Calibration safeguards

- Stabilization is not continuation.
- Absorption is not recovery.
- BTC health is not ecosystem transmission.
- A bullish long horizon must not suppress qualified tactical pullback warnings.
- A bearish short horizon must not silently invalidate a bullish cycle thesis.
- Missing/conflicting evidence lowers confidence.
- No hindsight reconstruction.
- No synthetic composite precision score.
- Compare against simple baselines when enough observations mature.
- Prefer `NO_EDGE` / abstention to unsupported precision.

## Authority ceiling

Navigation and forecast-accountability only.

No portfolio execution authority.
No source override.
No market-threshold or model-weight changes.
No rewrite of frozen Compass or Cycle Navigator history.
No automatic promotion of research/shadow evidence into canonical confirmation.
