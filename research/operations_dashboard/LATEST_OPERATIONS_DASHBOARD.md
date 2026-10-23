# Operations Dashboard

Overall: **AMBER**
Generated: `2026-10-23T08:45:30.348648Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 3.913 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 8.649 |
| `weekly_output` | **GREEN** | FRESH | 99.501 |
| `automation_health` | **AMBER** | AMBER | 0.045 |
| `architecture_health` | **GREEN** | GREEN | 0.011 |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.659 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.673 |
| `remediation_maturation` | **GREEN** | FRESH | 13.27 |

## AI and learning activity

- OpenAI receipts this month: **297**
- OpenAI estimated cost this month: **$13.594415 from receipts**
- Pending forecast candidates: **257**
- Experiment candidates: **593**
- Experiment dispatch requests: **36530**
- Codex-ready remediation tasks: **6**
- Needs-more-evidence items: **2**

## Incidents

Open incident references: **23**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `SHADOW_COMPASS_V2` | 49 | $3.026708 | 0 | 49 | 0 |
| `DAILY_CONFLICT_REVIEW` | 32 | $2.936662 | 0 | 32 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 18 | $2.476158 | 0 | 18 | 1 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 4 | $1.036608 | 0 | 4 | 0 |
| `MONTHLY_LEARNING_ANALYST` | 4 | $1.026470 | 0 | 4 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 89 | $0.924748 | 0 | 89 | 88 |
| `FMOS_AUTONOMOUS_MISSION_LOOP_AUDIT` | 3 | $0.718824 | 0 | 3 | 0 |
| `TEMP_SOL_PR_REVIEW` | 8 | $0.674266 | 0 | 8 | 4 |
| `DECISION_MISS_AUDIT` | 23 | $0.293158 | 0 | 17 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 23 | $0.153069 | 0 | 0 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 3 | $0.101492 | 0 | 3 | 0 |
| `UNCLASSIFIED` | 3 | $0.073760 | 0 | 3 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `0f226b4f162c2f973499d2d3ee6310a0d94dfe181cdd9acb65ab2b7f8128310d`
