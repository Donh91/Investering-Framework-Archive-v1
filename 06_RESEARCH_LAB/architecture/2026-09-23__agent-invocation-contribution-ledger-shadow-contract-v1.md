# Port extraction Stage 1 + Stage 2 - contribution ledger shadow contract v1

Date: 2026-09-23
Status: SHADOW_CONTRACT_READY_FOR_OBSERVATION
Authority: research/meta-learning only
Parent: 2026-09-23__port-architecture-prior-extraction-and-admission-plan-v1.md
Primary owner: API_AGENT_AND_COMPOUNDING_LEARNING_ARCHITECTURE_v1
Canonical truth: existing source files and receipts. This contract is additive metadata only.

## Stage 1 - existing-capability map

Fresh main shows that the framework does not need a new invocation system.

Existing API receipts already capture execution-accounting primitives including task/model, reasoning configuration, prompt/input/output hashes, token usage and estimated cost. Existing daily machine-throughput code already aggregates model calls, tokens and recorded API cost. Existing canonical-context-router already returns a bounded verified context packet. Existing skill/capability registries already own routing metadata.

Therefore the missing capability is a JOIN between:
1. execution receipt;
2. context packet;
3. prospective evidence created or changed;
4. later outcome/adjudication.

The join must remain optional and fail-closed. A missing join is UNKNOWN, never zero contribution.

## Stage 2 - Agent Invocation Contribution Ledger shadow schema

This is a shadow sidecar. Do not mutate legacy receipts yet.

### Identity
- contribution_receipt_version: AICL_SHADOW_v1
- invocation_id: stable existing receipt/run identifier when available, otherwise UNKNOWN
- task_id
- owner
- observed_at_utc
- execution_receipt_ref
- context_packet_ref
- context_packet_hash
- input_hashes[]
- output_hash
- model
- agent
- tools[]
- skills[]
- reasoning_effort
- token_usage_input
- token_usage_output
- estimated_cost_usd
- latency_ms

### Pre-outcome contribution
Frozen before economic/downstream outcome where predictive credit is possible:
- contribution_state[]
- new_evidence_refs[]
- duplicate_evidence_refs[]
- conflict_refs[]
- uncertainty_before[]
- uncertainty_after[]
- route_before
- route_after
- route_changed: true/false/UNKNOWN
- prospective_freeze_refs[]
- candidate_ids[]
- no_op_reason
- source_health_refs[]
- omissions[]

Allowed contribution_state values:
- NO_NEW_INFORMATION
- DUPLICATE_CONFIRMATION
- CONFLICT_DETECTED
- IDENTITY_RESOLVED
- PROVENANCE_RESOLVED
- SOURCE_HEALTH_FAILURE_DETECTED
- CANDIDATE_REJECTED_USEFULLY
- CANDIDATE_ESCALATED
- FALSE_NEGATIVE_DISCOVERED
- PROSPECTIVE_SIGNAL_CONTRIBUTION
- CONTEXT_OMISSION_PREVENTED
- UNKNOWN

These are categorical evidence labels, not a model score.

### Post-outcome join
Written only after the canonical outcome owner has settled:
- outcome_refs[]
- adjudicated_at_utc
- contribution_adjudication
- counterfactual_champion_state
- incremental_information_confirmed: true/false/UNKNOWN
- timing_advantage_seconds: number/UNKNOWN
- critical_error: true/false/UNKNOWN
- notes

Allowed contribution_adjudication:
- USEFUL_INCREMENTAL
- USEFUL_REJECTION
- USEFUL_CONFLICT_DETECTION
- REDUNDANT
- NO_MEASURABLE_VALUE
- HARMFUL
- UNRESOLVED
- NOT_OUTCOME_ELIGIBLE

## Credit rules

1. Positive market outcome never grants contribution credit by itself.
2. The contribution must be timestamped before the relevant outcome.
3. The cheaper champion state must be reconstructable from frozen evidence.
4. Model prose is not evidence truth.
5. Identity, provenance, on-chain and source-health truth remain owned by their canonical deterministic/source owners.
6. UNKNOWN remains UNKNOWN.
7. No-op and redundant invocations remain in the denominator.
8. Useful rejection can be valuable even when no market outcome exists.
9. A false negative found after outcome can improve learning but cannot receive prospective signal credit.
10. Cost efficiency is evaluated only after evidence quality and safety.

## Alpha Lab first observation profile

For selective intelligence escalation, freeze:
- deterministic_champion_evidence_refs
- deterministic_champion_route
- escalation_trigger
- intelligence_new_evidence_refs
- intelligence_conflicts_resolved
- intelligence_route_delta
- first_seen_before_broad_propagation: true/false/UNKNOWN
- exact_ca_binding_delta
- provenance_delta
- sellability_delta
- source_health_delta
- qualified_watch_delta
- cost/latency

This directly tests the north-star question: did intelligence add prospectively available information that the cheaper champion did not possess?

## Context Packet A/B preregistration

Champion A:
current canonical-context-router behavior.

Challenger B:
same task plus a derived relation manifest limited to canonical refs required by the task.

Both arms must use the same task and frozen repository state.

Measure:
- context input tokens/bytes
- retrieval calls
- latency
- owner/authority correctness
- required canonical refs retained
- critical omissions
- stale refs
- unsupported inference
- manual correction burden
- downstream result equivalence or improvement

Hard fail:
- any authority regression;
- any critical canonical omission;
- UNKNOWN converted to fact/zero;
- challenger uses outcome knowledge unavailable to champion;
- derived relation cannot resolve back to canonical source.

Promotion gate:
No automatic promotion. Require a prospective bounded sample across multiple task families and no critical regressions. Sample size is intentionally not invented here; it must be set by experiment governance before outcome inspection.

## Minimum viable observation, no code required

Until runtime sidecar code exists, an existing agent or research pass may append schema-complete shadow observations as research artifacts provided:
- execution receipt references are real;
- timestamps are preserved;
- pre-outcome fields are frozen before outcomes where applicable;
- missing data are UNKNOWN;
- no legacy receipt is rewritten;
- no routing policy changes are made.

This lets evidence collection begin without waiting for a large implementation.

## Implementation residue

Code is justified only for:
1. deterministic sidecar generation from existing receipts;
2. deterministic joining of known context packet refs/hashes;
3. schema validation;
4. outcome join after canonical settlement;
5. aggregate readout by task/model/contribution state.

No code is justified for:
- global AI scoring;
- autonomous model promotion;
- inferred market truth;
- automatic budget increases;
- second context store;
- rewriting legacy receipts.

## Kill criteria

Kill or narrow if:
- attribution cannot separate upstream data value from model value;
- shadow logging materially increases operational burden;
- context A/B produces critical omissions;
- contribution labels drift into subjective winner credit;
- no routing-relevant incremental information appears after a sufficient prospective sample;
- the sidecar becomes a second truth plane.

## Next gate

Begin shadow observations on the next eligible Alpha Lab intelligence escalations and bounded context-router tasks.

Only after real rows exist should implementation be expanded or capability routing consume the ledger.
