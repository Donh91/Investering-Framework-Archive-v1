# S8 Execution Receipt - 2026-10-06

Status: SOURCE_RECONCILIATION_MERGED / HISTORICAL_EVENT_PANEL_PENDING / RESEARCH_ONLY
Master issue: #1512
Execution issue: Meme Alpha #111
Merged PR: Meme Alpha #112
Merge commit: 77462e3abbbecbf1e82bbb3d8513d0c7aa6b9708

## Fresh source finding

Tokenomist's current Scheduled Unlock Data scope excludes continuous mechanisms such as mining rewards, staking emissions and yield farming from that scheduled-cliff dataset.

DeFiLlama's current Unlocks surface includes both cliff and linear unlock families.

Therefore provider headline "unlock" values are not comparable without release-mechanism and scope reconciliation.

## Implemented

- unlock source observation contract;
- exact chain + contract identity requirement for cross-source agreement;
- canonical UTC event-time normalization;
- canonical Decimal amount normalization;
- release mechanism reconciliation;
- continuous-scope reconciliation;
- allocation reconciliation;
- methodology preservation including INFERRED_FROM_GRAPH;
- time, mechanism/scope, allocation and amount conflict states;
- USD value excluded from event identity;
- provider conflicts are never averaged.

## Reconciliation states

AGREED
SINGLE_SOURCE
AMOUNT_CONFLICT
TIME_CONFLICT
MECHANISM_SCOPE_CONFLICT
ALLOCATION_CONFLICT
DATA_INSUFFICIENT

## Audit learning

Two formatting-only false-conflict risks were removed before merge:
- 100 vs 100.0 now normalize to the same token amount;
- Z vs +00:00 representations of the same UTC instant now normalize to the same event time.

A unit test initially changed amount and allocation simultaneously; it was corrected to isolate one research variable at a time.

## Scientific state

Source reconciliation capability is ready.

No historical matched unlock panel has been created yet.
No unlock-impact edge is claimed.

Next:
1. bind exact token identities;
2. freeze comparable historical unlock events;
3. join realized recipient transfer/selling where reproducible;
4. join liquidity + spot/perp response;
5. compare against simple unlock-% and low-float/FDV baselines.

## Authority

No sell rule.
No alert authority.
No portfolio action.
No auto execution.
