# AUTOMATION PRODUCTION HEALTH ARCHITECTURE v1

Status: ACTIVE AFTER MERGE
Owner: GitHub Actions
Authority: Operational health only, no market or portfolio authority

## Purpose

Provide one durable, machine-readable and human-readable health surface for every GitHub Actions workflow in the canonical repository.

The system audits both:

1. Static workflow safety and governance.
2. Actual GitHub Actions production state.

It does not infer market state and does not modify framework model weights.

## Authoritative outputs

- `research/architecture_health/LATEST_AUTOMATION_HEALTH.json`
- `research/architecture_health/LATEST_AUTOMATION_HEALTH.md`
- `research/architecture_health/LATEST_ARCHITECTURE_HEALTH.json`
- `research/architecture_health/LATEST_ARCHITECTURE_HEALTH.md`
- RED incidents under `09_SOURCE_QA/incidents/`

## Schedule

`Automation Production Health` runs twice daily in `Europe/Copenhagen` and supports manual dispatch.

## Static checks

Each workflow is checked for:

- active schedule and explicit timezone
- direct-to-main writes
- shared `framework-main-writer` lock
- rebase abort before retry
- empty-commit guard
- main readback
- risky `pull_request_target` use
- artifact retention declaration
- OpenAI and CFGI dependency presence
- permissions surface

## Live checks

The health workflow queries GitHub Actions for:

- workflow registration and active state
- latest run status and conclusion
- latest run timestamp
- latest run attempt and commit
- recent conclusions
- repeated recent failures
- stale schedules
- stuck or delayed jobs
- registered workflows without a local file

## Classification

- `GREEN`: no current static or live findings.
- `AMBER`: degraded, stale, unregistered, API-limited or non-critical governance findings.
- `RED`: failed latest production run, repeated failures, unsafe writer contract, missing readback, or dangerous PR-target permissions.

## Durable failure rule

A RED result is committed to `main` before the workflow itself fails. This ensures that failure cannot erase its own diagnostic evidence.

After durable publication, the workflow:

- creates or updates one sanitized open incident issue
- uploads a 14-day transport artifact
- exits non-zero

## Reader order for agents

1. `LATEST_HANDOFF.json`
2. `research/architecture_health/LATEST_AUTOMATION_HEALTH.json`
3. `research/architecture_health/LATEST_ARCHITECTURE_HEALTH.json`
4. the affected workflow file
5. the latest Actions run and job logs
6. the corresponding incident file

## Governance boundary

GitHub Actions owns execution, persistence and receipts.

ChatGPT automations and other read-only agents may:

- read the health surfaces
- report exact failures and stale dependencies
- recommend or prepare repairs

They must not claim a GitHub mutation unless a write-capable execution context provides a real commit, PR, merge and readback.
