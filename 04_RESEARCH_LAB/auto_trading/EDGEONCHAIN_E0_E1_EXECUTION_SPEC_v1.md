# EDGEONCHAIN E0/E1 EXECUTION SPEC v1

Status: RESEARCH_ONLY / READY FOR NETWORK-ENABLED EXECUTION
Date: 2026-09-13
Case owner: #922
Scientific lifecycle: #885
Generic method: `EXTERNAL_STRATEGY_REVERSE_ENGINEERING_PROTOCOL_v1.md`
Collector: `scripts/experiments/polymarket_external_strategy_capture_v1.py`

## Objective

Resolve EdgeOnchain's canonical Polymarket execution identity from primary public Polymarket APIs and freeze the complete observable account ledger before any behavioral inference or performance claim is evaluated.

This stage must produce evidence, not a trading recommendation.

## Why E0/E1 is the current bottleneck

Public profile pages are mutable presentation surfaces. Historical indexed snapshots of `@EdgeOnchain` have shown different headline statistics at different dates. Therefore profile counters such as `Predictions` and `Biggest Win` are discovery context only.

The immutable research object must be the resolved Polymarket profile/proxy wallet plus raw public API/on-chain activity.

## E0 - canonical identity resolution

Use Polymarket Gamma public search:

`GET https://gamma-api.polymarket.com/public-search?q=EdgeOnchain&search_profiles=true&limit_per_type=20`

Polymarket's public-search schema exposes profile fields including `name`, `pseudonym`, `bio`, and `proxyWallet`.

Admission rule:

- require exactly one exact normalized `name` or `pseudonym` match for `EdgeOnchain`;
- require a valid 0x-prefixed 20-byte `proxyWallet`;
- fail closed if zero or multiple exact matches exist.

Then independently cross-check:

`GET https://gamma-api.polymarket.com/public-profile?address=<proxyWallet>`

The returned `proxyWallet` must match the search result. Preserve the full raw search response, the full profile response, retrieval timestamp and SHA-256.

Do not infer canonical identity from social links alone.

## E1 - complete public activity capture

Once identity is frozen, capture the public Data API surfaces.

### Activity

`GET https://data-api.polymarket.com/activity`

Required query semantics:

- `user=<proxyWallet>`
- `start=1` to request full user history rather than relying on the default recent window
- `sortDirection=ASC`
- `excludeDepositsWithdrawals=false`
- page with `limit=500` and offsets

The activity endpoint can expose trade, split, merge, redeem, reward, conversion, deposit, withdrawal, yield, maker rebate, taker rebate and referral-reward records. Preserve type rather than collapsing all rows into trades.

### Trades

`GET https://data-api.polymarket.com/trades`

Required query semantics:

- `user=<proxyWallet>`
- `start=1`
- `takerOnly=false`
- page with the documented limit/offset bounds

`takerOnly=false` is mandatory. The default is true and would otherwise bias the capture toward taker-side records.

Important: this does not by itself prove maker/taker role for every economic fill. Maker/taker attribution remains a later microstructure/on-chain reconstruction task.

### Closed positions

`GET https://data-api.polymarket.com/closed-positions`

Page all rows with a deterministic timestamp order and preserve realized P&L fields as supplied by Polymarket.

## Fail-closed completeness rule

The current collector deliberately stops with an error if an endpoint's documented offset cap would be exceeded.

If this occurs, do not call the ledger complete. Upgrade the collector to time-window pagination using the documented `start`/`end` parameters and prove adjacent windows compose without gaps or duplicates.

No silent truncation is admissible.

## Raw archive contract

Each capture run must preserve:

- immutable run ID;
- resolved proxy wallet;
- exact request URLs;
- retrieval timestamp;
- every raw page response;
- consolidated endpoint datasets;
- SHA-256 per raw and consolidated artifact;
- row counts;
- explicit completeness status;
- collector version/commit.

Raw bytes are evidence. Derived normalized tables must never replace them.

## E1 normalization contract

After the raw freeze, derive an action ledger with, where available:

- proxy wallet;
- transaction hash;
- action/activity type;
- timestamp;
- condition ID;
- asset/outcome token;
- event/market slug and title;
- side;
- size;
- USDC/cash size;
- execution price;
- outcome/outcome index;
- event start time;
- market close time;
- settlement time;
- realized P&L;
- product type, single/combo/parlay where identifiable;
- source provenance;
- source-artifact SHA.

Duplicate detection must use transaction/event identity, not title text.

## Mandatory microstructure enrichment

The 2026 Polymarket literature makes execution style a first-class confounder.

For each source action, attempt to enrich:

- maker/taker role;
- limit vs market/aggressive execution where inferable;
- spread at entry;
- best bid/ask and midpoint;
- order-book depth around source notional;
- maker rebates/taker fees where applicable;
- queue/resting-time evidence where observable.

Do not credit profitable execution to prediction accuracy until execution edge is separated.

## Mandatory event-time enrichment

For sports/prediction-market actions preserve separately:

- true event/game start;
- exchange trading close;
- administrative settlement;
- source trade timestamp;
- time-to-event/time-to-expiry at source action.

Do not use administrative settlement time as a substitute for true event timing.

Recommended research TTE buckets for comparability with the 2026 sports prediction-market literature:

- 0-10m
- 10-30m
- 30-90m
- 90-240m
- 240m+

These buckets are research controls, not assumed Edge rules.

## Opportunity-set requirement before reverse engineering

The Edge action ledger alone is not sufficient to infer why Oddy selected a bet.

For each source decision timestamp, reconstruct the contemporaneous eligible market set, including non-selected markets. At minimum preserve:

- market/condition ID;
- sport/category;
- market type/product type;
- implied probability/price;
- bid/ask/spread where available;
- volume/liquidity/attention measures;
- time to event;
- market age;
- observable price movement preceding the decision.

Positive examples are Edge actions. Negative examples are eligible markets available at the same decision time that Edge did not select.

Without this matched negative set, `selection-policy reconstruction` remains descriptive and must not be promoted.

## Analysis ladder after E1

Run in this order:

1. transparent descriptive rules and threshold plots;
2. regularized logistic/multinomial behavioral clone;
3. tree/boosting model only if it adds out-of-time explanatory value;
4. sizing regression against bankroll/exposure/odds/liquidity;
5. timing/TTE analysis;
6. source-alpha adjudication after calibration and execution controls;
7. observability and +30s/+1m/+5m copy-decay test;
8. optional linear/MaxEnt inverse reinforcement learning only after state/action/opportunity-set integrity is proven.

IRL may infer a behavioral reward approximation. It must not be described as recovering Oddy's proprietary internals.

## Primary falsifiers

Stop or downgrade if:

- canonical identity is ambiguous;
- raw history is truncated or materially incomplete;
- losing/redeemed/cancelled actions cannot be reconciled;
- source performance vanishes after maker/taker/spread controls;
- apparent alpha is explained by known time-to-event or product-type miscalibration;
- singles do not show edge independently of parlays;
- source probability quality is poorly calibrated;
- copy-delay execution destroys expectancy;
- reconstructed selection behavior fails out-of-time.

## Current execution status

`COLLECTOR_IMPLEMENTED / LIVE NETWORK CAPTURE NOT YET EXECUTED IN THIS CHAT RUNTIME`

Reason: the current local execution environment does not expose outbound network access to the Polymarket API, and the available Firecrawl quota was exhausted during this pass.

This is a tooling constraint, not an evidence substitute. Canonical wallet identity remains `UNRESOLVED` until the public API result is actually captured and cross-verified.

The correct next machine action is to run the read-only collector in the repository's network-enabled governed execution environment, archive its immutable artifacts, and only then begin policy reconstruction.