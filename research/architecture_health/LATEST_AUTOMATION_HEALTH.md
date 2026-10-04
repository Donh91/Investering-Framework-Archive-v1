# Automation Production Health
Status: **AMBER**
Generated: `2026-10-04T13:37:05.184243Z`
Workflows: 185 local / 210 registered
Scheduled: 56
Writers: 59
GREEN / AMBER / RED: 180 / 5 / 0

## Workflow matrix
| Workflow | Lifecycle | Schedule | Writer | Last conclusion | Last run | Status | Findings |
|---|---|---:|---:|---|---|---|---|
| `adaptive-decision-miss-validation.yml` | `ACTIVE` | yes | yes | success | 2026-10-04T01:57:27Z | **GREEN** | None |
| `adaptive-evidence-gap-gate.yml` | `ACTIVE` | no | no | success | 2026-10-01T23:46:53Z | **GREEN** | None |
| `adaptive-evidence-gap.yml` | `ACTIVE` | yes | yes | success | 2026-10-04T00:07:22Z | **GREEN** | None |
| `adaptive-gap-validation-gate.yml` | `ACTIVE` | no | no | success | 2026-10-02T06:48:23Z | **GREEN** | None |
| `adaptive-rotation-cadence.yml` | `ACTIVE` | yes | yes | success | 2026-10-04T08:27:50Z | **GREEN** | None |
| `alpha-arc-live-replay.yml` | `ACTIVE` | no | no | success | 2026-09-16T19:33:35Z | **GREEN** | None |
| `alpha-proof-supervisor.yml` | `ACTIVE` | no | no | success | 2026-10-04T09:00:13Z | **GREEN** | None |
| `alpha-shadow04-prospective.yml` | `ACTIVE` | yes | no | in_progress | 2026-10-04T13:15:40Z | **GREEN** | None |
| `api-agent-gateway-gate.yml` | `ACTIVE` | no | no | success | 2026-10-03T20:38:23Z | **GREEN** | None |
| `askr-forensic-replay.yml` | `ACTIVE` | no | no | skipped | 2026-10-04T09:59:23Z | **GREEN** | None |
| `askr-launch-sentinel.yml` | `RETIRED` | no | no | cancelled | 2026-09-18T19:11:54Z | **GREEN** | None |
| `astra-landing-zone-gate.yml` | `ACTIVE` | no | no | success | 2026-09-18T06:11:13Z | **GREEN** | None |
| `auto-trading-e2-candidate-selection-v4.yml` | `ACTIVE` | no | no | success | 2026-09-14T14:33:03Z | **GREEN** | None |
| `auto-trading-e2-candidate-selection.yml` | `ACTIVE` | no | no | success | 2026-09-14T12:58:08Z | **GREEN** | None |
| `auto-trading-e2-compiler-reliability.yml` | `ACTIVE` | no | no | success | 2026-09-14T10:39:09Z | **GREEN** | None |
| `auto-trading-e2-reproducibility.yml` | `ACTIVE` | no | no | success | 2026-09-13T22:46:04Z | **GREEN** | None |
| `automation-health-bootstrap.yml` | `ACTIVE` | no | no | success | 2026-10-04T13:36:14Z | **GREEN** | None |
| `automation-production-health-gate.yml` | `ACTIVE` | no | no | success | 2026-10-04T13:34:49Z | **GREEN** | None |
| `automation-production-health.yml` | `ACTIVE` | yes | yes | in_progress | 2026-10-04T13:36:19Z | **GREEN** | None |
| `autonomous-research-governance-gate.yml` | `ACTIVE` | no | no | success | 2026-10-02T06:48:23Z | **GREEN** | None |
| `autonomous-research-governance-loop.yml` | `ACTIVE` | yes | yes | success | 2026-10-04T11:10:58Z | **GREEN** | None |
| `backtest-engine-foundation.yml` | `ACTIVE` | no | no | success | 2026-09-23T20:30:50Z | **GREEN** | None |
| `backtest-readiness-contracts.yml` | `ACTIVE` | no | no | success | 2026-09-05T20:39:59Z | **GREEN** | None |
| `backtest-wave1-2-foundation.yml` | `ACTIVE` | no | no | success | 2026-09-23T20:30:50Z | **GREEN** | None |
| `backtest-wave1-3-authority-lineage.yml` | `ACTIVE` | no | no | success | 2026-07-28T16:15:15Z | **GREEN** | None |
| `backtest-wave1-4-prospective.yml` | `ACTIVE` | yes | no | success | 2026-10-03T18:48:10Z | **GREEN** | None |
| `binance-spot-owner-manual.yml` | `ACTIVE` | no | no | success | 2026-08-01T19:31:36Z | **GREEN** | None |
| `binance-usdm-owner-manual.yml` | `ACTIVE` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `buildwithclaude-shadow-evidence-ledger.yml` | `ACTIVE` | no | no | success | 2026-09-02T16:22:23Z | **GREEN** | None |
| `buildwithclaude-shadow-prospective-observer.yml` | `ACTIVE` | no | no | success | 2026-09-04T23:29:35Z | **GREEN** | None |
| `buildwithclaude-shadow-round1.yml` | `ACTIVE` | no | no | success | 2026-09-02T16:22:23Z | **GREEN** | None |
| `cfgi-recovery-launch-once.yml` | `ACTIVE` | no | no | success | 2026-08-23T07:25:36Z | **GREEN** | None |
| `cfgi-recovery-launch-trigger.yml` | `RETIRED` | no | no | skipped | 2026-10-02T06:26:39Z | **GREEN** | None |
| `cfgi-v3-launch-receipt-publish.yml` | `ACTIVE` | no | yes | success | 2026-08-23T07:24:14Z | **GREEN** | None |
| `cn-precision-learning-bootstrap.yml` | `ACTIVE` | no | no | success | 2026-10-02T06:50:18Z | **GREEN** | None |
| `cn-site-v2-gate.yml` | `ACTIVE` | no | no | success | 2026-10-04T13:34:49Z | **GREEN** | None |
| `codex-intake-dispatch.yml` | `ACTIVE` | no | no | success | 2026-10-02T07:52:13Z | **GREEN** | None |
| `compass-event-refresh.yml` | `ACTIVE` | yes | yes | success | 2026-10-04T12:53:03Z | **GREEN** | None |
| `compass-outcomes.yml` | `ACTIVE` | yes | yes | pending | 2026-10-04T13:36:20Z | **GREEN** | None |
| `compass-production-bootstrap.yml` | `ACTIVE` | no | no | success | 2026-10-04T13:36:14Z | **GREEN** | None |
| `compass-schedule-watchdog.yml` | `ACTIVE` | yes | no | success | 2026-10-04T13:24:36Z | **GREEN** | None |
| `continuity-learning-gate.yml` | `ACTIVE` | no | no | success | 2026-10-04T13:34:49Z | **GREEN** | None |
| `continuity-learning-maintenance.yml` | `ACTIVE` | yes | yes | success | 2026-10-04T00:02:39Z | **GREEN** | None |
| `cowork-historical-altseason-bundle-gate.yml` | `ACTIVE` | no | no | success | 2026-08-21T09:47:00Z | **GREEN** | None |
| `cowork-historical-altseason-bundle-receipt.yml` | `ACTIVE` | no | yes | success | 2026-08-21T09:47:59Z | **GREEN** | None |
| `cowork-historical-altseason-bundle.yml` | `ACTIVE` | no | no | success | 2026-08-21T09:47:47Z | **GREEN** | None |
| `cross-repo-agent-context-gate.yml` | `ACTIVE` | no | no | success | 2026-10-02T06:28:09Z | **GREEN** | None |
| `cycle-navigator-autonomous-calibration-gate.yml` | `ACTIVE` | no | no | success | 2026-10-02T06:48:23Z | **GREEN** | None |
| `cycle-navigator-autonomous-calibration-loop.yml` | `ACTIVE` | yes | yes | success | 2026-09-28T14:10:43Z | **GREEN** | None |
| `cycle-navigator-internal-precision.yml` | `ACTIVE` | yes | yes | success | 2026-09-28T16:46:06Z | **GREEN** | None |
| `cycle-navigator-pages.yml` | `ACTIVE` | no | no | success | 2026-10-04T13:36:43Z | **GREEN** | None |
| `cycle-navigator-precision-hardening-once.yml` | `ACTIVE` | no | no | failure | 2026-09-14T14:33:59Z | **GREEN** | None |
| `cycle-navigator-precision-hardening-v2-once.yml` | `ACTIVE` | no | no | failure | 2026-09-14T14:36:54Z | **GREEN** | None |
| `cycle-navigator-precision-hardening-v3-once.yml` | `ACTIVE` | no | no | success | 2026-09-14T14:38:47Z | **GREEN** | None |
| `cycle-navigator-precision-learning-supervisor.yml` | `ACTIVE` | yes | yes | success | 2026-10-02T06:50:24Z | **AMBER** | PENDING_FIRST_EXPECTED_RUN |
| `cycle-navigator-public-contract-gate.yml` | `ACTIVE` | no | no | success | 2026-10-04T13:36:14Z | **GREEN** | None |
| `cycle-navigator-weekly-publication.yml` | `ACTIVE` | yes | yes | success | 2026-09-28T15:17:53Z | **GREEN** | None |
| `daily-capture-architecture-gate.yml` | `ACTIVE` | no | no | success | 2026-10-04T13:32:53Z | **GREEN** | None |
| `daily-compass.yml` | `ACTIVE` | yes | yes | success | 2026-10-04T13:36:19Z | **GREEN** | None |
| `daily-director-shadow.yml` | `ACTIVE` | yes | yes | success | 2026-10-04T10:42:54Z | **GREEN** | None |
| `daily-machine-throughput-gate.yml` | `ACTIVE` | no | no | success | 2026-10-02T06:48:23Z | **GREEN** | None |
| `daily-machine-throughput.yml` | `ACTIVE` | yes | yes | success | 2026-10-04T02:01:36Z | **GREEN** | None |
| `daily-raw-owner-capture.yml` | `ACTIVE` | yes | yes | success | 2026-10-04T10:31:54Z | **GREEN** | None |
| `daily-settled-etf-calibration.yml` | `ACTIVE` | yes | yes | success | 2026-10-04T12:14:50Z | **GREEN** | None |
| `daily-slow-cycle-shadow.yml` | `ACTIVE` | yes | yes | success | 2026-10-04T10:43:56Z | **GREEN** | None |
| `daily-stablecoin-liquidity.yml` | `ACTIVE` | yes | yes | success | 2026-10-04T11:09:59Z | **GREEN** | None |
| `data-architecture-gate.yml` | `ACTIVE` | no | no | success | 2026-10-04T13:34:49Z | **GREEN** | None |
| `data-terminal-shadow-manual.yml` | `ACTIVE` | no | no | success | 2026-09-30T21:59:59Z | **GREEN** | None |
| `dataset-registry-gate.yml` | `ACTIVE` | no | no | success | 2026-09-04T23:12:36Z | **GREEN** | None |
| `entry-signal-ledger-gate.yml` | `ACTIVE` | no | no | success | 2026-10-04T13:34:39Z | **GREEN** | None |
| `entry-signal-ledger.yml` | `ACTIVE` | yes | yes | success | 2026-10-04T12:54:39Z | **GREEN** | None |
| `ethbtc-persistence-lifecycle.yml` | `ACTIVE` | no | yes | success | 2026-10-04T10:44:23Z | **GREEN** | None |
| `evidence-closure-gate.yml` | `ACTIVE` | no | no | success | 2026-10-04T13:34:49Z | **GREEN** | None |
| `evidence-lifecycle-observability-gate.yml` | `ACTIVE` | no | no | success | 2026-10-02T06:48:23Z | **GREEN** | None |
| `evidence-lifecycle-store-health.yml` | `ACTIVE` | yes | no | success | 2026-10-04T09:50:18Z | **GREEN** | None |
| `experiment-lifecycle-gate.yml` | `ACTIVE` | no | no | success | 2026-10-02T07:43:21Z | **GREEN** | None |
| `experiment-receipt-sync-bootstrap.yml` | `ACTIVE` | no | no | success | 2026-10-02T06:50:19Z | **GREEN** | None |
| `external-alpha-registry-gate.yml` | `ACTIVE` | yes | no | success | 2026-09-28T13:50:38Z | **GREEN** | None |
| `fetch_btc_d_cmc_free.yml` | `ACTIVE` | no | no | success | 2026-07-12T00:09:38Z | **GREEN** | None |
| `forecast-exact-settlement-owner-gate.yml` | `ACTIVE` | no | no | success | 2026-10-02T06:48:23Z | **GREEN** | None |
| `forecast-materialization-census-gate.yml` | `ACTIVE` | no | no | success | 2026-10-02T06:48:23Z | **GREEN** | None |
| `forecast-outcome-supersession-gate.yml` | `ACTIVE` | no | no | success | 2026-10-02T06:48:23Z | **GREEN** | None |
| `forecast-ratification-throughput-gate.yml` | `ACTIVE` | no | no | success | 2026-10-02T06:48:23Z | **GREEN** | None |
| `forecast-settlement-accountability-gate.yml` | `ACTIVE` | no | no | success | 2026-09-18T08:13:51Z | **GREEN** | None |
| `forecast-skill-study-v132-gate.yml` | `ACTIVE` | no | no | success | 2026-10-02T06:48:23Z | **GREEN** | None |
| `forecast-source-temporal-provenance-gate.yml` | `ACTIVE` | no | no | success | 2026-10-02T06:48:23Z | **GREEN** | None |
| `framework-intelligence-phase1-live-shadow.yml` | `ACTIVE` | yes | yes | success | 2026-09-28T15:36:53Z | **GREEN** | None |
| `framework-learning-operations.yml` | `ACTIVE` | yes | yes | success | 2026-10-04T07:00:02Z | **GREEN** | None |
| `framework-learning-supervisor.yml` | `ACTIVE` | yes | yes | success | 2026-10-04T08:43:07Z | **GREEN** | None |
| `full-architecture-1to7-gate.yml` | `ACTIVE` | no | no | success | 2026-10-04T13:34:49Z | **GREEN** | None |
| `historical-altseason-cfgi-enrichment.yml` | `RETIRED` | no | no | failure | 2026-08-23T05:18:07Z | **GREEN** | None |
| `historical-altseason-cfgi-publish.yml` | `ACTIVE` | no | yes | success | 2026-08-21T08:08:20Z | **GREEN** | None |
| `historical-altseason-cfgi-reservation.yml` | `RETIRED` | no | no | success | 2026-10-02T07:07:51Z | **GREEN** | None |
| `historical-altseason-cfgi-run-audit.yml` | `ACTIVE` | no | yes | success | 2026-10-02T06:50:41Z | **GREEN** | None |
| `historical-altseason-cfgi-terminal-finalize.yml` | `ACTIVE` | no | no | success | 2026-08-21T13:55:43Z | **GREEN** | None |
| `historical-altseason-cfgi-terminal-publish.yml` | `ACTIVE` | no | yes | success | 2026-08-21T13:55:57Z | **GREEN** | None |
| `historical-altseason-free-bootstrap.yml` | `ACTIVE` | no | no | success | 2026-10-02T06:50:41Z | **GREEN** | None |
| `historical-altseason-free-publish-regression-gate.yml` | `ACTIVE` | no | no | success | 2026-10-02T06:48:23Z | **GREEN** | None |
| `historical-altseason-free-publish.yml` | `ACTIVE` | no | yes | success | 2026-10-02T07:07:24Z | **GREEN** | None |
| `historical-altseason-lab-gate.yml` | `ACTIVE` | no | no | success | 2026-10-02T06:50:18Z | **GREEN** | None |
| `historical-altseason-throughput-gate.yml` | `ACTIVE` | no | no | success | 2026-10-02T06:48:23Z | **GREEN** | None |
| `historical-research-vault-gate.yml` | `ACTIVE` | no | no | success | 2026-09-04T23:12:36Z | **GREEN** | None |
| `hourly-sequence-capture.yml` | `ACTIVE` | yes | yes | pending | 2026-10-04T13:08:09Z | **GREEN** | None |
| `intraday-execution-gate.yml` | `ACTIVE` | no | no | failure | 2026-10-04T13:32:53Z | **GREEN** | None |
| `intraday-execution-research.yml` | `ACTIVE` | no | yes | success | 2026-08-31T00:03:54Z | **GREEN** | None |
| `legacy-knowledge-bootstrap-gate.yml` | `ACTIVE` | no | no | success | 2026-08-04T19:08:35Z | **GREEN** | None |
| `mar_wp04c4_gate.yml` | `ACTIVE` | no | no | success | 2026-07-31T01:41:02Z | **GREEN** | None |
| `master-monday-precision-repair-once.yml` | `ACTIVE` | no | no | success | 2026-09-14T14:30:57Z | **GREEN** | None |
| `master-monday-preflight-gate.yml` | `ACTIVE` | no | no | success | 2026-10-02T07:43:21Z | **GREEN** | None |
| `master-monday-remaining-gaps.yml` | `ACTIVE` | yes | yes | success | 2026-09-28T11:19:53Z | **GREEN** | None |
| `master-monday-w37-redispatch-once.yml` | `ACTIVE` | no | no | success | 2026-09-14T14:40:27Z | **GREEN** | None |
| `meme-alpha-clean-g3-core.yml` | `ACTIVE` | no | no | success | 2026-10-02T07:21:40Z | **GREEN** | None |
| `meme-alpha-ian-g2g3-research.yml` | `ACTIVE` | no | no | success | 2026-09-15T19:12:27Z | **GREEN** | None |
| `meme-alpha-moonshot-cohort-gate.yml` | `ACTIVE` | no | no | success | 2026-09-16T13:06:33Z | **GREEN** | None |
| `meme-alpha-moonshot-gate.yml` | `ACTIVE` | no | no | success | 2026-10-03T07:51:57Z | **GREEN** | None |
| `meme-alpha-red-causal-pair-replay.yml` | `ACTIVE` | no | no | success | 2026-09-15T20:43:39Z | **GREEN** | None |
| `meme-alpha-red-cohort-schema.yml` | `ACTIVE` | no | no | success | 2026-09-15T20:17:19Z | **GREEN** | None |
| `meme-alpha-red-detector-semantics.yml` | `ACTIVE` | no | no | success | 2026-09-15T20:39:00Z | **GREEN** | None |
| `meme-alpha-red-earliest-first-buy.yml` | `ACTIVE` | no | no | success | 2026-09-15T23:25:24Z | **GREEN** | None |
| `meme-alpha-red-first10-first-buy.yml` | `ACTIVE` | no | no | success | 2026-09-16T10:04:02Z | **GREEN** | None |
| `meme-alpha-red-scale-census.yml` | `ACTIVE` | no | no | success | 2026-09-16T01:35:46Z | **GREEN** | None |
| `meme-alpha-red-sellability-outcomes.yml` | `ACTIVE` | no | no | success | 2026-09-16T01:28:17Z | **GREEN** | None |
| `meme-alpha-red-trade-event-decode.yml` | `ACTIVE` | no | no | success | 2026-09-15T20:51:14Z | **GREEN** | None |
| `meme-alpha-red-tx-reconstruction.yml` | `ACTIVE` | no | no | success | 2026-09-15T20:31:11Z | **GREEN** | None |
| `meme-alpha-runtime-gate.yml` | `ACTIVE` | no | no | success | 2026-10-03T07:51:57Z | **GREEN** | None |
| `meme-alpha-trenches-point-in-time.yml` | `ACTIVE` | no | no | success | 2026-09-15T20:06:36Z | **GREEN** | None |
| `monthly-ai-learning-council-bootstrap-once.yml` | `ACTIVE` | no | no | success | 2026-09-03T06:03:59Z | **GREEN** | None |
| `monthly-ai-learning-council-gate.yml` | `ACTIVE` | no | no | success | 2026-10-03T16:38:53Z | **GREEN** | None |
| `monthly-ai-learning-council.yml` | `ACTIVE` | yes | yes | success | 2026-10-04T10:35:24Z | **GREEN** | None |
| `native-handlekompas.yml` | `ACTIVE` | yes | yes | success | 2026-10-04T12:53:01Z | **GREEN** | None |
| `native-market-recovery.yml` | `ACTIVE` | yes | yes | success | 2026-10-04T10:02:25Z | **GREEN** | None |
| `native-ota-research-readback.yml` | `ACTIVE` | yes | yes | success | 2026-10-04T06:23:00Z | **GREEN** | None |
| `okx-swap-owner-manual.yml` | `ACTIVE` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `operations-dashboard-gate.yml` | `ACTIVE` | no | no | success | 2026-10-02T06:48:23Z | **GREEN** | None |
| `operations-dashboard.yml` | `ACTIVE` | yes | yes | success | 2026-10-04T10:28:44Z | **GREEN** | None |
| `operations-recovery-launch-once.yml` | `ACTIVE` | no | no | success | 2026-08-31T16:26:39Z | **GREEN** | None |
| `owner-bound-daily-director-manual.yml` | `ACTIVE` | no | no | success | 2026-10-03T20:38:23Z | **GREEN** | None |
| `pdf-inspector-ingestion.yml` | `ACTIVE` | no | no | success | 2026-08-02T18:16:02Z | **GREEN** | None |
| `pdlt-bootstrap-once.yml` | `EXPECTED_BLOCK` | no | no | skipped | 2026-08-10T15:36:07Z | **AMBER** | EXPECTED_BLOCK |
| `pdlt-daily-census.yml` | `EXPECTED_BLOCK` | no | no | success | 2026-09-01T23:35:24Z | **AMBER** | EXPECTED_BLOCK |
| `pdlt-discovery-once.yml` | `EXPECTED_BLOCK` | no | no | failure | 2026-08-09T19:58:23Z | **AMBER** | EXPECTED_BLOCK |
| `pdlt-maturation.yml` | `EXPECTED_BLOCK` | no | no | success | 2026-09-02T00:19:38Z | **AMBER** | EXPECTED_BLOCK |
| `pdlt-runtime-gate.yml` | `ACTIVE` | no | no | success | 2026-10-02T06:48:23Z | **GREEN** | None |
| `pdlt-v1-1.yml` | `ACTIVE` | no | no | success | 2026-10-02T06:48:23Z | **GREEN** | None |
| `phase4-no-hindsight-replay.yml` | `ACTIVE` | no | no | success | 2026-08-23T17:53:27Z | **GREEN** | None |
| `provider-budget-readback.yml` | `ACTIVE` | no | yes | success | 2026-10-04T13:34:49Z | **GREEN** | None |
| `pullback-learning-gate.yml` | `ACTIVE` | no | no | success | 2026-10-02T06:48:23Z | **GREEN** | None |
| `pullback-learning-ledger.yml` | `ACTIVE` | yes | yes | success | 2026-10-04T12:52:57Z | **GREEN** | None |
| `remediation-maturation-gate.yml` | `ACTIVE` | no | no | success | 2026-10-02T08:00:24Z | **GREEN** | None |
| `remediation-maturation.yml` | `ACTIVE` | yes | yes | success | 2026-10-04T10:13:21Z | **GREEN** | None |
| `research-execution-coordinator.yml` | `ACTIVE` | yes | yes | success | 2026-10-04T13:08:54Z | **GREEN** | None |
| `research-owner-breadth-daily.yml` | `ACTIVE` | yes | yes | success | 2026-10-04T11:06:59Z | **GREEN** | None |
| `research-owner-btcd-daily.yml` | `ACTIVE` | yes | yes | success | 2026-10-04T11:15:54Z | **GREEN** | None |
| `rich-breadth-checkpoint.yml` | `ACTIVE` | yes | yes | success | 2026-10-04T06:02:24Z | **GREEN** | None |
| `round3-contract-freeze-gate.yml` | `ACTIVE` | no | no | success | 2026-09-13T09:52:24Z | **GREEN** | None |
| `round3-v2-materialization.yml` | `ACTIVE` | no | no | success | 2026-08-23T13:17:33Z | **GREEN** | None |
| `sequential-research-queue.yml` | `ACTIVE` | yes | yes | success | 2026-10-04T12:32:53Z | **GREEN** | None |
| `shadow-admission-ai-decider.yml` | `ACTIVE` | yes | yes | success | 2026-09-28T02:00:01Z | **GREEN** | None |
| `shadow-compass-v2-bootstrap.yml` | `ACTIVE` | no | no | success | 2026-10-04T13:36:14Z | **GREEN** | None |
| `shadow-compass-v2.yml` | `ACTIVE` | yes | yes | pending | 2026-10-04T13:36:19Z | **GREEN** | None |
| `shadow-registry-autonomous-portfolio-gate.yml` | `ACTIVE` | no | no | success | 2026-10-02T06:48:23Z | **GREEN** | None |
| `shadow-registry-autonomous-portfolio-loop.yml` | `ACTIVE` | yes | yes | success | 2026-09-28T14:31:05Z | **GREEN** | None |
| `shadow-registry-gate.yml` | `ACTIVE` | no | no | success | 2026-10-02T06:48:23Z | **GREEN** | None |
| `shadow-registry-weekly.yml` | `ACTIVE` | yes | no | success | 2026-09-28T11:58:05Z | **GREEN** | None |
| `shared-row-prospective-evidence-loop.yml` | `ACTIVE` | yes | yes | success | 2026-10-04T10:46:09Z | **GREEN** | None |
| `shared-row-tournament-research-gate.yml` | `ACTIVE` | no | no | success | 2026-10-02T06:48:23Z | **GREEN** | None |
| `shared-row-tournament-weekly.yml` | `ACTIVE` | yes | yes | success | 2026-09-28T13:54:59Z | **GREEN** | None |
| `situation-room-daily-static.yml` | `ACTIVE` | yes | yes | success | 2026-10-04T12:22:23Z | **GREEN** | None |
| `situation-room-owner-live-gate.yml` | `ACTIVE` | no | no | success | 2026-10-02T06:48:23Z | **GREEN** | None |
| `situation-room-shadow-bridge.yml` | `ACTIVE` | yes | yes | success | 2026-10-04T12:48:46Z | **GREEN** | None |
| `situation-room-static-bootstrap.yml` | `ACTIVE` | no | no | success | 2026-10-02T06:50:18Z | **GREEN** | None |
| `source-provenance-recovery-gate.yml` | `ACTIVE` | no | no | success | 2026-10-02T06:48:23Z | **GREEN** | None |
| `source-provenance-recovery-loop.yml` | `ACTIVE` | yes | yes | success | 2026-10-04T11:01:00Z | **GREEN** | None |
| `specialist-architecture-gate.yml` | `ACTIVE` | no | no | success | 2026-08-23T11:29:50Z | **GREEN** | None |
| `storage-health-gate.yml` | `ACTIVE` | no | no | success | 2026-10-04T13:34:49Z | **GREEN** | None |
| `sunday-market-close-and-cfgi.yml` | `ACTIVE` | yes | yes | success | 2026-09-28T05:05:37Z | **GREEN** | None |
| `top100-breadth-owner-manual.yml` | `ACTIVE` | no | no | success | 2026-09-02T21:44:48Z | **GREEN** | None |
| `typesafe_jev_alpha_blind_replay.yml` | `ACTIVE` | no | no | success | 2026-09-19T12:49:17Z | **GREEN** | None |
| `typesafe_jev_sanitized_smoke.yml` | `ACTIVE` | no | no | success | 2026-09-19T10:13:02Z | **GREEN** | None |
| `typesafe_jev_stress_token_benchmark.yml` | `ACTIVE` | no | no | success | 2026-09-24T21:59:23Z | **GREEN** | None |
| `unified-experimental-lifecycle-adjudication.yml` | `ACTIVE` | yes | yes | success | 2026-09-28T15:07:06Z | **GREEN** | None |
| `validate_m3_forward_ledger.yml` | `ACTIVE` | no | no | none | none | **GREEN** | None |
| `weekly-api-calibration-shadow.yml` | `ACTIVE` | yes | yes | success | 2026-09-28T05:47:05Z | **GREEN** | None |
| `weekly-raw-calibration-bridge.yml` | `ACTIVE` | yes | yes | success | 2026-09-28T05:38:00Z | **GREEN** | None |
| `weekly-sol-adversarial-review.yml` | `ACTIVE` | yes | yes | success | 2026-09-28T09:41:46Z | **GREEN** | None |

## Blockers
- None

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
- REGISTERED_WITHOUT_LOCAL_FILE:fmos-mission-loop-sol-audit.yml
- REGISTERED_WITHOUT_LOCAL_FILE:forecast-skill-admission-gate.yml
- REGISTERED_WITHOUT_LOCAL_FILE:harness-redteam-p0-remediation-gate.yml
- REGISTERED_WITHOUT_LOCAL_FILE:historical-shadow-validation-stage1-manifest.yml
- REGISTERED_WITHOUT_LOCAL_FILE:memes-alpha-research-gate.yml
- REGISTERED_WITHOUT_LOCAL_FILE:native-market-recovery-v1-1.yml
- REGISTERED_WITHOUT_LOCAL_FILE:one-shot-cfgi-w36-rebuild.yml
- REGISTERED_WITHOUT_LOCAL_FILE:persistent-agent-runtime-readiness-gate.yml
- REGISTERED_WITHOUT_LOCAL_FILE:t4-microstructure-live-readback.yml
- REGISTERED_WITHOUT_LOCAL_FILE:zero-manual-feed-graduation.yml
- cycle-navigator-precision-learning-supervisor.yml:PENDING_FIRST_EXPECTED_RUN
- pdlt-bootstrap-once.yml:EXPECTED_BLOCK
- pdlt-daily-census.yml:EXPECTED_BLOCK
- pdlt-discovery-once.yml:EXPECTED_BLOCK
- pdlt-maturation.yml:EXPECTED_BLOCK
