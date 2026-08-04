# AUTOMATION GOVERNANCE INCIDENT

Status: REMEDIATED_IN_PR_PENDING_MERGE
Date UTC: 2026-08-04

## Event

A change to `.github/workflows/daily-director-shadow.yml` on `agent/legacy-bootstrap-stabilization-v1` activated the workflow through its generic `push` trigger. The workflow checked out the task branch, created a Daily Director output and then pushed `HEAD:main` as designed for scheduled production writes.

This caused task-branch commits through `40ff6d3af11019fdad556d402fa41eb6840b6f47` to become ancestors of `main` without the intended pull-request gate. The subsequent durable Daily Director output was committed as `389c1e05e4a95cd4c630aecd08392ced4628d0fc`.

## Integrity assessment

- No portfolio action or canonical market-state authority was granted.
- The materialized Daily Director remained shadow-only.
- The legacy research lane was explicitly non-canonical.
- The repository delivery path violated code-lane governance because task-branch history reached `main` through a scheduled writer workflow.

## Root cause

A workflow with `contents: write` and `git push origin HEAD:main` also accepted a generic `push` event. The workflow therefore inherited the event branch instead of a main-only production checkout.

## Remediation

- Remove generic `push` triggers from `daily-director-shadow.yml` and `daily-raw-owner-capture.yml`.
- Add `if: github.ref == 'refs/heads/main'` to writer jobs.
- Pin writer checkout to `ref: main`.
- Add `scripts/health/check_writer_trigger_safety.py`.
- Make Automation Production Health Gate reject any push-triggered workflow that can push repository contents.

## Follow-up

The affected code remains subject to the stabilization PR and CI. This incident is operational governance evidence only and creates no market, framework, model-weight or portfolio authority.
