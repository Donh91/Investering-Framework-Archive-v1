# MAEVE REVERSE-ENGINEERING READINESS v1

Status: READY FOR BOUNDED BEHAVIORAL RECONSTRUCTION / NOT READY FOR UNCONSTRAINED MODELING
Standing-lane candidate: `EXT-ALPHA-0002`
Standing-lane owner: #937
Scientific lifecycle: #885

## Why this file exists

MAEVE is now routed through the same generic external-strategy reverse-engineering method as EdgeOnchain and future externally successful AI traders.

This does not replace the existing MAEVE archive. It converts current evidence into an explicit readiness decision and next experiment ladder.

## Current evidence state

The current MAEVE archive reports:

- 432 parent positions;
- 426 closed / 6 open;
- 1,073 recovered fills, including 641 DCA legs;
- 318 matched public social posts;
- 256 exact entry+exit price matches;
- near-complete reconstruction of the recoverable archived dashboard era;
- provider-side CFGI historical availability for MARKET/BTC/ETH on native 15m/1h/4h/1d back to March 2022;
- targeted locally materialized 1h BTC/ETH event windows;
- immutable point-in-time 4h and 1d forward cold-raw captures in the inspected archive period.

The standing Astra handover defines a heavy-modeling trigger of >=200 well-formed action/position rows, >=20% coverage of a documented epoch, or direct historical dashboard/API trade data.

The row-count and archived-era coverage triggers are therefore materially satisfied.

This is not permission to fit the largest possible model. The remaining bottleneck is feature-time integrity and construction of valid negatives / opportunity sets.

## Current admission ruling

`REVERSE_ENGINEER`

Reason:

The action-label dataset is now large enough to justify behavioral reconstruction, while the public-feature state still needs leakage-safe joining and no-trade controls before a clone can be graded.

## Critical leakage boundary

The existing archive explicitly warns that recovered `analisis_hora` is approximately one hour after entry and that related impulse/volatility/volume sub-score columns are look-ahead suspect until timestamp semantics are resolved.

Therefore:

- `cfgi_score_entry` is currently the cleanest recovered entry-time CFGI feature;
- suspect post-entry fields remain excluded from entry-model features;
- provider availability metadata is not equivalent to locally materialized point-in-time rows;
- derived 2h features may use only already-closed 1h observations;
- random train/test splits are insufficient.

## Experiment ladder

### M0 - action-ledger freeze

Freeze a versioned research subset from the restricted authoritative MAEVE package.

Preserve at minimum:

- parent position ID;
- action/fill ID;
- ENTRY / DCA / EXIT;
- asset;
- timeframe;
- action timestamp;
- price;
- size where available;
- parent linkage;
- version/era where supportable;
- source/provenance reference;
- final position result.

No public repo copy of restricted provider values is required. Public control-plane artifacts may contain hashes, schemas, coverage and derived non-restricted results.

### M1 - minimal clean entry model

Question:

`How much of MAEVE ENTRY timing can be explained by information already proven time-valid?`

Initial feature set should be deliberately small:

- clean entry-time CFGI score;
- asset;
- timeframe;
- time-of-day / day-of-week where defensible;
- contemporaneous price-return / volatility state from point-in-time market data;
- broad Framework regime state only if it can be reconstructed without hindsight.

Required controls:

- matched no-trade observations;
- frequency-only baseline;
- CFGI level-only baseline;
- price-state-only baseline.

Preferred first models:

- conditional frequency tables;
- logistic/multinomial regression;
- shallow decision tree / rule list.

No deep model until simple baselines have been exhausted.

### M2 - opportunity-set reconstruction

The key missing object is the set of moments/assets MAEVE plausibly could have acted on but did not.

Construct matched negative observations using only documented asset/timeframe universe and time-valid features.

Negatives must be sampled without using future outcome information.

Test sensitivity to negative-sampling policy. A clone that only works under one convenient negative construction is not identified.

### M3 - public CFGI feature ablation

After timestamp adjudication, test incremental value from:

- CFGI velocity;
- rolling percentile/range location;
- cross-timeframe disagreement;
- asset-vs-MARKET CFGI divergence;
- component values / component velocity where historical mapping is valid;
- 15m micro-dynamics;
- 1d regime/risk context;
- 1h and 4h native baselines.

Every feature family must be compared to the clean minimal model.

### M4 - DCA decomposition

Do not let MAEVE's position win rate hide poor initial entries.

Separately model:

- probability of DCA conditional on first entry state;
- DCA count and spacing;
- capital added per DCA;
- MAE before rescue;
- position PnL with and without DCA;
- capital-weighted return;
- risk concentration during simultaneous DCA episodes.

The archive already shows a large difference between no-DCA first-entry win rate and DCA-required first-entry win rate, making this a priority causal decomposition.

### M5 - exit / hold policy

Model EXIT separately from ENTRY.

Candidate questions:

- is exit primarily explained by absolute CFGI level?
- change in CFGI since entry?
- target / price return?
- time in trade?
- reversal in market/regime state?
- interaction with prior DCA?

Use survival/time-to-exit methods where appropriate.

### M6 - version / era split

Do not force one policy across architectural eras.

Test whether early/v1-like and later/v2-like behavior require separate models.

A version boundary is evidence only when supported by the archive, not because a model fits better after arbitrary splitting.

### M7 - Framework incremental-value test

Once a public-feature MAEVE clone is frozen, compare:

1. simple market baseline;
2. clean MAEVE public-feature clone;
3. Framework regime / market-direction baseline;
4. MAEVE clone + Framework context.

This is the most important transfer test.

The objective is not maximum action agreement with MAEVE. The objective is whether MAEVE-derived primitives add incremental post-cost value to the Framework's own market intelligence.

### M8 - residual analysis

Only after M1-M7:

Study systematic decisions the public-feature clone fails to explain.

Residual structure may nominate latent-factor hypotheses, feature interactions or timing rules.

Failure to explain an action is never proof of a specific hidden/private signal.

More flexible models, including constrained representation learning or inverse-policy methods, may be tested only if they add chronological OOS value and preserve interpretability enough for ablation.

### M9 - frozen clone competition

Freeze the best transparent MAEVE-inspired candidates before forward simulation.

Compete them under common clock/common cost against:

- simple CFGI rules;
- price/volume baselines;
- Framework regime-only strategy;
- other admitted strategy families.

Track:

- post-cost return;
- drawdown;
- turnover;
- exposure;
- MFE/MAE;
- DCA capital intensity;
- missed-opportunity cost;
- regime-conditioned stability;
- parameter sensitivity.

## Promotion rule

MAEVE history may teach the Framework, but historical similarity alone cannot promote a primitive.

A primitive becomes transfer-eligible only after:

- clean point-in-time evidence;
- interpretable attribution / ablation;
- chronological OOS or frozen-forward support;
- incremental value over an existing Framework owner;
- realistic fees/slippage/latency;
- explicit kill criteria.

## Highest-value near-term task

The next research object is not another architecture theory.

It is:

`MAEVE actions + leakage-clean point-in-time CFGI/market state + matched NONE controls`

That joined dataset is the minimum viable substrate for the first serious behavioral clone.

## Expected Astra role

Astra should consume this readiness bridge after reading the full MAEVE archive and current #885 lifecycle.

Its first job is to maximize evidence quality and falsification power, not model complexity.

Astra should stop, downgrade or simplify whenever a result is explainable by leakage, DCA rescue, regime exposure, counting conventions or other non-transferable mechanisms.
