# Framework Execution Harness Candidate v1

Status: INCUBATING
Date: 2026-08-06
Candidate ID: ARC-PERSISTENT-AGENT-RUNTIME-001
Authority: ARCHITECTURE_RESEARCH_ONLY
Legacy contract name: PERSISTENT_AGENT_RUNTIME_CANDIDATE_v1

## Updated decision

The primary architecture candidate is now a model-independent **Framework Execution Harness**.

Persistent or resident execution is a possible later capability, not the architecture's identity and not the first implementation priority.

Prime Agent remains a reference implementation for persistent asynchronous process management only. It is not evidence of scalable recursive agency and is not selected as a platform dependency.

## Architecture principle

The framework owns:

- task definition;
- context selection;
- capability boundaries;
- validation;
- evidence and receipts;
- ledgers and learning;
- authority and promotion gates.

Models and runtimes are replaceable workers inside that control plane.

The target path is:

`TASK CONTRACT -> CONTEXT BUNDLE -> BOUNDED WORKER -> EVIDENCE -> VALIDATION -> RECEIPT -> LEDGER`

The harness must remain deliberately simple, observable and fail-closed. It must not become a generic autonomous agent platform.

## Implement-now scope

The following product-neutral primitives may be built and tested before any persistent runtime is considered:

1. `FRAMEWORK_TASK_CONTRACT_v1`
2. `FRAMEWORK_CONTEXT_BUNDLE_v1`
3. `FRAMEWORK_WORKER_MANIFEST_v1`
4. `FRAMEWORK_EVIDENCE_ENVELOPE_v1`
5. `FRAMEWORK_EXECUTION_RECEIPT_v1`
6. `FRAMEWORK_TERMINAL_RECEIPT_v1`
7. `FRAMEWORK_RUNTIME_ADAPTER_MANIFEST_v1`

These contracts must work with ordinary GitHub Actions and bounded model calls. They must not require a daemon, nested recursion or hidden session memory.

## Core responsibilities

### Task contract

Every task must freeze:

- objective and task type;
- required inputs;
- allowed sources, read paths and write paths;
- allowed tools and capabilities;
- forbidden actions;
- expected artifacts;
- completion evidence;
- deterministic validation;
- budget and timeout;
- escalation route.

### Context loading

Context must be selected by task type and explicit pointers. Workers must not begin by reading the entire repository.

A context bundle must record every included source, content hash, reason for inclusion and freshness signal. Missing mandatory context must block execution.

### Worker isolation

A worker is an interchangeable reasoning or execution component. It receives only the task contract and resolved context bundle.

Workers may produce evidence, artifacts and claims. They may not expand their own authority, change canonical state, merge code, create secrets or silently delegate beyond the contract.

Default recursion depth is zero. A single explicitly contracted child layer may be permitted later only when evidence shows material value. Arbitrary recursive delegation is prohibited.

### Evidence and validation

Claims must be linked to source evidence or generated artifacts. Validation must be external to the worker where practical.

A worker declaring success is not completion. Completion requires a valid execution receipt and all frozen completion checks.

### Receipts and ledgers

Every execution must end in exactly one terminal state:

- `COMPLETED`
- `BLOCKED`
- `FAILED`
- `CANCELLED`
- `BUDGET_EXHAUSTED`

No hidden learning is permitted. Reusable learning must enter an existing experiment, remediation, reliability or outcome ledger with provenance and kill criteria.

## Explicit non-goals

This candidate does not authorize:

- installation of Prime Agent or another daemon;
- a self-hosted runner;
- new secret access;
- direct writes to `main`;
- automatic merge;
- unrestricted shell or repository access;
- autonomous prompt or harness mutation;
- arbitrary recursive subagents;
- hidden long-term memory;
- canonical market-state changes;
- model-weight changes;
- portfolio action;
- owner-grade DATA PING, ETF, weekly-freeze or Master Monday authority.

## Promotion stages

1. `INCUBATING` - architecture, contracts and failure criteria registered.
2. `READY_FOR_CONTRACT_BUILD` - product-neutral harness contracts may be implemented by bounded PR.
3. `READY_FOR_SIMULATION` - contracts may be exercised through existing GitHub-native workflows.
4. `READY_FOR_ISOLATED_CANARY` - one disposable, secret-free, non-authoritative runtime adapter may be compared with a control.
5. `READY_FOR_SHADOW_RUNTIME` - resumable execution may be tested behind deterministic receipts and hard budgets.
6. `LIMITED_OPERATIONAL_PROPOSAL` - explicit framework-owner review required before operational authority.

Automatic evaluation may advance only through `READY_FOR_ISOLATED_CANARY`.

## Readiness categories

### Demonstrated need

Durable rows must show that a capability solves real friction. Narrative enthusiasm does not count.

Evidence may include:

- repeated context reconstruction or handover loss;
- interrupted tasks that could not resume safely;
- missing delivery or terminal receipts;
- scheduled state loss;
- measurable excess cost from broad repository loading;
- repeated worker authority or output ambiguity.

### Harness contract readiness

The product-neutral contracts must exist, validate and pass negative tests before a runtime adapter is considered.

### Operational stability

The active framework must show:

- no unresolved P0 remediation;
- no current automation RED;
- no hash mismatch or missing required handoff pointer;
- a sustained successful observation window.

### Runtime-adapter maturity

Any later external runtime must provide:

- pinned version and reproducible installation;
- tested interruption and resumption semantics;
- explicit non-zero failure exits and terminal receipts;
- no silent success;
- immutable task and context inputs;
- external sandbox, budget and kill switch;
- complete artifact and message provenance;
- no automatic self-refinement without exact diff, tests and rollback.

## Claude Opus external audit

Claude Opus should be used as an adversarial reviewer after the internal design is frozen, not as the architecture owner.

Its task is to identify production failure modes, unsupported assumptions and unnecessary complexity. Findings must be classified as documented risk, probable design weakness or speculative concern. Only changes that simplify the harness or materially improve determinism, isolation, auditability or recovery should be considered.

## Automatic behavior

The readiness evaluator may:

- inspect repository evidence;
- publish a deterministic readiness receipt;
- retain blockers and missing evidence;
- recommend the next bounded stage;
- route a bounded contract task through existing remediation governance.

It may not install software, create secrets, run a resident daemon, alter authority or merge changes.

## Kill criteria

Close, reduce or replace the candidate if:

- the need is not supported by durable evidence;
- task contracts plus existing GitHub primitives solve the problem without a resident runtime;
- context bundles do not reduce cost or error in controlled tests;
- worker isolation cannot be enforced;
- receipts cannot distinguish success, blockage and partial failure reliably;
- runtime adapters add more operational risk than measurable value;
- the architecture grows into a generic agent platform rather than a framework-specific harness.
