---
name: archive-governance
description: 'Classify, place, update, index, and validate Investering framework material in GitHub. Use when the user says archive, save, preserve, add to GitHub, make canonical, update the archive, place this correctly, or asks whether something belongs in project sources. Differentiator: searches for the existing owner first and enforces duplication, precedence, explicit-branch, safepoint, addendum-registry, incident, backup-scope, and receipt rules before writing.'
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
00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md
00_ARCHIVE_CONTROL/ARCHIVE_MAP_AND_ROUTING.md
00_ARCHIVE_CONTROL/SKILL_REGISTRY.md
01_CORE_FRAMEWORK/governance/2026-07-11__repository-safety-and-backup-policy-v1__canonical.md
01_CORE_FRAMEWORK/governance/2026-07-11__external-vault-activation-and-snapshot-contract-v1-1__canonical.md
```

When a source is a Word, PowerPoint, Excel, OpenDocument, RTF, EPUB, CSV or otherwise unreadable supported document, also read:

```text
07_PROMPTS_AND_AGENTS/github_agent/2026-08-05__anydoc-agent-document-normalization-v1__operational.md
```

## Write authorization gate

Classify the request:

```yaml
write_intent: EXPLICIT | NOT_EXPLICIT
operation: CREATE | UPDATE | APPEND | INDEX | MOVE | DELETE | NO_WRITE
impact: LOW | HIGH | UNKNOWN
```

If write intent is not explicit, return a recommendation only. Do not mutate the repository.

## Mandatory branch assertion

Before every `create_file`, `update_file` or `delete_file` call, verify:

```yaml
target_branch_explicitly_supplied: YES
target_branch_verified_to_exist: YES
target_branch_is_default_branch: NO
target_branch_is_backup_branch: NO
target_branch_pattern: agent/task-YYYYMMDD-short-purpose
write_path:
write_operation:
```

Rules:

- Never omit the branch argument.
- Never rely on a connector's default branch behavior.
- Never use `main`, `master`, another default branch or any `backup-safepoint/*` branch as the write target.
- Never create a placeholder, probe or test file in a production repository to discover tool behavior.
- Tool capability must be learned from schemas, read-only calls or an isolated disposable repository, not by mutating canonical history.

If the assertion cannot be completed, stop with:

```text
WRITE_BRANCH_UNVERIFIED
```

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

### 1.5 Normalize unreadable documents before classification

Use document normalization only to expose source contents for inspection. It does not change source authority.

For supported non-PDF documents, use:

```bash
python scripts/document_ingestion/anydoc_ingest.py \
  --input <source> \
  --output-dir <temporary-output-directory>
```

Rules:

- The wrapper pins `@firecrawl/anydoc@0.1.3` and requires Node 20+ when no explicit binary is supplied.
- Preserve the original source as primary evidence and retain its SHA-256 in the generated manifest.
- Treat `document.md` as a convenience representation, not canonical truth.
- For large documents, read only relevant Markdown sections into context.
- PDF input defaults to the existing `scripts/pdf_ingestion/pdf_ingest.py` specialist route.
- Use `--allow-pdf-fallback` only deliberately. A PDF fallback remains `DEGRADED` because it lacks the separate layout, OCR and page-level receipt.
- Scanned or image-only PDFs require OCR or vision. Never infer missing text.
- Do not auto-commit the raw source, generated Markdown or receipt.
- Conversion output is not an evidence outcome row and cannot promote itself.

If conversion fails, is empty or returns `BLOCKED`, preserve the source and report the exact failure. Do not silently substitute model knowledge.

### 2. Search before writing

Search by:

- exact named concept;
- synonyms;
- proposed title;
- domain keywords;
- known owner files;
- current index, addendum registry and addenda.

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
- verify the branch before every write;
- make only intended changes;
- validate paths and content;
- use a pull request;
- merge only after validation and review.

### 6. Indexing and addendum registration

Canonical, operationally important and governance-relevant files must be discoverable.

Preferred options:

1. update an existing owner or registry already referenced by the index;
2. create or update an `00_ARCHIVE_CONTROL/*index-addendum*.md` when a safe addendum is sufficient;
3. register every valid addendum in `00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md`;
4. modify `CANONICAL_INDEX.md` only after the high-impact safepoint workflow.

An addendum update is incomplete until its registry row is verified. Never bypass the safety policy merely to improve discoverability.

### 7. Backup-scope truth

For every backup reference, record:

```yaml
backup_product: FULL_GIT_MIRROR | CANONICAL_SNAPSHOT | TARGETED_SNAPSHOT | DELTA_SNAPSHOT | NONE
snapshot_frozen_source_sha:
current_owner_or_merge_sha:
current_version_in_snapshot: YES | NO | PARTIAL | UNKNOWN
post_merge_delta_status: PASS | PENDING | NOT_REQUIRED | UNKNOWN
paths_expected:
paths_verified:
```

Rules:

- A pre-merge targeted snapshot does not prove that later owner, addendum or receipt updates are backed up.
- Separate `RESEARCH_PACKAGE_BACKUP` from `CURRENT_OWNER_VERSION_BACKUP`.
- Never call a targeted snapshot a full canonical snapshot or Git mirror.
- If the current merged version is absent, report `CURRENT_OWNER_VERSION_BACKUP: PENDING_POST_MERGE_DELTA`.

## Required decision manifest

Before writing, produce internally or in the PR body:

```yaml
archive_decision:
classification:
primary_owner:
operation:
target_branch:
branch_assertion: PASS | FAIL
paths_created:
paths_updated:
paths_deleted:
canonical_index_change: YES | NO
addendum_registry_change: YES | NO | NOT_APPLICABLE
high_impact_gate: PASS | NOT_REQUIRED | BLOCKED
duplicate_check:
source_lineage:
backup_scope:
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
6. Verify every write used the explicit verified task branch.
7. Verify every addendum is represented correctly in the addendum registry.
8. Verify high-impact policy compliance.
9. Verify backup claims against frozen and current SHAs.
10. Verify the PR diff matches the decision manifest.
11. Write an implementation receipt when the change is operationally important.

A failed check requires correction and a complete re-run.

## Incident-aware result classification

Use separate fields:

```yaml
archive_content_result: PASS | PARTIAL | FAIL
write_governance_result: PASS | PARTIAL_REMEDIATED | FAIL
final_repository_state: PASS | PARTIAL | FAIL
incident_count: integer
incident_paths: []
remediation_commits: []
```

A write to a default branch, a missing branch assertion, an unintended path or a placeholder write prevents an unqualified write-governance `PASS`, even when remediated immediately.

The final repository state may still be `PASS` after transparent remediation, but the incident remains part of the pilot evidence.

## Hard rules

- No repository write without explicit user intent.
- No write call without an explicit verified non-default task branch.
- No direct push to canonical `main`.
- No placeholder or connector-probe files in production repositories.
- No force operations.
- No hidden deletion, movement or replacement.
- No claim of canonical promotion without evidence.
- No automatic conversion of conversation text into doctrine.
- No full Git mirror claim from a selected-file snapshot.
- No claim that a pre-merge snapshot contains post-merge changes.
- No secrets, tokens or personal data in skill or archive files.

## Failure modes

- **Existing owner found** -> update or append instead of creating a new owner.
- **Branch argument absent or default** -> stop with `WRITE_BRANCH_UNVERIFIED`.
- **Placement unclear** -> use `09_ARCHIVE_INBOX/to_classify` only temporarily and record the unresolved routing question.
- **Canonical evidence insufficient** -> store as shadow, forward test, source note or reject.
- **Addendum not registered** -> report `ADDENDUM_NOT_REGISTERED`; do not claim global discoverability.
- **Index update needed but safety gate not run** -> create no index modification; report exact required safepoint sequence.
- **Backup frozen SHA predates current owner** -> report `PENDING_POST_MERGE_DELTA`.
- **Write result cannot be read back** -> report `WRITE_VERIFICATION_FAIL` and do not claim completion.

## Pilot review

The skill must reduce duplicates, wrong placement, missed addenda, unsafe writes and unsupported promotion. It should be modified or killed if it creates additional archive inflation or manual correction.
