# Operations Dashboard

Overall: **RED**
Generated: `2026-10-30T21:23:19.734010Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 2.792 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 1.676 |
| `weekly_output` | **GREEN** | FRESH | 110.466 |
| `automation_health` | **RED** | RED | 0.44 |
| `architecture_health` | **GREEN** | GREEN | 0.403 |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.675 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 12.643 |
| `remediation_maturation` | **GREEN** | FRESH | 0.349 |

## AI and learning activity

- OpenAI receipts this month: **368**
- OpenAI estimated cost this month: **$15.214814 from receipts**
- Pending forecast candidates: **271**
- Experiment candidates: **650**
- Experiment dispatch requests: **44966**
- Codex-ready remediation tasks: **3**
- Needs-more-evidence items: **4**

## Incidents

Open incident references: **25**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `SHADOW_COMPASS_V2` | 65 | $4.017304 | 0 | 65 | 0 |
| `DAILY_CONFLICT_REVIEW` | 32 | $2.936662 | 0 | 32 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 18 | $2.476158 | 0 | 18 | 1 |
| `DAILY_DIRECTOR_SHADOW` | 120 | $1.292139 | 0 | 120 | 119 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 4 | $1.036608 | 0 | 4 | 0 |
| `MONTHLY_LEARNING_ANALYST` | 4 | $1.026470 | 0 | 4 | 0 |
| `FMOS_AUTONOMOUS_MISSION_LOOP_AUDIT` | 3 | $0.718824 | 0 | 3 | 0 |
| `TEMP_SOL_PR_REVIEW` | 8 | $0.674266 | 0 | 8 | 4 |
| `DECISION_MISS_AUDIT` | 30 | $0.392313 | 0 | 24 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 30 | $0.200276 | 0 | 0 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 4 | $0.145990 | 0 | 4 | 0 |
| `UNCLASSIFIED` | 4 | $0.094826 | 0 | 4 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P0** `automation_health` - ['framework-learning-supervisor.yml:LATEST_RUN_FAILED']
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `954406c54d015a1448be00bef5aef4e345911fc01c1ea4e2bab3ec481965a64a`
