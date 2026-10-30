# Operations Dashboard

Overall: **RED**
Generated: `2026-10-30T11:01:28.025452Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 3.895 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 8.899 |
| `weekly_output` | **GREEN** | FRESH | 100.101 |
| `automation_health` | **RED** | RED | 0.073 |
| `architecture_health` | **GREEN** | GREEN | 0.014 |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.253 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.279 |
| `remediation_maturation` | **GREEN** | FRESH | 13.596 |

## AI and learning activity

- OpenAI receipts this month: **364**
- OpenAI estimated cost this month: **$15.119487 from receipts**
- Pending forecast candidates: **271**
- Experiment candidates: **644**
- Experiment dispatch requests: **44138**
- Codex-ready remediation tasks: **3**
- Needs-more-evidence items: **3**

## Incidents

Open incident references: **24**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `SHADOW_COMPASS_V2` | 64 | $3.958398 | 0 | 64 | 0 |
| `DAILY_CONFLICT_REVIEW` | 32 | $2.936662 | 0 | 32 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 18 | $2.476158 | 0 | 18 | 1 |
| `DAILY_DIRECTOR_SHADOW` | 117 | $1.255719 | 0 | 117 | 116 |
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

Dashboard SHA-256: `a505ae6e8d35a357b6bbfb577a853a9b4de8cba502789cf1362bd48be75a98a9`
