# Global Liquidity Causal Chain, preregistered analysis contract v1

**Status:** DESIGN_FROZEN / ECONOMIC_EXECUTION_LOCKED  
**Existing owners:** BT11, BT15, GRA04, GRA07 and Sensor Relationship & Incremental Value Standard

This creates no active market test, engine, live sensor or permission.

## A. Exact claim replication

Replicate a public numeric claim only if its original series, transformation, frequency, sample, lead-lag, smoothing and vintage policy can be recovered. Otherwise label outputs:

`RECONSTRUCTED_CHALLENGER_NOT_ORIGINAL_GMI`

No correlation is accepted from a dual-axis chart.

## B. Statistical definitions

For BTC and Nasdaq calculate separately:

1. price-level correlation;
2. log-level correlation;
3. return versus liquidity-growth correlation;
4. detrended residual correlation;
5. forward return versus lagged liquidity change;
6. rolling correlation and rolling beta;
7. cointegration only after unit-root diagnostics;
8. nonlinear and rank dependence as challengers.

Frequencies:

- weekly for market and transmission series;
- monthly and quarterly for fiscal and slow global-liquidity series;
- no silent interpolation across publication gaps.

Lead-lag grid:

- weekly: 0 to 156 weeks;
- monthly: 0 to 36 months;
- predictor knowledge time must precede outcome time.

Multiplicity:

- raw result;
- Holm family-wise result;
- Benjamini-Hochberg result;
- block-permutation family maximum;
- no lag selected from the final holdout.

## C. Real-time-vintage control

Every macro row preserves observation period, publication timestamp, retrieval timestamp and earliest defensible knowledge time. Current revised history is descriptive only unless an archived release or ALFRED vintage proves historical availability.

Compare:

- `CURRENT_VINTAGE`;
- `REAL_TIME_VINTAGE`;
- publication-lagged pseudo-real-time challenger.

## D. Causal chain and Liquidity Delivery Gap

Build separate, inspectable indices:

- Liquidity Requirement: interest payments, refinancing, deficit and issuance pressure;
- Liquidity Delivery: realised central-bank balance, reserves, broad money, bank credit and global dollar credit;
- Liquidity Delivery Gap: standardised requirement minus standardised delivered liquidity;
- Transmission State: dollar, real yields, credit spreads, volatility and crypto-native flow;
- Price Acceptance: settled BTC and Nasdaq trend, breadth and participation.

No scalar composite receives live authority.

## E. Out-of-sample and regime design

Use purged expanding walk-forward and preserve a final chronological holdout.

Required era splits:

- pre-2017 BTC market;
- 2017-2019;
- 2020-2021;
- 2022-2023;
- 2024 onward ETF regime.

Report sign flips, unstable lags, missingness regimes, crisis concentration and leave-one-era-out results.

## F. Incremental framework value

Compare sequentially:

1. simple price trend;
2. global-liquidity family alone;
3. existing framework macro state;
4. existing macro state plus liquidity family;
5. macro plus realised liquidity plus transmission;
6. full chain plus price acceptance.

The new family adds value only if it improves a declared out-of-sample endpoint without unacceptable degradation in MAE, missed upside, false transition or delay.

## G. Decision utility

Forbidden until G20 permits controlled economic execution.

Sell-side endpoints:

- drawdown avoided;
- upside foregone;
- false-exit cost;
- time out of market;
- utility versus hold and 40-week trend.

Rebuy-side endpoints:

- 4, 13, 26 and 52-week return;
- MFE and MAE;
- maximum drawdown;
- false-entry cost;
- missed upside under WAIT;
- time to final low and price confirmation.

## H. Derived research

Preregistered derived objects:

- BTC Liquidity Beta, time-varying and regime-tagged;
- BTC Liquidity Residual, with stationarity and duration tests;
- Liquidity Quality decomposition by reserves, broad money, credit, fiscal transfers, stablecoins, ETF capital and leverage;
- Policy Reaction Function challenger;
- Form Driver versus Edge Driver attribution.

## Kill criteria

Reject live or canonical promotion when any applies:

- claim survives only in levels, not growth or returns;
- optimal lag is unstable or selected by final holdout;
- real-time vintage reverses the result;
- effect disappears after DXY, real yields, credit and price trend;
- plausible liquidity specifications disagree on sign or action;
- decision utility loses to a simple trend baseline;
- sample is dominated by one crisis or one BTC era.

## Authority

No market-state change, gate change, rebuy change, deployment change or portfolio action.
