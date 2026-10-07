# Operations Dashboard

Overall: **RED**
Generated: `2026-10-07T10:56:39.836883Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 4.925 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 9.976 |
| `weekly_output` | **GREEN** | FRESH | 52.76 |
| `automation_health` | **RED** | RED | 0.506 |
| `architecture_health` | **GREEN** | GREEN | 0.465 |
| `experiment_lifecycle` | **GREEN** | FRESH | 3.639 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 3.641 |
| `remediation_maturation` | **GREEN** | FRESH | 0.344 |

## AI and learning activity

- OpenAI receipts this month: **115**
- OpenAI cost this month: **$7.793815**
- Pending forecast candidates: **226**
- Experiment candidates: **472**
- Experiment dispatch requests: **20899**
- Codex-ready remediation tasks: **4**
- Needs-more-evidence items: **5**

## Incidents

Open incident references: **26**

## Required actions

- **P0** `automation_health` - ['adaptive-decision-miss-validation.yml:LATEST_RUN_FAILED', 'edge001-t2-registry.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `fe06980586a594fa663dd7e193d5706c44b108668e5ff12c3e2c86755c1b2265`
