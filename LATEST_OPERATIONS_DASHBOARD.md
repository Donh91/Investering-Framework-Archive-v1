# Operations Dashboard

Overall: **AMBER**
Generated: `2026-10-20T20:55:38.811227Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 0.936 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 2.803 |
| `weekly_output` | **GREEN** | FRESH | 39.67 |
| `automation_health` | **AMBER** | AMBER | 0.052 |
| `architecture_health` | **AMBER** | AMBER | 0.015 |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.043 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.077 |
| `remediation_maturation` | **GREEN** | FRESH | 1.356 |

## AI and learning activity

- OpenAI receipts this month: **269**
- OpenAI estimated cost this month: **$12.853907 from receipts**
- Pending forecast candidates: **251**
- Experiment candidates: **575**
- Experiment dispatch requests: **34144**
- Codex-ready remediation tasks: **6**
- Needs-more-evidence items: **1**

## Incidents

Open incident references: **22**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `DAILY_CONFLICT_REVIEW` | 32 | $2.936662 | 0 | 32 | 0 |
| `SHADOW_COMPASS_V2` | 44 | $2.708154 | 0 | 44 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 18 | $2.476158 | 0 | 18 | 1 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 4 | $1.036608 | 0 | 4 | 0 |
| `MONTHLY_LEARNING_ANALYST` | 4 | $1.026470 | 0 | 4 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 80 | $0.821774 | 0 | 80 | 79 |
| `FMOS_AUTONOMOUS_MISSION_LOOP_AUDIT` | 3 | $0.718824 | 0 | 3 | 0 |
| `TEMP_SOL_PR_REVIEW` | 6 | $0.427192 | 0 | 6 | 2 |
| `DECISION_MISS_AUDIT` | 20 | $0.252288 | 0 | 14 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 20 | $0.133194 | 0 | 0 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 3 | $0.101492 | 0 | 3 | 0 |
| `UNCLASSIFIED` | 3 | $0.073760 | 0 | 3 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `architecture_health` - ['OWNER_TOPOLOGY_LEGACY_UNBOUND']
- **P1** `automation_health` - SEMANTIC_STATUS_AMBER
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `f6f06e2dedb8d9d1072944c1b9a8c3367719c2791a3f04aeba004969b7b19180`
