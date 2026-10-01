# Conviction Wallet Intelligence - Execution Block 2

Date: 2026-10-01
Parent: #1419
Status: IN_PROGRESS / HISTORICAL_RESEARCH / SHADOW_ONLY

## Material findings

### GOAT early trader - Hdxk / blueblueblue.sol
Public contemporaneous reporting (Decrypt, 2024-10-16) identifies a wallet beginning `Hdxk`, also known as blueblueblue.sol, that:
- bought USD 5,520 GOAT in four roughly even purchases over ~30 minutes;
- had already realized USD 9,851 within ~5 hours;
- by day six had realized about USD 1.1m and retained about USD 413k GOAT;
- was described as a high-frequency Pump.fun trader holding/trading many other tokens.

Classification: HIGH_VALUE_DENOMINATOR_CANDIDATE, NOT SMART_MONEY_YET.
Why: exceptional GOAT outcome + partial profit-taking + retained upside is useful behavior, but the wallet's broad high-frequency activity makes hit-rate/base-rate reconstruction mandatory.

### FARTCOIN early conviction cluster - Sigil-associated hypothesis
Multiple later reports tracing PANews analysis identify:
- `4DPxYoJ5DgjvXPUtZdT3CYUZ3EEbSPj4zMNEVFJTd1Ts` as accumulating ~12.02m FARTCOIN via ~700 buys for ~USD 191k beginning 2024-10-18;
- `FEeSRuEDk8ENZbpzXjn4uHPz3LQijbeKRzhqVr5zPSJ9` as another accumulator (~400 buys) that later transferred ~7.4m FARTCOIN to 4DPxY;
- funding-chain reporting links FEeSR via a Binance deposit path to `EsqEkirkY6s1RPsb3YaJZcP4APQz77BWmBAVCsbNNhpj`, socially labelled Sigil Fund;
- reported initial positioning began ~5 hours after launch around ~USD 2m market cap;
- reported >USD 3m sold by 2024-12-19 while 4DPxY still held ~USD 6.09m.

Nansen later independently described a Sigil Fund memecoin wallet as having ~USD 6.10m accumulated profits, ~820 trades, a major FARTCOIN win but notable GOAT and BONK setbacks.

Classification: STRONG_CLUSTER_HYPOTHESIS / ATTRIBUTION_NOT_CANONICAL.
Why: early large intentional accumulation + distributed execution + retained position + explicit evidence of losers makes this an unusually useful denominator case. Entity attribution remains probabilistic until independently resolved.

### Important counterexample
A very early FARTCOIN address `Dt51tQyWGNGp1eg8MDXK1tukJEDV9JfDE6f5PuBQaoAN` reportedly bought ~494k tokens for 3.2 SOL at 08:20:53 on launch day, but was suspected to be sandwich-profit infrastructure.

Learning: earliest != alpha. Bot/MEV/profit-address classification is mandatory before wallet promotion.

## Hypothesis updates
H1 strengthened: retention after a large gain may matter, but only conditional on denominator.
H2 strengthened: distributed accumulation across related execution wallets can mimic independent convergence. Cluster independence must be proven before counting wallet votes.
H3 new: multi-hundred-order accumulation at low market cap may be a conviction fingerprint distinct from launch sniping.
H4 new: a wallet/fund with both spectacular winners and documented large losers is more useful for falsification than curated 'smart money' lists.

## Immediate next data tasks
1. Resolve full Hdxk address deterministically, then reconstruct all intentional bets in a fixed pre/post GOAT window.
2. Resolve FARTCOIN 4DPxY/FEeSR/EsqEki funding and control relationships with chain-native evidence.
3. Compare FARTCOIN cluster behavior with Sigil's GOAT/BONK losses rather than treating FARTCOIN as isolated success.
4. Add matched Pump.fun failures from the same October 2024 period.
5. Expand winner cohort with cases where first-buyer history can be reconstructed reproducibly.
6. Do not promote any wallet to Tier A/B until denominator and independence checks pass.

## Tooling implication
Solana first-buyer reconstruction should prefer deterministic transaction history / dedicated first-buyer APIs where available. Third-party labels are hypotheses, never ownership truth.

No BUY/SELL authority. No prospective credit from this historical work.
