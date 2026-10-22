# Operations Dashboard

Overall: **AMBER**
Generated: `2026-10-22T19:45:55.798683Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 2.629 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 1.588 |
| `weekly_output` | **GREEN** | FRESH | 86.508 |
| `automation_health` | **AMBER** | AMBER | 0.439 |
| `architecture_health` | **GREEN** | GREEN | 0.387 |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.588 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 13.608 |
| `remediation_maturation` | **GREEN** | FRESH | 0.277 |

## AI and learning activity

- OpenAI receipts this month: **292**
- OpenAI estimated cost this month: **$13.491673 from receipts**
- Pending forecast candidates: **255**
- Experiment candidates: **591**
- Experiment dispatch requests: **36262**
- Codex-ready remediation tasks: **6**
- Needs-more-evidence items: **2**

## Incidents

Open incident references: **23**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `SHADOW_COMPASS_V2` | 48 | $2.959316 | 0 | 48 | 0 |
| `DAILY_CONFLICT_REVIEW` | 32 | $2.936662 | 0 | 32 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 18 | $2.476158 | 0 | 18 | 1 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 4 | $1.036608 | 0 | 4 | 0 |
| `MONTHLY_LEARNING_ANALYST` | 4 | $1.026470 | 0 | 4 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 88 | $0.913197 | 0 | 88 | 87 |
| `FMOS_AUTONOMOUS_MISSION_LOOP_AUDIT` | 3 | $0.718824 | 0 | 3 | 0 |
| `TEMP_SOL_PR_REVIEW` | 8 | $0.674266 | 0 | 8 | 4 |
| `DECISION_MISS_AUDIT` | 22 | $0.279514 | 0 | 16 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 22 | $0.146454 | 0 | 0 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 3 | $0.101492 | 0 | 3 | 0 |
| `UNCLASSIFIED` | 3 | $0.073760 | 0 | 3 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `908ee7108de0595712e8ef1cd2ae3a6844bd556a470f02b3f546efb79c94bed3`
