# BUNDLE: Navigator One x Kompas Pro 2.0 master research tribunal (WP1–WP9)

**Source.** Every section below is copied from the public repository
`Donh91/Investering-Framework-Archive-v1` at main `63013b156989cf69aa4cbf83f513c8c2433db465`.

- **FULL FILE** and **EXCERPT** sections are byte-exact. An excerpt keeps the original line numbers: line 1 of its body is the first line given in its header. Cite `section-id:line` with the original line number, for example `S0:33`.
- The two **DERIVED FIELD EXTRACT** sections (K7, K8) are single-line JSON files. They are re-serialized: their values are verbatim, but their formatting is not.
- Each header names the Git blob and the SHA-256 of the full file.

**Data boundary.** The bundle is public-only. It contains no credentials, wallet addresses, holdings, private-plane values, billing or spend figures, paid newsletter text or Bridge content. Your answer becomes a public GitHub artifact.

## P. Preface: pins, omissions and OPEN items

### P1. Spec pins re-read at this main

| Pin | Status at this main |
|---|---|
| A1 `MISSION_BRIEF.md` | Equals the #2221 snapshot blob 088272d4. |
| A2 `SOURCE_MANIFEST_AND_FINDINGS.md` | Equals the #2221 snapshot blob 3e4d1dfa. |
| M1, M2, M3, M5, K1–K8, prior Astra receipts | Equal every blob that S0 pins. |
| M4 `LATEST_OPERATIONAL_MEMORY_STATE.json` | Changed. #2224 pinned blob e056a5af (S0:53: 3761 active / 10259 history / 32 candidates). M4 shows the current blob. |
| AGENTS.md | Changed. #2224 pinned blob 840e9906. B2 is an excerpt of the current blob. |

### P2. Prior Astra results (06_RESEARCH_LAB/astra_program_20261116/results/)

| id | mission | report blob | receipt blob | manifest blob |
|---|---|---|---|---|
| R1 | ASTRA-HIGH-COMPASS-TOTAL-AUDIT-20261116-ONE | 767abd57 | 8dcc82c4 | f3972882 |
| R2 | ASTRA-HIGH-COMPASS-EDGE-SCIENCE-20261116-ONE | ef7f3b54 | 74291edb | 621ff38f |
| R3 | ASTRA-HIGH-COMPASS-EARLY-WARNING-CYCLE-20261116-ONE | 2e8c7b94 | 25e369af | 9f55dbf0 |
| R4 | ASTRA-HIGH-ALPHA-LAB-PAPER-EDGE-20261116-ONE | b1f444a7 | cbfef777 | e9a9b6c2 |
| R5 | ASTRA_MAEVE_TASK2_PREP_V1 | 3d0915bd | e5e33086 | 88bbb699 |
| R6 | ASTRA-HIGH-S1-VNEXT-ARCHITECTURE-20261116-ONE | d2782b4c | 3479897e | 8e88a93c |

- Each receipt states `status: completed`. Its `output_sha256` equals the SHA-256 of the archived report, which was checked at bundle build.
- "Completed" proves delivery. It is not proof of scientific improvement.
- Only the executive sections of each report are included. Their detailed sections are OPEN. The receipts themselves are summarised here, and their cost fields are deliberately omitted.

### P3. Omitted or summarised, and therefore OPEN

- **Alpha Lab `BENCHMARK_CONTROLS_V1.json` and the Strategy Arena README.** These are private-plane repositories. Only S0:21's public-safe description is available.
- **External sources: the papers, the X posts, the Substack post and Meta RAM.** Only S0's summaries are available. Treat their numbers as S0's claims.
- **The 11 reference repositories' code.** Only A2's clean-room paraphrase is available.
- **Native issue and comment threads.** This covers #885, #937, #1156, #1157, #1476, #1512, #1516, #1530, #1553, #1557, #1596, #1827 and #2221–#2226. Only quotes inside the bundled files are available.
- **W46/W47 forecast freezes, scorers and the Compass/Handlekompas source code.** Not included. Their state is UNKNOWN, apart from what R1–R3 state.
- **The remainder of AGENTS.md (88 KB).** Only §5 is included, as B2. The rest of `00_FMOS/S1/EVIDENCE_BINDINGS.md` is also omitted: only lines 1-6 are included, and the bindings B1–B9 are OPEN.
- **Partly omitted files:**
  - A10, the per-repository shortlist;
  - A11, lines 100-289 (A8–A12, findings not promoted, re-prioritised queue, architecture changes);
  - M1, lines 8-11 and 35-36 (model, pricing, ledger and closure mechanics);
  - B1, lines 102-166;
  - D1, lines 54-77;
  - K5, lines 57-86;
  - K6, ARP-02, ARP-03, ARP-05 and the shared-cost section;
  - K7/K8, the keys `hypotheses`, `uncertainties`, `evidence_for`, `forecast_candidates` and `status`.
- **The model policy, the budget ledger, the launcher and the reservations.** These are release mechanics, not research evidence. They are not needed for this mission.


## S0. EXCERPT `04_RESEARCH_LAB/auto_trading/navigator_one/research/reverse_engineering/2026-11-18/ASTRA62_MAX_MASTER_RESEARCH_PREP_V1.md` (blob 48b9c2d92429170234b978d93864b6f28127114a, sha256 of full file dfccd86fa339641e004228b5101e9e247398ceb7d16eb96a0db990f58e1a1c27) lines 1-79 of 130. WP: ALL. the master mission spec (#2226). Lines 80-81 (API envelope) and section 4 (lines 124-131, API release/budget) are omitted: release mechanics, not research evidence.

````
# NAVIGATOR ONE — Astra 6.2 MAX master research tribunal v1
Date: 2026-11-18. Status: PREP_ONLY / OWNER_REQUESTED_ASTRA_MAX (no dispatch). Existing PR #2221. Owner instruction in Investering Chat: combine new Bouchaud/VC/random/convexity research with relevant Navigator One research and prepare a deep Astra 6.2 MAX API run. This does not authorize duplicate paid Sol+Astra reports or alter existing queue release. No production, deployment, portfolio action, signers, automatic promotion or private source transmission.

## 0. Mission and unique value
Build the scientific and product blueprint for Navigator One: a unified, evidence-first portfolio/market/alpha/research interface that proves whether decisions create risk-adjusted, executable edge. Integrate the existing competitive engineering tribunal (MISSION_BRIEF.md, SOURCE_MANIFEST_AND_FINDINGS.md), not a second competing product/agent. Distinguish source discovery, selection, sizing, entry, exit, regime and implementation skill from favorable luck; quantify downside AND missed opportunity. Challenge whether a leaner no-build/adapter approach beats an elaborate engine. Deliver an adversarial, implementation-ready design with measurable falsifiers, not extra opinion reports. Use original owners #885/#937/#1512/#1557/#1133, Compass #1530/#1553/#1596, Alpha #77/#85/#228, Archive #1340. Preserve existing authority and scientific holds.

## 1. Source manifest and admission
A. Existing #2221 branch snapshot a93d0833e3f58dc8ac39be457d95b03e53a7f691: MISSION_BRIEF.md blob 088272d41c610783e46e3013c3a362cfd0050e67 and SOURCE_MANIFEST_AND_FINDINGS.md blob 3e4d1dfab5d43dbac04c848d540a929bab0f2eb2. These describe 11 pinned source repos, five actual inspected code files (ScreenerBot fills/executor, Hummingbot quote cache, Freqtrade wallets, AgentKit provider), design-only sources and BUSL no-copy. Include both, earlier AUTO_TRADING landscape/second-pass audit, cross-repo boundary and Navigator One design seed as verified public-safe text if present on released main. Re-read exact versions and record SHA256 at prepare time.
B. Research intake exactly recorded in https://github.com/Donh91/Investering-Framework-Archive-v1/issues/937#issuecomment-6976605791. Four user source links and five academic leads:
- https://klementoninvesting.substack.com/p/do-venture-capitalists-beat-a-random commentary, inspected; it overstates realized-return interpretation and entry valuation inference. Use underlying preprint, not blogger authority.
- https://arxiv.org/html/2605.03980v1 Knicker/Bouchaud/Benzaquen (2026-05-05), full HTML inspected. Constrained random portfolio benchmarking by timing, stage, sector, geography and count. 26,522 companies; 8,249 unique investors; 1,000 resamples. No detectable superior upper tail, weaker lower-tail evidence sensitive to zeros. Next/current funding ratio proxy, not fund IRR or realized PnL. Equal weights, follow-on missing within 3y mapped to zero, rank/order-statistic simulations, access heterogeneity and dependence limit inference. Do not infer all investor skill absent.
- https://x.com/beniduboss/status/2122858673294733589 enthusiasm and researcher discovery only; no proof of performance.
- https://x.com/beniduboss/status/2122861857065046237 exact reply retrieved from public mirror; direct X unavailable. Five links verified individually through arXiv abstracts (not all full papers):
  * https://arxiv.org/abs/0809.0822 Bouchaud/Farmer/Lillo, persistent order flow and delayed impact; long-memory, liquidity and market efficiency. Hypothesis: impact persistence conditional on replenishment adds warning value.
  * https://arxiv.org/abs/2108.00242v5 Bouchaud, microstructural inelastic market interpretation; impact multiplier increases with volatility and decreases with turnover fraction. Hypothesis: normalize flows by tradable liquidity, not all gross inflows equivalent.
  * https://arxiv.org/abs/cond-mat/0307332v2 Bouchaud et al., persistent market orders offset by mean-reverting limit orders; transient price impact. Hypothesis: distinguish real follow-through vs replenishment and fakeouts.
  * https://arxiv.org/abs/0904.0900v3 Eisler/Bouchaud/Kockelkoren, trade/add/cancel event impact, history and tick-size dependence. Hypothesis: depth withdrawal is a conditional risk challenger, not a standalone trigger.
  * https://arxiv.org/abs/1404.3274 Lempérière et al., long trends across four traditional asset classes, saturation and weakening short trends; no crypto transfer proof. Hypothesis: simple trend baseline can outperform expensive models at some horizons.
- https://x.com/lupinekwakeup/status/2122960763622957212 exact reply retrieved; mentions volume, 1/variance position size and unspecified alternative data in partial +convexity reverse engineering; no original strategy, returns, data identity or replicable rules. WATCH_ONLY until exact public primary spec/ledger; never invent secret alt data.
- https://www.nber.org/papers/w22208 Moreira/Muir volatility-managed portfolios; independent reference, not proof for low-liquidity assets.
C. Existing Alpha Lab main BENCHMARK_CONTROLS_V1.json blob 3bb5579f3c533004139cccea8f0a12492127d760 includes equal unit, momentum reclaim, single seeded matched random (chain, launch age, liquidity). Strategy Arena README blob 3368b670960091bcbbc45291feca4b1d5f30764f describes shared eight arms, source gates, due-only checkpoints and chronological holdouts; actual forward outcomes UNPROVEN. Source URLs: https://github.com/Donh91/Meme-Alpha-Lab/blob/main/experiments/paper_wallet/BENCHMARK_CONTROLS_V1.json and https://github.com/Donh91/Meme-Alpha-Lab/blob/main/research/alpha_audit/strategy_arena/README.md. Public-safe abstract observations only; do not transmit private cross-repo source, wallets or user holdings. No new ledger or writer.
D. Related verified Archive prior findings: 06_RESEARCH_LAB/audit_summaries/2026-11-05__kompas_pullback_altseason_independent_deep_research_intake_v1.md (Donier/Bouchaud liquidity), 06_RESEARCH_LAB/hugging_face_task2_audit_20261022/03_TASK2_RESEARCH_PROTOCOL.md (mechanical baselines). Relevant recent actual Astra outputs in 06_RESEARCH_LAB/astra_program_20261116/results/{compass_total,compass_edge,compass_warning,alpha_lab,maeve}/; re-read directory/receipt/manifest before selecting only nonduplicative public-safe excerpts with exact path/hash. Do not infer all filenames or scientific status. Prior MAEVE reverse engineering #937, forecast baseline and W46/W47 admission/program #1596: use as negative evidence and existing owners, not as validated edge.
E. Additional high-VOI external methodological references for later source admission: Bailey et al., Probability of Backtest Overfitting (https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253); Deflated Sharpe Ratio (https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551); White's Reality Check (https://doi.org/10.1111/1468-0262.00152); Hansen SPA (https://doi.org/10.1198/073500105000000063); Gneiting/Raftery proper scoring (https://doi.org/10.1198/016214506000001437). Candidate references, not fetched or verified in this intake; admit only after exact public source verification. No fabricated conclusions, citations or empirical results.

### OWNER_AUTHORIZED_EXTERNAL_RESEARCH_V1 (2026-11-18)
For external websites already in the owner-approved queued research scope, the framework owner reports that verbal research permission was obtained from the respective management teams; this is an owner attestation, not independently verified, and does not establish broader access or redistribution rights. Within the lawfully accessible and mission-admitted evidence, pursue the deepest useful independent research and functional reverse engineering: observable inputs/outputs, public interfaces, documented APIs, permissible source inspection, algorithm hypotheses, sensitivity tests, falsification and independent original designs. Do not stop a whole mission solely because a technique or source is proprietary; distinguish observed facts, inferred mechanisms, alternatives and missing evidence. Preserve licenses, attribution, source timestamps and provenance; do not reproduce proprietary implementation, protected expression, branding or UI 1:1, bypass access controls or rate limits, use credentials or obtain private data without specific authorization, or export restricted material. The no-tools API can reason only over its admitted bundle: never claim live browsing or reproduction. If evidence or permission for a specific operation is missing, isolate that operation, document the gap and the smallest lawful next step, then continue independent work with the remaining evidence. This mandate does not change the budget, one-shot/no-retry rule, review gates, model admission, scientific holdouts, or trading/production authority.

## 2. Research instructions (Astra must act as independent quantitative red team, not advocate)
Each work package: existing implementation proof (path/revision/receipt; unknown if absent), incremental hypothesis, baseline, data source/time/cost, experiment, denominator, uncertainty, falsifier/kill criteria, integration owner, dependency, acceptance and rollback. Separate source-observed, reproduction, hypothesis, proposal, unknown. Don't claim to access links/code not in input; no invented tests or results. Prefer minimal high-VOI changes to existing owners.

WP1 — Competitive architecture and UX: compare 11 pinned reference repositories per base mission, no-build vs thin adapter vs selective reusable components; evidence-grade source graph and producer/consumer/clock boundaries, permission, licenses, deterministic quote/ledger/fill design, privacy, event-time restart/idempotency, cost, mobile Today/Alpha/Desk/Portfolio/Lab, source/forecast truth. No new execution engine by default. Distinguish implemented feature vs docs-only name.

WP2 — Skill vs luck (highest priority): extend existing MATCHED_RANDOM only where missing. Given frozen as-of opportunity sets O_t, use same timestamp, chain, age, liquidity, market-cap, regime, source access, eligibility, portfolio count/notional, time-in-market and costs. Control A: random from all source-reachable launches (tests scanner+selection); B: random conditional on eligible universe (selection); C: simple rule and every eligible same risk budget; D: equal-weight vs model sizing same token choices; E: matched entry/exit crossover. Never match away the variable being evaluated; avoid post-treatment features; compare coverage/selection effects. Pre-register 1k deterministic seed-family resamples, 10k sensitivity, matched strata with sparse-strata abstention. For upper-tail claims report rank envelope, empirical p=(1+number null >= actual)/(B+1), confidence bands with dependence and finite-sample power; don't assume 1k simulated portfolios equal 1k independent real samples. Block by launch cluster/day/regime; paired chronological walk-forward, embargo overlapping outcome windows, untouched final holdout, multiple testing across arms/horizons, effective N. Include rejected, untradeable, dead and unknown incl failed quote; distinguish verified zero proceeds from missing data. Leave-largest-winner-out, top-1/5/10 concentration, trimmed/median, downside quantiles, drawdown, expected shortfall, return per committed unit, capital tie-up, hit 2x/5x/10x, matched benchmark net executable PnL and selection/timing/exit decomposition. Don't discard true heavy tails; show robustness, uncertainty and censoring sensitivity. No claim of edge unless after-cost improvement and robust independent forward evidence, no false confidence from single top winner.

WP3 — Market impact and liquidity intelligence: contrast persistent signed market-order imbalance with limit-book additions/cancellations, depth recovery and lagged response, turnover-scaled liquidity, price absorption and divergence. Explore pre-registered impulse/decay models and conditional impact estimators; consider sqrt volume impact only as candidate and stress-test power-law fit. Distinguish trade aggressor classification, quote clocks, venue aggregation, missing orderbook gaps and wash trades. CEX L2 order book != AMM/CLMM; for DEX use liquidity curves, LP withdrawals, sized executable routes, fee/tax and pool-specific impact. Aggregate nonredundant features into existing Pullback Radar / Compass and Alpha gates only via tests. Test lead time for drawdown, false alarms, missed warnings, Brier/PR-AUC and after-cost utility; compare forecast-only persistence, ATR, flow-only and existing warning; no automatic thresholds. Cross-asset BTC/ETH/tier/regime comparisons; ETF-era hypotheses must be falsifiable.

WP4 — Portfolio/sizing and +convexity challenger: size equal-dollar, inverse-vol, inverse-variance with predeclared lagged robust volatility (floor) and clips, same ex-ante volatility/capital risk target, turnover limits, covariance stress, capacity/exitability and cash constraints. Distinguish constant exposure vs risk scaling and cross-sectional selection; 1/sigma^2 can lever low-vol regimes, forbid leverage/signing and cap notional. Compare volume-free vs normalized volume term on identical trade set, pre-register volume semantics and lag. Test trend saturation, price-noise, regime switch, liquidity gap, rug and sudden volatility spikes; report evidence, capacity curve at $100/500/1k/2.5k/5k, drawdown/ES and opportunity cost. No paper profit at mark without full-size quote. Unverified +convexity remains WATCH; no reverse-engineered proprietary strategy claims.

WP5 — Forecast and warning science: separate nowcast/direction, path, range, regime, rotation, warning/action; horizons 12h/1-3d/5-7d/2-3w and longer shadow. Holdouts and proper scores (MAE vs naive persistence, WIS/interval coverage+sharpness, Brier and reliability calibration, warning precision/recall and lead-time, utility, FNP). Disaggregate by valid clock, version, regime and asset tier. Do not treat overlapping forecasts or same-week W46 as independent; don't score W47 before maturity or backdate. Check existing Astra reports first; deliver only genuine incremental improvements and concrete tests.

WP6 — Realizable paper portfolios/strategy arena: unify existing frozen decisions with paper fill/quote simulator, immutable cash reservation, partial exits, fees/gas/MEV, latency, stale quotes, missing decimals, sell constraints, duplicate event, reorg, gaps, retry/GET-only reconciliation and mark-to-market vs realizable distinction. Compare multiple risk profiles in isolated paper ledgers under common market clock and matched controls; no actual trade. Separate trader-reported gross chart returns from feasible full-size quote outcomes. Design scoreboard with coverage, sample size, benchmark percentile, uncertainty and no score when insufficient. Paper vs real is always labeled.

WP7 — Adversarial adaptive learning: falsify feature redundancy, selection bias, hindsight, winner-only memories, parameter search, trial multiplicity, overfit learning and feedback loop. Version/freeze every hypothesis and negative outcome; rank by incremental marginal VOI, scientific and economic evidence, kill or merge duplicate candidates. Abstain when data sparse. Design independent Claude critique checklist and no self-approval. No autonomous changes to model weights or strategy authority. Cost/latency of new features must be charged against incremental value.

## 2A. WP8 — ADAPTIVE MEMORY EVOLUTION / CROSS-DOMAIN SCIENTIFIC LEARNING (owner scope extension, 2026-11-18)

### Mission integration and source ownership
The owner explicitly requests integrating the Adaptive Memory Evolution v1 research into the large Navigator One Astra 6.2 MAX study. This is a consolidated advisory research scope, not a new production memory engine, model training mandate or authorization to run two overlapping paid analyses. Keep the original #2224 packet (mission ASTRA62-MAX-ADAPTIVE-MEMORY-EVOLUTION-20261118-ONE) as the source-owned scientific specification, with precise source pins and tests; consume it as an input and preserve its history. Original source: https://github.com/Donh91/Investering-Framework-Archive-v1/blob/c145959ebeeb5aaaadc6bd406266d8e6f980b1cf/06_RESEARCH_LAB/astra_program_20261116/missions/06_ADAPTIVE_MEMORY_EVOLUTION_ASTRA62_MAX_PREP_ONLY.md (Git blob bc83f6f0cade33f9648868f52156d51854d9ce97). Original queue #1157, Research Lab #1512, S1 #1156 and Bridge #173 remain the owners. Link them to this scope; independent review must decide final single release identity and mark overlapping standalone memory/Sol research as held or superseded by reviewed owner action (not delete prior history). Do not automatically invoke both. Reuse completed S1 vNext Astra report and original receipt plus source manifest; no repeat broad S1 architecture audit.

Existing memory evidence, exact historical pins from #2224 (re-read on fresh main and distinguish frozen vs current):
- scripts/framework_intelligence/operational_memory_v1.py @ eecedc566839f4b3367476565d10fac1ae0b4399
- 00_ARCHIVE_CONTROL/SEL_SELECTIVE_OPERATIONAL_BINDING_v1.json @ 6e4b7c59d33445b294b5a1d2e09635d06ca25834
- research/framework_learning/operational_memory/LATEST_OPERATIONAL_MEMORY_STATE.json @ e056a5af81a9c90864a1558e77fabfcae601409a (snapshot 3761 active / 10259 history / 32 procedure candidates, counts are not evidence of causal usefulness)
- 00_FMOS/S1/EVIDENCE_BINDINGS.md @ 41f19f5e652576de4125a6ef11812a73be83b477
- 06_RESEARCH_LAB/astra_program_20261116/results/s1_vnext/ASTRA_S1_VNEXT_RESEARCH.md @ d2782b4c92c20218b31ff2eef6e235a718799ca9; original receipt blob 3479897ef0089787c5baa8de2a0f897683d1eead and manifest blob 8e88a93cc74a28a4564e2433608406001f978414.
- #1512 source intake https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1512#issuecomment-6976461803 and #1157 adjudication https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1157#issuecomment-6976470871. Private Bridge review pointers may be referenced in governance internally; never send private content to external API. Supply only admitted public-safe excerpts and exact SHA256 at release.

Primary Meta RAM source https://facebookresearch.github.io/RAM/blogs/self_improving_memory/ inspected via direct provider fetch 2026-11-18. Kimi-K2.6 in both task/meta agent roles, persistent file store, fresh context per subtask, LOAD/OFFLOAD instructions. Harness search over paired memory prompts with trajectory analysis, ranked variants evaluated on separated splits and demonstrated behavior subsequently distilled into model weights. Reported three-task CL-Bench average 56.0 vs 44.6 best handwritten harness (+11.4 points); generic-harness fine-tuning score 43.1 vs 37.6 generic-training baseline (+5.5 points), separate experiment. Not demonstrated for this framework, finance or our model. Do not infer that fine-tuning, 1M context, more stored memories, or frequent prompt rewriting is necessary. #2224 cites 37/44 revisions not beating prior best: recheck exact primary result before use; do not treat repeated model-proposed improvements as likely successes. Retain failed versions, independent held-out evaluation, cost and safety. Additional #2224 related source candidates: CL-Bench https://arxiv.org/abs/2606.05661, MemOp https://arxiv.org/abs/2606.05646, ACE https://arxiv.org/abs/2510.04618, MemCalib https://arxiv.org/abs/2609.24259, Evo-Memory https://arxiv.org/abs/2511.20857, ALMA https://openreview.net/pdf/23878e570503a3805275ae0ee052f1d263ccd018.pdf; read and verify exact primary source before inclusion; not all independently examined in this scope extension. Candidate new comparative reference EvoMemBench https://arxiv.org/abs/2605.18421 (abstract inspected: benchmark distinguishes within/cross-episode and knowledge/execution memory); use as potentially relevant evaluation taxonomy only.

### Research questions and proposed architecture (not implementation)
H0: outcome-qualified memory management does not increase correctly verified task/decision utility beyond fixed retrieval and current-source-only alternatives under equal resources. H1: useful memory selection improves future independent outcomes, not merely recall volume/green checks, and reduces repeated errors and cost. Determine which changes are portable between domains and when not to transfer them. A memory pointer is an evidence hint, never authority. Existing action contracts, fresh main, forecast freeze, and release rules always prevail.

Model three separable layers in existing stores: immutable observation/outcome evidence; versioned candidate retrieval/retention policy; independent evaluation and promotion/rollback. No new canonical memory store or scheduler. A minimal lifecycle proposal: OBSERVE -> BIND_ORIGINAL_EVIDENCE -> OFFLOAD_CANDIDATE -> VALIDATE_SCOPE/FRESHNESS -> LOAD_ELIGIBLE -> INDEPENDENT_OUTCOME -> CREDIT/DEBIT/QUARANTINE -> REVIEWED_POLICY_UPDATE or RETIRE. Never rewrite an original forecast, receipt, or decision to reflect later knowledge. Keep raw historical evidence and negative results immutable while restricting stale/invalidated material from active recall. Memory eviction is not deletion of audit records.

A. S1 operational learning: stable failure signatures across repositories, source hashes, affected rule/version, known fix, actual native CI/run/main and verified natural outcome; match present preflight and compatibility before reuse. Distinguish recurrence from copied issue text or retries. Learning target independently verified closure, not comment count. Stale approval, race, stale bootstrap, false READY, wrong repo/HEAD, stale contract and 403/429 should have explicit negative fixtures. Never authorize writes, merge, budget or release via retrieved memory.

B. Alpha Lab discovery/strategy memory: preserve every eligible/rejected/dead/unknown candidate, exact first-known time/chain/CA/pool, ex-ante features and maturity clock. Case memory may suggest hypotheses or retrieve analogous cases; cannot introduce hidden future price, retrospectively award scanner/selection credit, or inherit a wallet label without current identity/execution proof. Compare selection, reachability, net full-size realizable returns, missing/missed candidates, after-cost lift against WP2 matched random and simple baselines. Separate failed research patterns from personal wallet/holdings; no public private-data projection. Do not conflate outcome memory from winners with prospective selection skill.

C. Compass / Cycle Navigator memory: retrieve only cases available at forecast issuance, bind policy/version/regime and independent outcome. Evaluate incremental MAE/WIS/Brier, warning lead time/false alarm, false-negative opportunity cost and utility against persistence/ATR and frozen model baseline. Distinguish post-outcome learning from prospective prediction, independent weeks from overlapping windows, and regime shift from repetitive anecdotes. No memory-driven automatic weight changes or signal escalation; preserve unknowns.

D. Navigator One portfolio/paper wallet research: learn execution failures, quote expiration, unsellable assets, capacity gaps and risk-reconciliation incidents from receipts. Evaluate whether recall prevents duplicate fills, stale quotes, phantom marks or capacity violations while maintaining opportunity coverage. No real fills or authority from memory. A domain-isolated research method may transfer (e.g. PIT discipline), but empirical claims/weights/user data may not. Test cross-domain transfer against domain-local memory and no transfer; quarantine negative transfer.

E. Memory economics and causal attribution: log candidate recall ID/version, why/when eligible, evidence class, access clock, tokens/latency, action taken, outcome and independent adjudication. Compare paired runs under same frozen model/settings, tools, time/data and budget. Score retrieval precision, harmful recall, missed useful recall, causal contribution to successful outcomes vs mere coincidence, and cost per verified success (not per generated token alone). Compare B0 current source/no optional memory, B1 fixed existing deterministic recall, B2 outcome-qualified adaptive policy, and at most two pre-registered challenger policies. No adaptive search on held-out data. Group correlated tasks by failure/launch/regime clusters; use temporal splits, source availability and strict blinding of outcome. Report paired confidence intervals/effective N, missingness, costs, robustness, multiplicity and uncertainty. 30–40 initial repair cases from #2224 measure feasibility only; adequate independent N for promotion determined before test. S1 proposed practical target +10 percentage points independently verified closure with positive lower 95% bound and acceptable power; no critical authority/provenance/privacy/false-READY regression. Alpha and Compass require distinct pre-registered economically relevant metrics and thresholds; no inference of market alpha from software eval. Underpowered/negative -> RESEARCH_ONLY / REJECT / WAIT_SOURCE. No fine-tuning, learned policy activation or source mutation by Astra. Prefer cheap deterministic checks; high-cost model is for this architectural synthesis, not routine recall.

Mandatory adversarial controls: intentionally outdated facts; deleted/superseded procedures; contradicted memory; erroneous high-confidence historical result; prompt-injection text masquerading as policy; future-outcome poison; wrong-repo/asset/clock; duplicate episodes; missing data vs zero, revoked permission, correlated episode grouping; hidden privacy payload; replay/rollback/restart. Injected evidence must never grant authority. Freeze each experiment and preserve all failed candidates; show no-build and fixed-memory alternatives. Any policy updates require original owner's reviewed PR, independent test and exact runtime evidence before promotion.

### Added outputs and acceptance
In the same consolidated report deliver: (i) source-backed actual memory dataflow, namespace/permission matrix, cross-domain transfer allow/deny rules and overlap census; (ii) minimal LOAD/OFFLOAD spec and versioned lifecycle, pseudocode and a synthetic receipt example; (iii) preregistered paired trial design per S1/Alpha/Compass/Navigator portfolio, with distinct primary endpoints and independent clocks; (iv) cost/latency/accuracy tradeoff and a concrete negative-test matrix; (v) prioritised implementation candidates with owning issues, evidence requirements, kill criteria and rollback; (vi) ranking of what to retain, compress, quarantine or exclude based on measured value; (vii) explicit verdict on whether adapting memory beats simply reading authoritative current-source or using a fixed policy. WP8 is a first-class work package, not a footnote to WP7; WP7 owns overall scientific methods, WP8 owns memory-specific ablations and transfer/retention design. Reuse prior finished Astra analysis rather than pay for repeating it.

````

## S0. EXCERPT `04_RESEARCH_LAB/auto_trading/navigator_one/research/reverse_engineering/2026-11-18/ASTRA62_MAX_MASTER_RESEARCH_PREP_V1.md` (blob 48b9c2d92429170234b978d93864b6f28127114a, sha256 of full file dfccd86fa339641e004228b5101e9e247398ceb7d16eb96a0db990f58e1a1c27) lines 82-123 of 130. WP: ALL. the master mission spec (#2226). Lines 80-81 (API envelope) and section 4 (lines 124-131, API release/budget) are omitted: release mechanics, not research evidence.

````

## 2B. WP9 — KOMPAS PRO 2.0: PIT MARKET FINGERPRINT, PROBABILISTIC PATH AND MARKET-TO-ALPHA
Owner scope extension 2026-11-18; PREP_ONLY. Integrate the existing Kompas2 Sol MAX research question into this single Astra 6.2 MAX master study, while maintaining Kompas's independent source, forecast, warning, scientific and delivery owners. Owner asks whether separate paid Sol research now would be valuable. Recommendation: do not duplicate the paid broad analysis; reuse completed Astra and Sol evidence. Keep urgent W47 production/scoring/source work independent of the research release. A narrowly defined independent Sol critique might be justified only if a distinct actionable gap cannot wait for Astra, deterministic source checks do not suffice, current budget/admission passes and a separate exact owner release is granted. No such gap has been established by this intake. Larger context/model capability is not itself evidence of greater forecast skill. Preserve earlier release history; do not silently relabel the packet or change its active queue state.

### Frozen source and status census
At main 6c7aacc4dcff11851c62674eac07ed0533553a0e: #2221 and #2224 merged. Existing sequence 27 mission KOMPAS2-FINGERPRINT-ALPHA-CROSS-EXAM-SOL61-MAX-20261111 is ACTIVE_RELEASED in queue (new_paid_attempts_authorized=true, native exact signed trigger still required); Navigator seq 28 OWNER_HELD_NEXT. Queue blob 86aed90194b7c53a9e444455e88bf50cb60d6293. Original packet's model gpt-6.1-sol / max; shared model policy may select qualified 6.2 Sol only as permitted by exact packet and policy. It is not already an Astra packet. Readback of 124 #1476 comments found no matching mission trigger/result; the ten exact planned L01-L10 output paths returned 404 at the pinned main. This is absence at checked routes, not definitive proof no related native work occurred. Recheck all native claims, durable response ID, workflows/artifacts and receipts before changing either release. If found, archive byte-exact and reuse; never repost a consumed mission. No signed release trigger in this change.

Mandatory source-bound inputs (existing Git blobs read at intake; at real preparation resolve fresh main, exact revision, SHA256, bytes and source rights):
- 06_RESEARCH_LAB/mission_packets/2026-11-11__KOMPAS2_FINGERPRINT_ALPHA_SOL61_MAX_v1.json @ ad615df9cf03324d0b55d94a248642893acecfee; retain as historical specification, not executable instructions embedded in Astra.
- research/autonomous_research_portfolio/KOMPAS_PRO_2_APPROVED_RESEARCH_PLAN_20261111.md @ 1f39d231a982925b84214cc0283cc9edb7d833fe.
- research/autonomous_research_portfolio/KOMPAS_PRO_2_PARALLEL_LANES_20261111.json @ 3f7620158e1c67c08fe529f60cd3ea6e549b0ec0.
- research/autonomous_research_portfolio/EVIDENCE_DECISIONS_AND_TOP10_v1.md @ 3bff958b85f00ada8b5b7463ba111c1ef47b8c89; PRODUCT_RECIPES_v1.md in same folder @ 79527717e56011908011071b8f58cee79852cb58.
- research/programs/MARKET_ANTICIPATION_RESEARCH_PROGRAM_v1/RESEARCH_CONTRACT.yaml @ 979e40191372ae0eea17ea925c8a99479fc58112.
- research/api_agent/outputs/research_lab_sol/ARP01-FORECAST-EDGE-CALIBRATION-SOL61-MAX-20261107/issue-1476/comment-6714216846/RESEARCH_LAB_SOL_ANALYSIS.json @ 0911c02b5ee4705ba7c232f676b77f745687c31b; ARP04-MICROCAP-SURVIVAL-EXECUTABLE-ALPHA-SOL61-MAX-20261107/issue-1476/comment-6720273819/RESEARCH_LAB_SOL_ANALYSIS.json @ f8c270f803c540a43787e4a4e11deb921c4086fe under same outputs directory. Prior findings: partially pre-issue OHLC interval, suffix-only denominator, width/quantile semantic limitations, first-decision clock ambiguity, test-aware feature selection, no proved full-sized sellable alpha. Revalidate fixes before suggesting code.
- 00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md @ c8ead1b0e92c32eef4a911ad1b6bf33a09170966; AGENTS.md @ 840e9906af233b1d8455e7f141a3341cc08283ac. Use limited public-safe relevant extracts, no private data or credential text.
- Prior Astra program completed receipts under 06_RESEARCH_LAB/astra_program_20261116/results/: compass_total/receipt.json @ 8dcc82c41f7133804e2c1809d1abb0ba091c6c8b, compass_edge/receipt.json @ 74291edb42575decfc0ee03fd3de837c2dd665d3, compass_warning/receipt.json @ 25e369af9907bca8dd1fef7977b4e0481fee8d7b. Status completed, not proof of scientific improvement. At release select verified report excerpts and manifests, match report SHA256 to receipt; no rerun of these broad topics. Integrate W46/W47 Task2 and MAEVE results where source-bound and nonoverlapping; compare current #1596/#1516/#1553/#1827/#1530 and private Alpha #22/#228. Other L01-L10 programs are not this plan's lane receipts.
- Original approved owner intent #1516 comment 6792163896. Preserve Round3 prospective-collection-only firewall and W47 onward prospective chronology; never retrospectively relabel weeks as untouched.

### Transfer all ten original lanes, with distinct scope and existing ownership
L01 source lineage: census issuer/collector/delivery/consumer, original immutable issue IDs, first-known/vintage, availability, target, venue/unit, hashes and expiry. Classify missing, late, stale, blocked, delivered and unscorable separately. Source/production owner #1827; no source substitutions.
L02 W46 frozen daily closes: reconstruct only original Monday 7/7 BTC/ETH targets, amendments, intervals and true maturity; check existing repairs/scorer on main, full denominator and earlier overlapping OHLC. Do not retune or rewrite original W46; historical W41–W46 development only.
L03 proper-score tournament: same-time no-change, realized-volatility bands, existing canonical, abstain; MAE/normalized MAE and directional balanced accuracy with coverage, interval score/WIS/pinball only for genuine declared nominal quantiles, Brier/log loss only originally issued probabilities. Separate scalar close, realized extrema and entire path; no invented confidence probabilities. Same cohort, forecast availability separately reported, paired block/cluster uncertainty.
L04 compact market fingerprint: preknown BTC trend, ETHBTC trend, realized volatility, observable breadth, ETF vintage and liquidity availability, only small fixed feature families; regress/ablate against price-only and volatility/current model. Connect WP3 liquidity/flow and WP8 memory as challengers, not new duplicated feature owners. No weighting or feature selected using future data. Missing source -> unknown/abstain.
L05 probabilistic path: compare frozen no-change median and rolling-volatility quantile bands vs one small shadow candidate (conditional quantile or path distribution, explicitly define target). Validate coverage+sharpness and proper score across 12h, 1–3d, 5–7d, 2–3w; 4–6w only existing shadow contract and longer horizons only authorized research. Report path consistency, turning-window, drawdown depth error and tradeoff vs short-horizon forecasting. No narrow interval precision claims without valid coverage.
L06 rotation: test ETHBTC leadership, sector/cap-tier relative performance, breadth/liquidity/ETF as-of vintages, lead-lag against ETHBTC-only, BTC vol, lagged/reversed-clock and shuffled-era placebo, market-shock dependence and correlated family control. Separate high-level rotation from investable token and warning decisions.
L07 Alpha survival: test predecision public CN regime context vs existing private Alpha G2/default and WP2 matched controls; strata chain/age/liquidity/venue/operator/launch cohort, include rugs/dead/unknown/censored/rejected, separate survival and saleable return. Only private original owner performs private research. Public-to-private one-way contract CONTEXT_ONLY; no data, token rows, wallet IDs, restricted values or private results sent back publicly. Aggregate receipts only with authorization; otherwise WAIT_PRIVATE.
L08 full-position paper utility: after-cost exit route size/fee/slippage/gas/MEV/capacity/failed fill and opportunity cost of HOLD/WAIT; contrast risk-reduction vs missed upside, quote-based implementability not chart 5x claim. Reuse WP6 paper and original Alpha owner; no actual order, signer or portfolio intervention.
L09 independent model critique: transfer the original Sol research question to this proposed Astra run; its decision scope is *at most two* distinct smallest nonduplicate Kompas shadow/code-design candidates, or zero if already addressed: e.g., original-issue scorecard/denominator and limited PIT fingerprint. One explicit no-code private Alpha negative-control proposal. No broad re-analysis of ARP01/04, S1 vNext, Compass Total/Edge/Warning. If native Sol results already exist, incorporate exact artifacts as evidence rather than rerun; no extra agents or paid fanout.
L10 adversarial review: Claude/Fable #173 independent assessment of source admission, null/missingness/score semantics, complexity and economic nulls; no claim reviewer executed merely from plan. Existing #1157 scientific disposition; #1156 original-owner routing. Keep all production work under existing owners, no replacement supervisor or forecast engine.

### Cross-WP integration and experiments
Factorial ablation on same immutable as-of-time cohort: B0 strongest cheap baseline; B1 existing frozen Compass; B2 compact fingerprint; B3 B2 plus vetted adaptive-memory retrieval only if independently pre-registered (WP8); B4 feature-off/clock-placebo. Cap challenger count and multiplicity; compare nested incremental contribution rather than crediting all correlated features. Separate source availability/admission, prediction skill, warning utility, regime-to-Alpha survival and net paper execution as independent endpoints. H0 no incremental forward proper-score or economic utility advantage; define meaningful effect before holdout; group by independent week, market shock, operator/cohort; purge/embargo overlapping horizons. Review target 26 independent prospective weekly cohorts is not power guarantee; W47 onwards only if candidate actually frozen before outcome; later freeze begins later cohort, never backdate. Record full denominator and eligible paired cohort, missingness and effective sample. If zero support or all gains fail cost/leak checks, reject extra complexity. Negative result valuable.
Public interface extension proposal only, reuse Alpha public_context/CONTRACT_V2.json and source-true fields: compass_issue_id, immutable source_commit_sha, forecast_schema_revision, issued_at_utc, known_at_utc, valid_until_utc, quote_unit, horizon, regime_label_or_unknown, feature availability, confidence provenance, source health, shadow_research_only. No new private-public return flow, no authority from regime. Include stale, future-known, wrong unit, mismatched ID, missing issue, expired context, censored rugs and postdecision features as negative fixtures.

### Required deliverables
Within master report: (i) L01–L10 evidence census, crosswalk and remaining gaps, distinguish plan from native tests/runs; (ii) source-first exact-clock/interval/denominator contract; (iii) smallest frozen market-fingerprint and calibrated path spec or rejection; (iv) same-clock proper-score benchmark/holdout/ablation with independent N and review target; (v) warning and rotation falsifiers, explicit link WP3/WP5/WP8; (vi) public-to-private Alpha survival/sellability interface and negative control, no private export; (vii) at most two nonduplicate candidate changes and precise existing paths/tests/owners/rollback, otherwise NO_NEW_CODE_IF_DUPLICATE or WAIT_SOURCE; (viii) Fable/Claude red-team handoff; (ix) prioritized P0 production/source vs P1 science distinction. Keep collection/scoring and urgent W47 integrity independent of Astra availability. No code or live prediction changes in this research.
### Release coordination
Prefer one consolidated Astra 6.2 MAX run under the owner-approved mission ceiling and release route in section 4. Existing active Sol seq27 and held seq28 remain unchanged by this docs PR. Before any dispatch, actual native claim/output census plus an independently reviewed owner queue transition must prevent a duplicate active paid release; if seq27 is unspent, record explicit owner-authorized hold/supersession into Astra without faking a completed Sol receipt or bypassing #2221's release gate. If already posted, recover GET-only and archive actual evidence. One independent nonoverlapping Sol run only if evidence establishes a time-critical actionable gap and separately qualifies; not recommended now. Preserve all source history and original scientific limits.

## 3. Required deliverable
One coherent raw research report across all nine work packages, explicitly including WP8 and WP9 outputs and preserving #2224 and original Kompas2 scientific conditions, + machine-readable candidate table (as Markdown JSON code block or separate section, not tool execution): (1) executive decision and source/evidence limitations; (2) source-to-decision dependency graph; (3) 10 best transferable competitive engineering primitives; (4) 10 pre-registered scientific experiments with exact nulls, units, outcome clock, costs, data gap/power and kill criteria; (5) skill-vs-luck benchmark design and worked SYNTHETIC example clearly labeled; (6) risk/sizing/sellability specification with negative tests; (7) market microstructure feasibility by CEX/DEX; (8) no-build vs minimal vs expanded architecture tradeoff and cost; (9) UX mockup information architecture and honest evidence labels; (10) 5 major hazards and independent red-team critique; (11) prioritized implementation/validation roadmap by existing issue/PR owner, with exact overlap, no duplicate tasks; (12) explicit GO/NO_GO/WAIT_SOURCE per proposal and scientific promotion conditions. At least 15 concrete testable acceptance cases; 3 bounded source probes only if materially valuable. Distinguish paper/model hypothesis vs actual observed data. Results review by Claude then S1 routing, no authority change.

````

## A1. FULL FILE `04_RESEARCH_LAB/auto_trading/navigator_one/research/reverse_engineering/2026-11-18/MISSION_BRIEF.md` (blob 088272d41c610783e46e3013c3a362cfd0050e67, sha256 e6863fdc596e42a5805f93741952df3928fe6d140f26e8fa25ddf2bd403a3f81, 16 lines, 4200 bytes). WP: WP1,WP6. competitive engineering tribunal brief (#2221).

````
# NAVIGATOR ONE | SOL MAX competitive learning mission v1
Status: source-frozen preparation for one explicitly requested paid advisory; no execution authority, no new scheduler. Base design PR #2220 open when drafted; use standalone public-safe evidence here rather than depend on unmerged files. Existing AUTO_TRADING #885/#937/#1512/#1557, portfolio #1133, Alpha portal #228 and original Alpha/scientific owners remain authoritative.
## Question
How can Navigator One exceed best-in-class trading product engineering in measurable correctness, safety, data integrity, after-cost paper realism, UX clarity and maintainability? Not a claim to outperform returns. Analyze before building. Compare separately from existing framework; no new engine without missing capability demonstrated.
## Work packages
A Discovery/verification: exact chain+CA+pool, provenance clocks, scanner admission, holder/rug evidence, source disagreement and unknown; existing Alpha producer only.
B Quote + execution simulation: quote provenance, full-position sellability, atomic decimals, costs, partial fills, expiry, slippage and MEV, no fake fill, source outages, reorg, reset vs executable return, quote adapter coverage and strategy paper wallet isolation.
C Risk/portfolio: aggregate budget across strategies, cash reservation, correlated positions, loss limits, deny by default, rollback, read-only wallet provenance, UNKNOWN not zero, mark-to-market vs executable value.
D Agent orchestration: typed observations, intents, decisions, receipts, deterministic independent policy, tool capability separation, prompt injection, no signing or transfer privileges, retry/restart reconciliation and cost control. Compare one agent vs specialism under same opportunity set.
E Research engine: reuse existing trial ledger, frozen PIT cohorts, holdout, matched baselines, opportunity cost, skipped candidates and selection bias. No score or strategy promotion without evidence.
F UX: desktop and mobile Today, Alpha, Desk, Portfolio, Lab; explain refusals, source freshness, model/data disagreement, frozen forecasts vs actual, accessible charts, synthetic fixture mockup concept only; no fabricated numbers. Unified backend via existing immutable outputs, not scraping sites.
G Code quality/security: license-by-file, dependency/SBOM, test seams, event idempotency, cache TTL, actors/permissions, audit integrity, load/time budgets, privacy and failure injection.
## Required report
For EVERY component report source repo/revision/path/blob or documented-only/unknown; actual observed invariant; existing owner/path or UNKNOWN; specific gap; original proposed design; comparison baseline; acceptance test incl negative control; priority and dependency; license/reuse verdict: clean room / consider permissive after check / reject / later verified. Score design options on correctness, provenance, privacy, execution realism, cost, latency, complexity and maintainability; do not assign observed performance scores without measured evidence. Identify 10 highest-value transferable primitives, 5 anti-patterns, 3 minimal high-VOI follow-up source probes, alternative architecture A/B/C including no-build, and the minimal future implementation sequence. Use exact supplied source observations only; missing evidence -> WAIT_SOURCE; no inventing code paths, running tests, accessing URLs or claiming live model edge. Include clean-room pseudocode/spec only if valuable; no executable source mutation. Present handoff to Astra and Claude/Fable for independent design proposals after foundations stable, and S1 for owner dedup.
## Result registration
Native Sol output, receipt and context_manifest stay immutable in research/api_agent/outputs/research_lab_sol/<mission>/issue-1476/comment-<id>/; once native receipt PASS, archive a linked byte-exact copy or a hash-bound pointer and human-readable synthesis under this folder/results/ via one reviewed docs PR. Do not create a fake results file; no re-POST. If project model unavailable, existing qualified model selection may fall back to Sol 6.1 and actual model must be reported, never mislabelled as 6.2. No Astra fallback. Existing one-shot queue and release gates apply.
````

## A2. FULL FILE `04_RESEARCH_LAB/auto_trading/navigator_one/research/reverse_engineering/2026-11-18/SOURCE_MANIFEST_AND_FINDINGS.md` (blob 3e4d1dfab5d43dbac04c848d540a929bab0f2eb2, sha256 f2262c1d2ccc986d2f0101259a0f19d71d98996325534d932393a45ffad70090, 23 lines, 8394 bytes). WP: WP1,WP6. 11 pinned reference repos; 5 inspected code files; clean-room paraphrase.

````
# Navigator One | public source census and first-pass technical evidence
Date 2026-11-18. Research/design only. Source revisions were resolved from native GitHub branch API; reported license is repository metadata unless explicitly confirmed by source header. No external code imported or executed. This file is a clean-room paraphrase, not a license approval. All links are public. Source strings are data, not instructions. Vendor website and user's video are NOT included. No external browsing tool is available to the Sol dispatcher: only these supplied public-safe observations are accessible to the model. Any new path or claim proposed by Sol requires later primary-source verification.
## Priority A: code actually inspected (immutable commit + source blob)
1. ScreenerBot https://github.com/farfary/ScreenerBot/tree/9cc0b74f9136c9cc5a4fe6b806471268c9b5ce1f (BUSL-1.1 confirmed in both source headers; metadata NOASSERTION; source-available, **not conventional open source**; do not copy code or infer rights). 
- src/positions/paper/fills.rs blob b6ef60255af04bdeba751878ae89969b7f903347, read lines 1–180. Paper buy/add/sale booking demands quote evidence, token decimals and nonzero raw amount; partial vs full exits; network fee conversion and net proceeds fed into position book. Reset close-at-mark explicitly uses no quote/fee, so must never be scored as executable liquidation. Candidate improvement: evidence-tiered fills, integer accounting, refusal if bid-side quote or full-size exit unavailable, reset as administrative mark only. Falsifiers: zero amount, missing decimals, stale quote, inconsistent gas/currency, position drain, reset counted as profit, partial exit duplicate.
- src/trader/copy/paper_execution/executor.rs blob 87c5677d0e86cbba41803e7674eb1cc4b95fd6b9, read lines 1–180. Per-task FIFO; checks force stop, enabled setting, paper-mode task, risk, spend, entry plan, admission and dispatch. Skips have reason, target event signature, source timestamps, observation/detection/decode/decision clock, and backfill flag. Candidate improvement: portfolio-wide atomic reservation across tasks, point-in-time policy hash, idempotent intent and attempt census, latency/copyability denominator, no retrospective credit; not an instruction to copy wallets. Tree confirms paper book/fills/account/tests, risk_band and rugcheck modules, copy paper execution tests; contents not yet inspected beyond two files.
2. Hummingbot Gateway https://github.com/hummingbot/gateway/tree/f23e91670781fba75eb023edecaf2d992f0918aa metadata Apache-2.0.
- src/services/quote-cache.ts blob 05bf1ba8cdc4f14fdb1c081418aba02a2e2021b9, 1–180 requested. In-memory singleton Map keyed by quote id, holds quote and request objects, lookup/delete/clear/size. This module itself does not show TTL, capacity limit, actor binding or strict typed payload; other routes may supply checks, so no whole-system vulnerability assertion. Candidate improvement: typed expiring quote, chain/token/pool/raw quantity binding, immutable quote digest, policy/actor scope, single consumption, bounded cache, restart and duplicate tests. Tree confirms separate quote/execute routes for 0x/Jupiter/Uniswap and extensive connector tests. Official connector docs https://hummingbot.org/gateway/connectors/ describe router/AMM/CLMM schema. No chain coverage extrapolation.
3. Freqtrade https://github.com/freqtrade/freqtrade/tree/56a3326fa7a2850a57e0548c210247334be31e82 metadata GPL-3.0.
- freqtrade/wallets.py blob 36c75d574927f455cc1287336cac506e38afbc24, read lines 1–180. Dry wallet rebuilt from starting stake, profits, open trades, reservations/pending orders. Absent balances return zero in shown getters; our unavailable external data must remain UNKNOWN. Study reconciliation and separate available/used balance, avoid inherited float precision and unknown/zero conflation. Tests: concurrent reservations, partial order/cancel, rounding, absent provider, replay equality. Existing archive already prioritizes temporal-integrity and recursive analysis, do not duplicate. Public docs https://www.freqtrade.io/en/latest/lookahead-analysis/ and https://github.com/freqtrade/freqtrade/blob/develop/docs/recursive-analysis.md explain those probes; moving docs not immutable evidence of current source behavior.
4. Coinbase AgentKit https://github.com/coinbase/agentkit/tree/f2f3e8c11a91d56a17979a229a172ba6e61a85c2 metadata NOASSERTION (license terms pending).
- python/coinbase-agentkit/coinbase_agentkit/wallet_providers/wallet_provider.py blob 8bca206a63899f58228a6a2b90c3f1661f7f73f7, read lines 1–180. Abstract wallet interface includes address/network/balance plus message signing and transfer, and metaclass initialization calls analytics with wallet address, network identifiers and provider name. Candidate improvement: split read-only adapter from transaction-intent and independent signer interfaces, no wallet identifiers to analytics without explicit authority, no signer in model or paper mode; test telemetry exfiltration and tool capability separation. This is an observed source path, not proof of actual network telemetry behavior. No wallet integration or transfer approval.
## Priority B: pinned repo/docs/tree candidates, not function-level verification yet
- NautilusTrader https://github.com/nautechsystems/nautilus_trader/tree/364254fb77046747926bd4314631ffb38195457a (LGPL-3.0 metadata): event replay, configurable latency/fill semantics and research/live parity concepts. Public design docs https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/backtesting/execution-flow.md and https://github.com/nautechsystems/nautilus_trader/blob/develop/crates/backtest/README.md studied at document level. Investigate deterministic event ordering, fill models, event IDs, reconciliation, restart. Existing September audit explicitly defers engine adoption.
- Hummingbot API https://github.com/hummingbot/hummingbot-api/tree/a0e714ac6ce6b90c8c9a116e9e0b6eb2d1a23614 MIT metadata; Hummingbot Dashboard https://github.com/hummingbot/dashboard/tree/ee42595bec85518eda0b9fe1a56046d09a3e36c6 Apache-2.0 metadata. Study read vs execute routes, authentication, process health, bot status, structured tasks. Official router docs https://hummingbot.org/hummingbot-api/routers/; no implementation security claims.
- rotki https://github.com/rotki/rotki/tree/0e2caf6decb4192a7da392da0b00e9794b23bf92 AGPL-3.0 metadata, self-hosted private portfolio/tax data concept; separate wallet valuation, unknowns, transaction history and privacy, no code import.
- FreqUI https://github.com/freqtrade/frequi/tree/ba9f272efe8cf42ed8bff33d382a2c26d015af2c GPL-3.0 metadata, Jesse https://github.com/jesse-ai/jesse/tree/ddb5a66183bea4da824492dc4ebaae1125856fde MIT metadata: strategy comparison, positions, drilldown, risk, mobile UX. Source-level mapping and test review pending; UI inspiration only.
- Lightweight Charts https://github.com/tradingview/lightweight-charts/tree/c29c51e1e5bc61981da5832c97797cb8283d120f Apache-2.0 metadata: chart UI library candidate only; no TradingView data extraction/MCP. Preserve existing blue forecast/green actual separation and gaps; inspect attribution, mobile rendering, time series handling, licensing before adoption.
- Existing AUTO_TRADING September audit covers Nautilus Agents typed proposal/decision/receipt, Condor (principles only, runtime rejected), RD-Agent (negative benchmark), Freqtrade leakage tests, arch statistical tests, VectorBT later. Do not reopen prohibited/rejected runtime or add modules before proven need.
## Product concept GC
https://youneedagc.com public-facing idea: chat-oriented specialist handoffs and bounded risk UX; earlier direct fetch unavailable. No verified source code; no copying branding, CSS, private sessions or hidden endpoints. Treat claimed features and costs as unverified. Study product interaction pattern independently. 
## License boundary
Metadata does not establish exact file/license compatibility. BUSL and NOASSERTION are hard no-copy; GPL/AGPL/LGPL and Apache/MIT require exact revision license, notices, dependency/usage obligations, distribution/SaaS implications and independent review. Use clean-room design by default. No third-party bytes in deliverable except references and original paraphrases. No dependency installation, real trades, wallet, secrets or private provider data.
````

## A3. FULL FILE `04_RESEARCH_LAB/auto_trading/navigator_one/README.md` (blob ef1737751082d1989200d12797f7b11e8a3ea7f6, sha256 41055b92ce1522417f601865e59fecc57d1557446129ce2af2458c3991a40633, 14 lines, 2089 bytes). WP: WP1. Navigator One seed.

````
# NAVIGATOR ONE | Trading & Portfolio OS
2026-11-18 | DESIGN_SEED / RESEARCH_ONLY | no production authority
Working name only; branding/domain/trademark clearance pending. One product surface, not a second framework or scanner. Existing AUTO_TRADING owner remains #885; portfolio #1133; Alpha Lab portal #228 in Meme-Alpha-Lab; source specialist queue #1512 and reverse engineering #937 in Archive. No duplicate schedules, source streams, ledger writers or strategy search.
Claude inspiration note verified at Bridge commit 5aeeae65816b540c21b74f16d153e53b8b0df787, NOTE.md. This is a product-design extension, not a replacement for that note. The private note's contents and owner's recording are not copied here.
## Index
- research/GC_AND_OPEN_SOURCE_REVIEW.md : public product patterns and code reference audit
- design/PRODUCT_AND_UX.md : original app concept and navigation
- architecture/INTEGRATION_AND_RISK.md : data contracts, authority and failure modes
- research/PAPER_AND_EDGE_PROTOCOL.md : falsifiable simulation and experimental comparisons
- handoff/BUILD_ROADMAP.md : S1/Claude/Astra work sequence and release gates
- handoff/MISSION.json : machine-readable discoverability (not dispatch)
Future folders when meaningful: design/mockups, frontend, backend/adapters, schemas, simulation, security, testing, deployment, operations, evidence, decisions. Executable app code should eventually be in a separately approved private application repository; this public folder holds public-safe plans, contracts, source links and receipts, not balances or orders. Avoid placeholders and folder bloat.
## Authority
Read AGENTS.md, existing AUTO_TRADING README and governance, canonical data owner routes and latest source receipts. Current observed functionality must be tested, not inferred from a README. No live trade, funds, signing, credentials, paid dispatch, new scheduler, Round 3 scoring, changes to S1 or production routing. No new strategy approval. Current app seed does not require all integrated systems to be operational for documents only; executable work is gated.
````

## A4. FULL FILE `04_RESEARCH_LAB/auto_trading/navigator_one/architecture/INTEGRATION_AND_RISK.md` (blob e2c29e313c7eee40d42a1cdaaa5a86312e42040c, sha256 30a668437d7709f9f70bba10b84aa2e733b455ef7fe2849bd8a11627b37796ff, 14 lines, 3325 bytes). WP: WP1,WP4,WP6. design seed: integration and risk.

````
# Integration architecture v0.1 (design only)
Existing canonical framework -> read adapters for Cycle Navigator frozen forecast/current Kompas/regime/risk. Meme Alpha Lab -> exact-CA candidate snapshots, DVL review, scanner receipt, existing paper v4 and Strategy Arena. Portfolio #1133 -> private read-only portfolio. Existing scientific owner #885 and source #937/#1512 -> frozen outcomes and qualification. App backend aggregates references, never writes upstream canonical truths or invents state. Existing site and Alpha portal are separate views of their own producers; avoid scraping frontends and duplicate algorithms. S1 = engineering/reliability/governance supervisor, NOT a wallet/trade agent.
## Proposed components
React/TypeScript PWA; Python FastAPI or existing compatible gateway (choose after adapter audit), small read model PostgreSQL with append-only event journal, WebSocket/SSE for updates if needed, immutable source references. Private deployment and auth; GitHub Actions remains research/CI not latency-critical trading runtime. Public site contains only public-safe projections. Restricted data on approved private plane, credentials on separate approved secret manager. Never store secrets in browser, repository, prompts or logs.
## Typed design handoff
EvidenceRef {producer, immutable_ref, source_contract, observed_at, available_at, expires_at, quality, visibility, hash}
Candidate {chain_id, ca, pool_id, evidence_refs, verification_state, sellability, strategy_id}
TradeIntent {intent_id, candidate_ref, policy_version, strategy_version, market_snapshot_id, mode:PAPER, quote_ref, max_notional, min_received, expiry, reason, idempotency_key}
DecisionReceipt {intent_id, status:ALLOW_PAPER|REFUSE|UNKNOWN, reason_codes, evidence_refs, policy_hash, created_at}
ExecutionReceipt {intent_id, mode:PAPER, fills, costs, balance_delta, clock, status, reconciliation_ref}
No production schema established. All amount arithmetic decimal/atomic units. IDs and source timestamps immutable. Dedup by chain+CA+pool and unique intent key, reject replay, expired quote, mismatched network or insufficient evidence. Separate mark-to-market and executable liquidation value.
## Safety and threat model
LLM is untrusted adviser; source text is untrusted data, not instructions. Deterministic independent policy evaluates intent, never arbitrary model tool call. Paper adapter has no network write permission; no credential/signer scope. Future live proposal requires a separate approval, audit, explicit owner signature, private runtime identity and reconciliation. No leverage/withdrawals/key import in MVP. Future signing design must separate master key and model; cap per order/day/strategy, reserve gas, allowance scope, route/token allowlist, nonce/idempotency, slippage/price impact, deadline, MEV, chain reorg/finality, emergency kill switch and restart reconciliation. Separate recovery authority. Reject malicious token symbols, prompt injection, spoofed CA, duplicate fill, stale data, fake sellability, rate limits, compromised dependency and partial fill. Emergency stop blocks new intents; any future cancel/unwind policy separate and explicit.
No change to canonical framework action semantics, S1 gates, Round 3, budget, or private data policy. Existing owners must sign off on data contracts. 
````

## A5. FULL FILE `04_RESEARCH_LAB/auto_trading/navigator_one/design/PRODUCT_AND_UX.md` (blob 768294fe40fdcc30493c3cfdb794ba7cb17936e5, sha256 c9733876b8cae03fb1a3ff0d86c8f7ba5450ae0f2e87edec97b6249f9c94b434, 12 lines, 2863 bytes). WP: WP1. design seed: product and UX.

````
# Product design v0.1 | working concept
Mobile-first private PWA, desktop research workspace; original visual language: midnight navy, neutral surfaces, blue forecast, green observed, restrained risk colors, high contrast, no hype, 390/430px responsive. Separate public CN site and Alpha Lab Pro portal remain owned by their respective producers; app consumes their approved backend outputs, not screenshots/HTML scraping.
## Five main tabs
TODAY: market phase, risk/pullback, weekly freeze vs current Kompas, one prioritized action queue and fresh/stale source labels. Swipe/expand for 12h/1-3d/5-7d/2-3w where canonical output exists. No invented horizons.
ALPHA: exact chain + CA search, candidates, Watch, Pre-buy, rejected, source/microcap range filters, cohort/holder concentration, sellability, quote, case history. Link to Alpha Lab #228 portal; do not launch another scanner. New candidates never default to qualified.
DESK: conversational assistant with structured cards: Scout (find), Analyst (verify), Compass (market context), Risk (size/refuse), Execution (paper intent), Reviewer (reconcile). Roles are projections/adapters to existing owners, not necessarily separate LLM calls or recurring agents. User can ask "what changed", "why rejected", "show counterargument", "simulate $50", "compare exits". Buttons Watch / Research / Paper proposal / Dismiss. No live button in MVP.
PORTFOLIO: read-only private wallet view; cost, exposure, allocation, open positions, risk, net liquidation value, invalid/missing values explicitly UNKNOWN. Paper wallets in clearly separate mode. No private user data in public app/assets.
LAB: existing Strategy Arena, comparison, replay, costs, missed candidates, accuracy, evidence, run freshness and model disagreement. Show losing strategies and refusal outcomes as prominently as winners.
## Interaction rules
A card contains asset identity, horizon, provenance, evidence timestamp/expiry, scenario invalidation, net simulated economics, risk veto and reason, confidence status (not fabricated probability), link to original case and paper evidence. User can inspect readback and cancel an unsubmitted intent. Stale or conflicting source = visibly disabled action. Notifications material/deduped, no casino UX, no false precision. Settings: mode, paper capital, per-strategy budgets, exposure, data/AI spend, quiet notifications.
## Example (illustrative, not live)
Market: defensive; alpha opportunity: hypothetical token X; research complete but quote unverified; Risk: WATCH, blocked on sellability. Paper proposal disabled until valid quote. Details: original observation vs subsequent outcome shown on distinct clocks. App explains why a compelling token can remain non-actionable in a particular regime; any allowed microcap strategy must be independently qualified, not inherit a global buy/sell decision.
````

## A6. FULL FILE `04_RESEARCH_LAB/auto_trading/navigator_one/handoff/BUILD_ROADMAP.md` (blob c9b751b7825cb6a06279962a52d672333332c4fe, sha256 0f951675a008de789cad33a2954351864bc7c274cbbac11465d74eb12a9d259f, 10 lines, 2594 bytes). WP: WP1. design seed: roadmap.

````
# Joint S1 / Claude / Astra handover
Status: DESIGN_SEED; no runtime dispatch. Future expensive models require qualified available official route, budget, current owner authorization and receipts. Astra 6.2 and Fable are requested design roles, not verified model/API availability or auto-selection. No parallel recurring agents.
0 NOW: archive inspiration and open-source first-pass; one reviewed docs PR, link existing owners. Avoid disturbing S1/Kompas restoration or Alpha portal work.
1 Readiness: S1 checks existing #1156, #1827/#1553, #1596, #1133, #885, #1557, Alpha #228/#194/#77/#88/#120/#124/#126 and actual current PR/run receipts. Identify overlaps and data contracts; don't call health PASS without native run/readback. Alpha portal and current CN/Kompas source connections first. Existing owners handle repairs in their queues. 
2 Design contest: independent Astra (architecture, source dissection, UX, component tradeoffs, build plan) and Claude Fable (adversarial design, contract/security, UX counterproposal), both review each other only after independent draft freeze. Output one reconciled spec, decision log and synthetic mockup; no code from unlicensed sources, no paid calls automatically. Ask reviewer to distinguish design confidence vs observed runtime state. 
3 Prototype: one private PWA with fixture data and read-only backend, route to existing CN and Alpha sources only after source contract tests; accessibility/mobile QA, no new market producers. Use existing issue #228 for its dashboard, do not combine releases merely for branding.
4 Shadow/paper: integrate existing paper engines and Strategy Arena only after source gates and separate approved scientific lane. Prove deterministic reconciliation and per-stream net-after-cost edge across preregistered samples. Independent security/negative tests and source outage drills.
5 Future owner decision: live manual-sign approval mode then separately admitted bounded automation if evidence and legal/security review support it. Keep signer out of model, no withdrawal access. Not authorized by this note.
## Agent handoff
S1 owns dependency dedup, prioritization, CI/readback and review routing only. Claude may extend docs/design in existing reviewed lane. Astra owner-directed research only, with source manifests and verifiable receipts. A separate reviewer must review model-generated production changes, no self-approval. Only one active high-impact build lane per existing policy; no new schedule or budget. Update mission file status through reviewed changes, no new reports if evidence already exists.
````

## A7. FULL FILE `04_RESEARCH_LAB/auto_trading/navigator_one/handoff/MISSION.json` (blob 47dca5ba3191c14576f1908209bdfddae431f1a3, sha256 6293f8de42686386d25366b182ed344936e80d8ce367b0fa5802f8e516b419d2, 35 lines, 1099 bytes). WP: WP1. design seed: mission.

````
{
  "id": "NAVIGATOR_ONE_DESIGN_SEED_V1",
  "status": "DESIGN_ONLY",
  "date": "2026-11-18",
  "authority": "NO_EXECUTION_NO_DISPATCH",
  "parent": "04_RESEARCH_LAB/auto_trading/README.md",
  "owners": {
    "scientific": "Archive#885",
    "portfolio": "Archive#1133",
    "external": "Archive#937/#1512",
    "trial_denominator": "Archive#1557",
    "alpha_portal": "Meme-Alpha-Lab#228",
    "supervisor": "Archive#1156"
  },
  "dependencies": [
    "canonical CN/Kompas source and health receipts",
    "Alpha Lab portal/source contracts",
    "existing paper strategy owners",
    "independent review"
  ],
  "roles": {
    "S1": "coordinate existing owners, no new schedule",
    "Claude": "design and red-team under existing review",
    "Astra": "owner-authorized architecture and design research only"
  },
  "permissions": {
    "live_trade": false,
    "sign": false,
    "paid_dispatch": false,
    "new_scheduler": false,
    "round3_scoring": false,
    "production_writes": false
  },
  "next": "review design seed and dedup with existing owners; no implementation before readiness"
}
````

## A8. FULL FILE `04_RESEARCH_LAB/auto_trading/navigator_one/research/GC_AND_OPEN_SOURCE_REVIEW.md` (blob 138fd81dbc2560ac5a45411630b086e7e075eb2b, sha256 ff8d24b5ee9236352a33a374d9c388bb5eb41f3b7a3854bd00185c4c7948386f, 15 lines, 4367 bytes). WP: WP1. earlier open-source review.

````
# Public inspiration and first-pass source review
2026-11-18 | research only. Evidence classes: public README/source read; vendor claim unverified; proposed design. No source imported, installed, run or security-audited.
GC https://youneedagc.com direct retrieval failed. Publicly described chat-first agent group suggests discover -> investigate -> risk budget -> trade -> follow up, quick actions, risk profiles, contract-specific cards, and a single conversation timeline. Vendor custody, fees, chain coverage, actual trade behavior and performance unverified. Clean-room only: independently specify behavior; no copied branding, code, CSS, hidden endpoints, private session material, or bypass. Private owner video remains outside public repo.
## Ranked component references (not vendor endorsements)
1. Hummingbot Gateway https://github.com/hummingbot/gateway : README https://raw.githubusercontent.com/hummingbot/gateway/main/README.md inspected; modular router/AMM/CLMM interfaces, OpenAPI, chain/connector separation. Proposed read-only quote adapter, explicit chain + pool identity, expiry and quote correlation. Never expose wallet endpoints to LLM. Verify chain-specific coverage, especially Robinhood; no implied support.
2. Freqtrade https://github.com/freqtrade/freqtrade : raw code https://raw.githubusercontent.com/freqtrade/freqtrade/develop/freqtrade/wallets.py inspected Wallets._update_dry: cash, committed stake and realized PnL derive from trades; missing balances may return 0, which we must not inherit for unknown. https://raw.githubusercontent.com/freqtrade/freqtrade/develop/freqtrade/optimize/backtesting.py inspected dry-run configuration and separate signal/rejected/exit accounting. Adapt concepts only; candle fills aren't adequate for microcaps. Existing AUTO_TRADING audit already covers look-ahead/recursive analysis: link rather than redo.
3. ScreenerBot https://github.com/farfary/ScreenerBot : public GitHub README describes Solana scanning, filters, quote routing, paper mode, wallet-copy and AI chat. Raw README fetch failed; no line-by-line code verified. Candidate for later pinned source dissection, not trusted installed software. Prioritize pipeline interfaces, refusal tracking, and paper exit realism; no key import or direct copytrading.
4. Hummingbot API https://github.com/hummingbot/hummingbot-api and dashboard https://github.com/hummingbot/dashboard : API README https://raw.githubusercontent.com/hummingbot/hummingbot-api/main/README.md directly inspected, explicitly warns about AI access to real orders and public ports. Adopt split read/intent/execute boundaries and private network, not runtime or credential permission.
5. NautilusTrader https://github.com/nautechsystems/nautilus_trader : repository overview inspected; deterministic event-driven engine, candidate for event replay and fill semantics only. Raw fill file fetch failed; defer engine adoption as previous AUTO_TRADING audit recommends.
6. FreqUI https://github.com/freqtrade/frequi and Jesse https://github.com/jesse-ai/jesse : repo overviews inspected, for positions, strategy dashboards, backtest investigation and drilldowns. Not strategy authority.
7. rotki https://github.com/rotki/rotki : portfolio/privacy design, read-only connector concept; not execution or tax source of truth.
8. Lightweight Charts https://github.com/tradingview/lightweight-charts : library overview inspected; chart library only, not restricted TradingView MCP/data extraction (already rejected). Validate attribution and licensing.
9. Condor https://github.com/centtient/condor : agent management/portfolio interaction benchmark; already rejected as runtime in existing AUTO_TRADING audit, so no duplicate adoption. No direct signing tool.
## Next source audit
Reuse OPEN_SOURCE_TRADING_STACK_LANDSCAPE_2026-09-12.md and EXTERNAL_ARCHITECTURE_AUDIT_2026-09-12__SECOND_PASS_DECISION.md. Pin each source commit and LICENSE, produce path/symbol manifest, check dependencies, vulnerabilities and maintenance; map tests to existing owners. Prioritize NEW GC-like UX + ScreenerBot, Hummingbot quote boundary and paper microcap fill failure. No source copy until license obligations (GPL, AGPL, Apache notices, attribution etc.) independently verified for exact revisions. Use clean-room specifications where uncertain. No claim of trading edge from code availability.
````

## A9. FULL FILE `04_RESEARCH_LAB/auto_trading/navigator_one/research/PAPER_AND_EDGE_PROTOCOL.md` (blob a512b74fd138f634b0719e4ff7cbdb3d7e8f92a8, sha256 990aa1cd4df396ec3440b15f9611fe427434573ddc9f1beb714dd5c3e759910e, 6 lines, 1975 bytes). WP: WP2,WP6. paper/edge protocol seed.

````
# Paper wallet and edge protocol v0.1
Reuse Meme Alpha Lab v4 frictionless diagnostic / scientific unit ledger / execution shadow distinction and existing AUTO_TRADING #885, #1557, #937. Reuse EDGE_LEDGER_v1; no competing authoritative ledger. App displays separate paper portfolios funded with identical synthetic capital for strategy comparison: long horizon BTC/ETH, swing, rotation, microcap selective, high-risk experimental; matched buy/hold and no-trade controls; profiles conceptual, not approved strategies. No live money, exchange key or signer.
## Fidelity
Point-in-time exact token + pool, quote both ways, latency, gas, fees, taxes, size/impact, route availability, transfer restrictions, partial fills and failures, pool drain, liquidity and censoring. Simulated orders record intent, quote, virtual fills and reconciliation; never label paper balance a real wallet. No retroactive cherry-picking or zero-cost assumption. A quote is not fill guarantee. Use forward event clock and public-safe evidence; no restricted data in public artifacts. Unknown outcomes stay unknown; retain misses, rejected candidates and no-trade outcomes.
## Tests and promotion
Compare same opportunity sets: alpha-only vs market-conditioned vs risk-only vs fixed baseline; one-agent vs typed specialist adapters; matched costs and timing; freeze hypothesis and endpoints, count all trials, holdout/walk-forward, measure net expectancy, realized fill rate, drawdown, tail loss, capital utilization, opportunity cost, turnover, source coverage, calibration (where applicable), operational latency and cost. Track missed/wrong decisions without selective exclusions. Require sufficient pre-registered N / maturity and independent review under current gates; no invented pass thresholds. Test kill switch, restart replay, duplicate receipts, stale/unknown evidence, invalid exits, privacy leakage and mobile renders before MVP acceptance. No Round 3 scoring and no automatic promotion. 
````

## A10. EXCERPT `04_RESEARCH_LAB/auto_trading/OPEN_SOURCE_TRADING_STACK_LANDSCAPE_2026-09-12.md` (blob b6e33a0e4e470732e6e0900eb461f9265a9f4ef1, sha256 of full file ff5e84ea93753133a93290cefb1481d17ab417fd705311d356a276783b03f609) lines 1-18 of 232. WP: WP1. earlier AUTO_TRADING landscape: decision frame and principles; the per-repo shortlist (lines 19-165) omitted, A2 is the current pinned census.

````
# OPEN-SOURCE AUTONOMOUS TRADING STACK LANDSCAPE — 2026-09-12

Status: RESEARCH QUEUE / NON-CANONICAL / NO EXECUTION AUTHORITY
Owner: Investering Framework Research Lab
Purpose: preserve high-value external repositories for later Astra/Cowork source-code-level research without prematurely adopting or installing them.

## Decision frame

These repositories are not approved components. They are research targets.

The framework should prefer:

`Astra/research intelligence -> explicit hypothesis -> cheap screening -> point-in-time validation -> deterministic event-driven simulation -> frozen forward/shadow -> independent risk gate -> execution adapter`

Do not collapse research, validation and execution into one LLM-controlled system.

## Priority shortlist

````

## A10. EXCERPT `04_RESEARCH_LAB/auto_trading/OPEN_SOURCE_TRADING_STACK_LANDSCAPE_2026-09-12.md` (blob b6e33a0e4e470732e6e0900eb461f9265a9f4ef1, sha256 of full file ff5e84ea93753133a93290cefb1481d17ab417fd705311d356a276783b03f609) lines 166-231 of 232. WP: WP1. earlier AUTO_TRADING landscape: decision frame and principles; the per-repo shortlist (lines 19-165) omitted, A2 is the current pinned census.

````
## Current architecture hypothesis to test

A promising future split is:

1. **Astra / Agents API / internal orchestrator** — research planning, hypothesis generation, specialist delegation, bounded tool routing.
2. **Existing Framework data + Research Lab** — point-in-time evidence, regime state, governance, F12, provenance.
3. **VectorBT-like lane** — cheap broad discovery and parameter-space rejection.
4. **NautilusTrader-like lane** — deterministic event-driven simulation and execution-realism testing.
5. **Shadow / frozen-forward layer** — prospective evidence before any capital authority.
6. **Independent risk governor** — machine-checkable vetoes outside the proposing model.
7. **Execution adapter** — future explicitly approved deterministic venue interface, potentially inspired by NautilusTrader or Hummingbot.
8. **TradingView MCP** — optional research/visual/Pine adapter only.

This is a hypothesis, not a design decision.

## Cross-repository principles worth reverse-engineering

Prioritize research on:
- proposal/decision/receipt protocols;
- point-in-time observation contracts;
- deterministic simulation semantics;
- same-code backtest/live parity and where it still breaks;
- event-time correctness and clock ownership;
- order-book / latency / fill modelling;
- paper/shadow-forward modes;
- multiple-testing and search-bias controls;
- independent validation separate from strategy generation;
- external kill switches that do not trust the agent's own claim;
- credential isolation and least privilege;
- exchange connector abstraction;
- replayable artifacts and immutable experiment records;
- bounded agent tool permissions;
- failure receipts and explicit rejected/no-action states.

## Research sequence

Do not install all candidates.

Recommended order:

`repository/docs audit -> capability/overlap matrix -> source-code boundary audit -> threat/authority model -> reproducibility test -> minimal sandbox benchmark -> compare against existing owner -> retain principle / benchmark / component candidate / reject`

The first deep source-code comparison should likely cover:

1. NautilusTrader + Nautilus Agents
2. Microsoft RD-Agent (+ Qlib where relevant)
3. Hummingbot + Condor
4. VectorBT as cheap-screening accelerator

## Mandatory evaluation labels

Every external project should end in exactly one of:

- `BORROW_PRINCIPLE`
- `BENCHMARK`
- `POTENTIAL_COMPONENT`
- `REJECT`

No project becomes a framework owner merely because it is mature, popular or technically impressive.

## No-duplicate rule

Before importing data, strategy logic, connectors or research outputs, compare against existing Framework owners and archives. Prefer reuse of existing data and owners. External tools should fill a proven capability gap rather than recreate Data Ping, Cycle Navigator, Research Lab, Shadow, F12, forecast/accountability or existing historical archives.

## Future Astra handoff

````

## A11. EXCERPT `04_RESEARCH_LAB/auto_trading/EXTERNAL_ARCHITECTURE_AUDIT_2026-09-12__SECOND_PASS_DECISION.md` (blob 3716cdff6e15954d7cea6826cfd128ba06b630a3, sha256 of full file ccd413f7a7cb66688d41300c2983f385bc03e5a1031dff73d0af17edf864f6a9) lines 1-99 of 290. WP: WP1. earlier second-pass audit decision.

````
# EXTERNAL ARCHITECTURE AUDIT — SECOND-PASS DECISION

Date: 2026-09-12
Status: `RESEARCH_ONLY / NON-EXECUTION / PRIORITIZATION_DECISION`
Owner: `04_RESEARCH_LAB/auto_trading/`
External audit snapshot: `39740dd390f58b47ce99fe0a8f861ef7dd12f4cd`
Current main reviewed in second pass: `b5d6d9d645d14453186336c6ce5c0c5dd3d3ff49`
Source audit file SHA-256: `8a479ca113388f99c480967f235badf10cafc2df3dd2cf229af3f3905dbf551a`

## Purpose

Record the framework-native decision after reviewing the independent Cowork architecture audit against the current repository state.

This file does not grant execution authority and does not create a new engine. It changes research priority, closes one rejected adapter lane, and makes empirical validation the next binding objective.

## Second-pass verdict

The independent audit materially improves the roadmap and is accepted as the strongest external architecture review of AUTO_TRADING to date.

The core conclusion is adopted:

> The current architecture is not primarily constrained by missing orchestration or execution infrastructure. It is constrained by insufficient executed, falsifiable strategy research and by missing mechanical protections around historical testing.

The framework should therefore spend the next marginal unit of effort on **evidence production and falsification**, not on additional agent roles, execution engines or governance prose.

### Important snapshot correction

The audit inspected repository snapshot `39740dd3`. Current `main` is already 23 commits ahead of that snapshot and now contains active experiment-lifecycle dispatch/observation artifacts outside this AUTO_TRADING ledger.

Therefore the audit sentence "nothing has been run" must be scoped precisely:

- **Verified current fact:** `04_RESEARCH_LAB/auto_trading/THEORY_LEDGER.md` still contains 22 hypotheses and none is marked as having completed a strategy test.
- **Not adopted as a repo-wide current claim:** the broader repository now contains live experiment-lifecycle activity.

This distinction does not weaken the audit's main AUTO_TRADING prioritization conclusion.

## Adopted findings

### A1 — Empirical work now outranks new architecture work

No new autonomous-trading engine, signer, matching engine, swarm or desktop adapter should be built before the first P0 evidence tasks below are complete.

### A2 — Trial count `N` becomes a first-class research object

AUTO_TRADING must eventually have one immutable, monotonic hypothesis-attempt counter incremented at proposal time, including failed/abandoned implementations.

This is a prerequisite for defensible multiple-testing control under high-throughput Astra research.

The counter must not be reset because a strategy family changes, an implementation fails, or a candidate is discarded before reporting.

### A3 — Mechanical leakage tests move ahead of statistical sophistication

Two property tests are promoted to P0 research:

1. right-truncation invariance — values available at time `t` must not change when observations after `t` are appended;
2. left-truncation / warm-up convergence — recursive indicators must publish convergence error versus declared startup history.

A statistical correction cannot repair a feature that was computed with future information.

### A4 — Historical backfill is primarily a falsification asset

Longer free history should be acquired before broad strategy mining, but historical success alone is not sufficient promotion evidence.

Framework wording adopted for promotion governance:

> Historical evidence may falsify, rank and stress-test candidates. Historical success does not by itself authorize promotion. Promotion-strength evidence must ultimately include sealed prospective/frozen-forward observations generated after the research specification is frozen.

This is deliberately more precise than treating "history can only kill" as a universal epistemic statement.

### A5 — Sharpe precision is calendar-time constrained

The audit's zero-edge iid baseline is mathematically sound:

`SE(annualised Sharpe) ≈ 1 / sqrt(calendar years)`

so increasing bar frequency does not create independent calendar-time evidence.

Use this identity as a **baseline planning approximation**, not as a universal estimator. Real strategy-return autocorrelation, non-stationarity, overlapping positions and regime segmentation must inflate uncertainty where applicable.

Independent second-pass arithmetic reproduced the audit's key selection-hurdle examples, including approximately `2.00` annualised Sharpe for `N=1000`, `Y=6` under the stated approximation.

### A6 — Search throughput must be budgeted, not maximized

Astra should not be optimized for hypotheses/hour.

Target metric:

`reproducible surviving research / unit of compute and calendar evidence`

Astra hypothesis generation remains valuable for research design, coding and failure analysis, but broad strategy mining is blocked until trial accounting and multiplicity controls exist.

### A7 — Event-driven execution engine is deferred

NautilusTrader remains a valuable future benchmark/component candidate, especially for reconciliation, typed event semantics, funding and venue lifecycle modelling.

It is not a P0 dependency for bar-level AUTO_TRADING research.

Adoption should be reconsidered only after data granularity and strategy frequency make the additional execution fidelity observable and decision-relevant.

````

## B1. EXCERPT `00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md` (blob c8ead1b0e92c32eef4a911ad1b6bf33a09170966, sha256 of full file b9050873169d2a44e1f0d50f28292a367989eeb46d8b0d0b15850c61bdf1b00f) lines 1-101 of 166. WP: WP2,WP7,WP8,WP9(L07). cross-repo data boundary; Round 3 firewall.

````
# Cross-repository data boundary

Status: `CANONICAL_CROSS_REPO_ROUTING_AUTHORITY`  
Effective: `2026-08-23`  
Scope: agent context, source provenance, restricted market data, credentials, Round 3 collection and cross-repository automation  
Machine map: `00_ARCHIVE_CONTROL/CROSS_REPO_AGENT_CONTEXT_MAP.json`

## Authority and precedence

This file is the public routing authority for the three-plane architecture. It overrides older statements that assume all framework data is held in one repository, that a private destination is still absent, or that `Donh91/Cycle-navigator-` is a current repository route.

It does not change any market rule, source contract, threshold, weight, portfolio rule, Master Monday semantic, Cycle Navigator semantic or frozen Round 3 research commitment. Historical receipts remain historical evidence and are not rewritten.

## Three-plane architecture

| Plane | Authority | May contain | Must not contain |
|---|---|---|---|
| Control plane | `Donh91/Investering-Framework-Archive-v1` | canonical framework state, code, contracts, schemas, governance, research decisions, source-contract IDs, provider-value-free provenance receipts, health status, agent instructions and cross-repository pointers | raw or normalized restricted provider values, credentials |
| Restricted data plane | `Donh91/secrets` | raw/restricted provider payloads, private normalized market data, immutable capture receipts, restricted source-health evidence and private object-store manifests | canonical framework decisions, public market-rule authority, credentials committed as files |
| Credential plane | GitHub Actions Secrets or an explicitly approved runtime secret manager/short-lived workload identity | API keys, tokens, passwords and deployment credentials | ordinary files in either repository, logs, receipts or issue/PR text |

`Donh91/secrets` is a restricted data repository. Its name does not make it a password or credential repository.

## Mandatory read order

Any new ChatGPT Work thread, Claude/Cowork session, Codex task, agent, skill, research controller or automation that may touch source data must:

1. read `Donh91/Investering-Framework-Archive-v1/AGENTS.md`;
2. read the control-plane canonical index, addendum registry, archive map and this file;
3. read `00_ARCHIVE_CONTROL/CROSS_REPO_AGENT_CONTEXT_MAP.json` and the current domain contract/status pointer;
4. determine whether the requested evidence class is public metadata or restricted provider data;
5. if restricted data is required and access is authorized, read `Donh91/secrets/AGENTS.md`, `README.md`, `GOVERNANCE/CROSS_REPO_DATA_BOUNDARY.md`, `GOVERNANCE/PRIVATE_DATA_BOUNDARY.md` and the exact private binding/health record;
6. bind all conclusions to immutable commits and exact paths, never merely to either repository's moving `main`;
7. stop with `PRIVATE_DATA_AUTHORITY_UNAVAILABLE` when restricted evidence is necessary but cannot be read.

Public-only work may stop after step 4. Lack of access to the restricted plane is not permission to infer values, search for them in the public repository or substitute public proxies.

## Data classification and movement

Allowed from restricted to public:

- private repository name;
- immutable private commit SHA;
- exact private receipt or dataset path;
- byte length and SHA-256;
- source-contract ID and schema identifier/version;
- capture, retrieval, availability and normalization timestamps;
- row or object counts, timestamp ranges, gap counts, completeness class and provider-value-free source health;
- public research decisions made only after the relevant analysis gate is opened.

Forbidden from restricted to public:

- raw payload bodies;
- order-book levels, prices, sizes, funding values, open interest, volatility values or other provider-derived market values;
- samples, excerpts, reconstructed values or small aggregates that disclose restricted values;
- object-store credentials, signed URLs, access tokens or sensitive storage coordinates;
- unredacted logs or exception text that contains provider values or credentials.

Movement from public to restricted may include contracts, schemas, collector code and immutable control-plane commit identifiers. It does not transfer canonical decision authority to the restricted repository.

## Required private dataset binding

Every private dataset or immutable capture used by an agent must be bound by one restricted-plane receipt containing, at minimum:

```text
private_repository
private_commit_sha_reachable_from_main
exact_path
bytes
sha256
source_contract_id
provider / venue / instrument_id
collector_commit_sha
schema_id / schema_version / schema_sha256
retrieval_start_utc / retrieval_end_utc
availability_at_utc / captured_at_utc / normalized_at_utc when applicable
row_or_object_count
timestamp_range
gap_count and missingness/completeness status
validation_status
```

When the raw payload is stored in private object/blob storage, the exact object key, immutable object version, storage checksum and retention state live in the private manifest. The public receipt binds to the private commit and exact manifest path, plus its bytes and SHA-256. Public pointers must remain provider-value-free.

Mutable branch names, workflow artifact URLs and latest-file names alone are not provenance.

## Round 3 analysis firewall

Current authority remains:

- mode: `PROSPECTIVE_COLLECTION_ONLY`;
- Round 1 and Round 2: closed evidence, never reopened or rescored by Round 3;
- historical findings: maximum classification `FORWARD_TEST` after separate review;
- hypothesis testing: `OFF`;
- outcome scoring: `OFF`;
- paid historical acquisition: not authorized;
- raw provider values in the control plane: forbidden;
- collection is not evidence of effect, and source health is not an outcome row.

No agent may read Round 3 provider values for hypothesis discovery, directional interpretation, threshold selection, outcome linkage or informal scoring before the frozen analysis gate passes. A private source-health read is limited to source contract, timestamps, sequence/gap status, schema, counts and completeness.

````

## B2. EXCERPT `AGENTS.md` (blob 256f814e5da4882b8ecf887feff669742bb77d8a, sha256 of full file 2df406317940abc095e34832f5efa7041960512ef11d56f0264892a077ca5af1) lines 508-524 of 619. WP: WP2,WP5,WP7,WP9. Archive AGENTS.md section 5 prospective evidence discipline only (current blob; #2224 pinned an older blob 840e9906).

````
## 5. Prospective evidence discipline

For active forward tests and ledgers:

- the target test must exist in the Active Test Registry;
- the owner defines the schema, horizon, benchmark, validator and scorer;
- forecasts, decisions, horizons and invalidators must be frozen before outcomes;
- frozen inputs may not be rewritten after outcomes become observable;
- source rows, initialization rows and schemas are not outcome evidence;
- incomplete horizons remain pending, not failed;
- duplicate and overlapping event-window status must be explicit;
- use existing validators and scorers rather than reproducing their logic;
- row validity, coverage readiness and promotion status must remain separate;
- a coverage gate may permit governance review but never automatic promotion.

Use `.agents/skills/prospective-evidence-ledger/SKILL.md` for prospective row creation, maturity checks, outcome attachment, lineage reconciliation and coverage validation.

````

## D1. EXCERPT `06_RESEARCH_LAB/audit_summaries/2026-11-05__kompas_pullback_altseason_independent_deep_research_intake_v1.md` (blob 4571a099688e34cceddefc318be1abd50fdb1ddb, sha256 of full file 718462a8c271a13c0207e713c0cfbf52f02d8ae101f1641e92ab3991bcfad740) lines 1-53 of 86. WP: WP3,WP5,WP9. prior Donier/Bouchaud liquidity intake.

````
# KOMPAS Pro | Independent Deep Research intake and original-owner reconciliation v1

**Date:** 2026-11-05 (Europe/Copenhagen)  
**Source:** owner-provided 15-page PDF, `KOMPAS PRO · Pullback Intelligence × Altseason Takeoff × Distribution & Exit`, research dated 2026-11-05, pp. 1-15. **The original PDF has NOT been published to this public repository.** This is a selectively paraphrased review and action crosswalk, not an independent replication of all 40 cited studies.  
**Authority:** RESEARCH_ONLY / NO_PREDICTION_PROMOTION / NO_BUY_SELL / NO_NEW_SCHEDULER / NO_NEW_MARKET_ENGINE.  
**Original owner:** #1918. Implementation/science owners #1516, #1553, #1596, #1530/#1552, #1157, #1578; S1 #1156.  
**Related MAX request:** #1918, merged dispatcher PR #1919, original native run 41949497953.

## 1. Executive verdict

**RETAIN / DESIGN CANDIDATE:** Use ONE existing canonical state/source-owner to project mutually consistent risk context to Pullback Radar and Altseason Lifecycle, but NEVER synthesize or replace official current market state from a report, shadow signal or model. Separate state projections and claims:
1. correction onset probability (only calibrated and source-admitted),
2. conditional drawdown depth quantile band,
3. time-to-trough / time-to-recovery with right censoring,
4. rebound/re-entry quality and after-cost decision analysis,
5. altseason ignition and rotation **survival**,
6. breadth/liquidity/spot-vs-derivatives **distribution** hazard.

Do not collapse these into one decorative numeric score. Explicit `UNKNOWN`, `NOT_MODELLED`, `INSUFFICIENT_INDEPENDENT_N` and stale states, including both source and forecast issue clock.

**Critical non-edge condition:** The source report recommends statistical models and candidate signals; it does **not** provide a validated Kompas-specific predictive or economic edge. PLOS One 2015 MtGox historical liquidity study and recent crypto-cross-sectional SSRN studies justify hypotheses, not live 2026 alpha. Prior studies' published results must not be reproduced as current framework validation.

## 2. Independent corrections to owner research PDF

1. **M4 is locatable, not UNKNOWN:** exact original [M4 Rotation Survival Replay, July 8 2026](../../04_MARKET_LEARNING/rotation_survival/2026-07-08__m4-rotation-survival-replay-degraded-first-pass__canonical.md) is present on `main`, source blob `d747d5017bd694b5ef5d6db06cbdcc290d6f1472` at intake. It reports 16 resolved ETH/BTC gate crosses, 13 categorized FAKE (81% pooled DESCRIPTIVE), 1 genuinely independent real-candidate episode, and unavailable BTC.D/breadth/deployment/ETF flow in that degraded run. The crossings are correlated, and the proportion cannot be promoted as a general probability. Crucially M4 already explicitly flags `EXIT_SIDE_GAP`, and ETH/BTC duration alone cannot detect when the door closes. This changes report pp. 3 and 11's M4-availability statement, not its overall caution.
2. **Shared latent regime is a design proposal, not a greenlit new producer:** report pp. 1, 6-7 propose a common `market_regime_state`. Reconcile field ownership against current official CN/Kompas structured projections before adding a schema. An unreviewed new state creator would violate the single-authority contract. Prefer a source-only, shadow projected view until product governance approves semantics.
3. **Research status is not product status:** #1516 Forward Path and #1553 contain live/pipeline/shadow distinctions; the report's pp. 2-3 issue-level characterization is time-sensitive. Require fresh main/code readback and actual natural producer/site acceptance for every asserted `IMPLEMENTED`, `LIVE` or `NOT_IMPLEMENTED` field.
4. **Academic signal ranking is not framework ranking:** report pp. 4-5 rank liquidity/volatility, breadth and leverage as promising. Incremental prediction and trade utility for this system remain UNKNOWN absent eligible same-clock ablations and independent event families.
5. **Avoid implied numeric probabilities and one-size-fits-all exit rules:** report pp. 5, 10 propose `p_onset_*`, `distribution_hazard` and two/three independent signalfamily deterioration. These are proposed data names/evidence requirements, NOT calibrated values, authorized thresholds or binding trading actions.
6. **Sol MAX side-by-side is currently blocked by TRANSPORT, not waiting for a normal answer:** original run [41949497953](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/41949497953) exhausted its one reserved paid attempt after network `RemoteDisconnected` during a synchronous Responses POST. Native exact claim [6647190305](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1476#issuecomment-6647190305), no accepted research output/response-id, actual billing UNKNOWN. Original incident disposition [#1918 comment 6647309321](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1918#issuecomment-6647309321). **No retry or new paid trigger.** Billing/transport remediation is its separate existing owner. Deep Research must not masquerade as MAX output.

## 3. Three evidence-priority experiments from PDF pp. 6-8, 11-12

### P0-A | PIT CORRECTION EVENT REGISTRY + price-only depth, duration, onset baselines
- Owners: #1596 admission, #1516 conditional paths, #1553 pullback, #1530 M6.
- Freeze first-known public data, provider/frozen/delivery clock, source hash, explicit venue/universe, event qualifying time, peak, trough, maturity and final recovery with horizon-specific censoring and a no-warning denominator.
- Independent shock families, not bars/72 repeated warnings. Keep recovered and ongoing bull periods as controls. Preserve BTC/ETH/tier episode memberships without inflating N across correlated assets.
- Score warning first lead vs fixed price/volatility/ATR threshold, PR-AUC/Brier/log loss only for admissible calibrated onset labels, pinball loss/coverage for conditional depth, time-dependent survival Brier/coverage for trough/recovery. Actual UTC delivery timing matters. Split ETF eras.
- First code delivery: add/reuse typed immutable `PIT_CORRECTION_EVENT_v1` shadow registry and deterministic price/ATR baseline plus source-clock adversarial tests through original owners. No numeric production projection.

### P0-B | ALTSEASON ROTATION SURVIVAL + BREADTH LEAD/LAG
- Owners: #1530/#1157 research admission, existing rotation and #1578 product.
- Reuse exact original M4 event/diagnostic ledger, do not rerun same degraded sample as a new result. PIT-validate BTC.D with/without stablecoin conventions, eligible historical coin universe and delisting/survivorship, cap tier measured at original issue date, ETH/BTC, cross-sectional breadth and dispersion, spot participation, available settled ETF flows and actual stablecoin deployment.
- Study ignition latency **and** false rotations, missed takeoffs and cumulative upside foregone versus ETH/BTC-only, price-only and no-allocation baselines. Keep stale breadth, overlapping tickers and one cycle as UNKNOWN.
- Do not assume fixed BTC→ETH→micro→meme order. Add `ROTATION_CANDIDATE` and `BROADENING` only as nonbinding source-owned shadow classifications at first.

### P0-C | DISTRIBUTION HAZARD, BULL TRAPS AND DECISION ECONOMICS
- Owners: EDGE-001/M6 #1530, protection #1553, RQS/rebound #1850, Forward #1516, governance #1157.
- Distinguish healthy pullbacks from terminal deterioration using breadth rollovers/failed recoveries, executable liquidity, spot-vs-leverage activity, relative strength, failed reclaim and basis/funding/OI as correlated feature **families**, not six independent votes.
- Pre-freeze index eligible denominator and slow decay states, compare hazard/exit against trailing-stop and naive trend baselines. Separate `EXISTING_HOLDER` from `NEW_CASH` and evaluate hold, early trim + reload, phased exits, delayed confirmation, DCA, first dip, and staged/reclaim entries, preserving no-action controls.
- Economic ledger needs feasible fills/size-adjusted liquidity/slippage, fees, missed upside and jurisdiction-dependent tax **sensitivity**, never pretend perfect trough fills. Future outcomes that are not matured remain censored.
- Prior M6 scope already distinguishes INFORMATION_EDGE from ACTION_EDGE; warning is not authorization to SELL.

````

## D1. EXCERPT `06_RESEARCH_LAB/audit_summaries/2026-11-05__kompas_pullback_altseason_independent_deep_research_intake_v1.md` (blob 4571a099688e34cceddefc318be1abd50fdb1ddb, sha256 of full file 718462a8c271a13c0207e713c0cfbf52f02d8ae101f1641e92ab3991bcfad740) lines 78-86 of 86. WP: WP3,WP5,WP9. prior Donier/Bouchaud liquidity intake.

````
## 7. Public source anchors, selected

- [Owner mission #1918](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1918)
- [M4 replay original](https://github.com/Donh91/Investering-Framework-Archive-v1/blob/main/04_MARKET_LEARNING/rotation_survival/2026-07-08__m4-rotation-survival-replay-degraded-first-pass__canonical.md)
- [M6/EDGE-001 preregistration](https://github.com/Donh91/Investering-Framework-Archive-v1/blob/main/06_RESEARCH_LAB/high_value_edge_research/EDGE-001_TSUNAMI/CHARTER_v1.md)
- [PLOS One, Donier/Bouchaud 2015 Bitcoin liquidity](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0139356)
- [Wang/Pang, SSRN October 2026 cross-sectional signal migration](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7556359)

**This intake is a researcher interpretation of a user-supplied PDF, with one independently verified archive correction; it does not assert an executed event registry, working model, live signal, economic edge, safe Sol retry, or changed portfolio authorization.**
````

## D2. FULL FILE `06_RESEARCH_LAB/hugging_face_task2_audit_20261022/03_TASK2_RESEARCH_PROTOCOL.md` (blob 8ee95e7d826862763bfd17fef0a54d123615e9ca, sha256 7729a968aa7ee5217ed3fb057ad11a15a73f51cc9d3ed9e43adbd984623f9f51, 53 lines, 6360 bytes). WP: WP2,WP5. mechanical baselines protocol.

````
# Phase 3 | Task 2: HF as a no-hindsight external benchmark source

**Mission:** existing COMPASS-HORIZON-EDGE-20261011 R0–R7. **Authority:** RESEARCH_ONLY. Existing Task 2 handoff owns source admission; EDGE #1530, Compass action #1553, Task1.5 #1596 retain their roles. This note adds source candidates and failure tests, not another experiment owner, scheduler, forecast framework or new threshold.

## Current repo status observed 2026-10-22
- PR #1573 (original Task 2) MERGED.
- PR #1597 historical forecast audit MERGED.
- PR #1617 source SHA verification patch CLOSED, NOT MERGED. Do not treat old PR body as current problem proof: inspect subsequent main for same defect/fix.
- PR #1675 censor-aware counts and fail-closed lifecycle MERGED (merge SHA f5f11ddeac4d01248209140efac6bb5cab43d364).
- PR #1683 Master Monday handoff integrity MERGED; separate system, don't recompute its status from chat.
- Dated gate `2026-10-13__TASK2_FULL_STACK_AUDIT_EXECUTION_GATE_v1.json` includes R0/public preflight, synthetic negative controls and historic R1 blocked. It is NOT a fresh readback of all admissibility after later PRs.
- Exact audited main branch HEAD at one preflight: b4a644faa5893bc7f33d87834d7a74a0639371dc, 2026-10-22T16:23:58Z. Re-read this on actual execution.

## R0: external source census, no source invention
For each source/series, freeze HF repo revision, blob/file SHA, split, record grain, UTC and timezone, market instrument identity, venue, publication time, historical earliest *available* snapshot proof (not only economic bar timestamp), provider source, completeness and expected cost. Use the owner's existing inventory and receipt format.

Do not conflate the dataset's **event_ts** (when an event occurred), **publish_ts** (claimed first published), **first_known_at** (our observer accepted), **ingest_ts** (later library upload), **retrieval_ts**, and **label/outcome cutoff**. Retrospective uploaded bars lack evidence of historical delivery to our system.

## R1: PIT source admissibility
For original forecast i with issue cutoff t_i:
1. Read original immutable issued forecast ID, horizon, target, issue-clock receipt, model and relevant source SHA.
2. Establish source first-known `s_i`, verify `s_i <= t_i`. Absence -> `UNKNOWN_SOURCE_TIMING`, not proof of knowledge.
3. Establish benchmark availability by decision cutoff. OHLCV `open_time <= t_i` is insufficient if that bar's `close_time > t_i`.
4. Bind labels to original outcome process, keep every censored, unknown, missing, abstained, mature and rejected record in denominator.
5. Detect split/conversion drift, time-zone errors, overlapping horizons, market venue mismatch, synthetic vs observed clock, revised metadata and event family dependence.
6. Fail closed for any original first-known/custody failure. HF revision SHA verifies today's stored file, not necessarily historical publish state.

Negative controls: deliberately inject future close within live candle, scrambled timestamps, missing original forecast, after-target received label, synthetic source flag, duplicate cluster, late provider revision and defunct symbol. Every leak must be rejected. Prove tests fail when guards are removed.

## R2: mechanical benchmarks ONLY after R1 eligible cohort
- Naive no-change, random/no-signal, prior-return momentum, ATR range with frozen window, prior-week high/low, ETH/BTC same-clock relative strength, cash/HOLD/WAIT action; exact baseline depends on pre-registered owner's domain.
- Publish all events, class base rates, coverage, calibration, MAE/MFE, Brier/log loss when suitable, WIS/Winkler for intervals, net return utility after costs/fees/slippage and false-exit/missed-upside penalties.
- For market regime/rotation, require pre-registered event definitions, asset universe as-of, all delistings and broad participation criteria before metric selection.
- Prefer matched issued forecasts, same clock/venue/horizon rather than anecdotal cherry-picking. Cluster overlapping events into independent families.
- No evaluation that uses HF model trained on the test window without embargo/walk-forward separation.

## R3–R7 conditional path
R3 source ablation: does HF external context add value after independent cheap benchmarks? R4 adversarial challenge: leakage, false alarm, undercoverage, regime change, survivorship and spoofed news. R5 action utility: holder vs cash investor, execution latency and portfolio privacy boundary. R6 site/Kompas/CN projection: all identical eligible frozen evidence; source research must not feed current site/Kompas. R7 owner-governed outcome memory, negative result and retirement decision.

### Exit criteria / metrics for pilot acceptance
- Per-provider licensed usable data, exact pinned revision, full denominator and failure-aware schema, no future feature leakage.
- Reproducible join audit with missingness and sufficient independent market families; threshold/N taken from existing owner protocol, NOT invented here.
- Failing negative controls and verified acceptance receipts.
- Material positive decision divergence under walk-forward validation relative to cheapest baseline (or honest null/negative conclusion).
- Only owner may authorize R2+ after R1 source eligibility. Zero promotional claims before that gate.

## First-pass bounded experiments
**T2-HF-PILOT-A:** Read only 2 instruments/small exact-window OHLCV from HF-001, report 15-minute bar custody and completeness versus original issue clocks without scoring. **T2-HF-PILOT-B:** HF-004 `markets` + `prices` only; filter resolution=-1, missing fee and late market creation; compare probability calibration in research lane. **T2-HF-PILOT-C:** HF-009 news timestamp/URL dedup against a sample of already archived Situation Room events, retaining published vs first-known separation.

All pilots require existing owner signoff, pinned inputs, controlled execution location. This packet authorizes only data discovery and publication of source metadata.

## Avoid acting on GitHub Actions outage
This research does not restart existing collectors or substitute HF for scheduled Actions. On the user's reported exhausted October GitHub minutes, keep research read-only and avoid large CI/Action runs; evaluate production health separately through the existing Supervisor. No fake machine uptime or re-created source timestamps.
````

## M1. EXCERPT `06_RESEARCH_LAB/astra_program_20261116/missions/06_ADAPTIVE_MEMORY_EVOLUTION_ASTRA62_MAX_PREP_ONLY.md` (blob bc83f6f0cade33f9648868f52156d51854d9ce97, sha256 of full file 46ecb24403751ed4a77fea7294b510aba31d1050315965830270e8aa5b33e09e) lines 1-7 of 36. WP: WP8. #2224 source-owned memory specification; lines 8-11 (model/pricing/ledger mandate) and 35-36 (closure mechanics) omitted.

````
# Astra 6.2 MAX — Adaptive Memory Evolution v1
Date: 2026-11-18 | Owner-authorized research queue preparation | P1, behind P0 release/production repairs
Mission ID: ASTRA62-MAX-ADAPTIVE-MEMORY-EVOLUTION-20261118-ONE
State: PREP_ONLY / NOT_DISPATCHED / NOT_BUDGET_ADMITTED
Owner: Archive #1157 scientific adjudication, #1512 intake, #1156 execution; Claude Bridge #173 independent review.
Prior completed study: ASTRA-HIGH-S1-VNEXT-ARCHITECTURE-20261116-ONE. Reuse output, do not rerun consumed ID or repeat broad supervisor architecture audit. This is a distinct memory-policy and scientific-evaluation delta, not a new system, scheduler or workflow owner.

````

## M1. EXCERPT `06_RESEARCH_LAB/astra_program_20261116/missions/06_ADAPTIVE_MEMORY_EVOLUTION_ASTRA62_MAX_PREP_ONLY.md` (blob bc83f6f0cade33f9648868f52156d51854d9ce97, sha256 of full file 46ecb24403751ed4a77fea7294b510aba31d1050315965830270e8aa5b33e09e) lines 12-34 of 36. WP: WP8. #2224 source-owned memory specification; lines 8-11 (model/pricing/ledger mandate) and 35-36 (closure mechanics) omitted.

````
## Prior evidence and source packet
Source snapshot: Archive main caa456c1a311a44a3e8b3e9650367693e100cf0c, exact Git blob references below. Re-resolve fresh main before launch; distinguish frozen prior evidence from current implementation, update manifest with SHA256/bytes/commit at preparation; no silent source substitution. Only public allowlisted sources, no restricted contents, prompts, personal data, APIs or credential text. If source inspection finds unsafe material, redact into reviewed public derivation with original pointer, or stop.
- scripts/framework_intelligence/operational_memory_v1.py @ eecedc566839f4b3367476565d10fac1ae0b4399
- 00_ARCHIVE_CONTROL/SEL_SELECTIVE_OPERATIONAL_BINDING_v1.json @ 6e4b7c59d33445b294b5a1d2e09635d06ca25834 (public binding only)
- research/framework_learning/operational_memory/LATEST_OPERATIONAL_MEMORY_STATE.json @ e056a5af81a9c90864a1558e77fabfcae601409a (historical snapshot: 3,761 active / 10,259 history, 32 candidate procedures; not utility evidence)
- 00_FMOS/S1/EVIDENCE_BINDINGS.md @ 41f19f5e652576de4125a6ef11812a73be83b477
- AGENTS.md @ 840e9906af233b1d8455e7f141a3341cc08283ac (current-source excerpt: selective memory, authority, governance, budget; copy no unrelated data)
- 06_RESEARCH_LAB/astra_program_20261116/results/s1_vnext/ASTRA_S1_VNEXT_RESEARCH.md @ d2782b4c92c20218b31ff2eef6e235a718799ca9
- prior corresponding receipt.json @ 3479897ef0089787c5baa8de2a0f897683d1eead; source_manifest.json @ 8e88a93cc74a28a4564e2433608406001f978414
- public research intake https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1512#issuecomment-6976461803
- adjudication request https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1157#issuecomment-6976470871
- Claude handoff https://github.com/Donh91/Investering-AI-Audit-Bridge/pull/173#issuecomment-6976469844
- Primary https://facebookresearch.github.io/RAM/blogs/self_improving_memory/ ; CL-Bench https://arxiv.org/abs/2606.05661 ; MemOp https://arxiv.org/abs/2606.05646 ; ACE https://arxiv.org/abs/2510.04618 ; MemCalib https://arxiv.org/abs/2609.24259 ; Evo-Memory https://arxiv.org/abs/2511.20857 ; ALMA https://openreview.net/pdf/23878e570503a3805275ae0ee052f1d263ccd018.pdf. Obtain short source-grounded evidence extracts before dispatch, with dates, version, URL and limitations; no full copyrighted text copying. Model cannot visit links in no-tools run, so supply evidence or mark absent. Verify all claims and do not assume replication.

## Research instruction to Astra (advisory only)
Conduct a rigorous adversarial architectural and scientific synthesis focused on whether the existing operational memory and selective shared-experience layer can learn better retrieval/offload policies and actually improve independently verified closure. Distinguish code-visible capability, reported health, verified runtime outcomes, proposals and unknowns. Explicitly separate memory quality from model capability; quantify causal utility, not storage volume or green CI. Audit existing telemetry, compatibility, timestamp/receipt lineage, prior S1 vNext research and current S1 evidence bindings before proposing changes. No parallel engine/registry, no self-certifying memory, no control-plane/private-boundary change.
1. Reproduce Meta method from supplied sources conceptually: selection bias, 37/44 failed revisions, train/dev/untouched test, sample independence, memory write/read policies, task-domain shift. Compare related work and strongest counterevidence.
2. Map current architecture and actual code paths for immutable episodes, hot/cold sets, relevance ranking, compatibility checks, preflight, feedback and procedure candidates; separate missing evidence from actual defect. #2157 repair-only: verify existing hot-set and natural readback; do not reopen.
3. Design minimum incremental outcome-qualified LOAD/OFFLOAD policy within existing stores: current authority first, evidence-bound recall, staleness/supersession, negative/failed memory, causal outcome append, abstention, privacy filtering, poison/injection resistance, bounded retrieval tokens. Candidate policy versioning and rollback; no automatic model training or promotion.
4. Specify point-in-time evaluation: B0 no-memory/current source, B1 exact fixed deterministic preflight, B2 outcome-qualified policy, max two challenger configurations, same model and caps; prepare 30–40 source-local temporal repair cases for feasibility not proof, grouping correlated incidents and separating development from untouched holdout. Freeze available-at, repo snapshots, oracle isolation, denominator, scoring rubric, power/sample plan, uncertainty and multiple testing before score. Primary endpoint independently verified correct closure, practical +10pp target, positive lower 95% confidence bound for promotion with adequate sample. Zero authority/provenance/privacy/false-READY/immutable-history regressions; kill on leak, poisoning, critical regression or insufficient meaningful benefit. Secondary: diagnosis repetition, false recall, missing recall, cost/latency/bytes per verified closure. Measure transfer separately, not assume market alpha.
5. Produce explicit ranked implementation-ready steps with exact owning issue, code/test surface, dependencies, bounded cost, negative fixtures, acceptance/kill criteria, fallback, and independent review checkpoints. Prefer deterministic-first, only use paid model where needed. State what can be achieved now without further paid research. Return one prioritized actionable hypothesis delta; other ideas as exploratory, not new queue items.
6. Designing extension proposals for Alpha Lab and Compass is allowed as separate future test concepts ONLY. Preserve first-seen, full denominator, after-cost realizability, immutable forecasts and current Round 3 collection-only firewall. No current market/portfolio/trading authority, no private values or scoring closed evidence.
7. Required final response: executive verdict; source register with SHA256 and uncertainty; overlap/dedup matrix with prior S1 study and active owners; minimum design or reject; pseudocode and negative tests; preregistration draft; credible resource estimate; implementation sequence; failure/misuse analysis; limitations; machine-readable action/disposition appendix. No claimed tests or runtime facts without native evidence. Challenge own recommendation.
````

## M2. FULL FILE `scripts/framework_intelligence/operational_memory_v1.py` (blob eecedc566839f4b3367476565d10fac1ae0b4399, sha256 31b880c971c3b017d266f08c0ec2ae68a0d572b9a028c84f2163abaff7c17a67, 191 lines, 16243 bytes). WP: WP8. the implemented operational memory harvester/index.

````
#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re, subprocess
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

AUTH = {"canonical_effect":False,"portfolio_execution":False,"automatic_promotion":False,"automatic_skill_activation":False,"automatic_repository_write":False}
SELF_PREFIX=("research: refresh framework learning supervisor","research: refresh operational memory")
STOP={"a","an","and","as","at","by","for","from","in","into","of","on","or","the","to","v1","v2","v3","with","without"}
ACTIONS={"fix","repair","correct","harden","hardening","close","retire","reconcile","restore","resolve","patch","prevent","build","add","implement","install","activate","extend","bind","archive","preserve","research","audit","preregister","qualify"}

def load(p,d=None):
    try:return json.loads(Path(p).read_text())
    except Exception:return d
def write(p,v,compact=False):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text((json.dumps(v,separators=(",",":"),sort_keys=True) if compact else json.dumps(v,indent=2,sort_keys=True))+"\n")
# WO-2c hot-set bound: routine automated data-writer episodes stay immutable in episodes/ (the cold
# store) but only the last HOT_WINDOW_DAYS of them are in LATEST_OPERATIONAL_MEMORY_INDEX.
# operation_type alone is too coarse (human "feat(...)"/"test(...)" PRs are typed UPDATE), so a row
# rolls off only if it is UPDATE/RESEARCH AND its subject has the automated data-writer shape
# ("<writer>: ... <Actions run id>" or a known bot phrase) AND it names no PR. Everything else is kept.
ROLLING_OPERATION_TYPES = {"UPDATE","RESEARCH"}
HOT_WINDOW_DAYS = 14
ROUTINE_SUBJECT = re.compile(r"^(learning|data|ops|ai|evidence|health|research|remediation)(\([^)]*\))?: .*\s\d{9,12}$")
ROUTINE_PHRASES = ("research: accumulate prospective","data: persist research","research: advance autonomous")
PR_REF = re.compile(r"\(#\d+\)")
def routine(row):
    s=str(row.get("task_summary","")).strip()
    if row.get("operation_type") not in ROLLING_OPERATION_TYPES or PR_REF.search(s):return False
    return ROUTINE_SUBJECT.match(s) is not None or s.lower().startswith(ROUTINE_PHRASES)
def utc_ts(s):
    try:t=datetime.fromisoformat(str(s).replace("Z","+00:00"))
    except ValueError:return None
    return t if t.tzinfo else None
def in_hot_set(row,cutoff):
    if cutoff is None or not routine(row):return True
    t=utc_ts(row.get("source_timestamp"))
    return t is None or t>=cutoff  # an unknown timestamp is kept, never silently dropped
def git(root,*args,check=True):
    r=subprocess.run(["git","-C",str(root),*args],text=True,capture_output=True)
    if check and r.returncode: raise RuntimeError(r.stderr.strip())
    return r.stdout
def head(root):return git(root,"rev-parse","HEAD").strip()
def toks(s):return [x for x in re.findall(r"[a-z0-9]+",s.lower()) if x not in STOP and len(x)>1]
def task_class(text,paths=()):
    b=(text+" "+" ".join(paths)).lower()
    if "cycle navigator" in b or "05_cycle_navigator" in b:return "CYCLE_NAVIGATOR"
    if "moonshot" in b or "meme alpha" in b:return "MEME_ALPHA"
    if "compounding learning" in b or "framework_learning" in b:return "FRAMEWORK_LEARNING"
    if "remediation" in b or "automation health" in b or "workflow" in b:return "AUTOMATION_REMEDIATION"
    if "auto_trading" in b or "auto trading" in b or "edgeonchain" in b:return "AUTO_TRADING_RESEARCH"
    if "api_agent" in b or "api agent" in b:return "API_AGENT"
    if "archive" in b or "preserve" in b or "retention" in b:return "RESEARCH_ARCHIVE"
    if "master monday" in b:return "MASTER_MONDAY"
    if "data ping" in b or "market state" in b or "handlekompas" in b:return "MARKET_STATE"
    return "GENERAL_FRAMEWORK"
def operation(s):
    s=s.lower()
    if any(x in s for x in ("fix","repair","correct","resolve","restore","reconcile","patch")):return "FIX"
    if any(x in s for x in ("harden","hardening","prevent","retire")):return "HARDEN"
    if any(x in s for x in ("build","add","implement","install","activate","extend","bind")):return "BUILD"
    if any(x in s for x in ("research","audit","preregister","qualify","adjudicat")):return "RESEARCH"
    if any(x in s for x in ("archive","preserve","retention")):return "ARCHIVE"
    return "UPDATE"
def signature(s):
    q=[x for x in toks(s) if x not in ACTIONS] or toks(s)
    return "-".join(q[:8])[:120]
def prefix(paths):
    c=Counter(Path(p).parts[0] for p in paths if Path(p).parts)
    return c.most_common(1)[0][0] if c else None
def blob(root,rev,path):
    x=git(root,"rev-parse",f"{rev}:{path}",check=False).strip()
    return x if re.fullmatch(r"[0-9a-f]{40}",x) else None
def compat(src,cur):
    if not src:return {"status":"UNKNOWN","same":0,"changed":0,"removed":0,"checked":0}
    same=changed=removed=0
    for p,o in src.items():
        n=cur.get(p)
        if n is None:removed+=1
        elif n==o:same+=1
        else:changed+=1
    n=len(src)
    st="REMOVED" if removed==n else "EXACT" if changed==0 and removed==0 else "DRIFTED" if same==0 else "PARTIAL"
    return {"status":st,"same":same,"changed":changed,"removed":removed,"checked":n}
def commits(root,n):
    raw=git(root,"log","--first-parent",f"-n{n}","--date=iso-strict","--format=%H%x1f%cI%x1f%s%x1f%b%x1e")
    out=[]
    for b in raw.split("\x1e"):
        b=b.strip("\n\r")
        if not b:continue
        p=b.split("\x1f",3)
        if len(p)==4:out.append(dict(zip(("sha","timestamp","subject","body"),[x.strip() for x in p])))
    return out
def paths(root,sha):
    return [x.strip() for x in git(root,"diff-tree","--root","--no-commit-id","--name-only","-r",sha).splitlines() if x.strip()][:60]
def episode(root,r):
    s=r["subject"]
    if not s or s.lower().startswith(SELF_PREFIX):return None
    ps=paths(root,r["sha"]);op=operation(s);src={p:blob(root,r["sha"],p) for p in ps[:25]}
    body=" ".join(x.strip() for x in r["body"].splitlines() if x.strip())[:600] or s
    return {"contract":"OPERATIONAL_EPISODE_v1","episode_id":"OE-"+r["sha"][:16],"source_kind":"MERGED_MAIN_COMMIT","source_commit_sha":r["sha"],"source_timestamp":r["timestamp"],"task_class":task_class(s+"\n"+r["body"],ps),"operation_type":op,"task_summary":s,"resolution_summary":body,"failure_signature":signature(s) if op in {"FIX","HARDEN"} else None,"changed_paths":ps,"dominant_path_prefix":prefix(ps),"source_blob_shas":src,"outcome":"MERGED_TO_MAIN","failed_approaches":[],"reusable_pattern":None,"evidence_limits":["Merged commit proves accepted repository change, not causal effectiveness by itself.","No failed approach is inferred unless separately evidenced.","No chain-of-thought or raw prompt is stored."],"authority":AUTH}
def ep_path(out,e):
    try:d=datetime.fromisoformat(e["source_timestamp"].replace("Z","+00:00"));ym=(str(d.year),f"{d.month:02d}")
    except Exception:ym=("unknown","unknown")
    return out/"episodes"/ym[0]/ym[1]/f'{e["episode_id"]}.json'
def harvest(root,out,n=250):
    made=[];skipped=0
    for r in reversed(commits(root,n)):
        e=episode(root,r)
        if e is None:skipped+=1;continue
        p=ep_path(out,e)
        if not p.exists():write(p,e);made.append(p)
    return made,skipped
def episodes(out):
    rows=[]
    for p in sorted((out/"episodes").rglob("OE-*.json")) if (out/"episodes").exists() else []:
        e=load(p,{})
        if e.get("contract")=="OPERATIONAL_EPISODE_v1":e["_path"]=str(p.relative_to(out));rows.append(e)
    return sorted(rows,key=lambda x:(x.get("source_timestamp",""),x.get("episode_id","")))
def index(root,eps,when):
    latest={}
    for e in eps:
        k=(e.get("task_class",""),e.get("failure_signature",""))
        if k[1]:latest[k]=e["episode_id"]
    cache={};rows=[]
    for e in eps:
        src=e.get("source_blob_shas") or {}
        for p in src:
            if p not in cache:cache[p]=blob(root,"HEAD",p)
        cp=compat(src,{p:cache.get(p) for p in src});k=(e.get("task_class",""),e.get("failure_signature",""))
        newer=latest.get(k) if k[1] and latest.get(k)!=e["episode_id"] else None
        tier="REVALIDATE" if cp["status"] in {"DRIFTED","REMOVED"} else "WARM"
        rows.append({"episode_id":e["episode_id"],"source_commit_sha":e["source_commit_sha"],"source_timestamp":e["source_timestamp"],"task_class":e["task_class"],"operation_type":e["operation_type"],"task_summary":e["task_summary"],"failure_signature":e.get("failure_signature"),"dominant_path_prefix":e.get("dominant_path_prefix"),"changed_paths":e.get("changed_paths",[])[:25],"compatibility":cp,"retrieval_tier":tier,"newer_related_episode":newer,"episode_path":e["_path"]})
    total=len(rows);now=utc_ts(when);cutoff=now-timedelta(days=HOT_WINDOW_DAYS) if now else None
    rows=[r for r in rows if in_hot_set(r,cutoff)]
    return {"contract":"OPERATIONAL_MEMORY_INDEX_v1","authority":AUTH,"generated_at_utc":when,"source_head_sha":head(root),"episode_count":len(rows),"total_episode_count":total,"hot_set_policy":{"rolling_rule":"UPDATE/RESEARCH automated data-writer subject (writer prefix + Actions run id, or known bot phrase), no PR reference","rolling_operation_types":sorted(ROLLING_OPERATION_TYPES),"routine_subject_pattern":ROUTINE_SUBJECT.pattern,"routine_phrases":list(ROUTINE_PHRASES),"rolling_window_days":HOT_WINDOW_DAYS,"always_kept":"ALL_OTHER_ROWS","cold_store":"episodes/ immutable, unchanged"},"rows":rows}
def candidates(idx,when):
    g=defaultdict(list)
    for r in idx["rows"]:
        if r["operation_type"] not in {"FIX","HARDEN","BUILD"}:continue
        fam="REMEDIATION" if r["operation_type"] in {"FIX","HARDEN"} else "BUILD"
        g[(r["task_class"],fam,r.get("dominant_path_prefix"))].append(r)
    out=[]
    for (tc,fam,pr),rs in g.items():
        cs={r["source_commit_sha"] for r in rs}
        if len(cs)<3:continue
        cid=hashlib.sha256(f"{tc}|{fam}|{pr}".encode()).hexdigest()[:16]
        out.append({"candidate_id":"PC-"+cid,"task_class":tc,"operation_family":fam,"dominant_path_prefix":pr,"independent_commit_count":len(cs),"currently_compatible_count":sum((r["compatibility"]["status"] in {"EXACT","PARTIAL"}) for r in rs),"supporting_episode_ids":[r["episode_id"] for r in rs[-8:]],"failure_signature_diversity":len({r.get("failure_signature") for r in rs if r.get("failure_signature")}),"status":"CANDIDATE_ONLY","automatic_skill_activation":False,"promotion_allowed":False,"required_next_gate":"GOVERNED_SKILL_REVIEW_WITH_CLEAR_PRECONDITIONS_EXIT_CRITERIA_FAILURE_MODES_AND_VERSIONING"})
    out.sort(key=lambda x:(-x["independent_commit_count"],x["task_class"],x["operation_family"]))
    return {"contract":"OPERATIONAL_PROCEDURAL_CANDIDATES_v1","authority":AUTH,"generated_at_utc":when,"promotion_policy":"NO_AUTOMATIC_SKILL_PROMOTION","candidate_count":len(out),"candidates":out[:50]}
def overlap(a,b):
    a,b=set(toks(a)),set(toks(b));return len(a&b)/len(a|b) if a and b else 0
def path_overlap(q,c):
    if not q or not c:return 0
    if set(q)&set(c):return min(1,len(set(q)&set(c))/max(1,len(set(q))))
    qp={Path(x).parts[0] for x in q if Path(x).parts};cp={Path(x).parts[0] for x in c if Path(x).parts};return len(qp&cp)/max(1,len(qp|cp))
def score(task,qpaths,fail,r):
    s=35 if r["task_class"]==task_class(task,qpaths) else 0;s+=30*path_overlap(qpaths,r.get("changed_paths",[]));s+=25*overlap(task+" "+(fail or ""),str(r.get("task_summary",""))+" "+str(r.get("failure_signature","")))
    if fail and r.get("failure_signature")==signature(fail):s+=15
    st=r["compatibility"]["status"];s+=8 if st=="EXACT" else 4 if st=="PARTIAL" else -15 if st=="DRIFTED" else -30 if st=="REMOVED" else 0
    if r.get("newer_related_episode"):s-=5
    return round(s,3)
def preflight(idx,task,qpaths,fail=None,top=5):
    ranked=[]
    for r in idx["rows"]:
        z=score(task,qpaths,fail,r)
        if z>0:x=dict(r);x["retrieval_score"]=z;ranked.append(x)
    ranked.sort(key=lambda x:-x["retrieval_score"]);sel=ranked[:max(1,min(top,10))]
    return {"contract":"OPERATIONAL_MEMORY_PREFLIGHT_v1","authority":AUTH,"task":task,"task_class":task_class(task,qpaths),"query_paths":qpaths,"source_index_head_sha":idx["source_head_sha"],"candidate_count":len(ranked),"selected_count":len(sel),"reusable_prior_work":[{"episode_id":x["episode_id"],"source_commit_sha":x["source_commit_sha"],"task_summary":x["task_summary"],"episode_path":x["episode_path"],"compatibility":x["compatibility"]["status"],"retrieval_score":x["retrieval_score"]} for x in sel if x["compatibility"]["status"] in {"EXACT","PARTIAL"}],"revalidation_required":[{"episode_id":x["episode_id"],"reason":x["compatibility"]["status"],"source_commit_sha":x["source_commit_sha"]} for x in sel if x["compatibility"]["status"] in {"DRIFTED","REMOVED"}],"known_failure_patterns":[{"episode_id":x["episode_id"],"failure_signature":x["failure_signature"],"task_summary":x["task_summary"]} for x in sel if x.get("failure_signature")],"selected":sel,"usage_instruction":"Acceleration context only. Re-read current authoritative files before acting. Memory never overrides current main.","telemetry":{"context_savings_baseline_status":"BASELINE_REQUIRED","repeated_investigation_baseline_status":"BASELINE_REQUIRED","no_savings_claim_without_measurement":True}}
def health(idx,cand,when):
    ids=[r["episode_id"] for r in idx["rows"]];dups=[k for k,v in Counter(ids).items() if v>1];bad=[r["episode_id"] for r in idx["rows"] if not r.get("source_commit_sha")]
    return {"contract":"OPERATIONAL_MEMORY_HEALTH_v1","generated_at_utc":when,"status":"PASS" if not dups and not bad else "FAIL","authority":AUTH,"episode_count":len(ids),"total_episode_count":idx.get("total_episode_count",len(ids)),"compatibility_counts":dict(Counter(r["compatibility"]["status"] for r in idx["rows"])),"procedural_candidate_count":cand["candidate_count"],"duplicate_episode_ids":dups,"episodes_missing_source_commit":bad,"retrieval_policy":"DETERMINISTIC_FIRST_NO_VECTOR_DB_NO_MODEL_CALLS","source_of_truth":"CURRENT_GITHUB_MAIN","memory_role":"DERIVED_ACCELERATION_LAYER_ONLY"}
def do_harvest(a):
    root=Path(a.repo_root);out=root/a.output_root;made,sk=harvest(root,out,a.max_commits);when=datetime.now(timezone.utc).isoformat().replace("+00:00","Z");idx=index(root,episodes(out),when);cand=candidates(idx,when);h=health(idx,cand,when)
    write(out/"LATEST_OPERATIONAL_MEMORY_INDEX.json",idx,compact=True);write(out/"LATEST_PROCEDURAL_CANDIDATES.json",cand);write(out/"LATEST_OPERATIONAL_MEMORY_HEALTH.json",h)
    state={"contract":"OPERATIONAL_MEMORY_AND_RETRIEVAL_v1","generated_at_utc":when,"status":h["status"],"source_head_sha":idx["source_head_sha"],"new_episode_count":len(made),"episode_count":idx["episode_count"],"total_episode_count":idx.get("total_episode_count",idx["episode_count"]),"hot_window_days":HOT_WINDOW_DAYS,"procedural_candidate_count":cand["candidate_count"],"self_generated_commits_skipped":sk,"authority":AUTH};write(out/"LATEST_OPERATIONAL_MEMORY_STATE.json",state);print(json.dumps(state,sort_keys=True))
def do_preflight(a):
    root=Path(a.repo_root);out=root/a.output_root;idx=load(out/"LATEST_OPERATIONAL_MEMORY_INDEX.json",{})
    if idx.get("contract")!="OPERATIONAL_MEMORY_INDEX_v1":raise SystemExit("operational memory index missing; run harvest first")
    if idx.get("source_head_sha")!=head(root):idx=index(root,episodes(out),datetime.now(timezone.utc).isoformat().replace("+00:00","Z"))
    doc=preflight(idx,a.task,a.path or [],a.failure_signature,a.top_k)
    if a.output:write(a.output,doc)
    print(json.dumps(doc,sort_keys=True))
def main():
    p=argparse.ArgumentParser();p.add_argument("--repo-root",default=".");p.add_argument("--output-root",default="research/framework_learning/operational_memory");sp=p.add_subparsers(dest="cmd",required=True)
    h=sp.add_parser("harvest");h.add_argument("--max-commits",type=int,default=250);h.set_defaults(fn=do_harvest)
    q=sp.add_parser("preflight");q.add_argument("--task",required=True);q.add_argument("--path",action="append",default=[]);q.add_argument("--failure-signature");q.add_argument("--top-k",type=int,default=5);q.add_argument("--output");q.set_defaults(fn=do_preflight)
    a=p.parse_args();a.fn(a)
if __name__=="__main__":main()
````

## M3. FULL FILE `00_ARCHIVE_CONTROL/SEL_SELECTIVE_OPERATIONAL_BINDING_v1.json` (blob 6e4b7c59d33445b294b5a1d2e09635d06ca25834, sha256 ac30482cebf4995f953956be2fc0707a813ada0abdb6e556c21b96063570a1f6, 50 lines, 1920 bytes). WP: WP8. public binding to the restricted SEL memory owner (paths/blobs only).

````
{
  "contract": "SEL_PUBLIC_BINDING_v1",
  "effective_date": "2026-10-01",
  "status": "BOUND_TO_PRIVATE_SELECTIVE_OPERATIONAL",
  "authority": "DISCOVERY_AND_ROUTING_ONLY",
  "control_plane": "Donh91/Investering-Framework-Archive-v1",
  "restricted_owner_repository": "Donh91/secrets",
  "restricted_merge_commit": "4e1f4097e1754312810a1d810bd0681279d1670b",
  "restricted_merge_verified_reachable_from_main": true,
  "restricted_artifacts": [
    {
      "path": "GOVERNANCE/SEL_OPERATIONAL_STATUS_v1.json",
      "git_blob_sha": "61303a4c3b090640b65e5dca8fcf364811e5b0be",
      "contract": "SEL_OPERATIONAL_STATUS_v1",
      "status": "SEL_V1_SELECTIVE_OPERATIONAL"
    },
    {
      "path": "GOVERNANCE/CROSS_REPO_AGENT_CONTEXT_MAP.json",
      "git_blob_sha": "a59c850c913d5fdeca4dc0f53a7753a167282893",
      "route_id": "SHARED_EXPERIENCE_MEMORY"
    },
    {
      "path": ".agents/skills/shared-experience-memory/SKILL.md",
      "git_blob_sha": "e5d795645c20df72ee0bcc6dd624dbb4341b5664",
      "role": "PRIVATE_OPTIONAL_SUPPORT_SKILL"
    }
  ],
  "memory_rule": "MEMORY != TRUTH",
  "practical_value_evidence": "MIXED_BUT_PROVEN",
  "routing": {
    "mode": "SELECTIVE_ONLY",
    "global_auto_retrieval": "HOLD",
    "current_authority_first": true,
    "smallest_relevant_recall_only": true,
    "access_failure_policy": "CONTINUE_WITH_CURRENT_AUTHORITY_NO_MEMORY",
    "access_failure_state": "SEL_OPTIONAL_CONTEXT_UNAVAILABLE",
    "post_task_outcome_feedback": "ONLY_WHEN_MEMORY_MATERIALLY_AFFECTED_WORK_AND_OUTCOME_BECOMES_OBSERVABLE"
  },
  "authority_prohibitions": [
    "MARKET",
    "PORTFOLIO",
    "CANONICAL_FRAMEWORK",
    "CREDENTIAL",
    "AUTOMATIC_RULE_PROMOTION"
  ],
  "contains_private_memory_payloads": false,
  "contains_restricted_provider_values": false,
  "contains_credentials": false,
  "next_expansion_gate": "ADDITIONAL_NATURAL_HIGH_VALUE_USE_WITH_DURABLE_OUTCOME_EVIDENCE"
}
````

## M4. FULL FILE `research/framework_learning/operational_memory/LATEST_OPERATIONAL_MEMORY_STATE.json` (blob 6578be458b86de4d4a9f6d9421b32eede72599a4, sha256 9ae27fb9438c6917bf6cc31c5bd9cc75f1e27224d3f525f673287304c71b8498, 19 lines, 580 bytes). WP: WP8. CURRENT memory state (differs from the #2224 pin e056a5af; see M4b).

````
{
  "authority": {
    "automatic_promotion": false,
    "automatic_repository_write": false,
    "automatic_skill_activation": false,
    "canonical_effect": false,
    "portfolio_execution": false
  },
  "contract": "OPERATIONAL_MEMORY_AND_RETRIEVAL_v1",
  "episode_count": 3816,
  "generated_at_utc": "2026-11-18T13:21:50.253803Z",
  "hot_window_days": 14,
  "new_episode_count": 10,
  "procedural_candidate_count": 32,
  "self_generated_commits_skipped": 3,
  "source_head_sha": "ab6b0343fd32898843a6a56a8972ad81f39ae552",
  "status": "PASS",
  "total_episode_count": 10386
}
````

## M5. EXCERPT `00_FMOS/S1/EVIDENCE_BINDINGS.md` (blob 41f19f5e652576de4125a6ef11812a73be83b477, sha256 of full file 58bb697dea55d7ef2fe84377b131e00b13420cf20034b620f20bfea916cd8a73) lines 1-6 of 131. WP: WP8. S1 evidence bindings: header and purpose only.

````
S1 EVIDENCE BINDINGS v3.0 (rubric of 00_FMOS/S1/ACTION_LOOP.md V3 EVIDENCE BINDINGS; pinned by rubric_blobs in 00_FMOS/S1/RUNTIME_CONTRACT.json; AGENTS.md section 0.2g)

PURPOSE
Six bindings (B1 to B6) close the gaps that the Astra S1 vNext review (Archive 06_RESEARCH_LAB/astra_program_20261116/results/s1_vnext/, fixes 4, 6, 7, 9, 12 and 14) found in v2.2. B8 and B9 repair the two defects that the first live audit of v2.2 found (Bridge #173 comment 6948786347, 2026-11-17): a main-health route that S1's fetch tool refuses, and a run that stopped at that refusal. Each binding B1 to B6 only NARROWS a rule of ACTION_LOOP.md: it adds a proof S1 must hold before it acts, or a record S1 must leave after it acts. B8 changes HOW the two main-health facts are read, never WHAT must be true; B9 orders reads, re-checks H1 before every write and adds one output line. No binding grants a new merge, a new write target or a new waiver, and no binding relaxes a hard stop H1 to H8. Where a rule and a binding differ, the stricter one wins. A proof S1 cannot read is NOT PROVEN, never a pass.

PARAMETERS (machine-readable; tests/governance/test_s1_v3_evidence_bindings_v1.py reads this block)
````

## K1. FULL FILE `06_RESEARCH_LAB/mission_packets/2026-11-11__KOMPAS2_FINGERPRINT_ALPHA_SOL61_MAX_v1.json` (blob ad615df9cf03324d0b55d94a248642893acecfee, sha256 4c11edb44d0c58b50c5976779d16f65c11a7a31c33298aa40d4e71aa53fb77b7, 79 lines, 8984 bytes). WP: WP9. original Kompas2 Sol packet: historical specification, not instructions.

````
{
  "contract": "RESEARCH_LAB_SOL_API_MISSION_PACKET_v1",
  "created_date": "2026-11-11",
  "status": "OWNER_APPROVED_NEW_DISTINCT_ONE_SHOT_PENDING_NATIVE_PACKET_RELEASE",
  "mission_id": "KOMPAS2-FINGERPRINT-ALPHA-CROSS-EXAM-SOL61-MAX-20261111",
  "priority": "P0",
  "title": "Kompas Pro 2.0 x Alpha Lab: PIT market fingerprints and probabilistic forecast calibration with nonduplicative adversarial implementation audit",
  "recommended_task_lane": "RESEARCH_LAB_SOL_ANALYSIS",
  "recommended_model": "gpt-6.1-sol",
  "reasoning_effort": "max",
  "original_owner_issue": 1156,
  "one_shot_owner_mandate": "https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1156#issuecomment-6682722905",
  "public_storage_consent_comment_id": 6682722905,
  "public_storage_consent_30_days": true,
  "public_source_only": true,
  "owner_authorization_scope": "Fresh explicit chat approval 2026-11-11 to run a distinct bounded GPT-6.1 Sol MAX research critique in the existing governed lane for Kompas Pro 2.0. Owner Archive #1516 comment 6792163896 registers research intent. Authenticated exact-packet owner GitHub signature on #1476 is STILL required before any paid POST. The storage consent comment is not a paid mission release.",
  "question": "Independent FALSIFICATION-FIRST scientific and code-design review, NOT another broad recap or extra prediction engine. Read already merged Kompas Pro 2.0 owner plan and ten-track Research Parallel Lanes manifest, existing ARP01/ARP04 Sol outputs, existing ARP portfolio and Market Anticipation prereg. FIRST identify overlaps and what already has a verified original owner, especially #1516 Forward Path, #1596 first-known forecast and scoring, #1827 integrity, Alpha #22/#228 existing PUBLIC_TO_PRIVATE_ONLY consumer. THEN propose at most TWO unique, source-gated smallest SHADOW improvements (e.g., original issuance/nominal-interval proper scorecard and *limited* PIT fingerprint challenger) and one explicit zero-change negative-control experiment for Alpha private research. Their purpose: determine whether market-state fingerprint has truly incremental prospective calibration or later Alpha paper survivor/sellability value over already used cheap original-clock baselines. Design exact field list with first-known vs nominal timestamps and venue/quote parity; avoid W44/W46 post-issue OHLC contamination and suffixed clock denominator, costless hindsight, multi-testing and 72h / week correlation. W41-W46 results are development only, W47 onward untouched prospective; prohibit re-scoring Round 3 and official W46 freeze rewrite. Separate BTC price-only calibration, ETHBTC rotation segment, token risk/survival label and after-cost execution; do not silently transfer model calibration to economic value. Identify the smallest *specific* existing source code locations and positive/negative tests to prove an incremental change, or return NO_NEW_CODE_IF_DUPLICATE / WAIT_SOURCE. Propose bounded 26 independent week candidate review target but no power overclaim; control for market-shock and token-operator clustered samples; reissue versions must remain immutable originals. Make the Fable 5.2 adversarial handoff precise with questions about null data, model complexity, overfitting and economic nulls, but DO NOT claim Fable executed or schedule it. The public Sol packet must not request or include any private Alpha data, token holdings or privileged research output. The final response must decide whether to keep current canonical unchanged and ONLY start shadow, and make a falsifiable, source-specific gate to the first safe implementation. Zero trade, portfolio decision, threshold/weight/market rule change, scheduler, new agents or model source writes.",
  "hypothesis": "The most valuable near-term Kompas Pro 2.0 contribution is truthful PIT issuance/interval-scoring and a small frozen shadow challenger; a more complex fused fingerprint is NOT yet proven better than existing official / price-only models. A public-to-private CN regime context may or may not add private Alpha outcome information but must not be inferred from public source.",
  "baseline": "Existing ARP01 frozen original issuance and same-clock no-change/volatility band; current CN/Kompas #1516 and #1596 with honest W46 source validity; existing Alpha G2/default and hold/abstain in private original owner; ARP04 one-POST source-limited critique; HRE is retrospective developmental, not original forecasts; no private point-in-time token labels in this PUBLIC packet.",
  "falsifier": "Reject unnecessary new feature/model when original code already exposes scored canonical or a qualified shadow incumbent; reject scientific uplift with absent first-known, one-week independent n, overlapping day points, vendor vintage substitution, no source-legal preknown features, min/max range mislabeled nominal quantile, or negative/cluster controls that eliminate lift. On true prospective holdouts no calibrated proper-score advantage versus no-change and simple volatility or no utility over Alpha default after measured full-position execution costs => NO_INCREMENTAL_EDGE. Private-source absence => WAIT_SOURCE, never pretend tested.",
  "kill_condition": "Do NOT recreate original #1596 #1516 #1827 owner, new supervisor/scheduler/scanner or synthetic Fable agent. Do NOT repeat ARP01 or ARP04 paid prompts, assert W46 all horizons matured, calculate performance without original issued forecasts, look ahead, score restricted Round3, transfer private wallet/Alpha rows into public source, use private dataset schema or deidentify user wallet improperly, alter original forecast history, automatically rewrite production thresholds/market state, trade, create scripts/workflows, merge patches, trigger follow-up paid retries, or invoke Astra.",
  "required_outputs": [
    "DEDUPE_EXISTING_OWNER_CODE_AND_SOL_ARP01_ARP04_IDENTIFY_PRECISE_ALREADY_SOLVED_VS_OPEN_UNVERIFIED",
    "FIRST_KNOWN_HORIZON_QUOTE_UNITS_MATURITY_AND_WEEK_EFFECTIVE_N_FIELD_CONTRACT",
    "TWO_AT_MOST_ADDITIVE_CODE_CANDIDATES_WITH_SPECIFIC_EXISTING_FILE_PATHS_TESTS_ROLLBACK_AND_P0_P1_RISK_OR_NULL",
    "SMALLEST_NO_CODE_BASELINE_AND_ONE_NEGATIVE_CONTROL_PROPER_SCORE_ABLATION_QUANTILES_WHEN_VALID",
    "ALPHA_PUBLIC_TO_PRIVATE_INTERFACE_AND_COHORT_OPERATOR_RUG_SELLABLE_PAPER_SCOPE_SAFE_OR_WAIT_PRIVATE",
    "FINGERPRINT_MINIMAL_FEATURE_AVAILABILITY_AND_NO_LOOKAHEAD_PREREG_OR_REJECT_AS_REDUNDANT",
    "UNCERTAINTY_COVERAGE_SHARPNESS_PRIMARY_PROPER_SCORE_HORIZON_MATCHED_DECISION_UTILITY_SECOND_STAGE",
    "PROSPECTIVE_W47_ONWARD_FROZEN_SHADOW_26_WEEK_REVIEW_TARGET_SEALED_PIT_AND_CLUSTERED_HOLDOUT_WITH_POWER_UNKNOWN",
    "FABLE52_REDTEAM_PRECISE_SOURCE_BOUNDED_HANDOFF_WITHOUT_EXECUTION_CLAIMS",
    "PRIORITIZED_FIRST_NONDUPLICATE_SHADOW_IMPLEMENTATION_NEXT_TASK_AND_NATIVE_GATE_WITH_CLEAR_BLOCKERS",
    "ADVERSARIAL_VERDICT_VERIFIED_WEAKENED_OR_INSUFFICIENT_EVIDENCE_ZERO_MODEL_AUTHORITY"
  ],
  "forbidden": [
    "Private Alpha source, user wallet holdings, restricted provider raw or normalized values, secrets and Vault",
    "Round3 hypothesis testing or outcomes before independent gate",
    "Writing or merging code, modifying official CN/Kompas forecasts, source thresholds or portfolio actions",
    "New orchestration, agents, cron, GitHub identity or paid retries",
    "Failure to distinguish observed actual native PR/run/receipt from plan"
  ],
  "authority": {
    "framework_state_change": false,
    "portfolio_action": false,
    "market_rule_change": false,
    "threshold_change": false,
    "weight_change": false,
    "canonical_promotion": false,
    "repository_write": false,
    "automatic_merge": false,
    "automatic_code_write": false
  },
  "research_only": true,
  "review_only_no_code_write": true,
  "max_runs_for_this_release": 1,
  "max_model_output_tokens_per_new_attempt": 64000,
  "previous_distinct_completed_mission": "S1-GENERAL-CLOSURE-CONVERGENCE-SOL61-MAX-20261108",
  "comparison_owner_issues": [
    1516,
    1596,
    1827,
    1156,
    1476,
    1530
  ],
  "source_observation_cutoff_utc": "2026-11-11",
  "allowed_public_context_paths": [
    "research/autonomous_research_portfolio/KOMPAS_PRO_2_APPROVED_RESEARCH_PLAN_20261111.md",
    "research/autonomous_research_portfolio/KOMPAS_PRO_2_PARALLEL_LANES_20261111.json",
    "research/autonomous_research_portfolio/EVIDENCE_DECISIONS_AND_TOP10_v1.md",
    "research/autonomous_research_portfolio/PRODUCT_RECIPES_v1.md",
    "research/programs/MARKET_ANTICIPATION_RESEARCH_PROGRAM_v1/RESEARCH_CONTRACT.yaml",
    "research/api_agent/outputs/research_lab_sol/ARP01-FORECAST-EDGE-CALIBRATION-SOL61-MAX-20261107/issue-1476/comment-6714216846/RESEARCH_LAB_SOL_ANALYSIS.json",
    "research/api_agent/outputs/research_lab_sol/ARP04-MICROCAP-SURVIVAL-EXECUTABLE-ALPHA-SOL61-MAX-20261107/issue-1476/comment-6720273819/RESEARCH_LAB_SOL_ANALYSIS.json",
    "00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md",
    "AGENTS.md"
  ],
  "no_private_data": true
}
````

## K2. FULL FILE `research/autonomous_research_portfolio/KOMPAS_PRO_2_APPROVED_RESEARCH_PLAN_20261111.md` (blob 1f39d231a982925b84214cc0283cc9edb7d833fe, sha256 f8d6cd60685c9674570bd2605fb2cf950fddbd6c89ef7bcfb2533a6eb40cb58a, 64 lines, 11911 bytes). WP: WP9. owner-approved Kompas Pro 2.0 plan.

````
# Kompas Pro 2.0 x Alpha Lab Pro · owner-approved scientific research plan (2026-11-11)

**Status:** OWNER_APPROVED_RESEARCH_DESIGN / SHADOW_ONLY / NO_MARKET_AUTHORITY / NO_PRODUCTION_PROMOTION.  
**Owner mandate:** [Archive #1516 owner comment 6792163896](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1516#issuecomment-6792163896).  
**Original owners:** [CN Forward Path #1516](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1516), [PIT/calibration #1596](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596), [Kompas integrity #1827](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1827), [S1 #1156](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1156), private Alpha Lab original [#22](https://github.com/Donh91/Meme-Alpha-Lab/issues/22) and [#228](https://github.com/Donh91/Meme-Alpha-Lab/issues/228). **No new owner, engine, scheduler, agent identity, GitHub permissions or trade authority.**

## Purpose and nonduplication

Prove or falsify whether (a) an *as-of-time* market-state fingerprint adds predictive information to **existing** canonical CN/Kompas over simple original-clock baselines, and (b) a legal, public-to-private, versioned CN regime projection adds **independent prospective** utility to Alpha Lab token *survival* and sellable paper-only opportunities versus its existing microstructure baselines. Do not assume either improvement exists. The intended result may be a **rejected** model and a smaller, safer stack.

Research Parallel Lanes v1 is an *existing skill* at `.agents/skills/research-parallel-lanes/SKILL.md`. The accompanying 10-lane manifest is a *plan only*: it does **not** mean that ten agents ran. Default at most 2-4 independently evidenced computational jobs, and no new recurring automation. Existing Sol MAX can be activated **once** only through the already governed, owner-authenticated #1156/#1476 release with genuine paid claim, strict budget and model admission. Claude Fable 5.2 can later red-team via the existing private Bridge #173, not via a new scheduler. Neither is a market authority.

## Sources already available and prior adversarial findings

1. Existing ARP programs already cover forecast calibration (#1596), forward path (#1516), transition/fragility, executable Alpha (#22) and HRE. Do not duplicate ARP01 or ARP04.
2. Prior [ARP01 Sol MAX evidence](../api_agent/outputs/research_lab_sol/ARP01-FORECAST-EDGE-CALIBRATION-SOL61-MAX-20261107/issue-1476/comment-6714216846/RESEARCH_LAB_SOL_ANALYSIS.json) reports (i) a risk of interpreting completed OHLC endpoints as wholly post-issue extrema, (ii) a risk of certifying a contiguous suffix without a declared full decision window, and (iii) W44 width-versus-overlap ranking differences. These are bounded *static findings* and not evidence of current W46 failure or improvement in live forecasting. Confirm against fresh original owner before fixing.
3. Prior [ARP04 Sol MAX evidence](../api_agent/outputs/research_lab_sol/ARP04-MICROCAP-SURVIVAL-EXECUTABLE-ALPHA-SOL61-MAX-20261107/issue-1476/comment-6720273819/RESEARCH_LAB_SOL_ANALYSIS.json) identifies first-decision clock ambiguity when `decision_ms` is missing, train/test feature-selection and chronological-grouping risks, and absence of proven executable whole-position microcap economics. Check current Alpha source first. Do **not** transfer private Alpha records into this public repository or public Sol context.
4. Claude Bridge current `claude/log` already separately reports W41-W46 as hypothesis generation, prospective W47 onward, and approximately five weekly effective observations in a W41-W45 band comparison. This is a Bridge report, **not a newly replicated current-main result**. Source-read and exact-HEAD verify before interpreting or promoting.
5. [Existing Market Anticipation Program](../programs/MARKET_ANTICIPATION_RESEARCH_PROGRAM_v1/RESEARCH_CONTRACT.yaml) already covers regime changes, liquidity and rotation. Its ownership and frozen preregistration are preserved.

## Proposed hypotheses, strictly research-only

**H1 / Market Fingerprint**: at an eligible issue time, a compact regime vector made from *preknown* BTC trend, ETH/BTC trend, realized volatility, market breadth, ETF flow vintage and liquidity observability increases honest out-of-sample value. Evaluate simple price-only, persistence, historical volatility and existing canonical CN first. Test small specified feature families rather than search arbitrary combinations. No invented composite score, invented probability or automatic reweight.

**H2 / Probabilistic Path**: a forecast distribution or central nominal interval (e.g. p10-p90 with *explicit issued quantile semantics*) improves joint calibration and sharpness relative to frozen price-only bands. A min/max week band is NOT a 90% prediction interval. Score only original-issued, immutable, matured forecasts; W46 and historical W41-W46 are development, not untouched evidence for a new model.

**H3 / Rotation**: at genuine first-known time, ETH/BTC leadership, stablecoin/market breadth and available on-chain or ETF signals lead later *segment* relative returns beyond BTC volatility and ETH/BTC-only baselines. Test lead/lag direction, inverted clocks and shuffled eras; no named trade/BUY.

**H4 / Market-to-Alpha**: the **already existing** CN public-to-private context may stratify pre-sighted token cohorts by contemporaneous regime, improving calibration of future survival and sellable outcome labels after controlling token age, chain, venue, launch cohort and liquidity. Counterfactual baseline = the same existing Alpha G2/default without CN regime. Must include rugs, nulls, delisted/zero-liquidity and censored candidates. 'Reached 5x' != saleable 5x; no post-launch `path_completed` as a predictor. No private features or personal wallets in public Archive.

**H5 / Utility and robustness**: any apparent statistical improvement survives chronological purging/embargo, market shock and creator/operator cluster blocks, realistic slippage/gas/failed-route scenario, alternate source vintages, negative controls and multiple-comparison correction. If no forward PIT evidence, return `WAIT_SOURCE`, not a retroactive result.

## First execution sequence, smallest safe action

0. Read `AGENTS.md`, cross-repo boundaries, current cockpit, original owner status, prior ARP01/04 Sol receipts, current W46 PR #2073 and actual source clocks; pin main SHA and all inputs. Do NOT infer that #2073 merged or that its seven closes have matured.
1. **L01-L03**: source and issuance census, paired original-vs-naive pre-registration. Record absent forecasts and distinct missing/late/expired counts as DENOMINATOR, not correct abstentions.
2. **L04-L06**: freeze three small non-authoritative challenger definitions and their negative-control ablations *before* any prospective outcomes; no lookahead, no vendor-vintage substitutions, no private Round3 scoring.
3. **L07-L08**: Alpha private owner evaluates interface and token cohort/whole-position paper execution with existing consumer contract and own privacy-controlled runtime. Public output = only safe aggregate, cohort/sample metadata and comparison digests (or `PRIVATE_DATA_AUTHORITY_UNAVAILABLE`).
4. **L09**: a **distinct** Sol MAX critique only if new question, owner packet, hash, budget and claim checks pass. Sol writes no code and has no market promotion rights.
5. **L10**: Claude Fable 5.2 counter-examination through existing Bridge #173 only after owner-directed model selection, natural Claude scheduling/capacity and authenticated result. S1 routes *eligible* proposed fixes through original owners.
6. Code or schema implementation only in existing CN/Alpha producers/consumers after source evidence; isolated branch, exact-head CI, independent review, owner release and main/hosted readback. No green-PR-equals-live claim.

## Measurement and publication contract

For each `(asset, venue, quote, issue_utc, target_utc, horizon, original_forecast_id, source_commit, source_first_known_utc, policy_revision)`:
- preserve immutable original-issued model output, valid from/to, complete scalar target definition (daily close vs within-day min/max vs path extrema), missingness, source units, delivery time, maturity and forecast availability;
- define a pairwise *same-clock* frozen baseline before maturity; never use later re-issued forecasts as the original; changing weekly forecast during the week must make a **new versioned issue**, not rewrite original proof;
- directional balanced accuracy + abstention/coverage; MAE or normalized MAE for scalar price; WIS or pinball only when specified nominal quantiles exist at issue time; expected and empirical coverage *plus width* per interval; Brier/log only for contemporaneously issued real probabilities;
- match scores on shared eligible cohorts, keep all null/missing cases, use temporal blocks and clustered bootstrap confidence intervals, not naive binomial standard errors over overlapping 72h or 7 daily points; report event-family effective N;
- test profitability/utility only as a separate *paper* decision layer, net of explicit price/venue/slippage/gas/failed-fill assumptions, including HOLD/ABSTAIN. No market rule auto-promotion.

**Pre-registration for a new challenger** must define issue cadence, features/as-of cutoff, forecast target/interval semantics, null behavior, primary metric and comparator, material-effect threshold and block bootstrap, multiple-test correction, out-of-sample window and stop condition BEFORE looking at outcomes. Minimum 26 independent weekly cohorts is a *candidate review target*, not a guarantee of power or a basis for claiming 26 independent weeks where data do not exist. Feature quality or scientific value may justify rejecting the candidate earlier.

## Cross-repo interface, not a second engine

Retain Alpha's `public_context/CONTRACT_V2.json` **PUBLIC_TO_PRIVATE_ONLY / CONTEXT_ONLY** direction. Candidate `COMPASS_MARKET_CONTEXT_RESEARCH_V1` is an *extension proposal* of its existing versioned consumer, NOT a replacement or public personal-wallet output. Proposed fields: `compass_issue_id`, immutable `source_commit_sha`, `forecast_schema_revision`, `issued_at_utc`, `known_at_utc`, `valid_until_utc`, `quote_unit`, `horizon`, `regime_label_or_unknown`, `feature_family_availability`, `confidence_provenance`, `source_health` and `shadow_research_only=true`. Owner must map each proposed field onto real current source, redact private value classes, prove monotonic clocks and stale/unknown behavior, and add positive and negative consumer tests. Regime alone cannot bypass Alpha sellability/rug/identity controls.

## Go/no-go and release

**Immediate practical candidate:** implement an additive, read-only original-source **scorecard/denominator projection**, owned by #1596/#1516, after verifying current W46 #2073 status and avoiding duplicate scoring. It can improve scientific honesty without requiring claimed predictive edge, API-dependent weekly issue or changes in canonical decision logic. A separate prospective shadow fingerprint challenger is next, contingent on legitimate features.

Promotion is **BLOCKED** unless source clocks and cohorts pass, baseline skill is materially better on genuinely forward independently grouped holdouts, adverse negatives/ablation tests are answered, independent technical review and exact-head CI are green, rollback is defined, and qualified owner release/main/site consumer readback exists. Keep Round3 `PROSPECTIVE_COLLECTION_ONLY` and outcome scoring `OFF`; do not reinterpret that restriction as approval.

**Falsifier-first result states:** `SOURCE_REPAIR`, `PLANNED`, `WAIT_SOURCE`, `NO_INCREMENTAL_EDGE`, `FORWARD_TEST`, `PROMOTION_REVIEW`, `BLOCKED`. No one-shot Sol result, Claude review or 10-lane plan self-promotes a model.
````

## K3. FULL FILE `research/autonomous_research_portfolio/KOMPAS_PRO_2_PARALLEL_LANES_20261111.json` (blob 3f7620158e1c67c08fe529f60cd3ea6e549b0ec0, sha256 a8aaee9857a602623e495c8aa4eb625f50ad308e6bcd0c1d228bbbce4897bdb8, 204 lines, 8932 bytes). WP: WP9. ten L01-L10 lanes.

````
{
  "contract": "RESEARCH_PARALLEL_LANES_V1",
  "status": "PLANNED",
  "mission_id": "KOMPAS_PRO_2_20261111_OWNER_APPROVED_RPL_10_TRACKS",
  "original_owner_issue": "https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1516",
  "project_repo": "Donh91/Investering-Framework-Archive-v1",
  "objective": "Falsify the incremental forecast calibration and Alpha market-regime value of a source-frozen market fingerprint versus existing canonical and cheap baselines.",
  "source_manifest_path": "research/autonomous_research_portfolio/PORTFOLIO_MANIFEST_v1.json",
  "source_snapshot_sha": "56187d1057b9e487163d1d39378759cb015812dc",
  "source_eligibility": "UNKNOWN",
  "data_classification": "PUBLIC_ONLY",
  "parallel_job_cap": 3,
  "approved_budget_usd": 3,
  "no_new_scheduler": true,
  "no_new_agent_identity": true,
  "no_trading_authority": true,
  "lanes": [
    {
      "id": "L01",
      "name": "Source lineage and original-owner census",
      "question": "Which current original clocks and source paths actually govern issuance?",
      "hypothesis": "A source-native ledger can distinguish absent from censored and late.",
      "baseline": "Current original source declarations, no synthetic fill",
      "falsifier": "Unverifiable first-known or original issuer identity",
      "source_ref": "Archive #1596 #1827 original source and API ledger",
      "depends_on": [],
      "max_minutes": 30,
      "executor_kind": "READ_ONLY_TOOL",
      "budget_usd": 0,
      "output_path": "research/autonomous_research_portfolio/kompas_pro_2/lanes/L01_RESULT.md",
      "status": "PLANNED",
      "run_evidence": {}
    },
    {
      "id": "L02",
      "name": "Frozen W46 and daily-close integrity",
      "question": "Were seven Monday-frozen per-day targets actually issued and scored honestly?",
      "hypothesis": "W46 daily close eligibility can be determined without rewriting snapshots.",
      "baseline": "Original frozen week and naïve last-close baseline",
      "falsifier": "Missing issue, target mismatch, quote mismatch or incomplete horizon",
      "source_ref": "Archive #1516 #1596 PR #2073",
      "depends_on": [
        "L01"
      ],
      "max_minutes": 30,
      "executor_kind": "READ_ONLY_TOOL",
      "budget_usd": 0,
      "output_path": "research/autonomous_research_portfolio/kompas_pro_2/lanes/L02_RESULT.md",
      "status": "PLANNED",
      "run_evidence": {}
    },
    {
      "id": "L03",
      "name": "Proper-score benchmark tournament",
      "question": "Does any canonical issued score beat fixed no-change, bands and abstain?",
      "hypothesis": "Width-sensitive paired scoring improves diagnostic truth.",
      "baseline": "PIT no-change, sigma-scaled bands, HOLD, abstain",
      "falsifier": "No baseline lift or no issued nominal distribution",
      "source_ref": "Archive ARP01 Sol and #1596 scorer",
      "depends_on": [
        "L01",
        "L02"
      ],
      "max_minutes": 40,
      "executor_kind": "READ_ONLY_TOOL",
      "budget_usd": 0,
      "output_path": "research/autonomous_research_portfolio/kompas_pro_2/lanes/L03_RESULT.md",
      "status": "PLANNED",
      "run_evidence": {}
    },
    {
      "id": "L04",
      "name": "Regime fingerprint source-safe ablation",
      "question": "Does a fixed small market-regime fingerprint add stable information?",
      "hypothesis": "PIT liquidity, trend and breadth have nonredundant effect.",
      "baseline": "Price-only drift and realized-volatility regime",
      "falsifier": "Same-clock conditional lift vanishes or features unavailable",
      "source_ref": "Market Anticipation Research Contract and ARP03",
      "depends_on": [
        "L01"
      ],
      "max_minutes": 45,
      "executor_kind": "READ_ONLY_TOOL",
      "budget_usd": 0,
      "output_path": "research/autonomous_research_portfolio/kompas_pro_2/lanes/L04_RESULT.md",
      "status": "PLANNED",
      "run_evidence": {}
    },
    {
      "id": "L05",
      "name": "Probabilistic path calibrator",
      "question": "Can a source-frozen path improve sharpness and true nominal coverage?",
      "hypothesis": "Quantile or density forecast is better calibrated after source gates.",
      "baseline": "Rolling-vol quantile band and no-change median",
      "falsifier": "No prospective nominal quantiles or poor proper score",
      "source_ref": "Archive #1516 current Forward Path owner",
      "depends_on": [
        "L01",
        "L02"
      ],
      "max_minutes": 45,
      "executor_kind": "READ_ONLY_TOOL",
      "budget_usd": 0,
      "output_path": "research/autonomous_research_portfolio/kompas_pro_2/lanes/L05_RESULT.md",
      "status": "PLANNED",
      "run_evidence": {}
    },
    {
      "id": "L06",
      "name": "Capital rotation falsification",
      "question": "Does lead/lag rotation survive ETHBTC-only and clock placebo tests?",
      "hypothesis": "Preknown breadth and liquidities precede segment divergence.",
      "baseline": "ETHBTC leadership and shuffled-clock placebo",
      "falsifier": "No surviving lead after cluster and temporal controls",
      "source_ref": "Existing transition program ARP03 and #1530",
      "depends_on": [
        "L01"
      ],
      "max_minutes": 40,
      "executor_kind": "READ_ONLY_TOOL",
      "budget_usd": 0,
      "output_path": "research/autonomous_research_portfolio/kompas_pro_2/lanes/L06_RESULT.md",
      "status": "PLANNED",
      "run_evidence": {}
    },
    {
      "id": "L07",
      "name": "Alpha cohort survival context",
      "question": "Does CN PUBLIC_TO_PRIVATE regime add predecision token survival signal?",
      "hypothesis": "Safe known-at CN context adds beyond existing Alpha G2.",
      "baseline": "Current Alpha G2 and token age liquidity controls",
      "falsifier": "No full survivor/rug denominator or no independent lift",
      "source_ref": "Meme-Alpha-Lab #22 #228 and public-context CONTRACT_V2",
      "depends_on": [
        "L01",
        "L04"
      ],
      "max_minutes": 50,
      "executor_kind": "READ_ONLY_TOOL",
      "budget_usd": 0,
      "output_path": "research/autonomous_research_portfolio/kompas_pro_2/lanes/L07_RESULT.md",
      "status": "PLANNED",
      "run_evidence": {}
    },
    {
      "id": "L08",
      "name": "Paper fill feasibility and utility",
      "question": "Do predicted opportunities remain sellable at realistic full-position cost?",
      "hypothesis": "Net utility and missed winners jointly improve over HOLD.",
      "baseline": "Always HOLD, no signal, existing Alpha base",
      "falsifier": "Rug, failed-route and slippage wipe out edge",
      "source_ref": "Meme-Alpha-Lab original paper and sellability owners",
      "depends_on": [
        "L07"
      ],
      "max_minutes": 50,
      "executor_kind": "READ_ONLY_TOOL",
      "budget_usd": 0,
      "output_path": "research/autonomous_research_portfolio/kompas_pro_2/lanes/L08_RESULT.md",
      "status": "PLANNED",
      "run_evidence": {}
    },
    {
      "id": "L09",
      "name": "Sol MAX independent cross-model adversary",
      "question": "What smallest nonduplicate model survives existing ARP01 and ARP04 critique?",
      "hypothesis": "One bounded paid critique can kill weak extra complexity.",
      "baseline": "Current ARP01 and ARP04 Sol outputs and simplest models",
      "falsifier": "No new falsifiable test or already-solved defects",
      "source_ref": "Existing #1156 #1476 gated owner Sol lane",
      "depends_on": [],
      "max_minutes": 20,
      "executor_kind": "EXISTING_AI_AGENT",
      "budget_usd": 3,
      "output_path": "research/autonomous_research_portfolio/kompas_pro_2/lanes/L09_RESULT.md",
      "status": "PLANNED",
      "run_evidence": {}
    },
    {
      "id": "L10",
      "name": "Claude Fable engineering and reviewer experiment",
      "question": "Can current original source and bounded patches survive Claude Fable scrutiny?",
      "hypothesis": "Independent adversarial reviewer finds reproducible contract weaknesses.",
      "baseline": "Existing tests, negative cases and no Fable intervention",
      "falsifier": "No authenticated native Claude run or no incremental finding",
      "source_ref": "Existing Bridge Claude log PR #173 and native reports",
      "depends_on": [
        "L09"
      ],
      "max_minutes": 45,
      "executor_kind": "EXISTING_AI_AGENT",
      "budget_usd": 0,
      "output_path": "research/autonomous_research_portfolio/kompas_pro_2/lanes/L10_RESULT.md",
      "status": "PLANNED",
      "run_evidence": {}
    }
  ],
  "notes": [
    "Planning manifest, not 10 spawned AI agents or run receipts.",
    "Private Alpha data remain in its own authorized plane; public Archive only contains approved public-safe descriptions.",
    "The sole $3 maximum is governed Sol research, not advance charging or Fable API authorization.",
    "Production promotion and W46 snapshot rewriting prohibited."
  ]
}
````

## K4. FULL FILE `research/programs/MARKET_ANTICIPATION_RESEARCH_PROGRAM_v1/RESEARCH_CONTRACT.yaml` (blob 979e40191372ae0eea17ea925c8a99479fc58112, sha256 bee0e63cec6aed0bdc6d952e6f644fd89bb1b5fb21be65e9840a94af32b2aa13, 71 lines, 2192 bytes). WP: WP5,WP9. market anticipation prereg contract.

````
schema_version: '1.0'
program_id: MARKET_ANTICIPATION_RESEARCH_PROGRAM_v1
status: FROZEN_BEFORE_ECONOMIC_RESULTS
research_question: >-
  Which point-in-time liquidity-routing, signal-failure, stress-propagation and
  regime-sequence features provide stable incremental early-warning information
  for Master Monday and RAW forecasts beyond the current framework?
primary_horizons:
  short: [6h, 12h, 24h, 48h, 72h, 7d]
  medium: [2w, 4w, 8w, 13w]
  long: [26w, 52w]
primary_targets:
  - next_horizon_direction
  - drawdown_probability
  - breakout_follow_through_probability
  - failed_move_probability
  - rotation_probability
  - regime_transition_probability
  - time_to_transition
baseline:
  description: current canonical and shadow framework inputs available at each historical timestamp
  comparison_required: true
anti_leakage:
  knowledge_timestamp_required: true
  revised_macro_vintages_required_where_available: true
  publication_lag_enforced: true
  final_holdout_sealed: true
  purging_required: true
  embargo_required: true
  no_hindsight_event_labels: true
validation:
  discovery: expanding_walk_forward
  robustness:
    - leave_one_era_out
    - alternate_source
    - alternate_frequency
    - specification_curve
    - block_bootstrap
    - event_cluster_robustness
  multiplicity_control:
    - holm
    - benjamini_hochberg
    - family_maximum_permutation
primary_metrics:
  - brier_score
  - log_loss
  - calibration_error
  - precision
  - recall
  - false_alarm_rate
  - median_lead_time
  - utility_under_asymmetric_drawdown_preference
promotion_gates:
  - incremental_out_of_sample_value
  - stable_direction_across_major_eras
  - no_material_lookahead
  - acceptable_false_alarm_burden
  - reproducible_by_independent_agent
  - source_lineage_complete
  - governance_approval
failure_conditions:
  - result_exists_only_in_price_levels
  - selected_lag_not_pre_registered
  - effect_disappears_out_of_sample
  - source_revision_explains_edge
  - result_is_redundant_with_existing_sensor
  - excessive_false_alarms
  - unstable_actor_attribution
  - economically_trivial_lead_time
framework_effect_before_promotion: NONE
portfolio_effect_before_promotion: NONE
````

## K5. EXCERPT `research/autonomous_research_portfolio/EVIDENCE_DECISIONS_AND_TOP10_v1.md` (blob 3bff958b85f00ada8b5b7463ba111c1ef47b8c89, sha256 of full file 51d62291ce548521b853366cb17700a52e48cf47acfd1056defc6f3d590cebd7) lines 1-56 of 86. WP: WP7,WP9. ARP evidence, scoring/selection and overlap decision; top-10 task list and budget sections (lines 57-86) omitted.

````
# ARP v1 | Evidence, negative results, portfolio decision and top 10 executable owner tasks
**Decision date:** 2026-11-07. **Repo snapshot:** `22b94f060e130586c62e4faba25f5097c39f30e5`. **Authority:** research coordination only, no market, wallet, release, credential, scheduling or paid dispatch authority. [Read the machine portfolio](PORTFOLIO_MANIFEST_v1.json) and [complete recipes](PRODUCT_RECIPES_v1.md).

## Verified current-state infrastructure and bounded evidence

| Evidence ID | Original source / exact Git blob | What is actually supported | Caveat |
|---|---|---|---|
| EV-HRE-01 | [Cross-era source-verified study](../historical_reality_engine/CROSS_ERA_RESULTS_20261107.md), blob `ddfd6d43e2f604d2003e7efedb68641c11f5b2e3`; [PR #2012](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/2012) and [Actions run 42391907367](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/42391907367) | Five selected 2022-26 event groups, two native independent replay jobs, fixed simple price baseline 8/46 BTC and 15/88 ETH severe overlapping daily windows, 18 source/time tests | Retrospective source archive ZIP/checksum is **not original first-known event-day model issuance**; overlapping outcomes not independent crisis sample |
| EV-HRE-02 | [Original pilot](../historical_reality_engine/NATIVE_FIRST_RESULTS_20261107.md); [PR #2010](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/2010), [Actions 42390995602](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/42390995602) | Actual native historical price-only work, source-clock bug in sampled exchange data, 2021 naive CN sample with two eligible complete weeks per asset | Repaired HRE research code does NOT prove canonical production source owner has same bug; all 2020-25 original investor warning skill unknown |
| EV-ALTS-01 | [Altseason source feasibility](../../06_RESEARCH_LAB/high_value_edge_research/EDGE-001_TSUNAMI/2026-11-05__ALTSEASON_SOURCE_FEASIBILITY_EXECUTION_V1.md), blob `ecc3496e6246fe7eda3b69bf1eb859339a921b28` | 18 input capabilities: 11 available but NOT admitted PIT, 6 missing, 1 unsafe; 0 admitted for combined portfolio tournament | 0/11 historically tested fixed reload policies beat HOLD in that specified sample, not universal proof that re-entry never works; no verified full-sized historical microcap sell |
| EV-ALPHA-01 | [HF Alpha source audit](../../06_RESEARCH_LAB/hugging_face_task2_audit_20261022/08_EXISTING_ALPHA_LAB_CODE_CROSSCHECK.md), blob `1c72da9ab50309804ab32221de24f8677a0bee46` | Existing HF Trenches experiment and GitHub workflow, potential source `tau` admission, test-set-aware numerical column choice, mutable `resolve/main`, missing split assertions | STATIC CODE AUDIT ONLY, 0 new tests run in that Oct 22 audit; Alpha owner must check current code before fixing |
| EV-NEWS-01 | [News source-to-decision audit](../../04_MARKET_LEARNING/external_research/news_intelligence/2026-11-04__NEWS_INTELLIGENCE_P0_SOURCE_AUDIT_EXECUTION_v1.md), blob `1ecd77916845f723396f9db276bb788284793655` | Four Nov1-4 Situation Room rows with 0 primary verified events despite 6/6 landing HTTP transport PASS; one frozen NEWSFT card vs N≥50 target | Timestamped historical short sample only; current global news recall or runtime health not established by this November 4 document |
| EV-MARP-01 | [Market Anticipation Research Program](../programs/MARKET_ANTICIPATION_RESEARCH_PROGRAM_v1/README.md), blob `a7a0c990bc829455bd00449a18792ac481f4eeb5` | Existing prior research tracks for liquidity routing, regime transition, market DNA, opportunity cost, stress propagation, institutions | Making standalone new liquidity engine would duplicate research scope; source/Actions runtime proof remains separately required |
| EV-HRV-01 | [Historical Research Vault](../historical_research_vault/README.md), blob `36f46294667e7ae3150e0128839d6ad3531ed010` | Existing DefiLlama owner, bounded SQD onchain replay, Coin Metrics limited public bootstrap, historical source registry | Repository and sample source files are not automatically licensed for bulk redistribution or PIT use |
| EV-ARCH-01 | [Agent instructions](../../AGENTS.md), blob `7c454fd27f56c339f923a1f07dec740fa79bed39`; [registry](../../00_ARCHIVE_CONTROL/SKILL_REGISTRY.md) | Existing Research Parallel Lanes and Skill Quality Gate, cross-repo separation, Round3 prospective-collection-only | RPL is a method, not actual five-agent worker execution. No extra automation, source promotion or paid authority |
| EV-ALPHA-02 | [Private Alpha Lab original #22](https://github.com/Donh91/Meme-Alpha-Lab/issues/22), main observed `048517f0e062623b75203d270cd9732f7ea5da5d` | Existing original autonomous wallet research and research loops, not another blank product | NO private Alpha source, token/wallet holdings or user data copied to public Archive |

Native HRE execution is *previous* verified work. **This ARP package itself has not launched five new native Actions experiments, does not claim Grok has returned a report, and has NOT placed a Sol MAX paid request.** The actual PR-specific CI will be evaluated on exact head separately.

### Hugging Face verified dataset discovery, bounded admission

- [RugPull1K](https://huggingface.co/datasets/fati-80-Sho/RugPull1K): dataset card claims 1,028 token projects, CC-BY-NC-4.0. Its midpoint-of-project observation is *not* token launch-time first-known; not admissible for production paper entries. Hub converted viewer metadata reports ~935,800 one-column rows while repository includes an XLSX, so actual schema/content needs independent inspection and reconciliation. No admission/weights training.
- [Instrumetriq Crypto Sentiment](https://huggingface.co/datasets/Instrumetriq/crypto-market-sentiment-observations): card documents 45 weekly Sunday samples from 2025-12-21 to 2026-11-01, 270+ assets, CC-BY-4.0, Feb 2026 methodology v1/v2 change. Observational and NOT a proof of 2020 historical first-known news or alpha. Tier3 full daily archive described as paid, not assumed in free access.
- [Chainticks DeFi liquidations](https://huggingface.co/datasets/Chainticks/defi-liquidations): CC-BY-4.0, public decentralized-protocol onchain liquidation events, ~3,200/22-column viewer rows with `source_kind=on_chain_event`. This is not a CEX margin liquidations/dealer exposure tape.
- [Ethereum transactions dump](https://huggingface.co/datasets/hilbium/ethereum-transactions): card ~517 GB and license `other`, not a bounded or legally qualified free dataset pilot. Prefer existing SQD/RPC scoped queries.

Viewer previews encountered rate limiting. **No raw sample download, unchanged HF commit hash, dataset split/class balance, exact publisher first-known revision, or full licensing audit was proven here.** Register as `SOURCE_REPAIR`, NOT research completion.

### Other external first-known verification leads

[Binance public archives](https://github.com/binance/binance-public-data), archived ZIP/checksum integrity and UTC candle close-time semantics; [FRED/ALFRED real-time periods](https://fred.stlouisfed.org/docs/api/fred/realtime_period.html), historic release/vintage knowledge; [CoinGecko history coverage](https://support.coingecko.com/articles/5723073761-what-granularity-do-you-support-for-historical-data), do not assume unlimited older intraday history in a free/demo account. These are **source candidates**, not locally certified original-event source rows, and all must be rechecked against current terms and source clocks.

## Scoring and selection method

Ex ante rubric, explicitly not empirical backtest success:

| Criterion | Weight |
|---|---:|
| Incremental prediction/decision value potential | 25% |
| Testability, historical and prospective source availability | 20% |
| Accumulating forward-learning value | 15% |
| Fit with existing GitHub runtime | 15% |
| Cross-framework reuse | 10% |
| Cost efficiency | 10% |
| Implementation simplicity | 5% |

Individual numeric criterion scores and exact weighted sums are in `PORTFOLIO_MANIFEST_v1.json`. **86.5, 82.3, 81.4, 79.4, 75.6** are human-reasoned *priority estimates*, with uncertainty ±9, ±13, ±14, ±17, ±15 points respectively. Pairwise ordering of #2-4 is not statistically meaningful. Execution order should favor the genuinely source-ready/cheap and unblock shared dependencies before engaging expensive models.

### Overlap decision versus HRE and existing owners

`HRE (historical truth tape + replay + false controls)` -> `Task2/#1827 (time admission + original issue)` -> `owner experiments with frozen baseline` -> `original due-only maturity and Strategist independent falsifier` -> `original owner PR + CI + governance` -> `S1 eligible closure only`.

ARP-01 consumes HRE but does NOT make another replay system. ARP-03 reuses Market Anticipation/EDGE and does NOT create another Global Liquidity Observatory. ARP-04 stays inside private Alpha Lab and cannot publish sensitive token/wallet data to public Archive. ARP-05 extends existing News P0 and is not another source crawl. ARP-02 improves whether any warning/action *matters*, without claiming trade authorization.

Cross-cutting source integrity is a necessary gate in all five, **not a sixth engine**. Historical replay supplies development counterexamples, not original event-time issuance or historical trade fills. The program's most important negative result can be `REJECTED` with the avoided maintenance bill.

````

## K6. EXCERPT `research/autonomous_research_portfolio/PRODUCT_RECIPES_v1.md` (blob 79527717e56011908011071b8f58cee79852cb58, sha256 of full file b68aad21ab4ddf0760ab11840935d69164310b7be69e44377ddaec83d68f4228) lines 1-28 of 99. WP: WP2,WP5,WP9. common contract, ARP-01 and ARP-04 recipes only.

````
# ARP v1 | Five autonomous research product recipes

**Status:** PRE-IMPLEMENTATION SCIENTIFIC DESIGN. **Evidence snapshot:** Archive main `22b94f060e130586c62e4faba25f5097c39f30e5`, 2026-11-07. All clocks, counts, costs and proposed tests are gated, not claims of newly executed research. Original owner policies override this coordination layer.

## Common research operating contract

Each package reuses the [Historical Reality Engine](../historical_reality_engine/README.md) episode atlas and historical research vault as input only; no second historical archive. Each registered hypothesis needs original owner issue, identifier, before-outcome model/feature/source SHA, source `event_time`, `source_published_at`, `first_available_at`, `request_started_at`, `response_completed_at`, `first_seen_at`, `first_used_at`, and freeze time, with field-specific precision and UNKNOWN. A file checksum verifies current archive bytes, **not** historical publication time. Store first-occurrence and full eligible universe, not only surviving winners. Outcomes live in existing due-only authority and retain missed, null, late, censored and failed rows.

Three mutually exclusive evidence classes: `ORIGINAL_ISSUED` (actual first-delivered forecast), `FROZEN_RETROSPECTIVE` (fixed current code replayed on historical period-legal knowledge, not an original past signal), and `CHALLENGER_DEVELOPMENT` (post-hoc model proposal, never evaluation holdout). Revisions do not alter preregistered hypotheses. No finding can directly change official Kompas, CN, risk state or trades. Existing Research Lab/Strategist review, scientific admission and original owner qualified release apply.

R0 owner, duplicate and fixed main census. R1 source rights, first-known/PIT validation. R2 one primary endpoint, fixed source cohort, baseline, falsifier and sample/stop budget. R3 bounded HRE historical experiment plus negative controls, no tuning on test. R4 immutable prospective shadow, maturity and failure logs. R5 deterministic falsification followed, only if marginally useful, by **separately evidenced** Grok Bridge red-team or policy-authenticated Sol MAX advisory. R6 small original-owner PR, exact-head CI, independent qualified review, main and natural consumer readback, retain or kill. Skill Foundry candidate only if repeated procedure has demonstrable uplift over existing skill/no-skill. Existing Skill Quality Gate remains independent and cannot itself register/promote.

### ARP-01 · Forecast Edge & Calibration Tournament

**Question/owner.** Does the official Kompas/Cycle Navigator actually improve price range, timing, direction or decisions compared with cheap alternatives? Original scientific owner [Task2 #1596](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596), original products [CN/Forward Path #1516](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1516), integrity [#1827](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1827), Strategist #1157. Existing CRE and forecast ledgers remain authoritative: **build a tournament view, not another forecaster**.

**Data.** Original issued 12h,72h,168h, 1-3d,5-7d and 2-3w source-qualified forecasts; frozen Monday weekly high/low intervals; hourly completed Binance spot candles, HRE first-known source QA and original model/config/scoring commits. Use price in exact quoted unit and never join USDT as if USD without an explicit price-source unit contract. Source rights from existing registry, not direct bulk transfer.

**Falsifiable experiments.** (i) 12h nowcast-copy versus persistence, volatility-adjusted direction and no-forecast abstention; (ii) 1-3d joint high/low, range width+placement and break probability against fixed naive volatility bands; (iii) 5-7d interval width/containment/pinball proper scoring with Monday freeze; (iv) 2-3w calibrated risk and horizon consistency against no-change. Score each by asset, horizon and regime; paired temporal blocks with purge/embargo and uncertain effective N. Primary endpoint is out-of-sample width-adjusted interval proper score versus the strongest frozen cheap benchmark; direction Brier/log loss only if probability genuinely issued pre-outcome. A claimed 80% interval covering 100% via huge width is NOT precision.

**Historical/prospective.** HRE 2020-26 gives period-legal price baselines and source failure cases. Historical issued forecast comparisons are restricted to real original-issued 2026 clock. Prospective W46 onward freeze same T0 for baseline/challenger/official, mature 12h-21d before scoring. Retain ALL false directions and unissued slots. No synthetic blue forecast line.

**Parallel jobs.** Existing PR-only Research Parallel Lanes CI can independently run (A) issuer/denominator/source-clock census, (B) hourly actuals/interval scoring, (C) reference baselines and chronological ablation. They share immutable snapshot but not labels when fitting. No schedule creation. Grok attacks alternative explanations and leakage; optional Sol MAX only if model-selection uncertainty survives deterministic trials. Candidate skill: `forecast-first-known-proper-score-auditor` **only after** repeated score reconciliation failures.

**R0-R6 acceptance.** R0 current #1596/#1516. R1 original-delivery and source clock admission. R2 freeze 12h and weekly baseline. R3 HRE historical price-only non-promotional. R4 source-frozen prospective independent cohort. R5 leakage, regime and abstention review. R6 only source/code repairs under original issue when qualified; later model promotion demands stronger separate scientific review. **Kill:** no robust prospective paired skill after two eligible chronological slices; if missing source, WAIT not claim failure. **Cost planning:** 12×6 ≈72 standard Actions minutes/month, $0 default.

**First three work items:** (1) issue/forecast census with original 12/72/168h issue IDs, lineage and gaps; (2) naive width-penalized W46+ range benchmark; (3) frozen 12h nowcast/persistence shadow comparator, no official edit.

````

## K6. EXCERPT `research/autonomous_research_portfolio/PRODUCT_RECIPES_v1.md` (blob 79527717e56011908011071b8f58cee79852cb58, sha256 of full file b68aad21ab4ddf0760ab11840935d69164310b7be69e44377ddaec83d68f4228) lines 61-78 of 99. WP: WP2,WP5,WP9. common contract, ARP-01 and ARP-04 recipes only.

````
### ARP-04 · Microcap Survival & Executable Alpha Evidence

**Question/owner.** What can actually be discovered *and exited* at positive net expected value? Original **private** [Meme-Alpha-Lab #22](https://github.com/Donh91/Meme-Alpha-Lab/issues/22), sellability #98, wallet #88, outcome #77. Do not mirror private source/tax/wallet content in this PUBLIC folder, no second scanner or paper wallet.

**Data.** Exact chain+contract+pool launch time, deployer/creator ancestry, holder concentration and funded buys, independent wallet behavior, bundled launches, LP deposits/removals, first-known social post, bid/route/capacity, full-position executable sales, reverted trades, gas, slippage, MEV and later failure/zero-liquidity outcomes. Current original Alpha HF Trenches ablation already exists; do **not** build duplicate. Existing Oct 22 static audit flags feature `tau` evidence, train/test-wide unsupervised column selection, `resolve/main` mutable download and split membership; tests still required.

**Independent Hugging Face qualification.** RugPull1K claims 1,028 projects, CC-BY-NC-4.0 and truncates features at *project midpoint*, which is not the same as prospective token launch cutoff. Viewer reports one text column and 935.8k apparent rows, so exact cohort/schema is **NOT VERIFIED**. Research-only and no commercial deployment. Chainticks DeFi liquidation events are on-chain protocol liquidations, not a venue-wide centralized exchange liquidation heatmap. Huge `hilbium/ethereum-transactions` (~517 GB, license other) is *rejected as bulk import*: use bounded original SQD/RPC chunks. This is not a free, preevent wallet-alpha oracle.

**Hypothesis and falsifier.** A frozen wallet+liquidity+creator risk lens selects more *sellable* survivors than momentum-only and unbiased token-minted census at fixed entry notional, without false positive/false negative risk inflation; net gain must survive full-position exit mechanics. Falsifier: survival label correlates with selection/leakage, costs erase alpha, token vanishes/untradable, or independent future tokens fail.

**Historical/prospective.** Source PIT token and dead-token census, not winners-only top gainers. Counterfactual historical token source reconstruction cannot prove original real-time discovery unless T0 evidenced. Prospective accepted source capture, due-only 1d/3d/7d/30d returns and full-size exit feasibility, failed transactions explicitly losses/UNKNOWN.

**Parallel jobs.** (A) HF dataset pin/schema/time/split QA, (B) bounded exact-chain creator/funding on-chain deterministic replay, (C) independent notional sellability slippage and loser cohort. Grok reviews wallet-control assumptions and rug categorization; Sol only for source-bounded contract ambiguity not execution. Skill candidate: `microcap-realizable-outcome-test` evaluated against original Alpha scripts.

**R0-R6.** R0 check Alpha original live owners and heavy lane constraints; R1 first-known and rights; R2 baseline and fixed losing universe; R3 limited forensic replay; R4 frozen prospective full-cohort; R5 adverse capacity/slippage/control review; R6 only Alpha original owner PR/test and main readback. **Kill:** no historical live-capacity proof or net returns vanish under friction. **Cost:** 12×12 ≈144 min/month, $0 default.

**First three:** (1) repair/verify prior HF timestamp/train-only/source SHA complaints; (2) source-clocked bounded 30-token winner/loser/zero-sell cohort; (3) full-position sellability on Alpha #98 with explicit capacity before any edge claims.

````

## K7. DERIVED FIELD EXTRACT `research/api_agent/outputs/research_lab_sol/ARP01-FORECAST-EDGE-CALIBRATION-SOL61-MAX-20261107/issue-1476/comment-6714216846/RESEARCH_LAB_SOL_ANALYSIS.json` (blob 0911c02b5ee4705ba7c232f676b77f745687c31b, sha256 of full file f36059602a3b8051b0dd6909afbdf58fd0e80b790d67ef6a91b2fb9b79392ab4, 29775 bytes, single-line JSON). Keys summary, evidence_against re-serialized with json.dumps(indent=1, ensure_ascii=False); values are verbatim, formatting is not byte-exact; other keys (evidence_for, forecast_candidates, hypotheses, status, uncertainties) omitted. WP: WP5,WP9. ARP01 Sol output: summary and evidence_against.

````
{
 "summary": "VERDICT=INSUFFICIENT_EVIDENCE; MODEL_USED=gpt-6.1-sol; NO_CODE_WRITE_PERFORMED; NO_AUTHORITY_CHANGE; The narrow original-owner evidence-gap hypothesis survives as a supported research priority, not a measured highest-expected-value result. #2002 already corrects the batch-window/candle-clock interpretation, and #2022 already supplies substantial declared-time, quote, maturity and warning gates; duplicate repairs are rejected. Original first-known/delivery denominators, a qualified proper-score comparison and independent prospective skill remain unproven. Static review identifies an intrahour-extrema qualification issue and a leading-slot denominator counterexample, but not their realized incidence or a deployed production failure. W46 is future at the frozen cutoff. The three bounded tests prioritize its authentic original issuance, then an unchanged 30/60-day tournament, then warning diagnosis with economic utility separately gated. VERIFIED below means supplied-code inspection or arithmetic conditional on supplied records, not native execution or canonical truth. No code/tests were executed, no external reads or provider calls were made, and no model report establishes edge.",
 "evidence_against": [
  "REJECTED duplicate diagnoses — Reopening the 55-batch-ending problem as missing hourly data would contradict the supplied repaired code. Re-proposing Goal2 Graph B N1/N2 patches is also unsupported: the earlier advisory itself reported corresponding implementation already visible. The current packet contains neither that renderer's source nor a fresh deployment receipt, so present hosted qualification remains UNKNOWN. Earlier scheduler, freshness and paid-claim concerns cannot be carried forward as verified current defects from an older assistant report.",
  "VERIFIED static counterexample to an overly broad post-issue claim — The W44 first retained hourly row opens at 06:00 and closes at 07:00, but the freeze is 06:57:49. Its full-hour low/high can include 57 minutes 49 seconds before issuance. The generic score_weekly_pair also selects by completed endpoint, not by the start of the OHLC observation interval. This does not invalidate the locked 162-endpoint descriptive record; it does prevent automatically calling all included extrema wholly post-issue. Actual contamination of the reported global extrema is UNKNOWN.",
  "VERIFIED static counterexample to self-certified complete risk grids — audit_pullback_episode constructs its expected timestamps from len(slots). In the supplied four-slot fixture, deleting the earliest slot leaves a contiguous suffix that passes that construction. The existing test removes an interior slot, so it does not address this case. An independent declared window is necessary to certify the denominator. Furthermore, no proven early delivery is not equivalent to a proven missed warning when source or delivery evidence is unknown.",
  "VERIFIED limitation, not proof of an absent systemwide gate — _is_sha checks hexadecimal shape, not ancestry, publication time or object relationships. score_weekly_pair checks outcome count/first/last metadata, not the underlying timestamp ledger or extrema derivation, and it has no independent current-as-of authentication. Its supplied fixture uses different custody/model hashes, which can be legitimate if their relationship is externally attested. The Wave B documentation explicitly assigns such authentication to callers. Claiming that these pure gates alone certify original issuance, contiguity or live maturity is rejected; claiming callers lack the required evidence is also unsupported.",
  "REJECTED score overclaims — A wide joint minimum/maximum band is not a central probabilistic interval for a scalar closing price. No nominal quantiles or joint predictive distribution are supplied for W44. Its 2/2 containment cannot establish calibrated precision or alpha, and Jaccard is not a proper probabilistic score. The W44 build function also locks in known containment outcomes and expects the BTC daily-price-path status UNAVAILABLE; this reconciliation cannot stand in for an untouched seven-daily-close prospective trial.",
  "VERIFIED arithmetic conditional on the HRE matrices — Across 418 daily cutoffs per asset, BTC baseline TP/FP/FN/TN totals are 8/16/38/356 versus candidate 11/25/35/347; ETH totals are 15/24/73/306 versus 22/39/66/291. The candidate adds three caught BTC severe windows alongside nine false-positive windows, and seven caught ETH windows alongside fifteen false positives. Net warning counts rise by twelve BTC and twenty-two ETH rows, not necessarily that many exact paired disagreements. Without joint predictions, exact disagreement is UNKNOWN; compatible bounds are 12–60 of 418 BTC rows and 22–100 of 418 ETH rows. These are overlapping selected-era cutoff counts, not independent crisis hit rates.",
  "VERIFIED conditional false-positive/false-negative trade-off, not economic value — With constant hypothetical per-cutoff error costs c_FP and c_FN, candidate minus baseline loss is 9*c_FP - 3*c_FN for BTC and 15*c_FP - 7*c_FN for ETH. It is lower only when c_FN/c_FP exceeds 3 and 15/7 respectively, assuming positive costs. No such costs are evidenced. Overlapping labels, repeated alert episodes, unknown era availability and absent execution mean these are classification-loss identities, not investable break-even ratios. At most five selected event families are represented across both assets; two compute jobs do not create independent market cohorts.",
  "VERIFIED arithmetic; REJECTED cross-target transfer — In LATEST.json's 24 matured ETHBTC 7d binary rows, ALWAYS-POSITIVE is correct on 22/24, versus C02 on 9/24. C02 avoids two false positives but misses fifteen positives and differs from ALWAYS-POSITIVE on seventeen rows. A hypothetical error-cost model favors C02 only if false-positive cost exceeds 7.5 times false-negative cost. The earlier 23-row statement's ratio above 7 is not the current aggregate and cannot be added as an independent sample. Neither snapshot is broad-altseason evidence or an economic policy test; both concern one correlated block.",
  "SUPPORTED adverse temporal/economic evidence — The supplied summary reports a historical strategy return changing from 17.54475% with zero extra delay to -4.978081% with one extra day, a -22.522831 percentage-point difference. Raw common-timestamp paired economics are absent, so this is sensitivity evidence, not reproduced after-cost utility. The preserved derivative null, breadth deterioration, rejected ETF strong-edge claim and historical 0/11 reload policies beating HOLD oppose assuming that adding indicators or acting on warnings necessarily helps.",
  "REJECTED premature acceptance or failure — Synthetic passing cases, reported merges and checksum-validated retrospective archives cannot prove W46 issuance, public delivery, calibrated skill or investor benefit. Conversely, an original W46 forecast absent from a November 7 packet cannot be called a missed November 9 issuance. The earlier Goal2 INSUFFICIENT_EVIDENCE verdict is neither automatically ratified nor overturned: new research-clock/gate implementation is visible, while the decisive original-source and prospective economic evidence is still missing."
 ]
}
````

## K8. DERIVED FIELD EXTRACT `research/api_agent/outputs/research_lab_sol/ARP04-MICROCAP-SURVIVAL-EXECUTABLE-ALPHA-SOL61-MAX-20261107/issue-1476/comment-6720273819/RESEARCH_LAB_SOL_ANALYSIS.json` (blob f8c270f803c540a43787e4a4e11deb921c4086fe, sha256 of full file 54ae7a457c4427c646df3c2ef6bad15d23189697ed5c7dee9cff14915b5d0194, 23493 bytes, single-line JSON). Keys summary, evidence_against re-serialized with json.dumps(indent=1, ensure_ascii=False); values are verbatim, formatting is not byte-exact; other keys (evidence_for, forecast_candidates, hypotheses, status, uncertainties) omitted. WP: WP2,WP9. ARP04 Sol output: summary and evidence_against.

````
{
 "summary": "VERDICT=INSUFFICIENT_EVIDENCE; MODEL_USED=gpt-6.1-sol; NO_CODE_WRITE_PERFORMED; NO_AUTHORITY_CHANGE; The supplied Trenches experiment evaluates first-sighting lifecycle completion, not prelaunch discovery or sellable 5x/10x outcomes. Previously documented PIT, train-selection and split qualifications remain visible, but their measured impact and current original-owner deployment are unknown. One additional static admission edge case permits file-order selection when decision_ms is absent; its real incidence and economic effect are UNKNOWN. No qualified clean-G3 buyer ledger, complete non-survivor denominator or whole-position after-cost comparison is supplied. Specific evidence gates are SUPPORTED, but the prevalence claim that many labels fail is unmeasured. Economic identification remains WAIT_SOURCE, not proof of zero alpha or justification for another model, wrapper or trading system. Three conditional existing-owner test specifications are provided; none is executed, registered or authorized.",
 "evidence_against": [
  "FALSIFICATION FIRST / VERIFIED safeguards — The supplied implementation is not indiscriminately using outcomes as predictors. Its explicit feature lists exclude path_completed, reach/X and the named curve-progress proxies. The pipeline fits its imputation, scaling and logistic model on training data. It validates a one-to-one merge, rejects empty split lists and explicitly labels smart_degen_count secondary. These safeguards weaken any blanket allegation that all observed discrimination must be direct target leakage. No supplied run establishes whether the remaining qualifications materially alter metrics.",
  "REJECTED inference — path_completed is explicitly a chain-reading lifecycle-completion label, not profitability, sellable survival or a realizable 5x/10x multiple. A future outcome can legitimately serve as a target; its post-decision occurrence is not itself feature leakage. The unresolved questions are predictor availability, training-label maturity, sample selection and whether the target answers the economic question. Even perfect graduation classification would not establish executable alpha.",
  "REJECTED description of the present experiment — A first-sighting/post-launch feature table is not a demonstrated prelaunch opportunity set. The script does not verify launch identity or require a launch clock, and a row timestamp is not field availability. Likewise, immutable historical chain events could support a declared retrospective replay, but a later dataset revision or vendor annotation cannot prove original contemporaneous discovery, receipt or issued use.",
  "CONFLICTED — The script joins on mint within its declared Solana/pump.fun source scope; it does not independently verify chain, pool or venue identity. It selects from available feature rows and an inner label join, then excludes null targets during evaluation. Counts alone do not explain unmatched or censored candidates. These operations may be appropriate for a limited descriptive replication, but cannot certify a complete minted-token, dead-token or investable economic denominator. Actual bias and its magnitude remain UNKNOWN.",
  "SUPPORTED adverse baseline, with transfer rejected — ROUND2_TERMINAL_RESEARCH_DECISION.md reports zero of 11 reload policies and zero of three liquidity cohorts beating HOLD in its 35-symbol price/volume study, with survivorship and universe fragility. That is a scoped negative result, not a wallet/G2 comparison or a microcap executable-exit test. Its event anchors cannot be pooled with Trenches tokens as independent evidence. Earlier Goal5 and ARP02/03 Sol outputs are prior analyses, not independent microcap replications; their warning and ETHBTC statistics cannot supply missing Alpha performance.",
  "FALSIFIER NOT MET — No supplied experiment jointly demonstrates licensed source custody, original first-known availability, uncontaminated temporal/operator holdouts, a non-survivor denominator, whole-position executable economics and net improvement over frozen G2 plus trivial controls. This absence does not prove such evidence does not exist elsewhere. Conversely, source absence makes the new-model claim untestable; it is not a measured negative return or automatically a repository defect. Qualified prospective after-cost underperformance would reject the tested economic claim, while missing evidence leaves it UNKNOWN."
 ]
}
````

## R1. EXCERPT `06_RESEARCH_LAB/astra_program_20261116/results/compass_total/ASTRA_COMPASS_TOTAL_RESEARCH.md` (blob 767abd57f2bfadcb05d1a52b7187076f349122e3, sha256 of full file cf072b3cf7f674e94522a85c7660bad309cd67c57dcb08f2b2ca35e7bffacc45) lines 1-70 of 1403. WP: WP5,WP9. prior Astra Compass Total: executive decision.

````
# Kompas Pro: source-to-decision architecture and scientific audit

**Scope:** supplied public source packet, identified as main `82f6cd830fbcd26d77e043da0ad3222abd7cae92`  
**Original owners:** integrity **#1827** · research **#1596** · Cycle Navigator/forward output **#1516** · risk/protection **#1553**  
**Status:** **READ-ONLY AUDIT — IMPLEMENTATION AND SCIENTIFIC REVIEW PENDING**

This is an audit of the supplied text, not a repository execution or current-market assessment. I have not independently verified the main commit, recomputed the supplied file hashes, opened referenced-but-unsupplied files, inspected GitHub runs, accessed private data, or contacted another model. “ASTRA HIGH” is treated as the requested audit standard—not as proof that this response came from a dispatched Astra API run.

**Independent Claude scientific review is required before adopting this audit’s research recommendations or consequential implementation changes.**

---

## 1. Executive decision

### What the supplied sources establish

Kompas has a recognizable, substantially governed architecture:

1. Autonomous evidence feeds an **Auto Market State** owner.
2. Native Handlekompas reads that state without making new provider calls.
3. Official Compass combines the current state with structured Cycle Navigator context.
4. Weekly CN and Master Monday provide distinct frozen/contextual ownership.
5. Protection, re-entry and SELL are deliberately separated.
6. Public builders project those sources into site artifacts.
7. Shadow and strategic research have separate bindings and restricted authority.

Several important safeguards are actually visible in code:

- Missing data is not universally converted to zero.
- Repeated identical hourly observations can be distinguished from genuinely flat prices.
- The current 12-hour lane explicitly says **observed momentum, not forecast**.
- Retired breadth/ETHBTC action proxies have zero action weight.
- CN prose is not parsed into protection signals.
- SELL remains unavailable without a governed decision owner.
- Original Official source clocks are preserved in several downstream checks.
- Official freezes resist ordinary rewriting.
- Shadow research does not grant action permission.

### What the supplied sources do **not** establish

They do not establish:

- a currently functioning end-to-end **LIVE** producer → issuance → Pages → consumer chain;
- a complete current source census;
- independently verified first-known histories;
- calibrated probabilistic path envelopes;
- demonstrated turn-timing or drawdown-depth skill;
- a beneficial live escalation from 3/5 to 4/5;
- a functioning dynamic buy/sell action policy;
- sufficient independent long-horizon outcomes;
- economic value after realistic delivery delays, costs and opportunity costs.

### Principal conclusion

> **The strongest justified improvement is not a more elaborate prediction engine. It is a trustworthy issuance-and-delivery chain, consistent source admission, explicit horizon semantics, and paired prospective evaluation of a small number of existing research candidates.**

The most consequential source-visible defects are:

1. **Uneven integrity verification:** Auto Market State admission is weaker than prior-Compass admission.
2. **Source-hash-only event deduplication:** CN-only protection changes can be missed.
3. **Protection state-machine gaps:** re-entry watch can disappear while risk remains elevated, and REVIEW can persist without renewed constructive confirmation.
4. **Decision-health inconsistencies:** the Official builder, Native builder and event watcher do not apply identical completeness gates.
5. **Publication truth gaps:** “request,” “issued,” “built,” “deployed” and “delivered” are not established as the same event.
6. **Public weekly admission gaps:** the top-level site snapshot consumes weekly material before proving the same custody checks used elsewhere.
7. **Semantic overstatement risks:** `NEXT_12H`, 5/5, hardcoded horizon ETAs and repeated weekly projections can look more predictive than their implementation warrants.

None of these findings justifies inventing new market thresholds, retroactively changing W46, scoring W47 from this packet, or promoting a model.

---

````

## R2. EXCERPT `06_RESEARCH_LAB/astra_program_20261116/results/compass_edge/ASTRA_COMPASS_EDGE_SCIENCE_RESEARCH.md` (blob ef7f3b54c84ca5d89ec522058b94269d60584cdd, sha256 of full file 201c1c6d5e50a67e49d10d406ffc49a436138fb47f7e6649116455fff3161b88) lines 1-35 of 812. WP: WP5,WP9. prior Astra Compass Edge: executive judgment.

````
# ASTRA HIGH — Mission 3/5
## Scientific design review for a next-generation Kompas

**Supplied source-main:** `82f6cd830fbcd26d77e043da0ad3222abd7cae92`  
**Disposition:** **RESEARCH DESIGN / STATIC SOURCE REVIEW / SHADOW ONLY**  
**Execution:** No tools, code, repository writes, external retrieval, paid dispatch, or trading performed.  
**Evidence boundary:** Supplied text was inspected; file bytes, SHA digests, Git ancestry, publication receipts, and current repository state were **not independently verified**.

**This is not a repetition of the prior W46 assessment. W47 is not scored here. No new market outcomes are introduced.**

## Executive judgment

The defensible next-generation Kompas is **not initially a larger predictive model**. It is an existing-owner forecasting system that can demonstrate, separately:

1. **What information was genuinely available before issuance;**
2. **What exact forecast was actually issued, and when;**
3. **Which independently observed outcome became known afterward;**
4. **Whether the forecast improved on simple, same-clock alternatives;**
5. **Whether any improvement survived dependence, model selection, abstention, and implementation costs.**

The supplied code materially improves what can be inspected compared with the earlier report: A’s formula, calibration procedure, scoring implementation, and internal digest definition are now visible. But it also exposes important unresolved methodological risks:

- Filtering historical bars by their **event time** does not prove those exact data vintages were available at issuance.
- A’s model-origin clock, A’s own publication, B’s own publication, and consumer delivery are distinct.
- A’s weekly decision logic can accept sufficiently populated but unfinished weeks and can overlook unresolved earlier weeks.
- B’s scoring route expressly lacks verified **B-first-issuance** evidence.
- A’s probabilistic close intervals and CN’s uncalibrated range envelopes do not have equivalent forecast semantics.
- B’s directional probabilities are, algebraically, **identical across BTC and ETH for identical views and horizons**, despite different volatility inputs.
- Historical evidence-index membership does not establish predictive feature use.
- No supplied evidence establishes an LSTM advantage, calibrated official probabilities, or risk-to-action economic value.

**Priority:** repair and test scientific admission before expanding model complexity. Preserve official ownership; treat every research challenger as an unpromoted alternative.

---

````

## R3. EXCERPT `06_RESEARCH_LAB/astra_program_20261116/results/compass_warning/ASTRA_COMPASS_EARLY_WARNING_RESEARCH.md` (blob 2e8c7b946021c79116b66f915bcb6e5200be56b6, sha256 of full file c62b860b2359ef08b2a11573028767779a8ee8a08dcac9c0e16cd3793d0bb496) lines 1-21 of 649. WP: WP3,WP5,WP9. prior Astra Compass Warning: executive finding.

````
# ASTRA HIGH mission 4/5 — early deterioration and cycle/rotation research

**Requested source-main:** `82f6cd830fbcd26d77e043da0ad3222abd7cae92`  
**Disposition:** **RESEARCH DESIGN ONLY — no live threshold changes, trades, backtest results, promotion, or new delivery claim.**

## Executive finding

**A move from 3/5 ELEVATED to 4/5 HIGH could be legitimate before a drawdown—but this packet does not establish that such an upgrade was warranted, issued, delivered, or actionable in any particular episode.**

Three questions must remain separate:

1. **Was HIGH permitted by the then-effective risk contract?** The actual protection contract, upstream producer and refresh logic are not supplied.
2. **Could legally available evidence have supported an earlier HIGH assessment?** Potentially, but this requires point-in-time inputs, a rule fixed before evaluation, independent episodes and matched-warning-budget controls.
3. **Would the warning have protected capital?** That additionally requires actual delivery—or explicitly simulated counterfactual delivery—plus feasible quotes, a separately specified response and complete costs.

The best research direction is **not a more elaborate crash narrative**. It is a source-admitted test of whether **deteriorating resilience and failed recovery add useful warning time beyond price/volatility**, without increasing false alarms, warning occupancy or false-exit harm. This follows the supplied research constraints; it is not an established finding. [S1–S3, S6, S8]

W46 remains **exposed development material**. This mission neither re-scores it nor invents an earlier alert. W47 is not scored here. [S2, S7, S8]

---

````

## R4. EXCERPT `06_RESEARCH_LAB/astra_program_20261116/results/alpha_lab/ASTRA_ALPHA_LAB_PRO_PAPER_EDGE_RESEARCH.md` (blob b1f444a7f23a96d70c9aa9e5f27ee686d2cee4fe, sha256 of full file a3c5880525057846dadf80ee90ac40cbfe6a59e8144c398f3323a3a49184a16b) lines 1-46 of 1531. WP: WP2,WP6. prior Astra Alpha Lab: executive finding and limits.

````
# Alpha Lab Pro: execution-truth research and paper-wallet architecture

**Supplied source-main:** `82f6cd830fbcd26d77e043da0ad3222abd7cae92`  
**Disposition:** **DESIGN_AND_RESEARCH_ONLY — NOT IMPLEMENTED, NOT PERSISTED, NO TRADING AUTHORITY**

## Executive finding

The supplied evidence supports a disciplined research architecture, but **does not establish a profitable Alpha Lab strategy, verified paper returns, or superiority over a simple executable baseline**.

In particular:

- Matched original v4 **decision → fill → exit → costs** records are absent.
- The site handoff reports **zero verified full exits in its reviewed paired-ledger census**. That is a source assertion about that census—not proof that no exits exist anywhere.
- Historical winners, screenshots, market-cap changes, project quality, wallet labels and graduation outcomes cannot substitute for executable, costed returns.
- Five separate paper wallets can be specified realistically, but they cannot be activated by silently creating the scanner, scorer, ledger, wallet sensor or scheduler that existing contracts prohibit.
- The highest-value next work is **denominator integrity, original first-known clocks, exact identity, full-size exit evidence and deterministic execution accounting**, not another alpha score.

**Current conclusions**

| Question | Finding |
|---|---|
| Did original v4 generate realized profits? | **NOT_EVALUABLE** |
| Did original v4 generate independently verified paper profits? | **NOT_EVALUABLE** |
| Do wallet precursors outperform public price/liquidity information? | **HYPOTHESIS; not demonstrated here** |
| Can project research identify interesting candidates? | Historical examples support investigation, not trading edge |
| Are manual discoveries proven scanner misses? | Not without original eligibility and discovery logs |
| Is launch-origin information potentially useful? | Plausible risk information; profitability remains unproven |
| Can a realizable paper architecture be designed? | Yes, conditionally, through existing owners and approved extensions |
| Is a public, near-live Alpha Lab Pro feed established? | Not by this packet |

### Scope and verification limits

I used only the supplied text. **No tools, execution, repository reads, private access, independent SHA verification or deployment inspection occurred.**

Throughout:

- **SUPPLIED FACT** means explicitly stated in a supplied file.
- **SOURCE ASSERTION** means the file reports an external or operational condition not independently reproduced here.
- **HYPOTHESIS** means a falsifiable research proposition.
- **PROPOSAL** means a future design, not an approved implementation.
- **UNKNOWN** is not zero, false, safe or failed.

Required current cockpit, boundary, registry, skill and private binding files were not supplied. Consequently, this report does not certify current authority, current issue status or implementation readiness. Work requiring unavailable private authority must remain blocked as `PRIVATE_DATA_AUTHORITY_UNAVAILABLE`; the public-only architectural analysis can still proceed.

---

````

## R5. EXCERPT `06_RESEARCH_LAB/astra_program_20261116/results/maeve/ASTRA_MAEVE_TASK2_RAW_REPORT.md` (blob 3d0915bd12d0907a36cd15e3ad4c644a48b16c58, sha256 of full file 10bce9dc190b0a55065e971d6f71e04ae186799cba71170f2634e4b5f807d597) lines 1-19 of 652. WP: WP2,WP7. prior Astra MAEVE: decision.

````
# ASTRA_MAEVE_TASK2_PREP_V1

**Source commit:** `1ebf45acc3004fbf4e6387e6db1e3dcabe1338aa`  
**Status:** `RESEARCH_ONLY / PUBLIC_SOURCE_REVIEW / EXPERIMENT_SPECIFICATION_NOT_EXECUTED`

## Decision

**The frozen question is not yet answerable from the supplied public evidence.** The archive supports a substantial recovered MAEVE action history, but it does not establish the complete historical opportunity set, eligible NONE denominator, or a sufficiently complete point-in-time feature join. Nor does it contain eligible results demonstrating incremental Kompas forecasting or warning value.

The immediate deliverable is therefore:

> **An audited action/opportunity contract, followed by deterministic time-valid joins and matched simple-model tests—not a larger behavioral model or a transfer recommendation.**

I read all **11 supplied source texts**. Their linked archives, private rows, manifests, underlying result files and script dependencies were **not opened or independently verified**. Counts and hashes below are attributed to those sources, not reproduced calculations.

**Transfer candidates nominated: 0.** Eligible deterministic result tables must exist and receive independent review first.

---

````

## R6. EXCERPT `06_RESEARCH_LAB/astra_program_20261116/results/s1_vnext/ASTRA_S1_VNEXT_RESEARCH.md` (blob d2782b4c92c20218b31ff2eef6e235a718799ca9, sha256 of full file b20e7e940c2cdbb6f6dd4339193eb5295d2be41d4dde6bf9f37cb929c8506785) lines 1-29 of 881. WP: WP8. prior Astra S1 vNext: executive determination.

````
# Supervisor vNext — adversarial architecture review

**Scope:** original #1156; existing S1 task `6ae5fd466b48819187abc224ec0f1c5f`; supplied source-main identifier `82f6cd830fbcd26d77e043da0ad3222abd7cae92`.

**Disposition: DESIGN REVIEW ONLY — NOT ADOPTION-READY.**

I examined only the supplied text. **No tools were invoked, hashes recomputed, repositories inspected, tests executed, reviews requested, or production changes made.** The supplied SHA-256 values identify the evidence packet; they are not independently validated checksums here. This response is adversarial analysis, **not an authenticated detached-review receipt, native GitHub approval, owner consent, or an Astra/API execution claim**.

**The original Claude review of the final integrated proposal remains required before adoption.** The supplied Claude adjudication does not review this recommendation or a final implementation. [V, Verdict; D, §10]

## Executive determination

The safest coherent direction is **an incremental, source-bound steward inside the existing S1 task**, not a replacement supervisor:

1. retain GitHub/main as policy authority;
2. make planning and classification explicitly non-authorizing;
3. authenticate evidence separately from evaluating it;
4. use one designated original-branch writer;
5. separate independent technical review from release authority;
6. reconcile uncertain mutations before attempting another;
7. distinguish merge verification, natural consumer verification, and attributable S1 closure;
8. make Claude optional **only after** a governed reviewer-admission change—not by ignoring today’s Claude-specific lane. [A, §§0.2a–e; O, Remediation and Codex; D, §§1–3, 7]

The principal risks are not insufficient intelligence. They are **identity ambiguity, policy/implementation divergence, incomplete dependency boundaries, non-atomic mutations, and evidence that can be asserted more easily than authenticated**. The supplied code explicitly acknowledges that its classifications do not authenticate callers; current lane policy also acknowledges shared-account review-authentication risk. [C, module and classifier docstrings; A, §0.2e(d)]

**Do not apply the frozen Claude v2 package byte-for-byte.** Its supplied adjudication reports four stale base pins at its own comparison snapshot, accepts the forged-counter and self-review objections, and leaves D4–D8 unverified. That is sufficient to reject blind application, but not sufficient to establish the state of today’s repository. [V, D1–D8]

---

````

## END. End of bundle. Anything not shown above is OPEN.
