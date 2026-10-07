# Operations Dashboard

Overall: **RED**
Generated: `2026-10-07T10:29:20.100024Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 4.469 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 9.52 |
| `weekly_output` | **GREEN** | FRESH | 52.305 |
| `automation_health` | **RED** | RED | 0.05 |
| `architecture_health` | **GREEN** | GREEN | 0.009 |
| `experiment_lifecycle` | **GREEN** | FRESH | 3.184 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 3.186 |
| `remediation_maturation` | **GREEN** | FRESH | 2.545 |

## AI and learning activity

- OpenAI receipts this month: **114**
- OpenAI cost this month: **$7.793454**
- Pending forecast candidates: **226**
- Experiment candidates: **472**
- Experiment dispatch requests: **20899**
- Codex-ready remediation tasks: **4**
- Needs-more-evidence items: **2**

## Incidents

Open incident references: **26**

## Required actions

- **P0** `automation_health` - ['adaptive-decision-miss-validation.yml:LATEST_RUN_FAILED', 'edge001-t2-registry.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `dc103ce4fe257acc85236c5a6fc393de528fa8f1a64c585a08f8bb8882faf2aa`
