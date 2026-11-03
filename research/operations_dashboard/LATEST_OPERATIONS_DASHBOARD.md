# Operations Dashboard

Overall: **AMBER**
Generated: `2026-11-03T22:13:17.695004Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 2.1 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 1.548 |
| `weekly_output` | **GREEN** | FRESH | 37.971 |
| `automation_health` | **AMBER** | AMBER | 0.331 |
| `architecture_health` | **GREEN** | GREEN | 0.28 |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.543 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 12.54 |
| `remediation_maturation` | **GREEN** | FRESH | 0.142 |

## AI and learning activity

- OpenAI receipts this month: **46**
- OpenAI estimated cost this month: **$3.505802 from receipts**
- Pending forecast candidates: **279**
- Experiment candidates: **681**
- Experiment dispatch requests: **49554**
- Codex-ready remediation tasks: **3**
- Needs-more-evidence items: **3**

## Incidents

Open incident references: **23**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `DAILY_CONFLICT_REVIEW` | 12 | $1.387242 | 0 | 12 | 0 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 2 | $0.878252 | 0 | 2 | 1 |
| `MONTHLY_LEARNING_ANALYST` | 2 | $0.577860 | 0 | 2 | 0 |
| `SHADOW_COMPASS_V2` | 5 | $0.308648 | 0 | 5 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 12 | $0.146475 | 0 | 12 | 12 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 1 | $0.050186 | 0 | 1 | 0 |
| `DECISION_MISS_AUDIT` | 3 | $0.044222 | 0 | 3 | 0 |
| `UNCLASSIFIED` | 1 | $0.030018 | 0 | 1 | 0 |
| `CN_PRECISION_4W_REVIEW` | 1 | $0.028784 | 0 | 1 | 0 |
| `CN_INTERNAL_LONG_HORIZON_SCORER` | 1 | $0.024004 | 0 | 1 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 3 | $0.020150 | 0 | 0 | 0 |
| `EVIDENCE_GAP_AUDIT` | 3 | $0.009961 | 0 | 0 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `7cefa82a116a53ba3bffd18b05252223bc23078c09cbe76a5891252810f27b84`
