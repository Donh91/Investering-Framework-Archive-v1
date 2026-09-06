# Meme Alpha Lab - Adaptive Architecture

**Canonical human name:** Meme Alpha Lab  
**Stable repository path:** `04_MARKET_LEARNING/tactical_microcap_lab/`  
**Status:** LEARNING_AND_ADVISORY_ONLY  
**Authority:** NONE_BY_ITSELF

`Tactical Microcap Lab` remains a valid legacy/path name. The human-facing name is `Meme Alpha Lab` because the mission is broader than contract safety and narrower than long-horizon investing: discover, verify, enter and exit temporary speculative alpha in memes, microcaps, YOLO and casino plays.

## Mission

Optimize the quality of short-horizon decisions where:

- the asset may have little or no durable fundamental value;
- the edge can disappear within minutes, hours or days;
- wallet behavior, launch structure, distribution and liquidity matter more than long-term valuation;
- a successful outcome can be a temporary 2x, 5x, 10x, 25x, 100x or larger move;
- exit quality is part of the thesis from the beginning.

The lab is not designed to maximize the number of BUY calls. It is designed to maximize evidence quality, avoid obvious exit-liquidity traps and learn which observable patterns improve expected outcomes.

## System model

The lab has eight cooperating layers.

```text
1. SIGNAL INTAKE
      |
2. TOKEN / CONTRACT FORENSICS
      |
3. WALLET ALPHA GRAPH
      |
4. CONNECTED-WALLET / COORDINATION INFERENCE
      |
5. MARKET MICROSTRUCTURE + LIQUIDITY
      |
6. ENTRY / EXIT DECISION
      |
7. IMMUTABLE OUTCOME MATURATION
      |
8. ADAPTIVE LEARNING + RESEARCH
```

No later layer may silently repair missing evidence from an earlier layer.

## 1. Signal intake

A play may arrive from:

- Telegram or another private group;
- X / social media;
- Dexscreener / launchpad discovery;
- a wallet watchlist;
- a public analytics service;
- a prior case or recurring wallet cluster;
- direct user discovery.

The source is a discovery/timing input, not proof.

Capture point-in-time fields when available:

```text
signal_received_utc
chain
contract_address
pair_address
source_class
market_cap_at_signal
liquidity_at_signal
claimed_catalyst
claimed_relationship
expected_horizon
```

Private source identity is never required in the public repository.

## 2. Token and contract forensics

Before market interpretation:

- establish exact chain + contract + pair;
- detect copy/impersonation ambiguity;
- inspect factory, bytecode/source verification and admin controls;
- reconstruct launch transaction and launch configuration;
- identify deployer, creator, opening buyer, privileged wallets and liquidity path;
- identify transfer/tax/mint/freeze/blacklist/upgradeability risks where applicable.

A known factory can reduce custom-contract risk but cannot establish fair distribution or good entry quality.

## 3. Wallet Alpha Graph

The Wallet Alpha Graph is the core research asset.

It must learn from wallets across tokens rather than treating every token as an isolated event.

For every economically relevant wallet, preserve observations such as:

```text
wallet address
chain
first relevant observation
funding ancestry where observable
launch-relative entry time
entry market cap / price / liquidity
position size and pool share
exit times and exit sequence
realized / observable PnL where derivable
maximum favorable excursion while held
maximum adverse excursion while held
remaining balance
prior token participation
future token participation
co-trading wallets
creator / deployer / launch relationships
public labels with source and timestamp
```

The graph must distinguish a wallet address from a person. Identity claims require evidence.

See `WALLET_ALPHA_RESEARCH_PROTOCOL.md`.

## 4. Connected-wallet and coordination inference

The goal is not to accuse anonymous wallets of unlawful insider trading. The goal is to estimate whether behavior is consistent with privileged access, coordinated distribution, recurring early-access clusters or ordinary public speculation.

Evidence can include:

- direct creator/deployer funding;
- launch whitelist/tax exemption/bundle membership;
- same funder before multiple launches;
- repeated synchronized early entries;
- repeated synchronized exits;
- transfers between the wallets;
- repeated presence before public announcements;
- shared unusual counterparties;
- recurring cluster membership across independent successful launches;
- public attribution from a credible source.

Use evidence grades rather than unsupported labels:

```text
DIRECTLY_LINKED
STRONGLY_LINKED
REPEATED_CLUSTER_EVIDENCE
EARLY_ACCESS_PATTERN
WEAK_ASSOCIATION
NO_MATERIAL_LINK_FOUND
UNKNOWN
```

`insider` may be used in user-facing shorthand only when the evidential basis is stated. The stored research vocabulary should remain neutral and reproducible.

## 5. Market microstructure and liquidity

A strong wallet thesis can still be a bad trade if the current tape is wrong.

Capture fresh evidence for:

- market cap / FDV;
- total and quote-side liquidity;
- volume by horizon;
- buys vs sells;
- buy vs sell volume;
- unique buyers / sellers;
- holder count and trend when available;
- price structure;
- launch age;
- liquidity additions/removals;
- concentration of likely sellers;
- realistic entry and exit slippage for the intended trade size.

For tiny pools, market cap is a display statistic, not necessarily realizable value.

## 6. Entry and exit decision

The lab uses the existing four-way vocabulary:

```text
BUY
SPECULATIVE_BUY
WAIT
REJECT
```

Every material call should include:

- current evidence timestamp;
- primary upside mechanism;
- primary hidden risk;
- entry trigger or reason to act now;
- invalidation;
- realistic liquidity constraint;
- expected short horizon;
- profit-taking logic appropriate to the pool.

A failed tactical trade must not be silently converted to long conviction.

## 7. Immutable outcome maturation

Preserve the original recommendation and evidence before the outcome is known.

High-value meme horizons are shorter than ordinary investment research. Prefer observations around:

```text
+15m where data exists
+1h
+6h
+24h
+72h
+7d
```

Also capture path-dependent outcomes:

```text
MFE - maximum favorable excursion
MAE - maximum adverse excursion
time to 2x / 5x / 10x if reached
time to -50% / -80% if reached
peak liquidity
lowest liquidity
peak market cap
post-peak drawdown
survival / death / revival state
```

Outcome data must not rewrite the original call.

## 8. Adaptive learning and research

The lab learns across three units:

### Token-case learning
What evidence made this particular decision better or worse?

### Wallet learning
Which wallets repeatedly demonstrate early selection, profitable exits or connected behavior across independent events?

### Regime learning
Which broad conditions make meme alpha easier or harder to monetize, for example chain-specific DEX volume, speculative breadth, launch velocity, liquidity expansion or contraction?

No heuristic becomes a rule from one memorable winner.

Historical research may generate hypotheses. Promotion requires repeatable evidence and, where practical, forward observation. Keep descriptive evidence, hypothesis, candidate rule and validated rule as separate states.

See `ADAPTIVE_LEARNING_PROTOCOL.md`.

## Relationship to Master Monday / Data Ping

Master Monday, Data Ping and canonical portfolio owners may supply broad regime context. They do not authorize Meme Alpha Lab trades and Meme Alpha Lab does not rewrite their thresholds or weights.

```text
MASTER_MONDAY_AUTHORITY_CHANGE = NONE
DATA_PING_AUTHORITY_CHANGE = NONE
CANONICAL_PORTFOLIO_STATE_CHANGE = NONE
AUTOMATIC_EXECUTION = FORBIDDEN
```

The useful relationship is informational:

```text
core framework -> broad risk / liquidity regime context
Meme Alpha Lab -> token-specific microstructure and wallet evidence
user -> final execution and position size
```

## Research boundary

The lab may detect manipulation, coordination or suspicious distribution from public evidence. It is not a system for coordinating pumps, inducing other traders to buy, or participating in manipulation.

A known or suspected pump group should be treated as a distribution-risk input, not as permission to manipulate the market.

## Public / private data split

The control-plane repository is public. Therefore:

- public chain addresses, transactions and public labels can be stored here;
- private Telegram group names, private identities, invitation links, private messages and sensitive source details must not be stored here;
- if future source-performance tracking requires private identifiers, store only the minimum necessary representation in the private plane and reference it through a non-identifying alias from the public case record.

## Design rule

The lab should become more intelligent as cases accumulate, but not more confident merely because it has more data.

Every increase in complexity must earn its place by improving a measurable decision problem such as:

```text
avoid bad entry
identify connected distribution earlier
distinguish skilled wallet from lucky wallet
improve exit timing
improve realistic return after liquidity/slippage
reduce false-positive BUY calls
reduce false-negative missed asymmetry
```
