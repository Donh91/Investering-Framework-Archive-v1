# DATA PING Platform — Transition and Coexistence Guard

**Date:** 2026-07-20  
**Status:** ACTIVE_TRANSITION_GUARD  
**Scope:** Prevent confusion between current V6/V2 RAW production and future DATA PING Platform drafts

## Current production authority

Until an explicit activation record is accepted:

```yaml
active_data_ping_thread_version: V6
active_external_contract: DATA_PING_MAIN_THREAD_INGEST_v2_0_RAW
active_runtime_authority: CURRENT_V2_RAW_RUNTIME_AND_ACCEPTED_V6_HANDOVER
active_main_framework_consumer: CHATGPT_MAIN_FRAMEWORK
new_platform_status: DESIGN_AND_TEST_ONLY
```

## Naming rules

Every future architecture artifact must carry one of these status classes:

```text
DRAFT_NOT_ACTIVE
SHADOW_TEST_ONLY
COMPATIBILITY_CANDIDATE
RELEASE_CANDIDATE_NOT_ACTIVE
ACTIVE_REFERENCE_RUNTIME
HISTORICAL_READ_ONLY
```

No architecture draft may be named merely `ACTIVE`, `CURRENT`, `CANONICAL` or `LATEST` without a separate activation receipt.

## Output coexistence rule

During development, both current and new implementations may run only if outputs are explicitly labeled:

```text
CURRENT_PRODUCTION_V2_RAW
PLATFORM_V3_SHADOW_CANDIDATE
```

Only `CURRENT_PRODUCTION_V2_RAW` may be considered for Main Framework canonical acceptance before cutover.

A Platform v3 shadow packet must not become:

- canonical predecessor
- latest accepted log
- active event owner
- Master Monday source owner
- portfolio or framework state input

unless Main Framework explicitly accepts it under a release activation record.

## No mixed-document boot

The Custom GPT Builder must not load an uncontrolled mixture of:

- current V2 RAW production documents
- legacy human-output documents
- Platform v3 draft documents

The reference implementation requires an explicit `ACTIVE_KNOWLEDGE_UPLOAD_LIST` generated from the Runtime Manifest.

Unlisted files are non-authoritative even if present in Knowledge.

## Required cutover artifacts

Activation of DATA PING Runtime v3 requires all of the following:

1. Ratified Core Standard.
2. Machine-readable Runtime Manifest.
3. Execution Context Contract.
4. Active source-plugin list and compatibility declarations.
5. Exact V2 RAW output compatibility proof.
6. Compliance test result.
7. Runtime degraded-source scenario result.
8. Historical regression result.
9. Golden-packet parity report.
10. Builder active Knowledge upload list.
11. Thread bootstrap and handover artifact.
12. Explicit activation receipt naming the first active runtime and packet.

## Minimum cutover tests

Blocking tests include:

- strict JSON and exact 11-key root set
- constants and authority parity
- current-run receipts for populated layers
- no framework interpretation
- no guessed lineage
- new-thread context status handling
- missing/null/no-session semantics
- stablecoin official-total guard
- breadth comparability guard
- partial candle settlement guard
- exact hash behavior
- REPACK_ONLY behavior
- source fallback proof

## Historical packet protection

Historical V1.1, V2.x, V3_PLUS_MACHINE and human-output artifacts remain immutable historical evidence.

They may be mined for requirements and regression fixtures but must not control the new runtime unless explicitly mapped into the active Runtime Manifest.

## Lineage at cutover

The first active Runtime v3 packet must declare:

```yaml
canonical_predecessor_id: latest Main-Framework-accepted production packet
collector_predecessor_id: latest accessible method-compatible collector packet or NONE
runtime_predecessor: active V2 RAW runtime identifier
runtime_activation_receipt: required
```

A new thread without loaded canonical context must use `UNKNOWN_CONTEXT_NOT_LOADED`; it must not guess an older version.

## Rollback rule

If Runtime v3 fails a blocking production check:

- preserve the failed packet as validation-only evidence
- do not advance canonical predecessor
- do not update latest accepted log
- do not change Main Framework state
- revert reference implementation to the last accepted V2 RAW runtime
- record the failure as a permanent regression testcase

## Final guard

Architecture ratification is not runtime activation.

Source-plugin creation is not source promotion.

A valid shadow packet is not a canonical packet.

A new Builder configuration is not active until compatibility tests, handover and explicit activation receipt are complete.
