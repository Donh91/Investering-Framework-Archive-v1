# Miles garchmethod, source-code triage
artifact_id: RL-AT-20261010-GARCH-CODE-001
source: https://github.com/milesdeutscher/garchmethod
source_type: third-party MIT-licensed code; code audit only
freeze: upstream tree e1e93d9bbced22ca74fc61858a62e4ca9e4a0607; direct file blob SHAs below
status: PRELIMINARY_STATIC_REVIEW, no numerical reproduction or installs were performed
owner: existing CN range tournament and AUTO_TRADING backtest research. NOT an accepted production risk/sizing model.

## Source inspected
- README: blob 0437ba9abbe334f686e947c90495f89546a48b29.
- scripts/garch_forecast.py: blob 99007d05f8726f8a19d07d5a2ad361e34ad5cb54.
- scripts/compare.py: blob d17830c40d4b757f92b1fed48a13710d62b92da8.
- scripts/vol_target.py: blob 75a9b3a721374742654f3e03af1a59ba2d5bb707.
- skills/garch/SKILL.md: blob d33d7135f09a25c262225cdc55d2c7c1fdf71b1c.
- Pine native `storm-gauge.pine` not used as GARCH forecast; upstream README explicitly says its gauge reflects REALIZED volatility, not future forecast.
- Upstream tree shows one initial commit and no test fixture suite in captured file tree; no evidence this is a field-validated strategy.
- MIT license appears present; *validate dependencies and license compliance before importing anything*.

## Static issue S1, priority HIGH: verify possible GARCH recursion off-by-one at refit
`walkforward_garch()`:
```
am = arch_model(rets[:t], ...)
res = am.fit(...)
sigma2 = res.conditional_volatility[-1] ** 2
eps = rets[t] - mu
sigma2 = omega + alpha * eps**2 + beta * sigma2
fcast_var[t] = sigma2
```
A conventional GARCH(1,1) 1-day forecast after observing `r_t` is
`h_(t+1) = omega + alpha * eps_t^2 + beta * h_t`.
At the refit, the initialized `res.conditional_volatility[-1]**2` corresponds to conditional variance of the *last in-sample point t-1*, not `h_t`. An intermediate variance update from residual `eps_(t-1)` appears to be missing before the update from `eps_t`.
This is a **static suspected index bug**, not a proven wrong series. Validate against `arch_model` one-step forecast re-fitted through t with fixed parameters, check first forecast after every 21-day refit, then compare next 20 days. If error proven, **only use corrected independently replicated code**, not upstream claim of zero lookahead.

## Static issue S2, priority MEDIUM: `--ticker` dependency not declared
`garch_forecast.py` PEP-723 header lists `arch,pandas,numpy,matplotlib` but ticker branch imports `yfinance` separately with ImportError bailout. Upstream README says first-run dependencies install automatically and no manual installation. For `--ticker`, this is a verifiable packaging inconsistency. Use frozen CSV mode for first research test to prevent network revision and isolate data provider. No dependency install needed for this source review.

## Static issue S3, priority HIGH: not a realistic trading comparison yet
`compare.py` uses next-day shift for signals and forecast sizing, encouraging causal alignment, but reports **gross return curves** without:
- trading fees, taxes, spreads, impact, latency or transaction rejection;
- turnover and target-leverage financing/borrowing, though multiplier can reach 2x;
- capacity/crowding or volatility regime breaks;
- same-risk alignment for fixed vs dynamic sizing.
Consequently **better gross Sharpe is not copyable or scalable alpha**; don't count as profitable or usable auto-trading.

## Static issue S4, priority MEDIUM: forecast & weight contracts
- `size_from_vol` caps multiplier to [0.25,2.0], but clipping positive size is not a defensible permanent risk limit for illiquid microcaps, and automatic 2x sizing must never flow to live orders.
- `load_prices` sorts and discards invalid/nonpositive closes but does not reject duplicate dates, resampled/non-daily interval mixtures or exchange/FX discrepancies; validate point-in-time price vintage separately.
- `load_signals` clips numeric signals [-1,1] rather than validating exactly {-1,0,1}, allowing unintended exposures.
- Parameter fitting suppresses warnings globally. Log convergence, parameter stability and failures (not silently interpret as calm).
- No current code evidence of proper crypto intraday calibration; daily GARCH forecast is not a 24h directional trading signal.

## Required rerun/acceptance
1. Freeze upstream SHA, dataset, currency, daily close definition and data observation time.
2. Unit test GARCH h_t recursion vs reference one-step forecasting across refit boundaries, including stationary/simple synthetic returns, price gap, zero returns, heavy tails, NaNs and insufficient history.
3. Compare original vs corrected code if S1 reproduces; label historical results affected.
4. Walk-forward predictive loss (QLIKE, squared variance error), compare EWMA, realized vol random walk, ATR; same risk and costed backtest; report all no-result/fail cases.
5. Pine Storm Gauge is only a visualization of realized-vol; no self-described 'forecast accuracy' from Pine.
6. If no incremental lift vs simple baseline, close NOOP / REJECT for any implementation, preserve test receipts.
7. Do not modify production CN, COMPASS, market states, leverages, risk weights, live alerts or `secrets` based solely on this package.

## Distinct economics
A model could improve *ex-ante sizing* while degrading fill/realized returns. Profitability requires separate entry edge; good vol forecast is not profit forecast. It is more plausibly a risk-control/control-model than an alpha generator.

Use existing issue ownership for execution and promotion gates; this note is independent research review, no tests or integration performed.
