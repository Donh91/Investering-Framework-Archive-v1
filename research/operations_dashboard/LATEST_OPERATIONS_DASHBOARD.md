# Operations Dashboard

Overall: **AMBER**
Generated: `2026-11-21T21:49:39.397864Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 0.206 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 1.152 |
| `weekly_output` | **GREEN** | FRESH | 133.248 |
| `automation_health` | **AMBER** | AMBER | 0.061 |
| `architecture_health` | **GREEN** | GREEN | 0.017 |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.152 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 11.893 |
| `remediation_maturation` | **GREEN** | FRESH | 8.748 |

## Source coverage (advisory, not producer/consumer acceptance)

| Lane | Cadence | Source state | Schedule observation | Source age (h) | Consumer |
|---|---|---|---|---:|---|
| hourly | HOURLY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_NOT_SUCCESS | 0.828 | UNKNOWN |
| daily_live_anchor | SIX_PER_LOCAL_DAY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 0.206 | UNKNOWN |
| settled_etf | SETTLED_SESSION_DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 6.526 | UNKNOWN |
| stablecoin_liquidity | DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 7.024 | UNKNOWN |
| market_breadth | CHECKPOINT | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 1.596 | UNKNOWN |
| btc_dominance | DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 6.912 | UNKNOWN |
| news_intelligence | DAILY_DISCOVERY | MISSING_OR_DEGRADED (NEWS_DISCOVERY_NOT_VERIFIED) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 6.436 | UNKNOWN |
| entry_signals | EVENT_AND_HOURLY_FALLBACK | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 0.375 | UNKNOWN |
| edge_research | PROSPECTIVE_EVENT_DRIVEN | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | NATIVE_SCHEDULE_UNVERIFIED | 1.152 | UNKNOWN |

A successful schedule does not prove a complete source, verified news, point-in-time first-known, consumer readback or financial edge.

## AI and learning activity

- OpenAI receipts this month: **253**
- OpenAI estimated cost this month: **$13.408857 from receipts**
- Pending forecast candidates: **315**
- Experiment candidates: **819**
- Experiment dispatch requests: **5**
- Codex-ready remediation tasks: **17**
- Needs-more-evidence items: **12**

## Incidents

Open incident references: **23**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `RESEARCH_LAB_SOL_ANALYSIS` | 16 | $4.139881 | 0 | 16 | 0 |
| `DAILY_CONFLICT_REVIEW` | 25 | $2.906588 | 0 | 25 | 0 |
| `SHADOW_COMPASS_V2` | 45 | $2.745530 | 0 | 45 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 85 | $0.927879 | 0 | 85 | 66 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 2 | $0.878252 | 0 | 2 | 1 |
| `MONTHLY_LEARNING_ANALYST` | 3 | $0.870176 | 0 | 3 | 0 |
| `DECISION_MISS_AUDIT` | 21 | $0.330586 | 0 | 21 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 3 | $0.146838 | 0 | 3 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 21 | $0.142277 | 0 | 0 | 0 |
| `CN_INTERNAL_LONG_HORIZON_SCORER` | 4 | $0.126708 | 0 | 4 | 0 |
| `UNCLASSIFIED` | 3 | $0.081110 | 0 | 3 | 0 |
| `EVIDENCE_GAP_AUDIT` | 21 | $0.067839 | 0 | 0 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `9127eec63e939804231342aa641777a7121723c5220734227d01ac526d77730e`
