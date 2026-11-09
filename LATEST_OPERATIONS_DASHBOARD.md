# Operations Dashboard

Overall: **AMBER**
Generated: `2026-11-09T13:42:40.502591Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 5.719 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 11.826 |
| `weekly_output` | **GREEN** | FRESH | 5.046 |
| `automation_health` | **AMBER** | AMBER | 0.573 |
| `architecture_health` | **GREEN** | GREEN | 0.516 |
| `experiment_lifecycle` | **GREEN** | FRESH | 3.746 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 3.795 |
| `remediation_maturation` | **GREEN** | FRESH | 0.289 |

## Source coverage (advisory, not producer/consumer acceptance)

| Lane | Cadence | Source state | Schedule observation | Source age (h) | Consumer |
|---|---|---|---|---:|---|
| hourly | HOURLY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 1.711 | UNKNOWN |
| daily_live_anchor | SIX_PER_LOCAL_DAY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 5.719 | UNKNOWN |
| settled_etf | SETTLED_SESSION_DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 23.437 | UNKNOWN |
| stablecoin_liquidity | DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 24.049 | UNKNOWN |
| market_breadth | CHECKPOINT | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 5.6 | UNKNOWN |
| btc_dominance | DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 23.854 | UNKNOWN |
| news_intelligence | DAILY_DISCOVERY | MISSING_OR_DEGRADED (NEWS_DISCOVERY_NOT_VERIFIED) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 23.406 | UNKNOWN |
| entry_signals | EVENT_AND_HOURLY_FALLBACK | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 1.447 | UNKNOWN |
| edge_research | PROSPECTIVE_EVENT_DRIVEN | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | NATIVE_SCHEDULE_UNVERIFIED | 3.746 | UNKNOWN |

A successful schedule does not prove a complete source, verified news, point-in-time first-known, consumer readback or financial edge.

## AI and learning activity

- OpenAI receipts this month: **126**
- OpenAI estimated cost this month: **$9.701894 from receipts**
- Pending forecast candidates: **291**
- Experiment candidates: **720**
- Experiment dispatch requests: **55972**
- Codex-ready remediation tasks: **6**
- Needs-more-evidence items: **19**

## Incidents

Open incident references: **23**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `RESEARCH_LAB_SOL_ANALYSIS` | 12 | $3.154796 | 0 | 12 | 0 |
| `DAILY_CONFLICT_REVIEW` | 25 | $2.906588 | 0 | 25 | 0 |
| `SHADOW_COMPASS_V2` | 16 | $1.015974 | 0 | 16 | 0 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 2 | $0.878252 | 0 | 2 | 1 |
| `MONTHLY_LEARNING_ANALYST` | 3 | $0.870176 | 0 | 3 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 33 | $0.404359 | 0 | 33 | 33 |
| `DECISION_MISS_AUDIT` | 9 | $0.135309 | 0 | 9 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 2 | $0.097580 | 0 | 2 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 9 | $0.060639 | 0 | 0 | 0 |
| `UNCLASSIFIED` | 2 | $0.055710 | 0 | 2 | 0 |
| `CN_INTERNAL_LONG_HORIZON_SCORER` | 2 | $0.048362 | 0 | 2 | 0 |
| `EVIDENCE_GAP_AUDIT` | 9 | $0.029637 | 0 | 0 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `cb6fc292637d65125940d386693eda4406f8e0019422e5efb8b5fbce5fe4f3ab`
