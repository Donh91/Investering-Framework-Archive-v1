# research/ - Live Research Runtime Mission Card

**Status:** NAVIGATION_ONLY  
**Authority:** NONE_BY_ITSELF  
**Folder role:** Live research runtime outputs, API-agent evidence, experiment lifecycle, remediation state, specialist outputs, architecture health and operational learning artifacts.

## Entering this folder

This is an active runtime surface. File volume is not priority.

Start with root live routing:

```text
../LATEST_OPERATIONS_DASHBOARD.json
../LATEST_HANDOFF.json
../LATEST_REMEDIATION_QUEUE.json
../LATEST_CODEX_READY_TASKS.json
../LATEST_CODEX_EXECUTION_STATE.json
```

Then follow the exact current pointer for the subsystem you are investigating.

## Important distinctions

```text
candidate != accepted experiment
accepted experiment != supported hypothesis
supported hypothesis != canonical rule
CODEX_READY != Codex executed
PR opened != fix merged
fix merged != production proof
health PASS != scientific validity
API output != framework authority
```

## High-value mission seeds

### 1. Backlog compression

The system can accumulate many experiment candidates, forecast candidates, incidents and remediation items. Cluster duplicates, stale aliases and dependency chains before creating new work.

### 2. Experiment portfolio audit

Ask whether incubating/inconclusive experiments still justify their complexity and data cost. Identify merge/kill/observe decisions without hindsight promotion.

### 3. Remediation closure

Trace `NEEDS_MORE_EVIDENCE` and `CODEX_READY` items through actual execution, PR, validation, merge and completion receipts. Find queue items whose apparent state no longer matches current main.

### 4. Agent incremental value

Compare API-agent/specialist outputs against deterministic baselines and no-agent alternatives. Measure whether model calls add unique decision/research value rather than duplicated prose.

### 5. Forecast-candidate hygiene

Audit duplicate candidates, maturity, scoring eligibility and frozen lineage. Avoid counting file copies as independent forecasts.

### 6. Architecture health truth

Use health objects as observability, then inspect their owners and evidence before inferring system quality.

### 7. Historical Research Vault

Use `historical_research_vault/` as the index and governed collection surface for replay-grade historical data. Reuse existing owner datasets before adding sources, keep bulk payloads out of ordinary Git history, and require source/license/storage admission before durable promotion.

## Current live seed from 2026-09-04

At the time this README was created, the root dashboard reported a large experiment/forecast/remediation backlog and an automation-health RED caused by `daily-slow-cycle-shadow.yml` latest/repeated failures.

**This is not frozen truth. Revalidate immediately from `LATEST_OPERATIONS_DASHBOARD.json` before using it as a mission.**

The durable lesson is the mission shape: prioritize root-cause closure and backlog compression before adding new experiments.

## Authority ceiling

Default mode is `READ_ONLY`.

Do not promote API output, specialist votes, experiment status or remediation metadata into market/portfolio authority.

If you find a reproducible bounded code defect, use the governed Codex/remediation intake rather than creating an ad-hoc patch path.

## Astra-class challenge

A stronger model should ask whether the research runtime has become too easy to grow and too hard to close.

High-value outcomes include:

- fewer duplicate candidates;
- clearer dependency graphs;
- evidence-backed retirement;
- better completion accounting;
- lower model/API cost for equivalent evidence quality;
- stronger separation between observability and authority.

See:

```text
../06_RESEARCH_LAB/README.md
historical_research_vault/README.md
codex/README.md
../07_PROMPTS_AND_AGENTS/astra/README.md
```
