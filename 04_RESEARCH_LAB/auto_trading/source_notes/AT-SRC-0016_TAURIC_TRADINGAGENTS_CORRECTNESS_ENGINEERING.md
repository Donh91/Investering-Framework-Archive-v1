# AT-SRC-0016 - TauricResearch TradingAgents correctness engineering

Date captured: 2026-09-21
Status: SCREENED / HIGH-VALUE CORRECTNESS CORPUS
Evidence class: PUBLIC SOURCE CODE + TESTS + CHANGELOG + RELEASE HISTORY
Project: TauricResearch/TradingAgents
Frozen release: v0.5.0
Frozen commit: 7fe225224431aeb3adfe1a6a23885c03fc43620a
Primary source note: ../../../08_SOURCE_MATERIAL/external_methods/2026-09-21__tauric-tradingagents-v0.5.0__source-note.md
Authority: RESEARCH_ONLY / NO_EXECUTION / NO_AUTO_PROMOTION

## Executive verdict

TradingAgents is not admitted as a strategy or execution engine.

Its highest-value contribution is a concrete failure corpus showing how agentic trading systems can silently become incorrect even when their outputs look coherent. The transfer target is therefore correctness invariants, adversarial tests and evaluation semantics, not the multi-agent "trading firm" structure.

The source is especially useful because several upstream bugs are exactly the classes that can inflate apparent historical performance:
- future/revised information in historical runs;
- future lessons in memory;
- partial holding windows settled as complete outcomes;
- source unavailability converted into negative/zero evidence;
- model-output parse failures converted into tradeable decisions.

## Source-derived facts

- v0.5.0 binds dated tool requests to the run date and expands point-in-time protection across historical paths.
- The current release includes a backtest harness over ticker x date grids using the normal decision pipeline but an isolated backtest decision log.
- The release exposes an explicit REVIEW state for unreadable decision output instead of silently converting it to HOLD.
- Historical memory is guarded by the date an outcome/lesson became knowable.
- Outcome settlement waits for the complete configured holding period.
- Data-source coverage gaps and vendor failures are represented separately from observed absence.
- The project documented and repaired a debate bug where the opening speaker could rebut an opponent response that did not yet exist.
- The project documented and repaired checkpoint reuse across incompatible graph configurations.
- The repository is Apache-2.0 licensed at capture.

## Unverified / non-admitted claims

Do not promote:
- paper headline Sharpe/return claims;
- "multi-agent is better" as a general conclusion;
- debate as a default intelligence multiplier;
- agent count as a quality measure;
- the v0.5.0 backtest as a full execution simulator;
- any claim of robust live trading alpha without independent post-correction reproduction.

## Extracted framework ideas

### A. Information-time contract

Every load-bearing datum should have enough timing metadata to answer:
- when did the underlying event occur?
- when did the source publish/file it?
- when could our system first have observed it?
- when was it retrieved?
- which historical decision is allowed to see it?

TradingAgents' repaired history reinforces our existing effective_at / observable_at / retrieved_at direction.

Disposition: ALREADY_STRONG / KEEP AS ADVERSARIAL REGRESSION SOURCE.

### B. Coverage-state contract

The following must remain different:
- observed zero;
- observed absence;
- unobserved/unavailable;
- provider failure;
- stale/partial coverage;
- not due yet.

Disposition: ALREADY_STRONG in DATA PING and Alpha Lab, but TradingAgents provides additional test cases for cross-provider fallthrough and historical-window coverage.

### C. Decision parse contract

An ambiguous or unreadable LLM output must never be mapped into a tradeable neutral action simply to keep the pipeline moving.

Proposed generic state:
VALID_ACTION | REVIEW/UNKNOWN | INVALID

No downstream layer may coerce REVIEW/UNKNOWN into BUY, HOLD or SELL without explicit governed logic.

Disposition: PARTIAL GAP / HIGH-VALUE TRANSFER CANDIDATE.

### D. Outcome-knowledge-time memory contract

A historical decision at T may only consume a learned lesson if the lesson's outcome was fully resolved and observable by T.

Required guard:
lesson_resolution_observable_at <= decision_at

Disposition: NEW/PARTIAL GAP. Repository search found strong outcome maturity machinery but no clear generic learning-memory guard expressed in this form.

### E. Full-window settlement contract

Never settle a prediction/trade outcome on partial data merely because a rerun occurred before the intended horizon completed.

Required:
- configured horizon;
- expected final observation;
- actual coverage;
- resolution timestamp;
- explicit censor/degraded state if incomplete.

Disposition: PARTIAL DUPLICATE. Existing framework has maturity/censor semantics, but this exact regression is useful to bind across future Auto Trading strategy tests.

### F. Backtest/live semantic parity

Research and later paper/live evaluation should share the same decision semantics where feasible. The backtest may have isolated state/logs, but it should not use a special easier decision interpretation.

Disposition: ALREADY A DESIGN TARGET / KEEP AS REFERENCE. Existing Auto Trading source notes already identify same-code/same-semantics parity.

### G. Backtest state isolation

Backtest memory/decision logs must be isolated from production/live/paper state.

Disposition: PARTIAL GAP / CHEAP HIGH-VALUE INVARIANT for any future stateful strategy or agent test.

### H. Portfolio-context explicitness

"No portfolio supplied" must not equal "portfolio is flat."

Represent at least:
PORTFOLIO_KNOWN | PORTFOLIO_UNKNOWN/UNSUPPLIED

Any sizing/risk evaluation requiring holdings must fail closed when portfolio context is absent.

Disposition: NEW/PARTIAL GAP, but low urgency until capital/sizing research becomes active.

### I. Adversarial independence

An adversarial pass may only rebut evidence or a thesis actually present in its input. If blind opposition is intended, independent passes commit before reveal.

Disposition: ALREADY STRONG. Astra BLIND_OPPOSITION already goes beyond the upstream repair and should remain canonical.

### J. Typed provider failure taxonomy

Provider outage, rate-limit, not-configured, malformed response, no market data and genuine empty result should be separately routable.

Disposition: PARTIAL DUPLICATE. Route generic operational lesson to #1156 rather than creating Auto Trading-specific retry logic.

## Overlap check

Existing framework components with strong overlap:
- Auto Trading GOVERNANCE.md
- #885 scientific experiment lifecycle
- #937 External Alpha standing lane
- DATA PING UNKNOWN / UNAVAILABLE semantics
- #1134 Alpha Lab data-health invariant
- Astra Point-in-Time Evidence Fabric
- Astra BLIND_OPPOSITION
- #1156 reliability/self-healing router
- backtest readiness constitution
- monotonic trial accounting / multiple-testing work

Therefore this source does not justify a new engine, swarm, memory service, backtester or execution layer.

## Testable transfer thesis

The source is valuable if its real-world failure cases identify correctness defects our current generic invariants or tests do not yet cover.

The source is not valuable merely because its architecture is popular or complex.

## Falsifier / kill condition

Kill or archive any candidate when:
- existing framework already proves the same invariant mechanically;
- the proposed addition creates a second owner;
- it only improves prose rather than machine-verifiable behavior;
- it changes market semantics rather than correctness plumbing;
- it requires importing the TradingAgents stack;
- its expected value is below maintenance/complexity cost.

## Next action

Use the companion extraction and machine-readable transfer ledger:
- ../TRADINGAGENTS_EXTRACTION_2026-09-21.md
- ../TRADINGAGENTS_TRANSFER_CANDIDATES_v1.json

Only candidates classified PARTIAL_GAP or NEW_CANDIDATE should proceed to owner-specific verification. DUPLICATE candidates are retained as regression ideas or external corroboration only.
