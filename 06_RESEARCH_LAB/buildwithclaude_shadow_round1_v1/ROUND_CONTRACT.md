# BuildWithClaude Shadow Admission Round #1

Status: SHADOW_TESTING INFRASTRUCTURE ONLY
Authority: RESEARCH_ONLY_NON_CANONICAL
Canonical effect: false
Portfolio execution: false
Paid data authorized: false
External provider calls authorized: false

## Purpose

Evaluate four agent-engineering candidates discovered through BuildWithClaude against the existing framework baseline without granting any candidate authority over market semantics, portfolio semantics, thresholds, weights, prospective floors, outcome labels, live data collection or canonical outputs.

The four candidates are:

1. Property-based invariant testing
2. Mutation testing for critical research-governance contracts
3. Session telemetry / execution observability
4. Minimal pre/post-flight guardrails

These candidates are test instruments around the machine. They are not market sensors, models, trading agents or decision engines.

## Prime rule

Observe -> accumulate evidence -> validate -> learn -> adjust only when the evidence warrants it.

Every candidate remains a SHADOW_CANDIDATE until measured evidence justifies a reviewed status change.

## Baseline

The baseline is the current framework without these four candidates. Existing CI, research governance, data architecture, storage health, prospective evidence and canonical market/portfolio semantics remain unchanged.

## Protected surfaces

This round must not modify or mutate:

- `01_CORE_FRAMEWORK/**`
- `02_DATA_PING/**`
- live runtime/state files outside this round
- canonical thresholds, weights or signal definitions
- prospective eligibility floors
- forecast/outcome labels
- portfolio or execution semantics
- source credentials or restricted data-plane content
- scheduled production workflows

The round may only add:

- this isolated research package,
- `scripts/research/shadow_*` candidate probes,
- a dedicated validation script,
- one dedicated PR/manual shadow workflow,
- the Shadow Idea Admission governance files rebased from PR #531.

## Candidate promotion boundary

No candidate may automatically promote itself.

Possible next classifications after evidence review:

- ARCHIVE_ONLY
- SHADOW_TESTING
- OPERATIONAL_HELPER
- RETIRED

A move to CANONICAL_CANDIDATE or CANONICAL requires a separate reviewed change path and fresh evidence. None of the four candidates can gain market-decision authority through this round.

## Complexity tax

Each candidate is evaluated on:

- incremental defect/risk detection,
- overlap with existing controls,
- runtime overhead,
- maintenance burden,
- external dependencies,
- API/token cost,
- latency,
- security/privacy surface,
- false-positive / false-block risk,
- correlated failure risk,
- rollback simplicity.

If measurable benefit does not exceed the complexity tax, archive or retire the candidate.

## Candidate-specific preregistration

### 1. Property-based invariant testing

Problem: conventional example tests may miss edge cases in research-governance helper logic.

Success criteria:

- dependency-free deterministic fuzz run with >= 1,000 generated cases,
- zero violations of preregistered invariants on the current baseline,
- exercises at least six independent invariants,
- completes without repository writes,
- runtime remains suitable for PR validation.

Failure / kill criteria:

- flaky/non-reproducible failures,
- material runtime burden,
- tests merely restate existing example tests without new coverage,
- requires external services or market data.

Promotion evidence:

Repeated stable runs plus either discovery of a real defect or demonstrated protection against mutations that existing validation would miss.

### 2. Mutation testing

Problem: green tests do not prove that the test suite would detect small but dangerous logic changes.

Success criteria:

- mutate temporary copies only, never repository source,
- preregistered mutation set targets governance-critical invariants,
- kill rate >= 80% is sufficient to continue shadow testing,
- no source-tree writes or dependency installation.

Failure / kill criteria:

- mutations touch real source,
- mutation result is not reproducible,
- low kill rate persists without actionable coverage insight,
- runtime cost exceeds likely quality benefit.

Promotion evidence:

Stable high kill rate and evidence that mutation testing exposes a coverage gap or protects a critical contract at acceptable cost.

### 3. Session telemetry / execution observability

Problem: complexity tax currently contains operational costs that are partly qualitative rather than measured.

Success criteria:

- records duration, exit code, output byte counts, hashes and resource usage,
- never persists raw stdout/stderr,
- detects non-zero exit codes correctly,
- no external telemetry backend,
- low execution overhead,
- stable machine-readable schema.

Failure / kill criteria:

- secret/data leakage risk,
- raw output persistence,
- unstable schema,
- material runtime overhead,
- duplicates existing telemetry without incremental value.

Promotion evidence:

Useful cost/failure measurements across multiple research jobs that improve complexity-tax decisions.

### 4. Minimal pre/post-flight guardrails

Problem: CI can detect some violations after a change, but a shadow research helper should also prove it stayed inside its permitted surface.

Success criteria:

- synthetic protected-path mutation is blocked 100%,
- allowed shadow paths pass 100%,
- post-flight detects dirty working-tree state,
- candidate scripts leave repository clean,
- no production workflow or market-state mutation.

Failure / kill criteria:

- false blocks on legitimate shadow work,
- missed protected-path violations,
- reliance on brittle path assumptions without review,
- material maintenance burden.

Promotion evidence:

Repeated zero-false-positive operation plus demonstrated ability to block a real or synthetic unsafe change.

## Round verdict rule

The round itself may merge only if the harness is safe, reproducible, read-only with respect to canonical/runtime state and all ordinary repository gates remain green.

Candidate quality results do not automatically become policy. They become evidence rows for a later promotion or retirement decision.
