# Persistent Agent Runtime Candidate v1

Status: INCUBATING
Date: 2026-08-06
Candidate ID: ARC-PERSISTENT-AGENT-RUNTIME-001
Authority: ARCHITECTURE_RESEARCH_ONLY

## Decision

Register the need for a persistent, resumable agent runtime now, but do not install Prime Agent or any equivalent resident runtime yet.

Prime Agent is a reference implementation only. The candidate is product-neutral and may later be satisfied by an internal implementation or a different upstream runtime.

## Intended capability

The candidate covers:

- persistent and resumable agent sessions;
- explicit objectives, budgets and terminal receipts;
- parent and child agent relationships;
- mailbox delivery with acknowledgements;
- continuity across compaction and process interruption;
- schedule claiming and coalescing;
- bounded self-refinement with preview and rollback;
- recovery without reconstructing state from conversation memory.

## Explicit non-goals

This candidate does not authorize:

- installation of a daemon or self-hosted runner;
- new secret access;
- direct writes to `main`;
- automatic merge;
- canonical market-state changes;
- model-weight changes;
- portfolio action;
- owner-grade DATA PING, ETF, weekly-freeze or Master Monday authority.

## Promotion stages

1. `INCUBATING` - candidate and criteria registered.
2. `READY_FOR_CONTRACT_BUILD` - internal runtime contracts may be implemented by bounded PR.
3. `READY_FOR_SIMULATION` - existing GitHub primitives may simulate resumable operation.
4. `READY_FOR_ISOLATED_CANARY` - disposable, secret-free and non-authoritative runtime test permitted.
5. `READY_FOR_SHADOW_RUNTIME` - persistent shadow execution permitted behind deterministic receipts and budget limits.
6. `LIMITED_OPERATIONAL_PROPOSAL` - explicit framework-owner review required before any operational authority.

Automatic evaluation may advance only through `READY_FOR_ISOLATED_CANARY`. Any runtime installation, new secret, self-hosted runner or operational authority requires a separate governed PR and explicit approval.

## Readiness categories

### Internal need

Evidence must come from durable incidents, remediation rows or reliability records, not narrative preference.

Target evidence:

- at least three cross-run context-loss or manual handover reconstruction events;
- at least two interrupted long-task events;
- at least two message-delivery or continuation failures;
- at least one scheduled state-loss event.

### Internal architecture

Before an external runtime is considered, the framework should own product-neutral contracts for:

- agent objective;
- session state;
- message receipt;
- terminal receipt;
- compaction continuity;
- runtime budget;
- capability manifest.

### Operational stability

The active framework must show:

- no unresolved P0 remediation;
- no current automation RED;
- no hash mismatch or missing required handoff pointer;
- a sustained successful observation window for continuity and operations.

### Upstream maturity

Any external runtime must have:

- a pinned version;
- an observation period without breaking changes;
- tested recovery around compaction;
- failure semantics that cannot appear as silent success;
- preview and rollback for refinement;
- session persistence tests;
- an external sandbox and kill switch.

## Automatic behavior

The readiness evaluator may:

- inspect repository evidence;
- publish a deterministic readiness receipt;
- retain blockers and missing evidence;
- recommend the next stage;
- create a bounded future Codex-ready proposal through existing remediation governance.

It may not install software, create secrets, run a resident daemon, alter authority or merge changes.

## Kill criteria

Close or replace the candidate if:

- the need is not supported by durable evidence after a meaningful observation period;
- existing GitHub-native primitives solve the problem with lower complexity;
- the runtime cannot be sandboxed or audited;
- failure and compaction semantics remain ambiguous;
- expected value does not justify cost, security surface or maintenance burden.
