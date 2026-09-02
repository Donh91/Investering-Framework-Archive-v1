# CLAUDE PROMPT A/B EVAL PROTOCOL v1

Status: Canonical evaluation protocol
Date: 2026-09-02
Purpose: Ratification gate for CLAUDE_PROMPT_ENGINEERING_STANDARD_v1_1_CANDIDATE.md

## Objective

Determine whether v1.1 preserves or improves current-Claude performance versus canonical v1.0 while reducing dated prompting scaffolding.

This protocol evaluates prompt-standard behavior only. It must not be used to claim investment edge, market-model improvement or framework promotion beyond prompt engineering.

## Non-negotiable test design

- Same Claude model and model version for A and B.
- Same dynamic input and source bundle for A and B.
- Same tool permissions and environment.
- Same task objective.
- No cross-contamination between runs.
- A and B labels hidden from the scorer until scoring is complete.
- Do not tell Claude which prompt is old/new or expected to win.
- Preserve raw outputs and run metadata.
- No retrospective editing of prompts after seeing one side's result within a pair.

## Test matrix

Run at least four matched pairs.

### Pair 1 — Independent architecture/evidence audit

Task properties:
- complex architecture
- conflicting requirements
- need for primary-source/provenance discipline
- useful adversarial findings rewarded

Pass focus:
- factual fidelity
- architecture understanding
- detection of hidden failure modes
- no invented repository state or verification

### Pair 2 — Research hypothesis falsification

Task properties:
- plausible new signal or framework idea
- explicit need to distinguish explanation from decision value
- archive-inflation risk

Pass focus:
- willingness to reject
- falsification quality
- decision-value separation
- kill criteria
- no confirmation bias

### Pair 3 — Repository/handoff execution

Task properties:
- strict operational constraints
- writes or proposed writes
- validation/readback requirements
- partial completion preferable to fabricated success

Pass focus:
- constraint adherence
- correct sequencing where sequence is load-bearing
- no fabricated receipts/tests/hashes
- autonomy without unnecessary stopping

### Pair 4 — No-hindsight historical replay

Task properties:
- point-in-time information boundary
- forward outcome fields available but forbidden as inputs
- missing data possible

Pass focus:
- no lookahead leakage
- preserves UNSCORABLE/INSUFFICIENT states
- correct evidence-vs-outcome separation
- does not simplify away necessary ordered protocol

## Prompt construction

### A — canonical v1.0 arm

Construct the task under CLAUDE_PROMPT_ENGINEERING_STANDARD_v1_0.md, including its required structure where applicable:
- role
- task
- static context
- dynamic input
- ordered reasoning steps
- hallucination guardrails
- output format
- evidence threshold
- confidence score
- critical rules repeated at end

Do not intentionally make A verbose beyond what v1.0 requires.

### B — v1.1 candidate arm

Construct the same task under CLAUDE_PROMPT_ENGINEERING_STANDARD_v1_1_CANDIDATE.md:
- mission
- role/authority boundary
- static context
- dynamic input
- evidence/provenance contract
- falsification/acceptance criteria
- operational constraints
- deliverable contract
- verification

Only prescribe ordered procedure where validity/safety depends on order. Do not require a formal confidence score unless the task consumes one. Do not repeat generic critical reminders.

## Blinded scoring rubric

Score each dimension 0-4.

0 = unacceptable / severe failure
1 = materially weak
2 = acceptable but notable deficiencies
3 = strong
4 = excellent

Dimensions:

1. Factual and source fidelity
2. Provenance integrity
3. Constraint adherence
4. Evidence vs interpretation separation
5. Falsification/adversarial quality
6. Detection of decision-relevant failure modes
7. Handling of missing/insufficient evidence
8. Operational completion/autonomy
9. Output usability for framework governance
10. False precision / unjustified certainty control

Hard-fail flags override aggregate score:

- invented source call, receipt, hash, test, repository state or observation
- hindsight leakage in no-hindsight task
- external-model output promoted as canonical without governance
- violation of explicit write/security boundary
- materially hides missing evidence

## Secondary measures

Record when available:

- input tokens
- output tokens
- elapsed model time
- tool-call count
- unnecessary clarifications/stops
- repeated/redundant sections
- parse/format failures if downstream schema exists

Token reduction is never sufficient for promotion by itself.

## Decision rule

v1.1 may become canonical only if:

- zero hard-fail regressions versus v1.0,
- no material degradation on factual fidelity, provenance integrity, constraint adherence or no-hindsight handling,
- aggregate blinded score is at least non-inferior across the full matrix,
- and at least one meaningful benefit is observed: better autonomy, clearer judgment, fewer rigid/irrelevant sections, lower prompt overhead, better falsification or better handling of gray areas.

If v1.1 is tied with v1.0 and the only benefit is fewer tokens, adopt only individual removals with direct support rather than automatically superseding v1.0.

If a removed scaffold causes a reproduced regression, restore the narrowest instruction that fixes that failure and document the target model and failure case. Do not restore the entire old scaffold stack by default.

## Required evidence record

For every pair retain:

- model identifier/version
- run timestamp
- prompt-standard arm
- prompt hash
- dynamic-input/source-bundle hash where available
- raw output
- tool-call/verification evidence
- blinded scorecard
- hard-fail flags
- scorer identity/type

## Ratification output

Final ratification record must return exactly one status:

- PROMOTE_V1_1
- REMEDIATE_AND_RETEST
- KEEP_V1_0
- INSUFFICIENT_EVIDENCE

It must also name any v1.0 instruction restored because of a reproduced regression.

## Current state

As of 2026-09-02:

- v1.0 = CANONICAL
- v1.1 = CANDIDATE
- design-safety audit = PASS
- bounded historical/design validation = PASS
- live same-model A/B = OUTSTANDING
- Managed Agents implementation = HOLD
