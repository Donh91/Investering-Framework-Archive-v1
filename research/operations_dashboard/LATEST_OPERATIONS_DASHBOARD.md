# Operations Dashboard

Overall: **AMBER**
Generated: `2026-10-28T10:46:13.320664Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 3.898 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 9.183 |
| `weekly_output` | **GREEN** | FRESH | 51.847 |
| `automation_health` | **AMBER** | AMBER | 0.068 |
| `architecture_health` | **GREEN** | GREEN | 0.014 |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.061 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.079 |
| `remediation_maturation` | **GREEN** | FRESH | 13.794 |

## AI and learning activity

- OpenAI receipts this month: **346**
- OpenAI estimated cost this month: **$14.714494 from receipts**
- Pending forecast candidates: **267**
- Experiment candidates: **630**
- Experiment dispatch requests: **41939**
- Codex-ready remediation tasks: **2**
- Needs-more-evidence items: **3**

## Incidents

Open incident references: **23**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `SHADOW_COMPASS_V2` | 60 | $3.697558 | 0 | 60 | 0 |
| `DAILY_CONFLICT_REVIEW` | 32 | $2.936662 | 0 | 32 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 18 | $2.476158 | 0 | 18 | 1 |
| `DAILY_DIRECTOR_SHADOW` | 109 | $1.160091 | 0 | 109 | 108 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 4 | $1.036608 | 0 | 4 | 0 |
| `MONTHLY_LEARNING_ANALYST` | 4 | $1.026470 | 0 | 4 | 0 |
| `FMOS_AUTONOMOUS_MISSION_LOOP_AUDIT` | 3 | $0.718824 | 0 | 3 | 0 |
| `TEMP_SOL_PR_REVIEW` | 8 | $0.674266 | 0 | 8 | 4 |
| `DECISION_MISS_AUDIT` | 28 | $0.363808 | 0 | 22 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 28 | $0.186763 | 0 | 0 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 4 | $0.145990 | 0 | 4 | 0 |
| `UNCLASSIFIED` | 4 | $0.094826 | 0 | 4 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `bdb885b6150b7a28909db830a79447956ec048f9851b0099c9aee8b5301ed476`
