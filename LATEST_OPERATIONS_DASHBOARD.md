# Operations Dashboard

Overall: **AMBER**
Generated: `2026-11-04T22:26:31.633136Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 2.022 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 1.49 |
| `weekly_output` | **GREEN** | FRESH | 62.191 |
| `automation_health` | **AMBER** | AMBER | 0.416 |
| `architecture_health` | **GREEN** | GREEN | 0.367 |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.485 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 13.002 |
| `remediation_maturation` | **GREEN** | FRESH | 0.25 |

## AI and learning activity

- OpenAI receipts this month: **60**
- OpenAI estimated cost this month: **$4.295009 from receipts**
- Pending forecast candidates: **281**
- Experiment candidates: **689**
- Experiment dispatch requests: **50747**
- Codex-ready remediation tasks: **4**
- Needs-more-evidence items: **3**

## Incidents

Open incident references: **23**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `DAILY_CONFLICT_REVIEW` | 16 | $1.857162 | 0 | 16 | 0 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 2 | $0.878252 | 0 | 2 | 1 |
| `MONTHLY_LEARNING_ANALYST` | 2 | $0.577860 | 0 | 2 | 0 |
| `SHADOW_COMPASS_V2` | 7 | $0.446108 | 0 | 7 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 16 | $0.196020 | 0 | 16 | 16 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 1 | $0.107406 | 0 | 1 | 0 |
| `DECISION_MISS_AUDIT` | 4 | $0.059023 | 0 | 4 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 1 | $0.050186 | 0 | 1 | 0 |
| `UNCLASSIFIED` | 1 | $0.030018 | 0 | 1 | 0 |
| `CN_PRECISION_4W_REVIEW` | 1 | $0.028784 | 0 | 1 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 4 | $0.026875 | 0 | 0 | 0 |
| `CN_INTERNAL_LONG_HORIZON_SCORER` | 1 | $0.024004 | 0 | 1 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `48d80907bdf83e93b8f306ff3597dec1b803e442cfbb7ffa0ac4bbcf772eb3c6`
