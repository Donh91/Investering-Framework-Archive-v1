# Operations Dashboard

Overall: **AMBER**
Generated: `2026-11-20T22:47:56.785022Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 1.735 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 0.827 |
| `weekly_output` | **GREEN** | FRESH | 110.22 |
| `automation_health` | **AMBER** | AMBER | 0.067 |
| `architecture_health` | **GREEN** | GREEN | 0.018 |
| `experiment_lifecycle` | **GREEN** | FRESH | 0.826 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 12.661 |
| `remediation_maturation` | **GREEN** | FRESH | 5.237 |

## Source coverage (advisory, not producer/consumer acceptance)

| Lane | Cadence | Source state | Schedule observation | Source age (h) | Consumer |
|---|---|---|---|---:|---|
| hourly | HOURLY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_NOT_SUCCESS | 0.799 | UNKNOWN |
| daily_live_anchor | SIX_PER_LOCAL_DAY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 1.735 | UNKNOWN |
| settled_etf | SETTLED_SESSION_DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 6.711 | UNKNOWN |
| stablecoin_liquidity | DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 7.165 | UNKNOWN |
| market_breadth | CHECKPOINT | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 4.904 | UNKNOWN |
| btc_dominance | DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 7.065 | UNKNOWN |
| news_intelligence | DAILY_DISCOVERY | MISSING_OR_DEGRADED (NEWS_DISCOVERY_NOT_VERIFIED) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 6.632 | UNKNOWN |
| entry_signals | EVENT_AND_HOURLY_FALLBACK | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 0.397 | UNKNOWN |
| edge_research | PROSPECTIVE_EVENT_DRIVEN | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | NATIVE_SCHEDULE_UNVERIFIED | 0.826 | UNKNOWN |

A successful schedule does not prove a complete source, verified news, point-in-time first-known, consumer readback or financial edge.

## AI and learning activity

- OpenAI receipts this month: **244**
- OpenAI estimated cost this month: **$13.240517 from receipts**
- Pending forecast candidates: **313**
- Experiment candidates: **811**
- Experiment dispatch requests: **5**
- Codex-ready remediation tasks: **21**
- Needs-more-evidence items: **11**

## Incidents

Open incident references: **23**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `RESEARCH_LAB_SOL_ANALYSIS` | 16 | $4.139881 | 0 | 16 | 0 |
| `DAILY_CONFLICT_REVIEW` | 25 | $2.906588 | 0 | 25 | 0 |
| `SHADOW_COMPASS_V2` | 43 | $2.629416 | 0 | 43 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 81 | $0.902310 | 0 | 81 | 66 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 2 | $0.878252 | 0 | 2 | 1 |
| `MONTHLY_LEARNING_ANALYST` | 3 | $0.870176 | 0 | 3 | 0 |
| `DECISION_MISS_AUDIT` | 20 | $0.313829 | 0 | 20 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 3 | $0.146838 | 0 | 3 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 20 | $0.135537 | 0 | 0 | 0 |
| `CN_INTERNAL_LONG_HORIZON_SCORER` | 4 | $0.126708 | 0 | 4 | 0 |
| `UNCLASSIFIED` | 3 | $0.081110 | 0 | 3 | 0 |
| `EVIDENCE_GAP_AUDIT` | 20 | $0.064679 | 0 | 0 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `42e4b66ee5b88f3ecb9cd9219ef4bd9601746dd4663bf67060cbfc972bfb3b4f`
