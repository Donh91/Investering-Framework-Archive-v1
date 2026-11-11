# 0xArchive | External specialist source audit and scientific transfer | 2026-11-11

Status: SOURCE_SCREENED / SHADOW_SOURCE_CHALLENGER_ONLY / NO_PAID_ACCESS / NO_LIVE_SIGNAL / NO_RUNTIME_INTEGRATION
Authority: RESEARCH_ONLY. This document cannot promote an edge, change Master Monday/CN, trigger trading, create a scheduler, or authorize API spending.
Upstream checked: https://github.com/0xArchiveIO/0xarchive-quant at main commit 3ff0c83409525ad9cd74f76a7cfd6fe0aa3bdc51.
Control main at preflight: e305a365d1fd3984c39636d530d9fc0d9d142269.
Captured: 2026-11-11, public documentation/source only. No authenticated provider request or dataset quality test was executed.

## Decision

GO for a bounded, free, read-only source feasibility and method extraction study. HOLD on vendor-dependent production signals, broad historical purchase, official Compass scoring, paid recurrent refresh, raw public publication, and installation of third-party skills into privileged agent runtimes. No independent 0xArchive supervisor or standalone backtester.

0xArchive is primarily a normalized event/market-data vendor for Hyperliquid and Lighter. Its unusual comparative value is full depth/order-lifecycle and wallet-attributed activity, plus long-lived market records and reproducibility-oriented tooling. These are provider claims until independently checked on exact symbols and windows. Hyperliquid core historical L2/books and perps data are more mature than order-level L4; Lighter and HIP-3/4 have differing clocks and starts. It is NOT a universal EVM/Base/Solana DEX microcap record.

## 2026-11-11 public capabilities + binding legal primary-source addendum

This section supersedes the earlier "binding terms not retrieved" caveat **for publicly readable text only**. The provider API remains UNAUTHENTICATED for market data; no account rights/entitlement, symbol-specific depth, record continuity, first-known-vintage or actual fills have been verified.

**Live public metadata proof (zero credentials, zero paid credits):** `GET https://api.0xarchive.io/v1/capabilities` returned `success:true`, **111 declared capability rows** in six venue-family namespaces: `hyperliquid`, `hip3`, `hip4`, `spot`, `lighter`, `rh-lighter`. Examples of `available_from` **policy floors**, NOT independently checked data completeness or historic first publication:
- Hyperliquid core L2 from 2023-04-15; core trades from 2023-04-15T03:31Z; core funding/OI from 2023-05-20T02:50Z.
- Hyperliquid core L4 orderbook checkpoint from 2026-03-11T01:03Z. L4 orderbook route metadata is `live:false/replay:false` but **L4 diffs stream metadata is live/replay true**; distinguish snapshots from diff streams and reconstruction.
- Hyperliquid core candle route policy floor 2025-03-22T12:00Z even though trades have an earlier public route. This is separate from the upstream 0xbt minute-dataset statement; do not infer any unsupported earlier engine backtest.
- Lighter mainnet trades from 2025-01-17T08:43Z, L3 orderbook from 2026-03-05T03:33Z. Lighter Robinhood Chain L2 floor 2026-08-22T18:43Z.
- Each family/data type has separate `live`, `replay`, cadence and page-limit constraints; a capability row is a catalog descriptor, not a source-health receipt or per-symbol contract.

**Binding Data License read directly**: https://0xarchive.io/policies/data-license, updated 2026-10-28. Covers 0xArchive-obtained website/API/stream/export records, NOT peering data received from one's own Hyperliquid node. Permits internal research, backtesting, model training, risk management and materially transformed charts/analytics/customer-facing outputs subject to entitlement. Written permission is required for benchmarks, indices, financial products, raw redistributions, substitute feeds and white-label/OEM delivery. Downloaded entitled data can be retained subject to the same license after cancellation. Publishing derived outputs that reasonably reconstruct records remains prohibited.

**Terms of Service read directly**: https://0xarchive.io/terms, updated 2026-11-05. Explicitly incorporates the Data License and states no guarantee of completeness, accuracy or timeliness; API keys are nontransferable; contractual rate limits apply. For data-use conflicts the Data License controls. Terms restrict reverse engineering proprietary service source code, but the separately MIT-licensed public `0xarchive-quant` repository remains a distinct software rights object; do not conflate these rights.

**Regulatory/public-display boundary:** Our public Proof section could plausibly be interpreted as a benchmark/indicator depending on design, so keep explicit `PUBLICATION_RIGHTS_REVIEW` before publishing any provider-derived benchmark or vendor-reconstructable datapoints. Do not categorically assume an internal experimental score is permitted for public index use.

**Updated E0 stage:** `PUBLIC_CAPABILITIES_METADATA_VERIFIED` only. The actual BTC/ETH symbol-level quality/coverage windows, API response schema, availability timestamps, incidents, request IDs, vendor rights/entitlement and bytes remain unverified; E0 cannot pass source admission. No account, free-key signup, paid subscription or raw API pull performed.

## 2026-11-11 additional PUBLIC service-quality check (not authenticated market data)

Read-only, no-key GET public endpoints returned:
- `https://api.0xarchive.io/v1/status/coverage`: public provider coverage/status descriptors and a specific historical orderbook quality notice.
- `https://api.0xarchive.io/v1/data-quality/status`: `success:true`, service `status:"degraded"`, `active_incidents:1`, snapshot `updated_at:2026-11-11T20:41:18.897532620Z`, provider `meta.request_id:07a93706-7e57-4342-bc8f-2112752ede09`. It separately describes six venue-family substatuses as `operational`. This is a provider-reported snapshot, NOT independent diagnosis. No actual root cause was returned.
- Public coverage metadata reports Hyperliquid `orderbook` source `node` snapshots between **2026-07-25T17:23:00Z and 2026-10-01T21:20:00Z** could depict a book several minutes earlier at busy times; source `venue` snapshots and trades/candles/L4 data for the same period are claimed unaffected. This is **a material warning** for naive L2 point-in-time or execution assumptions. Require per-record source, event clock, availability clock, and reject unsafe intervals unless independently reconciled.
- Public coverage `historical_coverage:0.4` occurs in some rows alongside `completeness:99.9` or `100.0`. Without the field definition/denominator, do NOT interpret 0.4 as 40% record coverage or 60% missing; record `UNINTERPRETED_PROVIDER_METRIC`.
- Endpoints `/v1/data-quality/coverage/hyperliquid/BTC`, `/v1/data-quality/incidents`, `/v1/data-quality/latency` return **HTTP 401 without credentials**. Thus no independently observed exact BTC coverage, incident detail or data-type latency test was completed. Do not bypass access requirements.
- No trading quotes, raw provider trades, prices, book depth, wallets, model output or vendor paid data were fetched. Only public capability and source-health metadata.

**Source decision:** `PUBLIC_CAPABILITIES_AND_STATUS_VERIFIED`, `VENDOR_GLOBAL_STATUS_DEGRADED`, `SYMBOL_SOURCE_QUALITY_UNVERIFIED`, `ACTIVE_INCIDENT_DETAIL_AUTH_REQUIRED`, `PROVIDER_DATA_ACCESS_NOT_AUTHORIZED`. E0 stays **HOLD** for data-source admission and scientific performance testing. Public metadata must never become a proof of independent historical first-known.

## Source inventory and fact grades

- Product and data taxonomy: https://0xarchive.io/ and https://docs.0xarchive.io/venue-coverage
- Coverage/quality endpoints: https://docs.0xarchive.io/data-quality
- Plan and quotas: https://0xarchive.io/pricing
- Data rights explainer: https://docs.0xarchive.io/data-rights (explicitly subordinate to binding Data License and Terms)
- Point-in-time guide: https://docs.0xarchive.io/guides/point-in-time-backtesting
- Agent/backtester project: https://github.com/0xArchiveIO/0xarchive-quant
- Backtest agent skill at audited head: skills/backtest/SKILL.md, blob 9450a2b0aff2fc969b1db661d45a695453713f14
- PyPI distribution: https://pypi.org/project/0xarchive-backtest/
- Code license: MIT for upstream repository, including Rust source under skills/backtest/engine/. Keep copyright/license on copied or derived substantial software. MIT software license is NOT the data license.

EVIDENCE_GRADES:
* VERIFIED_PUBLIC_CODE: upstream repository contains Rust engine source, Cargo project, backtest/query skills and explicit MIT license; README and skill describe deterministic receipts, trials ledger, sealed holdout, negative/null controls, clock-phase checks, out-of-sample, and deflated Sharpe. Source existence does NOT establish code correctness or benchmark validity.
* DOCUMENTED_VENDOR_CLAIM: Hyperliquid core L2 from April 2023; funding/OI from May 2023; wallet-attributed core L4 from March 11 2026; Lighter trades from January 17 2025; Lighter L3 from March 5 2026; liquidations with shorter coverage; symbol/schema-dependent limits.
* UNVERIFIED: actual API uptime, historical gap rate, delivery lag, latency distributions, vendor comparatives, depth fidelity, wallet identification quality, finality/version behavior, end-to-end engine determinism in our environment, out-of-sample results and economic forecasting uplift.
* NOT_TESTED: a single authenticated request, quality endpoint response, public API schema response at our runtime, or any provider market data. No quantitative edge claim.

Supplier's published examples are demonstrations, not our independent replication; do not reuse their showcased Sharpe, alpha or trader identification as achieved internal evidence.

## Coverage and market identity hazards

Two top-level providers: Hyperliquid and Lighter. Hyperliquid has separate core perpetual, Spot, HIP-3 builder-perp, HIP-4 outcome namespaces; Lighter has mainnet and Robinhood Chain deployment. Preserve venue, market family, symbol, instrument type, settlement and schema on every join. The same plain symbol does not mean the same market. HIP-4 price may represent probability, not USD. Spot/HIP-4 do not use perpetual funding. Snapshot-based L2 and order-level L4/L3 have different fidelity and history. Native Hyperliquid L2 may be depth-capped; Lighter L3 order-level samples may be capped; reconstructability is not automatic.

The provider documentation gives family-level start dates only. The source admission must inspect symbol-specific data-quality coverage and gaps, pagination, event resolution, snapshot anchor, source event time vs availability time, restatement/finality, and finalized_through if offered. Data from a newly reconstructed prior interval is not automatically evidence it was first-known at the historical decision cutoff. Upstream generated OHLCV or normalized data is not proof of contemporaneous availability.

No 2020-2022 Hyperliquid market-microstructure replay is possible from data that starts in 2023. March 2026 L4 cannot prove an order-level 2024 backtest. No modern data can be presented as an original earlier-issued Compass prediction. Historical retrospective, original-issued, and challenger-developed records stay separate.

## Existing owners, not new engines

1. Derivatives S5, original Archive issue https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1514 and canonical spec 04_RESEARCH_LAB/external_specialist_dissection/S5_DERIVATIVES_CROWDING_TO_PULLBACK_V1.md: source challenger for price response, taker flow, open-interest delta, funding, spot-versus-perp mismatch, liquidation shocks. Baseline stays exchange-native public Binance/OKX as presently governed; vendor joins require exact market-family and clock compatibility. Reuse M6 outcomes at 24h/72h/7d/14d/30d, not an invented outcome owner.
2. Historical Reality Engine (HRE), original issue https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596 and research/historical_reality_engine/README.md: use for point-in-time, gaps, replay, regime splits, same-universe null controls, opportunity set reconstruction and paper economics. Respect Round 3 collection-only firewall. Do not create duplicate HRE, backtest or PIT authority.
3. Cycle Navigator original https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1516 and 05_CYCLE_NAVIGATOR/: potential RESEARCH_CHALLENGER for short-horizon BTC/ETH risk contextualization, not a change to current frozen W46 seven daily price/close/range forecast, published scores, market compass weight, or Master Monday. First prove incremental forecast or risk discrimination against existing sources.
4. Alpha Lab Pro original https://github.com/Donh91/Meme-Alpha-Lab/issues/228; existing sellability/execution owner https://github.com/Donh91/Meme-Alpha-Lab/issues/98: evaluate transferable design patterns for realistic fill, cost, partial/no-fill and wallet-skill audit. Hyperliquid perps are NOT comparable to low-liquidity on-chain DEX memes. No promotion of any microcap signal by extrapolating perp backtests.
5. Framework research methodology: existing 06_RESEARCH_LAB/protocols/ and 04_RESEARCH_LAB/auto_trading/GOVERNANCE.md own hypothesis freeze, trial accounting, fixed baselines, walk-forward/holdout, multiple-comparison controls, red team, retention of negative trials, and no-hindsight proof. Compare external gauntlet to existing methodology and extract only genuinely missing primitives.
6. External specialist queue: existing 04_RESEARCH_LAB/external_specialist_dissection/QUEUE_V1.json owns prioritization, one heavy lane at a time and deduplication. This is an additive S5/HRE source feasibility memo, NOT another top-level S11 or separate priority queue.
7. Existing S1 #1156 and Claude/Grok Bridge have review/routing roles only; no new identity, schedule, cron, writer, credential or unconditional merge privilege.

## Source-code correction: vendor raw archive != 0xbt fill engine

Verified against upstream at pinned commit, especially skills/backtest/references/data.md and skills/backtest/references/gauntlet.md (not merely vendor marketing).

1. **The currently documented 0xbt strategy dataset is minute bars for Hyperliquid core perps only.** It does not backtest HIP-3, HIP-4, Spot, Lighter or sub-minute order streams. The upstream data.md says actual tradable price/volume rows in that path start 2025-03-22. Thus the provider's 2023 L2 market archive does not itself give 0xbt a 2023 tradeable-backtest window.
2. **Book columns are always null in the 0xbt data-pull parquet files.** The vendor states best_bid/best_ask/spread/depth/imbalance and liquidation-level fields are null in *every* data-pull month; the API has other more granular routes, but the engine's minute dataset does not integrate them. Its fill model uses a fixed fallback slippage of 2 basis points when actual depth is absent, configurable for stress tests. An 0xbt performance result is therefore NOT a proved orderbook/L3/L4 queue-position fill simulation.
3. **Sealed holdout is a process guard, not an access-control boundary.** Upstream gauntlet.md explicitly states engine reads after holdout start raise Sealed, while reading Parquet through another library can bypass it. A copied/new study directory or independent analyst access also requires separate governance: study-level ledger is not necessarily global trial accounting. Independent sandbox permission + immutable trial registry + authorized reveal must enforce our claims.
4. **Data receipt strength needs tests.** The Rust Receipt DatasetRef holds market, month and dataset_version, and the result record holds hash; this struct alone does not show a byte-level Parquet SHA binding. Check dataset manifests and replay hashing separately before calling a receipt fully independently reproducible. Do not allege tampering based on absence from this one struct.
5. **Method reuse is the immediate value.** Source-level designs for nulls, trial ledger, moving clock phases, deflated Sharpe and walk-forward are worth comparison; not yet justification for replacing HRE or Alpha paper fill engine.
6. **Version/provenance gate:** upstream skill currently instructs pip pin 0xarchive-backtest[curated]==0.3.2; separately verify PyPI artifact, exact release commit, source/wheel attestation, Cargo.lock and executable identity before code execution. No install was made.

Practical consequence: E0 should separate provider granular API quality from **0xbt minute-engine** capabilities. E1 must not imply this ready-made engine already implements execution-realistic L4 replay. If realistic order-level simulation is needed, first evidence a minimal adapter into our EXISTING HRE/paper economics owner and test with actual book snapshots and immutable timestamps; do not silently patch vendor engine or build a parallel engine.

## High-value candidate primitives

P0a - Data-quality-aware shadow candidate: capture exact venue+family+symbol+datatype coverage, known gaps, ingestion lag, request_id, first-known clock and checksum at each cutoff; label quality UNKNOWN / COMPLETE_WINDOW / GAP / STALE / NOT_SUPPORTED. Stop rather than silently fill. Distinguish provider metadata claims from measured record completeness.

P0b - Execution realism: same specified order at signal time under 1) perfect close fill (negative fantasy baseline), 2) bid/ask and fees, 3) latency/size/partial/no-fill and exit capacity. Do not claim L2 orderbook proves exact queue position or fills; L4/L3 is a richer challenger only when verified for that market and cutoff. For on-chain DEX microcaps, keep gas, MEV, transfer tax, toxic routes, rugged liquidity and full exit separately under Alpha Lab original owner.

P1a - Frozen S5 microstructure ablation: test price/OI/funding-only, taker imbalance-only, liquidation-only (when complete), and their combination against matched conditions and existing M6 truth. Event type and venue must match; require improvement net of added source cost, latency, missingness and false-alert burden.

P1b - Cross-venue lead-lag: test whether Hyperliquid versus Lighter divergences lead a future risk event using common available timestamps, synchronized universe and observable tradeable notional. False positive: correlation due to common BTC shock or a stale venue; negative controls must time-shift and venue-swap with embargo.

P1c - Agent methods transfer: compare upstream 0xbt trial ledger, sealed holdout, deflated Sharpe and clock-phase perturbation to current existing internal falsification protocol. Prefer methods with transparent mathematical definitions, fixtures and independent replication; do not import an agent plugin into a privileged environment without pinned-tree, license, dependency and prompt-injection/security review.

P2 - Wallet reconstruction: wallet-level fills and maker/taker/context can form an exploratory challenger for repeatability-vs-luck on covered venues, but not direct evidence of cross-chain DEX smart money or identities. Complete loser coverage, selection denominator, realized exits and first-known timestamps mandatory.

## Cheap, preregistered, falsifiable experiments

E0 SOURCE_ADMISSION (first, no strategy claims). BTC/ETH (Hyperliquid core) and at most one Lighter market in a bounded trailing rolling Free window, only once authorized key access exists; fetch capabilities, exact symbols, quality coverage/incidents, 2 short slices, pagination and timestamp sanity. Compare independent exchange-native sample where feasible. Reject for this experiment if basic completeness or clock semantics cannot be established. No secret goes in GitHub, ChatGPT issue, public PR or logs.

E1 EXECUTION_COST_ABLATION (after E0). Same frozen 1-3 day signal events using three cost/fill assumptions. Primary outcome is deviation in net realized simulated value and whole-position exit fill rate, NOT gross win rate. For each attempted trade include no-fill and delisting/last trade. Hold size and opportunity set fixed. HRE / paper-economics owner only.

E2 S5_INCREMENTS (after E0, first prospectively frozen S5 observations). Existing price+OI/funding vs +taker flow vs +liquidation / microstructure on matched BTC/ETH event/cutoff cohorts. Primary: risk discrimination for M6 24h/72h adverse outcomes, report gains and uncertainty separately for BTC/ETH, volatility-normalized and percent units. Freeze event cutoff before outcome, use episode/block-bootstrap, effective-N, regime segments and false-warning cost. A prospective result cannot be inferred from a 2026 post-hoc provider exploration.

E3 QUANT_GAUNTLET_REPLICATION (public code only first). Pin upstream git commit and dependency hashes, review licensing/source and sandbox the Rust/Python engine; feed synthetic fixtures and compare result hashes across runs and fixed clock shifts. Attempt to break sealed-holdout/trial count by direct dataset access, study copying, backdated revised data and repeated strategy tuning. Outcome: VERIFIED_METHOD / METHOD_GAP / NOT_REPRODUCED, not trading alpha.

E4 CROSS_VENUE_LEAD_LAG (deferred until E0 plus comparable venue coverage): matched BTC/ETH liquid markets, timestamps and execution capacity; contrast with common factor, lagged/reshuffled and inactive-market controls; report effect by regime and remove if no stable incremental signal.

## Invariants and fail-closed gates

- NO data purchase, subscription, card, paid API dispatch, data export order or automatic renewal without a separate exact owner approval. Free tier is $0, rolling 30 days, 50k monthly credits, per vendor published pricing at 2026-11-11. Build is $49/month on monthly billing ($39/month equivalent only when billed annually), Pro $199/month. Credit and throughput usage are still metered.
- NO new external agent connector/plugin installation into privileged code spaces from unreviewed upstream scripts or prompts. Third-party skill READ/Write/Edit/Bash is powerful, review the referenced engine/scripts, packaging/build provenance, dependency lock and capability scope before any sandbox install.
- NO provider API key in repository files; keep credentials only in approved runtime store and audit use with no secret output. Never connect personal trading wallet, seed, or signing key.
- NO restricted raw/normalized source values in PUBLIC Archive or PUBLIC-facing Alpha store. Restricted evidence route: Donh91/secrets under 00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md and binding policy, after authorization. No private raw values here.
- NO public replay feed, downloadable vendor rows, raw chart reconstructability, benchmarks/indices/financial products, white-label substitute data distribution without legal review and any required written permission. Internal research/model outputs generally permitted by vendor explainer but binding Data License and Terms prevail; those primary legal pages were not independently retrieved in this pass.
- NO claims that subscription history starts at symbol creation; coverage is per dataset/symbol. Preserve UNKNOWN for first-known/publishing availability without proof. Do not silently fill incident windows or mix unfinalized and final records.
- NO inference that 0xbt marketing reports or sample Sharpe are verified. MIT license applies to software, NOT vendor data.
- NO simulation = LIVE label; any paper wallet/fill receipt is explicitly simulated, with fill assumptions and sample boundary. No real trading authority.
- NO new current-state Compass source authority, scoring reweighting, production graph or S1 automation change from this research document.

## Access, cost and licensing assessment

Free: 30-day rolling history; 50,000 credits/month; 15 req/sec, 3 concurrent requests, 10 WebSocket subscriptions, replay 10x. Vendor describes several endpoints restricted to Build and live mempool to Pro; check exact route before assuming Free coverage.
Build: $49/month or annual $468 (equivalent $39/month), 80m credits/month, full *retained* archive, 50 req/sec, 50x replay and $50/month export credit.
Pro: $199/month or annual equivalent $159/month, 400m credits/month, 150 req/sec, 100x replay and mempool support. No objective case for our current plan.
Parquet export fees depend on schema/GB/minimum; budget an explicit quote, not an invented flat price.
Provider's rights summary permits internal research, transforms/model training and non-reconstructable customer-facing analysis. Written permission flagged for benchmarks/indices, raw redistribution/substitute feeds, financial products and OEM. Treat public Proof scoreboards and index-like public signals as licensing-review candidates before publication. Downloaded data retention after cancellation is described as allowed subject to license.

## Exit/next decision protocol

PASS_E0 only with two reproducible source receipts, symbol-level coverage/gaps, exact available_at/cutoff evidence, verified numeric/timestamp semantics and compatible permission; otherwise STOP_SOURCE_GAP.
PASS_E1 only if execution differences from naive fills are measurable, stable, and not replicated by a cheaper native source; otherwise RETAIN_INTERNAL_BASELINE.
PASS_E2 only with frozen prospective outcomes, sufficient complete paired sample, measured incremental risk forecast value over native baseline, costs and false-positive trade-off; otherwise DO_NOT_PROMOTE.
PASS_E3 only with independent code integrity/security review, deterministic fixture proof and zero sealed-holdout leakage; otherwise METHOD_ONLY_PARK.
No promotion to operational Compass, Alpha, HRE engine or paid source without original-owner PR, exact-head CI, independent review, qualified merge, main readback and prospective monitoring.

## Explicitly unresolved

- Exact market-level Free-tier route and trade/quality API response: not sampled, OXARCHIVE_API_KEY not supplied.
- Market-data API schema/version: upstream query skill uses 0xArchive-Version: 2026-10-01; must independently pin/check OpenAPI and handshake before parsing.
- Binding Data License and Terms page retrieval not completed. Rights risk remains open.
- Whether internal trial ledger, holdout and clock-phase protocols already cover all upstream primitives: overlap partly documented, full code-level equivalence not audited.
- Whether S5 source uplift can beat zero-cost exchange-native data: unmeasured.
- Any 0xArchive-to-DEX-microcap alpha: unsupported.

## Trigger for next action

Route this read-only source memo to existing S5 #1514, HRE #1596, Alpha #98 and existing Claude/S1 review channel. One free-access proof only after authorized credentials and source rights are resolved; no paid path by default. If an existing owner already has this candidate under a stronger acceptance contract, deduplicate and close the redundant intake. Negative results must be logged, not erased.
