# FuturAI Labs Hyperliquid vault: reverse-engineering, risk-layer observability and cross-regime falsification

**Dato:** 2026-11-11  
**Status:** SOURCE_NOTE / RESEARCH_ONLY / NOT_VALIDATED_EDGE  
**Område:** Research Lab, Task 2 / market microstructure / derivatives, Alpha Lab methodological transfer  
**Primary folder:** `06_RESEARCH_LAB/audit_summaries/`  
**Owner:** existing Research Lab red-team; downstream original owners Task 2 #1596, derivatives #387, pullback T4 and Alpha Lab #228 where applicable  
**Authority:** ZERO production, portfolio, trading, model-promotion or live-signal authority. No new engine, scheduled agent, provider expense or source contract.  
**Evidence class:** EXTERNAL_CLAIMS + USER_SUPPLIED_SCREEN_RECORDING + VERIFIED_PUBLIC_METADATA; ZERO INDEPENDENT TRADE-LEVEL OUTCOME ROWS  
**Assessment:** Primary `MODIFY_EXISTING_TEST`; methodological relevance HIGH, actual replicable alpha UNPROVEN, microcap-transfer confidence LOW.

## 1. Frozen proposition

For highly liquid crypto perpetual futures, some abrupt downward overshoots may be temporarily reversible liquidity shocks rather than durable trend breaks. A fixed, time-stamped dip/mean-reversion entry rule MAY generate incremental after-cost value, but only when liquidity, position accumulation, crash-continuation, execution and market-regime risk are explicitly modeled and measured against simpler alternatives. Observing profitable fills does NOT reveal the full risk-control policy, especially vetoes and position reductions that generate no fills.

This note does not endorse using the source's purported entry thresholds as a live signal. It tests a methodology and exposes hidden failure modes.

## 2. Source and timestamp ledger

- S1 author-linked medium-volatility vault profile: https://tradingstrategy.ai/vaults/futurai-labs-high-sharpe-medium-volatility . Vault identity `0x53375ca9a649f337d83d0834fec0db97640a2a06`, Hyperliquid native perp user vault, USDC denomination. The search-indexed detail page retains an explicitly dated 2026-10-30 snapshot (3M annualised net 12.9%, 3M Sharpe 4.84, 3M annualised volatility 2.8%, TVL ~$7.1K). Do not present that stale snapshot as Nov 11 live state.
- S2 user-supplied ~108-second X screen recording `ScreenRecording_11-11-2026 15-18-42_1.mp4`, reviewed visually on 2026-11-11. Shows analyst **Astraeus (@AstraeusCap)**' reverse-engineering write-up, FuturAI market-data page at approx 15:19 Copenhagen, and founder **FM (@FMChain_)**'s response at approx 15:20. Screenshots are user-supplied observations, NOT machine-verifiable on-chain trade receipts, not reproduced experiments.
- S3 founder X thread: https://x.com/fmchain_/status/2120470530176254249 . Screen recording evidences the founder's statement that apparently manual June interventions were automated market-conditioned risk reductions; exact algorithm/source code not public in these materials.
- S4 curator comparison: https://tradingstrategy.ai/vaults/curators/futurai-labs . At 2026-11-11 web retrieval it listed TWO vaults, ~$444K combined TVL, low-vol ~$438K vs medium-vol ~$6.2K, medium-vol 3M Sharpe ~5.0, 3M annualized net ~15.3%, max DD -6%; the curator's latest-post excerpt says medium-vol is NOW a long/short momentum system, indicating probable strategy-version/mandate drift. Treat as displayed claim, require official timestamped vault policy/fill confirmation before declaring exact switch timing or continuity.
- S5 in-video 2026-11-11 Trading Strategy snapshot displays medium-vol 3M annualised net 15.3%, 3M Sharpe 5.0, 3M annualised volatility 3.1%, TVL ~$6.8K vs peak ~$27.9K, max drawdown -6.0%, CORE3 CCC, lockup 1 day. These figures differ from the older Oct30 indexed detail snapshot due to date/source freshness; no contradiction implied.
- S6 vault data definitions: https://tradingstrategy.ai/docs/overview/defi-vault-data.html ; daily-return-based 3M Sharpe annualizes by sqrt(365), rolling-window sample lengths matter; net and gross Sharpe may use same series even if fee treatment differs.
- S7 return arithmetic: https://tradingstrategy.ai/docs/programming/market-data/profitability.html ; net share-price / flow-adjusted profitability must be separated from TVL and raw equity curves; deposit/redeem events distort naive PnL. Protocol rules: https://tradingstrategy.ai/vaults/protocols/hyperliquid .
- S8 primary venue API documentation: https://hyperliquid.gitbook.io/Hyperliquid-docs/for-developers/api/info-endpoint ; `vaultDetails` allows authoritative current identity/performance interrogation, but no API request or fill-level independent audit was executed in this source-note task.
- S9 existing canonical owners: `06_RESEARCH_LAB/README.md`; `.agents/skills/research-lab-red-team/SKILL.md`; `06_RESEARCH_LAB/protocols/README.md`; `04_RESEARCH_LAB/auto_trading/OCELLUS_RULE_ABLATION_RESEARCH_QUEUE.md`; `06_RESEARCH_LAB/hugging_face_task2_audit_20261022/IRONFLOW_10_LANE_MISSION_20261106.md`. Reuse their approved experiment paths; do not create another research engine.

## 3. Source claims, not independent findings

| Claim | Source class | Reproduction status |
|---|---|---|
| Public Hyperliquid fills expose buy/add/sell ladders in a real vault | Analyst screenshot / public-venue capability | Plausible, **exact event identities and full history not independently verified** |
| Approx initial entry: price >=0.6% below 15h EMA AND >=0.85% below 10h high | Analyst estimated parameter | Explicitly called least certain by author; NEVER canonical |
| ~0.364% of equity first buy; averaging down; average entry ~-5.3% when mark ~-7% | Analyst inferred executed fills | Historical mechanical characterization only; excludes invisible vetoes/cancelled orders |
| Take-profit ~+0.56% average entry, ~+0.65% for deeper ladders; 93% sell orders purportedly close whole position | Analyst inferred fills | Must verify sell-event vs whole-position outcome semantics |
| 5-day time stop raises reconstructed Sharpe ~1.6 to ~2.4; one June disagreement with vault | Analyst simulation | **Counterfactual**, not operator's real rule; time-stop selection/overfit risk |
| 2023-Oct 2026 reconstructed top-5/top-10/top-30/ranks-51-100 after-fee Sharpe ~2.75/2.49/1.71/0.48 | Analyst simulation | NOT independently reproduced; listing/universe/rank point-in-time risk |
| Synthetic random-walk tests with 16 trials do not reproduce high Sharpe | Analyst test | Useful negative control, too few and mismatched volatility clustering to prove causal alpha |
| First buy modeled as taker 1.5bp slippage + 4.3bp fee; ladder adds and TP modeled maker | Analyst simulation assumptions | Maker fill and queue realism unverified; costs and funding / impact must be revalidated |
| June 'manual' adjustments were rule-based risk-layer changes, invisible in fills | Vault operator own response | Competing insider claim; unverifiable full hidden risk logic, strongest warning against overclaiming reverse engineering |
| Medium-vol now long/short momentum | Curator latest social-post excerpt 2026-11-11 | Possible structural break, unconfirmed exact migration timestamp; prevent mixing old/new as stationary strategy |

Do **not** compare article's approx 1.9 reconstructed historical Sharpe with TradingStrategy's 3M Sharpe ~5.0 as if they are the same time horizon, data grain, fee model, or strategy version. Nor call the displayed 15.3% **annualized 3-month net return** a realized +15.3% over the last three months. The cached detail page instead reports 3M absolute net returns near 3.0% on Oct30.

## 4. Strongest case for relevance

A. Trade-path forensics can infer entry ladders, exits, hold time, maker/taker fee sensitivity and exposure *on executed paths*. With correct sample clocks this can be a useful mechanism benchmark even if no economic edge is replicated.

B. Liquidity shocks, liquidation acceleration and spread/depth conditions might distinguish a transient overshoot from a structurally failing market. The existing Hyperliquid/Ironflow source-QA and Task 2 microstructure work are already logical owners.

C. The key transferable hypothesis is NOT the 0.6% entry threshold; it is **risk-layer observability**. A model can seem effective because it suppresses trades in bad regimes. These no-trade observations are part of the denominator and must be modeled as first-known decisions.

D. Negative controls (randomized entry time, shuffled events, synthetic paths, path-block resampling, out-of-period tests), explicit net execution costs and capacity limits are valuable methodological upgrades if missing from EXISTING experiments.

## 5. Strongest falsification / red-team case

1. **Hidden zero-fill selection:** a dataset of fills is conditional on the hidden risk gate permitting a trade. It excludes vetoed dips, reduced size, paused periods and unavailable liquidity. Matching its filled trades without their unseen eligible population gives false attribution.
2. **Hindsight universes:** daily top-N must be timestamped with true historical membership, delistings, venue eligibility and earliest tradeability. Using Nov2026 favorites or the vault's 18 traded coins after observing its results is selection bias.
3. **Overfit degrees of freedom:** EMA 15h, high 10h, 0.6%/0.85%, 5-day exit, layered sizing and coin cohort have many implicit tests. 16 synthetic series plus an apparently stable grid do not substitute for pre-registered holdout, Deflated Sharpe or Probability of Backtest Overfitting where applicable.
4. **Market structure mismatch:** a random walk without jump clustering, funding feedback, order-book depletion, forced liquidations, correlated crashes and time-varying spread is a weak placebo. Synthetic random paths have value, not decisive proof of a genuine risk premium.
5. **Execution fallacy:** price touching a maker limit does not establish queue fill. Adverse selection, fees, funding, spread, 24/7 liquidity, simultaneous multi-asset correlations, rejected/cancelled orders and emergency exits can eliminate apparent edge.
6. **Short-volatility tail:** averaging down accumulates exposure precisely when crash continuation, liquidation cascades and correlation rise. Smooth-looking realized PnL may reflect negative skew and rare catastrophic loss; median trade success and Sharpe alone insufficient.
7. **Sample/strategy drift:** vault inception April 2026 (source detail) versus 2023-Oct2026 reconstructed sim; curator now suggests medium mandate changed to long/short momentum. Date-segment every live return and do not silently extrapolate old rules to a new strategy.
8. **TVL illusion:** ~$6-7K remaining versus ~$28K peak can reflect redemptions, not drawdown. Confirm flow adjusted share-return rather than pretending TVL decline is trading loss.
9. **Protocol/operational risk:** CORE3 CCC is protocol risk, not a verdict on this vault strategy; 1-day withdrawal delay and possible forced exits on redemption matter for investor outcomes.
10. **Microcap non-transfer:** the analyst's own reported Sharpe falls substantially in smaller cap bands. Sub-$1M on-chain memecoins have distinct liquidity, rugs, tax/transfer mechanisms, MEV, launch selection and non-exitable size. Do not transfer positive top-10 perp mean reversion to Alpha Lab without separate cohort tests.
11. **Cross-source circularity:** TradingStrategy and a screenshot of its page are not two independent confirmations. Operator claim vs analyst inference is not independent trade-level reproduction.

## 6. Decision-divergence test inside existing owners

**Task 2 / derivatives original owner**: Given the same timestamped eligible **BTC/ETH/HYPE or liquid top-N** liquidation shock and instrument-hours, compare on a held-out, frozen source clock:
- B0: no mean reversion trade / cash; B1: simple fixed 1h/4h dip or 15h EMA deviation, no ladder;
- B2: preregistered mean-reversion entry with capped exposure and single take profit;
- B3: exact same entries and opportunity denominator with a ladder;
- B4: B3 + one observable source-eligible crash/continuation risk veto, including no-trade ledger and same bankroll;
- B5: B4 + isolated time-stop candidate, only if declared BEFORE evaluation and not tuned using June 2026;
- independent conditional benchmark: simple trend-following/momentum and BTC buy-and-hold, with sensible exposure accounting.

Keep **identical events, eligibility clocks, capital, fills/costs, maturity, risk budget and opportunity set**, and store rejected/unknown opportunities. Compute paired differences in whole-position post-cost returns, max adverse excursion, tail CVaR, liquidation risk, capital occupancy, drawdown avoided, upside forfeited, and dependence on extreme market episodes. Report effective independent episode N and confidence/cluster bootstrap; perform regime/year splits, embargo/purged validation, placebo controls and an untouched forward cohort. Track trials and adjust for selection (DSR/PBO or pre-specified multiple-comparison control). Abstain rather than force zero on unavailable quotes/hours.

**Pullback T4**: test whether a liquidity-continuation veto can improve *lead time* and avoid false escalations beyond the existing price-only severe-drop baseline. No automated replacement of 3/5 or 4/5 bands. Only if action-class changes prospectively and actuals are mature.

**Alpha Lab #228**: first use this as a **failure-mode/control** for DIP/PHOENIX and paper-wallet exposure sizing. Test continuation risk, non-exitable rugs, failed sells and refusal opportunity cost on its native prospective denominator. Do NOT instantiate Hyperliquid perp paper wallet on a memecoin platform or claim a viable <1M mean-reversion strategy.

**Research Lab methodological transfer**: add evaluation *design only* to existing Ocellus one-rule ablation and Task 2 source clock. Do not create a new 'FuturAI Engine', new L11 roadmap lane, private source export or production scraper.

## 7. Minimum experiment and kill contract

```yaml
experiment_class: MODIFY_EXISTING_TEST
owner: existing Task2#1596 / derivatives#387, existing ResearchLab T4 and Alpha#228 as downstream
source_data_class: PUBLIC_METADATA_ONLY_IN_THIS_NOTE
source_first_known_required: true
policy_first_known_required: true
unobserved_veto_denominator: REQUIRED_OR_UNKNOWN
sample_minimum: TO_BE_PREREGISTERED_FROM_FEASIBILITY_AND_POWER; zero observed validated rows now
comparison: same-event simple dip, no trade, naive ladder, bounded ladder, regime-gated bounded ladder
primary_endpoint: paired whole-position after-cost risk-adjusted utility AND crash-tail loss
secondary_endpoints: MAE/MFE completeness; CVaR; max DD; funds committed; missed rebounds; gate-specific FNP
falsifier: no incremental edge vs B1/B2 after realistic fills/costs, or no reliable eligible denominator/clock, or strategy only wins with hindsight universe
promotion_condition: independent reproducible PIT source/decision and fill ledger; calibrated prereg holdout; meaningful net paired edge vs simple baseline; prospective across regimes; governance review
kill_condition: survivorship, stale input, unfillable exits, concentrated crash loss, excessive complexity/cost, or null after multiple-testing correction
review_date: after first eligible owner-bound experimental receipt, not automatic
permitted_action: only research design and advisory crosswalk
forbidden_action: live BTC/alt permissions, Kompas or CN forecasts, trading, vault deposits, automatic copying of vault rules, bypassing Round3 firewall
```

## 8. Research priorities and owner routing

| Priority | Next durable action | Owner/duplication |
|---|---|---|
| P0 | Preserve explicit strategy-version and measurement-window caution for FuturAI medium vault; query venue-specific facts only through legitimate permitted public source | This source note; no new scheduler |
| P0 | Reuse existing Ironflow Hyperliquid market data and source clock in a bounded *liquidity shock vs crash continuation* hypothesis spec; verify event-level independent rows | Existing derivatives #387 and Task 2 #1596; no claim results today |
| P1 | Add no-fill veto / exposure-suppression counterfactual to existing one-gate ablation contract and paper/whole-position exit evaluations | Existing Research Lab Ocellus research queue; Alpha Lab #228 |
| P1 | Freeze maker-order fill convention, multi-asset liquidation tail & fee/funding/latency stress; validate execution after-cost | Existing original experiment owners |
| P2 | Track this vault only as a public external observation or illustrative case, if unique value remains after simpler data/controls | No automatic provider costs |

## 9. Research Lab red-team verdict

**Primary verdict:** `MODIFY_EXISTING_TEST` (methodology reuse, no new engine).  
**Evidence class:** `SOURCE_BACKED_NOT_OUTCOME` and `RETROSPECTIVE_RECONSTRUCTION`, NOT verified strategy edge.  
**Methodological importance:** HIGH. **Economic replicability:** UNKNOWN. **Transfer to microcaps < $1M:** NOT SUPPORTED.  
**Biggest insight:** *Executed trades reveal what an algorithm DID when it traded, but not what its hidden risk layer STOPPED it from doing*. This is exactly the reason to count no-decision/NO_TRADE, first-known source clocks, matched eligibility sets and downside/upside opportunity costs as first-class experiment inputs.

**Archive governance:** Additive note, branch/PR only, no canonical index/addendum, no restricted provider values, no backup claim, no source-to-trading promotion. Await original PR acceptance and independent review before counting this source note as merged archive truth.
