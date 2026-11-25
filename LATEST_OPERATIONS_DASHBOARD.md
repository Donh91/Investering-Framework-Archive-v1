# Operations Dashboard

Overall: **RED**
Generated: `2026-11-25T01:02:11.798340Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 2.017 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 1.385 |
| `weekly_output` | **GREEN** | FRESH | 39.281 |
| `automation_health` | **RED** | RED | 0.079 |
| `architecture_health` | **GREEN** | GREEN | 0.026 |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.384 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 12.425 |
| `remediation_maturation` | **AMBER** | DELAYED | 21.974 |

## Source coverage (advisory, not producer/consumer acceptance)

| Lane | Cadence | Source state | Schedule observation | Source age (h) | Consumer |
|---|---|---|---|---:|---|
| hourly | HOURLY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 1.037 | UNKNOWN |
| daily_live_anchor | SIX_PER_LOCAL_DAY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 2.017 | UNKNOWN |
| settled_etf | SETTLED_SESSION_DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 6.18 | UNKNOWN |
| stablecoin_liquidity | DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 7.067 | UNKNOWN |
| market_breadth | CHECKPOINT | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 1.939 | UNKNOWN |
| btc_dominance | DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 6.786 | UNKNOWN |
| news_intelligence | DAILY_DISCOVERY | MISSING_OR_DEGRADED (NEWS_DISCOVERY_NOT_VERIFIED) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 6.135 | UNKNOWN |
| entry_signals | EVENT_AND_HOURLY_FALLBACK | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 0.757 | UNKNOWN |
| edge_research | PROSPECTIVE_EVENT_DRIVEN | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | NATIVE_SCHEDULE_UNVERIFIED | 1.384 | UNKNOWN |

A successful schedule does not prove a complete source, verified news, point-in-time first-known, consumer readback or financial edge.

## AI and learning activity

- OpenAI receipts this month: **285**
- OpenAI estimated cost this month: **$14.089379 from receipts**
- Pending forecast candidates: **319**
- Experiment candidates: **840**
- Experiment dispatch requests: **3**
- Codex-ready remediation tasks: **13**
- Needs-more-evidence items: **10**

## Incidents

Open incident references: **26**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `RESEARCH_LAB_SOL_ANALYSIS` | 16 | $4.139881 | 0 | 16 | 0 |
| `SHADOW_COMPASS_V2` | 51 | $3.098260 | 0 | 51 | 0 |
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

- **P0** `automation_health` - ['remediation-maturation.yml:LATEST_RUN_FAILED', 'remediation-maturation.yml:SCHEDULE_STALE']
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED
- **P1** `remediation_maturation` - DELAYED

Dashboard SHA-256: `420fd89e48168cd768a9eb3e73eae617b5c3a27fdcdf9de3be32c111b7b061d3`
