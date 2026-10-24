# Operations Dashboard

Overall: **AMBER**
Generated: `2026-10-24T08:21:31.584379Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 3.726 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 8.398 |
| `weekly_output` | **GREEN** | FRESH | 123.102 |
| `automation_health` | **AMBER** | AMBER | 0.062 |
| `architecture_health` | **GREEN** | GREEN | 0.011 |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.303 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.368 |
| `remediation_maturation` | **GREEN** | FRESH | 10.124 |

## AI and learning activity

- OpenAI receipts this month: **306**
- OpenAI estimated cost this month: **$13.784859 from receipts**
- Pending forecast candidates: **259**
- Experiment candidates: **601**
- Experiment dispatch requests: **37607**
- Codex-ready remediation tasks: **6**
- Needs-more-evidence items: **2**

## Incidents

Open incident references: **23**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `SHADOW_COMPASS_V2` | 51 | $3.145460 | 0 | 51 | 0 |
| `DAILY_CONFLICT_REVIEW` | 32 | $2.936662 | 0 | 32 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 18 | $2.476158 | 0 | 18 | 1 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 4 | $1.036608 | 0 | 4 | 0 |
| `MONTHLY_LEARNING_ANALYST` | 4 | $1.026470 | 0 | 4 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 93 | $0.972111 | 0 | 93 | 92 |
| `FMOS_AUTONOMOUS_MISSION_LOOP_AUDIT` | 3 | $0.718824 | 0 | 3 | 0 |
| `TEMP_SOL_PR_REVIEW` | 8 | $0.674266 | 0 | 8 | 4 |
| `DECISION_MISS_AUDIT` | 24 | $0.307146 | 0 | 18 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 24 | $0.159770 | 0 | 0 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 3 | $0.101492 | 0 | 3 | 0 |
| `EVIDENCE_GAP_AUDIT` | 22 | $0.074347 | 0 | 0 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `ab0290c19a4fb557debdeb79bd6044816da03377072b0488056559d58ca11e13`
