# Automation Production Health
Status: **RED**
Generated: `2026-08-29T00:02:55.840358Z`
Workflows: 116 local / 123 registered
Scheduled: 44
Writers: 50
GREEN / AMBER / RED: 96 / 18 / 2

## Workflow matrix
| Workflow | Lifecycle | Schedule | Writer | Last conclusion | Last run | Status | Findings |
|---|---|---:|---:|---|---|---|---|
| `adaptive-decision-miss-validation.yml` | `ACTIVE` | yes | yes | success | 2026-08-28T06:16:32Z | **GREEN** | None |
| `adaptive-evidence-gap-gate.yml` | `ACTIVE` | no | no | success | 2026-08-28T20:06:33Z | **GREEN** | None |
| `adaptive-evidence-gap.yml` | `ACTIVE` | yes | yes | success | 2026-08-28T05:50:00Z | **GREEN** | None |
| `adaptive-gap-validation-gate.yml` | `ACTIVE` | no | no | success | 2026-08-26T14:16:58Z | **GREEN** | None |
| `adaptive-rotation-cadence.yml` | `ACTIVE` | yes | yes | success | 2026-08-28T14:21:50Z | **GREEN** | None |
| `api-agent-gateway-gate.yml` | `ACTIVE` | no | no | failure | 2026-08-28T20:06:33Z | **GREEN** | None |
| `automation-production-health-gate.yml` | `ACTIVE` | no | no | success | 2026-08-28T23:10:30Z | **GREEN** | None |
| `automation-production-health.yml` | `ACTIVE` | yes | yes | in_progress | 2026-08-29T00:02:43Z | **GREEN** | None |
| `autonomous-research-governance-gate.yml` | `ACTIVE` | no | no | success | 2026-08-23T11:29:50Z | **GREEN** | None |
| `autonomous-research-governance-loop.yml` | `ACTIVE` | yes | yes | success | 2026-08-28T17:31:19Z | **GREEN** | None |
| `backtest-engine-foundation.yml` | `ACTIVE` | no | no | success | 2026-08-09T17:25:05Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `backtest-readiness-contracts.yml` | `ACTIVE` | no | no | success | 2026-07-30T18:08:16Z | **GREEN** | None |
| `backtest-wave1-2-foundation.yml` | `ACTIVE` | no | no | success | 2026-08-09T17:25:05Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `backtest-wave1-3-authority-lineage.yml` | `ACTIVE` | no | no | success | 2026-07-28T16:15:15Z | **GREEN** | None |
| `backtest-wave1-4-prospective.yml` | `ACTIVE` | yes | no | success | 2026-08-28T00:33:58Z | **AMBER** | SCHEDULE_STALE |
| `binance-spot-owner-manual.yml` | `ACTIVE` | no | no | success | 2026-08-01T19:31:36Z | **GREEN** | None |
| `binance-usdm-owner-manual.yml` | `ACTIVE` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `buildwithclaude-shadow-evidence-ledger.yml` | `ACTIVE` | yes | yes | success | 2026-08-23T23:51:52Z | **GREEN** | None |
| `buildwithclaude-shadow-prospective-observer.yml` | `ACTIVE` | no | no | success | 2026-08-23T15:24:40Z | **GREEN** | None |
| `buildwithclaude-shadow-round1.yml` | `ACTIVE` | no | no | success | 2026-08-23T20:47:41Z | **GREEN** | None |
| `cfgi-recovery-launch-once.yml` | `ACTIVE` | no | no | success | 2026-08-23T07:25:36Z | **GREEN** | None |
| `cfgi-recovery-launch-trigger.yml` | `ACTIVE` | no | yes | skipped | 2026-08-28T21:33:52Z | **GREEN** | None |
| `cfgi-v3-launch-receipt-publish.yml` | `ACTIVE` | no | yes | success | 2026-08-23T07:24:14Z | **GREEN** | None |
| `codex-intake-dispatch.yml` | `ACTIVE` | no | no | success | 2026-08-28T06:01:02Z | **GREEN** | None |
| `continuity-learning-gate.yml` | `ACTIVE` | no | no | success | 2026-08-28T20:06:33Z | **GREEN** | None |
| `continuity-learning-maintenance.yml` | `ACTIVE` | yes | yes | success | 2026-08-28T05:49:16Z | **GREEN** | None |
| `cowork-historical-altseason-bundle-gate.yml` | `ACTIVE` | no | no | success | 2026-08-21T09:47:00Z | **GREEN** | None |
| `cowork-historical-altseason-bundle-receipt.yml` | `ACTIVE` | no | yes | success | 2026-08-21T09:47:59Z | **GREEN** | None |
| `cowork-historical-altseason-bundle.yml` | `ACTIVE` | no | no | success | 2026-08-21T09:47:47Z | **GREEN** | None |
| `cross-repo-agent-context-gate.yml` | `ACTIVE` | no | no | success | 2026-08-28T16:11:32Z | **GREEN** | None |
| `cycle-navigator-autonomous-calibration-gate.yml` | `ACTIVE` | no | no | success | 2026-08-22T19:38:07Z | **GREEN** | None |
| `cycle-navigator-autonomous-calibration-loop.yml` | `ACTIVE` | yes | yes | success | 2026-08-24T07:33:01Z | **GREEN** | None |
| `cycle-navigator-weekly-publication.yml` | `ACTIVE` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY |
| `daily-capture-architecture-gate.yml` | `ACTIVE` | no | no | success | 2026-08-28T19:44:52Z | **GREEN** | None |
| `daily-director-shadow.yml` | `ACTIVE` | yes | yes | failure | 2026-08-28T23:10:07Z | **RED** | LATEST_RUN_FAILED, REPEATED_CONSECUTIVE_FAILURES, SCHEDULE_STALE |
| `daily-machine-throughput-gate.yml` | `ACTIVE` | no | no | success | 2026-08-28T16:53:47Z | **GREEN** | None |
| `daily-machine-throughput.yml` | `ACTIVE` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY |
| `daily-raw-owner-capture.yml` | `ACTIVE` | yes | yes | success | 2026-08-28T22:16:51Z | **GREEN** | None |
| `daily-settled-etf-calibration.yml` | `ACTIVE` | yes | yes | success | 2026-08-28T18:35:17Z | **GREEN** | None |
| `daily-slow-cycle-shadow.yml` | `ACTIVE` | yes | yes | failure | 2026-08-28T16:54:04Z | **RED** | LATEST_RUN_FAILED |
| `daily-stablecoin-liquidity.yml` | `ACTIVE` | yes | yes | success | 2026-08-28T17:29:34Z | **GREEN** | None |
| `data-architecture-gate.yml` | `ACTIVE` | no | no | success | 2026-08-28T23:10:31Z | **GREEN** | None |
| `data-terminal-shadow-manual.yml` | `ACTIVE` | no | no | success | 2026-08-28T23:10:31Z | **GREEN** | None |
| `dataset-registry-gate.yml` | `ACTIVE` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `entry-signal-ledger-gate.yml` | `ACTIVE` | no | no | success | 2026-08-20T13:44:05Z | **GREEN** | None |
| `entry-signal-ledger.yml` | `ACTIVE` | yes | yes | success | 2026-08-28T19:36:44Z | **GREEN** | None |
| `ethbtc-persistence-lifecycle.yml` | `ACTIVE` | no | yes | success | 2026-08-27T15:26:37Z | **GREEN** | None |
| `evidence-closure-gate.yml` | `ACTIVE` | no | no | success | 2026-08-25T20:53:58Z | **GREEN** | None |
| `evidence-lifecycle-observability-gate.yml` | `ACTIVE` | no | no | success | 2026-08-16T11:33:59Z | **GREEN** | None |
| `evidence-lifecycle-store-health.yml` | `ACTIVE` | yes | no | success | 2026-08-28T15:24:37Z | **GREEN** | None |
| `experiment-lifecycle-gate.yml` | `ACTIVE` | no | no | success | 2026-08-27T15:42:59Z | **GREEN** | None |
| `fetch_btc_d_cmc_free.yml` | `ACTIVE` | no | no | success | 2026-07-12T00:09:38Z | **GREEN** | None |
| `framework-learning-operations.yml` | `ACTIVE` | yes | yes | success | 2026-08-28T12:57:03Z | **GREEN** | None |
| `full-architecture-1to7-gate.yml` | `ACTIVE` | no | no | success | 2026-08-28T21:33:34Z | **GREEN** | None |
| `historical-altseason-cfgi-enrichment.yml` | `RETIRED` | no | no | failure | 2026-08-23T05:18:07Z | **AMBER** | RETIRED_WORKFLOW_LOCAL_FILE_PRESENT |
| `historical-altseason-cfgi-publish.yml` | `ACTIVE` | no | yes | success | 2026-08-21T08:08:20Z | **GREEN** | None |
| `historical-altseason-cfgi-reservation.yml` | `RETIRED` | no | no | success | 2026-08-27T15:57:24Z | **AMBER** | RETIRED_WORKFLOW_LOCAL_FILE_PRESENT |
| `historical-altseason-cfgi-run-audit.yml` | `ACTIVE` | no | yes | success | 2026-08-27T15:44:04Z | **GREEN** | None |
| `historical-altseason-cfgi-terminal-finalize.yml` | `ACTIVE` | no | no | success | 2026-08-21T13:55:43Z | **GREEN** | None |
| `historical-altseason-cfgi-terminal-publish.yml` | `ACTIVE` | no | yes | success | 2026-08-21T13:55:57Z | **GREEN** | None |
| `historical-altseason-free-bootstrap.yml` | `ACTIVE` | no | no | success | 2026-08-27T15:44:03Z | **GREEN** | None |
| `historical-altseason-free-publish-regression-gate.yml` | `ACTIVE` | no | no | success | 2026-08-21T13:54:37Z | **GREEN** | None |
| `historical-altseason-free-publish.yml` | `ACTIVE` | no | yes | success | 2026-08-27T15:56:53Z | **GREEN** | None |
| `historical-altseason-lab-gate.yml` | `ACTIVE` | no | no | success | 2026-08-27T15:43:49Z | **AMBER** | ARTIFACT_RETENTION_UNBOUNDED |
| `historical-altseason-throughput-gate.yml` | `ACTIVE` | no | no | success | 2026-08-27T15:43:00Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `hourly-sequence-capture.yml` | `ACTIVE` | yes | yes | success | 2026-08-28T15:48:50Z | **AMBER** | SCHEDULE_STALE |
| `intraday-execution-gate.yml` | `ACTIVE` | no | no | success | 2026-08-24T05:51:40Z | **GREEN** | None |
| `intraday-execution-research.yml` | `ACTIVE` | yes | yes | success | 2026-08-28T20:31:12Z | **AMBER** | SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE |
| `legacy-knowledge-bootstrap-gate.yml` | `ACTIVE` | no | no | success | 2026-08-04T19:08:35Z | **GREEN** | None |
| `mar_wp04c4_gate.yml` | `ACTIVE` | no | no | success | 2026-07-31T01:41:02Z | **GREEN** | None |
| `master-monday-preflight-gate.yml` | `ACTIVE` | no | no | success | 2026-08-25T05:37:19Z | **GREEN** | None |
| `master-monday-remaining-gaps.yml` | `ACTIVE` | yes | yes | success | 2026-08-24T07:49:35Z | **GREEN** | None |
| `okx-swap-owner-manual.yml` | `ACTIVE` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `operations-dashboard-gate.yml` | `ACTIVE` | no | no | success | 2026-08-27T15:43:00Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `operations-dashboard.yml` | `ACTIVE` | yes | yes | success | 2026-08-28T16:27:26Z | **GREEN** | None |
| `owner-bound-daily-director-manual.yml` | `ACTIVE` | no | no | success | 2026-08-28T20:06:33Z | **GREEN** | None |
| `pdf-inspector-ingestion.yml` | `ACTIVE` | no | no | success | 2026-08-02T18:16:02Z | **GREEN** | None |
| `pdlt-bootstrap-once.yml` | `ACTIVE` | no | no | skipped | 2026-08-10T15:36:07Z | **GREEN** | None |
| `pdlt-daily-census.yml` | `ACTIVE` | yes | yes | success | 2026-08-28T05:50:08Z | **GREEN** | None |
| `pdlt-discovery-once.yml` | `EXPECTED_BLOCK` | no | no | failure | 2026-08-09T19:58:23Z | **AMBER** | EXPECTED_BLOCK |
| `pdlt-maturation.yml` | `ACTIVE` | yes | yes | success | 2026-08-28T06:10:38Z | **GREEN** | None |
| `pdlt-runtime-gate.yml` | `ACTIVE` | no | no | success | 2026-08-10T20:05:49Z | **GREEN** | None |
| `pdlt-v1-1.yml` | `ACTIVE` | no | no | success | 2026-08-10T15:36:09Z | **GREEN** | None |
| `phase4-no-hindsight-replay.yml` | `ACTIVE` | no | no | success | 2026-08-23T17:53:27Z | **GREEN** | None |
| `pullback-learning-gate.yml` | `ACTIVE` | no | no | success | 2026-08-20T14:17:33Z | **GREEN** | None |
| `pullback-learning-ledger.yml` | `ACTIVE` | yes | yes | success | 2026-08-28T19:36:53Z | **GREEN** | None |
| `remediation-maturation-gate.yml` | `ACTIVE` | no | no | success | 2026-08-22T13:30:18Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `remediation-maturation.yml` | `ACTIVE` | yes | yes | success | 2026-08-28T15:41:11Z | **AMBER** | SCHEDULE_STALE |
| `research-execution-coordinator.yml` | `ACTIVE` | yes | yes | success | 2026-08-28T19:23:39Z | **GREEN** | None |
| `research-owner-breadth-daily.yml` | `ACTIVE` | yes | yes | success | 2026-08-28T17:26:52Z | **GREEN** | None |
| `research-owner-btcd-daily.yml` | `ACTIVE` | yes | yes | success | 2026-08-28T17:40:48Z | **GREEN** | None |
| `rich-breadth-checkpoint.yml` | `ACTIVE` | yes | yes | success | 2026-08-28T22:27:39Z | **GREEN** | None |
| `round3-contract-freeze-gate.yml` | `ACTIVE` | no | no | success | 2026-08-25T21:03:50Z | **GREEN** | None |
| `round3-v2-materialization.yml` | `ACTIVE` | no | no | success | 2026-08-23T13:17:33Z | **GREEN** | None |
| `sequential-research-queue.yml` | `ACTIVE` | yes | yes | success | 2026-08-28T18:50:03Z | **GREEN** | None |
| `shadow-admission-ai-decider.yml` | `ACTIVE` | yes | yes | success | 2026-08-25T05:37:19Z | **GREEN** | None |
| `shadow-registry-autonomous-portfolio-gate.yml` | `ACTIVE` | no | no | success | 2026-08-22T19:41:03Z | **GREEN** | None |
| `shadow-registry-autonomous-portfolio-loop.yml` | `ACTIVE` | yes | yes | success | 2026-08-24T07:44:57Z | **GREEN** | None |
| `shadow-registry-gate.yml` | `ACTIVE` | no | no | success | 2026-08-23T07:46:06Z | **GREEN** | None |
| `shadow-registry-weekly.yml` | `ACTIVE` | yes | yes | success | 2026-08-24T06:07:00Z | **GREEN** | None |
| `shared-row-prospective-evidence-loop.yml` | `ACTIVE` | yes | yes | success | 2026-08-28T16:56:40Z | **GREEN** | None |
| `shared-row-tournament-research-gate.yml` | `ACTIVE` | no | no | success | 2026-08-25T05:25:12Z | **GREEN** | None |
| `shared-row-tournament-weekly.yml` | `ACTIVE` | yes | yes | success | 2026-08-24T07:20:39Z | **GREEN** | None |
| `situation-room-daily-static.yml` | `ACTIVE` | yes | yes | success | 2026-08-28T18:42:54Z | **GREEN** | None |
| `situation-room-owner-live-gate.yml` | `ACTIVE` | no | no | success | 2026-08-28T23:10:31Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `source-provenance-recovery-gate.yml` | `ACTIVE` | no | no | success | 2026-08-23T11:29:50Z | **GREEN** | None |
| `source-provenance-recovery-loop.yml` | `ACTIVE` | yes | yes | success | 2026-08-28T17:12:57Z | **GREEN** | None |
| `specialist-architecture-gate.yml` | `ACTIVE` | no | no | success | 2026-08-23T11:29:50Z | **GREEN** | None |
| `storage-health-gate.yml` | `ACTIVE` | no | no | success | 2026-08-28T23:10:31Z | **GREEN** | None |
| `sunday-market-close-and-cfgi.yml` | `ACTIVE` | yes | yes | success | 2026-08-24T01:48:47Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `top100-breadth-owner-manual.yml` | `ACTIVE` | no | no | success | 2026-08-25T20:53:58Z | **GREEN** | None |
| `unified-experimental-lifecycle-adjudication.yml` | `ACTIVE` | yes | yes | success | 2026-08-24T07:59:32Z | **GREEN** | None |
| `validate_m3_forward_ledger.yml` | `ACTIVE` | no | no | none | none | **GREEN** | None |
| `weekly-api-calibration-shadow.yml` | `ACTIVE` | yes | yes | success | 2026-08-24T02:09:28Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `weekly-raw-calibration-bridge.yml` | `ACTIVE` | yes | yes | success | 2026-08-24T02:04:27Z | **GREEN** | None |
| `weekly-sol-adversarial-review.yml` | `ACTIVE` | yes | yes | success | 2026-08-24T04:03:27Z | **GREEN** | None |

## Blockers
- daily-director-shadow.yml:LATEST_RUN_FAILED
- daily-director-shadow.yml:REPEATED_CONSECUTIVE_FAILURES
- daily-director-shadow.yml:SCHEDULE_STALE
- daily-slow-cycle-shadow.yml:LATEST_RUN_FAILED

## Warnings
- REGISTERED_WITHOUT_LOCAL_FILE:agent-tool-shadow-round2.yml
- REGISTERED_WITHOUT_LOCAL_FILE:cfgi-full-profile-smoke-temp.yml
- REGISTERED_WITHOUT_LOCAL_FILE:cfgi-live-smoke-temp.yml
- REGISTERED_WITHOUT_LOCAL_FILE:harness-redteam-p0-remediation-gate.yml
- REGISTERED_WITHOUT_LOCAL_FILE:historical-shadow-validation-stage1-manifest.yml
- REGISTERED_WITHOUT_LOCAL_FILE:persistent-agent-runtime-readiness-gate.yml
- REGISTERED_WITHOUT_LOCAL_FILE:t4-microstructure-live-readback.yml
- backtest-engine-foundation.yml:RECOVERING_AFTER_RECENT_FAILURES
- backtest-wave1-2-foundation.yml:RECOVERING_AFTER_RECENT_FAILURES
- backtest-wave1-4-prospective.yml:SCHEDULE_STALE
- cycle-navigator-weekly-publication.yml:NO_RUN_HISTORY
- daily-machine-throughput.yml:NO_RUN_HISTORY
- historical-altseason-cfgi-enrichment.yml:RETIRED_WORKFLOW_LOCAL_FILE_PRESENT
- historical-altseason-cfgi-reservation.yml:RETIRED_WORKFLOW_LOCAL_FILE_PRESENT
- historical-altseason-lab-gate.yml:ARTIFACT_RETENTION_UNBOUNDED
- historical-altseason-throughput-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- hourly-sequence-capture.yml:SCHEDULE_STALE
- intraday-execution-research.yml:SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE
- operations-dashboard-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- pdlt-discovery-once.yml:EXPECTED_BLOCK
- remediation-maturation-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- remediation-maturation.yml:SCHEDULE_STALE
- situation-room-owner-live-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- sunday-market-close-and-cfgi.yml:RECOVERING_AFTER_RECENT_FAILURES
- weekly-api-calibration-shadow.yml:RECOVERING_AFTER_RECENT_FAILURES
