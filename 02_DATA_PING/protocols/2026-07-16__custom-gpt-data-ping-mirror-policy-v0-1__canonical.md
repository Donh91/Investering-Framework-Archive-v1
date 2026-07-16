# Custom GPT DATA PING Mirror Policy v0.1

**Status:** CANONICAL_ARCHITECTURE_POLICY  
**Owner:** MAIN_FRAMEWORK / CHATGPT  
**Decision:** KEEP_FULL_ARCHIVE_PRIVATE  
**Optional interface:** SEPARATE_SANITIZED_READ_ONLY_MIRROR

## Executive decision

The full `Investering-Framework-Archive-v1` repository must remain private.

A separate repository named approximately `custom-gpt-data-pings` may be useful only as a narrow read-only exchange interface when authenticated private access from the Custom GPT is unavailable or unreliable.

The separate repository must never become the canonical framework owner.

## Preferred access order

```text
1. AUTHENTICATED_READ_ACTION_TO_PRIVATE_SANITIZED_PATHS
2. PRIVATE_READ_ONLY_MIRROR_WITH_AUTHENTICATED_ACTION
3. PUBLIC_SANITIZED_READ_ONLY_MIRROR
4. MANUAL_COPY_ONLY
```

Public access is a fallback for portability, not the preferred security design.

## One-way authority model

```text
CUSTOM_GPT CREATES SENSOR PACKET
-> MAIN FRAMEWORK ACCEPTS OR REJECTS
-> PRIVATE CANONICAL REPO STORES ACCEPTED STATE
-> SANITIZED MIRROR RECEIVES ALLOWLISTED ACCEPTED FILES
-> CUSTOM GPT READS MIRROR ON NEXT RUN
```

Custom GPT must not write directly to the canonical or mirror repository.

## Mirror allowlist

A mirror may contain only:

- `schema.json`
- `latest.json`
- `latest_decision_context.json` with sensitive fields removed
- accepted sensor payloads under immutable dated paths
- fixed-cohort identity and forward values needed for continuity
- local ETF sensor ledger with source provenance
- source health and freshness
- checksums and manifest
- explicit instructions that partial sessions are pending, never zero

## Mirror denylist

A mirror must not contain:

- portfolio holdings, sizes, cost basis or tax information
- personal or family information
- private paid research content or reproduced TechDev material
- API keys, tokens, secrets or connector configuration
- internal portfolio permission logic
- unpublished action plans
- private prompts or hidden governance instructions
- raw unaccepted Custom GPT output
- branches, drafts or provisional state
- any file not explicitly allowlisted

## Canonical eligibility

A mirrored packet is readable only when all are true:

```text
acceptance_status = ACCEPTED_BY_MAIN_FRAMEWORK
readback_status = PASS
payload_hash is present
source_snapshot_id is present
canonical_private_pointer is present
```

Any other file is non-canonical and must be ignored.

## Required mirror files

### latest.json

Must point to exactly one accepted snapshot and include:

- snapshot ID
- accepted timestamp
- immutable payload path
- payload SHA-256
- schema version
- previous accepted snapshot ID
- source quality
- completion status

### latest_decision_context.json

Must contain only sensor-facing context:

- active DATA PING version
- latest accepted snapshot
- continuity state
- fixed-cohort version
- required next sensor observations
- missing data priorities
- no portfolio permission or user-specific action data

### manifest.json

Must list every published path and hash. Files absent from the manifest are untrusted.

## Custom GPT read instruction

At the beginning of every DATA PING run:

1. Fetch `latest.json`.
2. Require `readback_status = PASS`.
3. Fetch the immutable payload and verify the declared SHA when technically possible.
4. Load continuity, fixed cohort and ETF ledger from accepted data only.
5. Never infer missing values from older runs.
6. Produce a new sensor packet with the prior accepted snapshot ID.
7. Defer all framework interpretation, gates and portfolio action to Main Framework.

## Expected value

A mirror can materially improve:

- continuity across new Custom GPT conversations;
- fixed-cohort persistence;
- ETF ledger persistence;
- source-switch bridges;
- reproducibility and auditability;
- reduced `NOT_COMPUTED` caused by lost local state.

It does not directly improve source truth, market-wide flow coverage or predictive edge. It is therefore an infrastructure improvement, not a signal improvement.

## Public mirror activation gate

Do not create or publish a public mirror until:

1. the allowlist files exist and have passed private readback;
2. at least one full update cycle has been tested privately;
3. secret and personal-data scans return clean;
4. the Custom GPT can demonstrate deterministic reading of `latest.json` and the immutable payload;
5. Main Framework confirms that no private framework authority leaked.

## Current recommendation

```text
FULL EXISTING REPOSITORY PUBLIC: NO
SEPARATE SANITIZED REPOSITORY: CONDITIONALLY YES
PUBLIC IMMEDIATELY: NO
PRIVATE/AUTHENTICATED ACTION FIRST: YES
ONE-WAY READ-ONLY MIRROR: YES IF REQUIRED
```
