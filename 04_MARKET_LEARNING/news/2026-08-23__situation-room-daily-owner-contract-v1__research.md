# Situation Room Daily Owner v1

**Status:** RESEARCH_ONLY_NON_CANONICAL  
**Authority:** catalyst/context evidence only  
**Owner id:** `SITUATION_ROOM_DAILY_OWNER_v1`

## Purpose

Create one durable, timestamp-clean daily catalyst/context observation without giving news causal, market-state, rule, threshold, Cycle Navigator, Master Monday or portfolio authority.

Situation Room is `DISCOVERY_ONLY`. A Situation Room item cannot become a verified material catalyst unless a primary source, or a strong independent source when a primary source is unavailable in the bounded review, supports the event.

## Durable outputs

```text
03_DAILY_CAPTURE_LOGS/catalyst_overlay/situation_room/YYYY/MM/YYYY-MM-DD.json
03_DAILY_CAPTURE_LOGS/catalyst_overlay/situation_room/LATEST.json
03_DAILY_CAPTURE_LOGS/catalyst_overlay/situation_room/EVENT_LEDGER.jsonl
```

The dated file is the daily observation. `LATEST.json` is a pointer/snapshot. `EVENT_LEDGER.jsonl` is append-only and deduplicated by stable event/family identity.

## Required daily semantics

Every run records:

- `observation_date_utc`
- `detection_time_utc`
- source coverage and per-source provenance receipts
- material events, if any
- unverified discoveries separately
- event time separately from detection time
- classification: `NOISE`, `LOCAL_EVENT`, `MARKET_RELEVANT`, `SYSTEMIC`, `STRUCTURAL`
- catalyst subtype
- confidence
- expected duration
- potentially affected framework lanes
- explicit authority firewalls

A successful collector run with no verified material event MUST produce:

```text
NO_NEW_MATERIAL_CATALYST
```

A source/collector failure MUST NOT be encoded as no-event. Allowed run-level states are:

```text
MATERIAL_CATALYSTS_FOUND
NO_NEW_MATERIAL_CATALYST
REVIEW_REQUIRED_UNRESOLVED_CANDIDATES
UNKNOWN_DUE_TO_SOURCE_FAILURE
COLLECTOR_FAILURE
```

## Event/reaction separation

The owner captures events and provenance. Subsequent BTC, ETH, ETH/BTC, BTC.D, breadth, ETF, stablecoin, funding, OI, taker-flow, liquidation or volatility behavior is a separate market-reaction observation. Reaction data never proves causality. Attribution remains `MULTI_CAUSAL_UNRESOLVED` unless separately established by governed research.

## Dedupe

Reposts, Federal Register publication of an already-recorded SEC proposal, later comments on the same policy action and repeated press coverage must retain one event family where appropriate. Follow-ups can be recorded as evidence updates without being counted as independent catalysts.

## Prospective firewall

This owner is not part of Shared Row Tournament eligibility. Backfill and current-day rows have:

```yaml
shared_row_tournament_eligible: false
retroactive_candidate_eligibility: false
canonical_effect: false
market_state_effect: false
portfolio_effect: false
```

No catalyst row may backdate a candidate decision, change a prospective floor, rewrite a frozen catalyst ledger, or become hindsight-based causal attribution.

## Bounded backfill rule

The approved 2026-08-18 through 2026-08-23 backfill is research/context evidence only. It preserves the historical event time when sourceable and the later backfill detection time separately. Missing exact event times remain explicitly date-only or unresolved, never guessed.

## Activation boundary

Collector code, tests, contracts and bounded research artifacts are normal research changes. Adding or changing a scheduled `.github/workflows/*` writer is HIGH-IMPACT under repository safety governance and requires the mandated safepoint plus verified external-vault snapshot before activation.

Until that gate is satisfied, repository state must say `IMPLEMENTED_NOT_SCHEDULE_ACTIVATED`, not imply a daily production schedule exists.
