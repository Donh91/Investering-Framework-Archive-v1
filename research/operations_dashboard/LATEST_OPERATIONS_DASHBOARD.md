# Operations Dashboard

Overall: **AMBER**
Generated: `2026-10-17T07:59:49.985366Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 3.536 |
| `openai_daily_director` | **GREEN** | FRESH | 8.192 |
| `weekly_output` | **GREEN** | FRESH | 121.523 |
| `automation_health` | **AMBER** | AMBER | 0.054 |
| `architecture_health` | **GREEN** | GREEN | 0.01 |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.282 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.339 |
| `remediation_maturation` | **GREEN** | FRESH | 12.969 |

## AI and learning activity

- OpenAI receipts this month: **233**
- OpenAI estimated cost this month: **$11.858567 from receipts**
- Pending forecast candidates: **246**
- Experiment candidates: **549**
- Experiment dispatch requests: **30321**
- Codex-ready remediation tasks: **5**
- Needs-more-evidence items: **2**

## Incidents

Open incident references: **22**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `DAILY_CONFLICT_REVIEW` | 32 | $2.936662 | 0 | 32 | 0 |
| `SHADOW_COMPASS_V2` | 37 | $2.277346 | 0 | 37 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 16 | $2.232892 | 0 | 16 | 1 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 4 | $1.036608 | 0 | 4 | 0 |
| `MONTHLY_LEARNING_ANALYST` | 4 | $1.026470 | 0 | 4 | 0 |
| `FMOS_AUTONOMOUS_MISSION_LOOP_AUDIT` | 3 | $0.718824 | 0 | 3 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 65 | $0.657369 | 0 | 65 | 64 |
| `TEMP_SOL_PR_REVIEW` | 6 | $0.427192 | 0 | 6 | 2 |
| `DECISION_MISS_AUDIT` | 17 | $0.212319 | 0 | 11 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 17 | $0.113258 | 0 | 0 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 2 | $0.064436 | 0 | 2 | 0 |
| `EVIDENCE_GAP_AUDIT` | 15 | $0.050586 | 0 | 0 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER

Dashboard SHA-256: `7a932050cb5bc87e9de5ae02dcc9943d424c55ec1235f861e62563e1e94aa763`
