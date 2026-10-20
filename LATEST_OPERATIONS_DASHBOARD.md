# Operations Dashboard

Overall: **AMBER**
Generated: `2026-10-20T22:32:12.988966Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 2.545 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 4.412 |
| `weekly_output` | **GREEN** | FRESH | 41.28 |
| `automation_health` | **AMBER** | AMBER | 0.069 |
| `architecture_health` | **AMBER** | AMBER | 0.022 |
| `experiment_lifecycle` | **GREEN** | FRESH | 3.653 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 3.687 |
| `remediation_maturation` | **GREEN** | FRESH | 2.965 |

## AI and learning activity

- OpenAI receipts this month: **270**
- OpenAI estimated cost this month: **$12.918457 from receipts**
- Pending forecast candidates: **251**
- Experiment candidates: **575**
- Experiment dispatch requests: **34144**
- Codex-ready remediation tasks: **6**
- Needs-more-evidence items: **1**

## Incidents

Open incident references: **22**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `DAILY_CONFLICT_REVIEW` | 32 | $2.936662 | 0 | 32 | 0 |
| `SHADOW_COMPASS_V2` | 45 | $2.772704 | 0 | 45 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 18 | $2.476158 | 0 | 18 | 1 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 4 | $1.036608 | 0 | 4 | 0 |
| `MONTHLY_LEARNING_ANALYST` | 4 | $1.026470 | 0 | 4 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 80 | $0.821774 | 0 | 80 | 79 |
| `FMOS_AUTONOMOUS_MISSION_LOOP_AUDIT` | 3 | $0.718824 | 0 | 3 | 0 |
| `TEMP_SOL_PR_REVIEW` | 6 | $0.427192 | 0 | 6 | 2 |
| `DECISION_MISS_AUDIT` | 20 | $0.252288 | 0 | 14 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 20 | $0.133194 | 0 | 0 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 3 | $0.101492 | 0 | 3 | 0 |
| `UNCLASSIFIED` | 3 | $0.073760 | 0 | 3 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `architecture_health` - ['OWNER_TOPOLOGY_LEGACY_UNBOUND']
- **P1** `automation_health` - SEMANTIC_STATUS_AMBER
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `efcc90e5295ae357a4d3dedfb296324e93e12810aec419a98662ab546b5408c1`
