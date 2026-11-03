# Operations Dashboard

Overall: **AMBER**
Generated: `2026-11-03T12:41:30.733775Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 4.756 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 9.024 |
| `weekly_output` | **GREEN** | FRESH | 28.441 |
| `automation_health` | **AMBER** | AMBER | 0.552 |
| `architecture_health` | **GREEN** | GREEN | 0.513 |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.977 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 3.011 |
| `remediation_maturation` | **GREEN** | FRESH | 0.266 |

## AI and learning activity

- OpenAI receipts this month: **37**
- OpenAI estimated cost this month: **$2.470384 from receipts**
- Pending forecast candidates: **279**
- Experiment candidates: **676**
- Experiment dispatch requests: **48678**
- Codex-ready remediation tasks: **4**
- Needs-more-evidence items: **10**

## Incidents

Open incident references: **23**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `DAILY_CONFLICT_REVIEW` | 9 | $1.039532 | 0 | 9 | 0 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 1 | $0.587104 | 0 | 1 | 1 |
| `MONTHLY_LEARNING_ANALYST` | 1 | $0.287610 | 0 | 1 | 0 |
| `SHADOW_COMPASS_V2` | 4 | $0.238880 | 0 | 4 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 9 | $0.109934 | 0 | 9 | 9 |
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

Dashboard SHA-256: `6b5d4bef12586f601e0c3ba680639e434ea64c1a918d0124313410bab177f114`
