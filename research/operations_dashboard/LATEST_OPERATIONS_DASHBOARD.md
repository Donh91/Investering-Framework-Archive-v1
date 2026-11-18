# Operations Dashboard

Overall: **AMBER**
Generated: `2026-11-17T23:48:14.416452Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 2.044 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 1.144 |
| `weekly_output` | **GREEN** | FRESH | 39.225 |
| `automation_health` | **AMBER** | AMBER | 0.201 |
| `architecture_health` | **GREEN** | GREEN | 0.121 |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.144 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 11.92 |
| `remediation_maturation` | **GREEN** | FRESH | 0.092 |

## Source coverage (advisory, not producer/consumer acceptance)

| Lane | Cadence | Source state | Schedule observation | Source age (h) | Consumer |
|---|---|---|---|---:|---|
| hourly | HOURLY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_NOT_SUCCESS | 0.804 | UNKNOWN |
| daily_live_anchor | SIX_PER_LOCAL_DAY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 2.044 | UNKNOWN |
| settled_etf | SETTLED_SESSION_DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 6.937 | UNKNOWN |
| stablecoin_liquidity | DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 7.537 | UNKNOWN |
| market_breadth | CHECKPOINT | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 0.905 | UNKNOWN |
| btc_dominance | DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 7.364 | UNKNOWN |
| news_intelligence | DAILY_DISCOVERY | MISSING_OR_DEGRADED (NEWS_DISCOVERY_NOT_VERIFIED) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 6.908 | UNKNOWN |
| entry_signals | EVENT_AND_HOURLY_FALLBACK | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 0.464 | UNKNOWN |
| edge_research | PROSPECTIVE_EVENT_DRIVEN | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | NATIVE_SCHEDULE_UNVERIFIED | 1.144 | UNKNOWN |

A successful schedule does not prove a complete source, verified news, point-in-time first-known, consumer readback or financial edge.

## AI and learning activity

- OpenAI receipts this month: **210**
- OpenAI estimated cost this month: **$11.573632 from receipts**
- Pending forecast candidates: **307**
- Experiment candidates: **788**
- Experiment dispatch requests: **10**
- Codex-ready remediation tasks: **7**
- Needs-more-evidence items: **6**

## Incidents

Open incident references: **24**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `RESEARCH_LAB_SOL_ANALYSIS` | 12 | $3.154796 | 0 | 12 | 0 |
| `DAILY_CONFLICT_REVIEW` | 25 | $2.906588 | 0 | 25 | 0 |
| `SHADOW_COMPASS_V2` | 34 | $2.103338 | 0 | 34 | 0 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 2 | $0.878252 | 0 | 2 | 1 |
| `MONTHLY_LEARNING_ANALYST` | 3 | $0.870176 | 0 | 3 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 69 | $0.826788 | 0 | 69 | 66 |
| `DECISION_MISS_AUDIT` | 17 | $0.263483 | 0 | 17 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 3 | $0.146838 | 0 | 3 | 0 |
| `CN_INTERNAL_LONG_HORIZON_SCORER` | 4 | $0.126708 | 0 | 4 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 17 | $0.115225 | 0 | 0 | 0 |
| `UNCLASSIFIED` | 3 | $0.081110 | 0 | 3 | 0 |
| `EVIDENCE_GAP_AUDIT` | 17 | $0.055137 | 0 | 0 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `3ff7337a0f0d40f484404b868c839d76af01d699d1a4423dda54788a9a2a3a89`
