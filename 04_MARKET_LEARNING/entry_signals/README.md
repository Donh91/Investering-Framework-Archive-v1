# Entry Signal Ledger v1

Purpose: automatically timestamp the framework's observable graduated-altcoin entry pattern and later measure whether those observations were useful.

This layer is a **learning/audit observer only**. It does not execute trades, change framework rules, alter thresholds, create canonical market state, or independently authorize a DATA PING / Action Compass decision.

## Measurement-validity guard (v1.1)

The original observer used three already-registered observable conditions:

- ETHBTC > 0.0300
- Top100 proxy breadth >= 50%
- ETH 24h return > BTC 24h return

Those three conditions are still preserved as the legacy pattern definition; no threshold was optimized or replaced.

However, the Top100 breadth owner currently declares the market-cap Top100 series as `PROXY_ONLY` and `canonical_compatible: false`. Under the canonical Sensor Relationship & Incremental Value Standard, correlated or proxy evidence must not silently count as independent confirmation.

Therefore v1.1 separates:

```text
LEGACY_PATTERN_OBSERVED
from
INDEPENDENT_ROTATION_CONFIRMATION_ELIGIBLE
```

If the three legacy conditions are true while breadth remains proxy-only / canonical compatibility is unconfirmed:

```text
observer_state = PROXY_PATTERN_OBSERVED_NOT_ACTION_ELIGIBLE
state = WAIT
```

Only evidence explicitly eligible for independent rotation confirmation may permit the existing `GRADUATED_ALTCOIN_TOPUP_ACTIVE` observer state. This is an authority/evidence-role guard, not a new market threshold.

## Absolute breadth versus relative transmission

Absolute Top100 advancers remain useful descriptive tape colour. They are not, by themselves, proof of rotation away from BTC.

The observer now exposes existing owner fields alongside absolute breadth:

- `outperforming_btc_count` / share
- `outperforming_eth_count` / share
- equal-weight 24h return
- median 24h return

These fields are measurement-validity and transmission context. No new activation threshold is introduced for them by this ledger.

Repeated observations from the same rolling 24h window are not treated as independent survival confirmation. Capture-level correlation or survival studies must also account for adaptive / uneven capture cadence rather than treating every checkpoint as an independent sample.

## Automatic state observation

Every hourly GitHub run reads fresh repository breadth plus direct ETHBTC/BTC/ETH prices.

The existing three conditions are evaluated as a **pattern**. The state machine then applies the evidence-role guard described above.

`HOT` remains descriptive only. It never activates or deactivates the signal and therefore cannot silently modify framework semantics.

## ETH/BTC evidence semantics

The registered `ETHBTC > 0.0300` condition is retained as a **structural floor/context condition**, not treated as proof of fresh directional leadership by itself. The observer exposes the current hourly owner directional context (`eth_leads_btc_hours`, `ethbtc_positive_hours`, trailing positive run and latest relative performance) when available, but v1.1 does not introduce a new threshold from those fields.

This prevents a long-lived structural floor from being mislabeled as new rotation confirmation while preserving the original registered condition for historical comparability.

## DATA PING bridge

`data_ping_bridge.display_line` is deliberately non-binding and begins with `LEARNING OBSERVER:`. It must not be rendered or interpreted as a portfolio instruction, canonical entry permission or replacement for Three-Horizon Action Compass authority.

The bridge includes:

```text
canonical_action_authority=NONE
```

so learning-state authority cannot leak into the main decision surface.

## Historical validity and 12 July discipline

Historical event files remain immutable.

The canonical 12 July discipline is preserved in implementation semantics:

> A prospective signal that could not be rejected at its measurement time must not later be declared invalid solely because the subsequent outcome looks poor.

Accordingly:

- later outcomes calibrate **definition quality**;
- they do not rewrite historical event validity;
- a defect that was already observable from contemporaneous evidence roles or measurement semantics may be annotated as a measurement-definition defect without rewriting the event itself;
- no historical activation event is deleted or silently relabelled by v1.1.

This distinction is essential: hindsight disappointment is not the same thing as a contemporaneous measurement-validity failure.

## Files

- `LATEST.json`: current machine-readable observer status and non-binding DATA PING bridge summary.
- `STATE.json`: previous/current state used for transition detection.
- `events/*.json`: immutable activation/deactivation transitions with timestamp and source data.
- `outcomes/*.json`: automatically matured +24h, +72h, +7d, +14d and +30d outcomes.
- `PERFORMANCE_SUMMARY.json`: descriptive outcome summary, now including Top100 relative alpha versus BTC and ETH where data are available.

Outcome rows measure BTC, ETH, ETHBTC and a matched-constituent Top100 equal-weight return where baseline constituent prices are available. Relative alpha is reported explicitly so a broad-market rise cannot be mistaken for successful altcoin transmission merely because absolute returns were positive.

## Main-thread / DATA PING use

When a main-thread analysis or DATA PING reads `04_MARKET_LEARNING/entry_signals/LATEST.json`, it must treat the ledger as supplementary learning evidence only.

The Main Framework and Three-Horizon Action Compass remain the decision authority. Proxy-only breadth may support observation/watch context, but this ledger may not independently graduate a user action.

## Historical first event

The first event remains preserved from the first accepted 2026-08-20 packet on which the main thread explicitly changed its conclusion to `FIRST GRADUATED ALTCOIN TOP-UP WINDOW: ACTIVE`. The event time is anchored to that historical packet (`2026-08-20T05:22:15Z`). v1.1 does not retroactively rewrite that event; it changes how future observer states handle measurement validity and how historical outcomes are interpreted.
