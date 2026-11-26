# EDGE DETECTIVE CP02 | Negative wallet-following evidence and Solana cash-realism

Date 2026-11-21 Copenhagen. **STATUS: INDEPENDENT RESEARCH SYNTHESIS, NOT A TRADING-EDGE CLAIM**. Original Source Archive `06_RESEARCH_LAB/mission_packets/2026-11-18__PROXIMA_ORGANIC_DEMAND_SOL62_MAX_v1_EVIDENCE.md` already reviewed the October 29 study below; do **not** present it as a novel research finding or start a duplicate paid Sol mission. This CP02 only adds the November 8 second paper and binds economic-accounting checks to the existing Alpha owners. The source articles are **unreviewed preprints**; reported results are not independently replicated and are constrained by their original sample definitions.

## 1. October 29 preprint (ALREADY KNOWN to Archive)

Fail Gafarov, "Early-Buyer Groups and Fast-Wallet Teams on a Bonding-Curve Launchpad: A Prospective Measurement Study of pump.fun on Solana" (arXiv:2610.39458), https://arxiv.org/abs/2610.39458 . Reported observed cohort: 200,443 launches, 15,854,121 curve trades, 51,025,958 SOL transfers over 88.3 hours. Prospective wallet-group discovery has no verified ownership/intent labels. The external preprint reports **negative follower profit out of sample in all 32 tested configurations**, no better than random follower-entry baseline; extra network complexity did not add token-ranking advantage above naive co-buy clustering. Apparent team effects in final holdout did not beat the early curve-state baseline. It also documents evaluation mistakes where omitting one's own position / using leaked outcomes fabricates profits. This is evidence **against imitative smart-wallet following** on this particular horizon/cohort, not against using cluster signals as *risk vetoes* and not a statement about all markets.

**Existing overlapping work:** Archive Proxima packet blob `bb38a569a8ec100ea3893ba8437910f5a975456f` already includes this paper, with owner #1512 and existing S3/S4/S6/X0 plans. Do not buy a new report repeating it.

## 2. November 8 preprint (incremental economic-accounting warning)

Same author, "Retrospective Analysis of Team-Following Trading Profitability in Pump.fun Meme Coins Using Funding Networks" (arXiv:2611.11436), https://arxiv.org/abs/2611.11436 . Uses 10 separately recorded windows from Apr 2024–Sep 2026, reconstructs real-SOL curve states and hypothetical finite-capital 1-SOL accounts.

From the author's abstract:
- After **hindsight** choice of each team's best exit reserve, modeled equity finished over 1 SOL in all **8** windows with eligible teams, but actually reusable **free cash** finished over 1 SOL in only **5**.
- Of marked equity, **17–94%** was in positions that never reached the selected exit threshold, i.e. marked hypothetical gains are not freely realized capital.
- If teams are identified online after earlier tokens mature, **9 of 19** teams become identifiable only after their **last** launch. Other 10 above-one-SOL equity outcomes are not necessarily executable, because funding links still use the complete future window.
- 3 of 40 null comparisons survive Holm adjustment, but nulls condition on already reconstructed funding graph, not the full detection+selection process. The source explicitly does not claim executable profits.

This is strong *methodological* evidence that running wallet PnL on chosen top winners and marking stuck tokens at model prices can overstate edge. It does not establish a profitable alternative strategy.

## 3. Tests that should be added ONLY to original Alpha economic paper owners

Original Alpha `scripts/research/alpha_edge_economic_tournament_v1.py` and `research/alpha_audit/strategy_arena/README.md` remain the sole economic experiment implementations. Any additions must first compare to existing tests and frozen contracts. New research checks, not new signals:
- **Spendable cash vs terminal marked equity:** aggregate realized free cash, unrealized non-exitable positions, pending/failed exits and economic abstentions separately. A marked profitable open position never finances a later entry until realized. If current engine only reports paired per-opportunity return, keep its semantics and add the test to original paper-wallet/capital-account owner, not misuse a percentage average as portfolio equity.
- **As-of wallet recognition:** derive each wallet/entity skill only from activity visible at the decision cutoff. A team that becomes identifiable after its last launch contributes **zero prospective eligible copy candidates**, not a profitable historical cohort. If graph funding ties are discovered later, keep as postmortem explanations.
- **Same-opportunity baselines:** at equal original source-clock and notional, compare risk veto or wallet rule against (B0) eligibility-only/WAIT, (B1) age+curve liquidity/independent counts, (B2) original champion, (B3) entity-adjusted risk challenger. Retain every rejected token and quantify sacrificed **sellable winners**, not only protected losers. Test risk veto separately from wallet-copy long signal.
- **Execution latency frontier:** wallet signal time = first observable source receipt, NOT wallet transaction event timestamp; include detection, confirmation, decision and actual market quote delay. Quote each buy and full exit at $100/$500/$1k; repeated fills must account for position feedback to pool reserves, fees, priority, slippage and capacity. Compare frozen 5/15/60 min wait variants only if source cadence supports them.
- **Anti-leak tests:** correct reserve state includes user's own hypothetical position; historical access to future team membership, owner lifetime success, creator outcome, title/ticker hindsight, post-migration price high and last-known incomplete opens must fail prior-time eligibility. Require temporal event/actor-group holdout, not random trade-row split.
- **Exposure concentration:** effective number of independent wallet teams, launch days, creators, funding entities and market regimes. One high-frequency actor generating many calls cannot be n=100 independent discoveries.
- **Financial interpretation:** results as after-friction **net spendable cash**, avoided loss, lost upside, full-size unfilled exits, realized wins and N of eligible *economic episodes*. If no complete eligible denominator, return `NOT_IDENTIFIABLE`, not `0%` or `PASS`.

## 4. Specific research decision after negative-control evidence

1. **KILL/PARK generic copying of clustered early buyers as a standalone long-entry rule.** The claimed literature samples show adverse expected follower outcomes, and current Alpha original first-known/live quote evidence is missing. No proof of any improvement over baseline for this system.
2. **RETAIN SHADOW for asymmetric capital protection:** early coordinated concentration / creator serial behavior may still be useful to refuse low-quality quotes, provided independently executable, first-known, opportunity-cost-aware evidence is actually collected. No assumed manipulation or guilt from any individual's connections.
3. **Advance original sellability/Pons first:** exact source completeness and $100/$500/$1k buy/sell full-quantity execution truth. Existing specialist `QUEUE_V1.json` S1 already `PAIRED_DENOMINATOR_MERGED_PROSPECTIVE_DATA_PENDING`; next is prospective observations, not building a second ledger.
4. **Next true edge test is information + economic action lift:** if B3 risk veto does not beat age/liquidity B1 and original champion at equal eligible sources, while accounting for false rejects, reject the proposed enhancement despite impressive fraud classification AUC.

**CP02 verdict:** `WALLET_COPY_LONG_EDGE_UNSUPPORTED_WITH_STRONG_EXTERNAL_COUNTEREVIDENCE`; `RISK_VETO_INFO_EDGE_UNKNOWN`; `SPENDABLE_CASH_AND_ORIGINAL_PROOF_MISSING`. All external figures are author-reported, not framework-measured or independently reproduced. This checkpoint is subject to the existing PR #2300 exact-head independent review/CI; it is not canonical until merge. No private data read and no live action.
