# Ocellus Research Execution - 2026-10-05

Status: METHOD_PROTOTYPE_EXECUTED / EMPIRICAL_EDGE_PENDING / RESEARCH_ONLY
Research issue: #1507
Alpha implementation: Donh91/Meme-Alpha-Lab PR #97
Parent queue: ../OCELLUS_RULE_ABLATION_RESEARCH_QUEUE.md
Source note: ../source_notes/AT-SRC-0017_OCELLUS_RULE_ABLATION_AND_LAUNCH_INTELLIGENCE.md

## Executive result

The Ocellus transfer has moved beyond source review into an executable research primitive.

Meme Alpha Lab now has a tested all-refusal / sole-blocker instrument that can measure the marginal value and opportunity cost of individual decision gates prospectively.

No gate edge is claimed yet because the current v4 paper-wallet decision and terminal-outcome ledgers have no matured rows.

That is a scientific result, not a failure: the method is ready before the observations it will grade.

## Implementation produced

Alpha PR #97 adds:

- GATE_REFUSAL_CONTRACT_V1;
- gate_refusal_ledger_v1.csv;
- gate_refusal_outcomes_v1.csv;
- deterministic freeze/mature/report code;
- sole-blocker attribution;
- interaction-only treatment for multi-blocker refusals;
- immutable duplicate-decision rejection;
- hash-chained research rows;
- full-repo Ocellus data-readiness audit;
- CI and scientific-control tests.

The implementation has no signing, real-fund, automatic-trading or portfolio authority.

## Scientific interpretation

For marginal single-gate attribution:

- exactly one refusing rule -> eligible sole-blocker observation;
- more than one refusing rule -> interaction evidence only;
- taken decisions cannot contain a refusing gate;
- outcomes mature later under the same cost/fill semantics;
- no retrospective rule edits are allowed.

This is materially stronger than a strategy log that stores only the first or final rejection reason.

## First empirical data-readiness receipt

A full-repo CI scan on 2026-10-05 found:

- Birth Tape rows: 124,170;
- unique token IDs: 123,496;
- Robinhood-chain Birth Tape rows: 116,232;
- Robinhood launch-evidence rows: 111,864;
- Robinhood launch-evidence files: 26;
- malformed launch-evidence JSON rows: 0;
- DexScreener PROFILE events: 4,009;
- DexScreener BOOST events: 2,927;
- point-in-time snapshot rows: 19;
- snapshot rows with liquidity: 19;
- snapshot rows with holders: 0;
- snapshot rows with creator_pct: 0;
- snapshot rows with top10_real_pct: 0;
- v4 frozen paper decisions: 0;
- terminal labels: 0.

Robinhood exact launch evidence currently contains:
token/curve/deployer/block/transaction identity, but not verified buyer/seller cohort history, graduation progress or trade amounts.

## Ocellus-derived method rulings

### GATE_REFUSAL_VALUE_V1
State: READY_FOR_PROSPECTIVE_CAPTURE

Instrument exists and is tested.
Blocker to an edge conclusion: no matured gate sample yet.

### SINGLE_RULE_PAIRED_COHORT_V1
State: SCHEMA_READY_DATA_PENDING

The causal design is valid, but no v4 decisions exist yet from which to run paired variants.

### EARLY_BUYER_RETENTION_V1
State: ADAPTER_GAP

Current Pons launch evidence does not contain verified buy/sell cohort history.

A concrete Alpha adapter gap is now owned as:
ROBINHOOD_PONS_CURVE_TRADE_HISTORY_V1.

### CREATOR_FATE_PRIOR_V1
State: ADAPTER_GAP

Current canonical launch evidence resolves deployer identity but does not contain sufficient point-in-time matured creator history.

Ocellus creator endpoint is a candidate challenger, not truth.

### PRE_GRADUATION_VELOCITY_V1
State: PARTIAL

Canonical exact curve identity exists, but repeated curve-progress observations are missing.

### HOLDER_EXIT_OVERHANG_STRESS_V1
State: PARTIAL

Liquidity snapshots exist; entity-adjusted holder history is incomplete.

### MATERIAL_STATE_DELTA_V1
State: PARTIAL_READY

The null-safe delta method is valid but needs comparable repeated observations and entity normalization.

### DEX_PROFILE_VISIBILITY_EVENT_V1
State: READY_EVENT_STUDY

Current DexScreener PROFILE observations can support a generic visibility-event study.

### DEX_PAID_ATTENTION_EVENT_V1
State: ADAPTER_GAP

Important correction during audit:
a DexScreener PROFILE or BOOST observation must not be silently equated with Ocellus dexPaidAt.

Ocellus documents dexPaidAt specifically as the timestamp when DexScreener approved a paid profile. That semantic must be independently captured/audited before this method is called paid-attention research.

## External API audit

Ocellus public API is judged OPTIONAL_EXTERNAL_CHALLENGER, not a canonical dependency.

Highest-value challenger fields:
1. Robinhood curve progress / raised / target / payToken;
2. creator launch/dead/graduated history;
3. dexPaidAt;
4. holder concentration;
5. sellability / sellCost.

Do not import:
- composite Ocellus risk score as edge;
- smart-wallet labels as truth;
- paper-account PnL;
- exact thresholds.

The Alpha chain-derived launch event remains canonical for launch identity.

## Generic AUTO_TRADING transfer

The Research Lab-wide reusable primitive is:

same opportunity set
+ same clock
+ same costs/fills
+ exactly one changed rule
+ all refusal reasons recorded
+ sole-blocker attribution
+ later counterfactual maturation.

This can later apply to any sufficiently mature paper/frozen-forward strategy family without importing meme-specific features.

## Rulings on queue work packages

R1 Refusal Opportunity Ledger: PROTOTYPE EXECUTED in Alpha.
R2 Paired single-rule harness: SPECIFIED, DATA PENDING.
R3 Gate-value metrics: PROTOTYPE EXECUTED for sole-blocker post-cost/MFE/MAE outcomes.
R4 Multiple-testing protection: GOVERNANCE REQUIRED BEFORE MULTI-VARIANT EXPANSION.
R5 Exit-policy decomposition: SPECIFIED, NOT YET RUN.
R6 Refusal calibration: INSTRUMENTED, OUTCOMES PENDING.
R7 Ocellus external benchmark: SOURCE AUDITED, OPTIONAL CHALLENGER ONLY.

## Next evidence sequence

Do not create another engine.

1. Let the new refusal ledger collect genuinely prospective decisions.
2. Mature refused opportunities under frozen common cost/fill rules.
3. Run one-rule paired challenger only after a non-trivial common opportunity sample exists.
4. In parallel, close the narrow Pons curve-trade adapter gap if deterministic event semantics can be proven.
5. Test Ocellus API as a bounded challenger only if incremental information value justifies the dependency.
6. Promote nothing on architecture elegance alone.

## Current conclusion

The strongest Ocellus idea survived the design audit and has been converted into a testable internal method.

Evidence that the method improves returns is still UNKNOWN.

That distinction is intentional and binding.
