# Port architecture prior - extraction and admission plan v1

Date: 2026-09-23
Status: RESEARCH PRIOR / ADMISSION PLAN
Authority: research only
External prior: Port
Canonical source of truth remains GitHub. Port is not admitted as a framework owner, market source, execution authority or second truth plane.

## Decision

Do not adopt Port as a platform dependency now.

Extract and test four design ideas against capabilities already present in the Investering framework:

1. relational context graph/lake;
2. agent invocation ledger;
3. agent/skill/tool registry with empirical outcome feedback;
4. context-aware execution with minimal verified task packets.

The framework already contains partial implementations of all four. Therefore the correct experiment is incremental-value extraction, not platform migration.

## Fresh-framework overlap

### Existing capability A - context-aware execution
The existing canonical-context-router already resolves current repository authority and returns a small verified context packet before downstream reasoning.

Admission question: Can the context packet become more relational and task-selective without creating a second truth plane or omitting critical evidence?

### Existing capability B - invocation receipts
API_AGENT_AND_COMPOUNDING_LEARNING_ARCHITECTURE_v1 already requires immutable API receipts with task, model, reasoning effort, prompt version, input hashes, output hash, token usage and estimated cost.

Admission question: Can those receipts be extended or joined to prospective downstream information contribution and outcome, rather than merely execution accounting?

### Existing capability C - capability/skill routing
The framework already has SKILL_REGISTRY.md, SKILL_ROUTING_INDEX.json, CAPABILITY_ROUTING_POLICY_v1.json, agent metadata and task registries.

Admission question: Can routing learn from observed task outcomes and information gain without allowing self-promotion, hindsight leakage or uncontrolled policy mutation?

### Existing capability D - canonical relations
The repository already models owners, authority, cross-repo context, experiments, evidence, outcomes and execution state, but relations are distributed across files.

Admission question: Can a derived machine-readable relation index reduce retrieval cost and missed context while GitHub files remain canonical?

## External-prior extraction

Port's current architecture is useful as prior art because it treats persistent context as entities/relations, AI agents and invocations as catalog objects, MCP servers/workflows as governed resources, and separates persisted integrations from runtime MCP access.

We adopt none of those claims as proof that the same design improves this framework. They generate challenger hypotheses only.

## Four bounded challengers

### P1 - Derived Context Graph
Build only as a derived read model from canonical GitHub.

Candidate entity classes:
OWNER, TASK, EXPERIMENT, HYPOTHESIS, SOURCE, OBSERVATION, PROJECT, CA, WALLET, AGENT, MODEL, SKILL, TOOL, INVOCATION, RECEIPT, OUTCOME, INCIDENT, PR.

Candidate relation examples:
TASK -> OWNED_BY -> OWNER
TASK -> USES -> SKILL
INVOCATION -> EXECUTES -> TASK
INVOCATION -> USES -> MODEL
INVOCATION -> CONSUMES -> SOURCE/CONTEXT_PACKET
OBSERVATION -> SUPPORTS/CONTRADICTS -> HYPOTHESIS
PROJECT -> BINDS_TO -> CA
OUTCOME -> EVALUATES -> OBSERVATION/EXPERIMENT
INCIDENT -> AFFECTS -> WORKFLOW/OWNER

Hard rule: graph is rebuildable and disposable. It never outranks source files.

Success:
- lower context-retrieval cost/latency;
- fewer wrong-owner/stale-context errors;
- no critical omission increase;
- deterministic lineage back to canonical files.

Kill:
- second truth plane emerges;
- relation drift cannot be reproduced;
- material evidence is lost through graph compression;
- maintenance cost exceeds measured retrieval value.

### P2 - Agent Invocation Contribution Ledger
Extend existing receipt semantics conceptually from execution accounting to contribution accounting.

Minimum joinable fields:
invocation_id, task_id, owner, model/agent/tool/skill, reasoning_effort, prompt/input hashes, canonical context hash, started_at/completed_at, token usage, estimated cost, latency, new evidence count, duplicate/no-op count, uncertainty resolved, decision/route changed, prospective freeze ids, downstream outcome ids, information_contribution_state, post-outcome contribution adjudication.

Contribution states must not be a single subjective score initially:
NO_NEW_INFORMATION
DUPLICATE_CONFIRMATION
CONFLICT_DETECTED
IDENTITY_RESOLVED
PROVENANCE_RESOLVED
CANDIDATE_REJECTED_USEFULLY
CANDIDATE_ESCALATED
FALSE_NEGATIVE_DISCOVERED
PROSPECTIVE_SIGNAL_CONTRIBUTION
UNKNOWN

No model receives credit merely because a later outcome was positive.

Success: demonstrate which intelligence classes add incremental prospective information over cheaper champion routing.

Kill:
- cannot separate model contribution from upstream data;
- credit becomes hindsight winner attribution;
- logging cost exceeds decision value.

### P3 - Empirical Capability Registry
Do not create another registry. Join existing skill/model/tool/task registries to P2 receipts and outcomes.

The registry may learn evidence such as:
- task family where deterministic path is sufficient;
- task family where Luna adds useful semantic triage;
- task family where Sol resolves material conflicts;
- skill that repeatedly prevents stale-context errors;
- tool that adds cost without incremental evidence.

No automatic self-promotion initially.

Promotion/routing changes require prospective evidence, sufficient denominator, regression check, authority boundary and rollback.

Success: better routing quality at equal/lower cost without higher critical error or false-negative burden.

### P4 - Context Packet A/B
Champion: current canonical-context-router packet.
Challenger: task-specific relational packet derived from P1.

Compare:
tokens supplied, retrieval/tool calls, latency, authority correctness, critical evidence retention, stale-context errors, manual correction burden and downstream task quality.

No long-context reduction is accepted if it increases critical omissions.

Success: materially smaller/faster context with equal or better correctness.

## Alpha Lab first proving ground

Alpha Lab is the preferred first domain because it already has prospective evidence discipline, exact timestamps, negative denominator, false-positive/false-negative accounting, model/API cost receipts, selective intelligence escalation north-star, Project->CA and Phoenix experiments.

First experiment: compare deterministic/API champion vs selectively escalated intelligence and log P2 contribution states.

The important question is not whether AI touches a winner. It is whether AI added information before outcome that the cheaper champion did not possess.

## Sequencing

Stage 0 - this research prior. No runtime change.
Stage 1 - map existing fields to P1-P4 and identify missing joins. Prefer schema/research work, not code.
Stage 2 - P2 contribution ledger shadow schema, reusing existing receipt IDs.
Stage 3 - P4 context-packet A/B on bounded non-market-authority tasks.
Stage 4 - P3 empirical routing readout, no automatic policy mutation.
Stage 5 - only if P2/P4 show value, consider P1 derived graph implementation.
Stage 6 - only after internal evidence, optionally benchmark Port itself in an isolated sandbox. Never connect it as canonical authority by default.

This ordering deliberately tests the highest-value/lowest-complexity ideas first. A full context graph is deferred until contribution logging and context A/B demonstrate that the missing relation layer is a real bottleneck.

## Cost doctrine

The experiment follows the Alpha Lab adaptive-intelligence north-star:
- no-change should trend toward zero model calls;
- cheap deterministic/cached context first;
- escalate intelligence when expected information gain is material;
- cost savings never justify critical context omission;
- measure value per useful contribution, not tokens alone.

## Anti-degradation

Forbidden:
- new parallel owner;
- Port as canonical truth;
- opaque global agent score;
- autonomous model/skill self-promotion;
- outcome-aware context construction;
- deletion of negative/no-op invocations;
- missing fields coerced to zero;
- compression without provenance;
- using Port marketing claims as framework evidence.

## Immediate recommendation

Proceed with Stage 1 and Stage 2 as the next bounded research work. Do not install Port and do not build a full Context Lake yet.

The near-term highest expected value is P2 Agent Invocation Contribution Ledger plus P4 Context Packet A/B, because the framework already has the necessary receipts, routing policy and canonical-context-router. These can directly test the adaptive intelligence north-star without a new platform dependency.
