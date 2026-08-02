# Full Architecture Audit, 2026-08-02

Status: REMEDIATION IMPLEMENTED, CI AND LIVE READBACK PENDING

Scope: repository-wide review after activation of OpenAI API, CFGI, five daily owner captures, Daily Director, weekly calibration, Specialist Intelligence Layer and weekly market-close packages.

## Executive result

The architecture has strong evidence-governance foundations: owner-first data, explicit missingness, hashes, immutable AI receipts, cost controls and no automatic portfolio authority. The largest risk was orchestration, not individual collectors.

## Findings and remediation

### Critical, corrected

1. **Weekly calibration preceded final exchange-week close.** Weekly Terra ran Monday 00:10 local while final Binance UTC close arrived Monday 02:05. The calibration is moved to 02:20 and now requires a fail-closed weekly evidence freeze.

### High, corrected

2. **No explicit final-week orchestration gate.** Added `weekly_orchestration_controller.py`, requiring final close and weekly bridge before Terra runs.
3. **Chat app DATA PING packets lacked machine ingest.** Added `ACCEPTED_DATA_PING_PACKET_v1` bridge with schema, authority and collision validation.
4. **Forecasts had no generic immutable maturation path.** Added an outcome maturation engine that never rewrites frozen forecasts and censors unavailable metrics.
5. **No single health surface.** Added JSON and Markdown health dashboard generation.

### Medium, corrected or bounded

6. **ETF flows were not automated.** Added a Farside web-table owner with raw-source hashes, BTC/ETH separation, total parity and fail-closed status.
7. **Multiple writers could overlap.** New and corrected workflows share the global `framework-main-writer` concurrency group and verify main readback after push.
8. **Public-repository exposure.** Secrets remain GitHub Actions secrets and are only supplied to workflows that explicitly request them. No secret values are committed. Fork pull requests do not receive repository secrets by default. Public status is not required for normal operation and may be reverted after external review.

### Remaining bounded risks

1. Existing older workflows do not all share the new global write lock. They remain protected by local concurrency and rebase retries, but should be migrated incrementally.
2. Farside is a web-table source without a documented official API. Parser failure must remain `SOURCE_UNAVAILABLE` or `PARTIAL`, never zero flow.
3. The DATA PING bridge cannot pull conversation text from ChatGPT. It ingests only explicitly exported accepted packets.
4. Health status is operational, not a market signal and carries no portfolio authority.
5. Outcome scoring requires pre-registered `FROZEN_FORECAST_v1` rows with explicit metric path, horizon, direction and threshold.

## Security review

- Workflows use explicit permissions.
- API secrets are not written to outputs or committed files.
- OpenAI calls remain behind schema, cost and authority gates.
- CFGI is an optional sentiment owner and cannot create canonical truth.
- External HTML is treated as untrusted data, not executable instructions.
- Bot writes are compact and use readback verification.
- No workflow introduced self-promotion of model weights or portfolio action.

## Dataflow after remediation

Daily owner captures -> Daily Director -> accepted DATA PING bridge and ETF owner -> final UTC weekly close -> weekly evidence freeze -> Terra calibration -> RAW, Cycle Navigator, Forecast Ledger and Master Monday handoff -> outcome maturation -> precision scorecards.

## Health scorecard at design review

- Evidence governance: 92/100
- API safety and cost control: 91/100
- Data lineage and missingness: 90/100
- Weekly orchestration after remediation: 90/100
- Write-race resilience: 80/100
- App-to-repository integration: 78/100, export still required
- Adaptive learning readiness: 88/100
- Overall architecture health: 87/100 pending first production readbacks

## Acceptance gates

The seven-phase package is accepted only after:

1. integrated unit tests pass;
2. repository-wide Data Architecture and Storage Health gates pass;
3. final weekly workflow contains the 02:20 post-close schedule and freeze preflight;
4. temporary live triggers are absent;
5. merged-main readback succeeds;
6. first scheduled or manual operational workflow produces a health receipt;
7. no secrets or forbidden authority fields are found in committed outputs.
