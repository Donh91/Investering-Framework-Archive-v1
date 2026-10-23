# Task 2 + HF | Prioritized FREE pilot selection and scientific acceptance matrix
**Issued:** 2026-10-22. **Status:** RESEARCH_DESIGN; NOT EXECUTED, NOT A QUEUE OWNER, NOT A NEW SCHEDULE OR CODE RELEASE. All proposals go to **existing** Task 2 R0–R7 and Alpha owners. Future execution needs actual eligible source/forecast receipts, security/permissions and no-hindsight prereg.

## Priority table
| Rank | Research pilot | Minimal HF input | Measurable utility | Existing owner | Gate now |
| --- | --- | --- | --- | --- | --- |
| P1-A | Price source QA | `linxy/CryptoCoin` BTCUSDT/ETHUSDT 1h, two small bounded dates, optionally `zongowo111/v2-crypto-ohlcv-data` same-completed-bar crosscheck | timestamps/close boundary, missing/duplicates, venue adjusted gaps vs original *issued* hours; no skill claim | Task 2 R0/R1 Hourly | CANDIDATE, original issue+provider first-known unverified |
| P1-B | News chronology | `katelabs/crypto-news-scored` published/ingested timestamps, no raw full text export; matching Situation Room source IDs only if authorized | age, reprints, news-first vs price-first, delays and same-clock naive no-news placebo | Existing Situation Room + Task 2 NEWS family | NONCOMMERCIAL + proof pending |
| P1-C | Liquidations quality | `ochinimus/crypto-liquidation-ticks` coverage.csv then five continuous pairs only | 5→800 symbol capture-step negative control, venue truncation, proportion missing and cap bias | Task 2 Stress/Flush source owner | NO June 2026 coverage; NO market-wide N |
| P1-D | Stablecoin source quality | `Chainticks/stablecoin-flows` _manifest daily partitions, `source_kind` and 1–2 sampled days | split mint/burn/bridge, coverage, date/availability, duplicates and whether flow is nontrading | Task 2 stablecoin owner, existing research | SOURCE QA ONLY; no inferred deployment |
| P2-A | Polymarket executable vs optical edge | `polyorderbooks/polymarket-crypto-updown-orderbooks-l2` one selected file | spreads, crossed/one-sided quotes, fees/slippage and vs naive/price-only; exclude `winning_outcome` from X | Task 2 market model owner, if in scope | PRELIMINARY, not CN forecast source |
| P2-B | Existing Alpha PIT repair | Existing `trenches_point_in_time_ablation_v1.py`, same pinned HF source | block negative ages, test-aware feature inclusion, mutable revision risk; rerun exact same holdout only after permitted access | **existing Alpha Lab** | REUSE, NO DUPLICATE WORKFLOW |
| P3-A | News label controls | `SahandNZ/cryptonews-articles-with-price-momentum-labels` | NLP text class control only, no price-prophet scoring | Situation Room research | LOW priority, historical first-known unknown |
| P3-B | Rug benchmark schema audit | `fati-80-Sho/RugPull1K` text/raw representation | test advertised 1,028 project records against Viewer 935.8k 1-column | Alpha Lab research | FORMAT BLOCKED, noncommercial, future-defined midpoint concern |

## Common deterministic acceptance template
Every pilot must emit `pilot_id`, existing owner, source HF repo + **pinned revision SHA**, exact file+content SHA256, file size, coverage UTC, expected grain/key, source license, source first-known claim and *certainty*, original framework **forecast emitted/first delivered** UTC (if asking predictive skill), target time+horizon, all attempted/censored/unknown counts, number of independent families, baseline definitions, negative-control list, abstention, error state, output SHA and evidence status.

Minimum proof tiers:
- **T0 DISCOVERY:** repo metadata, README, license and claimed rows only.
- **T1 FILE_QA:** pinned actual file rows + clock ranges, missingness, duplicates, schema/grain; publisher claims verified/rejected.
- **T2 R1 PIT_ADMITTED:** original issued forecast, provider observer-time and first deliverability certified at decision; full denominator and independent events.
- **T3 R2 MATCHED_CONTROL:** same-clock comparable baseline with preregistered loss/utility; independent families and credible uncertainty; no leakage.
- **T4 FORWARD_CHALLENGER:** prospective held-out observations with decision impact, fees/latency, robust negative controls, governance review; only owner can propose promotion.
Existing HF research today is **T0** for new sources, selected T0+file-manifest inspection, not T1/T2/T3/T4. Code existence and 100% unit-test pass are not valid evidence for any higher tier.

## Rejection/abstention tests (pre-register prior to rows)
- One price candle that closes after issue cutoff → reject; null missing price → unknown, never zero.
- One ingestion timestamp after claimed signal issue → reject; unverified first-known → research-only; published_at must not replace ingested_at.
- One prior-news reprint with new publisher URL → one story family, not two independent predictive events.
- Liquidation collector universe expands 5→800 → fail any aggregate series that crosses it without comparable-universe normalization.
- Venue capped prints in cascade → do not infer market-wide notional count, or lead-time without consistent venue coverage.
- Polymarket missing one side / crossed quote / price known only after resolution → no assumed executable trade or hindsight winning outcome X.
- Pump.fun `reach_derivable_at_decision=false` or negative token age → no nominal-clock alpha feature admission without conservative time treatment.
- Noncommercial/unverified license → local bounded research only where license permits, no live commercial reuse.
- Historical model trained on same period, news label derived from later price or mean-while-test tuning → exclude from clean out-of-sample comparison.

## Evaluation cadence without new automation
Further source claims can be appended to this exact PR branch with versioned addenda. Existing Supervisor/Task 2 research owners may optionally review this *same PR* when normal operational slots run, but this document does not request or create any scheduled job. No monitoring promised from the chat itself. Do not trigger GitHub Actions until minutes are restored and existing governance allows it. A source can be rejected permanently when its type or terms are incompatible; 'REJECT' is useful research.
