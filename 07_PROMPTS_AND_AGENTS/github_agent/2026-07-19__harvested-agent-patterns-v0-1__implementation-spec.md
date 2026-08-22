# Harvested Agent Patterns v0.1 - Implementation Specification

**Date:** 2026-07-19  
**Status:** APPROVED_IMPLEMENTATION_SPEC  
**Classification:** OPERATIONS_AND_LINEAGE_HARDENING  
**Source inspiration:** `Shubhamsaboo/awesome-llm-apps`, harvested patterns only, no wholesale installation  
**Authority boundary:** no market logic, gate, threshold, score, active event, forecast, DATA PING state or portfolio action

## 1. Objective

Harvest four narrowly useful patterns into the existing Investering repository without importing the upstream applications, adding a new market engine or expanding the active Skill stack:

1. deterministic scope-creep detection for larger Codex diffs;
2. read-only commit archaeology before edits to canonical or historically complex paths;
3. deterministic collection/normalization/deduplication boundaries for Data Terminal pipelines;
4. tamper-evident hash-chained receipts for selected Data Terminal and agent-run artifacts.

The durable principle is:

```text
mechanical work -> deterministic utilities
judgment work   -> bounded agent review
all changes     -> explicit intent, evidence and verification
```

## 2. Existing ownership and dependency map

This work must not duplicate or silently expand the two currently open implementation streams.

### PR #49 - Framework operations hardening v0.2

Owns:

- Framework Integrity Canary hardening;
- Master Monday pointer-chain visibility;
- prospective maturity/status queue;
- archive-hygiene reporting;
- weekly operations-integrity workflow and issue ledger.

This harvest must not create a competing canary, weekly integrity workflow, archive scanner or issue ledger.

### PR #82 - Data Terminal Phase 1 shadow pilot

Already implements or proposes:

- deterministic common contracts;
- source registry;
- one FRED CSV collector;
- fixture-backed unit/schema/negative/stale tests;
- payload SHA-256;
- source health;
- immutable receipt;
- shadow snapshot;
- DATA PING handoff candidate;
- manual read-only artifact workflow.

This harvest must treat PR #82 as the owner of the Data Terminal root and extend it only after branch/main availability is verified. Do not recreate its paths from memory.

## 3. Required read order

Before implementation, read:

1. `AGENTS.md`
2. `00_ARCHIVE_CONTROL/CANONICAL_INDEX.md`
3. `00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md`
4. `00_ARCHIVE_CONTROL/ARCHIVE_MAP_AND_ROUTING.md`
5. `00_ARCHIVE_CONTROL/SKILL_REGISTRY.md`
6. `.agents/skills/canonical-context-router/SKILL.md`
7. `.agents/skills/archive-governance/SKILL.md`
8. `07_PROMPTS_AND_AGENTS/github_agent/2026-07-12__agent-control-loop-v0-1__canonical.md`
9. PR #49 specification and current diff
10. PR #82 specification, current diff, tests and implementation receipt
11. all existing `.github/workflows/`

Search before create. Reuse existing deterministic helpers where functionally equivalent.

## 4. Delivery strategy

Implementation is split into two bounded waves to avoid cross-PR contamination.

### Wave A - repository change-control tools

May proceed independently from PR #82 if no overlap with PR #49 is found.

#### A1. Scope Creep Guard

Create one dependency-free, read-only utility under the existing GitHub-agent tools area.

Required behavior:

- accepts an explicit one-line intent;
- evaluates working, staged, branch-base or supplied unified diff input;
- emits deterministic JSON;
- reports changed paths and subsystem spread;
- flags unrelated path families;
- flags dependency-manifest changes;
- flags workflow/config changes;
- flags public contract/schema changes;
- flags deletion, rename and move signals;
- flags oversized hunks and formatting-only spill where deterministically detectable;
- classifies each finding as `KEEP`, `JUSTIFY`, `SPLIT` or `BLOCK_REVIEW`;
- never modifies the repository;
- never invokes an LLM;
- never infers market impact.

Required inputs must include at least one of:

```text
--intent TEXT
--intent-file PATH
```

and one diff source:

```text
--staged
--base REF
--diff PATH_OR_STDIN
```

The output must state limitations instead of claiming unavailable checks.

#### A2. Commit Archaeology Helper

Create one dependency-free, read-only utility under the existing GitHub-agent tools area.

Required behavior:

- accepts a tracked file and optional line range;
- identifies the introducing commit where deterministically possible;
- returns an oldest-to-newest relevant commit timeline;
- records path aliases/renames where Git supports discovery;
- reports repeatedly co-changed files;
- extracts issue/PR references, revert/workaround/TODO signals from commit metadata;
- summarizes current blame ownership counts as evidence, not authority;
- emits deterministic JSON plus an optional concise text view;
- produces a change-risk note grounded only in repository history;
- never modifies the repository;
- never calls external services or an LLM.

It must explicitly distinguish:

```text
FACT_FROM_GIT
HEURISTIC_FROM_COMMIT_TEXT
NOT_DETERMINABLE
```

#### A3. Change-control integration

Do not create a new GitHub workflow in this PR.

Provide a documented invocation contract so PR #49 or a later reviewed workflow can call the tools after its ownership is settled.

For larger Codex changes, the intended order is:

```text
intent declaration
-> commit archaeology for sensitive paths
-> implementation
-> scope-creep report
-> tests
-> human/Codex review
```

### Wave B - Data Terminal pipeline and receipt lineage

Wave B is blocked until PR #82 code is available on the target branch or a deliberate stacked-PR base is used. Never reproduce PR #82 files manually.

#### B1. Deterministic pipeline-stage contract

Extend the existing Data Terminal owner with explicit stages:

```text
COLLECT
-> NORMALIZE
-> DEDUPLICATE
-> VALIDATE
-> SOURCE_HEALTH
-> RECEIPT
-> SHADOW_SNAPSHOT
-> HANDOFF_CANDIDATE
```

Rules:

- `COLLECT`, `NORMALIZE`, `DEDUPLICATE` and schema validation are deterministic utilities;
- no LLM may fetch, normalize, deduplicate, repair or silently fill source data;
- source adapters return one shared record envelope;
- direct and derived observations remain separated;
- missing remains `UNKNOWN`/explicit missing;
- conflicts remain preserved;
- synthesis remains a non-binding downstream candidate;
- each stage records input/output hashes and explicit status;
- retries must be bounded and visible;
- no silent fallback.

Do not add a second orchestrator if the existing Phase 1 collector can be refactored into the stage contract without unnecessary churn.

#### B2. Hash-chained receipts

Upgrade selected Data Terminal or agent-run receipt records from isolated hashes to an optional tamper-evident chain.

Minimum receipt fields:

```yaml
chain_id:
seq:
timestamp_utc:
actor:
action:
input_hash:
output_hash:
previous_entry_hash:
entry_hash:
source_refs:
authority:
status:
```

Hash rules:

- SHA-256 only;
- hash canonical UTF-8 JSON with stable key ordering and normalized separators;
- exclude `entry_hash` from its own hash material;
- genesis `previous_entry_hash` is 64 zeroes;
- append-only artifacts only;
- no blockchain or immutability claim beyond `tamper_evident`;
- provide a dependency-free verifier that returns the first broken sequence;
- chain failure must never rewrite history automatically;
- chain failure is an audit finding, not a market signal.

The chain must not include secrets, private API keys or raw personal data.

#### B3. Receipt scope

Initial scope is deliberately narrow:

- Data Terminal manual shadow runs;
- implementation receipts where a run contract explicitly opts in;
- future agent-run audit artifacts only after separate review.

Do not retroactively fabricate chain entries for historical receipts. Historical isolated receipts remain valid historical artifacts.

## 5. Non-goals

Explicitly forbidden:

- installing or vendoring the upstream repository;
- adding Agno, Google ADK, Streamlit, FastAPI or other framework dependencies;
- creating a new Skill or market engine;
- adding a new scheduled workflow;
- changing PR #49 workflow ownership;
- changing active DATA PING schemas, pointers or accepted logs;
- adding LLM-based collection, normalization or deduplication;
- automated repair, merge or writeback;
- deleting, renaming or moving existing files;
- retroactive receipt reconstruction;
- market, portfolio or execution authority.

## 6. Change budget

### Wave A target

Maximum intended changed files: 6

Expected:

- this specification;
- scope-creep utility;
- scope-creep tests/fixtures;
- commit-archaeology utility;
- commit-archaeology tests/fixtures;
- implementation receipt or concise runbook only if required by existing governance.

### Wave B target

Maximum intended changed files: 7, after PR #82 dependency resolution.

Expected:

- minimal stage-contract extension;
- canonical-record helper if needed;
- hash-chain helper/verifier;
- focused tests/fixtures;
- minimal documentation/receipt update;
- existing manual workflow update only if PR #82 ownership permits and no workflow duplication exists.

No deletion, rename or move.

## 7. Required validation

### Wave A

- Python compile checks;
- deterministic fixture tests;
- clean-repo, staged, base-diff and stdin-diff cases for Scope Creep Guard;
- positive and deliberately unrelated-change cases;
- introducing-commit, line-range, rename/co-change and invalid-input cases for Commit Archaeology;
- identical input produces identical JSON except explicitly variable timestamps, which should be absent unless requested;
- exact changed-file list;
- zero-deletion check;
- scope report run against the implementation itself.

### Wave B

- existing PR #82 tests remain passing;
- canonical JSON/hash determinism;
- valid chain verification;
- tampered middle-entry failure;
- missing sequence failure;
- wrong previous-hash failure;
- genesis validation;
- stale, missing, conflict and no-silent-fallback tests remain passing;
- workflow YAML structural validation if an existing manual workflow is changed;
- no schedule and read-only permissions preserved;
- exact diff and zero-deletion checks.

## 8. Branch and PR strategy

This specification branch is:

`agent/harvest-agent-patterns-v0-1`

Implementation must stop before merge.

Recommended execution:

1. implement Wave A on this branch after overlap check with PR #49;
2. keep the PR draft;
3. after PR #82 is merged or deliberately selected as a stacked base, rebase/update intentionally;
4. implement Wave B in a separate follow-on PR unless the final Wave A diff remains small and dependency history is clean;
5. no auto-merge.

## 9. Completion report

Return:

1. exact changed paths;
2. overlap findings against PR #49 and PR #82;
3. Wave A test commands and results;
4. self-scope-creep report;
5. commit-archaeology evidence for every pre-existing sensitive path changed;
6. Wave B status: `IMPLEMENTED`, `BLOCKED_BY_PR_82`, or `FOLLOW_ON_PR_REQUIRED`;
7. limitations and false-positive risks;
8. explicit confirmation of zero market and portfolio authority.

## 10. Stop conditions

```text
SCOPE_OVERLAP_WITH_PR_49
DATA_TERMINAL_OWNER_UNAVAILABLE
STACKED_PR_BASE_UNVERIFIED
WRITE_BRANCH_UNVERIFIED
DETERMINISTIC_CHECK_NOT_RELIABLE
NEW_DEPENDENCY_REQUIRED
WORKFLOW_DUPLICATION_RISK
MARKET_OR_PORTFOLIO_AUTHORITY_REQUESTED
HISTORY_REWRITE_REQUIRED
```

A narrow honest implementation is preferred to broad feature accumulation.
