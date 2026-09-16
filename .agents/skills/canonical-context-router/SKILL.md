---
name: canonical-context-router
description: 'Resolve the current authoritative Investering framework context before analysis or execution. Use for framework, DATA PING, Master Monday, Cycle Navigator, kompas, handlekompas, compass, governance, active-version, current-rule, precedence, or cross-domain questions. Differentiator: identifies the canonical owner files, registered index addenda and overrules before any task-specific reasoning begins.'
---

# Canonical Context Router

## Purpose

Build a small, verified context packet from the repository's current authority structure. Do not solve the market or framework task inside this skill. Resolve what is current, what is historical, what conflicts, and which files the next step must read.

## Cross-repository preflight

Read `00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md` and `00_ARCHIVE_CONTROL/CROSS_REPO_AGENT_CONTEXT_MAP.json`. The public repository is the control plane; `Donh91/secrets` is the restricted data plane; credentials remain outside repo files. When a route requires restricted evidence, resolve the authorized private commit/path/hash binding or return `PRIVATE_DATA_AUTHORITY_UNAVAILABLE`. Never search the control plane for missing private values or use `Donh91/Cycle-navigator-` as a current route.

## Mandatory read order

1. Read `AGENTS.md`.
2. Read `00_ARCHIVE_CONTROL/2026-09-14__autonomous-data-authority-transition-v1__canonical.md`.
3. Read `00_ARCHIVE_CONTROL/CURRENT_PRODUCTION_DATA_AUTHORITY.json`.
4. Read `00_ARCHIVE_CONTROL/CANONICAL_INDEX.md`.
5. Read `00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md`.
6. Read `00_ARCHIVE_CONTROL/ARCHIVE_MAP_AND_ROUTING.md`.
7. Read `00_ARCHIVE_CONTROL/SKILL_REGISTRY.md`.
8. Read `00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md`.
9. Read `00_ARCHIVE_CONTROL/CROSS_REPO_AGENT_CONTEXT_MAP.json`.
10. Identify the task domain and data classification.
11. Read the current owner files named by the current routing surfaces, index or registered addenda for that domain.
12. Read the exact restricted-plane authority when required and authorized.
13. Read only directly relevant addenda, ledgers and runtime registries.

The 2026-09-14 autonomous-data transition owner supersedes older archive/index prose only for **current production data routing**. Historical sections remain valid for frozen historical periods.

Do not load the entire archive by default.

## Domain routing

Use these primary domains:

```text
framework architecture or governance -> 01_CORE_FRAMEWORK
DATA PING protocol, explicit packet interpretation, replay or source QA -> 02_DATA_PING
Master Monday, weekly operations, ledgers or automation -> 03_WEEKLY_OPERATIONS
market learning or calibration -> 04_MARKET_LEARNING
Cycle Navigator -> 05_CYCLE_NAVIGATOR
Research Lab, forward tests or audits -> 06_RESEARCH_LAB
prompts and agent workflows -> 07_PROMPTS_AND_AGENTS
external evidence -> 08_SOURCE_MATERIAL
```

### Current production data route

When `current_state_required: YES` for Master Monday, Cycle Navigator, the CN website, short-horizon navigation, or general market-state work, route in this order:

```text
LATEST_OPERATIONS_DASHBOARD.json / LATEST_HANDOFF.json
-> exact current autonomous pointer(s), path(s), hash(es), receipt(s)
-> current domain machine output / pointer
-> main-framework accepted interpretation or ratification
-> consumer output (Master Monday / Cycle Navigator / public surface)
```

Manual DATA PING submission is not a prerequisite for this route.

A file or path containing `DATA_PING`, `data_ping_derived`, `latest`, or an old version identifier is not current merely because of its name. Require an explicit current operational pointer to route to it.

For `NEXT DAYS` or another short-horizon public field, use an existing current autonomous canonical output only when fresh, eligible and public-safe. If no such output exists, the correct result is unavailable/not published. Do not create a parallel website forecast engine.

### Global Action Compass route - all Investering threads

When the normalized user request is exactly `kompas`, `handlekompas` or `compass`, or one of those words is clearly the primary imperative, classify it as:

```yaml
task_type: GLOBAL_ACTION_COMPASS
current_state_required: YES
global_compass_invocation: YES
explicit_data_ping_or_raw_packet_input: NO
```

Then include these files under `Required files`:

```text
07_PROMPTS_AND_AGENTS/action_compass/2026-09-16__global-action-compass-invocation-contract-v1__canonical.md
07_PROMPTS_AND_AGENTS/action_compass/GLOBAL_ACTION_COMPASS_ROUTE_v1.json
02_DATA_PING/protocols/2026-08-25__three-horizon-action-compass-output-contract-v1__canonical.md
```

The global contract supplies invocation, current-state routing and text-only rendering rules. The Three-Horizon contract supplies the controlled action and altcoin-regime vocabulary. A plain compass invocation is not a fresh DATA PING ingest and does not create a new prospective receipt merely because it was rendered.

The downstream answer must use the current autonomous production route, keep the human-facing compass compact and text-only, add ETA where actionable, and avoid intentionally rendering widgets, API cards, connector cards, interactive charts, raw JSON or tool output.

Do not ask the user which thread, DATA PING version, workflow or agent they mean when a hard trigger is present.

### Mandatory DATA PING / RAW interpretation route - explicit packet tasks only

When `task_type` is specifically Main-Framework interpretation of a DATA PING packet or RAW market-data ingest, including a replay, correction, replacement thread or future DATA PING version, the context packet must include this owner under `Required files`:

`02_DATA_PING/protocols/2026-08-25__three-horizon-action-compass-output-contract-v1__canonical.md`

This route is mandatory for that explicit packet task even if the same contract was used in a prior thread. Do not satisfy it from conversation memory or inherited prose. Resolve the file from current GitHub state and honor explicit supersession if a newer canonical owner replaces it.

This explicit packet rule does not restore DATA PING as the normal upstream production feed for current Master Monday or Cycle Navigator.

The router itself does not make the portfolio decision. It guarantees that the downstream Main Framework receives the applicable decision-translation contract for the explicit packet task.

## Authority resolution

Apply this order unless a newer canonical file explicitly changes it:

```text
CURRENT-STATE TASKS
1. Current operational cockpit and exact hash-bound autonomous pointers/outputs.
2. Main-framework accepted canonical state and runtime configuration.
3. Current canonical methodology/governance needed to interpret those outputs.
4. User-verified actuals that are explicitly eligible under the active owner.
5. Historical DATA PING / source / shadow / challenger context.
6. Legacy or memory-only context.

EXPLICIT DATA PING / RAW PACKET TASKS
1. Current repository authority and applicable packet contract.
2. The explicit verified packet/RAW input being interpreted.
3. Main-framework accepted canonical state and runtime configuration.
4. Current GitHub canonical governance and archive history.
5. Shadow/challenger context.
6. Legacy or memory-only context.
```

Within one domain:

- highest explicitly active version wins only within the task class it actually governs;
- newer operational patches override older conflicting files;
- current autonomous pointer/output beats historical feed descriptions for current-state routing;
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
explicit_data_ping_or_raw_packet_input: YES | NO
global_compass_invocation: YES | NO
```

### 2. Discover authority

Find:

- current production-data routing owner;
- current operational pointer/output when current state is required;
- canonical owner file;
- active version or runtime registry;
- directly index-listed addenda;
- registry-discoverable addenda for the domain;
- open ledger or forward-test state when applicable;
- any explicit supersession or overrule;
- required source material.

For every registry-discoverable addendum, verify the path and its declared owner before using it.

For a global compass invocation, additionally verify that both the Global Action Compass contract and its machine route are present in `Required files`, along with the active Three-Horizon decision vocabulary owner. Treat it as a current-state route and set render-only receipt behavior to `NO_NEW_RECEIPT` unless the same turn separately contains a fresh eligible ingest.

For explicit DATA PING / RAW Main-Framework interpretation, additionally verify that the Three-Horizon Action Compass owner is present in `Required files`; absence is a routing failure, not an optional omission. The owner is the sole current decision vocabulary for that task class, separates warning from action and requires one immutable receipt attempt for each fresh explicit ingest. The historical E0-E7 Exit Ladder is `RETIRED_UNIMPLEMENTED` and must not be routed as a current owner.

### 3. Separate state classes

Classify every material file used as one of:

```text
CANONICAL_CURRENT
OPERATIONAL_CURRENT
EXPLICIT_PACKET_INPUT
SHADOW_ONLY
FORWARD_TEST
SOURCE_MATERIAL
LEGACY
SUPERSEDED
UNKNOWN_STATUS
```

Never silently promote an unknown, historical DATA PING, or shadow file.

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
Current production route:
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
- Do not treat historical/manual DATA PING as the default upstream source for current CN or Master Monday.
- Do not classify a DATA PING-named or `latest_master_monday.json` artifact as current without a current pointer binding.
- Do not ask for thread/version clarification on a hard global compass trigger.
- Do not route a plain global compass render request as a fresh prospective ingest.
- Do not intentionally render widgets or raw tool/API output in the downstream global compass answer.
- Do not omit the Three-Horizon Action Compass owner from an explicit DATA PING / RAW Main-Framework interpretation context packet.
- Do not route the retired E0-E7 Exit Ladder as current decision vocabulary or map Action Compass warnings into it.
- Do not treat a replay, duplicate or `NOT_PERSISTED` interpretation as a new prospective receipt row.
- Do not create a short-horizon or market-state engine in the public website to compensate for a missing current autonomous field.

## Validation loop

Before completing:

1. Verify the current production-data transition owner exists.
2. Verify every listed required path exists.
3. When current state is requested, verify the exact current operational pointer/path/hash chain.
4. Verify active versions against the canonical index or runtime registry while respecting explicit routing supersessions.
5. Verify every used registered addendum exists and points to valid owner files.
6. Verify no legacy or superseded file is presented as current.
7. Verify all unresolved conflicts are explicit.
8. For a global compass invocation, verify the Global Action Compass canonical contract, machine route and active Three-Horizon decision vocabulary owner are all present, and verify the downstream visible-output policy is `TEXT_ONLY` with no render-only receipt.
9. For explicit DATA PING / RAW Main-Framework interpretation, verify `02_DATA_PING/protocols/2026-08-25__three-horizon-action-compass-output-contract-v1__canonical.md` or its explicit canonical successor is included in `Required files`, and record whether the input is fresh or replayed for receipt routing.
10. Re-read the request and confirm the packet contains only task-relevant context.

If any check fails, correct the packet and re-run all checks.

## Failure modes

- **Current production-data owner missing** -> stop and report `CURRENT_DATA_AUTHORITY_UNAVAILABLE`.
- **Index path missing** -> stop and report `CANONICAL_INDEX_UNAVAILABLE`.
- **Addendum registry missing** -> report `ADDENDUM_REGISTRY_UNAVAILABLE` and use only directly index-listed material plus explicit current routing owners.
- **Registered addendum missing** -> report `ADDENDUM_PATH_MISSING` and do not use it.
- **Owner file missing** -> report exact missing path and `OWNER_FILE_MISSING`.
- **Global compass contract or machine route missing** -> report `GLOBAL_ACTION_COMPASS_ROUTE_UNAVAILABLE`; do not substitute old thread prose.
- **Required DATA PING action-compass owner missing or unresolved for an explicit packet task** -> report `ACTION_COMPASS_OWNER_UNAVAILABLE`; do not silently fall back to prior-thread wording.
- **Two current canonical files conflict** -> report `UNRESOLVED_CANONICAL_CONFLICT`.
- **Requested live state has no current registry/pointer** -> report `LIVE_STATE_NOT_VERIFIED`.
- **Only historical DATA PING route found for a current-state request** -> report `CURRENT_AUTONOMOUS_ROUTE_NOT_RESOLVED`; do not promote the historical packet.
- **Search finds only legacy material** -> provide historical context only and state that no current authority was found.

## Pilot review

The skill remains useful only if it reduces wrong-version use, missed addenda, legacy reactivation and unnecessary archive loading. Review under `00_ARCHIVE_CONTROL/SKILL_REGISTRY.md` after the pilot gate.