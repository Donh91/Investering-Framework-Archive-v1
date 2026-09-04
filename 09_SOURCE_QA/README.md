# 09_SOURCE_QA - Incident & Source-Quality Mission Card

**Status:** NAVIGATION_ONLY  
**Authority:** NONE_BY_ITSELF  
**Folder role:** Source QA, automation incidents, provider/source validation and durable failure evidence.

## Entering this folder

Do not count incident files as independent current failures.

Start with:

```text
../LATEST_OPERATIONS_DASHBOARD.json
../LATEST_HANDOFF.json
../research/architecture_health/LATEST_AUTOMATION_HEALTH.json
../research/architecture_health/LATEST_ARCHITECTURE_HEALTH.json
```

Then use incident files to reconstruct history and root cause.

## What this folder should answer

```text
What failed?
When did it fail?
Was the failure current or historical?
Was durable output still published?
What was the actual root cause?
Was the root cause fixed or merely masked?
What regression evidence proves closure?
Did a later incident represent the same underlying defect?
```

## High-value mission seeds

### 1. Incident clustering

Collapse repeated symptom incidents into root-cause families. Distinguish unresolved architecture defects from historical residue.

### 2. Failure-state honesty

Find cases where workflow status, health status and durable output disagree. A RED observer can coexist with valid output; a GREEN workflow can publish wrong/stale content.

### 3. Regression-proof audit

For closed incidents, identify the exact test/CI/production evidence that would catch recurrence. Flag fixes with no durable regression guard.

### 4. Source-quality propagation

Trace whether stale, missing, partial or proxy source status is preserved through downstream consumers instead of being normalized into false certainty.

### 5. Automation incident archaeology

Use commit/run history to distinguish code defects, schedule gaps, permissions, Git identity, concurrency/locks, provider availability and consumer-pointer failures.

## Current-state rule

Revalidate any "current" incident at session start. The dashboard is the operational entrypoint; incident markdown is historical evidence, not a live-state oracle.

## Authority ceiling

Default mode is `READ_ONLY`.

Do not close incidents, relabel health, change workflows or modify source contracts merely from a narrative diagnosis. Reproduce the mechanism first.

## Astra-class challenge

A stronger model should be able to walk from symptom -> logs -> commit -> workflow -> producer -> pointer -> consumer -> regression guard without losing the chain.

The valuable result is a smaller number of true root causes, not a larger incident report.

See:

```text
../03_WEEKLY_OPERATIONS/README.md
../02_DATA_PING/README.md
../research/README.md
../07_PROMPTS_AND_AGENTS/astra/README.md
```
