# 02_DATA_PING - Data Truth Mission Card

**Status:** NAVIGATION_ONLY  
**Authority:** NONE_BY_ITSELF  
**Folder role:** DATA PING collection contracts, source QA, version governance, handoffs, accepted evidence and live-state routing.

## Entering this folder

Do not infer the active runtime from one historical handoff or version-named file.

Resolve current state from root operational surfaces first:

```text
../LATEST_OPERATIONS_DASHBOARD.json
../LATEST_HANDOFF.json
```

Then follow the exact DATA PING owner/pointers named by current governance and receipts.

Historical handoff files are intentionally preserved and may remain older than the current collector/runtime generation.

## DATA PING's job

DATA PING captures verified observations and state. It does not own unrestricted interpretation or portfolio execution.

Core truth rules:

```text
MISSING != NEGATIVE
UNAVAILABLE != ZERO
STALE != CURRENT
PROXY != CANONICAL
SOURCE CALL DECLARED != SOURCE CALL EXECUTED
RECEIPT PRESENT != RECEIPT VALID
```

Never fabricate a source call, hash, receipt, validator result, freshness timestamp or fallback value to make a packet complete.

## High-value mission seeds

### 1. Mixed-snapshot / temporal-coherence audit

Find where a packet can combine individually valid observations that do not belong to one coherent decision-time state.

### 2. Pointer and target integrity

Audit pointer -> target -> hash -> source timestamp -> acceptance linkage, including stale/latest conflicts.

### 3. Source failure self-repair

Test whether source failures degrade honestly to `UNAVAILABLE` while preserving the best bounded fallback path, without proxy promotion or silent substitution.

### 4. Delta/unit arithmetic audit

Re-run known hard classes such as order-of-magnitude, units, percentage-point vs percent, session selection and latest-eligible calculations.

### 5. Compression without truth loss

Ask whether the collector can expose a smaller decision-ready packet while preserving complete provenance, freshness and missing-data semantics.

## Astra-class qualification challenge

A stronger model should reproduce bugs and edge cases from frozen historical packets and current runtime code rather than merely inspect prose.

Good tests include:

- stale live anchor;
- mixed snapshot state;
- BTC OI x10-type arithmetic defect;
- ETF latest-eligible session selection;
- breadth universe disagreement;
- missing/blocked source where the correct result is `UNAVAILABLE`;
- duplicate/replay behavior;
- exact current-main source binding.

Freeze expected behavior before replay where possible.

## Authority ceiling

Default mode is `READ_ONLY` or bounded replay.

Do not:

- change market thresholds;
- promote a proxy source;
- alter active DATA PING authority;
- create a new collector family because one source is inconvenient;
- backfill values without explicit canonical permission;
- turn DATA PING alone into portfolio action.

Code fixes later require the governed branch -> PR -> CI -> main readback path.

## Useful adjacent surfaces

```text
../09_SOURCE_QA/README.md
../research/README.md
../07_PROMPTS_AND_AGENTS/astra/README.md
```
