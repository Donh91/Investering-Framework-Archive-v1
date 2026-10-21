# Operations Dashboard

Overall: **RED**
Generated: `2026-10-21T19:55:59.976612Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 2.775 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 1.659 |
| `weekly_output` | **GREEN** | FRESH | 62.676 |
| `automation_health` | **RED** | RED | 0.495 |
| `architecture_health` | **GREEN** | GREEN | 0.45 |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.659 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 4.092 |
| `remediation_maturation` | **GREEN** | FRESH | 0.327 |

## AI and learning activity

- OpenAI receipts this month: **279**
- OpenAI estimated cost this month: **$13.050305 from receipts**
- Pending forecast candidates: **253**
- Experiment candidates: **583**
- Experiment dispatch requests: **35198**
- Codex-ready remediation tasks: **6**
- Needs-more-evidence items: **3**

## Incidents

Open incident references: **24**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `DAILY_CONFLICT_REVIEW` | 32 | $2.936662 | 0 | 32 | 0 |
| `SHADOW_COMPASS_V2` | 46 | $2.835590 | 0 | 46 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 18 | $2.476158 | 0 | 18 | 1 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 4 | $1.036608 | 0 | 4 | 0 |
| `MONTHLY_LEARNING_ANALYST` | 4 | $1.026470 | 0 | 4 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 84 | $0.867005 | 0 | 84 | 83 |
| `FMOS_AUTONOMOUS_MISSION_LOOP_AUDIT` | 3 | $0.718824 | 0 | 3 | 0 |
| `TEMP_SOL_PR_REVIEW` | 6 | $0.427192 | 0 | 6 | 2 |
| `DECISION_MISS_AUDIT` | 21 | $0.265729 | 0 | 15 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 21 | $0.139819 | 0 | 0 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 3 | $0.101492 | 0 | 3 | 0 |
| `UNCLASSIFIED` | 3 | $0.073760 | 0 | 3 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P0** `automation_health` - ['daily-settled-etf-calibration.yml:LATEST_RUN_FAILED']
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `2c653e1e39aa4c11aed9f1883d7929f76458b4e0b0554d67d77942ebae472455`
