# Operations Dashboard

Overall: **AMBER**
Generated: `2026-10-29T21:20:21.369124Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 2.389 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 1.46 |
| `weekly_output` | **GREEN** | FRESH | 86.416 |
| `automation_health` | **AMBER** | AMBER | 0.064 |
| `architecture_health` | **GREEN** | GREEN | 0.012 |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.459 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 12.716 |
| `remediation_maturation` | **GREEN** | FRESH | 10.198 |

## AI and learning activity

- OpenAI receipts this month: **359**
- OpenAI estimated cost this month: **$15.012583 from receipts**
- Pending forecast candidates: **269**
- Experiment candidates: **642**
- Experiment dispatch requests: **43862**
- Codex-ready remediation tasks: **3**
- Needs-more-evidence items: **4**

## Incidents

Open incident references: **23**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `SHADOW_COMPASS_V2` | 63 | $3.887638 | 0 | 63 | 0 |
| `DAILY_CONFLICT_REVIEW` | 32 | $2.936662 | 0 | 32 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 18 | $2.476158 | 0 | 18 | 1 |
| `DAILY_DIRECTOR_SHADOW` | 116 | $1.243807 | 0 | 116 | 115 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 4 | $1.036608 | 0 | 4 | 0 |
| `MONTHLY_LEARNING_ANALYST` | 4 | $1.026470 | 0 | 4 | 0 |
| `FMOS_AUTONOMOUS_MISSION_LOOP_AUDIT` | 3 | $0.718824 | 0 | 3 | 0 |
| `TEMP_SOL_PR_REVIEW` | 8 | $0.674266 | 0 | 8 | 4 |
| `DECISION_MISS_AUDIT` | 29 | $0.377993 | 0 | 23 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 29 | $0.193572 | 0 | 0 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 4 | $0.145990 | 0 | 4 | 0 |
| `UNCLASSIFIED` | 4 | $0.094826 | 0 | 4 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `b4d7be6a30edfb9a0969fdeded5742d877f94b713a3494d07446cbf8023a945d`
