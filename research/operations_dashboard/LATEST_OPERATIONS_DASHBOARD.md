# Operations Dashboard

Overall: **AMBER**
Generated: `2026-10-18T18:18:15.949340Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 2.474 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 1.396 |
| `weekly_output` | **GREEN** | FRESH | 155.83 |
| `automation_health` | **AMBER** | AMBER | 0.077 |
| `architecture_health` | **GREEN** | GREEN | 0.03 |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.396 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 12.286 |
| `remediation_maturation` | **GREEN** | FRESH | 0.014 |

## AI and learning activity

- OpenAI receipts this month: **246**
- OpenAI estimated cost this month: **$12.141223 from receipts**
- Pending forecast candidates: **248**
- Experiment candidates: **561**
- Experiment dispatch requests: **32097**
- Codex-ready remediation tasks: **6**
- Needs-more-evidence items: **2**

## Incidents

Open incident references: **22**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `DAILY_CONFLICT_REVIEW` | 32 | $2.936662 | 0 | 32 | 0 |
| `SHADOW_COMPASS_V2` | 40 | $2.460296 | 0 | 40 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 16 | $2.232892 | 0 | 16 | 1 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 4 | $1.036608 | 0 | 4 | 0 |
| `MONTHLY_LEARNING_ANALYST` | 4 | $1.026470 | 0 | 4 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 72 | $0.733722 | 0 | 72 | 71 |
| `FMOS_AUTONOMOUS_MISSION_LOOP_AUDIT` | 3 | $0.718824 | 0 | 3 | 0 |
| `TEMP_SOL_PR_REVIEW` | 6 | $0.427192 | 0 | 6 | 2 |
| `DECISION_MISS_AUDIT` | 18 | $0.225721 | 0 | 12 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 18 | $0.119900 | 0 | 0 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 2 | $0.064436 | 0 | 2 | 0 |
| `EVIDENCE_GAP_AUDIT` | 16 | $0.053894 | 0 | 0 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `265c183bb706af084ae0e2bf111848e6e67f2cb28ac7f4e8b66f0ea12d66d6e8`
