# ASTRA ADJUDICATION BRIEF - External Tooling Audit 2026-09-15

**Authority:** RESEARCH ONLY. No execution, trading, dependency-installation, promotion, or canonical rewrite authority is created by this file.

**Source:** Claude-generated `AUTO_TRADING_RESEARCH_AUDIT_2026-09-15` package, preserved as non-canonical research input.

## Mission

Given CURRENT MAIN, determine the smallest set of additional mechanisms required to make an Auto Trading result genuinely difficult to fool ourselves with.

Do not choose a new backtester by popularity. Do not build another research machine. Do not install a dependency until a concrete current-main capability gap is demonstrated.

Reconstruct and verify this evidence chain:

`hypothesis -> immutable registration -> trial/search accounting -> point-in-time/leakage controls -> null controls -> multiplicity correction -> parameter stability -> realistic costs/execution assumptions -> OOS -> immutable result -> independent replication -> adjudication -> forward qualification`

For every link classify exactly one of:

- PROVEN_OWNED
- PARTIAL
- BROKEN
- MISSING
- REDUNDANT

## P0 - verify before implementation

1. Independently verify the source claim that replication receipts can pass through a no-op/hardcoded path and that Control Plane can report PASS without importing/recomputing expected receipts. Use current main and current execution-plane state, not historical derived documents. If falsified, close the claim with evidence. If confirmed, this outranks tooling adoption.
2. Verify current trial/search accounting. Determine whether every attempted hypothesis/variant has a monotonic, immutable search-N/trial ledger that survives failures and rejected attempts.
3. Verify leakage and recursive-indicator correctness coverage, including planted-leak tests. Compare current mechanisms against Freqtrade `lookahead-analysis` and `recursive-analysis` as test-spec references, not as adoption targets.
4. Verify whether a same-universe sensor/feature shuffle null control already exists. Missing evidence is not evidence of absence.

## P1 - highest-value experiments

### A. Same-universe shuffle null
If genuinely missing, design the smallest deterministic control that asks whether a candidate signal beats appropriately shuffled features from the same information universe. It must preserve relevant temporal/distributional structure sufficiently to be a meaningful null. Plant known-positive and known-negative cases before using it on real hypotheses.

### B. Multiple-testing family controls
Compare current Benjamini-Hochberg/FDR, bootstrap and effective-N machinery with SPA / Reality Check / StepM / Model Confidence Set capabilities from `bashtage/arch`. Decide capability-by-capability whether to:
- reuse current implementation,
- extract a small mechanism,
- add `arch` as a dependency,
- or reject as redundant.

No dependency addition merely because the package exists.

### C. Parameter-neighbourhood stability
Test the OxfordStrat-derived principle: publish/store the parameter surface or neighbourhood, not only the winning point. Determine the minimum artifact needed to expose brittle optima, cliffs and broad stable plateaus. Prefer extending an existing experiment/result record over creating a new subsystem.

## P2 - external mechanisms worth benchmarking

- Freqtrade: lookahead and recursive-analysis correctness mechanisms. EXTRACT TEST PRINCIPLES ONLY unless a stronger need is proven.
- OxfordStrat: parameter-sensitivity surface principle. EXTRACT if current artifacts cannot express it.
- NautilusTrader: event-driven execution/reconciliation/fill semantics. BENCHMARK ONLY until empirical alpha survives the upstream evidence gates and realistic execution becomes the binding constraint.
- QuantConnect/LEAN: BENCHMARK ONLY. Prove a unique capability gap before any integration proposal.

## P3 - parked by default

VectorBT, PyBroker, Backtrader, Backtesting.py, Jesse, Zipline-Reloaded, OpenBB, yfinance, Alpha Vantage, Nasdaq Data Link, EODHD, Tiingo and similar alternatives remain PARKED/REJECT-FOR-NOW unless current-main evidence demonstrates a unique capability that cannot be obtained more cheaply from an existing owner or a small extracted mechanism.

## Claims that MUST NOT be inherited as facts

1. `framework already owns stronger validation statistics than every engine` - re-evaluate capability-by-capability. Engines solve different layers.
2. `1,000 variants over nine years implies expected best Sharpe 1.04` - preserve as a reproducible simulation/example, not a universal constant. Reproduce assumptions before citing.
3. Licensing and maintenance classifications - verify against current primary repository/license sources before using them in an implementation decision.
4. Replication-integrity counts and PASS/no-import behavior - P0 claim requiring current-main verification.

## Stop rules

STOP and do not build when:
- the capability is already PROVEN_OWNED;
- the proposed tool only increases search/backtest throughput without improving false-positive control;
- a smaller extracted test/mechanism provides the same marginal value;
- point-in-time, leakage, trial accounting, null control or replication integrity is unresolved upstream;
- historical performance is the only promotion evidence;
- implementation creates live trading/execution authority not explicitly granted by canonical governance.

## Required Astra output

Produce one deduplicated adjudication table with:

`capability | current owner | current-main evidence | status | external reference | marginal value | implementation cost | decision | falsification test | next action`

Then return only:

1. P0 defects confirmed/falsified,
2. smallest P1 implementation set,
3. mechanisms explicitly rejected as redundant,
4. tests/receipts proving each accepted change,
5. remaining blockers before any strategy can progress to forward qualification.

## Success criterion

A successful mission may result in zero new dependencies and only a few hundred lines of tests/control logic. Architectural growth is not a success metric. Stronger falsification, lower false-positive risk, reproducibility and trustworthy independent verification are.
