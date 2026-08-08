# DATA PING Platform — Ratified Target Architecture

**Date:** 2026-07-20  
**Status:** RATIFIED_TARGET_ARCHITECTURE_NOT_ACTIVE_RUNTIME  
**Authority:** Architecture, compatibility and transition planning only  
**Market authority:** NONE  
**Portfolio authority:** NONE

## Ratified definition

DATA PING is an implementation-independent collector standard with one or more reference implementations.

The Custom GPT collector is not DATA PING itself. It is one implementation of the standard.

## Ratified architecture

```yaml
platform_name: DATA_PING_PLATFORM
core_standard: DATA_PING_CORE_STANDARD_v1_DRAFT
active_reference_runtime_target: DATA_PING_RUNTIME_v3_DRAFT_2
external_contract: DATA_PING_MAIN_THREAD_INGEST_v2_0_RAW
external_contract_change: NONE
architecture:
  - LEVEL_0_CORE
  - LEVEL_1_RUNTIME
  - LEVEL_2_SOURCES
  - LEVEL_3_OPERATIONS
  - SEPARATE_TEST_LAYER
source_model: PLUGIN_BASED
context_model: EXECUTION_CONTEXT_CONTRACT
test_model:
  - COMPLIANCE
  - RUNTIME
  - REGRESSION
reference_implementation: CUSTOM_GPT_COLLECTOR_v1
builder_role: MINIMAL_BOOTSTRAP_ONLY
```

## Platform layout

```text
DATA_PING_PLATFORM/
├── 00_CORE/
├── 01_RUNTIME/
├── 02_SOURCES/
├── 03_OPERATIONS/
├── 04_TESTS/
└── 05_REFERENCE_IMPLEMENTATION/
```

## Core boundary

Core defines invariants that every compatible collector must satisfy:

- AI-to-AI collector philosophy
- raw source rows are authoritative
- deterministic aggregates are convenience values
- explicit provenance and current-run receipts
- explicit missing/null semantics
- collector has no framework-state authority
- collector has no portfolio authority
- no silent reconstruction, interpolation or guessed lineage
- source context and framework context remain separate
- validation and hash claims require executed proof

## Runtime boundary

Runtime v3 is a reference execution model. It may evolve independently from Core provided it remains Core-compliant and continues to emit the active external contract.

Runtime configuration is represented by a compact machine-readable Runtime Manifest. Version History is separate and append-only.

## Source plugin contract

Each source plugin should expose at minimum:

```text
PLUGIN_ID
PLUGIN_VERSION
SOURCE_FAMILY
COMPATIBLE_RUNTIME
COMPATIBLE_OUTPUT_CONTRACT
APPROVED_ACTIONS
COLLECTION_SEQUENCE
RAW_ROW_SCHEMAS
RECEIPT_REQUIREMENTS
FRESHNESS_POLICY
FAILURE_POLICY
FALLBACK_POLICY
DETERMINISTIC_METHODS
PROHIBITED_INTERPRETATIONS
```

## Execution context contract

Framework context is not a market-data source.

Canonical context statuses must be distinct from source-health statuses.

Context statuses include:

```text
AVAILABLE_CURRENT_RUN
AVAILABLE_THREAD_LOCAL
AVAILABLE_CANONICAL_BOOTSTRAP
UNKNOWN_CONTEXT_NOT_LOADED
NONE_NEW_THREAD
NOT_COMPARABLE
INCOMPATIBLE_METHOD
STALE_CONTEXT
```

Missing canonical predecessor in a new thread is not source failure and must never be guessed.

## Testing model

Three separate test layers are required:

1. Compliance tests — contract, schema, enums, JSON, UTF-8, receipts and hashing.
2. Runtime tests — degraded and partial source scenarios, retry/fallback and REPACK_ONLY behavior.
3. Regression tests — every verified historical bug becomes a permanent testcase.

## Internal and external errors

Detailed diagnostics may use an internal artifact such as `DATA_PING_OS_INTERNAL_ERROR_v1`.

Main Framework must still receive only the existing V2 RAW 11-key contract, including its contract-valid `ERROR_PACKET` representation when required.

## First OS v3 draft disposition

```yaml
artifact: DATA_PING_OS_v3_FIRST_DRAFT
status: CORE_DRAFT_1_AND_REQUIREMENTS_SOURCE
active_runtime: false
disposition: DECOMPOSE_INTO_DATA_PING_PLATFORM_ARCHITECTURE_DRAFT_2
```

## Activation boundary

This document does not activate Runtime v3, a new Builder, new source methods, a new packet contract or a new DATA PING thread version.

The active external contract remains `DATA_PING_MAIN_THREAD_INGEST_v2_0_RAW` until a separate compatibility-tested activation record explicitly changes runtime ownership.
