# Investering Framework - Agent Operating Instructions

These instructions apply to all agent work in this repository.

## 1. Read order

Before framework, DATA PING, weekly operations, Cycle Navigator, Research Lab, archive, governance or automation work:

1. Read `00_ARCHIVE_CONTROL/CANONICAL_INDEX.md`.
2. Read `00_ARCHIVE_CONTROL/ARCHIVE_MAP_AND_ROUTING.md`.
3. Read `00_ARCHIVE_CONTROL/SKILL_REGISTRY.md`.
4. Load the relevant skill from `.agents/skills/`.
5. Read only the current canonical and operational files identified by those anchors.

Do not rely on conversation memory when repository sources are available.

## 2. Source and version governance

- The highest explicitly active DATA PING version wins.
- Newer operational patches override older conflicting documents in the same domain.
- Historical, legacy, superseded, shadow and source material remain context, not current authority.
- `DATA_MISSING` means `UNKNOWN`. It is not negative evidence.
- Source-backed claims are not outcome rows.
- Written governance is not functioning governance without behavior, valid rows or a documented blocked state.
- Never infer, interpolate or backfill missing market values unless a canonical rule explicitly permits it.

## 3. Framework roles

- DATA PING captures verified evidence and state.
- The main framework owns interpretation, permissions, action and ratification.
- Shadow and Research Lab challenge, test and learn. They do not self-promote.
- Master Monday is the weekly official synthesis after ratification.
- Cycle Navigator is public output and pre-registered accountability.
- GitHub is versioned memory and the governance control plane.

## 4. Current architecture constraints

- Tighten and simplify before expanding.
- Respect the active new-engine freeze.
- Do not create a new engine, shadow layer, scoring concept or duplicate forward test without an explicit canonical exception.
- Prefer rows, source-lineage repair, missing-data completion, reproducibility, retirement and compression over new theory.
- Keep BTC permission and alt permission as separate evidence lanes.
- No portfolio action may be produced from DATA PING alone.

## 5. Repository write safety

- Work on an isolated `agent/task-YYYYMMDD-short-purpose` branch.
- Use pull requests for canonical changes.
- Never force-push, rewrite history, delete backup branches or use backup branches as workspaces.
- Search before creating a file.
- Prefer updating or appending to the existing owner file over creating a duplicate document.
- Preserve historical files unless an approved retirement workflow applies.
- Follow `01_CORE_FRAMEWORK/governance/2026-07-11__repository-safety-and-backup-policy-v1__canonical.md` before any high-impact operation.
- Changing `00_ARCHIVE_CONTROL/CANONICAL_INDEX.md`, archive routing, precedence or source governance is high-impact and requires the policy safepoint sequence first.

## 6. Archive discipline

Classify material before writing:

- framework governance or architecture -> `01_CORE_FRAMEWORK/`
- DATA PING protocol or source QA -> `02_DATA_PING/`
- weekly operations or automation -> `03_WEEKLY_OPERATIONS/`
- market and regime learning -> `04_MARKET_LEARNING/`
- Cycle Navigator product -> `05_CYCLE_NAVIGATOR/`
- Research Lab synthesis or tests -> `06_RESEARCH_LAB/`
- prompts and agent workflows -> `07_PROMPTS_AND_AGENTS/`
- raw external evidence -> `08_SOURCE_MATERIAL/`
- unclear temporary material -> `09_ARCHIVE_INBOX/`

Archive the durable learning, not every intermediate conversation or report.

## 7. Validation before completion

Before declaring work complete:

- verify every referenced path exists;
- verify active versions against the canonical index;
- verify no legacy file was treated as current authority;
- verify output status and evidence status are explicit;
- verify no hidden interpolation or unsupported scoring occurred;
- verify the diff contains only intended files;
- report unresolved paths, blocked data and manual interventions honestly.

## 8. Skill composition

Default composition order:

1. `canonical-context-router` to resolve current authority.
2. The task-specific workflow.
3. `archive-governance` before any repository write.
4. `research-lab-red-team` when evaluating a framework claim, proposal or external model output.

Skills define procedure. Canonical repository files define current truth. A skill must never become a parallel source of market rules.