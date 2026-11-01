# Operations Dashboard

Overall: **AMBER**
Generated: `2026-11-01T11:28:01.031198Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 3.905 |
| `openai_daily_director` | **GREEN** | FRESH | 10.067 |
| `weekly_output` | **GREEN** | FRESH | 148.544 |
| `automation_health` | **AMBER** | AMBER | 0.062 |
| `architecture_health` | **GREEN** | GREEN | 0.013 |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.997 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.089 |
| `remediation_maturation` | **GREEN** | FRESH | 15.168 |

## AI and learning activity

- OpenAI receipts this month: **5**
- OpenAI estimated cost this month: **$0.154641 from receipts**
- Pending forecast candidates: **275**
- Experiment candidates: **660**
- Experiment dispatch requests: **46368**
- Codex-ready remediation tasks: **3**
- Needs-more-evidence items: **3**

## Incidents

Open incident references: **23**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `DAILY_CONFLICT_REVIEW` | 1 | $0.117564 | 0 | 1 | 0 |
| `DECISION_MISS_AUDIT` | 1 | $0.014743 | 0 | 1 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 1 | $0.012282 | 0 | 1 | 1 |
| `EVIDENCE_GAP_VALIDATION` | 1 | $0.006747 | 0 | 0 | 0 |
| `EVIDENCE_GAP_AUDIT` | 1 | $0.003305 | 0 | 0 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER

Dashboard SHA-256: `516632d649f7a05dc043c26544ae37b0c0f32307faa6995be3dc19476f4bfca3`
