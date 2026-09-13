# EXTERNAL ARCHITECTURE AUDIT — SECOND-PASS DECISION

Date: 2026-09-12
Status: `RESEARCH_ONLY / NON-EXECUTION / PRIORITIZATION_DECISION`
Owner: `04_RESEARCH_LAB/auto_trading/`
External audit snapshot: `39740dd390f58b47ce99fe0a8f861ef7dd12f4cd`
Current main reviewed in second pass: `b5d6d9d645d14453186336c6ce5c0c5dd3d3ff49`
Source audit file SHA-256: `8a479ca113388f99c480967f235badf10cafc2df3dd2cf229af3f3905dbf551a`

## Purpose

Record the framework-native decision after reviewing the independent Cowork architecture audit against the current repository state.

This file does not grant execution authority and does not create a new engine. It changes research priority, closes one rejected adapter lane, and makes empirical validation the next binding objective.

## Second-pass verdict

The independent audit materially improves the roadmap and is accepted as the strongest external architecture review of AUTO_TRADING to date.

The core conclusion is adopted:

> The current architecture is not primarily constrained by missing orchestration or execution infrastructure. It is constrained by insufficient executed, falsifiable strategy research and by missing mechanical protections around historical testing.

The framework should therefore spend the next marginal unit of effort on **evidence production and falsification**, not on additional agent roles, execution engines or governance prose.

### Important snapshot correction

The audit inspected repository snapshot `39740dd3`. Current `main` is already 23 commits ahead of that snapshot and now contains active experiment-lifecycle dispatch/observation artifacts outside this AUTO_TRADING ledger.

Therefore the audit sentence "nothing has been run" must be scoped precisely:

- **Verified current fact:** `04_RESEARCH_LAB/auto_trading/THEORY_LEDGER.md` still contains 22 hypotheses and none is marked as having completed a strategy test.
- **Not adopted as a repo-wide current claim:** the broader repository now contains live experiment-lifecycle activity.

This distinction does not weaken the audit's main AUTO_TRADING prioritization conclusion.

## Adopted findings

### A1 — Empirical work now outranks new architecture work

No new autonomous-trading engine, signer, matching engine, swarm or desktop adapter should be built before the first P0 evidence tasks below are complete.

### A2 — Trial count `N` becomes a first-class research object

AUTO_TRADING must eventually have one immutable, monotonic hypothesis-attempt counter incremented at proposal time, including failed/abandoned implementations.

This is a prerequisite for defensible multiple-testing control under high-throughput Astra research.

The counter must not be reset because a strategy family changes, an implementation fails, or a candidate is discarded before reporting.

### A3 — Mechanical leakage tests move ahead of statistical sophistication

Two property tests are promoted to P0 research:

1. right-truncation invariance — values available at time `t` must not change when observations after `t` are appended;
2. left-truncation / warm-up convergence — recursive indicators must publish convergence error versus declared startup history.

A statistical correction cannot repair a feature that was computed with future information.

### A4 — Historical backfill is primarily a falsification asset

Longer free history should be acquired before broad strategy mining, but historical success alone is not sufficient promotion evidence.

Framework wording adopted for promotion governance:

> Historical evidence may falsify, rank and stress-test candidates. Historical success does not by itself authorize promotion. Promotion-strength evidence must ultimately include sealed prospective/frozen-forward observations generated after the research specification is frozen.

This is deliberately more precise than treating "history can only kill" as a universal epistemic statement.

### A5 — Sharpe precision is calendar-time constrained

The audit's zero-edge iid baseline is mathematically sound:

`SE(annualised Sharpe) ≈ 1 / sqrt(calendar years)`

so increasing bar frequency does not create independent calendar-time evidence.

Use this identity as a **baseline planning approximation**, not as a universal estimator. Real strategy-return autocorrelation, non-stationarity, overlapping positions and regime segmentation must inflate uncertainty where applicable.

Independent second-pass arithmetic reproduced the audit's key selection-hurdle examples, including approximately `2.00` annualised Sharpe for `N=1000`, `Y=6` under the stated approximation.

### A6 — Search throughput must be budgeted, not maximized

Astra should not be optimized for hypotheses/hour.

Target metric:

`reproducible surviving research / unit of compute and calendar evidence`

Astra hypothesis generation remains valuable for research design, coding and failure analysis, but broad strategy mining is blocked until trial accounting and multiplicity controls exist.

### A7 — Event-driven execution engine is deferred

NautilusTrader remains a valuable future benchmark/component candidate, especially for reconciliation, typed event semantics, funding and venue lifecycle modelling.

It is not a P0 dependency for bar-level AUTO_TRADING research.

Adoption should be reconsidered only after data granularity and strategy frequency make the additional execution fidelity observable and decision-relevant.

### A8 — Borrow Nautilus Agents protocol ideas, not the current crate

High-value transferable concepts:

- `Observation -> Proposal -> Decision -> Receipt` separation;
- engine/validator owns the decision;
- agent owns only a bounded proposal;
- explicit `provenance[]` and `omissions[]`;
- expiring capability grants;
- canonical digesting;
- `DispatchUnknown`-style ambiguity states.

Do not adopt the current early-alpha crate as a runtime dependency solely because the architecture is attractive.

### A9 — RD-Agent is a negative benchmark, not a component

Retain for study of autonomous quant-R&D loops and Trace-DAG provenance.

Reject its default strategy-selection architecture for our use because proposer/judge independence, adaptive holdout discipline and multiplicity control are insufficient for our governance standard.

### A10 — Condor is a principle source, not a runtime component

Borrow:

- fail-closed confirmation semantics;
- timeout/no-delivery => deny;
- asymmetric brakes/exposure reduction;
- independent `book_trusted`-style state verification.

Reject as a component while a generic unsandboxed code path can bypass narrow trading gates or credential boundaries.

### A11 — TradingView MCP lane is closed for AUTO_TRADING

Independent second-pass review verified that the repository README explicitly says the tool must not be used for:

`Performing automated trading or algorithmic decision-making using extracted data`

The same repository also depends on TradingView Desktop, a local Chrome DevTools port and undocumented application internals.

Therefore:

`TRADINGVIEW_MCP_RESEARCH_QUEUE = REJECTED_FOR_AUTO_TRADING`

The prior research note remains archived for provenance. No install or benchmark is justified inside AUTO_TRADING.

If Pine-only authoring/compiler ideas are ever independently useful, they require a separate terms-safe evaluation that does not consume TradingView-extracted market data for algorithmic decisions.

### A12 — Option A is adopted as the present operating posture

Current posture:

`EVIDENCE MACHINE / RESEARCH ONLY / NO EXECUTION LAYER`

This does **not** permanently reject future paper/live infrastructure. It means future execution work must be triggered by evidence rather than anticipated in advance.

## Findings not promoted to canonical truth

### C1 — The audit's numeric probability of live capital within five years

The report's `~12%` estimate is an informed subjective inference, not a measured framework probability.

Preserve it as author judgement only. Do not encode it into routing, promotion or budget logic.

### C2 — Binance back-history quality is not assumed clean before reconciliation

The audit reports that Binance Vision exposes deep free history and that some futures metrics objects appear to have been regenerated in March 2026.

The opportunity is high-value, but source quality must be tested rather than assumed.

Required ingest provenance for every archive object:

- source URL/path;
- retrieval time;
- checksum / content hash;
- `ETag` where available;
- `Last-Modified` where available;
- event timestamp semantics;
- reconstruction/revision tag where known;
- sorted-time invariant before downstream use.

### C3 — "History can only kill" is adopted only as a promotion rule

Historical evidence remains useful for:

- falsification;
- feature debugging;
- leak discovery;
- ranking;
- parameter sensitivity;
- cost stress;
- regime stress;
- replication.

The strong rule is that historical success cannot by itself create execution authority.

## Reprioritized research queue

### P0 — Do before more architecture expansion

1. **Historical archive reconciliation**
   - backfill the highest-value free Binance series;
   - compare the overlapping period against the framework's independently captured data;
   - classify agreement, systematic difference or random capture/source error.

2. **Monotonic proposal-time trial counter**
   - define what counts as a hypothesis attempt;
   - increment before implementation/result visibility;
   - preserve failures and abandoned candidates;
   - never reset silently.

3. **Mechanical leakage / convergence tests**
   - right-truncation invariance;
   - left-truncation convergence;
   - planted-leak benchmark before trusting the detector;
   - freeze required warm-up per feature/sensor.

### P1 — Immediately after P0

4. Evaluate `arch` SPA / StepM / MCS against the framework's existing bootstrap implementations.
5. Add DSR/minimum-backtest-length style search-budget checks without importing incompatible licensing.
6. Derive embargo/purge width structurally from prediction/label horizon.
7. Audit the selection **procedure** with PBO/CSCV concepts, not only individual strategies.
8. Reuse existing receipts and add only proven missing fields such as trial count / chain linkage if current owners do not already cover them.
9. Separate evaluation context from governance/repository-memory context where historical strategy knowledge would contaminate a purported holdout.

### P2 — Only after real candidates survive

10. Cheap deterministic high-throughput screener, benchmarked against an independent implementation.
11. Prospective/frozen-forward slot and power-budget design.
12. `aggTrades` / top-of-book acquisition when required by the surviving strategy family's execution horizon.
13. Reassess Nautilus or another deterministic engine only when richer data makes its fidelity testable.

## Specific architecture changes caused by the audit

### KEEP

- Research Lab ownership;
- F12/adjudication;
- point-in-time evidence firewall;
- frozen-forward promotion concept;
- Minimum Sufficient Intelligence;
- bounded subagents with unique question ownership;
- independent validation;
- artifact-backed research;
- explicit NO_EDGE / reject outcomes.

### DEMOTE / DEFER

- execution-engine selection;
- microstructure fidelity beyond observed data needs;
- agent-swarm scaling;
- complex signer/governor implementation;
- GUI/Pine research lanes;
- hypothesis-volume optimization.

### ADD / PROMOTE

- `N` trial accounting;
- mechanical leakage tests;
- source reconciliation before backfill trust;
- multiple-testing maximum/search-bias controls;
- power-aware frozen-forward planning;
- taint/provenance discipline for attacker-writable free text;
- explicit distinction between governance context and blinded evaluation context.

## Next acceptance condition

The next major AUTO_TRADING architecture review should be triggered by **empirical output**, not another architecture source.

Minimum trigger:

- reconciliation result exists;
- leak detector has been validated on planted defects;
- proposal-time `N` is operational;
- at least one existing hypothesis has moved from `QUEUED` into an actual reproducible test artifact.

Until then, new external repositories may still be logged for discovery, but they should not displace the P0 empirical work.

## Final decision

The audit is accepted with the snapshot and statistical caveats above.

The roadmap changes from:

`prepare increasingly sophisticated autonomous trading infrastructure`

into:

`prove the research process can produce one honest, reproducible surviving result before building the capital path`.

That is the current canonical prioritization decision for AUTO_TRADING. It grants no trading authority.