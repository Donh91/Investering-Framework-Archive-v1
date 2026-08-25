---
name: canonical-context-router
description: 'Resolve the current authoritative Investering framework context before analysis or execution. Use for framework, DATA PING, Master Monday, Cycle Navigator, governance, active-version, current-rule, precedence, or cross-domain questions. Differentiator: identifies the canonical owner files, registered index addenda and overrules before any task-specific reasoning begins.'
---

# Canonical Context Router

## Purpose

Build a small, verified context packet from the repository's current authority structure. Do not solve the market or framework task inside this skill. Resolve what is current, what is historical, what conflicts, and which files the next step must read.

## Cross-repository preflight

Read `00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md` and `00_ARCHIVE_CONTROL/CROSS_REPO_AGENT_CONTEXT_MAP.json`. The public repository is the control plane; `Donh91/secrets` is the restricted data plane; credentials remain outside repo files. When a route requires restricted evidence, resolve the authorized private commit/path/hash binding or return `PRIVATE_DATA_AUTHORITY_UNAVAILABLE`. Never search the control plane for missing private values or use `Donh91/Cycle-navigator-` as a current route.

## Mandatory read order

1. Read `AGENTS.md`.
2. Read `00_ARCHIVE_CONTROL/CANONICAL_INDEX.md`.
3. Read `00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md`.
4. Read `00_ARCHIVE_CONTROL/ARCHIVE_MAP_AND_ROUTING.md`.
5. Read `00_ARCHIVE_CONTROL/SKILL_REGISTRY.md`.
6. Read `00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md`.
7. Read `00_ARCHIVE_CONTROL/CROSS_REPO_AGENT_CONTEXT_MAP.json`.
8. Identify the task domain and data classification.
9. Read the current owner files named by the index or registered addenda for that domain.
10. Read the exact restricted-plane authority when required and authorized.
11. Read only directly relevant addenda, ledgers and runtime registries.

Do not load the entire archive by default.

## Domain routing

Use these primary domains:

```text
framework architecture or governance -> 01_CORE_FRAMEWORK
DATA PING protocol, runtime or source QA -> 02_DATA_PING
Master Monday, weekly operations, ledgers or automation -> 03_WEEKLY_OPERATIONS
market learning or calibration -> 04_MARKET_LEARNING
Cycle Navigator -> 05_CYCLE_NAVIGATOR
Research Lab, forward tests or audits -> 06_RESEARCH_LAB
prompts and agent workflows -> 07_PROMPTS_AND_AGENTS
external evidence -> 08_SOURCE_MATERIAL
```

### Mandatory DATA PING / RAW interpretation route

When `task_type` is Main-Framework interpretation of a DATA PING packet or RAW market-data ingest, including a replay, correction, replacement thread or future DATA PING version, the context packet must always include this owner under `Required files`:

`02_DATA_PING/protocols/2026-08-25__three-horizon-action-compass-output-contract-v1__canonical.md`

This route is mandatory even if the same contract was used in a prior thread. Do not satisfy it from conversation memory or inherited prose. Resolve the file from current GitHub state and honor explicit supersession if a newer canonical owner replaces it.

The router itself does not make the portfolio decision. It guarantees that the downstream Main Framework receives the current decision-translation contract and therefore can produce the required three-lane `HANDLEKOMPAS` after analysis.

## Authority resolution

Apply this order unless a newer canonical file explicitly changes it:

```text
1. User-verified actuals and verified DATA PING truth-layer
2. Main-framework accepted canonical state and runtime configuration
3. Current GitHub canonical governance and archive history
4. Grok shadow context
5. Claude or Research Lab challenger context
6. Legacy or memory-only context
```

Within one domain:

- highest explicitly active version wins;
- newer operational patches override older conflicting files;
- canonical beats shadow;
- runtime state does not rewrite permanent methodology;
- source material supports claims but does not become doctrine;
- legacy and superseded files remain historical context only;
- an index-addendum registry entry is a discovery pointer, not independent authority.

## Workflow

### 1. Parse the request

Extract:

```yaml
task_type:
domain:
time_horizon:
requested_action:
write_intent: YES | NO
current_state_required: YES | NO
historical_context_required: YES | NO
```

### 2. Discover authority

Find:

- canonical owner file;
- active version or runtime registry;
- directly index-listed addenda;
- registry-discoverable addenda for the domain;
- open ledger or forward-test state when applicable;
- any explicit supersession or overrule;
- required source material.

For every registry-discoverable addendum, verify the path and its declared owner before using it.

For DATA PING / RAW Main-Framework interpretation, additionally verify that the Three-Horizon Action Compass owner is present in `Required files`; absence is a routing failure, not an optional omission.

### 3. Separate state classes

Classify every material file used as one of:

```text
CANONICAL_CURRENT
OPERATIONAL_CURRENT
SHADOW_ONLY
FORWARD_TEST
SOURCE_MATERIAL
LEGACY
SUPERSEDED
UNKNOWN_STATUS
```

Never silently promote an unknown or shadow file.

### 4. Resolve conflicts

For each conflict, record:

```yaml
claim_or_rule:
winning_file:
losing_file:
reason:
operational_effect:
```

If the repository does not resolve the conflict, mark `UNRESOLVED_CANONICAL_CONFLICT`. Do not guess.

### 5. Produce the context packet

Return:

```markdown
## CONTEXT PACKET

Task domain:
Current owner:
Active version or runtime:
Required files:
Index-listed addenda:
Registry-discoverable addenda:
Relevant ledgers:
Explicit overrules:
Historical context allowed:
Missing or unresolved:
Write-safety requirement:
Next skill or workflow:
```

Keep the packet concise. Reference paths rather than copying whole documents.

## Hard rules

- Do not make portfolio decisions.
- Do not infer missing market values.
- Do not treat `DATA_MISSING` as bearish evidence.
- Do not create or modify files.
- Do not declare a rule active because it is merely written or registered.
- Do not use conversation memory as a substitute for repository verification.
- Do not treat a source-backed claim row as an outcome row.
- Do not use a legacy namespace when the active top-level namespace exists.
- Do not use a broken or missing addendum pointer.
- Do not omit the Three-Horizon Action Compass owner from a DATA PING / RAW Main-Framework interpretation context packet.

## Validation loop

Before completing:

1. Verify every listed required path exists.
2. Verify active versions against the canonical index or runtime registry.
3. Verify every used registered addendum exists and points to valid owner files.
4. Verify no legacy or superseded file is presented as current.
5. Verify all unresolved conflicts are explicit.
6. For DATA PING / RAW Main-Framework interpretation, verify `02_DATA_PING/protocols/2026-08-25__three-horizon-action-compass-output-contract-v1__canonical.md` or its explicit canonical successor is included in `Required files`.
7. Re-read the request and confirm the packet contains only task-relevant context.

If any check fails, correct the packet and re-run all checks.

## Failure modes

- **Index path missing** -> stop and report `CANONICAL_INDEX_UNAVAILABLE`.
- **Addendum registry missing** -> report `ADDENDUM_REGISTRY_UNAVAILABLE` and use only directly index-listed material.
- **Registered addendum missing** -> report `ADDENDUM_PATH_MISSING` and do not use it.
- **Owner file missing** -> report exact missing path and `OWNER_FILE_MISSING`.
- **Required DATA PING action-compass owner missing or unresolved** -> report `ACTION_COMPASS_OWNER_UNAVAILABLE`; do not silently fall back to prior-thread wording.
- **Two current canonical files conflict** -> report `UNRESOLVED_CANONICAL_CONFLICT`.
- **Requested live state has no current registry** -> report `LIVE_STATE_NOT_VERIFIED`.
- **Search finds only legacy material** -> provide historical context only and state that no current authority was found.

## Pilot review

The skill remains useful only if it reduces wrong-version use, missed addenda, legacy reactivation and unnecessary archive loading. Review under `00_ARCHIVE_CONTROL/SKILL_REGISTRY.md` after the pilot gate.
