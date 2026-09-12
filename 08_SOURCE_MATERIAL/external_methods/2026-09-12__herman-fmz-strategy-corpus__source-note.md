# Herman Trading + FMZ Strategy Corpus Audit

**Dato:** 2026-09-12  
**Status:** SOURCE_NOTE / RESEARCH_ONLY / NO_ALPHA_CLAIM  
**Område:** autonomous trading research / external strategy corpus / execution infrastructure / baseline library  
**Primary folder:** `08_SOURCE_MATERIAL/external_methods/`  
**Related framework:** Research Lab governance, Forecast/FNP accountability, future autonomous trading research, paper trading / execution research  
**Core impact:** NONE  
**Shadow impact:** RESEARCH QUEUE ONLY

## Supplied sources

User supplied:

1. Herman Trading Strategy Vault  
   `https://twilight-sky-83a4.helmans13.workers.dev/Herman_Trading_Strategy_Vault`
2. FMZ strategy repository  
   `https://github.com/fmzquant/strategies`
3. HermanTrading GitHub profile  
   `https://github.com/HermanTrading`
4. Herman Trading premium research / indicator page  
   `https://www.hermantrading.pro/premium`
5. TradingView/X screenshots containing selected strategy tester outputs.

The screenshots are treated as user-supplied evidence of displayed hypothetical backtests only. They are not treated as independently verified live performance or proof of alpha.

---

## Executive verdict

The highest-value finding is **not any single advertised strategy**.

The highest-value asset is the combination of:

- a large external strategy corpus (FMZ),
- reproducible/open Pine examples (Herman),
- session-conditioned probability-map methodology,
- execution/webhook/WebSocket/order-flow examples,
- and a natural benchmark set for future autonomous-trading agents.

Recommended classification:

```yaml
FMZ_STRATEGY_REPO: HIGH_VALUE_RESEARCH_CORPUS
HERMAN_STRATEGY_VAULT: HIGH_VALUE_DISCOVERY_INDEX
HERMAN_PUBLIC_PINE: USEFUL_REPRODUCIBLE_METHOD_REFERENCE
HERMAN_SESSION_PROBABILITY_METHOD: RESEARCH_CANDIDATE
TRADINGVIEW_SCREENSHOT_PERFORMANCE: UNVERIFIED_MARKETING_EVIDENCE
HERMAN_PREMIUM_SUBSCRIPTION: NOT_REQUIRED_FOR_CURRENT_RESEARCH
CORE_FRAMEWORK_CHANGE: NONE
AUTONOMOUS_TRADING_RESEARCH_VALUE: HIGH
```

The material should be used as a **candidate corpus and infrastructure reference**, never as imported alpha.

---

## 1. FMZ repository

The public `fmzquant/strategies` repository is unusually broad. It contains thousands of strategy/example records across JavaScript, Python, C++, PineScript and other FMZ formats.

High-relevance families visible in the repository include:

- TradingView signal execution / webhooks,
- Binance/OKX WebSocket examples,
- multi-symbol trading templates,
- funding-rate monitoring,
- hedging and arbitrage,
- HFT/order-flow factor examples,
- exchange/account/order utilities,
- market-making / grid examples,
- derivatives/options examples,
- simple moving-average/trend strategies,
- DCA / rebalancing,
- new-listing monitors,
- Uniswap V3 execution libraries.

### Research value

The repository is more valuable as:

```text
strategy corpus
+
execution pattern library
+
benchmark library
+
exchange integration reference
```

than as a collection of proven strategies.

Many records are educational, old, exchange-specific, parameter-sensitive or potentially unsuitable for current markets. Some titles make extraordinary return claims. Those claims receive zero evidentiary weight until independently reproduced.

### Most valuable lanes for future autonomous trading

1. **Execution plumbing**
   - TradingView -> webhook -> execution
   - order state handling
   - multi-symbol orchestration
   - WebSocket vs REST patterns
   - exchange latency / connection examples

2. **Market microstructure**
   - order-flow factors
   - funding monitoring
   - arbitrage / cross-venue relationships
   - hedging logic

3. **Benchmark strategies**
   - EMA / moving-average systems
   - breakout / trend systems
   - simple mean-reversion systems
   - DCA / rebalance controls

These are useful because future AI trading agents must beat simple, frozen baselines net of costs before any alpha claim is accepted.

---

## 2. Herman Strategy Vault

The Strategy Vault is a research interface layered over the FMZ universe. It exposes filters for strategy logic, market/timeframe, actionable status, Martingale/Grid exclusion, queue/promising/tested state and JSON/CSV export.

This is structurally interesting because it resembles the correct workflow for autonomous research:

```text
large external corpus
-> deterministic filtering
-> research queue
-> independent reproduction
-> paper test
-> adversarial audit
-> promotion/rejection
```

The interface itself is therefore more relevant than any headline backtest.

### Framework mapping

Do **not** create a new engine or new permanent agent simply because this interface exists.

Use it as inspiration for a future external-strategy intake dataset, compatible with existing Research Lab governance and existing paper-trading/adversary concepts.

---

## 3. Herman public GitHub code audit

Public profile currently exposes `Trend-Rebalance-Map-Herman-`.

The public Pine Script v6 source is materially better than a typical social-media strategy post:

- source is visible;
- explicit Mozilla Public License 2.0 header is present in the script;
- `commission_value` is set;
- slippage is explicitly modelled;
- signals are gated by `barstate.isconfirmed`;
- `calc_on_every_tick = false`;
- no `request.security()` / higher-timeframe lookahead is used;
- the author documents repaint assumptions;
- strategy logic is mechanically defined.

Core signal family:

```text
price re-crosses fast SMA
+
fast/slow SMA direction filter
+
minimum MA separation
+
explicit TP/SL logic
```

### Verdict

```yaml
CODE_QUALITY_AS_REFERENCE: GOOD
REPRODUCIBILITY: GOOD
NO_REPAINT_INTENT: EXPLICIT_AND_CODE_CONSISTENT_AT_INITIAL_REVIEW
ALPHA_STATUS: UNPROVEN
DIRECT_CRYPTO_TRANSFER: UNPROVEN
RESEARCH_VALUE: MEDIUM_HIGH
```

This is useful as a reproducibility/reference test case, not as a strategy to deploy.

---

## 4. Herman premium probability-map methodology

Herman's public site describes NQ probability models based on multi-year historical data, including:

- previous-hour high/low sweep-first probabilities,
- Asia/London/New York session-conditioned outcomes,
- sweep failure / reversal probabilities,
- median penetration / target distributions,
- OHLC behavioural tendencies,
- context-dependent scenario maps.

A public backtest-library article provides materially better methodological detail than the marketing pages, including:

- NQ 1-minute data,
- 2009 through August 2025 in one study,
- explicit resampling,
- previous-hour liquidity-sweep detection,
- return-to-open / return-to-midpoint measurement,
- aggregation into conditional outcome tables.

### Why this matters for the framework

This is potentially relevant to **execution timing**, not to macro regime determination.

Candidate research question:

> Do BTC/ETH exhibit stable, out-of-sample session-conditioned sweep/reversion probabilities around Asia, London and New York liquidity transitions, after fees/slippage and multiple-testing controls?

If yes, this could improve execution quality after the framework has already decided that a trade is permitted.

It must **not** override DATA PING, regime, rotation or portfolio-risk gates.

### Current status

```yaml
NQ_METHOD_FAMILY: PLAUSIBLE_AND_PARTLY_REPRODUCIBLE
VENDOR_EDGE_CLAIMS: NOT_INDEPENDENTLY_VERIFIED
CRYPTO_TRANSFER: HYPOTHESIS_ONLY
EXECUTION_RESEARCH_PRIORITY: MEDIUM_HIGH
PURCHASE_PREMIUM_NOW: NO
```

The free/public material is sufficient to test the concept before paying for proprietary indicators.

---

## 5. TradingView screenshot audit

User-supplied screenshots showed examples including:

- Squeeze Momentum 30m, approximately 159 trades, profit factor around 1.57;
- BTC EMA crossover, approximately 99 trades, profit factor around 2.22;
- ETH daily EMA crossover, approximately 29 trades, profit factor around 4.36;
- BTC Swingtrader v2.1 daily, approximately 16 trades, profit factor around 6.09.

These results are interesting for **candidate discovery only**.

They do not establish edge because the screenshots do not independently establish:

- exact dataset and symbol feed,
- complete sample period,
- parameter search history,
- in-sample vs out-of-sample status,
- walk-forward performance,
- survivorship / selection effects,
- realistic market impact,
- robustness to parameter perturbation,
- regime stability,
- multiple-hypothesis correction,
- live execution parity.

Small samples such as 16 or 29 trades are especially weak evidence regardless of displayed profit factor.

### Screenshot evidence classification

```yaml
STRATEGY_TESTER_DISPLAY: OBSERVED
LIVE_TRACK_RECORD: NOT_ESTABLISHED
OUT_OF_SAMPLE_EDGE: NOT_ESTABLISHED
ROBUSTNESS: NOT_ESTABLISHED
AUTONOMOUS_DEPLOYMENT_AUTHORITY: ZERO
```

---

## 6. Licensing / provenance guardrail

No root `LICENSE` file was found in the FMZ repository during this audit.

The Herman public Pine script contains an explicit MPL-2.0 header, but no repository-level `LICENSE` file was found in the Herman repo during the audit.

Individual FMZ strategy files may contain their own licenses. Therefore:

```text
DO NOT bulk-vendor or copy strategy source into the framework.
```

Before any code reuse:

1. inspect the exact file's license / header;
2. preserve attribution and license obligations;
3. otherwise store only source URL, metadata and independently reimplemented research logic.

---

## 7. Recommended research queue

### Priority A - build/use as benchmark corpus

Use external strategies as **frozen comparison baselines** for future AI/autonomous systems.

Initial reproducibility candidates:

1. simple BTC EMA crossover baseline;
2. simple ETH EMA crossover baseline;
3. Squeeze Momentum 30m candidate;
4. Herman Trend Rebalance Map reference implementation.

Required evaluation:

- same market data as agent/model;
- frozen parameters before OOS window;
- realistic fees/slippage;
- no lookahead/repaint;
- walk-forward or true OOS;
- parameter-neighbourhood robustness;
- regime segmentation;
- risk-normalized performance;
- comparison against buy-and-hold / no-trade / simple trend baselines.

### Priority A - infrastructure mining

Review FMZ examples for reusable *patterns*, especially:

- WebSocket data ingestion;
- multi-symbol orchestration;
- funding monitoring;
- TradingView/webhook execution;
- order/fill state handling;
- latency/error handling;
- paper/live execution separation.

Extract architecture ideas, not copied code by default.

### Priority B - session probability research

Independently reproduce Herman-style conditional sweep maps on BTC and ETH.

Pre-register:

- sessions / windows;
- definitions of high/low sweep;
- conditioning variables;
- minimum sample size;
- test period;
- baseline probability;
- transaction-cost model;
- false-discovery / multiple-testing handling.

### Priority C - premium material

Do not purchase or rely on premium indicators yet.

Only revisit if independent replication of the public methodology produces stable OOS decision value in crypto.

---

## 8. Governance and kill criteria

This source note creates **no new shadow engine**.

Any strategy candidate enters existing research governance and must die if it fails the following.

### Integrity kill

Reject immediately if:

- lookahead/repaint cannot be excluded;
- backtest parity cannot be reproduced;
- execution assumptions are impossible;
- provenance/license is incompatible.

### Robustness kill

Reject or quarantine if:

- OOS edge collapses;
- performance depends on a narrow exact parameter;
- reasonable costs/slippage remove the edge;
- one period/trade dominates the result;
- strategy materially underperforms a simple frozen baseline on risk-adjusted terms.

### Promotion threshold

No external strategy may be described as `edge`, `alpha`, `validated` or `deployable` until it produces independent, frozen, reproducible rows under the framework's existing forward-test / adversarial standards.

---

## Final disposition

```yaml
ARCHIVE: YES
LOCATION: 08_SOURCE_MATERIAL/external_methods
STATUS: RESEARCH_ONLY
FMZ: HIGH_PRIORITY_CORPUS_AND_INFRA_REFERENCE
HERMAN_VAULT: HIGH_PRIORITY_DISCOVERY_INDEX
HERMAN_PUBLIC_CODE: MEDIUM_HIGH_PRIORITY_REPRO_CASE
HERMAN_PROBABILITY_MAPS: MEDIUM_HIGH_PRIORITY_EXECUTION_HYPOTHESIS
SCREENSHOT_BACKTESTS: LOW_EVIDENCE_CANDIDATE_DISCOVERY
PREMIUM_PURCHASE: DEFER
CORE_CHANGE: NONE
NEW_ENGINE: NONE
CODE_IMPORT: NONE_PENDING_LICENSE_AND_REPRODUCTION
NEXT_BEST_ACTION: independent reproduction + baseline harness, then paper-forward testing
```
