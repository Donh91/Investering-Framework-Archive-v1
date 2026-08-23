# BuildWithClaude Shadow Prospective Observation Policy v1

Status: SHADOW_TESTING
Authority: RESEARCH_ONLY_NON_CANONICAL
Decision authority: OPENAI_API_AUTONOMOUS_LIFECYCLE_DECIDER
Blocking authority: NONE

## Purpose

Round #1 established that the four engineering candidates can run safely in isolation. This policy defines how evidence is accumulated prospectively and how the designated OpenAI API lifecycle decider may autonomously promote, retain, archive or retire candidates without owner confirmation.

## Trigger principle

The observer runs when the existing research-governance helper under test changes, or when manually dispatched for diagnostic purposes.

It does not run on market data, DATA PING, portfolio, signal, forecast or execution changes.

## Non-blocking observation rule

The prospective observer remains evidence-only.

Candidate failures, mutation survivors, property violations, telemetry anomalies or guardrail warnings are recorded as research evidence. They do not themselves block or alter a pull request.

Blocking production authority is a separate capability from lifecycle status. Promotion to `OPERATIONAL_HELPER` does not automatically convert a candidate into a merge-blocking gate.

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

## Autonomous lifecycle decision

No number of green observer runs automatically promotes a candidate by deterministic rule.

Instead, the designated OpenAI API lifecycle decider reviews the frozen candidate contract, prospective evidence, incremental-value evidence, complexity tax, failures and rollback path, then makes the substantive lifecycle decision.

Allowed decisions for this round are:

- `PROMOTE_OPERATIONAL_HELPER`,
- `KEEP_SHADOW`,
- `ARCHIVE_ONLY`,
- `RETIRED`.

The four Round #1 candidates have no market or portfolio authority ceiling. The lifecycle decider therefore cannot use this round to create canonical market logic, change thresholds or gain execution authority.

A deterministic validator may reject malformed output, unknown candidate IDs, missing evidence binding or an attempted authority escalation. It may not replace the AI's substantive judgment with its own PASS/FAIL opinion.

## Promotion evidence question

Before `OPERATIONAL_HELPER` status, the AI must determine whether the evidence supports all of the following in substance:

1. the candidate adds measurable value beyond existing controls,
2. the value survives multiple real changes rather than synthetic tests alone where the candidate contract requires real-change evidence,
3. runtime and maintenance cost remain acceptable,
4. false-positive or false-block behavior is acceptable,
5. no new data-egress or dependency risk has appeared,
6. rollback remains bounded and credible.

If the evidence is insufficient or ambiguous, the correct autonomous decision is `KEEP_SHADOW`.

## Owner interaction

Owner approval is not part of the normal promotion path. Master Monday reports the AI decision, evidence sufficiency, complexity tax, implementation status and rollback path after the decision.

The owner may still manually override framework governance if explicitly desired, but absence of owner confirmation does not block a valid AI lifecycle decision.

## Kill rule

The AI should select `ARCHIVE_ONLY` or `RETIRED` when prospective evidence shows that a candidate is redundant, noisy, brittle, expensive, privacy-risking or not materially better than the existing baseline after complexity tax.
