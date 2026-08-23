# Round 3 New Information Research v1

Status: `CONTRACT_FROZEN_V2_MATERIALIZED_PRIVATE_COLLECTION_HOLD_TERMS_AND_PROVENANCE`
Authority: `RESEARCH_ONLY_NON_CANONICAL`

This programme follows the terminal Round 1 and Round 2 historical-altseason work. The broad historical price/volume/taker-share mining lane remains closed. Round 3 is restricted to genuinely new information dimensions and remains `PROSPECTIVE_COLLECTION_ONLY`.

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

The canonical framework repository is the public control plane. `Donh91/secrets` is the restricted data plane. GitHub Actions Secrets or an explicitly approved runtime secret manager/workload identity is the credential plane.

Provider-derived raw/normalized Round 3 market values MUST NOT be committed to this public repository. Public files may hold contracts, code, schemas, hashes, row/object counts, timestamp/completeness health, provider-value-free provenance receipts and gated research decisions. Every private dataset reference requires a private commit SHA, exact path, bytes, SHA-256, source-contract ID, timestamps, schema and completeness.

Current source state is fail-closed. SC01, SC03 and SC14 are on terms-attestation and provenance-v2 hold. SC06 is on the same terms hold and still requires a persistent continuous-stream runtime. No private source is currently collection-active.

The historical private canary workflow run `32633097190` passed, but that remains collection/source-health evidence only. The current private health readback records 11 raw captures: all 11 are integrity-valid, none are invalid or orphaned, and all 11 are analysis-ineligible legacy captures because they lack the frozen schema-v2 collector provenance. They were preserved without rewrite or deletion. There are zero schema-v2 captures and no analysis authorization.

See `COLLECTION_STATUS.json`, `PRIVATE_DATA_PLANE_BINDING_RECEIPT.json`, the historical `PRIVATE_COLLECTION_ACTIVATION_RECEIPT.json`, the current `PRIVATE_COLLECTION_HOLD_RECEIPT_2026-08-23.json`, `PROVIDER_TERMS_EVIDENCE_REQUIREMENTS_v1.json` and `00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md`.

## Required gates before analysis

- V2 catalogue and controls deterministically materialized before any Round-3 source values are linked.
- Source contracts pass timestamp, units, completeness, mapping and missingness gates.
- At least 80% complete-pair coverage.
- At least 30 complete pairs in each of two predeclared chronological prospective blocks.
- At least 80% simulated family-wise power at paired concordance 0.67.
- No outcome-linked analysis before all above gates are true.
- Provider terms applicability and intended-use evidence must be complete, then collection must be reactivated in a separate reviewed pull request.
- The first post-reactivation capture must use schema v2 and pass health-only validation before any linkage to outcomes.
- Hypothesis testing and outcome scoring remain `OFF` until the gate is formally opened by a new governed receipt.

See the machine-readable contracts in this directory. Any change to a frozen hypothesis, feature, direction, actionable window, policy threshold, control design or multiplicity family requires a new version and fresh prospective evidence.
