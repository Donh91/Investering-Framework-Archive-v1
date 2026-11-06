# Operations Dashboard

Overall: **AMBER**
Generated: `2026-11-06T12:21:57.214955Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 4.423 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 9.597 |
| `weekly_output` | **GREEN** | FRESH | 100.115 |
| `automation_health` | **AMBER** | AMBER | 0.066 |
| `architecture_health` | **GREEN** | GREEN | 0.014 |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.824 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.872 |
| `remediation_maturation` | **GREEN** | FRESH | 14.047 |

## AI and learning activity

- OpenAI receipts this month: **82**
- OpenAI estimated cost this month: **$5.659104 from receipts**
- Pending forecast candidates: **285**
- Experiment candidates: **697**
- Experiment dispatch requests: **52264**
- Codex-ready remediation tasks: **5**
- Needs-more-evidence items: **3**

## Incidents

Open incident references: **24**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `DAILY_CONFLICT_REVIEW` | 21 | $2.437202 | 0 | 21 | 0 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 2 | $0.878252 | 0 | 2 | 1 |
| `MONTHLY_LEARNING_ANALYST` | 3 | $0.870176 | 0 | 3 | 0 |
| `SHADOW_COMPASS_V2` | 10 | $0.634400 | 0 | 10 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 2 | $0.284578 | 0 | 2 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 21 | $0.256929 | 0 | 21 | 21 |
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

Dashboard SHA-256: `e56b2e58b80c757c722b599c91bfd31b85f82f651b7be0d65c3cfa27ac54fd9b`
