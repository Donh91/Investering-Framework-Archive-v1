# Operations Dashboard

Overall: **AMBER**
Generated: `2026-10-18T08:43:53.323442Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 4.14 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 9.389 |
| `weekly_output` | **GREEN** | FRESH | 146.257 |
| `automation_health` | **AMBER** | AMBER | 0.54 |
| `architecture_health` | **GREEN** | GREEN | 0.498 |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.674 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.713 |
| `remediation_maturation` | **GREEN** | FRESH | 0.374 |

## AI and learning activity

- OpenAI receipts this month: **242**
- OpenAI estimated cost this month: **$12.043122 from receipts**
- Pending forecast candidates: **248**
- Experiment candidates: **557**
- Experiment dispatch requests: **31335**
- Codex-ready remediation tasks: **6**
- Needs-more-evidence items: **2**

## Incidents

Open incident references: **22**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `DAILY_CONFLICT_REVIEW` | 32 | $2.936662 | 0 | 32 | 0 |
| `SHADOW_COMPASS_V2` | 39 | $2.394740 | 0 | 39 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 16 | $2.232892 | 0 | 16 | 1 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 4 | $1.036608 | 0 | 4 | 0 |
| `MONTHLY_LEARNING_ANALYST` | 4 | $1.026470 | 0 | 4 | 0 |
| `FMOS_AUTONOMOUS_MISSION_LOOP_AUDIT` | 3 | $0.718824 | 0 | 3 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 69 | $0.701178 | 0 | 69 | 68 |
| `TEMP_SOL_PR_REVIEW` | 6 | $0.427192 | 0 | 6 | 2 |
| `DECISION_MISS_AUDIT` | 18 | $0.225721 | 0 | 12 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 18 | $0.119900 | 0 | 0 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 2 | $0.064436 | 0 | 2 | 0 |
| `EVIDENCE_GAP_AUDIT` | 16 | $0.053894 | 0 | 0 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `df6274932e793f0ffe920a188a9aea87b9fba87d014cd37c0089fb5a8e14b818`
