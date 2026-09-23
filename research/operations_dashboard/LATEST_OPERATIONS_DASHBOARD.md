# Operations Dashboard

Overall: **RED**
Generated: `2026-09-23T19:27:45.240274Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 2.543 |
| `openai_daily_director` | **GREEN** | FRESH | 1.491 |
| `weekly_output` | **GREEN** | FRESH | 49.525 |
| `automation_health` | **RED** | RED | 0.32 |
| `architecture_health` | **AMBER** | AMBER | 0.278 |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.491 |
| `experiment_receipt_sync` | **RED** | STALE | 205.076 |
| `remediation_maturation` | **GREEN** | FRESH | 0.239 |

## AI and learning activity

- OpenAI receipts this month: **177**
- OpenAI cost this month: **$12.324557**
- Pending forecast candidates: **201**
- Experiment candidates: **387**
- Experiment dispatch requests: **11192**
- Codex-ready remediation tasks: **24**
- Needs-more-evidence items: **17**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['adaptive-decision-miss-validation.yml:LATEST_RUN_FAILED', 'adaptive-decision-miss-validation.yml:REPEATED_CONSECUTIVE_FAILURES', 'daily-settled-etf-calibration.yml:LATEST_RUN_FAILED', 'daily-settled-etf-calibration.yml:REPEATED_CONSECUTIVE_FAILURES', 'framework-learning-operations.yml:LATEST_RUN_FAILED', 'framework-learning-operations.yml:REPEATED_CONSECUTIVE_FAILURES', 'unified-experimental-lifecycle-adjudication.yml:LATEST_RUN_FAILED']
- **P0** `experiment_receipt_sync` - STALE
- **P1** `architecture_health` - ['OWNER_COVERAGE_DEGRADED', 'ETF_OWNER_STALE', 'EXPERIMENT_RECEIPT_SYNC_STALE']

Dashboard SHA-256: `803f5236ad4a8f27331d0b4a227df6430b0b3ede3b128f2a4c1257ae93233919`
