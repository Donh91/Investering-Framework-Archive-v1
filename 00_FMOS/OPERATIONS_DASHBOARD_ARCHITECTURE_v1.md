# OPERATIONS DASHBOARD ARCHITECTURE v1

Status: ACTIVE AFTER MERGE
Owner: GitHub Actions
Authority: Operational observability only
Market authority: NONE
Portfolio authority: NONE

## Purpose

Provide one compact, public, hash-aware operational cockpit for humans and agents without replacing the underlying health, handoff, receipt or owner contracts.

## Read order

1. `LATEST_OPERATIONS_DASHBOARD.json`
2. `LATEST_HANDOFF.json`
3. `research/architecture_health/LATEST_AUTOMATION_HEALTH.json`
4. `research/architecture_health/LATEST_ARCHITECTURE_HEALTH.json`
5. affected pointer, receipt or incident

## Design rules

- The dashboard aggregates existing evidence. It does not create market truth.
- Missing or invalid inputs can never become GREEN.
- Pointer hashes are rechecked against repository bytes.
- `SKIPPED_NO_DELTA` is an expected token-saving outcome, not a failure.
- Historical incident references do not alone create RED. Current health and freshness do.
- Codex activity remains UNKNOWN unless a dedicated delivery receipt exists.
- OpenAI usage is derived from durable API receipts where available.
- System-specific freshness windows are used instead of one global timeout.

## Outputs

- `LATEST_OPERATIONS_DASHBOARD.json`
- `LATEST_OPERATIONS_DASHBOARD.md`
- `research/operations_dashboard/LATEST_OPERATIONS_DASHBOARD.json`
- `research/operations_dashboard/LATEST_OPERATIONS_DASHBOARD.md`

## Current systems

- Daily capture
- OpenAI Daily Director
- Weekly output
- Automation health
- Architecture health
- OpenAI API usage
- Forecast candidate backlog
- Incident references
- Codex attribution state

## Status semantics

### GREEN

Fresh, hash-consistent and semantically healthy. Expected no-op outcomes such as `SKIPPED_NO_DELTA` are GREEN.

### AMBER

Delayed, incomplete, missing attribution, missing optional pointer or degraded without evidence corruption.

### RED

Stale critical evidence, hash mismatch, current automation health RED, architecture health RED or invalid required input.

## Simulation set

The gate must verify:

- happy-path GREEN
- no-delta skip remains GREEN
- pointer hash mismatch becomes RED
- stale capture becomes RED
- automation RED propagates
- missing inputs never produce false GREEN

## Schedule

The dashboard runs at 06:00 and 18:00 Europe/Copenhagen, after the production-health audit at 05:30 and 17:30.

## Future v2 candidates

Not part of v1 acceptance:

- dedicated Codex delivery receipts
- per-owner CFGI/FRED/Binance/OKX rows
- explicit monthly API budget percentage
- forecast accuracy and calibration summary
- cross-repository status surface

These must be added only when durable source contracts exist. Dashboard v1 must not infer them from commit messages.
