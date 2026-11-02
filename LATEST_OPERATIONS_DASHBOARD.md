# Operations Dashboard

Overall: **AMBER**
Generated: `2026-11-02T13:15:42.163241Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 5.562 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 11.524 |
| `weekly_output` | **GREEN** | FRESH | 5.011 |
| `automation_health` | **AMBER** | AMBER | 0.552 |
| `architecture_health` | **GREEN** | GREEN | 0.497 |
| `experiment_lifecycle` | **GREEN** | FRESH | 3.603 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 3.642 |
| `remediation_maturation` | **GREEN** | FRESH | 0.355 |

## AI and learning activity

- OpenAI receipts this month: **24**
- OpenAI estimated cost this month: **$1.821535 from receipts**
- Pending forecast candidates: **277**
- Experiment candidates: **668**
- Experiment dispatch requests: **47515**
- Codex-ready remediation tasks: **3**
- Needs-more-evidence items: **21**

## Incidents

Open incident references: **23**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `MONTHLY_LEARNING_ADVERSARIAL` | 1 | $0.587104 | 0 | 1 | 1 |
| `DAILY_CONFLICT_REVIEW` | 5 | $0.573502 | 0 | 5 | 0 |
| `MONTHLY_LEARNING_ANALYST` | 1 | $0.287610 | 0 | 1 | 0 |
| `SHADOW_COMPASS_V2` | 2 | $0.130136 | 0 | 2 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 5 | $0.060771 | 0 | 5 | 5 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 1 | $0.050186 | 0 | 1 | 0 |
| `UNCLASSIFIED` | 1 | $0.030018 | 0 | 1 | 0 |
| `DECISION_MISS_AUDIT` | 2 | $0.029298 | 0 | 2 | 0 |
| `CN_PRECISION_4W_REVIEW` | 1 | $0.028784 | 0 | 1 | 0 |
| `CN_INTERNAL_LONG_HORIZON_SCORER` | 1 | $0.024004 | 0 | 1 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 2 | $0.013474 | 0 | 0 | 0 |
| `EVIDENCE_GAP_AUDIT` | 2 | $0.006648 | 0 | 0 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `eb8ee3dbe7cf10439470217cb738e418b194d76f9d8f50f47005248931a4b69a`
