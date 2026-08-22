# Automation Orchestration Architecture v2

Status: ACTIVE OPERATIONAL AUTHORITY
Date: 2026-08-05
Scope: Donh91 GitHub framework repositories

## Purpose

This document defines the current execution, observability, remediation and agent-handoff order. It prevents scheduled jobs, health observers and code agents from becoming parallel sources of truth.

## Repository roles

- `Investering-Framework-Archive-v1` is the execution, evidence, governance and health control plane.
- `Eksperimenter-framework-` is a bounded experiment workspace and may not promote rules or canonical state into the main framework without explicit ratification and a governed handoff.
- `Cycle-navigator-` is a public product surface, not an independent market-state owner.

No repository may silently create a competing canonical pointer, model-weight authority or portfolio action.

## Mandatory agent read order

For automation, incident, GitHub Actions, API-agent, Codex or delivery work:

1. `LATEST_OPERATIONS_DASHBOARD.json`
2. `LATEST_HANDOFF.json`
3. `research/architecture_health/LATEST_AUTOMATION_HEALTH.json`
4. `research/architecture_health/LATEST_ARCHITECTURE_HEALTH.json`
5. `LATEST_REMEDIATION_QUEUE.json`
6. `LATEST_CODEX_READY_TASKS.json` when code remediation is relevant
7. `LATEST_CODEX_EXECUTION_STATE.json` when Codex or research-to-code handoff is relevant
8. `AGENTS.md`, canonical index, registries and the relevant skill
9. the exact workflow, receipt, pointer, run and job logs

Conversation memory and stale issue descriptions are not operational authority when these files exist.

## Daily observability order

Europe/Copenhagen:

```text
05:30 / 17:30  Automation Production Health
05:45 / 17:45  Remediation Maturation Controller
06:00 / 18:00  Operations Dashboard
```

The ordering is deliberate:

- Health reads actual workflow state and publishes the fleet report.
- Remediation matures the new health findings into observe, evidence, self-heal, Codex or framework-owner lanes.
- Dashboard reads both health and remediation outputs and exposes one combined cockpit.

The Remediation Maturation Controller additionally has a path-restricted event trigger for durable research-to-Codex intake, research transition receipts and research completion receipts. Those events do not wait for the normal daily cadence.

Cron ordering is not a finality guarantee. Each consumer must validate timestamp, contract and hash of its input and remain explicit when the newest upstream output is unavailable.

## Observer versus observed status

A health observer must not fail merely because the observed fleet is RED.

The observer workflow is successful when it:

- completed the audit,
- durably published the exact RED report,
- verified remote bytes,
- recorded or updated the incident channel.

The report and dashboard remain RED. The observer run remains successful. Failures in the observer itself are reserved for inability to audit, publish, read back or notify.

## Workflow lifecycle semantics

Technical execution health and intended workflow lifecycle are separate dimensions.

Supported lifecycle states are:

- `ACTIVE`: normal production or verification behavior; failures are evaluated normally.
- `EXPECTED_BLOCK`: an intentionally fail-closed workflow. It must be unscheduled, carry a durable reason, declare the UTC timestamp from which the lifecycle state became authoritative, declare expected exit code 78 and contain the matching exit contract. Historical runs before the lifecycle timestamp remain history and cannot be used to claim a post-declaration lifecycle violation.
- `PENDING_FIRST_EXPECTED_RUN`: a newly scheduled workflow that has not yet had an expected schedule opportunity. It remains visible without being mislabeled `NO_RUN_HISTORY`.
- `RETIRED`: historical registration state only; a still-scheduled retired local workflow is a configuration defect.

Lifecycle directives live with the workflow instead of in a parallel registry:

```text
# framework-lifecycle: EXPECTED_BLOCK
# framework-lifecycle-reason: <durable reason>
# framework-lifecycle-since: <UTC timestamp>
# framework-expected-exit: 78
```

Lifecycle state never converts a genuine active failure into success. Invalid lifecycle declarations, an `EXPECTED_BLOCK` workflow with a schedule, an invalid/missing lifecycle timestamp, a missing reason/exit contract, or a successful run after the expected-block lifecycle became authoritative remain actionable health defects.

## Remediation and Codex

`CODEX_READY` means the problem has sufficient evidence for a bounded code task. It does not mean that code has been changed or merged.

The controller publishes:

- `LATEST_REMEDIATION_QUEUE.json`
- `LATEST_CODEX_READY_TASKS.json`
- `LATEST_NEEDS_MORE_EVIDENCE.json`
- `LATEST_CODEX_EXECUTION_STATE.json` as observability only
- `research/codex/LATEST_CODEX_INTAKE_STATUS.json`
- `research/codex/CODEX_EXECUTION_LEDGER.jsonl`
- one deduplicated GitHub issue titled `CODEX READY REMEDIATION QUEUE`

`LATEST_CODEX_READY_TASKS.json` remains the only machine authority for work that is currently ready for Codex. The execution state and ledger are read-only observability surfaces and cannot promote a task.

### Research-to-Codex intake

Bounded code-remediation candidates may originate from Automation Production Health or from durable research intake. Research threads do not gain code authority and cannot set `CODEX_READY` directly.

The governed research path is:

```text
research finding
-> deduplicate against current Codex/remediation signatures
-> CODEX_RESEARCH_CANDIDATE_v1
-> isolated branch and PR
-> research/codex/intake/YYYY/MM/<candidate_id>.json on main
-> path-triggered Remediation Maturation Controller
-> CODEX_READY / NEEDS_MORE_EVIDENCE / DEDUPED_TO_HEALTH_TASK / REJECTED
```

The path trigger is event-driven. A candidate does not wait for the normal 05:45/17:45 maturation schedule after it lands on `main`. The normal schedule remains a reconciliation and recovery path.

Candidate contract authority is defined by `research/codex/CODEX_RESEARCH_CANDIDATE.schema.json` and `.agents/skills/codex-intake/SKILL.md`. A valid standalone research candidate must include bounded change scope, durable evidence, reproduction, positive and negative acceptance tests and explicit code-only authority. `EXPEDITED` changes queue ordering only.

If the candidate links to an active health signature, research evidence is attached to the existing task instead of creating duplicate remediation authority.

Each task must preserve:

- exact signature and source identity,
- a concrete objective and fresh-state precondition,
- explicit clean-no-op, stop and escalation conditions,
- allowed change paths,
- forbidden authority changes,
- required positive and negative tests,
- post-fix production observation.

Health-origin code remediation must be revalidated against fresh Automation Production Health and bound to a non-default task branch through `scripts/remediation/write_transition_receipt.py`. Standalone research-origin tasks use their task-specific `scripts/remediation/write_codex_research_transition_receipt.py` command, which verifies candidate identity, candidate hash, task-contract hash, code-only authority and safe branch before recording `IN_REMEDIATION` under `research/codex/transitions/`.

A stale task must not be repaired speculatively. A valid hash-bound receipt moves the finding into `IN_REMEDIATION`. Invalid receipts are reported and ignored. Health-origin disappearance after bound remediation enters `POST_FIX_OBSERVATION`; it is not `RESOLVED` until the post-fix gate is satisfied. A returning health signature becomes `REOPENED` and requires a newly generated transition receipt before remediation can resume. Research-origin tasks require a hash-bound completion receipt after merge and verification before the execution ledger may show `RESOLVED`.

`research/codex/CODEX_EXECUTION_LEDGER.jsonl` records state or contract transitions from activation of Codex Intake v1 forward. Its first production pass imports the currently visible remediation tasks as a baseline without pretending to have observed older activity live. Earlier history remains reconstructable through remediation history, transition receipts, issues, PRs and commits.

No automation may self-merge a Codex change. Model weights, market gates, canonical predecessor rules, authority boundaries, portfolio logic, API budget and new policy semantics remain framework-owner proposal-only.

## API-agent failure semantics

Structured API output is accepted only when it parses and validates against the strict schema.

For incomplete or malformed output:

1. one bounded retry is allowed with the same prompt and immutable context,
2. all attempts, tokens and cost are recorded,
3. if still invalid, a deterministic `BLOCKED` output and `API_OUTPUT_INVALID` receipt are persisted,
4. no forecast candidates are created,
5. the failure remains visible to health and remediation.

An invalid model response must not erase the deterministic data context or cause silent absence of a receipt.

## Weekly chain

The current weekly order remains:

```text
owner captures and DATA PING bridge
-> Sunday/final market close
-> deterministic Master Monday preflight
-> Weekly Evidence Freeze and remote readback
-> optional OpenAI calibration
-> machine package, report, scorecard, operational translation and delivery pointer
-> handoff to RAW, Cycle Navigator, Forecast Ledger and Master Monday
```

Freeze and preflight must survive API failure. A weekly output may be partial or an explicit API-failure publication, but it may not disappear silently.

## Expected first-run and retirement semantics

- A new scheduled workflow with no expected schedule opportunity yet is `PENDING_FIRST_EXPECTED_RUN`, not a production failure.
- Deleted temporary smoke workflows may be recorded as retired registration residue only through an exact allowlist or durable retirement receipt.
- Unknown registered workflows without a local file remain visible until explicitly classified.
- Historical failures clear only after the configured recovery window. They may not keep a currently healthy workflow permanently RED.

## Cross-repository automation policy

The main repository is the only current automation control plane. The other two repositories have no independent authority to repair or mutate the main framework.

Future workflows in the experiment or Cycle Navigator repositories must publish a hash-bound handoff back to the main repository and be registered in Automation Production Health before being considered active framework infrastructure.

Research in any repository or thread that wants Codex remediation must hand the candidate into the canonical control plane. It may not create a parallel Codex queue in Experiments or Cycle Navigator.

## Acceptance

Automation architecture is current only when:

- all main writers use `framework-main-writer`, explicit `main` checkout, retry, abort and readback,
- scheduled workflows use explicit `Europe/Copenhagen` where local timing matters,
- lifecycle declarations are timestamped, validated and cannot mask active production failures,
- artifacts have bounded retention and durable evidence is committed separately,
- health does not self-poison,
- remediation has one visible source-agnostic Codex queue, fresh-state preflight, hash-bound transition receipts and post-fix evidence lane,
- research intake is schema-bound, deduplicated and event-driven without becoming authority,
- Codex execution state and ledger remain observability-only,
- strict API failures produce durable receipts,
- the full CI suite passes,
- real production runs enter post-fix observation before incidents are resolved.

Authority: operational orchestration only. No market-state, model-weight or portfolio authority.
