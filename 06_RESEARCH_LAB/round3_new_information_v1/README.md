# Round 3 New Information Research v1

Status: `CONTRACT_FROZEN_V2_MATERIALIZED_PRIVATE_PROSPECTIVE_COLLECTION_ACTIVE_ANALYSIS_OFF`
Authority: `RESEARCH_ONLY_NON_CANONICAL`

This programme follows the terminal Round 1 and Round 2 historical-altseason work. The broad historical price/volume/taker-share mining lane remains closed. Round 3 is restricted to genuinely new information dimensions and remains `PROSPECTIVE_COLLECTION_ONLY`.

## Runtime authority

`PRIVATE_RUNTIME_STATE.json` is the provider-value-free public runtime readback for the restricted data plane. `COLLECTION_STATUS.json` is now explicitly retained as the frozen pre-reactivation snapshot because the Round 3 contract-freeze gate binds it historically. Do not infer live private collection state from that frozen file.

`CROSS_REPO_FRESHNESS_POLICY_v1.json` defines the freshness semantics. Public runtime state is always an explicit point-in-time readback, never a claim that the public repository has a live view of private `main`. Append-only private capture commits may advance after a health snapshot without invalidating the bound governance state, but any private governance-state change requires a new public reconciliation. A stale governance binding is classified `PUBLIC_CONTROL_PLANE_STALE` and must not be silently treated as current.

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

The reconciled private governance state activates SC01, SC03 and SC14 for prospective collection-only. SC06 remains blocked on persistent continuous-stream runtime, private object storage and paid-infrastructure authorization. Hypothesis testing, outcome scoring and restricted analysis remain `OFF`.

The current public readback is bound to private owner-attestation merge `b9f28b42e1c71168c3b991868e1fe823bb481e39`, reviewed reactivation merge `65b56778fec8916603675cf18529d6f957432550`, governance-authority commit `6f5a3e5514c3d1ca88b6b5329d76420a45cffe58`, and a point-in-time private health snapshot at commit `cbe6119d7523c0fc45b660f166eef1bf53db5c73`.

That health snapshot contains 15 raw captures, all 15 integrity-valid, zero invalid/orphan files, zero duplicate payload captures, 11 preserved legacy schema-v1 captures in provenance quarantine and 4 post-floor schema-v2 captures with complete provenance. Analysis authorization remains false. These counts are collection-health evidence only, not signal-performance evidence.

## Required gates before analysis

- V2 catalogue and controls deterministically materialized before any Round-3 source values are linked.
- Source contracts pass timestamp, units, completeness, mapping and missingness gates.
- At least 80% complete-pair coverage.
- At least 30 complete pairs in each of two predeclared chronological prospective blocks.
- At least 80% simulated family-wise power at paired concordance 0.67.
- No outcome-linked analysis before all above gates are true.
- Private prospective collection remains limited to separately reviewed and activated sources.
- Collection-health readbacks may update without opening analysis.
- Hypothesis testing and outcome scoring remain `OFF` until the gate is formally opened by a new governed receipt.
- Any private governance change must be reconciled to `PRIVATE_RUNTIME_STATE.json` before the public control plane may describe the new state.

See `PRIVATE_RUNTIME_STATE.json`, `CROSS_REPO_FRESHNESS_POLICY_v1.json`, the frozen `COLLECTION_STATUS.json`, `PRIVATE_DATA_PLANE_BINDING_RECEIPT.json`, historical activation/hold receipts, `PROVIDER_TERMS_EVIDENCE_REQUIREMENTS_v1.json` and `00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md`.

Any change to a frozen hypothesis, feature, direction, actionable window, policy threshold, control design or multiplicity family requires a new version and fresh prospective evidence.
