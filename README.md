# Investering Framework Archive v1

Dette repository fungerer som udvidet canonical projektarkiv og operationelt control plane for Investering-frameworket.

Det er ikke kun backup. Det er versioneret hukommelse, governance, runtime-routing, research-accountability og agent-kontekst.

## New model / agent entrypoint

A repository-aware model must not wait for a chat-specific mission before it can understand the system.

Start every fresh repository session here:

```text
1. AGENTS.md
2. LATEST_OPERATIONS_DASHBOARD.json
3. LATEST_HANDOFF.json
4. 00_ARCHIVE_CONTROL/CANONICAL_INDEX.md
5. 00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md
6. 00_ARCHIVE_CONTROL/ARCHIVE_MAP_AND_ROUTING.md
7. 00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md
8. 00_ARCHIVE_CONTROL/CROSS_REPO_AGENT_CONTEXT_MAP.json
9. the README.md in the domain folder you enter
10. the exact current owner/status/receipt named by those routing surfaces
```

Folder `README.md` files are **navigation and mission cards, not independent authority**. They tell a capable model what the folder owns, where current truth lives, what questions are worth challenging, and what authority ceiling applies. Canonical owners, current machine pointers and verified receipts always win over README prose.

For Astra or any successor model with materially stronger long-horizon engineering/research capability, also read:

```text
07_PROMPTS_AND_AGENTS/astra/README.md
07_PROMPTS_AND_AGENTS/astra/ASTRA_REPOSITORY_MISSION_ROUTER_v1.json
```

The intended behavior is:

```text
UNDERSTAND THE REPOSITORY
-> RECONSTRUCT CURRENT AUTHORITY
-> WALK DOMAIN READMES
-> CHALLENGE THE EXISTING PLAN
-> PROPOSE THE HIGHEST-VALUE MISSION SEQUENCE
-> REMAIN READ-ONLY UNTIL THE APPLICABLE AUTHORITY GATE IS SATISFIED
```

Do not treat model capability as permission.

## Permanent safety invariant

The canonical owner is:

```text
01_CORE_FRAMEWORK/governance/2026-07-11__repository-safety-and-backup-policy-v1__canonical.md
```

Permanent mnemonic:

```text
IMPROVE THE AIRCRAFT.
PROTECT THE PARACHUTE.
NEVER HOLD BOTH DESTRUCTIVE KEYS.
```

No autonomous or semi-autonomous principal may simultaneously hold source-destructive and recovery-destructive authority. No future "golden key", benchmark score or model identity overrides that rule.

## Mandatory cross-repository boundary

```text
CONTROL PLANE: Donh91/Investering-Framework-Archive-v1
RESTRICTED DATA PLANE: Donh91/secrets
CREDENTIAL PLANE: GitHub Actions Secrets or an explicitly approved runtime secret manager/workload identity
```

`Donh91/secrets` stores restricted data and receipts, not passwords as repository files. Raw/private values never return to this public repository. If private authority is required but unavailable, report that state. Do not infer the missing values.

## Repository structure

Canonical archive domains:

```text
00_ARCHIVE_CONTROL/
01_CORE_FRAMEWORK/
02_DATA_PING/
03_WEEKLY_OPERATIONS/
04_MARKET_LEARNING/
05_CYCLE_NAVIGATOR/
06_RESEARCH_LAB/
07_PROMPTS_AND_AGENTS/
08_SOURCE_MATERIAL/
changelog/
```

Important active operational surfaces also include:

```text
00_FMOS/
03_DAILY_CAPTURE_LOGS/
09_SOURCE_QA/
research/
scripts/
tests/
.github/
```

Do not infer current authority from folder numbering alone. Some historical/legacy directories remain intentionally preserved.

## Never hard-code current operational state here

This README intentionally does **not** freeze the current DATA PING version, market state, active incident, gate, recovery state, forecast state or portfolio action.

Those change faster than this document. Resolve them from current repository evidence, beginning with:

```text
LATEST_OPERATIONS_DASHBOARD.json
LATEST_HANDOFF.json
research/architecture_health/LATEST_AUTOMATION_HEALTH.json
research/architecture_health/LATEST_ARCHITECTURE_HEALTH.json
LATEST_REMEDIATION_QUEUE.json
LATEST_CODEX_READY_TASKS.json
LATEST_CODEX_EXECUTION_STATE.json
```

Then follow the exact domain pointers and hash-bound receipts they reference.

Historical handoff files may remain valid history while no longer representing the newest runtime generation. `latest` is not automatically `canonical`, and a filename containing `latest` is not authority without its governing contract.

## Core precedence rule

```text
Newer valid canonical authority overrides older conflicting archive assumptions.
Current verified machine state overrides stale navigation prose.
Missing or unavailable data remains UNKNOWN, never inferred negative evidence.
```

Older files are not automatically wrong. They may be historical, legacy, source material, receipts or superseded owners.

## Folder-mission principle

When a capable model enters a domain folder, it should ask four questions before doing anything:

```text
1. What does this folder own?
2. What file is current authority right now?
3. What evidence would falsify or improve the current system?
4. What am I NOT authorized to change?
```

A folder README may contain mission seeds. Those are hypotheses for useful work, not permission and not a frozen priority queue. A stronger model is expected to challenge them and propose a better sequence if the repository evidence supports it.

## Archive principle

```text
Raw inputs are evidence.
Distilled notes are archive.
Canonical notes are rules.
Index entries are navigation.
Machine pointers are current-state routing, not doctrine by themselves.
Receipts prove executed state, not scientific validity by themselves.
```

The goal is not to save everything. The goal is to preserve what future framework runs must understand, reproduce, challenge and safely improve.
