# Operations Dashboard

Overall: **RED**
Generated: `2026-11-22T13:09:53.133377Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 5.154 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 10.596 |
| `weekly_output` | **GREEN** | FRESH | 148.585 |
| `automation_health` | **RED** | RED | 0.424 |
| `architecture_health` | **GREEN** | GREEN | 0.388 |
| `experiment_lifecycle` | **GREEN** | FRESH | 3.164 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 3.274 |
| `remediation_maturation` | **GREEN** | FRESH | 0.243 |

## Source coverage (advisory, not producer/consumer acceptance)

| Lane | Cadence | Source state | Schedule observation | Source age (h) | Consumer |
|---|---|---|---|---:|---|
| hourly | HOURLY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_NOT_SUCCESS | 1.165 | UNKNOWN |
| daily_live_anchor | SIX_PER_LOCAL_DAY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 5.154 | UNKNOWN |
| settled_etf | SETTLED_SESSION_DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 21.863 | UNKNOWN |
| stablecoin_liquidity | DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 22.361 | UNKNOWN |
| market_breadth | CHECKPOINT | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 1.694 | UNKNOWN |
| btc_dominance | DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 22.249 | UNKNOWN |
| news_intelligence | DAILY_DISCOVERY | MISSING_OR_DEGRADED (NEWS_DISCOVERY_NOT_VERIFIED) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 21.773 | UNKNOWN |
| entry_signals | EVENT_AND_HOURLY_FALLBACK | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 0.812 | UNKNOWN |
| edge_research | PROSPECTIVE_EVENT_DRIVEN | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | NATIVE_SCHEDULE_UNVERIFIED | 3.164 | UNKNOWN |

A successful schedule does not prove a complete source, verified news, point-in-time first-known, consumer readback or financial edge.

## AI and learning activity

- OpenAI receipts this month: **259**
- OpenAI estimated cost this month: **$13.511356 from receipts**
- Pending forecast candidates: **317**
- Experiment candidates: **821**
- Experiment dispatch requests: **8**
- Codex-ready remediation tasks: **18**
- Needs-more-evidence items: **11**

## Incidents

Open incident references: **24**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `RESEARCH_LAB_SOL_ANALYSIS` | 16 | $4.139881 | 0 | 16 | 0 |
| `DAILY_CONFLICT_REVIEW` | 25 | $2.906588 | 0 | 25 | 0 |
| `SHADOW_COMPASS_V2` | 46 | $2.802504 | 0 | 46 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 86 | $0.934259 | 0 | 86 | 66 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 2 | $0.878252 | 0 | 2 | 1 |
| `MONTHLY_LEARNING_ANALYST` | 3 | $0.870176 | 0 | 3 | 0 |
| `DECISION_MISS_AUDIT` | 22 | $0.347425 | 0 | 22 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 22 | $0.149018 | 0 | 0 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 3 | $0.146838 | 0 | 3 | 0 |
| `CN_INTERNAL_LONG_HORIZON_SCORER` | 4 | $0.126708 | 0 | 4 | 0 |
| `UNCLASSIFIED` | 3 | $0.081110 | 0 | 3 | 0 |
| `EVIDENCE_GAP_AUDIT` | 22 | $0.071020 | 0 | 0 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P0** `automation_health` - ['cycle-navigator-pages.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `1a99d95cc01b98339d0b95d222fb788da9375528a68d2e12cb13b062b71baf62`
