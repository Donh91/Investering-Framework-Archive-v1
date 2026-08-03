# Legacy Automation Health and Integration Audit, 2026-08-03

Status: REMEDIATION IMPLEMENTED, CI AND PRODUCTION READBACK PENDING

## Scope

Review of scheduled and direct-to-main workflows that existed before or alongside the OpenAI API and CFGI integration. The purpose is to remove isolated automation islands and make captures, AI synthesis, weekly calibration, DATA PING ingest, ETF evidence, health, outcomes and downstream framework consumers share one governed evidence chain.

## Findings

1. Writer workflows used separate concurrency groups. This allowed daily capture, Daily Director, Sunday close, weekly bridge, weekly calibration and learning operations to overlap.
2. Several writers lacked `git rebase --abort` before retries and lacked verified main readback.
3. Daily Director could attempt an empty commit.
4. Automation health was not represented as a first-class machine-readable object.
5. Health selected files by checkout mtime rather than embedded timestamps.
6. Handoff targets existed mainly as labels, without one evidence manifest binding actual files and hashes to RAW, Cycle Navigator, Master Monday and Forecast Ledger.
7. `allowed_write_prefix` existed as registry documentation but was not enforced by the API gateway.
8. External and model-generated narrative content lacked a universal untrusted-data envelope.

## Remediation

- All six known direct-to-main writers use `framework-main-writer`.
- Writer retries abort stale rebases, require successful push and verify main readback.
- Daily and weekly OpenAI tasks declare and enforce their intended write prefixes.
- API input is wrapped as `UNTRUSTED_ANALYTICAL_INPUT_v1`.
- `AUTOMATION_HEALTH_INVENTORY_v1` scans every workflow for scheduling, write access, writer lock, retry and readback controls.
- `FRAMEWORK_HANDOFF_MANIFEST_v1` binds current evidence files by path and SHA-256 to explicit downstream consumers.
- Architecture health now uses embedded timestamps, freshness limits and ETF parity.
- Accepted DATA PING inbox files move to processed storage after immutable ingest.
- Outcome maturation requires valid horizons, positive directional thresholds or explicit range bounds and bounded evidence lag.

## New functional chain

Daily captures -> Daily Director -> automation and architecture health -> accepted DATA PING ingest -> ETF owner -> final weekly close -> weekly freeze -> Terra calibration -> handoff manifest -> RAW / Cycle Navigator / Master Monday / Forecast Ledger -> outcome maturation.

## Acceptance

This audit is accepted only when integrated CI passes, the automation inventory reports no direct-to-main writer outside the global writer contract, and merged-main readback confirms the new scripts and workflows.
