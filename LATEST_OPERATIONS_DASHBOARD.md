# Operations Dashboard

Overall: **RED**
Generated: `2026-08-26T04:44:11.890353Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 2.752 |
| `openai_daily_director` | **AMBER** | DELAYED | 19.118 |
| `weekly_output` | **UNKNOWN** | TIMESTAMP_UNAVAILABLE | - |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **GREEN** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.886 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 1.886 |
| `remediation_maturation` | **GREEN** | FRESH | 0.319 |

## AI and learning activity

- OpenAI receipts this month: **129**
- OpenAI cost this month: **$5.865384**
- Pending forecast candidates: **126**
- Experiment candidates: **145**
- Experiment dispatch requests: **505**
- Codex-ready remediation tasks: **15**
- Needs-more-evidence items: **32**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['api-agent-gateway-gate.yml:REPEATED_CONSECUTIVE_FAILURES', 'historical-altseason-cfgi-reservation.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P1** `openai_daily_director` - DELAYED
- **P1** `weekly_output` - TIMESTAMP_UNAVAILABLE

Dashboard SHA-256: `18396a18e5acfaa99602627aa5b3dd69fdf1a45d921e7182482bdf93ccb4fcff`
