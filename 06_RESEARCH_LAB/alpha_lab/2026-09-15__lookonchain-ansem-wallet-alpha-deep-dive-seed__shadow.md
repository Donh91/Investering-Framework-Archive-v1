# ALPHA LAB RESEARCH — Lookonchain / Ansem wallet deep-dive seed

Date captured: 2026-09-15
Status: SHADOW RESEARCH SEED — NOT A TRADING SIGNAL
Purpose: Preserve a concrete wallet-led alpha research case for later Astra deep dive and possible Alpha Lab methodology work.

## Source bundle

### 1. User-provided screenshot
The screenshot shows a Lookonchain post alleging that a wallet labelled `Ansem-2` spent approximately $233K to buy 2.79M CASHCAT over a three-hour window.

Wallet/address visible in screenshot:
- EVM-style wallet: `0x6f5bbfBFB82729cf356F37f88911952cA115D3F5`
- Linked Solana wallet: `CLM6E4zpTviEC77nWKo8gPVLQoXx9tgoQCYJ8NibxKg1Q`

The screenshot states that the linked Solana wallet held 10.5M ANSEM, valued around $2.7M at the time, and had made about $2.6M profit from ANSEM.

IMPORTANT: wallet ownership/identity attribution must remain ALLEGED until independently verified. Do not convert a Lookonchain label into canonical identity truth.

### 2. X post supplied for deep dive
https://x.com/lookonchain/status/1875814019724144710?s=46&t=SUBrcpc4yI4ppaXpURK03g

### 3. Lookonchain website supplied for source research
https://m.lookonchain.com

### 4. Independently discovered Lookonchain feed mirror/page
https://lookonchain.com/feeds/63065

This page reproduces the core allegation: the `Ansem-2` wallet spent $233K to purchase 2.79M CASHCAT and links it to Solana wallet CLM6E4.

## Why this belongs in Alpha Lab

This is useful primarily as a research object for wallet-behaviour analysis, not as influencer-following or a direct copy-trade signal.

Potential Alpha Lab questions:

1. Attribution confidence
   - Is `0x6f5b...3F5` genuinely controlled by the same entity as `CLM6E4...Kg1Q`?
   - What is the evidence chain linking either address to Ansem?
   - Is the relationship direct ownership, funding linkage, transfer linkage, exchange withdrawal linkage, naming heuristic, or social attribution?

2. Historical edge
   - Full trade history of both addresses where obtainable.
   - Realized vs unrealized PnL.
   - Hit rate is insufficient by itself, also measure payoff asymmetry, median return, drawdown, time-to-profit, time-to-loss, and survivorship bias.
   - Separate first-entry alpha from later averaging, transfers, airdrops and promotional/token-affiliation events.

3. Lead-lag value
   - Timestamp wallet entries against token price, liquidity, volume, holder growth, social activity and later Lookonchain/X publication.
   - Measure whether the wallet itself leads price, whether public Lookonchain publication leads price, or whether publication usually arrives after most alpha is gone.

4. Copy-trade feasibility
   - Simulate realistic delay windows, e.g. +1m, +5m, +15m, +30m, +1h after observable on-chain trade.
   - Include liquidity, spread, slippage, fees, MEV/front-running risk and exit capacity.
   - Compare wallet-entry replication against post-publication replication.

5. Regime dependence
   - Segment results by meme regime, chain, market cap/liquidity bucket and broad risk regime.
   - CASHCAT/ANSEM-era results must not be generalized automatically to normal altcoins.

6. Adverse-selection / manipulation risk
   - Check whether public-wallet awareness changes execution quality.
   - Detect buys followed by promotion, token transfers, insider/deployer relationships, concentrated supply or other conflicts.
   - Treat influencer-linked wallets as higher manipulation/confounding risk than anonymous smart-money wallets.

7. Signal extraction candidates
   - Wallet Conviction Score
   - Wallet Historical Edge Score
   - Entry Freshness / Alpha Decay
   - Liquidity-adjusted Replicability Score
   - Attribution Confidence
   - Promotion/Conflict Risk
   - Cluster Confirmation, independent high-quality wallets entering same asset

## Required Astra deep-dive output

Astra should not answer `is this wallet good?` qualitatively. Produce an auditable evidence package:

- address/entity graph with confidence per edge
- source provenance for every attribution
- transaction-level sample or full history where feasible
- PnL methodology and limitations
- event study around entries
- delayed-copy simulations
- liquidity/slippage sensitivity
- false-positive and failed-trade examples
- comparison with random/baseline wallets or appropriate benchmark
- publication-lag analysis for Lookonchain
- verdict per candidate feature: ADOPT / SHADOW TEST / RESEARCH ONLY / REJECT
- explicit kill criteria before any Alpha Lab signal is promoted

## Governance

- Shadow-only.
- No automatic buy/sell authority.
- No wallet identity claim without reproducible evidence.
- No cherry-picked winner-only evaluation.
- No use of Lookonchain labels as ground truth without independent corroboration.
- Preserve source timestamps because alpha decay is central to the hypothesis.
- Any future automated wallet-following concept requires forward testing and realistic execution costs before promotion.

## Initial verdict

KEEP FOR DEEP DIVE.

The highest-value hypothesis is not `copy Ansem`. It is whether a provenance-scored, liquidity-aware wallet-intelligence layer can identify repeatable early information before public dissemination, and whether that edge survives realistic observation and execution delay.
