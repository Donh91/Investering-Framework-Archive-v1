---
name: archive-governance
description: 'Classify, place, update, index, and validate Investering framework material in GitHub. Use when the user says archive, save, preserve, add to GitHub, make canonical, update the archive, place this correctly, or asks whether something belongs in project sources. Differentiator: searches for the existing owner first and enforces duplication, precedence, branch, safepoint, and receipt rules before writing.'
---

# Archive Governance

## Purpose

Govern repository writes so the archive remains searchable, non-duplicative, versioned and honest. This skill may prepare or execute writes only when the user has explicitly asked for repository changes.

## Required composition

Run `canonical-context-router` first for framework-related material.

Before writing, read:

```text
AGENTS.md
00_ARCHIVE_CONTROL/CANONICAL_INDEX.md
00_ARCHIVE_CONTROL/ARCHIVE_MAP_AND_ROUTING.md
00_ARCHIVE_CONTROL/SKILL_REGISTRY.md
01_CORE_FRAMEWORK/governance/2026-07-11__repository-safety-and-backup-policy-v1__canonical.md
01_CORE_FRAMEWORK/governance/2026-07-11__external-vault-activation-and-snapshot-contract-v1-1__canonical.md
```

## Write authorization gate

Classify the request:

```yaml
write_intent: EXPLICIT | NOT_EXPLICIT
operation: CREATE | UPDATE | APPEND | INDEX | MOVE | DELETE | NO_WRITE
impact: LOW | HIGH | UNKNOWN
```

If write intent is not explicit, return a recommendation only. Do not mutate the repository.

## Classification workflow

### 1. Extract the durable unit

Separate:

- raw source;
- temporary discussion;
- operational row;
- calibration note;
- forward-test specification;
- canonical learning;
- governance rule;
- implementation receipt.

Archive the smallest durable unit that preserves decision value.

### 2. Search before writing

Search by:

- exact named concept;
- synonyms;
- proposed title;
- domain keywords;
- known owner files;
- current index and addenda.

Determine:

```text
NEW_INFORMATION
EXISTING_OWNER_UPDATE
DUPLICATE
CONFLICT
SOURCE_ONLY
NOT_ARCHIVE_WORTHY
```

Prefer updating or appending to the existing owner file. Do not create a parallel canonical document when an owner already exists.

### 3. Choose status

Use only justified statuses:

```text
CANONICAL
OPERATIONAL
SHADOW_ONLY
FORWARD_TEST
SOURCE_NOTE
LEGACY
SUPERSEDED
RECEIPT
REJECTED_FROM_ARCHIVE
```

A strong explanation is not sufficient for canonical status.

### 4. Choose location

Follow `ARCHIVE_MAP_AND_ROUTING.md`.

Reusable agent workflows belong primarily in:

```text
07_PROMPTS_AND_AGENTS/
```

Runtime-discoverable skill files belong in:

```text
.agents/skills/<skill-name>/SKILL.md
```

Their canonical registry belongs in:

```text
00_ARCHIVE_CONTROL/SKILL_REGISTRY.md
```

### 5. Apply repository safety

High-impact operations include changing:

- `00_ARCHIVE_CONTROL/CANONICAL_INDEX.md`;
- archive routing, precedence or source governance;
- GitHub workflows, security or backup configuration;
- repository-wide namespaces or more than policy thresholds.

Before high-impact work, execute the required safepoint and vault sequence. If that sequence cannot be verified, stop with `HIGH_IMPACT_SAFETY_GATE_BLOCKED`.

For normal additions:

- create an isolated task branch;
- make only intended changes;
- validate paths and content;
- use a pull request;
- merge only after validation and review.

### 6. Indexing decision

Canonical, operationally important and governance-relevant files must be discoverable.

Preferred options:

1. update an existing owner or registry already referenced by the index;
2. create an `00_ARCHIVE_CONTROL/*index-addendum*.md` when a safe addendum is sufficient;
3. modify `CANONICAL_INDEX.md` only after the high-impact safepoint workflow.

Never bypass the safety policy merely to improve discoverability.

## Required decision manifest

Before writing, produce internally or in the PR body:

```yaml
archive_decision:
classification:
primary_owner:
operation:
paths_created:
paths_updated:
paths_deleted:
canonical_index_change: YES | NO
high_impact_gate: PASS | NOT_REQUIRED | BLOCKED
duplicate_check:
source_lineage:
validation_plan:
```

## File standard

New archive documents should begin with:

```markdown
# Title

**Dato:** YYYY-MM-DD  
**Status:** ...  
**Område:** ...  
**Primary folder:** `...`  
**Related folders:** optional  
**Supersedes:** optional  
**Depends on:** optional
```

Use `YYYY-MM-DD__short-topic__status.md` naming where applicable.

## Validation loop

After writing:

1. Read back every created or updated file.
2. Verify exact paths and status labels.
3. Verify referenced paths exist.
4. Verify no unintended files changed.
5. Verify no duplicate owner was created.
6. Verify high-impact policy compliance.
7. Verify the PR diff matches the decision manifest.
8. Write an implementation receipt when the change is operationally important.

A failed check requires correction and a complete re-run.

## Hard rules

- No repository write without explicit user intent.
- No direct push to canonical `main`.
- No force operations.
- No hidden deletion, movement or replacement.
- No claim of canonical promotion without evidence.
- No automatic conversion of conversation text into doctrine.
- No full Git mirror claim from a selected-file snapshot.
- No secrets, tokens or personal data in skill or archive files.

## Failure modes

- **Existing owner found** -> update or append instead of creating a new owner.
- **Placement unclear** -> use `09_ARCHIVE_INBOX/to_classify` only temporarily and record the unresolved routing question.
- **Canonical evidence insufficient** -> store as shadow, forward test, source note or reject.
- **Index update needed but safety gate not run** -> create no index modification; report exact required safepoint sequence.
- **Write result cannot be read back** -> report `WRITE_VERIFICATION_FAIL` and do not claim completion.

## Pilot review

The skill must reduce duplicates, wrong placement and unsupported promotion. It should be modified or killed if it creates additional archive inflation or manual correction.