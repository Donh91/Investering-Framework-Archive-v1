# Operations Dashboard

Overall: **AMBER**
Generated: `2026-10-16T18:57:44.935812Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 2.364 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 1.256 |
| `weekly_output` | **GREEN** | FRESH | 108.488 |
| `automation_health` | **AMBER** | AMBER | 0.082 |
| `architecture_health` | **GREEN** | GREEN | 0.014 |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.256 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 13.04 |
| `remediation_maturation` | **GREEN** | FRESH | 10.437 |

## AI and learning activity

- OpenAI receipts this month: **228**
- OpenAI estimated cost this month: **$11.765421 from receipts**
- Pending forecast candidates: **244**
- Experiment candidates: **547**
- Experiment dispatch requests: **30068**
- Codex-ready remediation tasks: **5**
- Needs-more-evidence items: **2**

## Incidents

Open incident references: **22**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `DAILY_CONFLICT_REVIEW` | 32 | $2.936662 | 0 | 32 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 16 | $2.232892 | 0 | 16 | 1 |
| `SHADOW_COMPASS_V2` | 36 | $2.218034 | 0 | 36 | 0 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 4 | $1.036608 | 0 | 4 | 0 |
| `MONTHLY_LEARNING_ANALYST` | 4 | $1.026470 | 0 | 4 | 0 |
| `FMOS_AUTONOMOUS_MISSION_LOOP_AUDIT` | 3 | $0.718824 | 0 | 3 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 64 | $0.646586 | 0 | 64 | 63 |
| `TEMP_SOL_PR_REVIEW` | 6 | $0.427192 | 0 | 6 | 2 |
| `DECISION_MISS_AUDIT` | 16 | $0.199267 | 0 | 10 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 16 | $0.106595 | 0 | 0 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 2 | $0.064436 | 0 | 2 | 0 |
| `UNCLASSIFIED` | 2 | $0.049244 | 0 | 2 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `baa75f922026e40ba199453e1dbacaecf0871172f4dbf4c6a5c28953f85514dd`
