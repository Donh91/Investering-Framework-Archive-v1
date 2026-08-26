# Operations Dashboard

Overall: **RED**
Generated: `2026-08-26T16:47:36.351778Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 3.542 |
| `openai_daily_director` | **RED** | STALE | 31.175 |
| `weekly_output` | **UNKNOWN** | TIMESTAMP_UNAVAILABLE | - |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **GREEN** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.417 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 13.943 |
| `remediation_maturation` | **GREEN** | FRESH | 0.163 |

## AI and learning activity

- OpenAI receipts this month: **135**
- OpenAI cost this month: **$6.259839**
- Pending forecast candidates: **126**
- Experiment candidates: **151**
- Experiment dispatch requests: **681**
- Codex-ready remediation tasks: **17**
- Needs-more-evidence items: **29**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['api-agent-gateway-gate.yml:REPEATED_CONSECUTIVE_FAILURES', 'historical-altseason-cfgi-reservation.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P0** `openai_daily_director` - STALE
- **P1** `weekly_output` - TIMESTAMP_UNAVAILABLE

Dashboard SHA-256: `6b5c18b868450f890f0b4a1f064c33052d8394c0ee85b5acc1d6d902be56e1a9`
