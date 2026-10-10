# Miles Deutscher AI Crypto Guide, source adjudication and framework-specific delta
Date: 2026-10-10
artifact_id: RL-AT-20261010-MILES-FULLTEXT-001
maturity: SOURCE_REVIEW / RESEARCH_DESIGN, not tested trading performance
authority: NONE; parent: RL-AT-20261010-EXTERNAL-INTAKE-001
Source: https://x.com/milesdeutscher/status/2108584190979764314
Input: user-provided complete prose transcription, not a direct authenticated X capture. Original prompt screenshots/other linked articles remain UNAVAILABLE and should not be fabricated.
Current PR: #1558; existing reverse-engineering owner #937; active research-only posture per `04_RESEARCH_LAB/auto_trading/README.md`.

## Bottom line
The article is an **operating-stack catalogue**, not evidence that any AI trading strategy earns positive net alpha. Its most reusable components are: (a) testable GARCH volatility method and honest risk-size benchmark; (b) constrained finance-research evidence feeds; (c) separated researcher/challenger/decision/approval roles; (d) budgeted personal portfolio-risk intelligence; (e) actionable read-only market feeds. Avoid copy-pasting another swarm, execution engine, UI dashboard or unrestricted Robinhood connector.

## Source-derived mapping, fact vs action
| Miles section/item | Actual article claim | Relevant local owner/precedent | Decision |
|---|---|---|---|
| I Claude/Projects/Skills/Research | centralized LLM research and persistent context | Existing Archive, Deep Research, GitHub/Bridge, skills, Supervisor | ALREADY OWNED; improve current retrieval/freshness receipts, no new agent |
| I Grok/X, sentiment, creators | social information early | Alpha Lab narrative/source confidence + Grok context | BOUNDED SHADOW challenger: as-of-first-discovery and fake-spam rate; no social hype alpha assumption |
| I Perplexity/NotebookLM | finance data, filings, YouTube transcript research | Existing document intake/AnyDoc/PDF Inspector; developer source-research | CONDITIONAL fallback when exact high-value source cannot be parsed inhouse; require rights/provenance |
| I CoinGecko, DefiLlama, Tokenomist, Dune, Lunarcrush, TradingView MCP | source connector catalogue | existing DATA PING, CoinGecko and Blockscout; Trader.dev and TradingView policy | SOURCE-GAP AUDIT ONLY. Assess missing data family and access cost/latency; no blanket MCP install; preserve TradingView automated-trading restriction |
| I Kaito, Messari, Nansen, ChainGPT | alternative crypto research AI | existing Nansen research queue and primary-source routing | COMPARE coverage and decision utility vs deterministic incumbent; institutional branding is not evidence of accuracy |
| II backtest engine | AI imports strategies and surfaces outliers | Existing AUTO_TRADING lifecycle, `#1007` older Miles benchmark, `#1557` trial denominator | DO NOT MINE NEW STRATEGIES before denominator/PIT gates. Winner dashboards risk selection bias |
| II Robinhood Agents trading MCP | connect an agent to Robinhood for portfolio/trading | separate broker from Robinhood Chain; current framework research-only | VERIFIED OFFICIAL ENDPOINT but NOT ADOPTED; account access/eligibility and default approvals risk; reference as isolated authority pattern only |
| II GarchMethod / Pine | GARCH risk/vol forecast, sizing and Storm Gauge | existing CN range tournament already includes GARCH(1,1); vol/shadow | HIGH-VALUE method challenger, read code audit below. DO NOT use Pine chart as modeled future GARCH forecast |
| II AI CFO | cross-account net worth, allocation, P&L, risk flags, unlocks | restricted portfolio/wallet in `secrets`; CN is public market product | MAYBE PRIVATE READ-ONLY FINANCE RISKS. Explicit privacy/legal/tax boundaries. No full wallet/account upload to public repo, no chart clone |
| II agent swarms | many specialized CT/price agents | current Supervisor + Alpha Meta-Governor | REJECT new standing swarm; existing bounded delegated task model |
| II journal, DCA, watchlist, airdrops | utility trackers | existing forecast/outcome/alpha ledgers, context | only fill a verified missing field/consumer; otherwise REJECT_OVERLAP |
| III brain/hands trading bot | API/MCP takes actual orders | research-only AUTO_TRADING policy / MAL Paper Wallet v4 | NO EXECUTION. Store as future conceptual source, not stage advancement |
| III Opus + Jev + exchange | LLM research, typed model probabilities, strategy controls, execution | existing `07_PROMPTS_AND_AGENTS/typesafe_jev/2026-09-20__JEV_DECISION_GATE_V1.md` | ALREADY OWNED; narrow, shadow-only. Jev probabilities have not been shown calibrated or tradable |
| III prediction markets | separate event-probability from market price | EdgeOnchain external-alpha issue #922; experiment lifecycle | refer to existing owner; independent probability calibration/baseline mandatory |
| III smart wallets, copy trading, stress/hedge | strategy ideas | #937 SOURCE/OBSERVABLE/COPYABLE/SCALABLE separation; wallet/provenance engines | refine controls and capacity only; do not adopt social performance claims |

## Independent verification and corrections
### 1. Official Robinhood Trading MCP is REAL, but economically and geographically constrained
Official source: https://robinhood.com/us/en/support/articles/agentic-trading-overview/
Robinhood Trading MCP endpoint: https://agent.robinhood.com/mcp/trading
- Robinhood says an external agent may READ account balances/holdings/order history across Robinhood accounts, but order placement is limited to a dedicated MCP/Agentic account. This is a wide READ boundary and narrow WRITE boundary, not read-only access.
- Official current supported products include eligible long equities, options and crypto in agentic account; supported assets can change.
- Official safety article: https://robinhood.com/us/en/support/articles/trading-with-your-agent/ : **trade approvals OFF by default for externally connected MCP accounts**, vs ON by default for built-in agents. Never assume a newly connected agent is approval-only.
- U.S. brokerage account prerequisites: https://robinhood.com/us/en/support/articles/what-you-need-to-get-started/ . Not a dependable Danish user integration without eligibility proof.
- `Robinhood Chain` onchain Pons/Blockscout **does not inherit this brokerage interface**. The existing Alpha Lab is EVM-onchain research, not U.S. brokerage execution.
Decision: **DO NOT CONNECT / NO ROBINHOOD TRADING PLUGIN**; retain the design principle `human-approved trade proposal -> constrained sandbox account -> audit feed` as eventual authority-system example, not an active plan.

### 2. Existing Jev pilot has more evidence than article implies
Local reference: `07_PROMPTS_AND_AGENTS/typesafe_jev/2026-09-20__JEV_DECISION_GATE_V1.md`.
Jev v1.13.0 was connected and tested for *typed semantic triage*; it was not validated for numerical probability calibration or return edge. A reordered feature representation changed its judgment magnitudes, though not routing in a small synthetic test. No right to call it trusted position-size or likelihood oracle. Store Miles's multi-model proposal only as cross-model competition against existing deterministic baselines. No automatic agent trades.

### 3. Institutional sources, use as providers/challengers, not as external arbiters
- Messari API advertises agent-ready source access incl. 34k+ assets: https://api.messari.io/ . Assess metadata freshness, survivorship, terms, rate/cost and provider-defined vs canonical economic measures before any addition.
- Glassnode / Nansen / Arkham: onchain measures and wallet labels may be vendor-derived. An entity label is not an independently established economic identity; compare with native RPC/Blockscout and point-in-time freezing.
- DefiLlama: compare protocol TVL, fee and revenue *definitions*, chains included, data revisions and settlement calendars; never equate TVL/fee growth with automatic price appreciation.
- Dune: bespoke queries are useful for frozen cohort reconstructions only with SQL, query version, block horizon, wallet/entity treatment and refresh timestamp preserved.
- Tokenomist: unlock data may be date projections or changed schedules. Useful as future risk context only after source/version verification.
- QuantConnect: compare research/backtest controls, not import platform if local lifecycle already owns experiments.
- Frontiers DOI 10.3389/frai.2026.1871825 is original 2026 research on daily data for ten large crypto assets 2020-2025. Reported dynamic optimization beating static is **authors' claim**, NOT independent verification of an alpha-producing AI swarm, not a microcap transfer result.
- YouTube/NotebookLM transcripts: source/provenance, creator bias, transcription errors and permissions; summary cannot replace a freeze of original date and claims.

## New, highest-VOI bounded experiments
**E-MILES-01: GARCH risk benchmark, do not import package into production.**
Use existing CN range-skill tournament owner, do not create a new risk authority.
- Model families: GARCH(1,1) (original code challenge), historical realized-vol random walk, EWMA, ATR and constant-risk benchmark.
- Cutoffs: purged daily chronological OOS, no testing against final untouched holdout until contracts freeze; split pre-ETF/ETF-era and vol regimes; BTC and ETH separate, no memecoin inference from BTC sample.
- Primary endpoint: forecast variance QLIKE / squared-error (scale stated) and risk-adjusted *costed* drawdown / realized-vol targeting at equal long-run risk; report interval quality on CN under existing proper scores if used.
- FIXED vs VOL_TARGETED must be compared at a comparable ex-ante volatility or notional risk, including realized leverage, transaction cost, slippage, financing and no-trade states.
- Null outcome, not improvement, is acceptable. Kill after preregistered failure vs EWMA/realized-vol and no decision benefit. Nothing changes canonical labels or sizing.

**E-MILES-02: Private risk overview discovery, no portfolio write.**
First inspect existing restricted portfolio and data permissions. Measure new information only: cross-platform allocation concentration, unlock exposure, drawdown/cash correlation and tax-relevant action reconciliation. Source credentials never enter Markdown/Bridge/public PR. Build only if concrete gap + valid privacy policy + maintained prices + read-only authenticated feeds + economic usefulness are proven.

**E-MILES-03: Prediction probability calibration challenger, not an auto-betting engine.**
Bind to #922 and existing Jev/Red Team where appropriate. Require event base rate, point-in-time published odds and resolutions, proper Brier/log scores, non-resolved labels, market fees/latency, negative controls. No exchange order authority.

**E-MILES-04: Anthropic evaluator/harness trial, no additional live agent.**
Compare present Supervisor/Red Team to a one-off external critic on task packs for factuality, abstention, source coverage, cost, and correction outcome. Incorporate Anthropic agent eval and finance practice articles selectively; do not introduce ten permanent workers.

## Preconditions and ordered follow-up
1. Preserve existing P0 blockers; this article is not permission to displace #1557 / #1512 or any active production repair.
2. Record proposed volatility-family benchmark in existing CN/backtest owner as a candidate only, not new model output.
3. Include exact upcoming GARCH source-code forensic note before asking an agent to import code.
4. Reconcile any candidate economic hypothesis to proposal-time trial denominator #1557, avoid multiple-test search inflation.
5. Keep PR #1558 draft and mark source text `USER_SUPPLIED`, external link `NOT_DIRECTLY_FETCHED`, any quoted measurements `CLAIM` until reproduced.
No external framework engine, restricted wallet, credentials, public site or trading endpoint was changed by this review.
