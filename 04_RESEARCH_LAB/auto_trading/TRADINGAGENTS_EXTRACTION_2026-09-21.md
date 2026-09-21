# TradingAgents extraction - 2026-09-21

Status: COMPLETED SOURCE EXTRACTION / TRANSFER CANDIDATES FROZEN
Source: AT-SRC-0016
Upstream snapshot: TauricResearch/TradingAgents v0.5.0 at 7fe225224431aeb3adfe1a6a23885c03fc43620a
Authority: RESEARCH_ONLY
Policy: extract mechanisms and regression cases, never copy the whole system.

## North-star question

Which TradingAgents mechanisms add incremental correctness, reproducibility or future Auto Trading value after overlap with the existing framework is removed?

## Bottom line

The repository is most valuable to us as a real-world adversarial failure corpus.

Our framework already covers several of its strongest 2026 lessons:
- point-in-time evidence and observable-at semantics;
- UNKNOWN / UNAVAILABLE rather than invented zero;
- fail-closed evidence handling;
- blind opposition with commit-before-reveal;
- immutable prospective experiment lifecycle;
- trial accounting / multiple-testing discipline;
- no parallel engine rule.

The extraction therefore rejects architecture cloning and retains only gaps or useful regression fixtures.

## Transfer matrix

| ID | Upstream mechanism / failure | Framework status | Existing owner | Disposition |
|---|---|---|---|---|
| TA-X-01 | Dated tools clamped to run date | already strong | Astra PIT evidence + #885 | DUPLICATE / REGRESSION ONLY |
| TA-X-02 | Historical fundamentals served as filed, not today's profile/revisions | partial, asset-specific | future cross-asset data contracts | ARCHIVE / DEFER |
| TA-X-03 | unavailable or unobserved window is not observed zero/absence | already strong | DATA PING + #1134 | DUPLICATE / REGRESSION ONLY |
| TA-X-04 | typed provider failure taxonomy and explicit fallback chain | partial | #1156 reliability router | PARTIAL_GAP |
| TA-X-05 | unreadable/ambiguous model decision becomes REVIEW, never silent HOLD | partial | Auto Trading lifecycle / decision outputs | PARTIAL_GAP / HIGH VALUE |
| TA-X-06 | learned memory may only use outcomes resolved and observable before decision time | no clear generic owner guard found | experiment/learning lifecycle | NEW_CANDIDATE / HIGH VALUE |
| TA-X-07 | outcome settlement waits for full configured horizon | partial | #885 lifecycle + matured outcome owners | PARTIAL_GAP / HIGH VALUE REGRESSION |
| TA-X-08 | backtest decision/memory state isolated from live/paper state | partial | backtest readiness + Auto Trading | PARTIAL_GAP |
| TA-X-09 | backtest uses same decision pipeline/semantics as normal runs | already design target | Auto Trading + backtest architecture | DUPLICATE / REFERENCE |
| TA-X-10 | missing portfolio context is not a flat portfolio | no clear generic contract found | future portfolio/sizing owner | NEW_CANDIDATE / DEFERRED |
| TA-X-11 | opening adversary cannot invent opponent argument | framework stronger | Astra BLIND_OPPOSITION | DUPLICATE / KEEP ANTI-PATTERN |
| TA-X-12 | checkpoint/resume identity binds to graph/config shape | partial | Astra/reliability execution plumbing | PARTIAL_GAP |
| TA-X-13 | failed backtest cells stay visible and do not abort/vanish | partial | immutable experiment + #1156 | PARTIAL_DUPLICATE |
| TA-X-14 | old performance claims must be re-tested after correctness fixes | not an implementation feature | #885 scientific lifecycle | REPRODUCTION ONLY |

## Detailed extraction

### TA-X-01 - run-date binding

Upstream lesson:
A model/tool caller can omit a requested date or request a later date. Point-in-time protection fails if the vendor alone is trusted to receive the correct date.

Our status:
Astra's Point-in-Time Evidence Fabric already requires effective_at, observable_at and retrieved_at, and historical use is forbidden when observable_at exceeds decision_at. #885 also required mechanical leakage tests and fail-closed timestamp semantics.

Decision:
Do not add a TradingAgents-specific date utility. Retain their historical bugs as planted-defect ideas for future regression suites.

### TA-X-02 - as-filed / vintage-aware fundamentals

Upstream lesson:
Period end is not information availability. A filing or revision may become known later. Present-day company profiles are not historical facts.

Our status:
The principle is already compatible with observable-at semantics, but this exact equity-fundamentals use case is not load-bearing for current crypto-first Auto Trading.

Decision:
Archive for later cross-asset expansion. Do not spend current engineering budget.

### TA-X-03 - coverage state is evidence

Upstream lesson:
A feed returning no rows for a historical window it never covered cannot support "nothing happened."

Our status:
This is already explicit in DATA PING and #1134. Missing/partial/implausibly empty queries remain UNKNOWN/DEGRADED and cannot enter promotion statistics as zero.

Decision:
No new owner. Keep TradingAgents examples as corroborating regression cases.

### TA-X-04 - typed provider failures

Upstream lesson:
Rate limit, not configured, vendor outage, malformed/empty response and genuine no-market-data should be distinguishable so routing can fall through safely without changing semantics.

Our status:
#1156 already distinguishes transient provider, data-contract, deterministic and unknown failures, but its taxonomy is operational rather than market-data-provider-specific.

Potential incremental value:
A compact provider-result envelope could improve routing:
status = OK | OBSERVED_EMPTY | COVERAGE_GAP | RATE_LIMIT | NOT_CONFIGURED | PROVIDER_ERROR | STALE | INVALID
plus provider identity, requested coverage and returned coverage.

Decision:
Route as a candidate enhancement to #1156, not as Auto Trading-specific retry code.

### TA-X-05 - REVIEW sentinel for ambiguous actions

Upstream lesson:
Coercing an unreadable recommendation into HOLD invents a market decision. Neutral-looking defaults are still fabricated calls.

Our status:
We fail closed in many evidence paths, but repository search did not find a generic action-output invariant equivalent to:
ambiguous/unreadable action -> REVIEW/UNKNOWN -> zero trade authority.

Proposed invariant:
1. Parse deterministic structured field first.
2. If no unique valid action exists, emit REVIEW/UNKNOWN.
3. REVIEW/UNKNOWN is not one of BUY/HOLD/SELL.
4. Any downstream conversion requires a separately governed rule and receipt.

This applies to future Auto Trading, Compass action generation, portfolio/sizing agents and any model-derived execution proposal.

Decision:
High-value candidate. Verify current action contracts before implementation to avoid duplicate semantics.

### TA-X-06 - outcome-knowledge-time memory

Upstream lesson:
A historical decision can be point-in-time clean at the raw-data layer and still cheat if its "memory" includes lessons learned from future outcomes.

Required invariant:
lesson_resolution_observable_at <= decision_at

Minimum fields for reusable learned cases:
- source decision id;
- source decision_at;
- target horizon;
- outcome_matured_at;
- outcome_observable_at;
- lesson_created_at;
- lesson version/hash.

Historical/replay callers may consume a lesson only when outcome_observable_at <= replay decision_at.

Our status:
The framework has strong maturity, frozen evidence and continuity learning machinery, but targeted search found no clear generic resolution-time memory guard expressed as an access rule.

Decision:
Highest-value new candidate from this extraction. Must be verified against current learning/continuity code before any patch.

### TA-X-07 - no premature settlement

Upstream lesson:
A rerun before the intended holding window ends must not settle on the partial return available so far.

Our status:
Maturity/censor semantics exist, but this exact failure should be a generic regression fixture wherever Auto Trading decisions later settle outcomes.

Required test:
Given horizon H and decision T, provide only a proper prefix of the expected outcome window. Settlement must remain PENDING/IMMATURE/DEGRADED, never MATURED.

Decision:
Add as a reusable regression candidate, preferably to existing lifecycle tests rather than a new module.

### TA-X-08 - state isolation between evaluation modes

Upstream lesson:
A backtest must not write to the live decision-memory path, and live memory must not contaminate historical evaluation.

Required partition key should include enough identity to prevent mode collision, at minimum:
mode + experiment/run id + candidate/version + universe + configuration fingerprint.

Decision:
Verify current backtest/experiment stores. If already proven, mark DUPLICATE. Otherwise add a cheap architecture test.

### TA-X-09 - same decision semantics

Upstream lesson:
A backtest that uses a different/easier parser, reasoning contract or action interpretation than prospective use can overstate relevance.

Our status:
This is already an explicit design target across Auto Trading source audits and execution-substrate research.

Decision:
No new implementation. Use as an acceptance question for future backtest/live substrates.

### TA-X-10 - missing portfolio is not flat portfolio

Upstream lesson:
Absence of holdings context is epistemic uncertainty, not a zero-exposure fact.

Required future states:
PORTFOLIO_KNOWN
PORTFOLIO_UNSUPPLIED
PORTFOLIO_STALE
PORTFOLIO_INVALID

Sizing/risk logic must fail closed unless its required portfolio state is known and fresh.

Decision:
Archive as a promotion prerequisite. Do not implement before portfolio/sizing becomes load-bearing.

### TA-X-11 - debate fabrication

Upstream lesson:
A first speaker must not "rebut" a position the opponent has never made.

Our status:
Astra BLIND_OPPOSITION is stronger. Independent analyses commit before reveal and disagreement is treated as data, not consensus target.

Decision:
No change. Keep upstream #1176 as an anti-pattern regression/example supporting our existing design.

### TA-X-12 - checkpoint identity

Upstream lesson:
Resuming a saved agent graph under a changed analyst roster/debate depth/asset mode can continue incompatible state.

Transfer principle:
Any resumable agent/workflow checkpoint identity must bind to the semantic configuration that determines graph/state shape.

Potential fingerprint:
code SHA + schema version + selected capabilities/roles + execution mode + key config hashes + input/frozen-evidence hash.

Decision:
Medium-value reliability candidate. Route to existing Astra/reliability plumbing only if resume/checkpoint state exists in a relevant owner.

### TA-X-13 - preserve failed cells

Upstream lesson:
A single failed cell should not erase an entire research sweep, and the failure must remain visible.

Our status:
Immutable negative evidence and #1156 already align.

Decision:
No new retry loop. Preserve failures as first-class rows and continue only when scientific semantics allow independent cells to proceed.

### TA-X-14 - performance re-reproduction

The old headline performance is not accepted as strategy evidence. Multiple later corrections touched classes capable of altering historical evaluation.

A future reproduction, if worth the research cost, must:
- use the frozen corrected release or later audited release;
- use point-in-time inputs;
- isolate evaluation state;
- report all failures and missing coverage;
- include realistic costs if the claim concerns tradable performance;
- use wider assets/time;
- include simple baselines;
- separate decision-quality scoring from portfolio/execution performance;
- freeze parameters before holdout/walk-forward.

Decision:
Low current priority. Correctness extraction has higher information value.

## Priority execution queue

### P0 - verify before patching

1. TA-X-06 outcome-knowledge-time memory guard.
2. TA-X-05 ambiguous action -> REVIEW/UNKNOWN sentinel.
3. TA-X-08 backtest/live state isolation.
4. TA-X-07 full-window settlement regression.

These are small, falsifiable and potentially cross-cutting.

### P1 - integrate only if a real gap remains

5. TA-X-04 provider failure envelope under #1156.
6. TA-X-12 checkpoint semantic fingerprint.

### Deferred

7. TA-X-10 portfolio-context explicitness, until portfolio/sizing research becomes active.
8. TA-X-02 as-filed fundamentals, until equity/cross-asset data is load-bearing.
9. TA-X-14 TradingAgents alpha reproduction, unless a future research question specifically needs it.

## Do-not-copy list

Do not import:
- the TradingAgents graph as our orchestration layer;
- permanent bull/bear/researcher agent roles;
- agent debates as a default quality mechanism;
- their memory file format;
- their vendor stack merely because it exists;
- their backtest as our execution simulator;
- their paper performance as evidence;
- their model/provider picker.

## Upstream watch policy

No scheduled daily watcher.

Revisit TradingAgents only when one of these occurs:
- a new major/minor release changes PIT, memory, backtest, decision or evaluation semantics;
- a correctness/security issue exposes a failure class not already represented in our transfer ledger;
- a future framework owner is about to implement a mechanism for which TradingAgents contains a directly relevant tested reference.

At revisit:
1. compare new tag to frozen v0.5.0;
2. inspect only relevant changed files/tests/issues;
3. append candidate delta;
4. never reopen DUPLICATE items without new evidence.

## Completion rule

This extraction is complete when:
- provenance is frozen;
- candidates are machine-readable;
- every candidate has an existing owner or DEFER disposition;
- no new engine/agent/automation is created;
- upstream source can be re-read later from exact release identity.

Companion machine-readable ledger:
TRADINGAGENTS_TRANSFER_CANDIDATES_v1.json
