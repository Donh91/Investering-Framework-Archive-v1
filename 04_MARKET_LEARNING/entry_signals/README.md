# Entry Signal Ledger v1

Purpose: timestamp the framework's **legacy** graduated-altcoin observation pattern and measure its forward outcomes without granting it market or portfolio authority.

This layer is a **learning/audit observer only**. It does not execute trades, change framework rules, alter thresholds, create canonical market state, or independently authorize a DATA PING / Action Compass decision.

## Canonical promotion guard (v1.2)

The original observer used three observable conditions:

- ETHBTC > 0.0300
- Top100 proxy breadth >= 50%
- ETH 24h return > BTC 24h return

Those conditions remain frozen as a **legacy pattern definition** for historical comparability. They are not a current entry rule.

The binding 12 July canonical owners are:

```text
06_RESEARCH_LAB/audit_summaries/2026-07-12__marginal-decision-value-and-breadth-truth-program-v1__canonical.md
01_CORE_FRAMEWORK/governance/2026-07-12__rule-and-evidence-registry-sensor-audit-v1__canonical-addendum.md
```

They establish:

```text
BREADTH_PREDICTIVE_GATE: NOT_SUPPORTED / RETIRED_ZERO_WEIGHT
BREADTH_STANDALONE_ACTION_AUTHORITY: ZERO
BREADTH_ROLE: DESCRIPTIVE_CONFIRMATION_ZERO_WEIGHT
GRADUATED_ALT_DEPLOYMENT: FORWARD_ONLY_NOT_PROMOTION_READY
RULE_PROMOTION: NONE
PORTFOLIO_AUTHORITY_CHANGE: NONE
```

Therefore a source-quality improvement, including future `canonical_compatible=true` breadth evidence, **cannot by itself reactivate** `GRADUATED_ALTCOIN_TOPUP_ACTIVE`.

The observer must remain:

```text
state = WAIT
```

when the legacy pattern is observed, unless a later explicit canonical governance action promotes graduated deployment and the implementation is deliberately updated against that new authority.

Current pattern-positive state:

```text
observer_state = LEGACY_PATTERN_OBSERVED_FORWARD_ONLY_NOT_PROMOTION_READY
```

This is a promotion/authority guard, not a new market threshold.

## Measurement-validity guard

Top100 absolute breadth remains useful descriptive tape colour. It is not entry permission, a hard gatekeeper, or standalone proof of rotation.

The observer exposes existing owner fields alongside absolute breadth:

- `outperforming_btc_count` / share
- `outperforming_eth_count` / share
- equal-weight 24h return
- median 24h return

These fields are measurement-validity and transmission context. No activation threshold is introduced for them by this ledger.

The source-role fields `canonical_compatible` and `source_independence_eligible` describe provenance/evidence quality only. They do **not** override the 12 July zero-weight breadth decision.

Repeated observations from the same rolling 24h window are not treated as independent survival confirmation. Capture-level correlation or survival studies must also account for adaptive / uneven capture cadence rather than treating every checkpoint as an independent sample.

## ETH/BTC evidence semantics

The registered `ETHBTC > 0.0300` legacy condition is retained as a **structural floor/context condition**, not treated as proof of fresh directional leadership by itself. The observer exposes current hourly directional context (`eth_leads_btc_hours`, `ethbtc_positive_hours`, trailing positive run and latest relative performance) when available, but does not create a new threshold from those fields.

## DATA PING bridge

`data_ping_bridge.display_line` is deliberately non-binding and begins with `LEARNING OBSERVER:`. It includes:

```text
canonical_action_authority=NONE
promotion=FORWARD_ONLY_NOT_PROMOTION_READY
```

It must not be rendered or interpreted as portfolio instruction, canonical entry permission, or replacement for Three-Horizon Action Compass authority.

## Historical validity discipline

Historical event files remain immutable.

Later outcomes calibrate **definition quality**; they do not rewrite the point-in-time historical record merely because the later outcome is poor. A defect that was already observable from contemporaneous evidence roles, registry status, or measurement semantics may be annotated prospectively without silently rewriting the historical event.

The important distinction is:

```text
poor later outcome != proof that the historical observation never occurred
contemporaneous authority/measurement defect != permission to keep using the definition prospectively
```

No historical activation event is deleted or silently relabelled by v1.2.

## Files

- `LATEST.json`: current machine-readable observer status and non-binding DATA PING bridge summary.
- `STATE.json`: previous/current state used for transition detection.
- `events/*.json`: immutable historical activation/deactivation transitions.
- `outcomes/*.json`: automatically matured +24h, +72h, +7d, +14d and +30d outcomes.
- `PERFORMANCE_SUMMARY.json`: descriptive outcome summary, including Top100 relative alpha versus BTC and ETH where available.

Outcome rows measure BTC, ETH, ETHBTC and a matched-constituent Top100 equal-weight return where baseline constituent prices are available. Relative alpha is reported explicitly so a broad-market rise cannot be mistaken for successful altcoin transmission merely because absolute returns were positive.

## Main-thread / DATA PING use

When a main-thread analysis or DATA PING reads this ledger, it must treat it as supplementary learning evidence only.

The Main Framework and Three-Horizon Action Compass remain decision authority. Neither proxy-only breadth nor a later source-quality upgrade can independently graduate a user action. A future ACTIVE state requires explicit later canonical promotion, not inference from data quality.

## Historical first event

The first event remains preserved from the historical 2026-08-20 packet on which the main thread explicitly changed its conclusion to `FIRST GRADUATED ALTCOIN TOP-UP WINDOW: ACTIVE`. Its historical timestamp remains part of the immutable learning record.

v1.2 does not assert that the historical label was canonically valid. It preserves what was recorded, while binding **future** observer authority to the current canonical registry status.
