# Automation Production Health
Status: **RED**
Generated: `2026-09-18T18:35:15.158500Z`
Workflows: 172 local / 196 registered
Scheduled: 53
Writers: 58
GREEN / AMBER / RED: 145 / 19 / 8

## Workflow matrix
| Workflow | Lifecycle | Schedule | Writer | Last conclusion | Last run | Status | Findings |
|---|---|---:|---:|---|---|---|---|
| `adaptive-decision-miss-validation.yml` | `ACTIVE` | yes | yes | failure | 2026-09-18T00:44:22Z | **RED** | LATEST_RUN_FAILED, REPEATED_CONSECUTIVE_FAILURES |
| `adaptive-evidence-gap-gate.yml` | `ACTIVE` | no | no | success | 2026-09-13T11:09:41Z | **GREEN** | None |
| `adaptive-evidence-gap.yml` | `ACTIVE` | yes | yes | success | 2026-09-17T23:44:00Z | **GREEN** | None |
| `adaptive-gap-validation-gate.yml` | `ACTIVE` | no | no | success | 2026-08-26T14:16:58Z | **GREEN** | None |
| `adaptive-rotation-cadence.yml` | `ACTIVE` | yes | yes | success | 2026-09-18T14:31:48Z | **GREEN** | None |
| `alpha-arc-live-replay.yml` | `ACTIVE` | no | no | success | 2026-09-16T19:33:35Z | **GREEN** | None |
| `api-agent-gateway-gate.yml` | `ACTIVE` | no | no | success | 2026-09-18T17:46:39Z | **GREEN** | None |
| `askr-launch-sentinel.yml` | `ACTIVE` | no | no | failure | 2026-09-18T18:33:34Z | **RED** | REPEATED_CONSECUTIVE_FAILURES |
| `astra-landing-zone-gate.yml` | `ACTIVE` | no | no | success | 2026-09-18T06:11:13Z | **GREEN** | None |
| `auto-trading-e2-candidate-selection-v4.yml` | `ACTIVE` | no | no | success | 2026-09-14T14:33:03Z | **GREEN** | None |
| `auto-trading-e2-candidate-selection.yml` | `ACTIVE` | no | no | success | 2026-09-14T12:58:08Z | **GREEN** | None |
| `auto-trading-e2-compiler-reliability.yml` | `ACTIVE` | no | no | success | 2026-09-14T10:39:09Z | **GREEN** | None |
| `auto-trading-e2-reproducibility.yml` | `ACTIVE` | no | no | success | 2026-09-13T22:46:04Z | **GREEN** | None |
| `automation-production-health-gate.yml` | `ACTIVE` | no | no | success | 2026-09-18T17:53:33Z | **GREEN** | None |
| `automation-production-health.yml` | `ACTIVE` | yes | yes | in_progress | 2026-09-18T18:34:59Z | **GREEN** | None |
| `autonomous-research-governance-gate.yml` | `ACTIVE` | no | no | success | 2026-09-13T09:58:52Z | **GREEN** | None |
| `autonomous-research-governance-loop.yml` | `ACTIVE` | yes | yes | success | 2026-09-18T09:55:33Z | **GREEN** | None |
| `backtest-engine-foundation.yml` | `ACTIVE` | no | no | success | 2026-08-09T17:25:05Z | **GREEN** | None |
| `backtest-readiness-contracts.yml` | `ACTIVE` | no | no | success | 2026-09-05T20:39:59Z | **GREEN** | None |
| `backtest-wave1-2-foundation.yml` | `ACTIVE` | no | no | success | 2026-08-09T17:25:05Z | **GREEN** | None |
| `backtest-wave1-3-authority-lineage.yml` | `ACTIVE` | no | no | success | 2026-07-28T16:15:15Z | **GREEN** | None |
| `backtest-wave1-4-prospective.yml` | `ACTIVE` | yes | no | success | 2026-09-17T19:13:11Z | **GREEN** | None |
| `binance-spot-owner-manual.yml` | `ACTIVE` | no | no | success | 2026-08-01T19:31:36Z | **GREEN** | None |
| `binance-usdm-owner-manual.yml` | `ACTIVE` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `buildwithclaude-shadow-evidence-ledger.yml` | `ACTIVE` | no | no | success | 2026-09-02T16:22:23Z | **GREEN** | None |
| `buildwithclaude-shadow-prospective-observer.yml` | `ACTIVE` | no | no | success | 2026-09-04T23:29:35Z | **GREEN** | None |
| `buildwithclaude-shadow-round1.yml` | `ACTIVE` | no | no | success | 2026-09-02T16:22:23Z | **GREEN** | None |
| `cfgi-recovery-launch-once.yml` | `ACTIVE` | no | no | success | 2026-08-23T07:25:36Z | **GREEN** | None |
| `cfgi-recovery-launch-trigger.yml` | `ACTIVE` | no | yes | skipped | 2026-09-18T18:01:18Z | **GREEN** | None |
| `cfgi-v3-launch-receipt-publish.yml` | `ACTIVE` | no | yes | success | 2026-08-23T07:24:14Z | **GREEN** | None |
| `cn-site-v2-gate.yml` | `ACTIVE` | no | no | success | 2026-09-18T17:53:33Z | **GREEN** | None |
| `codex-intake-dispatch.yml` | `ACTIVE` | no | no | success | 2026-09-18T07:25:33Z | **GREEN** | None |
| `compass-event-refresh.yml` | `ACTIVE` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY, SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE |
| `compass-outcomes.yml` | `ACTIVE` | yes | yes | cancelled | 2026-09-18T17:54:47Z | **AMBER** | LATEST_RUN_CANCELLED |
| `compass-production-bootstrap.yml` | `ACTIVE` | no | no | success | 2026-09-18T17:54:37Z | **GREEN** | None |
| `compass-schedule-watchdog.yml` | `ACTIVE` | yes | no | none | none | **AMBER** | NO_RUN_HISTORY, SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE |
| `continuity-learning-gate.yml` | `ACTIVE` | no | no | success | 2026-09-18T18:00:55Z | **GREEN** | None |
| `continuity-learning-maintenance.yml` | `ACTIVE` | yes | yes | success | 2026-09-17T23:40:56Z | **GREEN** | None |
| `cowork-historical-altseason-bundle-gate.yml` | `ACTIVE` | no | no | success | 2026-08-21T09:47:00Z | **GREEN** | None |
| `cowork-historical-altseason-bundle-receipt.yml` | `ACTIVE` | no | yes | success | 2026-08-21T09:47:59Z | **GREEN** | None |
| `cowork-historical-altseason-bundle.yml` | `ACTIVE` | no | no | success | 2026-08-21T09:47:47Z | **GREEN** | None |
| `cross-repo-agent-context-gate.yml` | `ACTIVE` | no | no | success | 2026-09-17T20:52:05Z | **GREEN** | None |
| `cycle-navigator-autonomous-calibration-gate.yml` | `ACTIVE` | no | no | success | 2026-08-22T19:38:07Z | **GREEN** | None |
| `cycle-navigator-autonomous-calibration-loop.yml` | `ACTIVE` | yes | yes | success | 2026-09-14T13:01:58Z | **GREEN** | None |
| `cycle-navigator-internal-precision.yml` | `ACTIVE` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY |
| `cycle-navigator-pages.yml` | `ACTIVE` | no | no | success | 2026-09-18T18:04:56Z | **GREEN** | None |
| `cycle-navigator-precision-hardening-once.yml` | `ACTIVE` | no | no | failure | 2026-09-14T14:33:59Z | **GREEN** | None |
| `cycle-navigator-precision-hardening-v2-once.yml` | `ACTIVE` | no | no | failure | 2026-09-14T14:36:54Z | **GREEN** | None |
| `cycle-navigator-precision-hardening-v3-once.yml` | `ACTIVE` | no | no | success | 2026-09-14T14:38:47Z | **GREEN** | None |
| `cycle-navigator-public-contract-gate.yml` | `ACTIVE` | no | no | success | 2026-09-18T17:54:37Z | **GREEN** | None |
| `cycle-navigator-weekly-publication.yml` | `ACTIVE` | yes | yes | success | 2026-09-14T13:52:57Z | **GREEN** | None |
| `daily-capture-architecture-gate.yml` | `ACTIVE` | no | no | success | 2026-09-15T22:45:47Z | **GREEN** | None |
| `daily-compass.yml` | `ACTIVE` | yes | yes | success | 2026-09-18T18:04:36Z | **AMBER** | SCHEDULE_STALE, SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE |
| `daily-director-shadow.yml` | `ACTIVE` | yes | yes | success | 2026-09-18T17:12:14Z | **GREEN** | None |
| `daily-machine-throughput-gate.yml` | `ACTIVE` | no | no | success | 2026-09-13T09:52:24Z | **GREEN** | None |
| `daily-machine-throughput.yml` | `ACTIVE` | yes | yes | success | 2026-09-18T00:49:34Z | **GREEN** | None |
| `daily-raw-owner-capture.yml` | `ACTIVE` | yes | yes | success | 2026-09-18T16:21:52Z | **GREEN** | None |
| `daily-settled-etf-calibration.yml` | `ACTIVE` | yes | yes | failure | 2026-09-18T11:05:29Z | **RED** | LATEST_RUN_FAILED |
| `daily-slow-cycle-shadow.yml` | `ACTIVE` | yes | yes | success | 2026-09-18T09:10:30Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `daily-stablecoin-liquidity.yml` | `ACTIVE` | yes | yes | success | 2026-09-18T09:53:41Z | **GREEN** | None |
| `data-architecture-gate.yml` | `ACTIVE` | no | no | success | 2026-09-18T18:00:55Z | **GREEN** | None |
| `data-terminal-shadow-manual.yml` | `ACTIVE` | no | no | success | 2026-09-13T22:23:40Z | **GREEN** | None |
| `dataset-registry-gate.yml` | `ACTIVE` | no | no | success | 2026-09-04T23:12:36Z | **GREEN** | None |
| `entry-signal-ledger-gate.yml` | `ACTIVE` | no | no | failure | 2026-09-13T09:52:24Z | **AMBER** | PR_GATE_REJECTION, REPEATED_PR_GATE_REJECTIONS |
| `entry-signal-ledger.yml` | `ACTIVE` | yes | yes | success | 2026-09-18T16:45:05Z | **GREEN** | None |
| `ethbtc-persistence-lifecycle.yml` | `ACTIVE` | no | yes | success | 2026-09-18T17:13:02Z | **GREEN** | None |
| `evidence-closure-gate.yml` | `ACTIVE` | no | no | success | 2026-09-13T09:38:09Z | **GREEN** | None |
| `evidence-lifecycle-observability-gate.yml` | `ACTIVE` | no | no | success | 2026-09-13T09:52:24Z | **GREEN** | None |
| `evidence-lifecycle-store-health.yml` | `ACTIVE` | yes | no | success | 2026-09-18T08:16:42Z | **GREEN** | None |
| `experiment-lifecycle-gate.yml` | `ACTIVE` | no | no | success | 2026-09-18T13:25:18Z | **GREEN** | None |
| `external-alpha-registry-gate.yml` | `ACTIVE` | yes | no | success | 2026-09-14T12:37:59Z | **AMBER** | SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE |
| `fetch_btc_d_cmc_free.yml` | `ACTIVE` | no | no | success | 2026-07-12T00:09:38Z | **GREEN** | None |
| `forecast-exact-settlement-owner-gate.yml` | `ACTIVE` | no | no | success | 2026-09-18T13:25:18Z | **GREEN** | None |
| `forecast-materialization-census-gate.yml` | `ACTIVE` | no | no | success | 2026-09-18T13:21:03Z | **GREEN** | None |
| `forecast-outcome-supersession-gate.yml` | `ACTIVE` | no | no | success | 2026-09-18T13:25:18Z | **GREEN** | None |
| `forecast-ratification-throughput-gate.yml` | `ACTIVE` | no | no | success | 2026-09-18T13:21:03Z | **GREEN** | None |
| `forecast-settlement-accountability-gate.yml` | `ACTIVE` | no | no | success | 2026-09-18T08:13:51Z | **GREEN** | None |
| `forecast-skill-study-v132-gate.yml` | `ACTIVE` | no | no | success | 2026-09-18T13:21:03Z | **GREEN** | None |
| `forecast-source-temporal-provenance-gate.yml` | `ACTIVE` | no | no | success | 2026-09-18T13:21:03Z | **GREEN** | None |
| `framework-intelligence-phase1-live-shadow.yml` | `ACTIVE` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY |
| `framework-learning-operations.yml` | `ACTIVE` | yes | yes | failure | 2026-09-18T05:59:34Z | **RED** | LATEST_RUN_FAILED, REPEATED_CONSECUTIVE_FAILURES |
| `framework-learning-supervisor.yml` | `ACTIVE` | yes | yes | failure | 2026-09-18T07:35:25Z | **RED** | LATEST_RUN_FAILED, REPEATED_CONSECUTIVE_FAILURES |
| `full-architecture-1to7-gate.yml` | `ACTIVE` | no | no | success | 2026-09-18T18:00:55Z | **GREEN** | None |
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
| `historical-altseason-throughput-gate.yml` | `ACTIVE` | no | no | success | 2026-08-27T15:43:00Z | **GREEN** | None |
| `historical-research-vault-gate.yml` | `ACTIVE` | no | no | success | 2026-09-04T23:12:36Z | **GREEN** | None |
| `hourly-sequence-capture.yml` | `ACTIVE` | yes | yes | success | 2026-09-18T18:19:13Z | **GREEN** | None |
| `intraday-execution-gate.yml` | `ACTIVE` | no | no | success | 2026-09-13T22:23:40Z | **GREEN** | None |
| `intraday-execution-research.yml` | `ACTIVE` | no | yes | success | 2026-08-31T00:03:54Z | **GREEN** | None |
| `legacy-knowledge-bootstrap-gate.yml` | `ACTIVE` | no | no | success | 2026-08-04T19:08:35Z | **GREEN** | None |
| `mar_wp04c4_gate.yml` | `ACTIVE` | no | no | success | 2026-07-31T01:41:02Z | **GREEN** | None |
| `master-monday-precision-repair-once.yml` | `ACTIVE` | no | no | success | 2026-09-14T14:30:57Z | **GREEN** | None |
| `master-monday-preflight-gate.yml` | `ACTIVE` | no | no | success | 2026-09-18T13:23:23Z | **GREEN** | None |
| `master-monday-remaining-gaps.yml` | `ACTIVE` | yes | yes | success | 2026-09-14T10:12:08Z | **GREEN** | None |
| `master-monday-w37-redispatch-once.yml` | `ACTIVE` | no | no | success | 2026-09-14T14:40:27Z | **GREEN** | None |
| `meme-alpha-clean-g3-core.yml` | `ACTIVE` | no | no | success | 2026-09-15T20:13:26Z | **GREEN** | None |
| `meme-alpha-ian-g2g3-research.yml` | `ACTIVE` | no | no | success | 2026-09-15T19:12:27Z | **GREEN** | None |
| `meme-alpha-moonshot-cohort-gate.yml` | `ACTIVE` | no | no | success | 2026-09-16T13:06:33Z | **GREEN** | None |
| `meme-alpha-moonshot-gate.yml` | `ACTIVE` | no | no | success | 2026-09-18T17:46:39Z | **GREEN** | None |
| `meme-alpha-red-causal-pair-replay.yml` | `ACTIVE` | no | no | success | 2026-09-15T20:43:39Z | **GREEN** | None |
| `meme-alpha-red-cohort-schema.yml` | `ACTIVE` | no | no | success | 2026-09-15T20:17:19Z | **GREEN** | None |
| `meme-alpha-red-detector-semantics.yml` | `ACTIVE` | no | no | success | 2026-09-15T20:39:00Z | **GREEN** | None |
| `meme-alpha-red-earliest-first-buy.yml` | `ACTIVE` | no | no | success | 2026-09-15T23:25:24Z | **GREEN** | None |
| `meme-alpha-red-first10-first-buy.yml` | `ACTIVE` | no | no | success | 2026-09-16T10:04:02Z | **GREEN** | None |
| `meme-alpha-red-scale-census.yml` | `ACTIVE` | no | no | success | 2026-09-16T01:35:46Z | **GREEN** | None |
| `meme-alpha-red-sellability-outcomes.yml` | `ACTIVE` | no | no | success | 2026-09-16T01:28:17Z | **GREEN** | None |
| `meme-alpha-red-trade-event-decode.yml` | `ACTIVE` | no | no | success | 2026-09-15T20:51:14Z | **GREEN** | None |
| `meme-alpha-red-tx-reconstruction.yml` | `ACTIVE` | no | no | success | 2026-09-15T20:31:11Z | **GREEN** | None |
| `meme-alpha-runtime-gate.yml` | `ACTIVE` | no | no | success | 2026-09-16T19:56:26Z | **GREEN** | None |
| `meme-alpha-trenches-point-in-time.yml` | `ACTIVE` | no | no | success | 2026-09-15T20:06:36Z | **GREEN** | None |
| `monthly-ai-learning-council-bootstrap-once.yml` | `ACTIVE` | no | no | success | 2026-09-03T06:03:59Z | **GREEN** | None |
| `monthly-ai-learning-council-gate.yml` | `ACTIVE` | no | no | success | 2026-09-13T09:52:24Z | **GREEN** | None |
| `monthly-ai-learning-council.yml` | `ACTIVE` | yes | yes | success | 2026-09-18T09:00:46Z | **GREEN** | None |
| `native-handlekompas.yml` | `ACTIVE` | yes | yes | success | 2026-09-18T15:26:31Z | **GREEN** | None |
| `native-market-recovery.yml` | `ACTIVE` | yes | yes | success | 2026-09-18T16:38:10Z | **GREEN** | None |
| `native-ota-research-readback.yml` | `ACTIVE` | yes | yes | success | 2026-09-18T05:15:34Z | **GREEN** | None |
| `okx-swap-owner-manual.yml` | `ACTIVE` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `operations-dashboard-gate.yml` | `ACTIVE` | no | no | success | 2026-09-15T23:21:25Z | **GREEN** | None |
| `operations-dashboard.yml` | `ACTIVE` | yes | yes | failure | 2026-09-18T08:54:28Z | **RED** | LATEST_RUN_FAILED, REPEATED_CONSECUTIVE_FAILURES |
| `operations-recovery-launch-once.yml` | `ACTIVE` | no | no | success | 2026-08-31T16:26:39Z | **GREEN** | None |
| `owner-bound-daily-director-manual.yml` | `ACTIVE` | no | no | success | 2026-09-18T17:46:39Z | **GREEN** | None |
| `pdf-inspector-ingestion.yml` | `ACTIVE` | no | no | success | 2026-08-02T18:16:02Z | **GREEN** | None |
| `pdlt-bootstrap-once.yml` | `EXPECTED_BLOCK` | no | no | skipped | 2026-08-10T15:36:07Z | **AMBER** | EXPECTED_BLOCK |
| `pdlt-daily-census.yml` | `EXPECTED_BLOCK` | no | no | success | 2026-09-01T23:35:24Z | **AMBER** | EXPECTED_BLOCK |
| `pdlt-discovery-once.yml` | `EXPECTED_BLOCK` | no | no | failure | 2026-08-09T19:58:23Z | **AMBER** | EXPECTED_BLOCK |
| `pdlt-maturation.yml` | `EXPECTED_BLOCK` | no | no | success | 2026-09-02T00:19:38Z | **AMBER** | EXPECTED_BLOCK |
| `pdlt-runtime-gate.yml` | `ACTIVE` | no | no | success | 2026-09-02T14:40:09Z | **GREEN** | None |
| `pdlt-v1-1.yml` | `ACTIVE` | no | no | success | 2026-09-02T14:41:13Z | **GREEN** | None |
| `phase4-no-hindsight-replay.yml` | `ACTIVE` | no | no | success | 2026-08-23T17:53:27Z | **GREEN** | None |
| `provider-budget-readback.yml` | `ACTIVE` | no | yes | success | 2026-09-18T16:22:31Z | **GREEN** | None |
| `pullback-learning-gate.yml` | `ACTIVE` | no | no | failure | 2026-09-13T09:52:24Z | **AMBER** | PR_GATE_REJECTION, REPEATED_PR_GATE_REJECTIONS |
| `pullback-learning-ledger.yml` | `ACTIVE` | yes | yes | success | 2026-09-18T15:31:43Z | **GREEN** | None |
| `remediation-maturation-gate.yml` | `ACTIVE` | no | no | success | 2026-09-16T00:25:47Z | **GREEN** | None |
| `remediation-maturation.yml` | `ACTIVE` | yes | yes | success | 2026-09-18T08:30:40Z | **GREEN** | None |
| `research-execution-coordinator.yml` | `ACTIVE` | yes | yes | success | 2026-09-18T12:11:54Z | **GREEN** | None |
| `research-owner-breadth-daily.yml` | `ACTIVE` | yes | yes | success | 2026-09-18T09:46:37Z | **GREEN** | None |
| `research-owner-btcd-daily.yml` | `ACTIVE` | yes | yes | success | 2026-09-18T10:01:14Z | **GREEN** | None |
| `rich-breadth-checkpoint.yml` | `ACTIVE` | yes | yes | success | 2026-09-18T13:00:30Z | **GREEN** | None |
| `round3-contract-freeze-gate.yml` | `ACTIVE` | no | no | success | 2026-09-13T09:52:24Z | **GREEN** | None |
| `round3-v2-materialization.yml` | `ACTIVE` | no | no | success | 2026-08-23T13:17:33Z | **GREEN** | None |
| `sequential-research-queue.yml` | `ACTIVE` | yes | yes | success | 2026-09-18T11:27:56Z | **GREEN** | None |
| `shadow-admission-ai-decider.yml` | `ACTIVE` | yes | yes | success | 2026-09-14T01:43:36Z | **GREEN** | None |
| `shadow-registry-autonomous-portfolio-gate.yml` | `ACTIVE` | no | no | success | 2026-08-22T19:41:03Z | **GREEN** | None |
| `shadow-registry-autonomous-portfolio-loop.yml` | `ACTIVE` | yes | yes | success | 2026-09-14T13:22:21Z | **GREEN** | None |
| `shadow-registry-gate.yml` | `ACTIVE` | no | no | action_required | 2026-09-14T10:57:31Z | **AMBER** | PR_GATE_REJECTION |
| `shadow-registry-weekly.yml` | `ACTIVE` | yes | no | success | 2026-09-14T10:57:05Z | **GREEN** | None |
| `shared-row-prospective-evidence-loop.yml` | `ACTIVE` | yes | yes | success | 2026-09-18T14:39:08Z | **GREEN** | None |
| `shared-row-tournament-research-gate.yml` | `ACTIVE` | no | no | success | 2026-09-13T09:58:52Z | **GREEN** | None |
| `shared-row-tournament-weekly.yml` | `ACTIVE` | yes | yes | success | 2026-09-14T12:47:16Z | **GREEN** | None |
| `situation-room-daily-static.yml` | `ACTIVE` | yes | yes | failure | 2026-09-18T11:15:30Z | **RED** | LATEST_RUN_FAILED |
| `situation-room-owner-live-gate.yml` | `ACTIVE` | no | no | success | 2026-09-13T22:23:40Z | **GREEN** | None |
| `situation-room-shadow-bridge.yml` | `ACTIVE` | yes | yes | failure | 2026-09-18T11:42:52Z | **RED** | LATEST_RUN_FAILED, REPEATED_CONSECUTIVE_FAILURES |
| `source-provenance-recovery-gate.yml` | `ACTIVE` | no | no | success | 2026-08-23T11:29:50Z | **GREEN** | None |
| `source-provenance-recovery-loop.yml` | `ACTIVE` | yes | yes | success | 2026-09-18T09:29:54Z | **GREEN** | None |
| `specialist-architecture-gate.yml` | `ACTIVE` | no | no | success | 2026-08-23T11:29:50Z | **GREEN** | None |
| `storage-health-gate.yml` | `ACTIVE` | no | no | success | 2026-09-18T18:00:55Z | **GREEN** | None |
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
- askr-launch-sentinel.yml:REPEATED_CONSECUTIVE_FAILURES
- daily-settled-etf-calibration.yml:LATEST_RUN_FAILED
- framework-learning-operations.yml:LATEST_RUN_FAILED
- framework-learning-operations.yml:REPEATED_CONSECUTIVE_FAILURES
- framework-learning-supervisor.yml:LATEST_RUN_FAILED
- framework-learning-supervisor.yml:REPEATED_CONSECUTIVE_FAILURES
- operations-dashboard.yml:LATEST_RUN_FAILED
- operations-dashboard.yml:REPEATED_CONSECUTIVE_FAILURES
- situation-room-daily-static.yml:LATEST_RUN_FAILED
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
- REGISTERED_WITHOUT_LOCAL_FILE:complete-kompas.yml
- REGISTERED_WITHOUT_LOCAL_FILE:e2-artifact-byte-exact-correction.yml
- REGISTERED_WITHOUT_LOCAL_FILE:edgeonchain-e0-identity-probe-once.yml
- REGISTERED_WITHOUT_LOCAL_FILE:edgeonchain-e1-ledger-capture-once.yml
- REGISTERED_WITHOUT_LOCAL_FILE:edgeonchain-e1-retain-on-branch-once.yml
- REGISTERED_WITHOUT_LOCAL_FILE:forecast-skill-admission-gate.yml
- REGISTERED_WITHOUT_LOCAL_FILE:harness-redteam-p0-remediation-gate.yml
- REGISTERED_WITHOUT_LOCAL_FILE:historical-shadow-validation-stage1-manifest.yml
- REGISTERED_WITHOUT_LOCAL_FILE:memes-alpha-research-gate.yml
- REGISTERED_WITHOUT_LOCAL_FILE:native-market-recovery-v1-1.yml
- REGISTERED_WITHOUT_LOCAL_FILE:one-shot-cfgi-w36-rebuild.yml
- REGISTERED_WITHOUT_LOCAL_FILE:persistent-agent-runtime-readiness-gate.yml
- REGISTERED_WITHOUT_LOCAL_FILE:t4-microstructure-live-readback.yml
- REGISTERED_WITHOUT_LOCAL_FILE:zero-manual-feed-graduation.yml
- compass-event-refresh.yml:NO_RUN_HISTORY
- compass-event-refresh.yml:SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE
- compass-outcomes.yml:LATEST_RUN_CANCELLED
- compass-schedule-watchdog.yml:NO_RUN_HISTORY
- compass-schedule-watchdog.yml:SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE
- cycle-navigator-internal-precision.yml:NO_RUN_HISTORY
- daily-compass.yml:SCHEDULE_STALE
- daily-compass.yml:SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE
- daily-slow-cycle-shadow.yml:RECOVERING_AFTER_RECENT_FAILURES
- entry-signal-ledger-gate.yml:PR_GATE_REJECTION
- entry-signal-ledger-gate.yml:REPEATED_PR_GATE_REJECTIONS
- external-alpha-registry-gate.yml:SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE
- framework-intelligence-phase1-live-shadow.yml:NO_RUN_HISTORY
- historical-altseason-cfgi-enrichment.yml:RETIRED_WORKFLOW_LOCAL_FILE_PRESENT
- historical-altseason-cfgi-reservation.yml:RETIRED_WORKFLOW_LOCAL_FILE_PRESENT
- historical-altseason-lab-gate.yml:ARTIFACT_RETENTION_UNBOUNDED
- pdlt-bootstrap-once.yml:EXPECTED_BLOCK
- pdlt-daily-census.yml:EXPECTED_BLOCK
- pdlt-discovery-once.yml:EXPECTED_BLOCK
- pdlt-maturation.yml:EXPECTED_BLOCK
- pullback-learning-gate.yml:PR_GATE_REJECTION
- pullback-learning-gate.yml:REPEATED_PR_GATE_REJECTIONS
- shadow-registry-gate.yml:PR_GATE_REJECTION
- sunday-market-close-and-cfgi.yml:RECOVERING_AFTER_RECENT_FAILURES
