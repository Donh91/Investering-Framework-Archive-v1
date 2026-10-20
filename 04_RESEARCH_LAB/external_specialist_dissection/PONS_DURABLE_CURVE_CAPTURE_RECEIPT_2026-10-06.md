# Pons Durable Prospective Curve Capture Receipt - 2026-10-06

Status: MERGED / FIRST_RUNTIME_FORWARD_BOUNDARY_PENDING / RESEARCH_ONLY
Parent specialist master: #1512
Alpha execution issue: #116
Merged PR: Donh91/Meme-Alpha-Lab#117
Merge commit: ed782d9fb94bd557d426d6de0e0ca7dee91414d3

## Purpose

Turn the previously live-proven Pons v2 CurveBuy/CurveSell decoder into durable prospective evidence for S4 Early Buyer Retention and S9 Launch Execution Quality.

## Architecture

The implementation reuses the existing Meme Alpha Prospective Census v4 hourly workflow at minute :17.

No new scheduler or parallel scanner was created.

Forward-only sample policy:
- first runtime state establishes activation_utc;
- launches observed before activation cannot receive prospective case credit;
- at most 1 new case per run;
- at most 8 active cases;
- max case freeze latency 90 minutes from machine launch observation;
- fixed 24h capture horizon;
- max 5000 blocks per case per run;
- exact block timestamp required before event persistence;
- timestamp-budget exhaustion leaves the unprocessed range pending.

## Data semantics

Persisted event identity:
transaction_hash + log_index.

Ordering:
block_number -> transaction_index -> log_index -> transaction_hash.

Pons semantics remain separated:
- CurveBuy initiator = buyer/msg.sender;
- CurveBuy cohort wallet = token recipient;
- CurveSell flow wallet = seller/msg.sender.

## Automatic research freezes

S9:
- immutable fixed first-5m execution-structure freeze;
- same-tx/same-block/originator evidence can be derived;
- no same-block -> bundle, same-tx -> private bundle, or early-entry -> insider inference.

S4:
- immutable first-10 unique CurveBuy token-recipient cohort;
- later curve-flow evidence can mature retention/first-sale outcomes against the frozen cohort.

Pre-case-freeze chain events may be used as descriptive feature evidence after deterministic prospective case selection, but they receive no launch-time action credit.

## Gates before merge

PASS:
- Meme Alpha Durable Pons Curve Capture v1
- Meme Alpha Research Genome v1 Gate
- Meme Alpha Historical Pair Series v1 Gate
- Meme Alpha v4 Prospective Evidence Gate

The first Genome run exposed a pre-existing lifecycle inconsistency for HISTORICAL_CLUSTER_RAW_MEMBERSHIP_V1. That gap was correctly reopened as engineering_open=true rather than bypassing the regression test; rerun passed.

## Remaining gaps

Still open:
- post-graduation Uniswap v4 flow join;
- direct ERC20 transfer inventory reconciliation;
- graduation-progress time series;
- generic outcome maturation across lanes.

## Runtime state

Code is merged and the existing :17 census now owns execution.
The first normal post-merge census run creates the immutable forward activation boundary. No pre-activation launch is eligible.

Current edge state:
FORWARD_DATA_CAPTURE_READY / EDGE_NOT_YET_PROVEN.

## Authority

No alerts.
No real trade execution.
No signing.
No portfolio action.
