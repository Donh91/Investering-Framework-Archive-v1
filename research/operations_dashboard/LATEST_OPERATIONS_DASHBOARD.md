# Operations Dashboard

Overall: **AMBER**
Generated: `2026-11-08T11:47:40.992782Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 4.426 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 10.032 |
| `weekly_output` | **GREEN** | FRESH | 147.544 |
| `automation_health` | **AMBER** | AMBER | 0.378 |
| `architecture_health` | **GREEN** | GREEN | 0.344 |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.632 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.671 |
| `remediation_maturation` | **GREEN** | FRESH | 0.233 |

## Source coverage (advisory, not producer/consumer acceptance)

| Lane | Cadence | Source state | Schedule observation | Source age (h) | Consumer |
|---|---|---|---|---:|---|
| hourly | HOURLY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 2.795 | UNKNOWN |
| daily_live_anchor | SIX_PER_LOCAL_DAY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 4.426 | UNKNOWN |
| settled_etf | SETTLED_SESSION_DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 21.845 | UNKNOWN |
| stablecoin_liquidity | DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 22.474 | UNKNOWN |
| market_breadth | CHECKPOINT | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 4.306 | UNKNOWN |
| btc_dominance | DAILY | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 22.294 | UNKNOWN |
| news_intelligence | DAILY_DISCOVERY | MISSING_OR_DEGRADED (NEWS_DISCOVERY_NOT_VERIFIED) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 21.735 | UNKNOWN |
| entry_signals | EVENT_AND_HOURLY_FALLBACK | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | LAST_SCHEDULE_SUCCESS_NOT_COVERAGE | 1.97 | UNKNOWN |
| edge_research | PROSPECTIVE_EVENT_DRIVEN | OBSERVED_SOURCE (SOURCE_ROW_PRESENT) | NATIVE_SCHEDULE_UNVERIFIED | 2.632 | UNKNOWN |

A successful schedule does not prove a complete source, verified news, point-in-time first-known, consumer readback or financial edge.

## AI and learning activity

- OpenAI receipts this month: **113**
- OpenAI estimated cost this month: **$9.074487 from receipts**
- Pending forecast candidates: **289**
- Experiment candidates: **713**
- Experiment dispatch requests: **54728**
- Codex-ready remediation tasks: **6**
- Needs-more-evidence items: **4**

## Incidents

Open incident references: **23**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `DAILY_CONFLICT_REVIEW` | 25 | $2.906588 | 0 | 25 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 11 | $2.829062 | 0 | 11 | 0 |
| `SHADOW_COMPASS_V2` | 14 | $0.886150 | 0 | 14 | 0 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 2 | $0.878252 | 0 | 2 | 1 |
| `MONTHLY_LEARNING_ANALYST` | 3 | $0.870176 | 0 | 3 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 29 | $0.355610 | 0 | 29 | 29 |
| `DECISION_MISS_AUDIT` | 8 | $0.119724 | 0 | 8 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 8 | $0.053793 | 0 | 0 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 1 | $0.050186 | 0 | 1 | 0 |
| `UNCLASSIFIED` | 1 | $0.030018 | 0 | 1 | 0 |
| `CN_PRECISION_4W_REVIEW` | 1 | $0.028784 | 0 | 1 | 0 |
| `EVIDENCE_GAP_AUDIT` | 8 | $0.026412 | 0 | 0 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `fa871a1173c6d9dabb3acf59e4479565a96e67a7605e12f704657a6ee0a49c9c`
