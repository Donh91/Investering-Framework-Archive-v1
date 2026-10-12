# Alpha Lab — Ten Sequential Research Missions (API-native, existing owners)

Date: 2026-10-12
Status: PREREGISTERED_DESIGN_ONLY; ROUND_1_READY_FOR_DETERMINISTIC_ADMISSION; NO HISTORICAL TRADE RESULTS CLAIMED
Primary governance: Archive #1340 (full candidate/outcome denominator), #1512 (specialist research), #1476 (one active Sol API mission), #1087 (Alpha owner), #1339 (alert receipt).
Related drafts: #1579 (tri-chain forensic cases), #1585 (REA mission 007). Neither draft is deployed merely because this document exists.
No new scanner, ledger, scheduler, API budget, token/portfolio action or execution keys.

## Purpose
Move from impressive retrospective token returns to *point-in-time discoverable, executable, independently validated* edge. Reuse existing MAL S1 sellability, S2 wallet history, S3 relationship, S4 Pons curve/retention, S6 distribution, S7 attention, Project-to-CA, and canonical #1340 candidate/outcome evidence. REA is an optional bounded tool under mission 007, **not** a dependency for these ten research rounds.

## Dependency order, one paid/heavy mission at a time
| Execution | Original rank | Mission | Owner | Deterministic work allowed now | Heavy / edge gate |
| --- | --- | --- | --- | --- | --- |
| R1 | #4 | Executable Moonshot | MAL S1, #1340 | Verify chain/CA, first source-time, historical pool/trade coverage, cost assumptions, outcome horizon availability | API synthesis only after frozen eligible historical case+control; historical never prospective |
| R2 | #2 | Synthetic Demand X-Ray | MAL S3 + S2 | Source-time funder/transfer graph; CEX/bridge/router negative controls | No entity claim from shared infrastructure |
| R3 | #6 | Graduation & Liquidity | MAL S4/Pons | Freeze complete launch/graduation cohort, failures included | Cannot select winners only; migration route+liquidity evidence |
| R4 | #1 | Second Wave | MAL S4/S7/#1340 | Predefine survivor denominator and 15m/1h/6h/24h/7d windows | New forward observations with baseline and exit realism |
| R5 | #3 | Project→CA | Existing Project→CA | Start passive signed/public project-watchlist capture NOW | No early identity claim absent authenticated deployer relation |
| R6 | #5 | Smart Money DNA | MAL S2 | Bound complete wallet history, failures, one-hit exclusion | No PnL from partial or hindsight-labelled history |
| R7 | #7 | Utility & Revenue | Existing utility/catalyst owner | Verify issuer, token-rights, treasury flows, contracts | Token economic accrual must be shown, not inferred from protocol revenue |
| R8 | #9 | Whale Exit & Distribution | MAL S6/S3 | Raw egress receipts, remaining holdings, pool-depth impact | Transfer != sale; no common-entity claim from CEX hub |
| R9 | #8 | KOL & Hype | MAL S7 | Preserve source-captured social timestamp and wallet transactions | Scraped publication date != original visibility |
| R10 | #10 | Cross-Chain Discovery | Existing chain/source owners | Compare source coverage, misses, false alerts and API cost | Must beat selective sampling after cost, not raw tokens scanned |

**Parallelism exception:** low-cost passive *data preservation* for R5, R8, R9 and R10 can occur under existing owners while R1–R4 run; it does not release another heavy model lane or count as a completed round. Research gates produce PASS, FAIL, INCONCLUSIVE, or DATA_BLOCKED; a FAIL is useful and does not stop independent later hypotheses, but a prerequisite FAIL blocks dependent claims.

## R1 — Can We Actually Buy the Winner? (frozen test)

### Case eligibility
- Historical positive-control leads: ASKR (Robinhood), PEPE (Ethereum), optional FARTCOIN (Solana) only if historical route/pool data are reproducible. These are not an unbiased sample and earn ZERO prospective edge credit.
- **Negative controls required:** same-chain/venue/time/age/liquidity ordinary token, failed/rug/unsellable token, launch not found in time, and no-pool/no-route example. Never claim sample-wide hit rate from named winners.
- Before any numerical backtest, prove **exact** chain ID, CA/mint, verified first executable pool, launch timestamp, source availability at observation, historical reserves/liquidity, trade fee/tax/gas, route and later exit liquidity. Historical quotes from today's reserves are inadmissible.
- If only top-of-candle OHLCV is available, label route/price impact UNKNOWN; do not use spot price as executable fill.

### Preregistered hypothetical tickets
- Quote-notional: USD 500 and USD 2,000 (converted with historical quote-asset price and timestamp, not today's FX).
- Entry anchors: `FIRST_PUBLICLY_OBSERVABLE_AND_EXECUTABLE`, `+5m`, `+15m`, `+30m`. If a time is before first observable source or pool availability -> `NOT_YET_AVAILABLE`, not a winning fill.
- Exit anchors: `+1h`, `+6h`, `+24h`, `+7d`, measured relative to **entry**, not launch. Require a full time-consistent route/reserve/tax/gas quote at exit or mark `UNKNOWN_EXIT`.
- If the entry is after the exit horizon, treat as a separate invalid request, never backfill.
- Failure states: `UNKNOWN_SOURCE_TIME`, `WRONG_CA`, `NO_ROUTE`, `INSUFFICIENT_LIQUIDITY`, `REVERT_OR_TAX_BLOCK`, `UNKNOWN_POOL_STATE`, `UNKNOWN_EXIT`, `SOURCE_OUTAGE`, `CENSORED_HORIZON`; preserve failures as denominator rows, do not turn into 0% or omit.
- Counterfactual: same venue/time and quote size public age/liquidity/volume strategy. Compare tradeability and net return, but with historical winner cases alone this is **plumbing diagnosis only**.

### Clock/provenance
Each opportunity has `discovery_at_utc`, `source_first_available_at_utc`, `source_exact_version_hash`, `source_delivery_verified`, `pool_first_executable_at_utc`, `signal_eligible_at_utc`, `first_possible_fill_at_utc`, `entry_anchor`, `exit_horizon`, `quote_usd`, `chain_id`, `token_id`, `pool_id`, `source_refs`, `coverage_state`, `outcome_state`.
Eligibility time is maximum of **verifiably** observed source/label/deployment/route availability. A timestamp typed into a current JSON file is not proof of past availability.
Full pool/candle endpoint must exist at horizon. No lookahead through same-block post-signal liquidity, terminal candle close one hour early, omitted partial bars or current contract state.

### Costs and economics
For each valid historical fill: report quote-asset units, route pool snapshot block, slippage/price impact, transfer tax, gas, DEX/platform fees, failed/reverted attempt cost and quote currency conversion. Track buy and sell separately; partial exits only when reconstructible. Compute USD net proceeds, USD net PnL, ROI, max adverse/favorable excursion only with sufficient intra-horizon data. No route evidence = `UNKNOWN`, not assumed frictionless.

### Pilot stages
1. **Zero-token census:** choose exact CA/pool/chain for ASKR and PEPE, snapshot historical data availability and control selection, check owner S1 overlap. No result or backtest until this passes.
2. **Deterministic simulator or refusal proof:** reuse S1; add only a minimal read-only fixture evaluator where missing. Freeze data hashes and expected outcomes before model calls.
3. **Adversarial API review:** one existing #1476 mission when released; check winner selection bias, timestamp leakage, missing failure states, venue costs, and whether any apparent lift survives matched controls.
4. **Forward shadow cohort:** collect future launches and no-trade/missed rows through #1340. Only this stage can establish prospective recall/edge.

### Acceptance and kill
- Technical PASS: reproducible first-source-time, source-hash and chain/pool snapshots; two ticket sizes; all four entry anchors; all four exit horizons or explicit UNKNOWN with reasons; matched negatives; no secret/trading rights.
- Research FAIL: technical mechanics cannot be reconstructed or source time cannot be authenticated; report this clearly and select cheaper future capture instead.
- Economic PASS: out of scope for historical named winners alone; needs prospective matched denominator, route-cost realism, independent holdout and repeated evidence.
- **Hard stop:** never use a simulated 20x price candle as evidence of an executable 20x fill.

## Common gates for R2–R10
Every round must freeze before outcome access: `question, champion, challenger, target_population, inclusion/exclusion, independent_unit, observation_clock, primary_metric, negative_controls, multiple_testing_family, costs, power/uncertainty, expected_false_negatives, rights, budget, owner, kill`. Each round produces `CASE_MANIFEST`, `SOURCE_TRUTH`, `PREREG`, `CONTROL_DENOMINATOR`, `RESULTS_OR_BLOCKER`, `LEARNING_LOG`, `OWNER_HANDOVER`.
Store immutable SHA source refs and outcome time; no duplicate evidence ledger, use #1340 and S1–S9. Include missed winners and false identities, never collapse UNKNOWN to false.
REAs browser and EVM analysis may help identify authorized observable data contracts, but shared REA/EVMole code is not independent corroboration; REA cannot recover proprietary labels or hidden server decisions.

## API execution architecture
- Existing API gateway `RESEARCH_LAB_SOL_ANALYSIS` on #1476; **only one ACTIVE_RELEASED**; M6 currently active on main, 007 waiting in draft #1585. R1 technical census does NOT need a new Sol mission to start.
- Treat 007 as the bounded cross-cutting adversarial specialist/REA synthesis, **not** ten calls or ten separate tasks. After 007, the existing owner may authorize ONE bounded material-delta API pass for a specific eligible round, only after budget and heavy slot readback. No API call is pre-authorized merely by the existence of this roadmap.
- Budget caps remain $40 global/month, $4 reserve, $10 Research Lab Sol lane, $1 lane reserve, $3 per-call stop. Spend receipts are required; no Work-credit dependency and no unbounded retries.
- Reuse existing GitHub Actions owner/supervisor. Do not introduce a new scheduled task, scraper or automatic code writer.
- No real-money execution, buy/sell calls, position sizing or promotion to production thresholds.

## First next action
Run the R1 **source eligibility and controls audit** against existing ASKR and PEPE owner evidence, before simulating returns. If exact CA/pool/availability/reserve source is missing, emit DATA_BLOCKED and a narrow owner-owned collection request. Proceed to R2 only when R1's **technical** result is frozen as PASS/FAIL/INCONCLUSIVE/DATA_BLOCKED, not because a model predicts an edge.
