# Automation Production Health
Status: **AMBER**
Generated: `2026-09-03T08:10:56.811786Z`
Workflows: 126 local / 134 registered
Scheduled: 41
Writers: 47
GREEN / AMBER / RED: 101 / 25 / 0

## Workflow matrix
| Workflow | Lifecycle | Schedule | Writer | Last conclusion | Last run | Status | Findings |
|---|---|---:|---:|---|---|---|---|
| `adaptive-decision-miss-validation.yml` | `ACTIVE` | yes | yes | success | 2026-09-03T00:34:40Z | **GREEN** | None |
| `adaptive-evidence-gap-gate.yml` | `ACTIVE` | no | no | success | 2026-08-28T20:06:33Z | **GREEN** | None |
| `adaptive-evidence-gap.yml` | `ACTIVE` | yes | yes | success | 2026-09-02T23:36:11Z | **GREEN** | None |
| `adaptive-gap-validation-gate.yml` | `ACTIVE` | no | no | success | 2026-08-26T14:16:58Z | **GREEN** | None |
| `adaptive-rotation-cadence.yml` | `ACTIVE` | yes | yes | success | 2026-09-03T07:11:09Z | **GREEN** | None |
| `api-agent-gateway-gate.yml` | `ACTIVE` | no | no | success | 2026-09-03T05:50:47Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `automation-production-health-gate.yml` | `ACTIVE` | no | no | success | 2026-09-03T06:03:17Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `automation-production-health.yml` | `ACTIVE` | yes | yes | in_progress | 2026-09-03T08:10:41Z | **GREEN** | None |
| `autonomous-research-governance-gate.yml` | `ACTIVE` | no | no | success | 2026-09-03T05:50:47Z | **GREEN** | None |
| `autonomous-research-governance-loop.yml` | `ACTIVE` | yes | yes | success | 2026-09-02T09:45:35Z | **GREEN** | None |
| `backtest-engine-foundation.yml` | `ACTIVE` | no | no | success | 2026-08-09T17:25:05Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `backtest-readiness-contracts.yml` | `ACTIVE` | no | no | success | 2026-07-30T18:08:16Z | **GREEN** | None |
| `backtest-wave1-2-foundation.yml` | `ACTIVE` | no | no | success | 2026-08-09T17:25:05Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `backtest-wave1-3-authority-lineage.yml` | `ACTIVE` | no | no | success | 2026-07-28T16:15:15Z | **GREEN** | None |
| `backtest-wave1-4-prospective.yml` | `ACTIVE` | yes | no | success | 2026-09-02T18:55:33Z | **GREEN** | None |
| `binance-spot-owner-manual.yml` | `ACTIVE` | no | no | success | 2026-08-01T19:31:36Z | **GREEN** | None |
| `binance-usdm-owner-manual.yml` | `ACTIVE` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `buildwithclaude-shadow-evidence-ledger.yml` | `ACTIVE` | no | no | success | 2026-09-02T16:22:23Z | **GREEN** | None |
| `buildwithclaude-shadow-prospective-observer.yml` | `ACTIVE` | no | no | success | 2026-09-03T05:50:47Z | **GREEN** | None |
| `buildwithclaude-shadow-round1.yml` | `ACTIVE` | no | no | success | 2026-09-02T16:22:23Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `cfgi-recovery-launch-once.yml` | `ACTIVE` | no | no | success | 2026-08-23T07:25:36Z | **GREEN** | None |
| `cfgi-recovery-launch-trigger.yml` | `ACTIVE` | no | yes | skipped | 2026-09-03T06:03:34Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `cfgi-v3-launch-receipt-publish.yml` | `ACTIVE` | no | yes | success | 2026-08-23T07:24:14Z | **GREEN** | None |
| `codex-intake-dispatch.yml` | `ACTIVE` | no | no | success | 2026-09-02T21:50:46Z | **GREEN** | None |
| `continuity-learning-gate.yml` | `ACTIVE` | no | no | success | 2026-09-03T05:50:47Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `continuity-learning-maintenance.yml` | `ACTIVE` | yes | yes | success | 2026-09-02T23:33:02Z | **GREEN** | None |
| `cowork-historical-altseason-bundle-gate.yml` | `ACTIVE` | no | no | success | 2026-08-21T09:47:00Z | **GREEN** | None |
| `cowork-historical-altseason-bundle-receipt.yml` | `ACTIVE` | no | yes | success | 2026-08-21T09:47:59Z | **GREEN** | None |
| `cowork-historical-altseason-bundle.yml` | `ACTIVE` | no | no | success | 2026-08-21T09:47:47Z | **GREEN** | None |
| `cross-repo-agent-context-gate.yml` | `ACTIVE` | no | no | success | 2026-08-31T00:58:50Z | **GREEN** | None |
| `cycle-navigator-autonomous-calibration-gate.yml` | `ACTIVE` | no | no | success | 2026-08-22T19:38:07Z | **GREEN** | None |
| `cycle-navigator-autonomous-calibration-loop.yml` | `ACTIVE` | yes | yes | success | 2026-08-31T14:06:12Z | **GREEN** | None |
| `cycle-navigator-weekly-publication.yml` | `ACTIVE` | yes | yes | success | 2026-09-01T17:15:21Z | **GREEN** | None |
| `daily-capture-architecture-gate.yml` | `ACTIVE` | no | no | success | 2026-09-02T21:44:27Z | **GREEN** | None |
| `daily-director-shadow.yml` | `ACTIVE` | yes | yes | success | 2026-09-02T23:30:36Z | **GREEN** | None |
| `daily-machine-throughput-gate.yml` | `ACTIVE` | no | no | success | 2026-08-28T16:53:47Z | **GREEN** | None |
| `daily-machine-throughput.yml` | `ACTIVE` | yes | yes | success | 2026-09-03T00:45:20Z | **GREEN** | None |
| `daily-raw-owner-capture.yml` | `ACTIVE` | yes | yes | success | 2026-09-03T04:34:04Z | **GREEN** | None |
| `daily-settled-etf-calibration.yml` | `ACTIVE` | yes | yes | success | 2026-09-02T11:10:37Z | **GREEN** | None |
| `daily-slow-cycle-shadow.yml` | `ACTIVE` | yes | yes | success | 2026-09-02T08:59:19Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `daily-stablecoin-liquidity.yml` | `ACTIVE` | yes | yes | success | 2026-09-02T09:43:22Z | **GREEN** | None |
| `data-architecture-gate.yml` | `ACTIVE` | no | no | success | 2026-09-03T06:03:17Z | **GREEN** | None |
| `data-terminal-shadow-manual.yml` | `ACTIVE` | no | no | success | 2026-09-02T21:44:48Z | **GREEN** | None |
| `dataset-registry-gate.yml` | `ACTIVE` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `entry-signal-ledger-gate.yml` | `ACTIVE` | no | no | success | 2026-09-02T15:54:46Z | **GREEN** | None |
| `entry-signal-ledger.yml` | `ACTIVE` | yes | yes | success | 2026-09-03T06:31:24Z | **GREEN** | None |
| `ethbtc-persistence-lifecycle.yml` | `ACTIVE` | no | yes | success | 2026-09-02T23:31:27Z | **GREEN** | None |
| `evidence-closure-gate.yml` | `ACTIVE` | no | no | success | 2026-09-02T21:44:48Z | **GREEN** | None |
| `evidence-lifecycle-observability-gate.yml` | `ACTIVE` | no | no | success | 2026-08-31T04:28:06Z | **GREEN** | None |
| `evidence-lifecycle-store-health.yml` | `ACTIVE` | yes | no | success | 2026-09-03T08:04:52Z | **GREEN** | None |
| `experiment-lifecycle-gate.yml` | `ACTIVE` | no | no | success | 2026-09-02T09:55:30Z | **GREEN** | None |
| `fetch_btc_d_cmc_free.yml` | `ACTIVE` | no | no | success | 2026-07-12T00:09:38Z | **GREEN** | None |
| `forecast-exact-settlement-owner-gate.yml` | `ACTIVE` | no | no | success | 2026-09-02T15:29:27Z | **GREEN** | None |
| `forecast-materialization-census-gate.yml` | `ACTIVE` | no | no | success | 2026-09-02T21:56:33Z | **GREEN** | None |
| `forecast-outcome-supersession-gate.yml` | `ACTIVE` | no | no | success | 2026-09-02T15:29:27Z | **GREEN** | None |
| `forecast-ratification-throughput-gate.yml` | `ACTIVE` | no | no | success | 2026-09-02T21:56:33Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `forecast-settlement-accountability-gate.yml` | `ACTIVE` | no | no | success | 2026-09-02T21:56:33Z | **GREEN** | None |
| `forecast-source-temporal-provenance-gate.yml` | `ACTIVE` | no | no | success | 2026-09-02T21:56:33Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `framework-learning-operations.yml` | `ACTIVE` | yes | yes | success | 2026-09-03T05:53:11Z | **GREEN** | None |
| `full-architecture-1to7-gate.yml` | `ACTIVE` | no | no | success | 2026-09-03T06:03:17Z | **GREEN** | None |
| `historical-altseason-cfgi-enrichment.yml` | `RETIRED` | no | no | failure | 2026-08-23T05:18:07Z | **AMBER** | RETIRED_WORKFLOW_LOCAL_FILE_PRESENT |
| `historical-altseason-cfgi-publish.yml` | `ACTIVE` | no | yes | success | 2026-08-21T08:08:20Z | **GREEN** | None |
| `historical-altseason-cfgi-reservation.yml` | `RETIRED` | no | no | success | 2026-08-31T06:28:37Z | **AMBER** | RETIRED_WORKFLOW_LOCAL_FILE_PRESENT |
| `historical-altseason-cfgi-run-audit.yml` | `ACTIVE` | no | yes | success | 2026-08-31T06:12:32Z | **GREEN** | None |
| `historical-altseason-cfgi-terminal-finalize.yml` | `ACTIVE` | no | no | success | 2026-08-21T13:55:43Z | **GREEN** | None |
| `historical-altseason-cfgi-terminal-publish.yml` | `ACTIVE` | no | yes | success | 2026-08-21T13:55:57Z | **GREEN** | None |
| `historical-altseason-free-bootstrap.yml` | `ACTIVE` | no | no | success | 2026-08-31T06:12:32Z | **GREEN** | None |
| `historical-altseason-free-publish-regression-gate.yml` | `ACTIVE` | no | no | success | 2026-08-21T13:54:37Z | **GREEN** | None |
| `historical-altseason-free-publish.yml` | `ACTIVE` | no | yes | success | 2026-08-31T06:28:20Z | **GREEN** | None |
| `historical-altseason-lab-gate.yml` | `ACTIVE` | no | no | success | 2026-08-31T06:12:20Z | **AMBER** | ARTIFACT_RETENTION_UNBOUNDED |
| `historical-altseason-throughput-gate.yml` | `ACTIVE` | no | no | success | 2026-08-27T15:43:00Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `hourly-sequence-capture.yml` | `ACTIVE` | yes | yes | success | 2026-09-03T04:16:58Z | **GREEN** | None |
| `intraday-execution-gate.yml` | `ACTIVE` | no | no | success | 2026-08-31T07:26:23Z | **GREEN** | None |
| `intraday-execution-research.yml` | `ACTIVE` | no | yes | success | 2026-08-31T00:03:54Z | **GREEN** | None |
| `legacy-knowledge-bootstrap-gate.yml` | `ACTIVE` | no | no | success | 2026-08-04T19:08:35Z | **GREEN** | None |
| `mar_wp04c4_gate.yml` | `ACTIVE` | no | no | success | 2026-07-31T01:41:02Z | **GREEN** | None |
| `master-monday-preflight-gate.yml` | `ACTIVE` | no | no | success | 2026-08-31T07:26:18Z | **GREEN** | None |
| `master-monday-remaining-gaps.yml` | `ACTIVE` | yes | yes | success | 2026-08-31T11:13:56Z | **GREEN** | None |
| `monthly-ai-learning-council-bootstrap-once.yml` | `ACTIVE` | no | no | success | 2026-09-03T06:03:59Z | **GREEN** | None |
| `monthly-ai-learning-council-gate.yml` | `ACTIVE` | no | no | success | 2026-09-03T06:03:17Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `monthly-ai-learning-council.yml` | `ACTIVE` | yes | yes | success | 2026-09-03T06:04:10Z | **AMBER** | NO_RUN_HISTORY |
| `okx-swap-owner-manual.yml` | `ACTIVE` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `operations-dashboard-gate.yml` | `ACTIVE` | no | no | success | 2026-08-27T15:43:00Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `operations-dashboard.yml` | `ACTIVE` | yes | yes | success | 2026-09-02T19:13:52Z | **GREEN** | None |
| `operations-recovery-launch-once.yml` | `ACTIVE` | no | no | success | 2026-08-31T16:26:39Z | **GREEN** | None |
| `owner-bound-daily-director-manual.yml` | `ACTIVE` | no | no | success | 2026-09-03T05:50:47Z | **GREEN** | None |
| `pdf-inspector-ingestion.yml` | `ACTIVE` | no | no | success | 2026-08-02T18:16:02Z | **GREEN** | None |
| `pdlt-bootstrap-once.yml` | `EXPECTED_BLOCK` | no | no | skipped | 2026-08-10T15:36:07Z | **AMBER** | EXPECTED_BLOCK |
| `pdlt-daily-census.yml` | `EXPECTED_BLOCK` | no | no | success | 2026-09-01T23:35:24Z | **AMBER** | EXPECTED_BLOCK |
| `pdlt-discovery-once.yml` | `EXPECTED_BLOCK` | no | no | failure | 2026-08-09T19:58:23Z | **AMBER** | EXPECTED_BLOCK |
| `pdlt-maturation.yml` | `EXPECTED_BLOCK` | no | no | success | 2026-09-02T00:19:38Z | **AMBER** | EXPECTED_BLOCK |
| `pdlt-runtime-gate.yml` | `ACTIVE` | no | no | success | 2026-09-02T14:40:09Z | **GREEN** | None |
| `pdlt-v1-1.yml` | `ACTIVE` | no | no | success | 2026-09-02T14:41:13Z | **GREEN** | None |
| `phase4-no-hindsight-replay.yml` | `ACTIVE` | no | no | success | 2026-08-23T17:53:27Z | **GREEN** | None |
| `pullback-learning-gate.yml` | `ACTIVE` | no | no | success | 2026-08-31T02:53:56Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `pullback-learning-ledger.yml` | `ACTIVE` | yes | yes | success | 2026-09-03T05:13:31Z | **GREEN** | None |
| `remediation-maturation-gate.yml` | `ACTIVE` | no | no | success | 2026-08-31T00:58:50Z | **GREEN** | None |
| `remediation-maturation.yml` | `ACTIVE` | yes | yes | success | 2026-09-02T21:50:53Z | **GREEN** | None |
| `research-execution-coordinator.yml` | `ACTIVE` | yes | yes | success | 2026-09-02T21:46:02Z | **GREEN** | None |
| `research-owner-breadth-daily.yml` | `ACTIVE` | yes | yes | success | 2026-09-02T09:38:32Z | **GREEN** | None |
| `research-owner-btcd-daily.yml` | `ACTIVE` | yes | yes | success | 2026-09-02T09:52:07Z | **GREEN** | None |
| `rich-breadth-checkpoint.yml` | `ACTIVE` | yes | yes | success | 2026-09-03T04:40:16Z | **GREEN** | None |
| `round3-contract-freeze-gate.yml` | `ACTIVE` | no | no | success | 2026-08-25T21:03:50Z | **GREEN** | None |
| `round3-v2-materialization.yml` | `ACTIVE` | no | no | success | 2026-08-23T13:17:33Z | **GREEN** | None |
| `sequential-research-queue.yml` | `ACTIVE` | yes | yes | success | 2026-09-02T11:29:00Z | **GREEN** | None |
| `shadow-admission-ai-decider.yml` | `ACTIVE` | yes | yes | success | 2026-08-31T01:38:05Z | **GREEN** | None |
| `shadow-registry-autonomous-portfolio-gate.yml` | `ACTIVE` | no | no | success | 2026-08-22T19:41:03Z | **GREEN** | None |
| `shadow-registry-autonomous-portfolio-loop.yml` | `ACTIVE` | yes | yes | success | 2026-08-31T14:26:54Z | **GREEN** | None |
| `shadow-registry-gate.yml` | `ACTIVE` | no | no | success | 2026-09-02T21:30:54Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `shadow-registry-weekly.yml` | `ACTIVE` | yes | no | success | 2026-09-02T21:28:14Z | **GREEN** | None |
| `shared-row-prospective-evidence-loop.yml` | `ACTIVE` | yes | yes | success | 2026-09-03T00:43:28Z | **GREEN** | None |
| `shared-row-tournament-research-gate.yml` | `ACTIVE` | no | no | success | 2026-09-01T19:22:58Z | **GREEN** | None |
| `shared-row-tournament-weekly.yml` | `ACTIVE` | yes | yes | success | 2026-08-31T13:50:20Z | **GREEN** | None |
| `situation-room-daily-static.yml` | `ACTIVE` | yes | yes | success | 2026-09-02T11:19:08Z | **GREEN** | None |
| `situation-room-owner-live-gate.yml` | `ACTIVE` | no | no | success | 2026-09-01T16:30:25Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `source-provenance-recovery-gate.yml` | `ACTIVE` | no | no | success | 2026-08-23T11:29:50Z | **GREEN** | None |
| `source-provenance-recovery-loop.yml` | `ACTIVE` | yes | yes | success | 2026-09-02T09:22:46Z | **GREEN** | None |
| `specialist-architecture-gate.yml` | `ACTIVE` | no | no | success | 2026-08-23T11:29:50Z | **GREEN** | None |
| `storage-health-gate.yml` | `ACTIVE` | no | no | success | 2026-09-03T06:03:17Z | **GREEN** | None |
| `sunday-market-close-and-cfgi.yml` | `ACTIVE` | yes | yes | success | 2026-08-31T05:14:28Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `top100-breadth-owner-manual.yml` | `ACTIVE` | no | no | success | 2026-09-02T21:44:48Z | **GREEN** | None |
| `unified-experimental-lifecycle-adjudication.yml` | `ACTIVE` | yes | yes | success | 2026-08-31T14:55:52Z | **GREEN** | None |
| `validate_m3_forward_ledger.yml` | `ACTIVE` | no | no | none | none | **GREEN** | None |
| `weekly-api-calibration-shadow.yml` | `ACTIVE` | yes | yes | success | 2026-08-31T06:02:03Z | **GREEN** | None |
| `weekly-raw-calibration-bridge.yml` | `ACTIVE` | yes | yes | success | 2026-08-31T05:50:31Z | **GREEN** | None |
| `weekly-sol-adversarial-review.yml` | `ACTIVE` | yes | yes | success | 2026-08-31T09:40:25Z | **GREEN** | None |

## Blockers
- None

## Warnings
- REGISTERED_WITHOUT_LOCAL_FILE:agent-tool-shadow-round2.yml
- REGISTERED_WITHOUT_LOCAL_FILE:cfgi-full-profile-smoke-temp.yml
- REGISTERED_WITHOUT_LOCAL_FILE:cfgi-live-smoke-temp.yml
- REGISTERED_WITHOUT_LOCAL_FILE:forecast-skill-admission-gate.yml
- REGISTERED_WITHOUT_LOCAL_FILE:harness-redteam-p0-remediation-gate.yml
- REGISTERED_WITHOUT_LOCAL_FILE:historical-shadow-validation-stage1-manifest.yml
- REGISTERED_WITHOUT_LOCAL_FILE:persistent-agent-runtime-readiness-gate.yml
- REGISTERED_WITHOUT_LOCAL_FILE:t4-microstructure-live-readback.yml
- api-agent-gateway-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- automation-production-health-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- backtest-engine-foundation.yml:RECOVERING_AFTER_RECENT_FAILURES
- backtest-wave1-2-foundation.yml:RECOVERING_AFTER_RECENT_FAILURES
- buildwithclaude-shadow-round1.yml:RECOVERING_AFTER_RECENT_FAILURES
- cfgi-recovery-launch-trigger.yml:RECOVERING_AFTER_RECENT_FAILURES
- continuity-learning-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- daily-slow-cycle-shadow.yml:RECOVERING_AFTER_RECENT_FAILURES
- forecast-ratification-throughput-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- forecast-source-temporal-provenance-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- historical-altseason-cfgi-enrichment.yml:RETIRED_WORKFLOW_LOCAL_FILE_PRESENT
- historical-altseason-cfgi-reservation.yml:RETIRED_WORKFLOW_LOCAL_FILE_PRESENT
- historical-altseason-lab-gate.yml:ARTIFACT_RETENTION_UNBOUNDED
- historical-altseason-throughput-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- monthly-ai-learning-council-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- monthly-ai-learning-council.yml:NO_RUN_HISTORY
- operations-dashboard-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- pdlt-bootstrap-once.yml:EXPECTED_BLOCK
- pdlt-daily-census.yml:EXPECTED_BLOCK
- pdlt-discovery-once.yml:EXPECTED_BLOCK
- pdlt-maturation.yml:EXPECTED_BLOCK
- pullback-learning-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- shadow-registry-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- situation-room-owner-live-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- sunday-market-close-and-cfgi.yml:RECOVERING_AFTER_RECENT_FAILURES
