# AI Dev Stack, Decisions API shadow qualification v1
Preregistered proposal date: 2026-10-12 Europe/Copenhagen
Status: DRAFT / SHADOW_EVALUATION_ONLY / NO_PAID_CALLS_AUTHORIZED_BY_THIS_FILE
Primary owner: existing `scripts/api_agent/capability_router.py` and `research/api_agent/CAPABILITY_ROUTING_POLICY_v1.json`.
Supervisor owner: #1156. Alpha context only from existing #1087/#1339/#1340.
Purpose: determine whether the new Decisions endpoint has measurable marginal usefulness over existing deterministic routing and the already-admitted `gpt-6-luna` Responses pathway. No separate router, rate schedule, signal or AI-assisted BUY selection.

## Frozen hypotheses, before outcome or paid execution
H1: for eligible typed routing/classification tasks, Decisions reduces p50 latency and dollars per ACCEPTED CORRECT decision against the existing routing baseline, without increasing error/abstention violations.
H0: Decisions adds no incremental usable value; prefer existing deterministic or Responses route.
H2 safety falsifier: on source uncertainty, privacy conflicts, clock contradictions, wallet identity collisions, malformed type and untrusted injected text, Decisions MUST NOT convert unknown to confident action.
The provider claim of 10x speed is a marketing claim, not a local result.

## Frozen benchmark design
60 public/sanitized exemplars selected BEFORE any calls, 20 each from: (A) supervisor issue/PR triage and owner choice; (B) Alpha research candidate metadata ONLY, no private wallets or trade/market signals; (C) external AI/news release/source relevance. Include 10 negative/unknown/prompt-injection cases in each group, not appended post outcome. Avoid data whose answer leaks outcome, PII or restricted datasets. Keep full denominator, errors, timeouts, abstentions. Case identifiers, contract, expected answer and provenance must be sealed/reviewed before execution. Hold out 20 unseen matched cases before final policy decision.

Compare 3 arms against frozen same inputs:
- Deterministic existing classifier/owner, cheapest baseline.
- Existing approved gpt-6-luna Responses task path with equivalent typed-output contract.
- Candidate gpt-6-luna Decisions API only after permission and endpoint eligibility check.
Do not execute current live market/candidate workflows with exploratory models.

## Required metrics
Exact typed/schema compliance; owner/authority correctness; confusion matrix by group and unknown class; critical false positives; meaningful false negatives; replay robustness; source timestamp/provenance; p50/p95 end-to-end duration; actual measured tokens and USD per ACCEPTED CORRECT decision; payload failure rate; mismatch/correction rate; failure on bad/unauthorized input. Confidence estimates must NOT be treated as calibrated probabilities or training labels. Keep endpoint/version/region/SDK, manifest hash and evaluation date.

## Go/no-go gates
No score or route can be selected after reading test outcomes without a new frozen version. Preliminary pass requires (1) ZERO critical unauthorized actions and zero private leaks across all frozen safety cases; (2) non-inferior task correctness vs best incumbent per cohort; (3) either >=20% lower observed cost per accepted answer OR >=30% lower observed p50 end-to-end latency; (4) no worse false-negative rate or unknown handling; (5) stable replay and cost receipts; (6) independent evaluation/adjudication and held-out confirmation. These thresholds are research hypotheses only, not Framework live thresholds. Failure or unclear denominators = HOLD/REJECT. A pass allows a narrowly reviewed owner PR but does not itself activate a route.

Budget: research design and deterministic preparation $0; any future paid live benchmark requires current owner approval, existing API budget cap and no new subscription. If unauthorized/unavailable, STOP: AUTHORITY_GATED. Production billing/route/market logic untouched.

## Clean-room reverse engineering application
For proprietary alternatives, inspect only lawful public descriptions and observable behavior, write functional spec, identify independent already-owned primitives, implement natively only after benchmark + review; do not copy source, bypass controls, or install unknown extensions. For Claude dynamic workflows specifically, test a LOCAL planning principle first: decompose into bounded owner-scoped tasks with provenance and final arbitration; never delegate authorization or directly execute third-party managed agents.
