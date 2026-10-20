# Operations Dashboard

Overall: **AMBER**
Generated: `2026-10-20T08:48:15.497977Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 3.937 |
| `openai_daily_director` | **GREEN** | FRESH | 8.231 |
| `weekly_output` | **GREEN** | FRESH | 27.547 |
| `automation_health` | **AMBER** | AMBER | 0.065 |
| `architecture_health` | **GREEN** | GREEN | 0.01 |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.685 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.697 |
| `remediation_maturation` | **GREEN** | FRESH | 12.063 |

## AI and learning activity

- OpenAI receipts this month: **265**
- OpenAI estimated cost this month: **$12.751691 from receipts**
- Pending forecast candidates: **251**
- Experiment candidates: **569**
- Experiment dispatch requests: **33374**
- Codex-ready remediation tasks: **6**
- Needs-more-evidence items: **1**

## Incidents

Open incident references: **22**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `DAILY_CONFLICT_REVIEW` | 32 | $2.936662 | 0 | 32 | 0 |
| `SHADOW_COMPASS_V2` | 43 | $2.639760 | 0 | 43 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 18 | $2.476158 | 0 | 18 | 1 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 4 | $1.036608 | 0 | 4 | 0 |
| `MONTHLY_LEARNING_ANALYST` | 4 | $1.026470 | 0 | 4 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 77 | $0.787951 | 0 | 77 | 76 |
| `FMOS_AUTONOMOUS_MISSION_LOOP_AUDIT` | 3 | $0.718824 | 0 | 3 | 0 |
| `TEMP_SOL_PR_REVIEW` | 6 | $0.427192 | 0 | 6 | 2 |
| `DECISION_MISS_AUDIT` | 20 | $0.252288 | 0 | 14 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 20 | $0.133194 | 0 | 0 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 3 | $0.101492 | 0 | 3 | 0 |
| `UNCLASSIFIED` | 3 | $0.073760 | 0 | 3 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER

Dashboard SHA-256: `9be81ecb1c053072f62e0248d2cef07216efd29c28e5a1ae771b74faa4f75e5d`
