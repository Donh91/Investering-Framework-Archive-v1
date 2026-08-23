# BuildWithClaude Shadow Prospective Observation Policy v1

Status: SHADOW_TESTING
Authority: RESEARCH_ONLY_NON_CANONICAL
Decision authority: NONE
Blocking authority: NONE

## Purpose

Round #1 established that the four engineering candidates can run safely in isolation. This policy defines how evidence is accumulated prospectively without converting a promising first result into production authority.

## Trigger principle

The observer runs only when the existing research-governance helper under test changes, or when manually dispatched for diagnostic purposes.

It does not run on market data, DATA PING, portfolio, signal, forecast or execution changes.

## Non-blocking rule

The prospective observer is evidence-only.

Candidate failures, mutation survivors, property violations, telemetry anomalies or guardrail warnings are recorded as research evidence. They must not automatically block or alter a pull request.

A candidate can become a blocking production control only through a separate reviewed promotion decision after sufficient prospective evidence and complexity-tax review.

## Evidence collected

### Property-based invariant testing

Track:
- generated cases,
- invariant checks,
- violations,
- runtime,
- reproducibility across real code changes.

### Mutation testing

Track:
- executed mutations,
- killed mutations,
- surviving mutations,
- kill rate,
- runtime,
- whether survivors reveal actionable coverage gaps.

### Session telemetry

Track only privacy-preserving metadata:
- duration,
- exit code,
- output byte counts,
- output hashes,
- resource usage where available.

Raw stdout/stderr is never persisted by the telemetry layer and no external telemetry backend is permitted.

### Guardrails

The shadow-round guardrail remains active around changes to the candidate infrastructure itself. Its prospective value is measured through future shadow-candidate changes, false-block rate and any unsafe mutations it prevents.

## Promotion boundary

No number of green observer runs automatically promotes a candidate.

Before `OPERATIONAL_HELPER` status, reviewers must have evidence that:

1. the candidate adds measurable value beyond existing controls,
2. the value survives multiple real changes rather than synthetic tests alone,
3. runtime and maintenance cost remain low,
4. false-positive / false-block behavior is acceptable,
5. no new data-egress or dependency risk has appeared,
6. rollback remains trivial.

Canonical market or portfolio authority is out of scope for all four candidates.

## Kill rule

Archive or retire a candidate if prospective evidence shows that it is redundant, noisy, brittle, expensive, privacy-risking or not materially better than the existing baseline after complexity tax.
