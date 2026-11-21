# EDGE DETECTIVE | Evidence-led hunt, first falsification round (2026-11-21)

**Mission:** OWNER_DIRECTED_SEARCH_FOR_ECONOMIC_EDGE. **Status:** RESEARCH_CANDIDATES_ONLY; one actually sampled negative-control test; no proven new trading edge. **Owner:** existing Research Lab #1512 and High-Value Edge Research framework; Alpha experimental owners remain #908 / original Meme Alpha Lab; pullback owner #1553. **No new canonical signal, trading engine, scheduler, S1 task, private values, paid API, autonomous trading or merge.** This paper is a small incremental evidence packet, not a competing execution queue or source of truth. Do NOT activate a new research program: the existing #1512 QUEUE_V1 still determines sequencing.

**Critical owner STOP:** Previous OPEX project #2299 was explicitly stopped and closed **without merge** on 2026-11-21. OPEX is OUT OF SCOPE and must not be resurrected by this packet.

**Baseline snapshot:** Archive main `24fbd4cbaf8eec12cab167dfa412b037cdfdd404`. External paper titles and dataset provider claims below were verified on 2026-11-21; do not infer that underlying data were replicated or source licenses/quality fully audited. All future validation must re-read exact current main and relevant private boundary as permitted.

## A. First search findings, rank by decision value and testability

| Rank | Distinct opportunity | First concrete experiment, original owner | State |
| --- | --- | --- | --- |
| 1 | **Executable organic-demand vs artificial pump / rug / illiquidity** for microcap tokens. Can we avoid unexitable losers while retaining truly tradable 2x+ winners? | Extend existing Alpha Lab execution_shadow_v4 and the original #1512 `S1_EXECUTABLE_SELLABILITY_TRUTH_V1` proposal; same original *eligible launch universe* at $100/$500/$1k with actual contemporaneous execution costs | **HIGHEST-VALUE TEST CANDIDATE**, no demonstrated edge |
| 2 | **Wallet skill that a follower can copy**, not merely profitable insider/developer wallets. | Original wallet research `04_MARKET_LEARNING/tactical_microcap_lab/WALLET_ALPHA_RESEARCH_PROTOCOL.md`, #908 and #1512 S2; full wins/losses/open positions, same-launch matched control, follow latency and copyability | **TEST CANDIDATE**, earlier 4-launch signal negative |
| 3 | **Second-leg survivor with real distributed demand** after cooldown. | Existing Phoenix lifecycle challenger, prospective trigger vs naive support/reclaim, full failures and exit liquidity | **SHADOW**, no new scanner |
| 4 | **Capital preservation from genuine early risk deterioration**, beyond price-only and always-HOLD. | Existing #1553 / EDGE-001 early warning; exact first-known to delivery to feasible action and false exit opportunity cost | **EXISTING P0**, prioritize fixing causal provenance before new features |
| 5 | **Simple one-hour mean-reversion/chase avoidance on BTC/ETH.** | Exploratory independent Binance hourly sanity check, below | **NO SUPPORT FOR IMMEDIATE TRADING** |
| 6 | **Funding carry / generic cross-sectional momentum.** | Revisit only for demonstrable fee/margin/regime-aware advantage over passive alternatives; avoid derivatives execution complexity | **PARK** until stronger non-duplicative reason |

These ranks express proposed expected decision *value of information*, not measured return, scientific confidence, or claims about ranking of winning strategies.

## B. New external evidence that materially changes feasibility

### B1: Peer-reviewed and preprint evidence

- **USENIX Security 2026: Mongardini & Mei, _A Midsummer Meme's Dream_**, https://www.usenix.org/conference/usenixsecurity26/presentation/mongardini. They study **34,988** tokens on Ethereum/BNB/Solana/Base and report **82.89%** of tokens with >100% gains showed evidence of artificial growth strategies such as wash trades or liquidity-pool-based price inflation. This describes *their cohort/labeling*, NOT a validated fraction of current Alpha tokens. Takeaway: an eye-catching chart +100% is a poor proxy for economically reachable profit.
- **Early Rug Pull Detection on Solana**, arXiv:2611.13342 (2026-11-09), https://arxiv.org/abs/2611.13342. 2,700 tokens, features at 12.5/35.5/93 minutes. Early transfer-graph differences exist; more complex GNNs did **not** show significant early advantage over matched simple XGBoost; do not waste model budgets before testing simple and already-owned features with matching information clocks.
- **_Catching the Rug_**, arXiv:2608.20271, https://arxiv.org/abs/2608.20271. Large Solana launch corpus and early risk classification; population/sampling, labels, chronological holdouts and platform shift need independent audit before using any headline metrics.
- **Crypto anomaly evidence**: 2026 _Taming crypto anomalies: A Lasso-type factor model_, https://www.sciencedirect.com/science/article/pii/S0275531926000255; only 13/49 anomalies significant in their 2014-2023 reanalysis. Other 2026 cross-sectional studies warn that full-sample data snooping defeats many apparently profitable strategies. Portfolio trading must beat simple same-clock controls and realistic frictions.
- **_Diagnostic expectations and cryptocurrency returns_**, 2026, https://www.sciencedirect.com/science/article/pii/S0165188926001612, finds hourly reversal associations; this is a reason to test, not a license to trade a churn-heavy rule.
- **_Crypto Carry_**, Management Science 2026, https://pubsonline.informs.org/doi/10.1287/mnsc.2024.05069, documents carry premia but time-varying economics and risks; user-appropriate executable utility has not been proven here.

### B2: Newly discovered PUBLIC research datasets (Hugging Face)

1. `loopholetape/pumpfun-launches` (CC BY 4.0), https://huggingface.co/datasets/loopholetape/pumpfun-launches. **2,713,057 launches**, Aug31-Nov05 2026, from provider dataset card; `launches` **1,853,849** rows/43 fields post-2026-09-27 decoder period; `launches_legacy` **859,208** rows with known missing-buy decoder; `features` **5,645,886** rows/66 columns; `graduation_pools` **48,438** rows. Verified Hub configs/field schema, not independently replicated raw stream. `KNOWN_ISSUES.md` states pre-Sep27 missed **48% buy instruction rows / 32% SOL entering curves**. Early features observed on **81.6%** of launches, non-random sampling (rug prevalence among sampled vs unsampled differs); some non-SOL quotes, mayhem mode, unclosed outcomes and capture gaps. **Hard gate:** use only eligible `decoder_complete=1`, quote/venue/time-unit matched, resolved outcomes, no prediction-field lookahead; pay attention to September 29 migration clock seam; exclude or stratify missing-not-at-random cohorts. `rugged` is an operational label not legal proof of fraud. `flags`, `rugged_before_row`, `migrated_before_row`, post-event creator sales, `p_rug...` scores and even `f_rep_rug` can leak label availability unless independently re-issued at cutoff. No automatic feature admittance from this schema. Provider's own live API is **NOT automatically an authorized source**.
2. `Slinky21/Pumpfun_Memecoin_Corpus` (MIT), https://huggingface.co/datasets/Slinky21/Pumpfun_Memecoin_Corpus. Advertises **798,430** launches, **33.58m** trades and **26.9m** curve snapshots during 39 days in Jun-Jul 2026. Its `KNOWN_ISSUES.md` documents **1,136,321** inconsistent SOL amounts (**3.38%** trades), **2,360,061** null-price trades (**7.03%**), a system-program address on **6,690,901** trade rows (**19.92%**), stale wallet_stats and near-perfect graduation label leakage from entry-price presence. Also 5 identified regime seams and one confirmed zero-trade outage Jul03. Source remains **HIGH_RISK_FOR_NAIVE_ML**. Do not rank wallets, calculate USD/SOL PnL, or learn graduates without all listed exclusions, snapshot timestamps and independent validation. Never blindly join it with loopholetape due to different periods, schemas and decoder rules.
3. `Smurfetc/solana-memecoin-calls` (CC0), https://huggingface.co/datasets/Smurfetc/solana-memecoin-calls. **13,091** time-stamped *selected calls*, including apparent misses, with mint, time, call cap and **maximum future peak**. It claims hash/OpenTimestamps provenance; NOT independently verified here. There is NO post-alert executable sell quote, full launch opportunity denominator, or drawdown in the seven-column public dataset. High-to-peak multiples are NOT PnL. Use at most as selected alert-cohort case-study after checking original timestamps; NEVER as unfiltered signal calibration/trading profit proof.
4. `pumpdatafun/pump-fun-trades-sample` (CC BY 4.0), https://huggingface.co/datasets/pumpdatafun/pump-fun-trades-sample, advertises one day of bonding-curve/PumpSwap trades with failures retained. Potential *independent* trade-event/clock decoder check, not enough history to establish trading edge. License and schema further audit needed.

**Main new finding:** available public data volume is no longer the only blocker. The harder blockers are **source quality, pre-decision availability, population representativeness, ability to exit, and actual public-chain replay**. Use external data to test original Alpha owners, not to insert their labels directly into production.

## C. Actual negative control: hourly mean reversion (EXPLORATORY)

Tool: Binance public read-only Spot 1h OHLC endpoint, `BTCUSDT` and `ETHUSDT`, 2026-06-01 00:00 UTC to 2026-11-20 23:00 UTC inclusive. **4,152 candles per asset**, fetched in five windowed calls (990/990/990/990/193 API rows; final partial boundary excluded), 2026-06 to August 31 as development, Sept01-Nov20 prospective-style **chronological historical holdout**. Data source output was *not* stored as an original hash-bound archive; figures are reproducibility targets, not independently validated performance. No brokerage order or fill executed.

Fixed illustrative rule: if previous completed 1h candle log return < -1%, **buy spot at the next hourly open, exit at close**. This is a research simulator assuming ideal open/close fills. Compare actual next-hour sign and gross return with same-clock unconditional baseline. Round-trip fee/slippage **30 bp total**, illustrative, not a claimed current actual fee. No short or leverage.

| Asset and cohort | Signals | Next-hour mean GROSS return | Illustrative 30bp after-cost mean |
| --- | ---: | ---: | ---: |
| BTC development Jun-Aug | 36 | +0.139% | -0.161% |
| BTC holdout Sep-Nov | 33 | -0.015% | -0.315% |
| ETH development Jun-Aug | 79 | +0.150% | -0.150% |
| ETH holdout Sep-Nov | 62 | -0.040% | -0.340% |

Trend/regime confounds, low signal N, fee model, open-fill feasibility and original tape reproduction need additional validation for *formal* inference. However **both holdouts gross-negative** and the strategy cannot overcome illustrative frictions. **Verdict: NO_RESEARCH_PRIORITY for naive hourly dip-buy**. Does NOT refute a different time horizon, execution design or information-only market-risk diagnostic.

## D. Only worthwhile next falsification in the existing queue: Organic-demand SELLABILITY TRUTH

**No new live tracker; use current `04_RESEARCH_LAB/external_specialist_dissection/S1_EXECUTABLE_SELLABILITY_TRUTH_V1.md` and existing Alpha Lab execution_shadow_v4 with $100/$500/$1k/$2.5k/$5k notional-aware impact and slippage.** The canonical #1512 queue already calls this S1. Owner shall not run a competing heavy S1 or rename/regate existing work.

**Proposed research-only hypotheses, pre-register before inspecting later outcomes:**
- H0: Simple token age + liquidity + observed transaction count + price trend (source-eligible at exact event clock) is at least as good as external anti-manipulation / issuer-history enhancements for subsequent **realizable exit**.
- H1: Pre-event creator prior-launch history + clustered early wallet funding + independent buyer breadth + transfer/paid-buy classification **reduces actual unexitable losses** relative to H0 after matching launch age, chain, pool type, notional, visibility and market regime.
- H2: Among tokens that pass H1's risk gate, adding a **post-hype 2nd-leg** independent-demand/reclaim signal to the EXISTING Phoenix owner yields more *net executable* 24h/72h outcomes than age/price-only reclaim. Separate program and independent prospective holdout; no retroactive promotion.
- H3: Wallet leaderboards independently beat same-launch mechanical entry **after observation + decision + DEX fill delay**, and with complete unexited losses, not winner-only PnL. Existing wallet skill owner; n=4 RED recurring-pair pilot in `research/api_agent/meme_alpha/experiments/CLEAN_G3_RED_SELLABILITY_PILOT_RESULT_v1.json` reached **zero 2x/5x/10x** post-qualification launches; no general claim from this tiny result.

**One matched-denominator protocol**: all opportunities first observable through the original source at `t0`, stable exact CA and full pool quote/units; exact vendor availability/retrieval clock; freeze model and first permissible decision time; reconstruct actual buy→sell capacity at **$100, $500 and $1,000** next available block/trade, include adverse slippage/gas/priority and bad/unfilled orders. Only source snapshots at or before decision; no later labels, fake event-time-only PIT, price highs, transfer-as-purchase, shuffling creator identity across chronological split, suspicious wallet future lifetime labels, selective surviving pools or negative-label null=0.

**Primary outcome**: *incremental realized after-friction utility* on complete eligible opportunity universe, with number of candidates allowed, no-action, original Alpha champion and simple veto/matched-liquidity baseline. Track avoided real loss, abandoned realized upside, false vetoes on tradable winners, infeasible exits, alert and decision delay, maker/taker/gas, capacity for multiple notionals, calendar/trading regime and token/wallet/entity cluster N. Precision/recall/AUC only secondary. Reject if model's gain is entirely from fewer trades without opportunity-cost adjustment, or disappears at realistic exits.

**Required source-admission gates**:
1. Check exact downloadable dataset snapshot revisions and terms, independent node/on-chain spot checks, schema/units, immutable source manifest and open-source licensing.
2. Exclude `loopholetape` legacy incomplete decoder rows from primary test; explicitly report 81.6%-only early-feature selection and unresolved labels, non-SOL pool subsets and mayhem regimes; never mislabel unsampled as safe.
3. Handle `Slinky21` documented severe PnL/volume/wallet leakage defects; use only audited portions for independent checks; no 6GB ingestion needed before validation.
4. Ensure complete native candidate → original observation→ frozen source → actual fill/exit quote→ outcome chain. No private source values in public issue, public Git, logs or prompt.
5. Block promotions until all prospective and out-of-sample gates in `06_RESEARCH_LAB/high_value_edge_research/README.md` pass. No auto-trading or action authority.

**Kill conditions**: insufficient validated historical source or original first-known clock; data with uncorrectable missingness; apparent effect only from already-known after-outcome features; risk veto misses too many sellable high-upside tokens; net utility below simple matched baseline at realistic capacity; regime failure in untouched forward data. Preserve the negative result and close the question rather than endlessly tuning.

## E. Owner-specific handoff

- **#1512 Research Lab**: Recognize this as incremental evidence/negative-control, deduplicate against existing `QUEUE_V1.json` S1/S2 before any new work. Choose the **single cheapest source-admission and same-clock notional-aware risk-veto comparison** as next action only if original queue permits. No new source scan.
- **Existing Alpha Lab/Meme-Alpha-Lab #908**: Original-scoped implementation after independent readback; do not create another paper wallet or public live feed. Use already existing execution shadow and strict data boundary.
- **#1553, existing Compass Protection**: Continue existing PIT warning science, not a new risk engine. This packet makes no claim of early-warning edge or earnings.
- **S1 #1156**: Observe original queue disposition, never create S1 rule/prompt change or merge from a research-note description. Required independent exact-head review and native CI before any PR merge. Author must not self-review.

**Disposition:** `NO_DOCUMENTED_NEW_TRADING_EDGE`; `P1_ORGANIC_DEMAND_SELLABILITY_CANDIDATE`; `PARK_HOURLY_DIP_BUY`. The work does identify one **more testable, lower-cost** area than building speculative market indicators, grounded in available large public labeled cohorts and existing Alpha execution infrastructure.

**No one should claim that this note proves improved Alpha PnL, a new active signal, verified primary data, a completed vendor/creator inspection, user benefit in production, an approved allocation, or an autonomous future run.**
