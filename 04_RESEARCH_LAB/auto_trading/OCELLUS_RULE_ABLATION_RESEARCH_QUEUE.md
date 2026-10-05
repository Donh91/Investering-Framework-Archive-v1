# Ocellus Rule-Ablation Research Queue - 2026-10-05

Status: RESEARCH_QUEUED / AUTO_TRADING / NO_EXECUTION_AUTHORITY
Parent source note: source_notes/AT-SRC-0017_OCELLUS_RULE_ABLATION_AND_LAUNCH_INTELLIGENCE.md
Cross-repo Alpha spec: Donh91/Meme-Alpha-Lab research/discovery/OCELLUS_DEEP_DIVE_EXPERIMENT_SPECS_2026-10-05.md

## Research question

Can explicit all-refusal accounting plus paired single-rule shadow portfolios improve the Framework's ability to identify which decision gates create real post-cost value and which merely create false-negative opportunity cost?

## Why Research Lab should own the generic method

This is broader than meme discovery. The method can later be used on any strategy family that reaches a frozen-forward or paper stage, including BTC/ETH systematic strategies, alt strategies, wallet-following hypotheses, regime-conditioned entries, exit rules and risk vetoes.

The method belongs inside existing experiment lifecycle and AUTO_TRADING governance.

## R1 - Refusal Opportunity Ledger

Design a reusable schema recording every evaluated gate, every refusal, sole-blocker status, champion decision, one-gate-removed counterfactual eligibility, frozen input timestamp and matured post-cost outcome.

Do not create a second Forecast Ledger.

Required output: schema proposal, owner mapping, duplication audit and migration path into existing experiment artifacts.

## R2 - Paired single-rule ablation harness

Specify a harness where champion and challenger read the same opportunity set, share the same clock, use identical costs/fills and differ on one declared rule only.

Required output: pre-registration contract, version freeze contract, pairing key, trial-count semantics and interaction-risk policy.

## R3 - Gate-value metrics

Develop metrics that separate avoided downside, foregone upside, correct refusal, false refusal, redundant refusal and regime-specific value.

Candidate primary statistic should be a paired post-cost difference with uncertainty/confidence reported. Do not optimize a single headline metric before data exists.

## R4 - Multiple-testing protection

Define search budget, trial counter, pre-registered families, holdout/frozen-forward rules, family-wise/FDR treatment where appropriate, and retirement/no-retry rules.

## R5 - Exit-policy decomposition

Use common frozen entries to compare exit policies separately from selection.

Measure return after costs, MFE capture, MAE, peak giveback, time in market, capital occupancy and tail loss.

## R6 - Refusal calibration

Treat NO_TRADE as a decision with an outcome.

The audit must answer what would have happened if the refused opportunity had been taken, which single gate caused the refusal, whether the gate was protective or costly and whether another gate made it redundant.

This connects to existing FNP/opportunity-cost discipline without rewriting FNP ownership.

## R7 - Ocellus as external benchmark, not truth

If useful, use the public Ocellus rules/API as a reproducible external comparison set.

Do not adopt its composite risk score, current paper PnL as strategy evidence, numeric thresholds as defaults, smart-wallet labels as verified or infer proprietary AI internals.

## Success condition

Produce a minimal reusable experiment contract that determines the marginal value of a gate without hindsight edits, unequal opportunity sets, unequal fill/cost assumptions, silent trial proliferation or live trading authority.

## Kill criteria

Stop or revise if one-rule attribution is dominated by interactions, the candidate universe cannot be frozen consistently, costs/fills cannot be common across variants, opportunities are too dependent for useful inference or maintenance exceeds likely information value.

If interactions dominate, escalate only to a pre-registered interaction/factorial design, not ad-hoc combinations.