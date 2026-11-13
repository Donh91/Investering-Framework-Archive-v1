# Operations Dashboard

Overall: **RED**
Generated: `2026-11-13T22:08:07.718337Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 1.65 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 1.129 |
| `weekly_output` | **GREEN** | FRESH | 109.47 |
| `automation_health` | **RED** | RED | 0.066 |
| `architecture_health` | **GREEN** | GREEN | 0.016 |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.129 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 12.445 |
| `remediation_maturation` | **GREEN** | FRESH | 6.037 |

## Source coverage (advisory, not producer/consumer acceptance)

| Lane | Cadence | Source state | Schedule observation | Source age (h) | Consumer |
|---|---|---|---|---:|---|
| hourly | HOURLY | DELAYED_SOURCE (BEYOND_OBSERVATIONAL_AGE_WINDOW) | LAST_SCHEDULE_NOT_SUCCESS | 4.135 | UNKNOWN |
| daily_live_anchor | SIX_PER_LOCAL_DAY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 1.65 | UNKNOWN |
| settled_etf | SETTLED_SESSION_DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 6.802 | UNKNOWN |
| stablecoin_liquidity | DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 7.401 | UNKNOWN |
| market_breadth | CHECKPOINT | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 1.606 | UNKNOWN |
| btc_dominance | DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 7.254 | UNKNOWN |
| news_intelligence | DAILY_DISCOVERY | MISSING_OR_DEGRADED (NEWS_DISCOVERY_NOT_VERIFIED) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 6.727 | UNKNOWN |
| entry_signals | EVENT_AND_HOURLY_FALLBACK | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 3.317 | UNKNOWN |
| edge_research | PROSPECTIVE_EVENT_DRIVEN | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | NATIVE_SCHEDULE_UNVERIFIED | 1.129 | UNKNOWN |

A successful schedule does not prove a complete source, verified news, point-in-time first-known, consumer readback or financial edge.

## AI and learning activity

- OpenAI receipts this month: **168**
- OpenAI estimated cost this month: **$10.570259 from receipts**
- Pending forecast candidates: **299**
- Experiment candidates: **754**
- Experiment dispatch requests: **61948**
- Codex-ready remediation tasks: **14**
- Needs-more-evidence items: **9**

## Incidents

Open incident references: **32**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `RESEARCH_LAB_SOL_ANALYSIS` | 12 | $3.154796 | 0 | 12 | 0 |
| `DAILY_CONFLICT_REVIEW` | 25 | $2.906588 | 0 | 25 | 0 |
| `SHADOW_COMPASS_V2` | 25 | $1.549236 | 0 | 25 | 0 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 2 | $0.878252 | 0 | 2 | 1 |
| `MONTHLY_LEARNING_ANALYST` | 3 | $0.870176 | 0 | 3 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 52 | $0.635506 | 0 | 52 | 52 |
| `DECISION_MISS_AUDIT` | 13 | $0.198556 | 0 | 13 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 2 | $0.097580 | 0 | 2 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 13 | $0.087958 | 0 | 0 | 0 |
| `UNCLASSIFIED` | 2 | $0.055710 | 0 | 2 | 0 |
| `CN_INTERNAL_LONG_HORIZON_SCORER` | 2 | $0.048362 | 0 | 2 | 0 |
| `EVIDENCE_GAP_AUDIT` | 13 | $0.042346 | 0 | 0 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P0** `automation_health` - ['cycle-navigator-internal-precision.yml:LATEST_RUN_FAILED']
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `4e7a07ed10a62da74d8b62abe1cdbc86e2d09b6b990541bd85a347bbafd68c11`
