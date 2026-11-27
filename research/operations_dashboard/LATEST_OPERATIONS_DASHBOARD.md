# Operations Dashboard

Overall: **RED**
Generated: `2026-11-27T14:08:42.126401Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 4.446 |
| `openai_daily_director` | **RED** | STALE | 62.493 |
| `weekly_output` | **GREEN** | FRESH | 100.39 |
| `automation_health` | **RED** | RED | 0.068 |
| `architecture_health` | **AMBER** | AMBER | 0.024 |
| `experiment_lifecycle` | **GREEN** | FRESH | 3.034 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 3.161 |
| `remediation_maturation` | **GREEN** | FRESH | 13.195 |

## Source coverage (advisory, not producer/consumer acceptance)

| Lane | Cadence | Source state | Schedule observation | Source age (h) | Consumer |
|---|---|---|---|---:|---|
| hourly | HOURLY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 1.145 | UNKNOWN |
| daily_live_anchor | SIX_PER_LOCAL_DAY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 4.446 | UNKNOWN |
| settled_etf | SETTLED_SESSION_DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 20.445 | UNKNOWN |
| stablecoin_liquidity | DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 21.031 | UNKNOWN |
| market_breadth | CHECKPOINT | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 1.726 | UNKNOWN |
| btc_dominance | DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 20.872 | UNKNOWN |
| news_intelligence | DAILY_DISCOVERY | MISSING_OR_DEGRADED (NEWS_DISCOVERY_NOT_VERIFIED) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 20.406 | UNKNOWN |
| entry_signals | EVENT_AND_HOURLY_FALLBACK | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 0.84 | UNKNOWN |
| edge_research | PROSPECTIVE_EVENT_DRIVEN | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | NATIVE_SCHEDULE_UNVERIFIED | 3.034 | UNKNOWN |

A successful schedule does not prove a complete source, verified news, point-in-time first-known, consumer readback or financial edge.

## AI and learning activity

- OpenAI receipts this month: **286**
- OpenAI estimated cost this month: **$14.147817 from receipts**
- Pending forecast candidates: **319**
- Experiment candidates: **840**
- Experiment dispatch requests: **3**
- Codex-ready remediation tasks: **21**
- Needs-more-evidence items: **8**

## Incidents

Open incident references: **31**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `RESEARCH_LAB_SOL_ANALYSIS` | 16 | $4.139881 | 0 | 16 | 0 |
| `SHADOW_COMPASS_V2` | 52 | $3.156698 | 0 | 52 | 0 |
| `DAILY_CONFLICT_REVIEW` | 25 | $2.906588 | 0 | 25 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 96 | $0.998690 | 0 | 96 | 66 |
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

- **P0** `automation_health` - ['adaptive-evidence-gap.yml:LATEST_RUN_FAILED', 'adaptive-evidence-gap.yml:REPEATED_CONSECUTIVE_FAILURES', 'daily-director-shadow.yml:LATEST_RUN_FAILED', 'daily-director-shadow.yml:REPEATED_CONSECUTIVE_FAILURES', 'daily-director-shadow.yml:SCHEDULE_STALE', 'research-execution-coordinator.yml:LATEST_RUN_FAILED', 'research-execution-coordinator.yml:REPEATED_CONSECUTIVE_FAILURES', 'shadow-compass-v2.yml:LATEST_RUN_FAILED', 'shadow-compass-v2.yml:SCHEDULE_STALE']
- **P0** `openai_daily_director` - STALE
- **P1** `architecture_health` - ['DAILY_DIRECTOR_STALE']

Dashboard SHA-256: `96c11363b8539346ca02cb67906b921b2b9e4a03ce7e5859c3c326af5762f48b`
