# Operations Dashboard

Overall: **RED**
Generated: `2026-10-16T02:43:55.976754Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 3.654 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 2.943 |
| `weekly_output` | **GREEN** | FRESH | 92.258 |
| `automation_health` | **RED** | RED | 0.141 |
| `architecture_health` | **GREEN** | GREEN | 0.009 |
| `experiment_lifecycle` | **GREEN** | FRESH | 0.01 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 0.075 |
| `remediation_maturation` | **GREEN** | FRESH | 7.336 |

## AI and learning activity

- OpenAI receipts this month: **223**
- OpenAI estimated cost this month: **$11.672998 from receipts**
- Pending forecast candidates: **244**
- Experiment candidates: **541**
- Experiment dispatch requests: **29310**
- Codex-ready remediation tasks: **5**
- Needs-more-evidence items: **3**

## Incidents

Open incident references: **25**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `DAILY_CONFLICT_REVIEW` | 32 | $2.936662 | 0 | 32 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 16 | $2.232892 | 0 | 16 | 1 |
| `SHADOW_COMPASS_V2` | 35 | $2.158818 | 0 | 35 | 0 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 4 | $1.036608 | 0 | 4 | 0 |
| `MONTHLY_LEARNING_ANALYST` | 4 | $1.026470 | 0 | 4 | 0 |
| `FMOS_AUTONOMOUS_MISSION_LOOP_AUDIT` | 3 | $0.718824 | 0 | 3 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 61 | $0.613759 | 0 | 61 | 60 |
| `TEMP_SOL_PR_REVIEW` | 6 | $0.427192 | 0 | 6 | 2 |
| `DECISION_MISS_AUDIT` | 16 | $0.199267 | 0 | 10 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 16 | $0.106595 | 0 | 0 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 2 | $0.064436 | 0 | 2 | 0 |
| `UNCLASSIFIED` | 2 | $0.049244 | 0 | 2 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P0** `automation_health` - ['framework-learning-operations.yml:LATEST_RUN_FAILED']
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `34a23b980ab8d0641fcbefa85ce3a02e5c5bb73e9b8610232288be3d9cf2a00f`
