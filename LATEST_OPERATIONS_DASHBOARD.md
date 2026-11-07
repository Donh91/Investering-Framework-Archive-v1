# Operations Dashboard

Overall: **RED**
Generated: `2026-11-07T11:35:58.850107Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 4.396 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 9.334 |
| `weekly_output` | **GREEN** | FRESH | 123.349 |
| `automation_health` | **RED** | RED | 0.377 |
| `architecture_health` | **GREEN** | GREEN | 0.325 |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.599 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.7 |
| `remediation_maturation` | **GREEN** | FRESH | 0.226 |

## AI and learning activity

- OpenAI receipts this month: **101**
- OpenAI estimated cost this month: **$7.940444 from receipts**
- Pending forecast candidates: **287**
- Experiment candidates: **705**
- Experiment dispatch requests: **53490**
- Codex-ready remediation tasks: **6**
- Needs-more-evidence items: **4**

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

Dashboard SHA-256: `92ea6aa1ddf13c7961436ee54705d966e58f699b5c5f4ba666281124406ebf43`
