# AT-SRC-0015 - Polymarket Users behavioral benchmark dataset

Date captured: 2026-09-13
Status: ADMITTED / HIGH VALUE BENCHMARK SOURCE
Source: https://huggingface.co/datasets/vgregoire/polymarket-users
License on processed research data: CC-BY-4.0, subject to the dataset card's field-level caveats for Polymarket-originated metadata
Related paper: Akey et al. 2026, `Who Wins and Who Loses In Prediction Markets? Evidence from Polymarket`

## Why admitted

This is not another trading strategy. It is a large, public behavioral/microstructure benchmark that can help prevent the EdgeOnchain case from overfitting to one visible account.

The dataset card reports:

- sample period 2022-11-11 through 2026-03-29 UTC;
- public Polygon on-chain CTF Exchange `OrderFilled` events as the base source;
- reconciled end-user identification using Polymarket's proxy/safe wallet pattern;
- approximately 3.12 billion rows across all published tables;
- approximately 119 GB total size;
- market/event metadata, token/prediction mapping, user behavioral features, terminal and daily P&L variants, trades and OHLCV aggregates;
- `user_features` includes behavioral measures such as maker/taker share;
- the `trades` data retains maker and taker addresses so role can be reconstructed at row level.

## Important version-history lesson

The dataset's changelog is itself useful scientific evidence about why immutable versioning matters.

Reported corrections include:

- v1.1 corrected P&L panel construction and removed large leakage/inconsistency in variant panels;
- v1.2 removed undocumented maker/taker terminal-PnL columns whose category recombination was inconsistent for users who acted in both roles, while retaining role reconstruction in the trade rows;
- v1.3 corrected directional longshot/sureshot feature aliases.

The published headline concentration statistics reportedly remained unchanged across those corrections, but underlying panels changed materially.

Framework consequence:

`DATASET VERSION != COSMETIC METADATA`.

Every derived benchmark result must bind to the exact dataset version/commit and table subset used.

## EdgeOnchain use

The dataset ends on 2026-03-29, so it may not cover the full later EdgeOnchain history and must not be treated as Edge's canonical ledger.

Its correct role is benchmark/reference data for:

- maker/taker behavioral priors;
- spread-adjusted versus raw P&L comparisons;
- matched trader cohorts;
- longshot/sureshot behavior;
- category concentration;
- turnover/holding behavior;
- market calibration/microstructure controls;
- sanity-checking any Edge-specific feature engineering.

Potential Edge questions it can contextualize:

- Is Edge unusually maker-heavy or taker-heavy relative to profitable cohorts?
- Is Edge's price/odds distribution unusual relative to profitable users?
- Is Edge concentrated in market categories or time regimes that already show different baseline economics?
- Does Edge resemble a known profitable behavioral cluster, or is its revealed policy distinct?

## Storage decision

Do not mirror 119 GB into the public Framework repository.

Preserve:

- canonical dataset URL;
- exact version/commit used for each experiment;
- schema/table contract;
- hashes for any downloaded subset;
- query/filter code;
- minimal derived benchmark artifacts required for reproducibility.

If a private large-data mirror is later justified, it belongs in the restricted data plane, not the public control plane.

## Promotion boundary

This dataset is a `BENCHMARK / CONTROL SOURCE`, not signal authority.

No strategy gains confidence merely because it resembles historically profitable users. Any candidate still requires #885 point-in-time, out-of-sample, cost-aware validation.