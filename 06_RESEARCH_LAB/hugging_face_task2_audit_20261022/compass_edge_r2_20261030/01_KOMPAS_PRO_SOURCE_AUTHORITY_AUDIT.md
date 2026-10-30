# C01/C02 · Official Kompas PRO architecture and original 24-feature provenance

**Status:** EXECUTED_CODE_AND_ORIGINAL_LEDGER_AUDIT / C01_PARTIAL / C02_PIT_HOLD.  
**Mission:** [Task2 Kompas EDGE #1596](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596#issuecomment-6519531633). Research-only. No producer/policy changes.

## A. Actually read code and source identities

Current public main `scripts/data_ping/native_handlekompas.py` original blob `e7b6ee28e3fe29b2f54069126cbf8599c27eb52e`, inspected functions: `action_context` (lines ~334+), `protection_tracker` (~934+), `horizon_map` (~1162+). `scripts/data_ping/compass_event_refresh.py` blob `43f4f625a909b9f6daa68e5e363a7e654de997bf`, event reassessment only. Exact original 11-forecast R1 admission ledger `04_MARKET_LEARNING/handlekompas/research/2026-10-15__TASK2_R1_NATIVE_V3_ORIGINAL_ADMISSION_v2.json`, original blob `9e728b835de294e5777222c171a89874a69dae95`, actually parsed and counted before this report.

## B. Decision DAG and model responsibility

| Output user observes | Current data/code owner | Actually computes | What it does NOT prove |
|---|---|---|---|
| Hourly direction | `derive_market_now`, current governed Auto Market State | Current relative BTC/ETH direction and ETH/BTC movement | Forecast of exact next 12-hour return |
| NEXT_12H | `horizon_map` maps current `directional_state` to UP/DOWN/SIDEWAYS | **Continuation / NOWCAST**, confidence null | Independent 12h predictive accuracy |
| NEXT_1_3D | `_cn_direction(cn_package,"next_1_3d")` plus current action constraints | Weekly source-issued regime / short-window context | A newly trained 24h intraday predictor |
| NEXT_5_7D | `_cn_direction(...,"next_5_7d")` | Canonical weekly freeze / base-case text | Current-hour independent path calibration |
| NEXT_2_3W | Structured CN `next_2_3w` with typed no-edge fallback | Longer structured scenario | Guaranteed return or action |
| Pullback P, 1..5 | `protection_tracker` reads CN `decision_projection.protection.pullback_risk_state` | Authoritative ordinal from weekly/structured source, fail-closed on missing | An hourly stress algorithm capable of promoting P=4 itself |
| Risk age | `last_material_change_at` resets whenever 6-field tuple changes | Latest material change of risk/class/distribution/ETA/quality/re-entry | Original first ELEVATED event or original first public alert |
| Action NOW | `action_context` line `now="HOLD_WAIT" if healthy else "HOLD_WAIT_DATA_DEGRADED"` | **Explicitly governed non-trading clamp**, retired Top100/ETHBTC >0.03 proxies have weight zero | Economically optimized HOLD decision or portfolio protection proof |
| SELL / exit E | Separate governed owners, shadow/unknown | None issued merely from elevated P | Sale/re-entry authority or automatically confirmed distribution |
| Event refresh | `compass_event_refresh.py` detection/dispatch | Reevaluate eligible current state upon market change | Independent new severity state / confirmed causal external event |

**Key root-cause distinction:** Static P=3 despite a sudden price move is not a site display defect: the Native producer reads the preexisting structured CN risk field rather than using intraday stress to recompute it. As a source-authority decision this is defensible, but it leaves an investor-facing temporal-risk *coverage gap*. An acute research stress monitor would have to remain **non-authoritative** pending independently frozen source revision/admission. Similarly a permanent official `HOLD_WAIT` is a governance permission, **not** a 'model recommends always holding because it predicts recovery' signal. Counting HOLD_WAIT as an economically validated prediction would be false.

## C. Original 11-forecast, 24-feature source-custody census (actual aggregation)

**11 immutable original v3 forecast attempts; 24 source feature IDs each => 264 feature observations.** Original 9 outcomes present at captured historical snapshot, 2 absent then; 0 independently PIT-admitted; 0 recorded independently verified vendor first-publication times. Original valid Git capture/packet IDs do not establish original vendor revision time. Data states:

| Original feature-observation custody state | Count |
|---|---:|
| `RETRIEVAL_CLOCK_UNKNOWN` | **143** |
| `ARCHIVE_CLOCK_PREISSUE_PROVIDER_FIRST_KNOWN_UNKNOWN` | **99** |
| `SETTLEMENT_IS_NOT_QUOTE_OBSERVATION` | **22** |
| **Total** | **264** |

**Source families, fixed 24 feature IDs:**

| Source family | Source owners/features | Distinct IDs |
|---|---|---:|
| Price baseline | HOURLY_SEQUENCE: btc_usdt, eth_usdt, ethbtc; AUTO_MARKET_STATE_DELTA: BTC/ETH/ETHBTC delta since prior packet | 6 |
| Participation | LIVE_ANCHOR_BREADTH_REFERENCE / RICH_BREADTH_OWNER: breadth_advance_ratio, breadth_advancers, breadth_decliners, breadth_equal_weight_24h | 4 |
| Rotation | COINMARKETCAP_BTC_D: btc_dominance_pct; BLOCKCHAINCENTER: altseason_score_90d | 2 |
| Capital flow | FARSIDE_SETTLED_ETF: btc_etf_musd, eth_etf_musd; DEFILLAMA_STABLECOINS: stablecoin_total_usd | 3 |
| Derivatives | OKX_HOURLY_DERIVATIVES: btc_open_interest, eth_open_interest; OKX_LIVE_SWAP: btc_funding, eth_funding | 4 |
| Sentiment (one correlated provider model) | CFGI: sentiment_state, sentiment_market_score, sentiment_btc_score, sentiment_eth_score | 4 |
| Previous observer | ENTRY_SIGNAL_LEDGER: entry_signal_state | 1 |
| **Total** | **12 original source-owner identities** | **24** |

**Version-varying ownership:** `breadth_advance_ratio`, `breadth_advancers`, `breadth_decliners` were assigned to `LIVE_ANCHOR_BREADTH_REFERENCE` in seven original forecasts and `RICH_BREADTH_OWNER` in four forecasts; rich breadth `breadth_equal_weight_24h` remains present. This is genuine source-owner switching at the SAME public feature ID, not distinct independent confirmations. A comparative backtest must bind source owner, true constituent universe, original timestamp, and publication clock per row or omit the feature. Likewise four CFGI fields come from a correlated provider model, not four independent predictive votes.

The historical ledger's 143 retrieval-unknown observation clocks cannot be legally converted to independently first-known at issue; the 99 existing archive retrieval clocks are **local archive receipts**, not original vendor first-published/engine revision proof; the 22 funding settlement observations must not be treated as available funding *quotes*. No non-funding feature's declared observed clock was later than the original recorded issuance, but this alone never establishes PIT. Original user warning delivery, no-warning denominator and admitted market event family N remain separate.

## D. What works, what is insufficient, what is missing

**Retain:** immutable source identities and typed reason fields; explicit P risk vs E exit vs current action separation; stale/unhealthy failure closed, no new buy/sell authority from observer labels; realized price-source hourly continuity is now measurable; original W44 frozen forecasts remain independent of later retrospective model development.

**Research-only modification candidates:**
- Separately display `first_stage_issued_at`, `last_material_review_at`, `first_public_known_at`, `last_eligible_price_at`, and expiry when authentic evidence exists; never use material review timestamp as first warning onset.
- Track deterioration speed + recovery/failed bounce as a different **research** dimension, without unilaterally converting P=3 into P=4 or SELL.
- For the alternative Compass candidate, measure proper adverse event *lead time* vs matched price/vol baseline on fresh and same-clock inputs; show action/no-action separately.
- Test ETH/BTC, market breadth, derivatives and same-clock CFGI *incremental value* one family at a time; avoid model-count inflation when provider instruments overlap.
- Historical incident context (FTX 2022; suspected Binance 2026 wallet episode) is an ex-post stress study, not proof of foresight.

**Blocked:** publish "better alternative Kompas" ranking, run hundreds of parameter variants on approx two exposed October event families, infer 24h or 72h true predictive edge from 12h NOWCAST, claim backtested actionable SELL without first delivered/executable quotes, use original outcomes as untouched prospective holdout, or bypass existing #1823 paid API admission. At current gate `R1_PIT=0/11`, `R2/R3 CERTIFIED_EDGE=NONE`.

## E. Next finite verification to unlock genuine testing

1. C02: recover authentic original first-known receipts for one complete source-bound forecast (or prove unavailable) in original #1814/R1. Preserve all no-issue and abstention attempts, derive explicit first stage-change versus publisher issue and investor delivery clocks.
2. C03: preregister primary future downside label, same-clock *completed bar* availability, censored windows, negative controls and independently clustered episodes; confirm a powered source-eligible population before any 150-400 candidate grid.
3. C04: CODEX_ONLY deterministic model engine once C02/C03 prove scope/availability; preserve sealed future outcomes. Compare to the [actual October baseline](04_OCT2026_DEVELOPMENT_BASELINE_REPORT.md), which is ex-post only.
4. C05-08: complete adverse/non-adverse matched event reviews, illustrative versus executable after-cost economics, independent skeptical model review and one consolidated result. Preserve the Round2 negative (zero robust pre-top leads/zero profitable reload policies in its tested tape).

**No source producer or trading code changed in this research.** Current status `C01_PARTIAL_ACTUAL_SOURCE_REPLAY`, `C02_ORIGINAL_METADATA_CENSUS_COMPLETE_PIT_NOT_ADMITTED`, `C04_PRICE_ONLY_DESCRIPTIVE_PILOT_COMPLETE`, `MODEL_COMPARATIVE_EDGE_UNPROVEN`.
