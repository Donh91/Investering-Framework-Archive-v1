# Operations Dashboard

Overall: **AMBER**
Generated: `2026-10-26T21:10:14.987587Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 1.896 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 1.01 |
| `weekly_output` | **GREEN** | FRESH | 14.248 |
| `automation_health` | **AMBER** | AMBER | 0.057 |
| `architecture_health` | **GREEN** | GREEN | 0.012 |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.01 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 13.281 |
| `remediation_maturation` | **GREEN** | FRESH | 10.604 |

## AI and learning activity

- OpenAI receipts this month: **332**
- OpenAI estimated cost this month: **$14.422849 from receipts**
- Pending forecast candidates: **263**
- Experiment candidates: **622**
- Experiment dispatch requests: **40578**
- Codex-ready remediation tasks: **2**
- Needs-more-evidence items: **3**

## Incidents

Open incident references: **23**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `SHADOW_COMPASS_V2` | 57 | $3.513870 | 0 | 57 | 0 |
| `DAILY_CONFLICT_REVIEW` | 32 | $2.936662 | 0 | 32 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 18 | $2.476158 | 0 | 18 | 1 |
| `DAILY_DIRECTOR_SHADOW` | 104 | $1.100860 | 0 | 104 | 103 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 4 | $1.036608 | 0 | 4 | 0 |
| `MONTHLY_LEARNING_ANALYST` | 4 | $1.026470 | 0 | 4 | 0 |
| `FMOS_AUTONOMOUS_MISSION_LOOP_AUDIT` | 3 | $0.718824 | 0 | 3 | 0 |
| `TEMP_SOL_PR_REVIEW` | 8 | $0.674266 | 0 | 8 | 4 |
| `DECISION_MISS_AUDIT` | 26 | $0.335244 | 0 | 20 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 26 | $0.173142 | 0 | 0 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 4 | $0.145990 | 0 | 4 | 0 |
| `UNCLASSIFIED` | 4 | $0.094826 | 0 | 4 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `38ffc0a088ea74f9042a34f92367c33e394e00ec07440d74d0605d5f21ae42d5`
