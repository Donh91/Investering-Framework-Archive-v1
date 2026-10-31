# Operations Dashboard

Overall: **AMBER**
Generated: `2026-10-31T10:48:00.426930Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 3.784 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 9.033 |
| `weekly_output` | **GREEN** | FRESH | 123.877 |
| `automation_health` | **AMBER** | AMBER | 0.31 |
| `architecture_health` | **GREEN** | GREEN | 0.263 |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.198 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.293 |
| `remediation_maturation` | **GREEN** | FRESH | 0.159 |

## AI and learning activity

- OpenAI receipts this month: **374**
- OpenAI estimated cost this month: **$15.313099 from receipts**
- Pending forecast candidates: **273**
- Experiment candidates: **652**
- Experiment dispatch requests: **45244**
- Codex-ready remediation tasks: **3**
- Needs-more-evidence items: **3**

## Incidents

Open incident references: **26**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `SHADOW_COMPASS_V2` | 66 | $4.078276 | 0 | 66 | 0 |
| `DAILY_CONFLICT_REVIEW` | 32 | $2.936662 | 0 | 32 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 18 | $2.476158 | 0 | 18 | 1 |
| `DAILY_DIRECTOR_SHADOW` | 121 | $1.304570 | 0 | 121 | 120 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 4 | $1.036608 | 0 | 4 | 0 |
| `MONTHLY_LEARNING_ANALYST` | 4 | $1.026470 | 0 | 4 | 0 |
| `FMOS_AUTONOMOUS_MISSION_LOOP_AUDIT` | 3 | $0.718824 | 0 | 3 | 0 |
| `TEMP_SOL_PR_REVIEW` | 8 | $0.674266 | 0 | 8 | 4 |
| `DECISION_MISS_AUDIT` | 31 | $0.406731 | 0 | 25 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 31 | $0.207032 | 0 | 0 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 4 | $0.145990 | 0 | 4 | 0 |
| `EVIDENCE_GAP_AUDIT` | 29 | $0.097717 | 0 | 0 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `69b34a634c88fd552892f87c71bc5908f0baa6581b75d78cc2b7b9bb24b61469`
