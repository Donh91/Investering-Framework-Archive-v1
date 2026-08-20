# Cowork Opus 5 - Maximum Value Sidecar Protocol

This file is mandatory companion context to `COWORK_OPUS5_MASTER_RESEARCH_PROMPT.md`.

These sidecars MUST remain analytically separate from the core Historical Altseason Pullback result. Their purpose is to harvest additional value from the same evidence without contaminating the primary hypothesis set or silently expanding production authority.

## S1 - Signal Interaction Atlas

Question: do combinations of independently sourced feature families add robust information beyond their individual components?

Test interactions among, at minimum, free breadth, direct ETH/BTC, CFGI families, flow/execution evidence, momentum and volume/liquidity context. Prefer 2-4 family combinations. Penalize search volume and report the exact search space.

Required output: `SIDECARS/SIGNAL_INTERACTION_ATLAS.md` plus machine-readable candidate table.

For every interaction report base-model delta, effect size, uncertainty, coverage, false positives, era replication, redundancy and whether the interaction survives multiplicity correction and leave-one-episode-out testing.

Do not promote an interaction simply because its in-sample fit exceeds its components.

## S2 - Lead/Lag and Information Timing Atlas

Question: when does each useful feature become actionable relative to local top, trigger, trough, reload and continuation?

Evaluate exact timestamp-aware lead/lag structure across supportable horizons, including 1h, 3h, 6h, 12h, 24h, 48h and 72h where data exists.

Required output: `SIDECARS/LEAD_LAG_INFORMATION_TIMING.md` plus event-level timing table.

Distinguish first deviation, first persistent deviation, confirmation and post-price reaction. Record data-availability time and reject signals whose apparent lead disappears under realistic availability timing.

## S3 - Failure and Opportunity-Cost Laboratory

Question: how does every promising candidate fail, and what does reacting to it cost when it is wrong?

Required output: `SIDECARS/FAILURE_AND_OPPORTUNITY_COST_LAB.md`.

Include dedicated forensics for false trims, premature trims, missed upside, late trims, falling-knife reloads, premature reloads, late reloads, false pullback warnings and cases where a candidate never gives a usable action window.

Every candidate that reaches OBSERVE or FORWARD_TEST must have an explicit failure taxonomy and opportunity-cost estimate versus HOLD after friction.

## S4 - Minimal Sufficient Signal Stack

Question: what is the smallest transparent set of feature families that preserves most of the robust out-of-sample information?

Required output: `SIDECARS/MINIMAL_SUFFICIENT_SIGNAL_STACK.md`.

Start from the strongest validated candidate set and perform disciplined ablation. Report marginal contribution, redundancy and performance decay as families are removed. Prefer a smaller stack when it retains approximately comparable robustness. Do not optimize a fixed target such as exactly 95%; show the full trade-off curve.

The result may conclude that no stable compact stack exists.

## S5 - Research Opportunity Register

Create `SIDECARS/RESEARCH_OPPORTUNITY_REGISTER.md` and a machine-readable register for all potentially valuable observations discovered outside the pre-specified core questions.

Every entry must be classified as one of:
- `REJECT`
- `INSUFFICIENT_DATA`
- `RESEARCH_LATER`
- `FORWARD_TEST_CANDIDATE`

Record why it was noticed, whether it is pre-specified or post-hoc, data requirements, leakage risk, multiplicity family, falsifier and next test required.

No opportunity-register item may modify the primary historical conclusion or receive production authority in this engagement.

## Mandatory separation and evidence labels

Every result across core research and sidecars must carry one of:
- `PRE_SPECIFIED`
- `EXPLORATORY`
- `POST_HOC_DISCOVERY`

Keep these evidence families separate in tables, significance correction and conclusions. A post-hoc discovery may at most become a future test candidate.

## Cross-sidecar synthesis

After all sidecars are complete, produce `SIDECARS/SIDECAR_SYNTHESIS.md` with:
- what added genuine incremental information
- what was redundant
- what failed
- what remains untestable
- what deserves prospective forward testing
- what should be permanently ignored

The synthesis must not replace the primary research report. Historical findings remain capped at `FORWARD_TEST`, and all portfolio execution authority remains false.
