# Operations Dashboard

Overall: **AMBER**
Generated: `2026-11-05T12:59:31.804795Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 5.069 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 10.28 |
| `weekly_output` | **GREEN** | FRESH | 76.741 |
| `automation_health` | **AMBER** | AMBER | 0.402 |
| `architecture_health` | **GREEN** | GREEN | 0.342 |
| `experiment_lifecycle` | **GREEN** | FRESH | 3.341 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 3.386 |
| `remediation_maturation` | **GREEN** | FRESH | 0.196 |

## AI and learning activity

- OpenAI receipts this month: **66**
- OpenAI estimated cost this month: **$4.510260 from receipts**
- Pending forecast candidates: **283**
- Experiment candidates: **691**
- Experiment dispatch requests: **51050**
- Codex-ready remediation tasks: **12**
- Needs-more-evidence items: **10**

## Incidents

Open incident references: **23**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `DAILY_CONFLICT_REVIEW` | 17 | $1.972900 | 0 | 17 | 0 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 2 | $0.878252 | 0 | 2 | 1 |
| `MONTHLY_LEARNING_ANALYST` | 2 | $0.577860 | 0 | 2 | 0 |
| `SHADOW_COMPASS_V2` | 8 | $0.508652 | 0 | 8 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 17 | $0.208209 | 0 | 17 | 17 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 1 | $0.107406 | 0 | 1 | 0 |
| `DECISION_MISS_AUDIT` | 5 | $0.073896 | 0 | 5 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 1 | $0.050186 | 0 | 1 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 5 | $0.033528 | 0 | 0 | 0 |
| `UNCLASSIFIED` | 1 | $0.030018 | 0 | 1 | 0 |
| `CN_PRECISION_4W_REVIEW` | 1 | $0.028784 | 0 | 1 | 0 |
| `CN_INTERNAL_LONG_HORIZON_SCORER` | 1 | $0.024004 | 0 | 1 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `59ed35ce56ded88223957513f70203f4cf04c4837ff9e29db85f7ed51c82d4ae`
