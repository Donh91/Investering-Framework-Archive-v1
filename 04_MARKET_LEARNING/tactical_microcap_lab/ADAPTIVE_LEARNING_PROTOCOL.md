# Meme Alpha Adaptive Learning Protocol

**Objective:** turn repeated token audits into a cumulative research advantage without overfitting, hindsight rewriting or promoting anecdotes into rules.

## Learning units

The lab learns at four distinct levels:

```text
CASE
WALLET / CLUSTER
SIGNAL SOURCE
REGIME / MARKET STRUCTURE
```

They must not be conflated.

A token can win despite a bad process. A Telegram source can be early once by luck. A wallet can be skilled but wrong on one token. A good setup can fail because the regime changed.

## Point-in-time freeze

Before a material recommendation is treated as evidence, preserve the best available point-in-time record:

```text
snapshot_utc
chain
contract
pair
market state
wallet findings
source context
recommendation
reason
entry trigger
invalidation
exit logic
major uncertainty
```

Later evidence may append outcome and adjudication fields but must not rewrite the original recommendation or original source timestamps.

## Fast-horizon outcome ladder

Meme trades can complete their entire lifecycle before ordinary research horizons mature.

Preferred observation ladder:

```text
+15m optional
+1h
+6h
+24h
+72h
+7d
```

Also preserve path metrics when obtainable:

```text
MFE
MAE
time_to_2x
time_to_5x
time_to_10x
time_to_minus_50pct
time_to_minus_80pct
peak_market_cap
peak_liquidity
lowest_liquidity
post_peak_drawdown
```

The first question is not "did price eventually go up?" but "was the original decision useful within the intended horizon and realistic liquidity?"

## Decision-quality adjudication

Each completed case should be assigned one descriptive quadrant:

```text
GOOD_DECISION_GOOD_OUTCOME
GOOD_DECISION_BAD_OUTCOME
BAD_DECISION_GOOD_OUTCOME
BAD_DECISION_BAD_OUTCOME
UNRESOLVED
```

This is qualitative until enough cases support calibrated scoring.

Examples:

- WAIT before an 85% collapse can be a good decision even if the token later revives.
- BUY followed by 5x can still be a bad decision if the evidence was weak and the win came from an unpredictable celebrity mention.
- REJECT followed by 20x may be defensible if the pool was unexitable for the intended size or contract risk was unacceptable.

## Hypothesis lifecycle

New patterns follow this state machine:

```text
OBSERVATION
-> HYPOTHESIS
-> HISTORICAL_CHALLENGE
-> FORWARD_CANDIDATE
-> FORWARD_OBSERVED
-> SUPPORTED / REJECTED / INCONCLUSIVE
```

No direct path exists from `OBSERVATION` to canonical rule.

Examples of hypotheses the lab may test:

- repeated creator-funded early-wallet clusters predict later distribution;
- certain launch venues show a reliable post-graduation base pattern;
- smart-wallet entry after seller exhaustion has better survival than buying the first major drawdown;
- quote-liquidity growth is more informative than market-cap recovery;
- Telegram callers differ materially in how early they surface plays;
- wallets with repeated good exits are more informative than wallets with merely high historical PnL;
- meme-regime expansion changes the value of confirmation versus earliest possible entry.

These are questions, not assumed truths.

## Anti-overfit controls

### 1. Count failures

When evaluating a wallet, caller, launchpad pattern or setup, include failed attempts and dead coins where observable.

### 2. Separate discovery from validation

Evidence used to discover a pattern should not be the only evidence used to validate it.

### 3. Forward-freeze promising signals

Once a wallet or setup is judged promising, freeze that state before future outcomes occur.

### 4. Do not optimize to one spectacular 100x

Track median behavior, drawdowns, hit distribution and realizable liquidity, not only maximum winners.

### 5. Preserve regime context

A pattern found in a manic meme regime may not transfer to quiet weekends or risk-off tape.

### 6. Prefer simpler explanations

If quote-liquidity growth plus seller exhaustion explains the edge, do not add six correlated indicators merely to improve historical fit.

## Source learning

Private signal sources can be evaluated without treating their claims as facts.

For each source alias, when enough user-provided history exists, preserve:

```text
signal timing relative to launch
market cap at first signal
pre-signal move
post-signal MFE / MAE
frequency of late calls
frequency of dead calls
whether claimed relationships gained on-chain support
whether calls correlate with distribution from linked wallets
```

Use non-identifying aliases in the public plane. Actual private identities or messages belong only in a private plane if they ever need storage.

Possible descriptive source states:

```text
UNASSESSED
EARLY_DISCOVERY_CANDIDATE
MIXED_TIMING
CONSISTENTLY_EARLY_SUPPORTED
OFTEN_LATE
DISTRIBUTION_RISK
INSUFFICIENT_SAMPLE
```

Do not infer intent from poor timing alone.

## Wallet learning

Wallet records mature separately from token cases.

A wallet may progress from:

```text
UNASSESSED
-> INSUFFICIENT_SAMPLE
-> REPEATABLE_EDGE_CANDIDATE
-> REPEATABLE_EDGE_SUPPORTED
```

or fall back to:

```text
MIXED_EVIDENCE
EDGE_DECAYED
LUCK_COMPATIBLE
```

A public analytics label such as `Smart Money` is an input, not a substitute for this lab's own evidence.

## Regime learning

The lab may study whether the opportunity set changes with observable market conditions, for example:

- chain DEX volume;
- new-pair / launch velocity;
- median new-token liquidity;
- meme breadth;
- percentage of new launches surviving 24h / 72h;
- distribution of first-day maximum returns;
- major-chain risk-on / risk-off context;
- weekend vs weekday behavior;
- broad altseason / speculative-liquidity state.

Regime context can alter confidence and preferred confirmation style, but it must not waive contract or liquidity checks.

## Review cadence

Do not force a fixed calendar review when there are too few new cases. Review when meaningful new evidence accumulates, and at thread handoffs when the lab has changed materially.

A review should ask:

1. Which heuristics helped avoid losses?
2. Which heuristics caused missed asymmetric winners?
3. Which wallet candidates survived forward observation?
4. Which supposed smart wallets regressed toward luck?
5. Which source aliases were consistently early or late?
6. Which market regimes materially changed entry quality?
7. Which evidence fields were expensive/noisy and should be removed?
8. Which missing field would have changed the decision?

## Promotion discipline

This lab has no portfolio authority by itself.

A heuristic can become a stronger lab rule only after evidence shows it improves a defined decision problem. Even then:

```text
LAB_RULE != CORE_FRAMEWORK_RULE
```

No Meme Alpha finding can silently modify Master Monday, Data Ping, canonical thresholds, long-conviction holdings or portfolio allocation.

## Research priority

The highest-value learning target is not predicting every meme winner.

It is improving the joint probability of:

```text
enter before the asymmetric move
avoid obvious coordinated distribution
size within actual liquidity
realize profits before the edge decays
avoid turning temporary speculation into permanent bagholding
```
