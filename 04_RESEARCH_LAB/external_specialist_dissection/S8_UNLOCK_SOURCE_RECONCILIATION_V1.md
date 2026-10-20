# S8 - Unlock Source Reconciliation v1

Status: IMPLEMENTATION_READY / RESEARCH_ONLY / EXTEND_EXISTING_PACKAGE
Parent package: Donh91/Meme-Alpha-Lab/research/packages/UNLOCK_SUPPLY_OVERHANG_V1.md
Master issue: #1512

## Fresh source-semantic finding - 2026-10-06

The first implementation problem is source scope, not prediction.

Tokenomist's current public Scheduled Unlock Data surface describes timestamped cliff unlocks with allocation breakdown and explicitly states that continuous mechanisms such as mining rewards, staking emissions and yield farming are excluded from that scheduled-unlock dataset.

DeFiLlama's current Unlocks surface reports both Cliff Unlocks and Linear Unlocks in aggregate and individual project schedules may include cliff, weekly/linear or other release mechanisms.

Therefore provider unlock value is not a canonical comparable unlock value unless release mechanism and scope are frozen.

## Required canonical event dimensions

- exact token identity;
- event timestamp;
- release mechanism: CLIFF | LINEAR | WEEKLY_RATE | STAKING_REWARD | MINING_EMISSION | ECOSYSTEM_EMISSION | UNKNOWN;
- token amount;
- % circulating float at cutoff when reproducible;
- allocation/recipient category;
- source;
- source observation UTC;
- source methodology state: DIRECT_SCHEDULE | ONCHAIN_EVENT | INFERRED_FROM_GRAPH | PROVIDER_DERIVED | UNKNOWN;
- continuous mechanisms included/excluded;
- source evidence ref/hash.

USD value is a time-varying derivative and must not define event identity.

## Reconciliation states

- AGREED
- SINGLE_SOURCE
- AMOUNT_CONFLICT
- TIME_CONFLICT
- MECHANISM_SCOPE_CONFLICT
- ALLOCATION_CONFLICT
- DATA_INSUFFICIENT

Do not average conflicting providers.

## Real public semantic fixture

DeFiLlama Portal (W) page observed 2026-10-06:
- next cliff event: 2026-10-16 00:00 UTC;
- categories shown: Guardian Nodes, Ecosystem & Incubation, Core Contributors, Strategic Network Participants;
- page notes that schedule data has been inferred from source-material graph.

The fixture is useful for testing exact event-time freeze, allocation aggregation, explicit INFERRED_FROM_GRAPH methodology, and separation of token amount from changing USD value.

It is not evidence of bearish impact.

## Next after reconciliation

Only after events are comparable:
schedule x recipient identity x cost basis x realized transfer/selling x executable liquidity x spot/perp response.

That is the existing UNLOCK_SUPPLY_OVERHANG_V1 hypothesis.

## Authority

No sell rule.
No portfolio action.
No alert authority.
