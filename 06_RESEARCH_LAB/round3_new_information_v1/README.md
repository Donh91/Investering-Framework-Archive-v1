# Round 3 New Information Research v1

Status: `CONTRACT_FROZEN_PENDING_MERGE`
Authority: `RESEARCH_ONLY_NON_CANONICAL`

This programme follows the terminal Round 1 and Round 2 historical-altseason work. The broad historical price/volume/taker-share mining lane remains closed. Round 3 is restricted to genuinely new information dimensions and is initially `PROSPECTIVE_COLLECTION_ONLY`.

## Frozen programme boundary

- Round 1 and Round 2 remain closed evidence and are never relabelled or rescored by Round 3.
- V2 is ratified only for new Round 3 research: preserve the legacy 5% drawdown trigger, close at 0.75 recovery OR 336 hours after trigger, whichever occurs first.
- The only confirmatory actionable window is `T-24h..T-1h`.
- One V2 event-control pair is one inferential observation.
- Four primary hypotheses form one global family at family-wise alpha 0.05.
- Confirmatory inference uses synchronized, era/block-preserving max-T permutation.
- Continuous feature evidence is Stage 1. Frozen policy thresholds are Stage 2 only and cannot cause Stage-1 rejection or be retuned.
- HOLD is the mandatory Stage-2 economic benchmark.
- No interpolation, forward fill, proxy replacement, venue substitution, source-driven control selection or post-unblinding feature/window/direction changes.
- Historical findings still have a maximum classification of `FORWARD_TEST` after separate review.

## Primary hypotheses

1. `R3-H01-ETH-OI-EXPANSION` — OKX ETH-USDT-SWAP open-interest expansion.
2. `R3-H02-ETH-FUNDING-BURDEN` — OKX ETH-USDT-SWAP realized funding burden.
3. `R3-H03-ETH-BID-DEPTH-WITHDRAWAL` — Binance Spot ETHUSDT contiguous-book bid-depth withdrawal.
4. `R3-H04-ETH-25D-PUT-SKEW` — Deribit ETH true 25-delta put-call IV skew.

## Collection boundary

The canonical framework repository is public. Provider-derived raw/normalized Round-3 market values MUST NOT be committed to this public repository. This repository may hold only contracts, code, schemas, hashes, row counts, timestamp/completeness health, provenance receipts that do not reveal provider values, and later research decisions.

Collection activation therefore requires a separately identified PRIVATE storage zone whose provider terms and retention rights have been reviewed. Until that exists, collection state is `BLOCKED_PRIVATE_STORAGE_REQUIRED` and no scheduled Round-3 provider calls are authorized by this contract.

## Required gates before analysis

- V2 catalogue and controls deterministically materialized before any Round-3 source values are linked.
- Source contracts pass timestamp, units, completeness, mapping and missingness gates.
- At least 80% complete-pair coverage.
- At least 30 complete pairs in each of two predeclared chronological prospective blocks.
- At least 80% simulated family-wise power at paired concordance 0.67.
- No outcome-linked analysis before all above gates are true.

See the machine-readable contracts in this directory. Any change to a frozen hypothesis, feature, direction, actionable window, policy threshold, control design or multiplicity family requires a new version and fresh prospective evidence.