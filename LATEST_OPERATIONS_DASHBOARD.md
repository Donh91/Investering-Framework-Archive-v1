# Operations Dashboard

Overall: **AMBER**
Generated: `2026-10-16T08:24:50.498238Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 3.857 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 8.625 |
| `weekly_output` | **GREEN** | FRESH | 97.939 |
| `automation_health` | **AMBER** | AMBER | 0.063 |
| `architecture_health` | **GREEN** | GREEN | 0.011 |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.485 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.491 |
| `remediation_maturation` | **GREEN** | FRESH | 13.017 |

## AI and learning activity

- OpenAI receipts this month: **224**
- OpenAI estimated cost this month: **$11.673377 from receipts**
- Pending forecast candidates: **244**
- Experiment candidates: **541**
- Experiment dispatch requests: **29310**
- Codex-ready remediation tasks: **5**
- Needs-more-evidence items: **3**

## Incidents

Open incident references: **25**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `DAILY_CONFLICT_REVIEW` | 32 | $2.936662 | 0 | 32 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 16 | $2.232892 | 0 | 16 | 1 |
| `SHADOW_COMPASS_V2` | 35 | $2.158818 | 0 | 35 | 0 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 4 | $1.036608 | 0 | 4 | 0 |
| `MONTHLY_LEARNING_ANALYST` | 4 | $1.026470 | 0 | 4 | 0 |
| `FMOS_AUTONOMOUS_MISSION_LOOP_AUDIT` | 3 | $0.718824 | 0 | 3 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 61 | $0.613759 | 0 | 61 | 60 |
| `TEMP_SOL_PR_REVIEW` | 6 | $0.427192 | 0 | 6 | 2 |
| `DECISION_MISS_AUDIT` | 16 | $0.199267 | 0 | 10 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 16 | $0.106595 | 0 | 0 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 2 | $0.064436 | 0 | 2 | 0 |
| `UNCLASSIFIED` | 2 | $0.049244 | 0 | 2 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `1e7f400394e18a5cf8d8dd66d8920b86c69ca73da323eca73a318bbba1731f91`
