# Memes v3 — FOMO Radar forensic benchmark v1

**Date:** 2026-09-12  
**Status:** OWNER-APPROVED RESEARCH ADDENDUM  
**Authority:** RESEARCH ONLY / SHADOW ONLY  
**Parent owner:** `2026-09-09__memes-v3-autonomous-alpha-research-workstream-v1__operational.md`  
**Method owner:** `2026-09-11__memes-v3-empirical-hardening-adjudication-v1__research-addendum.md`

## Purpose

Bind the public `cvxv666/fomo-robinhood-radar` implementation into the existing Memes v3 / Alpha Lab workstream as an external forensic benchmark and ablation source.

This addendum does not fork the external product, does not create a parallel scanner, and does not grant any trade authority.

Frozen external source commit:

`1c448e97a9617a19793aafb7963138e36ec5a1bf`

Primary provenance note:

`04_RESEARCH_LAB/auto_trading/source_notes/AT-SRC-0012_FOMO_ROBINHOOD_RADAR_FORENSIC_BENCHMARK.md`

Restricted evidence manifest and deep-log adjudication are stored in the private research plane.

## Why this enters Alpha Lab

The external project independently encountered several manipulation and attribution failures that map directly to current Alpha Lab research:

- profile address is not necessarily the execution wallet;
- execution wallet is not necessarily a discretionary trader address;
- token receipt from a router is not necessarily an intentional wallet buy;
- low-value seeded/dust flows can manufacture apparent multi-wallet convergence;
- raw wallet convergence is not independent entity convergence;
- leaderboard PnL can conceal one-hit, unrealized or attribution effects;
- a historical rule crossing is not the same as a contemporaneously delivered alert;
- entry signals without exits miss first-distribution information.

## Canonical additions to the research method

### TRADE_PROVENANCE_GATE

Any fill used by wallet-alpha, convergence, Early Confirmation or alert research must first be classified with enough deterministic evidence to distinguish at least:

- intentional wallet trade;
- direct recipient spoof / gifted swap;
- dust/probe;
- passive transfer;
- service/router/protocol flow;
- unresolved.

`UNRESOLVED` fails closed for promotion-grade evidence.

This gate sits after address-role resolution and before wallet skill or convergence scoring.

### Signal-time decomposition

Persist distinct timestamps where available:

- `condition_time`
- `observed_at`
- `computed_at`
- `alert_delivery_time`
- `first_executable_time`

Historical replay may infer `condition_time`; it may not silently backfill a historical live alert.

### Entity-adjusted convergence

Test both:

`raw_wallet_conviction`

and

`independent_entity_conviction`.

Common funders, shared controllers, coordinated service addresses and other graph evidence reduce assumed independence.

### Exit consensus

Extend First Distribution Survival with a research view of cohort exit:

- fraction of original independent conviction exited;
- exit acceleration;
- genuine sell vs transfer/migration;
- liquidity-adjusted pressure;
- new-buyer absorption;
- remaining high-quality cohort.

No fixed sell/exit threshold becomes canonical without prospective validation.

## External claims that remain unverified / bounded

The external project reports strong operational and replay metrics, including FLYBRAIN early detection and burst-rule outcome tables. These remain provider/self-reported claims until reproduced under Alpha Lab's own temporal and executable-return rules.

Specifically:

- current-score historical replay is ineligible for promotion because it can use a wallet score learned after the historical trade;
- a historical FLYBRAIN threshold crossing must be separated from the actual database/delivery latency of the system at that time;
- `2x reached` is not sufficient without path, drawdown, liquidity, executable depth and baseline context;
- the external 0-100 wallet bands are not imported as canonical alpha;
- model identity such as `Astra` or `Claude` carries no evidentiary authority.

## Required ablation mission

Codex should implement the minimum viable Alpha Lab versions of the strongest mechanisms and compare them against the existing baseline rather than transplanting the external stack.

Required comparisons:

1. no provenance gate vs receipt-level provenance gate;
2. raw wallet convergence vs independent-entity convergence;
3. fixed absolute dust vs wallet-relative/adaptive dust vs no dust filter;
4. no seeded-token quarantine vs adversarial seed quarantine;
5. current/global wallet score vs strict as-of conditional wallet evidence;
6. entry-only signal vs entry + exit-consensus state;
7. non-regime-conditioned burst vs Cycle Navigator conditioned evaluation;
8. chart return vs executable return.

A mechanism survives only if it adds prospective value after complexity, latency and false-negative cost are counted.

## High-value fixtures

Preserve and reproduce where evidence permits:

- recipient-spoof / gifted-wallet incident from the external project log;
- seeded low-dollar multi-wallet contamination case;
- a genuine trusted-wallet buy as positive control;
- FLYBRAIN replay with separate condition/detection/delivery/execution timestamps;
- CRUMBS-style broad cohort exit case;
- external scoring calibration where `active` vs `watch` separation weakens under marked outcomes.

External fixture labels are source claims until independently reconstructed.

## Promotion boundary

Nothing in this addendum may directly create:

- `QUALIFIED_ALPHA`;
- BUY/SELL/sizing output;
- portfolio authority;
- autonomous execution;
- public wallet disclosure;
- a new scheduler;
- a new research-governance stack.

Promotion still requires the existing exploration -> frozen hypothesis -> validation -> prospective shadow -> governance path.

## Astra use later

Astra should receive this benchmark only after deterministic collectors and Codex ablations exist.

Use Astra for:

- adversarial source-conflict adjudication;
- entity/provenance ambiguity;
- causal experiment design;
- red-team of threshold and replay assumptions;
- comparison of external vs Alpha Lab mechanisms;
- simplification where an external mechanism achieves equal value with less complexity.

Do not spend Astra on routine RPC parsing, arithmetic, fixed transformations or polling.
