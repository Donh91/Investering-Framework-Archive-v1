# Operations Dashboard

Overall: **RED**
Generated: `2026-10-22T09:17:35.235901Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 4.498 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 9.132 |
| `weekly_output` | **GREEN** | FRESH | 76.036 |
| `automation_health` | **RED** | RED | 0.506 |
| `architecture_health` | **GREEN** | GREEN | 0.441 |
| `experiment_lifecycle` | **GREEN** | FRESH | 3.125 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 3.135 |
| `remediation_maturation` | **GREEN** | FRESH | 0.346 |

## AI and learning activity

- OpenAI receipts this month: **288**
- OpenAI estimated cost this month: **$13.399487 from receipts**
- Pending forecast candidates: **255**
- Experiment candidates: **585**
- Experiment dispatch requests: **35466**
- Codex-ready remediation tasks: **6**
- Needs-more-evidence items: **3**

## Incidents

Open incident references: **25**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `DAILY_CONFLICT_REVIEW` | 32 | $2.936662 | 0 | 32 | 0 |
| `SHADOW_COMPASS_V2` | 47 | $2.901902 | 0 | 47 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 18 | $2.476158 | 0 | 18 | 1 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 4 | $1.036608 | 0 | 4 | 0 |
| `MONTHLY_LEARNING_ANALYST` | 4 | $1.026470 | 0 | 4 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 85 | $0.878425 | 0 | 85 | 84 |
| `FMOS_AUTONOMOUS_MISSION_LOOP_AUDIT` | 3 | $0.718824 | 0 | 3 | 0 |
| `TEMP_SOL_PR_REVIEW` | 8 | $0.674266 | 0 | 8 | 4 |
| `DECISION_MISS_AUDIT` | 22 | $0.279514 | 0 | 16 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 22 | $0.146454 | 0 | 0 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 3 | $0.101492 | 0 | 3 | 0 |
| `UNCLASSIFIED` | 3 | $0.073760 | 0 | 3 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P0** `automation_health` - ['daily-settled-etf-calibration.yml:LATEST_RUN_FAILED']
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `11ed1f7877d1d397e35747d41421d2e423cf7c8e6ffff2652ae68c2d32eaa19b`
