# Operations Dashboard

Overall: **RED**
Generated: `2026-11-07T11:17:33.786751Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 4.089 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 9.027 |
| `weekly_output` | **GREEN** | FRESH | 123.042 |
| `automation_health` | **RED** | RED | 0.071 |
| `architecture_health` | **GREEN** | GREEN | 0.018 |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.292 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.393 |
| `remediation_maturation` | **AMBER** | DELAYED | 22.761 |

## AI and learning activity

- OpenAI receipts this month: **101**
- OpenAI estimated cost this month: **$7.940444 from receipts**
- Pending forecast candidates: **287**
- Experiment candidates: **705**
- Experiment dispatch requests: **53490**
- Codex-ready remediation tasks: **11**
- Needs-more-evidence items: **5**

## Incidents

Open incident references: **24**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `DAILY_CONFLICT_REVIEW` | 25 | $2.906588 | 0 | 25 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 8 | $1.890838 | 0 | 8 | 0 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 2 | $0.878252 | 0 | 2 | 1 |
| `MONTHLY_LEARNING_ANALYST` | 3 | $0.870176 | 0 | 3 | 0 |
| `SHADOW_COMPASS_V2` | 12 | $0.765056 | 0 | 12 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 25 | $0.306476 | 0 | 25 | 25 |
| `DECISION_MISS_AUDIT` | 7 | $0.104229 | 0 | 7 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 1 | $0.050186 | 0 | 1 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 7 | $0.046999 | 0 | 0 | 0 |
| `UNCLASSIFIED` | 1 | $0.030018 | 0 | 1 | 0 |
| `CN_PRECISION_4W_REVIEW` | 1 | $0.028784 | 0 | 1 | 0 |
| `CN_INTERNAL_LONG_HORIZON_SCORER` | 1 | $0.024004 | 0 | 1 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P0** `automation_health` - ['remediation-maturation.yml:LATEST_RUN_FAILED', 'remediation-maturation.yml:SCHEDULE_STALE']
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED
- **P1** `remediation_maturation` - DELAYED

Dashboard SHA-256: `9f0920c2f269faef20d010628787d5f79579b2b01957825737ad04dcef8c6c3a`
