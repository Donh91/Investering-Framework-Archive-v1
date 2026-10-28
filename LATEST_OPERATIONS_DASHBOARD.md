# Operations Dashboard

Overall: **AMBER**
Generated: `2026-10-28T21:16:35.441912Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 2.397 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 1.368 |
| `weekly_output` | **GREEN** | FRESH | 62.353 |
| `automation_health` | **AMBER** | AMBER | 0.068 |
| `architecture_health` | **GREEN** | GREEN | 0.02 |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.368 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 12.585 |
| `remediation_maturation` | **GREEN** | FRESH | 9.93 |

## AI and learning activity

- OpenAI receipts this month: **350**
- OpenAI estimated cost this month: **$14.812668 from receipts**
- Pending forecast candidates: **267**
- Experiment candidates: **634**
- Experiment dispatch requests: **42762**
- Codex-ready remediation tasks: **3**
- Needs-more-evidence items: **3**

## Incidents

Open incident references: **23**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `SHADOW_COMPASS_V2` | 61 | $3.760024 | 0 | 61 | 0 |
| `DAILY_CONFLICT_REVIEW` | 32 | $2.936662 | 0 | 32 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 18 | $2.476158 | 0 | 18 | 1 |
| `DAILY_DIRECTOR_SHADOW` | 112 | $1.195799 | 0 | 112 | 111 |
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

Dashboard SHA-256: `dd678f6885dab01dc42752e472116ef3619b4dc5a0149c31e9c95da284f0c0ae`
