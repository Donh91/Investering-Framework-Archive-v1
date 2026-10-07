# Operations Dashboard

Overall: **RED**
Generated: `2026-10-07T07:58:21.446350Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 1.953 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 7.004 |
| `weekly_output` | **GREEN** | FRESH | 49.789 |
| `automation_health` | **RED** | RED | 0.226 |
| `architecture_health` | **GREEN** | GREEN | 0.192 |
| `experiment_lifecycle` | **GREEN** | FRESH | 0.668 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 0.669 |
| `remediation_maturation` | **GREEN** | FRESH | 0.029 |

## AI and learning activity

- OpenAI receipts this month: **113**
- OpenAI cost this month: **$7.793104**
- Pending forecast candidates: **226**
- Experiment candidates: **472**
- Experiment dispatch requests: **20899**
- Codex-ready remediation tasks: **4**
- Needs-more-evidence items: **2**

## Incidents

Open incident references: **25**

## Required actions

- **P0** `automation_health` - ['adaptive-decision-miss-validation.yml:LATEST_RUN_FAILED', 'edge001-t2-registry.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `3328eb55263685389875a309804c0b5d534b29ec9cafc812fafc9f275af20c8e`
