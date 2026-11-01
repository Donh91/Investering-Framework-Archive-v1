# Operations Dashboard

Overall: **AMBER**
Generated: `2026-11-01T20:43:56.298978Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 2.314 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 1.516 |
| `weekly_output` | **GREEN** | FRESH | 157.809 |
| `automation_health` | **AMBER** | AMBER | 0.06 |
| `architecture_health` | **GREEN** | GREEN | 0.013 |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.511 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 11.355 |
| `remediation_maturation` | **GREEN** | FRESH | 9.191 |

## AI and learning activity

- OpenAI receipts this month: **14**
- OpenAI estimated cost this month: **$1.478448 from receipts**
- Pending forecast candidates: **275**
- Experiment candidates: **666**
- Experiment dispatch requests: **47227**
- Codex-ready remediation tasks: **3**
- Needs-more-evidence items: **6**

## Incidents

Open incident references: **23**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `MONTHLY_LEARNING_ADVERSARIAL` | 1 | $0.587104 | 0 | 1 | 1 |
| `DAILY_CONFLICT_REVIEW` | 4 | $0.463496 | 0 | 4 | 0 |
| `MONTHLY_LEARNING_ANALYST` | 1 | $0.287610 | 0 | 1 | 0 |
| `SHADOW_COMPASS_V2` | 1 | $0.066266 | 0 | 1 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 4 | $0.049177 | 0 | 4 | 4 |
| `DECISION_MISS_AUDIT` | 1 | $0.014743 | 0 | 1 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 1 | $0.006747 | 0 | 0 | 0 |
| `EVIDENCE_GAP_AUDIT` | 1 | $0.003305 | 0 | 0 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `e8683c7f89aff8ee428d7bc77da3b36273bc2dffdb1f36cbb0db447431e1f55c`
