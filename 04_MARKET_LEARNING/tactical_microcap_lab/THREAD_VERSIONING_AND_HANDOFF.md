# Meme Thread Versioning and Handoff

## User-facing thread names

Use simple thread lineage:

```text
MEMES v1
MEMES v2
MEMES v3
...
```

`Meme - besyv?`, `Microcap - besyv?`, `YOLO - besyv?` and `Casino - besyv?` remain valid intake shorthand inside any version.

The chat version is not the research version. GitHub is the continuity layer.

## Why version threads

Fast token-audit threads can become long and noisy. A new `MEMES vN` thread should preserve accumulated research without carrying stale live-market assumptions forward.

## New-thread rule

At the beginning of a new meme-audit thread:

- current token prices, liquidity, holder counts and wallet balances must be fetched fresh before an entry recommendation;
- historical cases, wallet records and prior hypotheses may be read from GitHub as historical evidence;
- prior chat conclusions are not current-market evidence merely because they were correct before;
- contract addresses, chain IDs and pair IDs must be re-confirmed for each new active case;
- unresolved wallet/cluster hypotheses remain hypotheses until fresh evidence supports them.

This differs from a stateless Data Ping packet: Meme Alpha Lab intentionally keeps historical research continuity, while live trade evidence must be refreshed.

## Handoff manifest

A thread rollover should be able to reconstruct the useful state from a short manifest containing:

```text
thread_name
created_utc
lab_contract_path
open_cases
recent_closed_cases
wallet_candidates_under_forward_watch
active_cluster_hypotheses
source_aliases_with_material_evidence
current_research_hypotheses
known_data_gaps
```

Do not copy raw private Telegram content into the public manifest.

## Case identity

Every material case should be address-first:

```text
chain
contract_address
pair_address if relevant
launch timestamp if known
```

Ticker-only continuity is forbidden because meme tickers are frequently duplicated.

## Thread handoff goal

A new thread should need minutes, not hours, to regain research context while still being forced to refresh anything that can change rapidly.

The desired split is:

```text
PERSIST:
  wallet history
  prior case evidence
  source reliability observations
  research hypotheses
  outcome records
  contract / launch historical facts

REFRESH:
  price
  market cap
  liquidity
  volume
  holder count
  current balances
  current buy/sell flow
  current social / catalyst state
  current wallet movement
```

## Version-change trigger

Create the next chat version when the current thread becomes operationally cumbersome or when the user intentionally starts a new audit thread. No research reset is implied.

## Naming recommendation

Use `MEMES v1`, `MEMES v2`, etc. in ChatGPT because it is short and obvious.

Use `Meme Alpha Lab` in GitHub because it describes the persistent research function rather than a single chat session.
