# Wallet Alpha Research Protocol

**Purpose:** distinguish repeatable wallet skill / privileged access / coordination from hindsight, luck and selection bias.

This protocol exists because the most valuable evidence in fast meme markets may be the behavior of wallets that repeatedly enter early, size intelligently and exit before distribution is obvious.

It must not assume that an early profitable wallet is automatically an insider.

## Core question

For a wallet or cluster that appears in a successful meme trade, ask:

> Did this wallet demonstrate a repeatable edge before the outcome was obvious, or are we only noticing it because this particular token won?

## Discovery direction

Wallet research should work both directions.

### Token -> wallet

Start from a successful or suspicious token and identify:

- earliest meaningful buyers;
- best realized exits;
- wallets that bought before public distribution accelerated;
- wallets that avoided the final collapse;
- wallets with privileged launch mechanics;
- wallets that repeatedly traded together.

### Wallet -> token

Then leave the original winner and inspect the wallet's broader history:

- prior early buys that failed;
- prior early buys that succeeded;
- tokens exited badly;
- tokens never exited;
- frequency of buying new launches;
- average quality of selection;
- recurring counterparties / clusters;
- creator or deployer links;
- whether profitable behavior exists across independent events.

A wallet that bought 200 launches and happened to catch one 100x is different from a wallet that selectively entered ten launches and repeatedly exited several before collapse.

## Minimum evidence dimensions

### A. Entry quality

Observe, where derivable:

```text
seconds/minutes from launch
block distance from launch
market cap at entry
liquidity at entry
price percentile within early path
whether entry preceded public call / announcement
whether entry was bundled / privileged / tax-exempt
```

### B. Selection quality

Do not measure winners only.

Estimate:

```text
number of independent token entries
number of duds / rugs / dead launches
number of material winners
median and distribution of outcomes
capital concentration by outcome
```

A high hit rate with tiny wins and one catastrophic loss is not automatically skill.

### C. Exit quality

Inspect:

```text
first de-risk timing
partial exit sequence
final exit timing
market cap / liquidity at exit
exit relative to local / global peak
remaining bag after collapse
realized PnL where observable
```

Useful descriptive concepts include `exit efficiency` and `profit capture`, but no numeric promotion threshold should be invented before calibration.

### D. Risk behavior

Check whether the wallet:

- sizes larger only in stronger setups;
- repeatedly holds losers to zero;
- cuts weak launches quickly;
- adds into distribution;
- sells into strength;
- rotates capital immediately into related launches;
- repeatedly becomes a top holder in thin pools where exit is unrealistic.

### E. Relationship evidence

Trace bounded, decision-relevant relationships:

- direct transfers to/from deployer or creator;
- shared upstream funder;
- unusual same-block or same-transaction behavior;
- launch exemptions;
- bundled transactions;
- repeat co-entry / co-exit clusters;
- shared fresh-wallet creation / funding timing;
- recurrent use of the same unusual router or counterparty;
- public attribution.

Common infrastructure alone is weak evidence. Shared exchange withdrawals, common routers, bridges and MEV infrastructure can create false links.

## Skill vs luck adjudication

Never classify from one winner.

Use the following evidence states:

```text
UNASSESSED
INSUFFICIENT_SAMPLE
LUCK_COMPATIBLE
MIXED_EVIDENCE
REPEATABLE_EDGE_CANDIDATE
REPEATABLE_EDGE_SUPPORTED
EDGE_DECAYED
```

These are research states, not trading permissions.

Evidence favoring repeatable edge includes:

- repeated profitable selection across independent launches;
- consistently earlier-than-public entries without buying everything;
- repeated disciplined exits before collapse;
- positive outcomes after accounting for obvious failed entries;
- performance across more than one market micro-regime;
- recurring success not explainable by one giant outlier;
- forward observations after the wallet was added to the registry.

Evidence favoring luck includes:

- one spectacular hit among many dead launches;
- performance dominated by one outlier;
- high apparent PnL caused by unexitable illiquidity;
- wallet only discovered after the winning outcome;
- no forward success after discovery;
- frequent top buying / bag holding;
- suspiciously incomplete history.

## Connected / early-access inference

Keep performance skill separate from relationship inference.

A skilled public trader can have no privileged access. A connected wallet can also trade badly.

Store both axes independently:

```text
wallet_edge_state
relationship_evidence_state
```

Relationship evidence states:

```text
UNKNOWN
NO_MATERIAL_LINK_FOUND
WEAK_ASSOCIATION
EARLY_ACCESS_PATTERN
REPEATED_CLUSTER_EVIDENCE
STRONGLY_LINKED
DIRECTLY_LINKED
PUBLICLY_ATTRIBUTED
```

Do not collapse these into one score.

## Cluster analysis

When several wallets repeatedly appear together, build a cluster hypothesis.

Useful evidence:

- common funder;
- funding within a narrow time window;
- same launch set;
- same entry block sequence;
- repeated transfers between members;
- synchronized exits;
- shared privileged launch configuration;
- repeated distribution to the same downstream wallets.

Counterevidence:

- common CEX withdrawal hot wallet;
- common router/aggregator;
- public trading bot used by many unrelated traders;
- large popular launches where many wallets naturally co-occur;
- copy-trading after a public signal.

Clusters must preserve uncertainty.

## Survivor-bias control

A detective process that starts only from successful tokens will overestimate wallet skill.

Therefore every candidate wallet must be checked against a broader sample of its other meme/new-token trades.

Where feasible, compare against at least one mechanical baseline such as:

- all identifiable new-token buys by that wallet in the same period;
- random early buyers from the same launch cohort;
- wallets with similar activity frequency / capital size;
- token-level outcome distribution for the same launch venue.

Baselines are descriptive until enough evidence exists to validate them.

## Forward validation

The highest-quality evidence is created after discovery.

When a wallet becomes `REPEATABLE_EDGE_CANDIDATE`, freeze the reason and timestamp. Future trades then test whether the apparent edge survives without hindsight selection.

Do not silently add only the future winners to the record.

## Public analytics sources

Possible sources include:

- native chain explorers / APIs;
- Blockscout / Etherscan-like explorers;
- Dexscreener and launchpad data;
- public Dune dashboards where provenance is adequate;
- free/public Nansen surfaces where accessible;
- other public wallet profilers / label sources;
- direct RPC/log evidence when available.

Nansen labels are useful external evidence, not ground truth. Record the label, source, chain and observation timestamp. Coverage and free-tier availability vary, so absence of a Nansen label is not evidence that a wallet lacks skill or relationships.

No paid Nansen dependency is required by this lab.

## Decision relevance

Wallet evidence can change a token recommendation when it materially changes one of these questions:

```text
Are privileged wallets still holding or distributing?
Is a historically strong wallet entering now or already exiting?
Is the apparent organic demand actually one coordinated cluster?
Does the wallet history support the Telegram claim?
Is the token being accumulated before wider distribution?
Are likely future sellers concentrated and identifiable?
```

Wallet prestige alone is never sufficient for BUY.

## Research outputs

For each material wallet or cluster, preserve:

- address / chain;
- discovery case;
- discovery timestamp;
- evidence sources and observation times;
- edge state;
- relationship state;
- relevant historical trades including failures;
- cluster membership hypotheses;
- forward observations;
- last review timestamp;
- explicit uncertainty / missing evidence.

Use `schemas/WALLET_ALPHA_RECORD_V1.json` as the minimum machine-readable shape.
