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
7. `AGENTS.md`, canonical index, registries and the relevant skill
8. the exact workflow, receipt, pointer, run and job logs

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

Cron ordering is not a finality guarantee. Each consumer must validate timestamp, contract and hash of its input and remain explicit when the newest upstream output is unavailable.

## Observer versus observed status

A health observer must not fail merely because the observed fleet is RED.

The observer workflow is successful when it:

- completed the audit,
- durably published the exact RED report,
- verified remote bytes,
- recorded or updated the incident channel.

The report and dashboard remain RED. The observer run remains successful. Failures in the observer itself are reserved for inability to audit, publish, read back or notify.

## Remediation and Codex

`CODEX_READY` means the problem has sufficient evidence for a bounded code task. It does not mean that code has been changed or merged.

The controller publishes:

- `LATEST_REMEDIATION_QUEUE.json`
- `LATEST_CODEX_READY_TASKS.json`
- `LATEST_NEEDS_MORE_EVIDENCE.json`
- one deduplicated GitHub issue titled `CODEX READY REMEDIATION QUEUE`

Each task must preserve:

- exact signature and run identity,
- allowed change paths,
- forbidden authority changes,
- required positive and negative tests,
- post-fix production observation.

No automation may self-merge a Codex change. Model weights, market gates, canonical predecessor rules, authority boundaries, portfolio logic and API budget remain framework-owner proposal-only.

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

## Acceptance

Automation architecture is current only when:

- all main writers use `framework-main-writer`, explicit `main` checkout, retry, abort and readback,
- scheduled workflows use explicit `Europe/Copenhagen` where local timing matters,
- artifacts have bounded retention and durable evidence is committed separately,
- health does not self-poison,
- remediation has a visible Codex queue and an evidence lane,
- strict API failures produce durable receipts,
- the full CI suite passes,
- real production runs enter post-fix observation before incidents are resolved.

Authority: operational orchestration only. No market-state, model-weight or portfolio authority.
