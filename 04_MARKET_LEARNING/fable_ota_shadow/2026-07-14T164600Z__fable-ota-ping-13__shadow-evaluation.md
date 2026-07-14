# FABLE OTA Shadow Ping #13 — Framework Evaluation

**Shadow timestamp:** 2026-07-14 16:46 UTC / 18:46 CEST  
**Framework review basis:** latest accepted DATA PING `DATA_PING_V4_20260714T154709Z`  
**Status:** `SHADOW_ACCEPTED_FOR_LEARNING_ONLY`  
**Authority:** `NON_BINDING / NO_PORTFOLIO_ACTION / NO_RULE_PROMOTION`

## Accepted qualitative contribution

The strongest useful hypothesis is:

> Structure repaired before price accelerated; the current move is therefore the best Type-2 candidate observed so far, but not yet a confirmed Type-2 event.

The latest accepted DATA PING independently confirms the intraday components that matter:

- BTC current above 63.3K with three settled hourly closes above;
- direct ETH/BTC above 0.0285;
- 1H breadth 88.6% and 24H breadth 82.9%;
- BTC short-horizon spot-taker proxy improved;
- ETH 4H/24H spot-taker proxy improved;
- BTC OI fell while price rose.

These inputs justify `RESOLUTION_CANDIDATE: YES_INTRADAY_ONLY` for the existing event `ROTATION_REPAIR_EDGE_20260712_01`.

## Corrections to the Claude shadow narrative

### Breadth was not unverified

At the framework cutoff, 24H breadth was already verified at 82.9%, not missing. Claude's breadth caveat was stale relative to the accepted DATA PING.

### ETF confirmation was not available

The latest completed BTC ETF session remained -424.7M, with 3-, 5- and 10-session windows negative. The current session remained pending. Therefore ETF cannot support Type-2 confirmation in this row.

### Completed-close requirements remained unmet

- latest completed BTC daily close remained below 63.3K;
- no completed daily ETH/BTC close above 0.0285 was available;
- ETH/BTC remained below 0.0300;
- 7D breadth remained below majority.

The intraday move therefore cannot close the event or unlock entry/deployment.

### Macro and liquidation claims remain external shadow claims

The supplied CPI figures, short-liquidation amount, and causal statement that the move was squeeze-initiated were not verified inside the accepted DATA PING truth layer. They are preserved only as `EXTERNAL_SHADOW_CONTEXT`, not canonical facts.

## Type-2 prospective test

The candidate may be evaluated prospectively with the following non-promoted evidence checklist:

1. completed CEST ETH/BTC close above 0.0285;
2. completed BTC close above 63.3K and subsequent acceptance;
3. 24H breadth remains above majority beyond the initial impulse;
4. 7D breadth improves toward or above majority;
5. ETF and broader flow evidence cease contradicting the move;
6. no rapid full retrace back below reclaim and repair levels.

This checklist is an evaluation scaffold only. It does not create a new engine, threshold set, sensor weight, or portfolio rule.

## Framework result

```text
ACTIVE EVENT: ROTATION_REPAIR_EDGE_20260712_01
FRAMEWORK EDGE STATE: NEAR_PRESENT
ALERT STATUS: STILL_ACTIVE
EVENT STATUS: OPEN_TRIGGERED
RESOLUTION CANDIDATE: YES — INTRADAY ONLY
ROTATION: NO_ROTATION
REBUY: LOCKED
LARGE-CAP WINDOW: NOT_OPEN
ACTIVE TRIM: NO
PORTFOLIO ACTION: NONE
```

## Learning value

This row is highly informative because it creates a clean prospective distinction between:

- `load-bearing structure`,
- `leading structure`, and
- `transmitting structure`.

The accepted evidence now supports temporary transmission and a possible leading sequence, but not durable confirmation. The next completed-close and flow observations determine whether this becomes the first genuine Type-2 example or another catalyst-assisted intraday expansion that failed to persist.

## Governance

- Shadow scores `Transition ~47`, `Confirmation ~42`, and `Delta ~+5` are preserved as Claude-local qualitative markers only.
- They are not reproducible framework scores and must not enter official scoring.
- No retrospective change is made to CN #16.
- This row may be used as prospective outcome evidence in later decision-value audits.
