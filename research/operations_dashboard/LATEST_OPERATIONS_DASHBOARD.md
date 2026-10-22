# Operations Dashboard

Overall: **RED**
Generated: `2026-10-22T08:51:49.318722Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 4.069 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 8.703 |
| `weekly_output` | **GREEN** | FRESH | 75.606 |
| `automation_health` | **RED** | RED | 0.077 |
| `architecture_health` | **GREEN** | GREEN | 0.012 |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.695 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.706 |
| `remediation_maturation` | **GREEN** | FRESH | 13.257 |

## AI and learning activity

- OpenAI receipts this month: **287**
- OpenAI estimated cost this month: **$13.399152 from receipts**
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

Dashboard SHA-256: `53c6366b8772785cf511327125ba408f73eb417993c9809401b440dce310f366`
