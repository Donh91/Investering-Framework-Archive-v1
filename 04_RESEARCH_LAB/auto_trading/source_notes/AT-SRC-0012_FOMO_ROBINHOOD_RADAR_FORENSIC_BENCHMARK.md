# AT-SRC-0012 - FOMO Robinhood Radar forensic benchmark

Date captured: 2026-09-12
Status: DEEP_SCREENED / HIGH_VALUE_EXTERNAL_ARCHITECTURE_BENCHMARK
Evidence class: PUBLIC CODE + PUBLIC PROJECT LOG + AUTHOR CLAIMS
Authority: RESEARCH / SHADOW ONLY

## Sources

Owner-supplied X sources:

- `https://x.com/antpalkin/status/2098495219188863470?s=46&t=SUBrcpc4yI4ppaXpURK03g`
- `https://x.com/antpalkin/status/2085431604906766385?s=46&t=SUBrcpc4yI4ppaXpURK03g`

Public implementation:

- repository: `cvxv666/fomo-robinhood-radar`
- frozen external commit: `1c448e97a9617a19793aafb7963138e36ec5a1bf`
- license: MIT

The X post text supplied by the owner is treated as a claim snapshot. The repository, code and project log are the stronger implementation evidence.

## Why this source matters

This is not a generic smart-wallet dashboard. It directly addresses several failure modes that are already central to Memes v3 / Alpha Lab:

- profile-to-execution-wallet resolution;
- chain-native fill collection;
- transaction-receipt provenance;
- recipient-spoof / gifted-buy detection;
- dust and seeded-token contamination;
- wallet-book reconstruction;
- convergence / burst detection;
- exit consensus;
- prospective score calibration.

The project therefore qualifies as both:

`ADVERSARIAL_DATA_QUALITY_REFERENCE`

and

`ALPHA_LAB_ABLATION_CANDIDATE`.

It must not be forked wholesale into the Framework and must not become a new parallel signal engine.

## Load-bearing findings from the public code/log

### 1. Recipient provenance is a first-class problem

`fomo_agent/pipeline/provenance.py` documents and implements a concrete attack class where an outside key can execute a swap and name a famous/tracked wallet as recipient. A naive tracker sees the tracked wallet receiving tokens from a router and calls it a buy.

The project separates at least:

- `direct` — outside-key/router-directed activity, not the tracked wallet's own trade;
- `dust` — very small flow relative to the wallet's own size;
- `trade` — accepted intentional flow;
- seeded-token quarantine when pushed/dust activity overwhelms genuine trusted-wallet participation.

The project log states that the first live burst incident involved 17 trusted wallets apparently buying a token when none of them had intentionally bought it. It also records a second contamination case where low-dollar flows were pushed into 18 trusted wallets.

This strongly reinforces Alpha Lab's existing rule:

`ADDRESS_ROLE_GATE` is necessary but not sufficient.

Add the research principle:

`TRADE_PROVENANCE_GATE` before wallet convergence, wallet skill or entry conviction may consume a fill.

### 2. Thresholds evolved after adversarial failures

The public project log is unusually valuable because it preserves rule failures. The initial dust rule was too aggressive for a high-size wallet and incorrectly suppressed a genuine token. The threshold was subsequently reduced and the seeded rule gained an additional condition comparing seeded recipients with real buyers.

Research lesson:

- do not cargo-cult the project's current dust threshold;
- retain the attack/failure fixture and test alternative rules prospectively;
- threshold evolution is evidence, not a reason to assume the final threshold is universally correct.

### 3. Wallet resolution is useful, but source verification still wins

`pipeline/resolve.py` infers the execution wallet from repeated token/time windows and downweights crowded windows. The project reports 101/101 agreements against later source-verified wallets.

Useful principle:

`PROFILE_IDENTITY -> EXECUTION_WALLET -> ADDRESS_ROLE -> ENTITY`

not:

`PROFILE_ADDRESS == TRADER`.

The resolver is a strong benchmark fixture, not canonical truth.

### 4. BURST is a useful convergence primitive

`pipeline/hot.py` uses each wallet's first buy in a sliding window and weights wallet contribution by a trust score. This is substantially better than repeated-buy headcount.

However raw wallet conviction remains insufficient for Alpha Lab because correlated wallets, common funders or one economic entity can inflate apparent independence.

The Framework candidate should test:

`independent_entity_conviction`

against

`raw_wallet_conviction`.

### 5. The published burst performance is not yet promotion-grade evidence

The project reports a replay in which a selective burst rule fires far less often than a plain two-wallet feed and has somewhat better 2x/median-best outcomes.

Important caveat: `pipeline/hot.py` explicitly supports a `current` backtest mode that applies today's wallet scores to historical trades. The code describes this mode as reading the answer first. Only strict score-as-of-time mode is eligible for Alpha Lab promotion evidence.

Therefore reported values such as `5/day` and `39% reach 2x` are:

`INTERESTING_INTERNAL_REPLAY_CLAIM`

not

`VALIDATED_ALPHA`.

Required missing controls include executable entry, drawdown, regime, independent-entity count, matched token baseline, multiple-threshold selection and sealed forward validation.

### 6. FLYBRAIN timing needs replay-time vs delivery-time separation

The project reconstructs FLYBRAIN as having crossed its burst threshold before pool open and long before the later run. This is a valuable fixture.

But the project log also records that the data reached the database later and that the old live pipeline had approximately 15-20 minutes of end-to-end delay before a dedicated watcher was added.

Canonical research rule:

`signal_condition_time != detection_time != database_time != alert_delivery_time != executable_entry_time`.

A historical rule replay must never be presented as a historical live alert unless contemporaneous delivery evidence exists.

### 7. Exit consensus is high-value

The project explicitly distinguishes trimming from exiting and attempts to infer when tracked wallets have left most of the position. The CRUMBS case is presented as a token that moved from heavy trusted participation to broad cohort exit.

This maps directly to Alpha Lab's `FIRST_DISTRIBUTION_SURVIVAL` lane.

Candidate improvements:

- independent-entity exit acceleration;
- fraction of original conviction exited;
- genuine sell vs transfer/migration;
- liquidity-adjusted sell pressure;
- new-buyer absorption;
- remaining high-quality cohort.

### 8. Scoring is useful but materially weaker than Conditional Wallet Intelligence

The reproducible API scoring path in `pipeline/score.py` is Claude-based, while the public product can also export/import scoring through any LLM chat. The project log states that a `gpt-6 astra` UI label was retained for presentation/indexing while scoring is model-agnostic through export/import.

Therefore the owner-supplied post claim that `JUDGE is GPT-6 Astra` must not be interpreted as proof that Astra is the deterministic/default scorer in the public implementation.

More importantly, the scoring prompt gives large weight to headline Fomo PnL, including unrealized PnL. That is useful discovery evidence but not enough for Alpha Lab qualification.

Alpha Lab retains:

`wallet/entity x venue x entry-state x narrative x regime x liquidity x visibility`

rather than a global wallet score as canonical alpha.

### 9. The project's own calibration log falsifies part of its ranking claim

`pipeline/calibrate.py` correctly evaluates only positions opened after a wallet's earliest recorded verdict. This is a strong methodological choice.

But the public project log records a crucial result: realized outcomes separated active from dropped, while a marked-to-market reading caused `watch` to outperform `active`. The author explicitly concludes that the score separates bad from good better than it separates `active` from `watch`.

This negative result is more valuable than the marketing summary and must be retained.

Alpha Lab must not import the 70/40 score bands as if validated.

## What to borrow

High-value ablation targets:

1. receipt-level provenance;
2. recipient-spoof detection;
3. adaptive dust classification;
4. seeded-token quarantine;
5. first-buy convergence windows;
6. strict score-as-of-time replay;
7. exit consensus;
8. open/closed book reconstruction;
9. replayable failure fixtures;
10. fail-soft source handling.

## What to improve

Alpha Lab should test whether the external design is improved by:

- address-role classification before PnL;
- economic-entity clustering before convergence;
- conditional rather than global wallet skill;
- Cycle Navigator regime conditioning;
- signal visibility/capacity;
- executable-depth and slippage constraints;
- exact token/narrative-instance selection;
- first-distribution survival;
- matched failures and negative controls;
- sealed prospective validation;
- explicit separation of replay time from live delivery time.

## Explicit rejections

Do not import as canonical rules:

- global `0-100` wallet score;
- fixed dust percentage without calibration;
- current-score historical backtests;
- raw wallet count as independent confirmation;
- 2x-hit rate without executable/drawdown/baseline context;
- LLM model identity as evidence of alpha;
- autonomous execution from this source.

## Astra lane

When Astra is available, use the frozen benchmark for adversarial comparison, not routine chain collection.

Good Astra tasks:

- reason over conflicts between wallet identity, entity links, provenance and apparent convergence;
- blind red-team the burst and exit mechanisms;
- design causal/matched experiments;
- inspect project failure history for hidden assumptions;
- propose simpler variants that retain incremental value;
- adjudicate whether Alpha Lab's additional complexity actually improves forward discrimination.

Routine RPC collection, receipt classification and arithmetic remain deterministic/code-first.
