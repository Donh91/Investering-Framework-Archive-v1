# Meme Alpha Lab

**Stable path / legacy name:** `tactical_microcap_lab` / Tactical Microcap Lab  
**Status:** LEARNING_AND_ADVISORY_ONLY  
**Authority:** NONE_BY_ITSELF  
**Scope:** short-horizon, high-risk meme / microcap / YOLO / casino trades where the expected edge is temporary and the asset may rapidly decay.

## Purpose

This lab exists to improve decisions in speculative plays that are explicitly **not long-conviction investments**.

Typical objective:

```text
find asymmetric short-lived opportunity
avoid obvious bad entries and connected-wallet distribution
enter only when risk/reward and tradable liquidity are acceptable
realize temporary wins before the trade thesis decays
learn from every audited setup without hindsight rewriting
```

The target opportunity can be 2x, 5x, 10x, 25x, 100x or more, but upside ambition never converts weak evidence into a buy signal.

`Meme Alpha Lab` is the human-facing name. The existing repository path is intentionally retained for compatibility and to avoid unnecessary structural churn.

## User shorthand and thread lineage

When a thread or intake uses terms such as:

```text
meme
microcap
yolo
casino
meme - besyv?
```

interpret the request as **short-horizon speculative trade analysis**, not a request to assess long-term quality or portfolio conviction.

User-facing thread lineage should be simple:

```text
MEMES v1
MEMES v2
MEMES v3
...
```

GitHub is the persistent research layer across thread versions. Live market evidence must still be refreshed in every new thread.

See `THREAD_VERSIONING_AND_HANDOFF.md`.

A token may therefore be fundamentally weak but tactically interesting, or technically legitimate but tactically unattractive.

## Core distinction

```text
LEGIT PROJECT != GOOD ENTRY
LOW MARKET CAP != CHEAP
-70% / -90% != BOTTOM
GOOD NARRATIVE != GOOD LIQUIDITY
HIGH UPSIDE != HIGH EXPECTED VALUE
TEMPORARY WIN != LONG-TERM CONVICTION
EARLY BUYER != INSIDER
HIGH HISTORICAL PNL != REPEATABLE EDGE
```

The lab optimizes for entry quality, exit realism, wallet intelligence and survival through a fast-moving speculative cycle.

## Architecture

The persistent learning system is documented in `MEME_ALPHA_ARCHITECTURE.md`.

Core flow:

```text
signal intake
-> token / contract forensics
-> wallet alpha graph
-> connected-wallet / coordination inference
-> market microstructure + liquidity
-> entry / exit decision
-> immutable outcome maturation
-> adaptive learning / research
```

Wallet research is governed by `WALLET_ALPHA_RESEARCH_PROTOCOL.md` and learning by `ADAPTIVE_LEARNING_PROTOCOL.md`.

## Audit flow

Each serious token audit should follow, at minimum:

1. Identity and correct contract / chain.
2. Contract and admin-risk review.
3. Launch forensics.
4. Deployer, creator, connected and privileged-wallet tracing.
5. Holder concentration with LP / contracts / lockers separated from real holders.
6. Liquidity and realistic exit analysis.
7. Current market microstructure, including volume, buys/sells, unique traders and price path.
8. Narrative, catalyst and social-distribution quality.
9. Historical behavior of relevant wallets when evidence is available.
10. Skill-vs-luck challenge for apparently successful early wallets.
11. Entry map, invalidation and likely profit-taking logic.
12. Clear decision: `BUY`, `SPECULATIVE_BUY`, `WAIT`, or `REJECT`.
13. Any additional evidence that becomes materially relevant during the investigation.

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
historical winners AND failures
historical sell behavior
current balances
LP / locker / pool addresses
```

The lab specifically tries to distinguish:

```text
one lucky early buy
vs
repeatable early-selection skill
vs
repeatable connected / privileged access
vs
coordinated distribution
```

Those are different hypotheses and must remain separate.

No wallet should be labelled `insider` solely because it bought early. Store neutral evidence grades:

```text
DIRECTLY_LINKED
STRONGLY_LINKED
REPEATED_CLUSTER_EVIDENCE
EARLY_ACCESS_PATTERN
WEAK_ASSOCIATION
NO_MATERIAL_LINK_FOUND
UNKNOWN
```

The strongest wallet candidates should be frozen into forward watch before their next outcomes are known. This is how the lab learns whether apparent edge survives hindsight selection.

## Public/free source model

The lab should remain useful without premium subscriptions.

Core evidence should be recoverable from public/on-chain sources when possible. Free/public Nansen surfaces can be used for wallet PnL, labels, Smart Money discovery or holder context where accessible, but Nansen is an enrichment source rather than a required authority.

No premium subscription or paywall circumvention is part of the design.

See `PUBLIC_SOURCE_POLICY.md`.

## Private Telegram source discipline

Private groups are valuable discovery channels, but claims are not evidence by themselves.

Source performance may be learned over time from signal timing and later outcomes. The public framework should use pseudonymous aliases only. Private group names, identities, invite links and sensitive messages must not be stored in this public repository.

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

The useful relationship is:

```text
core framework = broad market / liquidity context
Meme Alpha Lab = token-specific temporary alpha analysis
user = final execution and position size
```

## Sizing principle

Casino capital should be treated as a separate risk bucket. Position size is decided case by case from current portfolio size, token liquidity, estimated exit capacity and maximum acceptable loss.

The existence of large portfolio gains during altseason may justify reviewing the casino budget, but it does not justify silently scaling individual bets or weakening token-specific risk checks.

## Learning loop

Every material audit should preserve a timestamped point-in-time record before the outcome is known.

Useful follow-up fields include:

```text
+15m where available
+1h
+6h
+24h
+72h
+7d
maximum favorable excursion
maximum adverse excursion
time to 2x / 5x / 10x
peak market cap
lowest market cap
liquidity path
whether the original entry decision was useful
what evidence mattered
what looked important but was noise
```

Outcomes calibrate future audit quality. They must not rewrite the original evidence or recommendation.

The lab learns separately at four levels:

```text
CASE
WALLET / CLUSTER
SIGNAL SOURCE
REGIME / MARKET STRUCTURE
```

The aim is to learn repeatable microstructure and wallet patterns, not to celebrate isolated winners.

## Manipulation boundary

The lab may detect signs of coordinated pumps or distribution in order to assess risk and avoid becoming exit liquidity. It is not designed to coordinate a pump, induce other traders to buy or participate in market manipulation.

## Initial case

The first preserved case is TAGPAD on Robinhood Chain, where an initial `WAIT` call near roughly $22k market cap was followed by a collapse toward roughly $3.3k rather than the expected reversal. The case is stored under `cases/2026-09-05__TAGPAD__robinhood.md` as an example of why narrative quality and low market cap do not override active sell pressure and launch-wallet evidence.
