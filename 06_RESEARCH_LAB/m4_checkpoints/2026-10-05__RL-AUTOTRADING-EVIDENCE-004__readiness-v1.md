# M4 Auto Trading Evidence Machine Readiness Checkpoint v1

**Mission:** `RL-AUTOTRADING-EVIDENCE-004`
**Date:** 2026-10-05
**Status:** FROZEN_INPUT_FOR_INDEPENDENT_REVIEW
**Authority:** RESEARCH_ONLY / NO_EXECUTION
**Framework main at freeze:** `e505e23e9f9f1fef75e65f265ef0b43d119a267f`

## Research question

Is the AUTO_TRADING evidence machine clean enough to admit a very small number of new empirical hypotheses, and if so which existing hypotheses have the highest value of information per forward slot?

## Current owner posture

`04_RESEARCH_LAB/auto_trading/README.md`:

`EVIDENCE MACHINE / RESEARCH ONLY / NO EXECUTION LAYER`

The empirical ordering remains:
1. historical source reconciliation;
2. proposal-time monotonic trial accounting;
3. mechanical temporal/leakage tests;
4. only then statistical search / actual hypotheses.

## Readiness matrix

### R1 - Historical high-value source reconciliation
**PASS**

Artifact:
`04_RESEARCH_LAB/auto_trading/audit_summaries/2026-09-14__historical-market-archive-reconciliation-closure-v1.json`

Result:
`P0_RECONCILIATION_ACCEPTANCE_SATISFIED`

Key facts:
- 35-symbol Binance Vision hourly panel, 851,882 rows, 2020-09-01 through 2026-07-31;
- independent SOLUSDT overlap check: 24/24 timestamps matched, max absolute differences zero for compared source fields;
- no bulk duplicate backfill needed;
- raw source fields research-admissible under coverage limits;
- pre-fix derived hourly return/OI-change history remains quarantined.

### R2 - Leakage detector can catch known defects
**PASS**

Artifact:
`04_RESEARCH_LAB/auto_trading/experiments/E1_LEAKAGE_VALIDATION_RESULT_v1.json`

- causal right-truncation controls pass;
- warm-up controls pass;
- planted shift(-1) and centered-window leaks detected;
- ambiguous timestamps fail closed;
- E1 verdict PASS.

Production extension E1X also reports 14/14 detector/classification controls meeting expectations.

### R3 - Production temporal-integrity surface
**PARTIAL / SOURCE-SCOPED**

E1X found true leaks in historical research consumers, but did not find a true-future-leak path in the active production market-state / CN / intraday surfaces it tested.

Important restrictions:
- pre-fix hourly derived return/OI-change history remains quarantined retrospectively;
- PDLT discovery labels have a known unclosed-candle-anchor issue and remain unsuitable without governed repair/reopen;
- copper/gold historical event-study signal timing requires publication-time repair before reuse;
- ETF historical timing is separately governed by the M1 Temporal Integrity outcome;
- future historical replay must respect source vintages.

Prospective post-fix hourly derived evidence is usable under existing research gates.

### R4 - Real hypothesis can be preregistered and killed honestly
**PASS**

Theory:
`AT-HYP-0019` rolling range normalization versus raw sentiment.

Trial sequence:
- N1: leakage validation prerequisite;
- N2: historical test, initially mis-adjudicated because relative improvement over negative OOS IC was allowed;
- N3: method correction replay, same data, explicitly NOT independent evidence;
- N4: frozen source binding blocked, counts as attempt, outcome not inspected;
- N5: independent prospective source preregistered before outcome replay.

N5:
`04_RESEARCH_LAB/auto_trading/experiments/E3_TRIAL_N5_INDEPENDENT_RESULT.json`

Result:
`INDEPENDENT_NOT_SUPPORTED`

No normalized transform passed the frozen positive-OOS gate.

This is positive evidence about the evidence machine even though it is negative evidence about the hypothesis.

### R5 - Proposal-time attempt denominator
**FUNCTIONALLY SUPPORTED / CENTRALIZATION GAP**

Evidence:
- experiment artifacts preserve N1-N5;
- failed and abandoned attempts explicitly remain counted;
- N4 blocked trial remains in denominator;
- N5 has a separate experiment-lifecycle candidate with `proposal_trial_n=5` and frozen source binding;
- weekly experiment adjudication retains AT-HYP-0019.

Gap:
Historical/remediation references mention:
`04_RESEARCH_LAB/auto_trading/trials/AT_TRIAL_LEDGER_v2.json`

That path does not exist on current main.

Interpretation:
Experiment lifecycle currently provides functional immutable attempt lineage for AT-HYP-0019, but there is not a single obvious current AUTO_TRADING-wide monotonic trial-denominator object across all future theories.

Therefore broad autonomous hypothesis generation/search remains inadmissible.

### R6 - AT-EXP-004 data-plane remediation lifecycle
**REMEDIATION RESOLVED / HISTORICAL QUARANTINE RETAINED**

The bounded remediation candidate is RESOLVED and has a MISSION_CONVERGENCE receipt with acceptance items satisfied.

However:
- historical damaged derived rows were intentionally not rewritten;
- retrospective alpha claims may not silently use those rows;
- this closure did not itself grant trading or capital authority.

## Preliminary readiness verdict

**READY_FOR_SELECTIVE_PREREGISTERED_RESEARCH, NOT_READY_FOR_BROAD_AUTONOMOUS_SEARCH**

Admissible next step:
- choose at most 2-3 already-existing theories;
- one proposal-time immutable identity/attempt record per test;
- clean or source-specific PIT data only;
- explicit baseline/falsifier/cost model before outcomes;
- history may falsify/rank; clean independent forward evidence is required for stronger confirmation.

Not admissible:
- generating dozens of variants;
- LLM strategy sweeps;
- tuning after outcome inspection;
- using quarantined historical derived columns as clean evidence;
- treating the 22-item theory ledger as 22 independent free shots;
- creating an execution layer.

## Candidate theory universe

Already tested:
- `AT-HYP-0019`: independent evidence NOT SUPPORTED. Do not immediately retest without a genuinely new hypothesis/data basis.

Potential high-information candidates must be chosen from existing ledger only.

Examples requiring ranking, not automatic selection:
- AT-HYP-0002 - regime-conditioned strategies beat universal strategies;
- AT-HYP-0005 - no-trade is an explicit action;
- AT-HYP-0006 - execution quality can dominate forecast quality;
- AT-HYP-0016 - global + asset-specific regime hierarchy;
- AT-HYP-0017 - time-loss exits reduce stagnant capital drag;
- AT-HYP-0018 - public CFGI features explain MAEVE actions;
- AT-HYP-0021 - specialist observers improve coverage without execution authority;
- AT-HYP-0022 - agent disagreement as uncertainty signal.

## Ranking criteria for Sol

Score conceptually, do not invent false numeric precision:
1. data already available and PIT-safe;
2. test can be deterministic;
3. clear baseline;
4. clear falsifier;
5. low multiple-testing burden;
6. low overlap with existing framework experiments;
7. short calendar time to informative outcome;
8. real potential decision value;
9. low execution-data dependency;
10. failure would teach something reusable.

Select **at most three**.
Selecting zero is allowed.

For each selected candidate provide:
- why now;
- minimum test;
- frozen baseline;
- falsifier;
- required data;
- forward-slot burden;
- duplication risk;
- promotion evidence burden.

Do not design live trading.
