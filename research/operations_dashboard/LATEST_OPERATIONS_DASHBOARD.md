# Operations Dashboard

Overall: **RED**
Generated: `2026-11-15T21:11:17.492343Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 1.816 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 1.225 |
| `weekly_output` | **GREEN** | FRESH | 156.523 |
| `automation_health` | **RED** | RED | 0.053 |
| `architecture_health` | **GREEN** | GREEN | 0.015 |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.225 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 11.603 |
| `remediation_maturation` | **GREEN** | FRESH | 8.858 |

## Source coverage (advisory, not producer/consumer acceptance)

| Lane | Cadence | Source state | Schedule observation | Source age (h) | Consumer |
|---|---|---|---|---:|---|
| hourly | HOURLY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_NOT_SUCCESS | 0.188 | UNKNOWN |
| daily_live_anchor | SIX_PER_LOCAL_DAY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 1.816 | UNKNOWN |
| settled_etf | SETTLED_SESSION_DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 6.472 | UNKNOWN |
| stablecoin_liquidity | DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 7.054 | UNKNOWN |
| market_breadth | CHECKPOINT | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 4.732 | UNKNOWN |
| btc_dominance | DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 6.918 | UNKNOWN |
| news_intelligence | DAILY_DISCOVERY | MISSING_OR_DEGRADED (NEWS_DISCOVERY_NOT_VERIFIED) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 6.422 | UNKNOWN |
| entry_signals | EVENT_AND_HOURLY_FALLBACK | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 0.893 | UNKNOWN |
| edge_research | PROSPECTIVE_EVENT_DRIVEN | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | NATIVE_SCHEDULE_UNVERIFIED | 1.225 | UNKNOWN |

A successful schedule does not prove a complete source, verified news, point-in-time first-known, consumer readback or financial edge.

## AI and learning activity

- OpenAI receipts this month: **188**
- OpenAI estimated cost this month: **$11.039584 from receipts**
- Pending forecast candidates: **303**
- Experiment candidates: **772**
- Experiment dispatch requests: **4**
- Codex-ready remediation tasks: **4**
- Needs-more-evidence items: **14**

## Incidents

Open incident references: **37**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `RESEARCH_LAB_SOL_ANALYSIS` | 12 | $3.154796 | 0 | 12 | 0 |
| `DAILY_CONFLICT_REVIEW` | 25 | $2.906588 | 0 | 25 | 0 |
| `SHADOW_COMPASS_V2` | 30 | $1.855004 | 0 | 30 | 0 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 2 | $0.878252 | 0 | 2 | 1 |
| `MONTHLY_LEARNING_ANALYST` | 3 | $0.870176 | 0 | 3 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 61 | $0.746997 | 0 | 61 | 61 |
| `DECISION_MISS_AUDIT` | 15 | $0.230634 | 0 | 15 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 15 | $0.101612 | 0 | 0 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 2 | $0.097580 | 0 | 2 | 0 |
| `UNCLASSIFIED` | 2 | $0.055710 | 0 | 2 | 0 |
| `EVIDENCE_GAP_AUDIT` | 15 | $0.048681 | 0 | 0 | 0 |
| `CN_INTERNAL_LONG_HORIZON_SCORER` | 2 | $0.048362 | 0 | 2 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P0** `automation_health` - ['cycle-navigator-internal-precision.yml:LATEST_RUN_FAILED']
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `fbb721c3a1a75b5f39ccafa83be4ae5f257f7b0f8a7b288509bd6e275e7c3a00`
