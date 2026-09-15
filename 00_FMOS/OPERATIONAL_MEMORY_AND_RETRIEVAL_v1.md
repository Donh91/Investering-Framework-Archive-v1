# Operational Memory & Retrieval v1

Status: SHADOW-ONLY FRAMEWORK LEARNING EXTENSION  
Owner: Framework Learning Supervisor  
Canonical market authority: NONE  
Scientific authority: NONE  
Portfolio authority: NONE

## Purpose

Reduce repeated framework investigation, unnecessary context rebuilding and rediscovery of prior fixes by deriving compact operational memory from verified GitHub history.

This is not a new orchestrator, semantic-memory owner or source of truth. Current GitHub `main` remains authoritative. Operational memory is a provenance-linked acceleration layer only.

## Ownership boundary

- Existing market/research owners continue to own source evidence and canonical state.
- Unified Adjudication continues to own interpretation of mature experiment evidence.
- Compounding Learning continues to own semantic-family learning and next-best-test proposals.
- Framework Learning Supervisor owns this operational-memory extension.
- Existing skills/governance remain the only procedural-skill authority.

## V1 products

- immutable `OPERATIONAL_EPISODE_v1` files derived from accepted `main` commits;
- `LATEST_OPERATIONAL_MEMORY_INDEX.json` with current-main compatibility;
- `LATEST_PROCEDURAL_CANDIDATES.json`, candidate-only repeated operational patterns;
- `LATEST_OPERATIONAL_MEMORY_HEALTH.json`;
- `LATEST_OPERATIONAL_MEMORY_POST_PRODUCTION_AUDIT.json` and `.md`;
- deterministic `OPERATIONAL_MEMORY_PREFLIGHT_v1` for task bootstrap.

## Episode semantics

An episode may store source commit/timestamp, task class, operation type, compact task/resolution summary, changed paths, source blob SHAs and a bounded failure signature for fixes/hardening.

An episode MUST NOT store chain-of-thought, full prompts, secrets or inferred failed approaches. A merged commit proves an accepted repository change, not causal effectiveness.

Episodes are append-only. Compatibility and retrieval status are recomputed in the derived index.

## Retrieval

V1 retrieval is deterministic-first:
1. task-class match;
2. exact/path-prefix overlap;
3. task/failure-signature token overlap;
4. current-main blob compatibility;
5. related newer work.

No embeddings, vector database, external memory service or model call is required. Preflight is acceleration context only. Consumers must re-read current authoritative files before acting.

## Staleness

Every episode binds relevant source blob SHAs. Retrieval compares them with current `HEAD`.

States are `EXACT`, `PARTIAL`, `DRIFTED`, `REMOVED` and `UNKNOWN`. `DRIFTED` and `REMOVED` memories require revalidation and cannot be treated as reusable instructions.

A newer related episode is a relation, not automatic supersession. Supersession requires explicit authoritative evidence.

## Procedural candidates

Repeated accepted work may create a `CANDIDATE_ONLY` procedural pattern after at least three independent commits in the same task/action/path family.

V1 never auto-activates or auto-promotes a skill. Promotion requires governed skill review with clear trigger, preconditions, steps, success criteria, failure modes, versioning and rollback/revalidation semantics.

## Autonomous post-production audit

Every production Supervisor run audits the just-built Operational Memory before it is committed back to `main`.

The audit verifies contract consistency, current-HEAD binding, authority firewalls, stale-memory quarantine, procedural-candidate safety and bounded deterministic retrieval probes. It also records the episode count, compatibility distribution, candidate count, stale share and a shadow retrieval-quality baseline.

Audit states are:
- `PASS`: continue shadow operation autonomously;
- `WARN`: continue shadow operation and accumulate evidence, with no user action required;
- `FAIL`: block Operational Memory reuse for that run, fail the workflow before unhealthy memory products are committed, and automatically open or update one deduplicated GitHub issue containing the failure evidence and workflow run URL.

When a later run recovers from `FAIL`, the same workflow automatically comments on and closes the escalation issue. Routine `PASS` and `WARN` runs create no issue.

The audit itself has no canonical, scientific, model, skill-promotion or portfolio authority.

## Zero-touch FAIL remediation routing

A production audit `FAIL` is also converted automatically into one bounded `CODEX_RESEARCH_CANDIDATE_v1` under `research/codex/intake/YYYY/MM/`.

The failure set is deterministically fingerprinted. Only one uncompleted candidate may exist per failure fingerprint. A recurrence may be created only after the prior matching candidate has a completion receipt. This prevents repeated Supervisor runs from flooding the Codex queue with duplicates.

The generated candidate is restricted to the Operational Memory/Supervisor implementation and tests, requires positive and negative acceptance tests, preserves the existing forbidden-change boundary, and has `CODE_REMEDIATION_ONLY` authority. It cannot authorize market gates, model weights, canonical authority, portfolio logic, API budget or new policy semantics, and it cannot auto-merge.

After the intake is safely committed to `main`, the Supervisor explicitly dispatches the existing `remediation-maturation.yml` workflow. This explicit dispatch is required because a normal push made with GitHub's workflow token is not relied upon to start a second workflow. The existing remediation owner therefore remains the only maturation/queue owner; no parallel repair supervisor is introduced.

GitHub-native automation covers detection, quarantine, incident lifecycle, bounded intake creation, deduplication, remediation maturation dispatch and Codex-ready queueing. The repository does not currently contain a GitHub Actions workflow that itself executes Codex code changes, so this contract does not falsely claim GitHub-native AI code execution. Any external Codex executor remains subject to the existing Codex queue, transition receipts, PR gates and no-automatic-merge authority.

## Retention

Operational evidence is not deleted because of age. Old or drifted episodes become cold/revalidation context. Forgetting means retrieval suppression, not destructive deletion.

## Safety

The extension may not change canonical market state, model weights, thresholds or market rules, execute portfolio actions, auto-promote scientific/procedural claims, or treat memory as authority over current `main`.

## Success measurement

Shadow operation must baseline and later measure repeated-investigation rate, task bootstrap/context load, useful retrieval precision, stale-memory safety and failed-task rate. No token/context-saving percentage may be claimed before measured evidence exists.
