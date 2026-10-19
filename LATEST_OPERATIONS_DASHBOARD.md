# Operations Dashboard

Overall: **AMBER**
Generated: `2026-10-19T09:44:37.991086Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 5.046 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 10.167 |
| `weekly_output` | **GREEN** | FRESH | 4.487 |
| `automation_health` | **AMBER** | AMBER | 0.601 |
| `architecture_health` | **GREEN** | GREEN | 0.532 |
| `experiment_lifecycle` | **GREEN** | FRESH | 3.444 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 3.45 |
| `remediation_maturation` | **GREEN** | FRESH | 0.412 |

## AI and learning activity

- OpenAI receipts this month: **254**
- OpenAI estimated cost this month: **$12.322115 from receipts**
- Pending forecast candidates: **249**
- Experiment candidates: **562**
- Experiment dispatch requests: **32350**
- Codex-ready remediation tasks: **6**
- Needs-more-evidence items: **1**

## Incidents

Open incident references: **22**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `DAILY_CONFLICT_REVIEW` | 32 | $2.936662 | 0 | 32 | 0 |
| `SHADOW_COMPASS_V2` | 41 | $2.520172 | 0 | 41 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 16 | $2.232892 | 0 | 16 | 1 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 4 | $1.036608 | 0 | 4 | 0 |
| `MONTHLY_LEARNING_ANALYST` | 4 | $1.026470 | 0 | 4 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 73 | $0.744468 | 0 | 73 | 72 |
| `FMOS_AUTONOMOUS_MISSION_LOOP_AUDIT` | 3 | $0.718824 | 0 | 3 | 0 |
| `TEMP_SOL_PR_REVIEW` | 6 | $0.427192 | 0 | 6 | 2 |
| `DECISION_MISS_AUDIT` | 19 | $0.238964 | 0 | 13 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 19 | $0.126537 | 0 | 0 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 3 | $0.101492 | 0 | 3 | 0 |
| `UNCLASSIFIED` | 3 | $0.073760 | 0 | 3 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `cb856b76d8dce5c33c2f2b5524a71cbf384ba266999cf5dea0bd369de5890dee`
