# Operations Dashboard

Overall: **RED**
Generated: `2026-11-24T15:38:53.189697Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 4.709 |
| `openai_daily_director` | **AMBER** | DELAYED | 13.738 |
| `weekly_output` | **GREEN** | FRESH | 29.893 |
| `automation_health` | **RED** | RED | 0.605 |
| `architecture_health` | **GREEN** | GREEN | 0.535 |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.901 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 3.037 |
| `remediation_maturation` | **GREEN** | FRESH | 12.586 |

## Source coverage (advisory, not producer/consumer acceptance)

| Lane | Cadence | Source state | Schedule observation | Source age (h) | Consumer |
|---|---|---|---|---:|---|
| hourly | HOURLY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 0.648 | UNKNOWN |
| daily_live_anchor | SIX_PER_LOCAL_DAY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 4.709 | UNKNOWN |
| settled_etf | SETTLED_SESSION_DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 20.443 | UNKNOWN |
| stablecoin_liquidity | DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 21.145 | UNKNOWN |
| market_breadth | CHECKPOINT | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 4.54 | UNKNOWN |
| btc_dominance | DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 20.936 | UNKNOWN |
| news_intelligence | DAILY_DISCOVERY | MISSING_OR_DEGRADED (NEWS_DISCOVERY_NOT_VERIFIED) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 20.381 | UNKNOWN |
| entry_signals | EVENT_AND_HOURLY_FALLBACK | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 0.277 | UNKNOWN |
| edge_research | PROSPECTIVE_EVENT_DRIVEN | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | NATIVE_SCHEDULE_UNVERIFIED | 2.901 | UNKNOWN |

A successful schedule does not prove a complete source, verified news, point-in-time first-known, consumer readback or financial edge.

## AI and learning activity

- OpenAI receipts this month: **281**
- OpenAI estimated cost this month: **$14.014762 from receipts**
- Pending forecast candidates: **319**
- Experiment candidates: **834**
- Experiment dispatch requests: **3**
- Codex-ready remediation tasks: **13**
- Needs-more-evidence items: **10**

## Incidents

Open incident references: **25**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `RESEARCH_LAB_SOL_ANALYSIS` | 16 | $4.139881 | 0 | 16 | 0 |
| `SHADOW_COMPASS_V2` | 50 | $3.042970 | 0 | 50 | 0 |
| `DAILY_CONFLICT_REVIEW` | 25 | $2.906588 | 0 | 25 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 93 | $0.979363 | 0 | 93 | 66 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 2 | $0.878252 | 0 | 2 | 1 |
| `MONTHLY_LEARNING_ANALYST` | 3 | $0.870176 | 0 | 3 | 0 |
| `DECISION_MISS_AUDIT` | 24 | $0.381781 | 0 | 24 | 0 |
| `CN_INTERNAL_LONG_HORIZON_SCORER` | 6 | $0.206606 | 0 | 6 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 4 | $0.193778 | 0 | 4 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 24 | $0.162333 | 0 | 0 | 0 |
| `UNCLASSIFIED` | 4 | $0.103642 | 0 | 4 | 0 |
| `EVIDENCE_GAP_AUDIT` | 24 | $0.077233 | 0 | 0 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P0** `automation_health` - ['cycle-navigator-pages.yml:REPEATED_CONSECUTIVE_FAILURES', 'daily-director-shadow.yml:LATEST_RUN_FAILED']
- **P1** `openai_daily_director` - DELAYED

Dashboard SHA-256: `4c04d59460992382bc363bd40e80435fc135f635d2b4ab66f80ea58d93da4c84`
