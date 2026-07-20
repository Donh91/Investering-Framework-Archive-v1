# DATA PING Platform - Architecture Decision Record 001

**Dato:** 2026-07-20  
**Status:** CANONICAL  
**Område:** DATA PING platform architecture  
**Primary folder:** `02_DATA_PING/architecture/`  
**Related folders:** `02_DATA_PING/protocols/`, `02_DATA_PING/version_governance/`, `02_DATA_PING/live_state_handover/`, `07_PROMPTS_AND_AGENTS/custom_gpt/`  
**Decision ID:** ADR-001  
**Decision status:** RATIFIED  
**Effective from:** Architecture Draft 2  
**Implementation status:** ARCHITECTURE_RATIFIED / DECOMPOSITION_AND_MIGRATION_PENDING  
**Supersedes:** Monolithic Custom GPT / OS v3-as-single-system model  
**External contract impact:** NONE - `DATA_PING_MAIN_THREAD_INGEST_v2_0_RAW` remains unchanged  

---

## Archive interpretation

This record is the authoritative architectural decision for the next DATA PING structure.

It changes the identity and decomposition of DATA PING:

- DATA PING is the platform standard.
- The Custom GPT collector is one reference implementation.
- Builder instructions are a minimal bootloader, not the architecture itself.

This ratification does **not** claim that all target files have already been created or that the current Custom GPT has completed migration.

Until the release checklist and migration plan are completed:

- the existing collector may continue operating under its current validated runtime;
- the external ingest contract remains unchanged;
- no market state, gate, forecast, portfolio action or Main Framework interpretation changes merely because this ADR is ratified.

---

## 1. Canonical decision

DATA PING is defined as:

> An implementation-independent collector standard against which any compatible collector implementation can be validated.

The current Custom GPT is not DATA PING itself. It is a reference implementation of the DATA PING standard.

---

## 2. Canonical platform identity

```yaml
PLATFORM_NAME: DATA PING Platform
CORE_STANDARD: DATA PING Core Standard v1 Draft 1
ACTIVE_REFERENCE_RUNTIME: DATA PING Runtime v3 Draft 2
EXTERNAL_CONTRACT: DATA_PING_MAIN_THREAD_INGEST_v2_0_RAW
EXTERNAL_CONTRACT_STATUS: UNCHANGED
SOURCE_MODEL: PLUGIN_BASED
CONTEXT_MODEL: EXECUTION_CONTEXT_CONTRACT
TEST_MODEL: COMPLIANCE + RUNTIME + REGRESSION
REFERENCE_IMPLEMENTATION: CUSTOM_GPT_COLLECTOR v1 Draft 1
BUILDER_ROLE: MINIMAL_BOOTSTRAP_ONLY
```

---

## 3. Architectural layers

```text
DATA_PING_PLATFORM/
├── 00_CORE/
├── 01_RUNTIME/
├── 02_SOURCES/
├── 03_OPERATIONS/
├── 04_TESTS/
└── 05_REFERENCE_IMPLEMENTATION/
```

### 00_CORE

Normative, implementation-independent and rarely changed.

Contains:

- `CORE_CONSTITUTION`
- `AUTHORITY_MODEL`
- `OWNERSHIP_BOUNDARY`
- `HARD_BANS`
- `DATA_AUTHORITY_MODEL`
- `COMPATIBILITY_PRINCIPLES`

Core must not contain:

- source endpoints
- connector details
- retry counts
- active patches
- implementation limitations
- current schema-routing configuration
- historical regression cases

### 01_RUNTIME

Defines the active reference runtime.

Contains:

- `RUNTIME_MANIFEST.yaml`
- `OUTPUT_PROTOCOL.md`
- `EXECUTION_PIPELINE.md`
- `VALIDATOR.md`
- `SERIALIZATION.md`
- `PATCH_MANIFEST.yaml`
- `VERSION_HISTORY.md`

`RUNTIME_MANIFEST.yaml` answers only:

> What is active now?

`VERSION_HISTORY.md` answers:

> How did the runtime reach its current state?

The manifest is machine-readable configuration. Version History is append-only historical documentation.

### 02_SOURCES

Contains replaceable source plugins.

Each plugin implements the same minimum interface:

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

Source plugins may define collection and source-specific normalization.

They may not define:

- recovery conclusions
- rotation conclusions
- gate results
- framework state
- portfolio actions
- Main Framework interpretation

### 03_OPERATIONS

Contains operational continuity and lifecycle procedures.

Contains:

- `EXECUTION_CONTEXT_CONTRACT`
- `THREAD_BOOTSTRAP`
- `THREAD_HANDOVER`
- `MIGRATION_PLAN`
- `DIAGNOSTICS_PLAYBOOK`
- `RELEASE_CHECKLIST`
- `ROLLBACK_PROCEDURE`

These documents support the runtime but do not constitute the runtime itself.

### 04_TESTS

Defines formal compatibility and regression validation.

Contains:

- `TEST_MANIFEST.yaml`
- `COMPLIANCE_TESTS`
- `RUNTIME_SCENARIOS`
- `REGRESSION_TESTS`
- `GOLDEN_PACKETS`
- `INVALID_FIXTURES`

The three test classes are:

1. Compliance tests
2. Runtime scenario tests
3. Regression tests

A verified production failure must be converted into a permanent regression test.

### 05_REFERENCE_IMPLEMENTATION

Contains Custom GPT-specific implementation material.

Contains:

- `BUILDER_MINIMAL.md`
- `ACTIVE_KNOWLEDGE_UPLOAD_LIST.md`
- `CUSTOM_GPT_BOOT_SEQUENCE.md`
- `IMPLEMENTATION_LIMITATIONS.md`

The Builder acts only as a bootloader.

It must not become the primary location for governance, source schemas, validation details, patch history or regression cases.

---

## 4. Authority model

The collector owns:

- source-native rows
- normalized observations
- current-run source receipts
- source health
- freshness
- missing-data representation
- explicitly permitted deterministic source mathematics
- packaging
- technical validation

Main Framework owns:

- canonical acceptance
- framework state
- gates and Stage-1
- recovery
- rotation
- deployment
- rebuy
- portfolio actions
- final interpretation

Raw source rows remain authoritative.

Aggregates remain convenience values.

No source proof means no populated source value.

Missing data must be represented explicitly.

---

## 5. Context model

Execution context and source health are separate domains.

Approved context statuses:

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

Approved source-health statuses remain independently defined, including:

```text
PASS
PARTIAL
FAIL
UNAVAILABLE
STALE
```

Example:

```yaml
canonical_predecessor_id:
  value: null
  context_status: UNKNOWN_CONTEXT_NOT_LOADED
```

It must not be represented as:

```yaml
source_status: FAIL
failure_cause: predecessor missing
```

Canonical lineage is framework context, not market-source data.

---

## 6. External error compatibility

Detailed internal diagnostics use:

```text
DATA_PING_OS_INTERNAL_ERROR_v1
```

Possible internal categories include:

- `SOURCE_ERROR`
- `VALIDATION_ERROR`
- `SERIALIZATION_ERROR`
- `REPACK_ONLY`
- `COLLECTION_ABORT`
- `PARTIAL_SUCCESS`

The external interface remains:

```text
DATA_PING_MAIN_THREAD_INGEST_v2_0_RAW
```

When no normal packet can be emitted, the collector must use the existing contract-valid 11-key error representation.

No competing external error wire format is introduced.

---

## 7. Patch model

The minimum patch-manifest schema is:

```yaml
patch_id:
status:
target:
supersedes:
compatibility:
requires:
conflicts_with:
effective_from:
```

Test bindings are maintained separately in `TEST_MANIFEST.yaml`.

Patches contain rule changes.

The test manifest contains evidence requirements and regression bindings.

---

## 8. Regression-memory rule

Every verified production failure must become a permanent regression test.

Each regression record must contain:

```yaml
test_id:
class:
historical_bug:
input_fixture:
expected:
forbidden:
affected_documents:
fixed_from_version:
status:
```

Initial mandatory regression families:

- `LINEAGE_AND_BOOTSTRAP`
- `JSON_AND_SERIALIZATION`
- `HASH_AND_RECEIPTS`
- `SOURCE_AUTHORITY`
- `MISSING_AND_FALLBACK`
- `CANDLE_SETTLEMENT`
- `ETF_NO_SESSION`
- `STABLECOIN_TOTAL`
- `BREADTH_COMPARABILITY`
- `COLLECTOR_AUTHORITY`

---

## 9. Treatment of the first OS v3 draft

```yaml
ARTIFACT: DATA_PING_OS_v3_FIRST_DRAFT
NEW_STATUS: CORE_DRAFT_1_AND_REQUIREMENTS_SOURCE
AUTHORITY: NON_ACTIVE_ARCHITECTURE_INPUT
DISPOSITION: DECOMPOSE_INTO_PLATFORM_ARCHITECTURE_DRAFT_2
```

Its contents are redistributed as follows:

- Constitution -> Core
- Output, Execution and Validator -> Runtime
- Source Registry -> source-plugin interface and Runtime Manifest
- Migration and Checklist -> Operations
- Builder Minimal -> Reference Implementation

The first draft is preserved as requirements evidence but is not the active platform architecture.

---

## 10. Immediate next release target

```yaml
PLATFORM: DATA PING Platform
ARCHITECTURE: Draft 2
CORE_STANDARD: v1 Draft 1
RUNTIME: v3 Draft 2
EXTERNAL_CONTRACT: v2.0 unchanged
SOURCE_PLUGIN_CONTRACT: v1 Draft 1
EXECUTION_CONTEXT_CONTRACT: v1 Draft 1
TEST_ARCHITECTURE: v1 Draft 1
CUSTOM_GPT_REFERENCE_IMPLEMENTATION: v1 Draft 1
```

This target is architectural and release-oriented. It must be completed through migration, validation and release evidence rather than inferred from document ratification alone.

---

## 11. Final principle

Further development must prioritize:

- decomposition
- formalization
- compatibility
- source proof
- context discipline
- validation
- regression protection

Further Builder growth is not an acceptable substitute for architecture.

---

## 12. Binding archive consequences

From 2026-07-20 onward:

1. New DATA PING architecture files must be classified into Core, Runtime, Sources, Operations, Tests or Reference Implementation.
2. Custom GPT-specific material must not be treated as platform-wide governance.
3. Current runtime state must be machine-readable and separate from append-only history.
4. Source plugins must remain replaceable and interpretation-free.
5. Context failures must not be mislabeled as source failures.
6. The external v2.0 ingest contract must not be changed by the internal decomposition.
7. Verified production failures must create regression fixtures and permanent tests.
8. The first OS v3 draft remains preserved, but non-active.
9. Migration completion requires explicit release and validation evidence.
10. This ADR does not alter market interpretation, gates, deployment or portfolio authority.
