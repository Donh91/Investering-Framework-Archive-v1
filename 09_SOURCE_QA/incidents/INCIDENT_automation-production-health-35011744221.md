# Automation Production Health
Status: **RED**
Generated: `2026-09-15T19:07:57.038833Z`
Workflows: 152 local / 176 registered
Scheduled: 49
Writers: 55
GREEN / AMBER / RED: 117 / 28 / 7

## Workflow matrix
| Workflow | Lifecycle | Schedule | Writer | Last conclusion | Last run | Status | Findings |
|---|---|---:|---:|---|---|---|---|
| `adaptive-decision-miss-validation.yml` | `ACTIVE` | yes | yes | failure | 2026-09-15T00:51:29Z | **RED** | LATEST_RUN_FAILED, REPEATED_CONSECUTIVE_FAILURES |
| `adaptive-evidence-gap-gate.yml` | `ACTIVE` | no | no | success | 2026-09-13T11:09:41Z | **GREEN** | None |
| `adaptive-evidence-gap.yml` | `ACTIVE` | yes | yes | success | 2026-09-15T00:00:49Z | **GREEN** | None |
| `adaptive-gap-validation-gate.yml` | `ACTIVE` | no | no | success | 2026-08-26T14:16:58Z | **GREEN** | None |
| `adaptive-rotation-cadence.yml` | `ACTIVE` | yes | yes | success | 2026-09-15T15:01:10Z | **GREEN** | None |
| `api-agent-gateway-gate.yml` | `ACTIVE` | no | no | success | 2026-09-15T19:05:51Z | **GREEN** | None |
| `astra-landing-zone-gate.yml` | `ACTIVE` | no | no | success | 2026-09-13T09:52:24Z | **GREEN** | None |
| `auto-trading-e2-candidate-selection-v4.yml` | `ACTIVE` | no | no | success | 2026-09-14T14:33:03Z | **GREEN** | None |
| `auto-trading-e2-candidate-selection.yml` | `ACTIVE` | no | no | success | 2026-09-14T12:58:08Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `auto-trading-e2-compiler-reliability.yml` | `ACTIVE` | no | no | success | 2026-09-14T10:39:09Z | **GREEN** | None |
| `auto-trading-e2-reproducibility.yml` | `ACTIVE` | no | no | success | 2026-09-13T22:46:04Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `automation-production-health-gate.yml` | `ACTIVE` | no | no | success | 2026-09-15T19:05:51Z | **GREEN** | None |
| `automation-production-health.yml` | `ACTIVE` | yes | yes | in_progress | 2026-09-15T19:07:43Z | **GREEN** | None |
| `autonomous-research-governance-gate.yml` | `ACTIVE` | no | no | success | 2026-09-13T09:58:52Z | **GREEN** | None |
| `autonomous-research-governance-loop.yml` | `ACTIVE` | yes | yes | success | 2026-09-15T10:13:04Z | **GREEN** | None |
| `backtest-engine-foundation.yml` | `ACTIVE` | no | no | success | 2026-08-09T17:25:05Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `backtest-readiness-contracts.yml` | `ACTIVE` | no | no | success | 2026-09-05T20:39:59Z | **GREEN** | None |
| `backtest-wave1-2-foundation.yml` | `ACTIVE` | no | no | success | 2026-08-09T17:25:05Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `backtest-wave1-3-authority-lineage.yml` | `ACTIVE` | no | no | success | 2026-07-28T16:15:15Z | **GREEN** | None |
| `backtest-wave1-4-prospective.yml` | `ACTIVE` | yes | no | success | 2026-09-14T19:55:17Z | **GREEN** | None |
| `binance-spot-owner-manual.yml` | `ACTIVE` | no | no | success | 2026-08-01T19:31:36Z | **GREEN** | None |
| `binance-usdm-owner-manual.yml` | `ACTIVE` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `buildwithclaude-shadow-evidence-ledger.yml` | `ACTIVE` | no | no | success | 2026-09-02T16:22:23Z | **GREEN** | None |
| `buildwithclaude-shadow-prospective-observer.yml` | `ACTIVE` | no | no | success | 2026-09-04T23:29:35Z | **GREEN** | None |
| `buildwithclaude-shadow-round1.yml` | `ACTIVE` | no | no | success | 2026-09-02T16:22:23Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `cfgi-recovery-launch-once.yml` | `ACTIVE` | no | no | success | 2026-08-23T07:25:36Z | **GREEN** | None |
| `cfgi-recovery-launch-trigger.yml` | `ACTIVE` | no | yes | skipped | 2026-09-15T19:06:10Z | **GREEN** | None |
| `cfgi-v3-launch-receipt-publish.yml` | `ACTIVE` | no | yes | success | 2026-08-23T07:24:14Z | **GREEN** | None |
| `codex-intake-dispatch.yml` | `ACTIVE` | no | no | success | 2026-09-13T22:32:34Z | **GREEN** | None |
| `continuity-learning-gate.yml` | `ACTIVE` | no | no | success | 2026-09-15T19:05:51Z | **GREEN** | None |
| `continuity-learning-maintenance.yml` | `ACTIVE` | yes | yes | success | 2026-09-14T23:58:51Z | **GREEN** | None |
| `cowork-historical-altseason-bundle-gate.yml` | `ACTIVE` | no | no | success | 2026-08-21T09:47:00Z | **GREEN** | None |
| `cowork-historical-altseason-bundle-receipt.yml` | `ACTIVE` | no | yes | success | 2026-08-21T09:47:59Z | **GREEN** | None |
| `cowork-historical-altseason-bundle.yml` | `ACTIVE` | no | no | success | 2026-08-21T09:47:47Z | **GREEN** | None |
| `cross-repo-agent-context-gate.yml` | `ACTIVE` | no | no | success | 2026-09-14T13:43:04Z | **GREEN** | None |
| `cycle-navigator-autonomous-calibration-gate.yml` | `ACTIVE` | no | no | success | 2026-08-22T19:38:07Z | **GREEN** | None |
| `cycle-navigator-autonomous-calibration-loop.yml` | `ACTIVE` | yes | yes | success | 2026-09-14T13:01:58Z | **GREEN** | None |
| `cycle-navigator-internal-precision.yml` | `ACTIVE` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY |
| `cycle-navigator-pages.yml` | `ACTIVE` | no | no | success | 2026-09-15T08:12:10Z | **GREEN** | None |
| `cycle-navigator-precision-hardening-once.yml` | `ACTIVE` | no | no | failure | 2026-09-14T14:33:59Z | **GREEN** | None |
| `cycle-navigator-precision-hardening-v2-once.yml` | `ACTIVE` | no | no | failure | 2026-09-14T14:36:54Z | **GREEN** | None |
| `cycle-navigator-precision-hardening-v3-once.yml` | `ACTIVE` | no | no | success | 2026-09-14T14:38:47Z | **GREEN** | None |
| `cycle-navigator-public-contract-gate.yml` | `ACTIVE` | no | no | success | 2026-09-15T13:31:52Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `cycle-navigator-weekly-publication.yml` | `ACTIVE` | yes | yes | success | 2026-09-14T13:52:57Z | **GREEN** | None |
| `daily-capture-architecture-gate.yml` | `ACTIVE` | no | no | success | 2026-09-13T22:32:57Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `daily-director-shadow.yml` | `ACTIVE` | yes | yes | success | 2026-09-15T17:45:34Z | **GREEN** | None |
| `daily-machine-throughput-gate.yml` | `ACTIVE` | no | no | success | 2026-09-13T09:52:24Z | **GREEN** | None |
| `daily-machine-throughput.yml` | `ACTIVE` | yes | yes | success | 2026-09-15T00:59:24Z | **GREEN** | None |
| `daily-raw-owner-capture.yml` | `ACTIVE` | yes | yes | success | 2026-09-15T16:56:21Z | **GREEN** | None |
| `daily-settled-etf-calibration.yml` | `ACTIVE` | yes | yes | success | 2026-09-15T11:37:16Z | **GREEN** | None |
| `daily-slow-cycle-shadow.yml` | `ACTIVE` | yes | yes | success | 2026-09-15T09:34:23Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `daily-stablecoin-liquidity.yml` | `ACTIVE` | yes | yes | success | 2026-09-15T10:10:39Z | **GREEN** | None |
| `data-architecture-gate.yml` | `ACTIVE` | no | no | success | 2026-09-15T19:05:51Z | **GREEN** | None |
| `data-terminal-shadow-manual.yml` | `ACTIVE` | no | no | success | 2026-09-13T22:23:40Z | **GREEN** | None |
| `dataset-registry-gate.yml` | `ACTIVE` | no | no | success | 2026-09-04T23:12:36Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `entry-signal-ledger-gate.yml` | `ACTIVE` | no | no | failure | 2026-09-13T09:52:24Z | **RED** | REPEATED_CONSECUTIVE_FAILURES |
| `entry-signal-ledger.yml` | `ACTIVE` | yes | yes | success | 2026-09-15T17:19:02Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `ethbtc-persistence-lifecycle.yml` | `ACTIVE` | no | yes | success | 2026-09-15T17:46:35Z | **GREEN** | None |
| `evidence-closure-gate.yml` | `ACTIVE` | no | no | success | 2026-09-13T09:38:09Z | **GREEN** | None |
| `evidence-lifecycle-observability-gate.yml` | `ACTIVE` | no | no | success | 2026-09-13T09:52:24Z | **GREEN** | None |
| `evidence-lifecycle-store-health.yml` | `ACTIVE` | yes | no | success | 2026-09-15T08:42:39Z | **GREEN** | None |
| `experiment-lifecycle-gate.yml` | `ACTIVE` | no | no | success | 2026-09-14T19:16:04Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `external-alpha-registry-gate.yml` | `ACTIVE` | yes | no | success | 2026-09-14T12:37:59Z | **AMBER** | SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE |
| `fetch_btc_d_cmc_free.yml` | `ACTIVE` | no | no | success | 2026-07-12T00:09:38Z | **GREEN** | None |
| `forecast-exact-settlement-owner-gate.yml` | `ACTIVE` | no | no | success | 2026-09-13T10:54:28Z | **GREEN** | None |
| `forecast-materialization-census-gate.yml` | `ACTIVE` | no | no | success | 2026-09-03T22:00:37Z | **GREEN** | None |
| `forecast-outcome-supersession-gate.yml` | `ACTIVE` | no | no | success | 2026-09-13T10:54:28Z | **GREEN** | None |
| `forecast-ratification-throughput-gate.yml` | `ACTIVE` | no | no | success | 2026-09-03T22:00:37Z | **GREEN** | None |
| `forecast-settlement-accountability-gate.yml` | `ACTIVE` | no | no | success | 2026-09-15T09:06:21Z | **GREEN** | None |
| `forecast-skill-study-v132-gate.yml` | `ACTIVE` | no | no | failure | 2026-09-15T09:06:21Z | **GREEN** | None |
| `forecast-source-temporal-provenance-gate.yml` | `ACTIVE` | no | no | success | 2026-09-13T09:52:24Z | **GREEN** | None |
| `framework-intelligence-phase1-live-shadow.yml` | `ACTIVE` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY |
| `framework-learning-operations.yml` | `ACTIVE` | yes | yes | cancelled | 2026-09-15T06:12:03Z | **RED** | LATEST_RUN_FAILED |
| `framework-learning-supervisor.yml` | `ACTIVE` | yes | yes | success | 2026-09-15T07:59:42Z | **GREEN** | None |
| `full-architecture-1to7-gate.yml` | `ACTIVE` | no | no | success | 2026-09-15T19:05:51Z | **GREEN** | None |
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
| `historical-research-vault-gate.yml` | `ACTIVE` | no | no | success | 2026-09-04T23:12:36Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `hourly-sequence-capture.yml` | `ACTIVE` | yes | yes | success | 2026-09-15T18:06:52Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `intraday-execution-gate.yml` | `ACTIVE` | no | no | success | 2026-09-13T22:23:40Z | **GREEN** | None |
| `intraday-execution-research.yml` | `ACTIVE` | no | yes | success | 2026-08-31T00:03:54Z | **GREEN** | None |
| `legacy-knowledge-bootstrap-gate.yml` | `ACTIVE` | no | no | success | 2026-08-04T19:08:35Z | **GREEN** | None |
| `mar_wp04c4_gate.yml` | `ACTIVE` | no | no | success | 2026-07-31T01:41:02Z | **GREEN** | None |
| `master-monday-precision-repair-once.yml` | `ACTIVE` | no | no | success | 2026-09-14T14:30:57Z | **GREEN** | None |
| `master-monday-preflight-gate.yml` | `ACTIVE` | no | no | success | 2026-09-15T12:57:11Z | **GREEN** | None |
| `master-monday-remaining-gaps.yml` | `ACTIVE` | yes | yes | success | 2026-09-14T10:12:08Z | **GREEN** | None |
| `master-monday-w37-redispatch-once.yml` | `ACTIVE` | no | no | success | 2026-09-14T14:40:27Z | **GREEN** | None |
| `meme-alpha-moonshot-cohort-gate.yml` | `ACTIVE` | no | no | success | 2026-09-14T18:49:56Z | **GREEN** | None |
| `meme-alpha-moonshot-gate.yml` | `ACTIVE` | no | no | success | 2026-09-14T18:49:55Z | **GREEN** | None |
| `meme-alpha-runtime-gate.yml` | `ACTIVE` | no | no | in_progress | 2026-09-15T19:09:07Z | **GREEN** | None |
| `monthly-ai-learning-council-bootstrap-once.yml` | `ACTIVE` | no | no | success | 2026-09-03T06:03:59Z | **GREEN** | None |
| `monthly-ai-learning-council-gate.yml` | `ACTIVE` | no | no | success | 2026-09-13T09:52:24Z | **GREEN** | None |
| `monthly-ai-learning-council.yml` | `ACTIVE` | yes | yes | success | 2026-09-15T09:26:18Z | **GREEN** | None |
| `native-handlekompas.yml` | `ACTIVE` | yes | yes | success | 2026-09-15T17:19:40Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `native-market-recovery.yml` | `ACTIVE` | yes | yes | success | 2026-09-15T18:23:23Z | **GREEN** | None |
| `native-ota-research-readback.yml` | `ACTIVE` | yes | yes | success | 2026-09-15T05:25:10Z | **GREEN** | None |
| `okx-swap-owner-manual.yml` | `ACTIVE` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `operations-dashboard-gate.yml` | `ACTIVE` | no | no | success | 2026-08-27T15:43:00Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `operations-dashboard.yml` | `ACTIVE` | yes | yes | success | 2026-09-15T09:18:02Z | **GREEN** | None |
| `operations-recovery-launch-once.yml` | `ACTIVE` | no | no | success | 2026-08-31T16:26:39Z | **GREEN** | None |
| `owner-bound-daily-director-manual.yml` | `ACTIVE` | no | no | success | 2026-09-15T19:09:07Z | **GREEN** | None |
| `pdf-inspector-ingestion.yml` | `ACTIVE` | no | no | success | 2026-08-02T18:16:02Z | **GREEN** | None |
| `pdlt-bootstrap-once.yml` | `EXPECTED_BLOCK` | no | no | skipped | 2026-08-10T15:36:07Z | **AMBER** | EXPECTED_BLOCK |
| `pdlt-daily-census.yml` | `EXPECTED_BLOCK` | no | no | success | 2026-09-01T23:35:24Z | **AMBER** | EXPECTED_BLOCK |
| `pdlt-discovery-once.yml` | `EXPECTED_BLOCK` | no | no | failure | 2026-08-09T19:58:23Z | **AMBER** | EXPECTED_BLOCK |
| `pdlt-maturation.yml` | `EXPECTED_BLOCK` | no | no | success | 2026-09-02T00:19:38Z | **AMBER** | EXPECTED_BLOCK |
| `pdlt-runtime-gate.yml` | `ACTIVE` | no | no | success | 2026-09-02T14:40:09Z | **GREEN** | None |
| `pdlt-v1-1.yml` | `ACTIVE` | no | no | success | 2026-09-02T14:41:13Z | **GREEN** | None |
| `phase4-no-hindsight-replay.yml` | `ACTIVE` | no | no | success | 2026-08-23T17:53:27Z | **GREEN** | None |
| `provider-budget-readback.yml` | `ACTIVE` | no | yes | success | 2026-09-15T16:57:00Z | **GREEN** | None |
| `pullback-learning-gate.yml` | `ACTIVE` | no | no | failure | 2026-09-13T09:52:24Z | **RED** | REPEATED_CONSECUTIVE_FAILURES |
| `pullback-learning-ledger.yml` | `ACTIVE` | yes | yes | cancelled | 2026-09-15T17:19:31Z | **RED** | LATEST_RUN_FAILED |
| `remediation-maturation-gate.yml` | `ACTIVE` | no | no | success | 2026-09-13T17:17:30Z | **GREEN** | None |
| `remediation-maturation.yml` | `ACTIVE` | yes | yes | success | 2026-09-15T08:58:48Z | **GREEN** | None |
| `research-execution-coordinator.yml` | `ACTIVE` | yes | yes | success | 2026-09-15T12:37:30Z | **GREEN** | None |
| `research-owner-breadth-daily.yml` | `ACTIVE` | yes | yes | success | 2026-09-15T10:05:22Z | **GREEN** | None |
| `research-owner-btcd-daily.yml` | `ACTIVE` | yes | yes | success | 2026-09-15T10:23:55Z | **GREEN** | None |
| `rich-breadth-checkpoint.yml` | `ACTIVE` | yes | yes | success | 2026-09-15T13:39:50Z | **GREEN** | None |
| `round3-contract-freeze-gate.yml` | `ACTIVE` | no | no | success | 2026-09-13T09:52:24Z | **GREEN** | None |
| `round3-v2-materialization.yml` | `ACTIVE` | no | no | success | 2026-08-23T13:17:33Z | **GREEN** | None |
| `sequential-research-queue.yml` | `ACTIVE` | yes | yes | success | 2026-09-15T11:53:28Z | **GREEN** | None |
| `shadow-admission-ai-decider.yml` | `ACTIVE` | yes | yes | success | 2026-09-14T01:43:36Z | **GREEN** | None |
| `shadow-registry-autonomous-portfolio-gate.yml` | `ACTIVE` | no | no | success | 2026-08-22T19:41:03Z | **GREEN** | None |
| `shadow-registry-autonomous-portfolio-loop.yml` | `ACTIVE` | yes | yes | success | 2026-09-14T13:22:21Z | **GREEN** | None |
| `shadow-registry-gate.yml` | `ACTIVE` | no | no | action_required | 2026-09-14T10:57:31Z | **GREEN** | None |
| `shadow-registry-weekly.yml` | `ACTIVE` | yes | no | success | 2026-09-14T10:57:05Z | **GREEN** | None |
| `shared-row-prospective-evidence-loop.yml` | `ACTIVE` | yes | yes | success | 2026-09-15T15:16:57Z | **GREEN** | None |
| `shared-row-tournament-research-gate.yml` | `ACTIVE` | no | no | success | 2026-09-13T09:58:52Z | **GREEN** | None |
| `shared-row-tournament-weekly.yml` | `ACTIVE` | yes | yes | success | 2026-09-14T12:47:16Z | **GREEN** | None |
| `situation-room-daily-static.yml` | `ACTIVE` | yes | yes | failure | 2026-09-15T11:44:53Z | **RED** | LATEST_RUN_FAILED, REPEATED_CONSECUTIVE_FAILURES |
| `situation-room-owner-live-gate.yml` | `ACTIVE` | no | no | success | 2026-09-13T22:23:40Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `situation-room-shadow-bridge.yml` | `ACTIVE` | yes | yes | failure | 2026-09-15T12:02:34Z | **RED** | LATEST_RUN_FAILED, REPEATED_CONSECUTIVE_FAILURES |
| `source-provenance-recovery-gate.yml` | `ACTIVE` | no | no | success | 2026-08-23T11:29:50Z | **GREEN** | None |
| `source-provenance-recovery-loop.yml` | `ACTIVE` | yes | yes | success | 2026-09-15T09:52:22Z | **GREEN** | None |
| `specialist-architecture-gate.yml` | `ACTIVE` | no | no | success | 2026-08-23T11:29:50Z | **GREEN** | None |
| `storage-health-gate.yml` | `ACTIVE` | no | no | success | 2026-09-15T19:09:07Z | **GREEN** | None |
| `sunday-market-close-and-cfgi.yml` | `ACTIVE` | yes | yes | success | 2026-09-14T04:37:56Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `top100-breadth-owner-manual.yml` | `ACTIVE` | no | no | success | 2026-09-02T21:44:48Z | **GREEN** | None |
| `unified-experimental-lifecycle-adjudication.yml` | `ACTIVE` | yes | yes | success | 2026-09-14T13:45:29Z | **GREEN** | None |
| `validate_m3_forward_ledger.yml` | `ACTIVE` | no | no | none | none | **GREEN** | None |
| `weekly-api-calibration-shadow.yml` | `ACTIVE` | yes | yes | success | 2026-09-14T14:40:32Z | **GREEN** | None |
| `weekly-raw-calibration-bridge.yml` | `ACTIVE` | yes | yes | success | 2026-09-14T05:11:39Z | **GREEN** | None |
| `weekly-sol-adversarial-review.yml` | `ACTIVE` | yes | yes | success | 2026-09-14T08:51:01Z | **GREEN** | None |

## Blockers
- adaptive-decision-miss-validation.yml:LATEST_RUN_FAILED
- adaptive-decision-miss-validation.yml:REPEATED_CONSECUTIVE_FAILURES
- entry-signal-ledger-gate.yml:REPEATED_CONSECUTIVE_FAILURES
- framework-learning-operations.yml:LATEST_RUN_FAILED
- pullback-learning-gate.yml:REPEATED_CONSECUTIVE_FAILURES
- pullback-learning-ledger.yml:LATEST_RUN_FAILED
- situation-room-daily-static.yml:LATEST_RUN_FAILED
- situation-room-daily-static.yml:REPEATED_CONSECUTIVE_FAILURES
- situation-room-shadow-bridge.yml:LATEST_RUN_FAILED
- situation-room-shadow-bridge.yml:REPEATED_CONSECUTIVE_FAILURES

## Warnings
- REGISTERED_WITHOUT_LOCAL_FILE:_temporary-automation-health-diagnostic.yml
- REGISTERED_WITHOUT_LOCAL_FILE:_temporary-repair-one-time-writer-triggers.yml
- REGISTERED_WITHOUT_LOCAL_FILE:agent-tool-shadow-round2.yml
- REGISTERED_WITHOUT_LOCAL_FILE:cfgi-full-profile-smoke-temp.yml
- REGISTERED_WITHOUT_LOCAL_FILE:cfgi-live-smoke-temp.yml
- REGISTERED_WITHOUT_LOCAL_FILE:cn-internal-precision-bootstrap-20260914.yml
- REGISTERED_WITHOUT_LOCAL_FILE:cn-internal-precision-bootstrap-v2-20260914.yml
- REGISTERED_WITHOUT_LOCAL_FILE:cn-internal-precision-engine-once.yml
- REGISTERED_WITHOUT_LOCAL_FILE:cn-internal-precision-v2-branch-test.yml
- REGISTERED_WITHOUT_LOCAL_FILE:cn26-refresh-once-20260914.yml
- REGISTERED_WITHOUT_LOCAL_FILE:e2-artifact-byte-exact-correction.yml
- REGISTERED_WITHOUT_LOCAL_FILE:edgeonchain-e0-identity-probe-once.yml
- REGISTERED_WITHOUT_LOCAL_FILE:edgeonchain-e1-ledger-capture-once.yml
- REGISTERED_WITHOUT_LOCAL_FILE:edgeonchain-e1-retain-on-branch-once.yml
- REGISTERED_WITHOUT_LOCAL_FILE:forecast-skill-admission-gate.yml
- REGISTERED_WITHOUT_LOCAL_FILE:harness-redteam-p0-remediation-gate.yml
- REGISTERED_WITHOUT_LOCAL_FILE:historical-shadow-validation-stage1-manifest.yml
- REGISTERED_WITHOUT_LOCAL_FILE:meme-alpha-ian-g2g3-research.yml
- REGISTERED_WITHOUT_LOCAL_FILE:memes-alpha-research-gate.yml
- REGISTERED_WITHOUT_LOCAL_FILE:native-market-recovery-v1-1.yml
- REGISTERED_WITHOUT_LOCAL_FILE:one-shot-cfgi-w36-rebuild.yml
- REGISTERED_WITHOUT_LOCAL_FILE:persistent-agent-runtime-readiness-gate.yml
- REGISTERED_WITHOUT_LOCAL_FILE:t4-microstructure-live-readback.yml
- REGISTERED_WITHOUT_LOCAL_FILE:zero-manual-feed-graduation.yml
- auto-trading-e2-candidate-selection.yml:RECOVERING_AFTER_RECENT_FAILURES
- auto-trading-e2-reproducibility.yml:RECOVERING_AFTER_RECENT_FAILURES
- backtest-engine-foundation.yml:RECOVERING_AFTER_RECENT_FAILURES
- backtest-wave1-2-foundation.yml:RECOVERING_AFTER_RECENT_FAILURES
- buildwithclaude-shadow-round1.yml:RECOVERING_AFTER_RECENT_FAILURES
- cycle-navigator-internal-precision.yml:NO_RUN_HISTORY
- cycle-navigator-public-contract-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- daily-capture-architecture-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- daily-slow-cycle-shadow.yml:RECOVERING_AFTER_RECENT_FAILURES
- dataset-registry-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- entry-signal-ledger.yml:RECOVERING_AFTER_RECENT_FAILURES
- experiment-lifecycle-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- external-alpha-registry-gate.yml:SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE
- framework-intelligence-phase1-live-shadow.yml:NO_RUN_HISTORY
- historical-altseason-cfgi-enrichment.yml:RETIRED_WORKFLOW_LOCAL_FILE_PRESENT
- historical-altseason-cfgi-reservation.yml:RETIRED_WORKFLOW_LOCAL_FILE_PRESENT
- historical-altseason-lab-gate.yml:ARTIFACT_RETENTION_UNBOUNDED
- historical-altseason-throughput-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- historical-research-vault-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- hourly-sequence-capture.yml:RECOVERING_AFTER_RECENT_FAILURES
- native-handlekompas.yml:RECOVERING_AFTER_RECENT_FAILURES
- operations-dashboard-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- pdlt-bootstrap-once.yml:EXPECTED_BLOCK
- pdlt-daily-census.yml:EXPECTED_BLOCK
- pdlt-discovery-once.yml:EXPECTED_BLOCK
- pdlt-maturation.yml:EXPECTED_BLOCK
- situation-room-owner-live-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- sunday-market-close-and-cfgi.yml:RECOVERING_AFTER_RECENT_FAILURES
