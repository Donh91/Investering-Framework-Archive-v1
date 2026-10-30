# Operations Dashboard

Overall: **RED**
Generated: `2026-10-30T23:44:28.115242Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 2.253 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 4.028 |
| `weekly_output` | **GREEN** | FRESH | 112.818 |
| `automation_health` | **RED** | RED | 0.084 |
| `architecture_health` | **GREEN** | GREEN | 0.03 |
| `experiment_lifecycle` | **GREEN** | FRESH | 4.028 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 14.996 |
| `remediation_maturation` | **GREEN** | FRESH | 2.701 |

## AI and learning activity

- OpenAI receipts this month: **369**
- OpenAI estimated cost this month: **$15.275786 from receipts**
- Pending forecast candidates: **271**
- Experiment candidates: **650**
- Experiment dispatch requests: **44966**
- Codex-ready remediation tasks: **3**
- Needs-more-evidence items: **4**

## Incidents

Open incident references: **26**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `SHADOW_COMPASS_V2` | 66 | $4.078276 | 0 | 66 | 0 |
| `DAILY_CONFLICT_REVIEW` | 32 | $2.936662 | 0 | 32 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 18 | $2.476158 | 0 | 18 | 1 |
| `DAILY_DIRECTOR_SHADOW` | 120 | $1.292139 | 0 | 120 | 119 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 4 | $1.036608 | 0 | 4 | 0 |
| `MONTHLY_LEARNING_ANALYST` | 4 | $1.026470 | 0 | 4 | 0 |
| `FMOS_AUTONOMOUS_MISSION_LOOP_AUDIT` | 3 | $0.718824 | 0 | 3 | 0 |
| `TEMP_SOL_PR_REVIEW` | 8 | $0.674266 | 0 | 8 | 4 |
| `DECISION_MISS_AUDIT` | 30 | $0.392313 | 0 | 24 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 30 | $0.200276 | 0 | 0 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 4 | $0.145990 | 0 | 4 | 0 |
| `UNCLASSIFIED` | 4 | $0.094826 | 0 | 4 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P0** `automation_health` - ['framework-learning-supervisor.yml:LATEST_RUN_FAILED']
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `ffcbee2dd9a770d9779356ffd5af18c61ab10f21aeda423d9630f2379d612384`
