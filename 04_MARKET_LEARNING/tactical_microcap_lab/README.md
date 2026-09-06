# Tactical Microcap Lab

**Status:** LEARNING_AND_ADVISORY_ONLY  
**Authority:** NONE_BY_ITSELF  
**Scope:** short-horizon, high-risk meme / microcap / YOLO / casino trades where the expected edge is temporary and the asset may rapidly decay.

## Purpose

This lab exists to improve decisions in speculative plays that are explicitly **not long-conviction investments**.

Typical objective:

```text
find asymmetric short-lived opportunity
avoid obvious bad entries and insider exits
enter only when risk/reward and tradable liquidity are acceptable
realize temporary wins before the trade thesis decays
learn from every audited setup without hindsight rewriting
```

The target opportunity can be 2x, 5x, 10x, 100x or more, but upside ambition never converts weak evidence into a buy signal.

## User shorthand

When a thread or intake uses terms such as:

```text
meme
microcap
yolo
casino
meme - besyv?
```

interpret the request as **short-horizon speculative trade analysis**, not a request to assess long-term quality or portfolio conviction.

A token may therefore be fundamentally weak but tactically interesting, or technically legitimate but tactically unattractive.

## Core distinction

```text
LEGIT PROJECT != GOOD ENTRY
LOW MARKET CAP != CHEAP
-70% / -90% != BOTTOM
GOOD NARRATIVE != GOOD LIQUIDITY
HIGH UPSIDE != HIGH EXPECTED VALUE
TEMPORARY WIN != LONG-TERM CONVICTION
```

The lab optimizes for entry quality, exit realism, wallet intelligence and survival through a fast-moving speculative cycle.

## Audit flow

Each serious token audit should follow, at minimum:

1. Identity and correct contract / chain.
2. Contract and admin-risk review.
3. Launch forensics.
4. Deployer, creator, insider and privileged-wallet tracing.
5. Holder concentration with LP / contracts / lockers separated from real holders.
6. Liquidity and realistic exit analysis.
7. Current market microstructure, including volume, buys/sells, unique traders and price path.
8. Narrative, catalyst and social-distribution quality.
9. Historical behavior of relevant wallets when evidence is available.
10. Entry map, invalidation and likely profit-taking logic.
11. Clear decision: `BUY`, `SPECULATIVE_BUY`, `WAIT`, or `REJECT`.
12. Any additional evidence that becomes materially relevant during the investigation.

The detailed guide lives in `TOKEN_AUDIT_GUIDE.md`.

## Entry philosophy

Do not treat a large drawdown as an entry signal by itself.

For falling-knife microcaps, prefer evidence such as:

```text
base formation
seller exhaustion
higher low
reclaim of a lost level
returning volume
improving buyer / seller structure
holder stabilization or growth
credible catalyst or renewed narrative distribution
```

Paying a higher market cap after real confirmation can be superior to buying a lower market cap while the token is still structurally dying.

## Wallet intelligence

Wallet analysis is a first-class component, not a decorative appendix.

Where possible, inspect:

```text
creator / deployer
opening buy
launch exemptions
bundled or privileged buyers
funding provenance
shared counterparties
wallet clusters
historical launches
historical sell behavior
current balances
LP / locker / pool addresses
```

No wallet should be labelled `insider` solely because it bought early. Use evidence and distinguish:

```text
confirmed relationship
strongly linked
probable cluster
possible link
unknown
```

## Liquidity discipline

Displayed market cap is not automatically realizable value.

Always distinguish:

```text
market cap
FDV
pool liquidity
quote-side liquidity
trade size
estimated slippage
realistic exit capacity
```

A theoretical 20x is not useful if the intended position cannot be exited near the displayed price.

## Relationship to Master Monday and the core framework

This lab may consume broad regime context from Master Monday, Data Ping or other framework owners, for example whether speculative alt/meme liquidity is expanding or contracting.

It does **not** modify those owners and does not inherit their portfolio authority.

```text
CANONICAL_PORTFOLIO_AUTHORITY_CHANGE = NONE
MASTER_MONDAY_THRESHOLDS_CHANGE = NONE
DATA_PING_THRESHOLDS_CHANGE = NONE
AUTOMATIC_TRADE_EXECUTION = FORBIDDEN
LONG_CONVICTION_PROMOTION = FORBIDDEN_BY_DEFAULT
```

A good casino setup must remain explicitly segregated from long-conviction reasoning.

## Sizing principle

Casino capital should be treated as a separate risk bucket. Position size is decided case by case from current portfolio size, token liquidity, estimated exit capacity and maximum acceptable loss.

The existence of large portfolio gains during altseason may justify reviewing the casino budget, but it does not justify silently scaling individual bets or weakening token-specific risk checks.

## Learning loop

Every material audit should preserve a timestamped point-in-time record before the outcome is known.

Useful follow-up fields include:

```text
+1h
+6h
+24h
+72h
maximum favorable excursion
maximum adverse excursion
peak market cap
lowest market cap
liquidity path
whether the original entry decision was useful
what evidence mattered
what looked important but was noise
```

Outcomes calibrate future audit quality. They must not rewrite the original evidence or recommendation.

The aim is to learn repeatable microstructure and wallet patterns, not to celebrate isolated winners.

## Initial case

The first preserved case is TAGPAD on Robinhood Chain, where an initial `WAIT` call near roughly $22k market cap was followed by a collapse toward roughly $3.3k rather than the expected reversal. The case is stored under `cases/2026-09-05__TAGPAD__robinhood.md` as an example of why narrative quality and low market cap do not override active sell pressure and launch-wallet evidence.
