# Operations Dashboard

Overall: **AMBER**
Generated: `2026-11-23T11:17:11.124621Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 2.158 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 8.268 |
| `weekly_output` | **GREEN** | FRESH | 1.531 |
| `automation_health` | **AMBER** | AMBER | 0.086 |
| `architecture_health` | **GREEN** | GREEN | 0.02 |
| `experiment_lifecycle` | **GREEN** | FRESH | 0.261 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 0.391 |
| `remediation_maturation` | **GREEN** | FRESH | 13.187 |

## Source coverage (advisory, not producer/consumer acceptance)

| Lane | Cadence | Source state | Schedule observation | Source age (h) | Consumer |
|---|---|---|---|---:|---|
| hourly | HOURLY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_NOT_SUCCESS | 0.286 | UNKNOWN |
| daily_live_anchor | SIX_PER_LOCAL_DAY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 2.158 | UNKNOWN |
| settled_etf | SETTLED_SESSION_DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 20.038 | UNKNOWN |
| stablecoin_liquidity | DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 20.544 | UNKNOWN |
| market_breadth | CHECKPOINT | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 2.058 | UNKNOWN |
| btc_dominance | DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 20.416 | UNKNOWN |
| news_intelligence | DAILY_DISCOVERY | MISSING_OR_DEGRADED (NEWS_DISCOVERY_NOT_VERIFIED) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 19.977 | UNKNOWN |
| entry_signals | EVENT_AND_HOURLY_FALLBACK | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 0.883 | UNKNOWN |
| edge_research | PROSPECTIVE_EVENT_DRIVEN | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | NATIVE_SCHEDULE_UNVERIFIED | 0.261 | UNKNOWN |

A successful schedule does not prove a complete source, verified news, point-in-time first-known, consumer readback or financial edge.

## AI and learning activity

- OpenAI receipts this month: **270**
- OpenAI estimated cost this month: **$13.763828 from receipts**
- Pending forecast candidates: **319**
- Experiment candidates: **829**
- Experiment dispatch requests: **11**
- Codex-ready remediation tasks: **7**
- Needs-more-evidence items: **7**

## Incidents

Open incident references: **24**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `RESEARCH_LAB_SOL_ANALYSIS` | 16 | $4.139881 | 0 | 16 | 0 |
| `SHADOW_COMPASS_V2` | 48 | $2.923336 | 0 | 48 | 0 |
| `DAILY_CONFLICT_REVIEW` | 25 | $2.906588 | 0 | 25 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 90 | $0.960101 | 0 | 90 | 66 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 2 | $0.878252 | 0 | 2 | 1 |
| `MONTHLY_LEARNING_ANALYST` | 3 | $0.870176 | 0 | 3 | 0 |
| `DECISION_MISS_AUDIT` | 23 | $0.364325 | 0 | 23 | 0 |
| `CN_INTERNAL_LONG_HORIZON_SCORER` | 5 | $0.183328 | 0 | 5 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 23 | $0.155658 | 0 | 0 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 3 | $0.146838 | 0 | 3 | 0 |
| `UNCLASSIFIED` | 4 | $0.103642 | 0 | 4 | 0 |
| `EVIDENCE_GAP_AUDIT` | 23 | $0.074127 | 0 | 0 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `d9713a17ea5e3f3d868cdd64213fa5cc564e2a9756d3a2caac60583dcf80e366`
