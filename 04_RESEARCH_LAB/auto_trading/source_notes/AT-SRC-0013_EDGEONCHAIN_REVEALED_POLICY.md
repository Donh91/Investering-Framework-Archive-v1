# AT-SRC-0013 - EdgeOnchain / revealed-policy reverse engineering

Date captured: 2026-09-13
Status: HIGH PRIORITY RESEARCH_QUEUED
Evidence class: PUBLIC DOCUMENTATION + PUBLIC PREDICTION-MARKET FOOTPRINT + UNVERIFIED PERFORMANCE CLAIMS
Issue: `#922`
Research queue: `../EDGEONCHAIN_FORENSIC_RESEARCH_QUEUE.md`
Generic method: `../EXTERNAL_STRATEGY_REVERSE_ENGINEERING_PROTOCOL_v1.md`

## Sources

Primary / project sources:

- https://edgeonchain.gitbook.io/docs/
- https://edgeonchain.gitbook.io/docs/overview/meet-oddy
- https://edgeonchain.gitbook.io/docs/overview/our-edge
- https://edgeonchain.gitbook.io/docs/the-vaults/how-it-works
- https://polymarket.com/profile/%40EdgeOnchain
- https://projects.assuredefi.com/project/edgeonchain

Primary venue/API documentation:

- https://docs.polymarket.com/market-data/overview
- https://docs.polymarket.com/api-reference/core/get-user-activity
- https://docs.polymarket.com/api-reference/core/get-trades-for-a-user-or-markets
- https://docs.polymarket.com/api-reference/core/get-closed-positions-for-a-user
- https://docs.polymarket.com/api-reference/misc/download-an-accounting-snapshot-zip-of-csvs

Social screenshots and public posts are discovery evidence only unless independently reconciled to primary ledger data.

## Executive verdict

The highest-value reason to study EdgeOnchain is not the `$EDGE` token, headline PnL or the future vault product.

The unusually valuable research opportunity is that an external strategy may be observable through:

`market state -> actual selection -> execution price -> position size -> settlement`

That makes Edge a clean reference case for **behavioral strategy reverse engineering**.

The Framework should not attempt to recover proprietary source code. It should reconstruct the strategy's **revealed decision policy** and then test which parts, if any, remain useful after observation latency, costs and capacity.

## Core research questions

### 1. Selection policy

Can point-in-time observable market features explain which eligible markets Edge chooses and which it ignores?

Required form:

`P(Edge action | point-in-time opportunity set)`

Candidate explanatory variables include:

- market-implied probability;
- sport / league / market type;
- time to event;
- available liquidity;
- price movement before entry;
- market breadth / candidate count;
- published model probability or stated edge when available.

Chosen markets alone are insufficient. Matched non-selected markets are required to avoid selection bias.

### 2. Sizing policy

Can Edge's stake size be explained by observable variables such as:

- implied probability;
- estimated edge / confidence;
- bankroll;
- current exposure;
- correlated-event exposure;
- market liquidity;
- drawdown / risk state?

This separates **prediction quality** from **capital-allocation quality**.

A strong equity curve produced mainly by compounding or aggressive sizing must not be misclassified as superior forecasting.

### 3. Timing policy

Does Edge enter at systematically advantageous times relative to subsequent market repricing?

For each source action record:

- source entry timestamp;
- first independent observable timestamp;
- event start;
- subsequent market probability / price path.

If Edge regularly enters before favorable probability movement, that is stronger evidence than headline hit rate alone, though still not sufficient without matched controls.

### 4. Source edge vs copyable edge

The Framework must evaluate two separate hypotheses:

`Does Edge itself have positive post-cost expectancy?`

and

`Can an independent observer enter after realistic delay and retain positive expectancy?`

Required delay grid:

- first independently observable timestamp;
- +30 seconds;
- +1 minute;
- +5 minutes.

The second question is more relevant to Framework transfer value.

## Highest-value generic takeaway

External trading research should use the permanent taxonomy:

- `SOURCE_ALPHA`
- `OBSERVABLE_ALPHA`
- `COPYABLE_ALPHA`
- `SCALABLE_ALPHA`

These are separate claims and require separate evidence.

A source may be genuinely skilled while being useless to copy because the opportunity reprices before a follower can enter.

## Edge decomposition

Any claimed Edge performance must be decomposed into:

- selection / prediction quality;
- sizing;
- timing;
- execution;
- compounding;
- parlays / correlated legs where applicable;
- follower modifications;
- fees.

The `$1k -> $85k/$93k` social challenge is not admissible evidence of Oddy's predictive alpha until bet-level reconstruction proves how much return came from source selection versus follower sizing/parlays/compounding.

## Material existing warning

The initial source audit found a material inconsistency between Edge's stated weekly backtest ROI and the arithmetic represented by its longer-horizon vault tables.

Therefore official headline backtest numbers remain:

`DOCUMENTATION_INCONSISTENCY / PERFORMANCE_EVIDENCE_NOT_ADMISSIBLE`

This is useful evidence about why primary action ledgers must dominate project-authored performance summaries.

## Why prediction markets are a valuable research laboratory

Prediction markets provide an unusually clean experimental setting because they can expose:

- explicit entry price / implied probability;
- timestamped execution;
- discrete final settlement;
- public action history;
- clear source-vs-follower timing;
- measurable probability repricing after a signal.

That makes the Edge case useful even if Edge itself fails the alpha test.

A failed Edge case can still validate or improve the Framework's generic external-strategy audit method.

## Potential transferable Framework outputs

If supported by evidence, the case may contribute reusable components such as:

- external-strategy action-ledger schema;
- opportunity-set reconstruction;
- selection-policy inference;
- sizing-policy inference;
- alpha-decay clock;
- source-vs-copy edge adjudication;
- capacity/crowding test;
- revealed-policy clone benchmark.

Promote only individual components that add measurable value. Do not import the Edge stack wholesale.

## Framework classification

- `$EDGE` token thesis: `OUTSIDE PRIMARY AUTO_TRADING RESEARCH VALUE`
- social PnL claims: `DISCOVERY_ONLY`
- project backtest tables: `NOT_ADMISSIBLE UNTIL REPRODUCED`
- public execution ledger: `VERY HIGH RESEARCH VALUE`
- source prediction edge: `UNVERIFIED`
- behavioral reverse engineering: `VERY HIGH PRIORITY`
- copyability / latency-decay study: `VERY HIGH PRIORITY`
- vault economics/security: `SECONDARY BUT REQUIRED BEFORE ANY VAULT INTEREST`
- direct copy trading: `REJECT UNTIL PROSPECTIVE EVIDENCE`

## Required next step

Prioritize the research chain:

`canonical Edge identity -> complete primary action ledger -> contemporaneous opportunity set -> selection/sizing/timing reconstruction -> source-alpha adjudication -> latency-decay copyability test`

Do not spend the next research cycle optimizing vault/token analysis before the revealed-policy question is answered.
