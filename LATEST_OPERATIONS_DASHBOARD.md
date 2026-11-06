# Operations Dashboard

Overall: **AMBER**
Generated: `2026-11-06T21:45:34.781865Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 1.81 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 1.171 |
| `weekly_output` | **GREEN** | FRESH | 109.509 |
| `automation_health` | **AMBER** | AMBER | 0.075 |
| `architecture_health` | **GREEN** | GREEN | 0.024 |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.166 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 7.145 |
| `remediation_maturation` | **GREEN** | FRESH | 9.228 |

## AI and learning activity

- OpenAI receipts this month: **95**
- OpenAI estimated cost this month: **$7.717903 from receipts**
- Pending forecast candidates: **285**
- Experiment candidates: **703**
- Experiment dispatch requests: **53179**
- Codex-ready remediation tasks: **11**
- Needs-more-evidence items: **5**

## Incidents

Open incident references: **23**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `DAILY_CONFLICT_REVIEW` | 24 | $2.789474 | 0 | 24 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 8 | $1.890838 | 0 | 8 | 0 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 2 | $0.878252 | 0 | 2 | 1 |
| `MONTHLY_LEARNING_ANALYST` | 3 | $0.870176 | 0 | 3 | 0 |
| `SHADOW_COMPASS_V2` | 11 | $0.697666 | 0 | 11 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 24 | $0.293930 | 0 | 24 | 24 |
| `DECISION_MISS_AUDIT` | 6 | $0.088858 | 0 | 6 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 1 | $0.050186 | 0 | 1 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 6 | $0.040173 | 0 | 0 | 0 |
| `UNCLASSIFIED` | 1 | $0.030018 | 0 | 1 | 0 |
| `CN_PRECISION_4W_REVIEW` | 1 | $0.028784 | 0 | 1 | 0 |
| `CN_INTERNAL_LONG_HORIZON_SCORER` | 1 | $0.024004 | 0 | 1 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `25ee071619de9b6ba64108fac012412090c0ce21ecb48d6b5fdb81b649329477`
