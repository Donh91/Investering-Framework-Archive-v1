# Operations Dashboard

Overall: **RED**
Generated: `2026-11-11T22:58:15.195930Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 2.785 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 1.411 |
| `weekly_output` | **GREEN** | FRESH | 62.305 |
| `automation_health` | **RED** | RED | 0.077 |
| `architecture_health` | **GREEN** | GREEN | 0.027 |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.411 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 12.914 |
| `remediation_maturation` | **GREEN** | FRESH | 10.735 |

## Source coverage (advisory, not producer/consumer acceptance)

| Lane | Cadence | Source state | Schedule observation | Source age (h) | Consumer |
|---|---|---|---|---:|---|
| hourly | HOURLY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_NOT_SUCCESS | 0.971 | UNKNOWN |
| daily_live_anchor | SIX_PER_LOCAL_DAY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 2.785 | UNKNOWN |
| settled_etf | SETTLED_SESSION_DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 7.856 | UNKNOWN |
| stablecoin_liquidity | DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 8.402 | UNKNOWN |
| market_breadth | CHECKPOINT | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 4.255 | UNKNOWN |
| btc_dominance | DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 8.28 | UNKNOWN |
| news_intelligence | DAILY_DISCOVERY | MISSING_OR_DEGRADED (NEWS_DISCOVERY_NOT_VERIFIED) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 7.752 | UNKNOWN |
| entry_signals | EVENT_AND_HOURLY_FALLBACK | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 0.562 | UNKNOWN |
| edge_research | PROSPECTIVE_EVENT_DRIVEN | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | NATIVE_SCHEDULE_UNVERIFIED | 1.411 | UNKNOWN |

A successful schedule does not prove a complete source, verified news, point-in-time first-known, consumer readback or financial edge.

## AI and learning activity

- OpenAI receipts this month: **150**
- OpenAI estimated cost this month: **$10.181917 from receipts**
- Pending forecast candidates: **295**
- Experiment candidates: **738**
- Experiment dispatch requests: **59412**
- Codex-ready remediation tasks: **9**
- Needs-more-evidence items: **6**

## Incidents

Open incident references: **28**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `RESEARCH_LAB_SOL_ANALYSIS` | 12 | $3.154796 | 0 | 12 | 0 |
| `DAILY_CONFLICT_REVIEW` | 25 | $2.906588 | 0 | 25 | 0 |
| `SHADOW_COMPASS_V2` | 21 | $1.310130 | 0 | 21 | 0 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 2 | $0.878252 | 0 | 2 | 1 |
| `MONTHLY_LEARNING_ANALYST` | 3 | $0.870176 | 0 | 3 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 44 | $0.537968 | 0 | 44 | 44 |
| `DECISION_MISS_AUDIT` | 11 | $0.166737 | 0 | 11 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 2 | $0.097580 | 0 | 2 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 11 | $0.074302 | 0 | 0 | 0 |
| `UNCLASSIFIED` | 2 | $0.055710 | 0 | 2 | 0 |
| `CN_INTERNAL_LONG_HORIZON_SCORER` | 2 | $0.048362 | 0 | 2 | 0 |
| `EVIDENCE_GAP_AUDIT` | 11 | $0.036124 | 0 | 0 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P0** `automation_health` - ['cycle-navigator-internal-precision.yml:LATEST_RUN_FAILED']
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `4577f9731e747aecc203036af897bb533e77605b5d474860010681c615a9c9b8`
