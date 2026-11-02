# Operations Dashboard

Overall: **AMBER**
Generated: `2026-11-02T23:44:04.201694Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 1.427 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 0.831 |
| `weekly_output` | **GREEN** | FRESH | 15.484 |
| `automation_health` | **AMBER** | AMBER | 0.093 |
| `architecture_health` | **GREEN** | GREEN | 0.04 |
| `experiment_lifecycle` | **GREEN** | FRESH | 0.826 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 14.115 |
| `remediation_maturation` | **GREEN** | FRESH | 0.017 |

## AI and learning activity

- OpenAI receipts this month: **31**
- OpenAI estimated cost this month: **$2.258049 from receipts**
- Pending forecast candidates: **277**
- Experiment candidates: **674**
- Experiment dispatch requests: **48388**
- Codex-ready remediation tasks: **4**
- Needs-more-evidence items: **4**

## Incidents

Open incident references: **23**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `DAILY_CONFLICT_REVIEW` | 8 | $0.924634 | 0 | 8 | 0 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 1 | $0.587104 | 0 | 1 | 1 |
| `MONTHLY_LEARNING_ANALYST` | 1 | $0.287610 | 0 | 1 | 0 |
| `SHADOW_COMPASS_V2` | 3 | $0.178412 | 0 | 3 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 8 | $0.097877 | 0 | 8 | 8 |
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

Dashboard SHA-256: `3f963a22d321d011665bb8477960da285c3158c5adf4c84b2fce691229015739`
