# Operations Dashboard

Overall: **RED**
Generated: `2026-11-10T13:24:28.853582Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 4.976 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 9.12 |
| `weekly_output` | **GREEN** | FRESH | 28.742 |
| `automation_health` | **RED** | RED | 0.57 |
| `architecture_health` | **GREEN** | GREEN | 0.522 |
| `experiment_lifecycle` | **GREEN** | FRESH | 3.384 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 3.427 |
| `remediation_maturation` | **GREEN** | FRESH | 0.36 |

## Source coverage (advisory, not producer/consumer acceptance)

| Lane | Cadence | Source state | Schedule observation | Source age (h) | Consumer |
|---|---|---|---|---:|---|
| hourly | HOURLY | DELAYED_SOURCE (BEYOND_OBSERVATIONAL_AGE_WINDOW) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 4.408 | UNKNOWN |
| daily_live_anchor | SIX_PER_LOCAL_DAY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 4.976 | UNKNOWN |
| settled_etf | SETTLED_SESSION_DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 19.981 | UNKNOWN |
| stablecoin_liquidity | DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 20.75 | UNKNOWN |
| market_breadth | CHECKPOINT | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 2.151 | UNKNOWN |
| btc_dominance | DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 20.584 | UNKNOWN |
| news_intelligence | DAILY_DISCOVERY | MISSING_OR_DEGRADED (NEWS_DISCOVERY_NOT_VERIFIED) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 19.902 | UNKNOWN |
| entry_signals | EVENT_AND_HOURLY_FALLBACK | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 3.455 | UNKNOWN |
| edge_research | PROSPECTIVE_EVENT_DRIVEN | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | NATIVE_SCHEDULE_UNVERIFIED | 3.384 | UNKNOWN |

A successful schedule does not prove a complete source, verified news, point-in-time first-known, consumer readback or financial edge.

## AI and learning activity

- OpenAI receipts this month: **137**
- OpenAI estimated cost this month: **$9.895638 from receipts**
- Pending forecast candidates: **293**
- Experiment candidates: **726**
- Experiment dispatch requests: **57220**
- Codex-ready remediation tasks: **8**
- Needs-more-evidence items: **18**

## Incidents

Open incident references: **25**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `RESEARCH_LAB_SOL_ANALYSIS` | 12 | $3.154796 | 0 | 12 | 0 |
| `DAILY_CONFLICT_REVIEW` | 25 | $2.906588 | 0 | 25 | 0 |
| `SHADOW_COMPASS_V2` | 18 | $1.134738 | 0 | 18 | 0 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 2 | $0.878252 | 0 | 2 | 1 |
| `MONTHLY_LEARNING_ANALYST` | 3 | $0.870176 | 0 | 3 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 37 | $0.453027 | 0 | 37 | 37 |
| `DECISION_MISS_AUDIT` | 10 | $0.150960 | 0 | 10 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 2 | $0.097580 | 0 | 2 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 10 | $0.067445 | 0 | 0 | 0 |
| `UNCLASSIFIED` | 2 | $0.055710 | 0 | 2 | 0 |
| `CN_INTERNAL_LONG_HORIZON_SCORER` | 2 | $0.048362 | 0 | 2 | 0 |
| `EVIDENCE_GAP_AUDIT` | 10 | $0.032812 | 0 | 0 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P0** `automation_health` - ['cycle-navigator-internal-precision.yml:LATEST_RUN_FAILED']
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `7c8ac84177319850b67275b601fb23603ef462cbab05feea6843c36f65fe53fa`
