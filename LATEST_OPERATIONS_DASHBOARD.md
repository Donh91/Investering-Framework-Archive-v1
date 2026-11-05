# Operations Dashboard

Overall: **RED**
Generated: `2026-11-05T22:13:51.087564Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 1.581 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 0.987 |
| `weekly_output` | **GREEN** | FRESH | 85.98 |
| `automation_health` | **RED** | RED | 0.068 |
| `architecture_health` | **GREEN** | GREEN | 0.015 |
| `experiment_lifecycle` | **GREEN** | FRESH | 0.983 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 12.624 |
| `remediation_maturation` | **GREEN** | FRESH | 9.435 |

## AI and learning activity

- OpenAI receipts this month: **74**
- OpenAI estimated cost this month: **$5.253415 from receipts**
- Pending forecast candidates: **283**
- Experiment candidates: **695**
- Experiment dispatch requests: **51959**
- Codex-ready remediation tasks: **12**
- Needs-more-evidence items: **10**

## Incidents

Open incident references: **24**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `DAILY_CONFLICT_REVIEW` | 20 | $2.320492 | 0 | 20 | 0 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 2 | $0.878252 | 0 | 2 | 1 |
| `MONTHLY_LEARNING_ANALYST` | 3 | $0.870176 | 0 | 3 | 0 |
| `SHADOW_COMPASS_V2` | 9 | $0.575290 | 0 | 9 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 20 | $0.244818 | 0 | 20 | 20 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 1 | $0.107406 | 0 | 1 | 0 |
| `DECISION_MISS_AUDIT` | 5 | $0.073896 | 0 | 5 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 1 | $0.050186 | 0 | 1 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 5 | $0.033528 | 0 | 0 | 0 |
| `UNCLASSIFIED` | 1 | $0.030018 | 0 | 1 | 0 |
| `CN_PRECISION_4W_REVIEW` | 1 | $0.028784 | 0 | 1 | 0 |
| `CN_INTERNAL_LONG_HORIZON_SCORER` | 1 | $0.024004 | 0 | 1 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P0** `automation_health` - ['research-lab-sol-dispatch.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `4eff6765a8e3fb5cb1688046fbcdeb40e3a2655bbb93a6cdc88abbea271cdcf8`
