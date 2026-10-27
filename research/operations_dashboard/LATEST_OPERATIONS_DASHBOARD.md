# Operations Dashboard

Overall: **AMBER**
Generated: `2026-10-27T09:59:48.308660Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 3.7 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 8.396 |
| `weekly_output` | **GREEN** | FRESH | 27.074 |
| `automation_health` | **AMBER** | AMBER | 0.069 |
| `architecture_health` | **GREEN** | GREEN | 0.012 |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.0 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.015 |
| `remediation_maturation` | **GREEN** | FRESH | 12.733 |

## AI and learning activity

- OpenAI receipts this month: **337**
- OpenAI estimated cost this month: **$14.524178 from receipts**
- Pending forecast candidates: **265**
- Experiment candidates: **624**
- Experiment dispatch requests: **40849**
- Codex-ready remediation tasks: **2**
- Needs-more-evidence items: **3**

## Incidents

Open incident references: **23**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `SHADOW_COMPASS_V2` | 58 | $3.579232 | 0 | 58 | 0 |
| `DAILY_CONFLICT_REVIEW` | 32 | $2.936662 | 0 | 32 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 18 | $2.476158 | 0 | 18 | 1 |
| `DAILY_DIRECTOR_SHADOW` | 105 | $1.112344 | 0 | 105 | 104 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 4 | $1.036608 | 0 | 4 | 0 |
| `MONTHLY_LEARNING_ANALYST` | 4 | $1.026470 | 0 | 4 | 0 |
| `FMOS_AUTONOMOUS_MISSION_LOOP_AUDIT` | 3 | $0.718824 | 0 | 3 | 0 |
| `TEMP_SOL_PR_REVIEW` | 8 | $0.674266 | 0 | 8 | 4 |
| `DECISION_MISS_AUDIT` | 27 | $0.349661 | 0 | 21 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 27 | $0.179939 | 0 | 0 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 4 | $0.145990 | 0 | 4 | 0 |
| `UNCLASSIFIED` | 4 | $0.094826 | 0 | 4 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `c47d7fe7fa0d393cb0067d06f1477f9d7b45570679a21b06f551aab4304a7344`
