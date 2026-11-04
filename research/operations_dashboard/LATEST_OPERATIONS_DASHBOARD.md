# Operations Dashboard

Overall: **AMBER**
Generated: `2026-11-04T12:25:53.573289Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 4.923 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 9.815 |
| `weekly_output` | **GREEN** | FRESH | 52.181 |
| `automation_health` | **AMBER** | AMBER | 0.078 |
| `architecture_health` | **GREEN** | GREEN | 0.015 |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.953 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.992 |
| `remediation_maturation` | **GREEN** | FRESH | 14.352 |

## AI and learning activity

- OpenAI receipts this month: **52**
- OpenAI estimated cost this month: **$3.726145 from receipts**
- Pending forecast candidates: **281**
- Experiment candidates: **683**
- Experiment dispatch requests: **49848**
- Codex-ready remediation tasks: **3**
- Needs-more-evidence items: **3**

## Incidents

Open incident references: **23**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `DAILY_CONFLICT_REVIEW` | 13 | $1.503904 | 0 | 13 | 0 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 2 | $0.878252 | 0 | 2 | 1 |
| `MONTHLY_LEARNING_ANALYST` | 2 | $0.577860 | 0 | 2 | 0 |
| `SHADOW_COMPASS_V2` | 6 | $0.375154 | 0 | 6 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 13 | $0.158774 | 0 | 13 | 13 |
| `DECISION_MISS_AUDIT` | 4 | $0.059023 | 0 | 4 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 1 | $0.050186 | 0 | 1 | 0 |
| `UNCLASSIFIED` | 1 | $0.030018 | 0 | 1 | 0 |
| `CN_PRECISION_4W_REVIEW` | 1 | $0.028784 | 0 | 1 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 4 | $0.026875 | 0 | 0 | 0 |
| `CN_INTERNAL_LONG_HORIZON_SCORER` | 1 | $0.024004 | 0 | 1 | 0 |
| `EVIDENCE_GAP_AUDIT` | 4 | $0.013312 | 0 | 0 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `5ccf1f98af598b7686bbdf017d5d8705508e6d6a07a9e8949419ac7bc1c47d97`
