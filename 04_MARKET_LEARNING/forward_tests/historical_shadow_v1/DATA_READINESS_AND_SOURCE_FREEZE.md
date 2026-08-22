# Data Readiness and Source Freeze

Status: `NOT_READY_FOR_ELIGIBLE_ROWS`
Authority: `RESEARCH_ONLY_NON_CANONICAL`
Last source audit: `2026-08-22`

## Purpose

The Stage 2 review showed that historical failure came primarily from missing contemporaneous sensor-state provenance. This file prevents the prospective program from repeating that defect.

No prospective row may be marked eligible until every required field has an explicit owner, source identity, calculation rule and timestamp cutoff.

## PT-HS-001 readiness

| Field | Required | Current readiness | Repository evidence | Freeze requirement |
|---|---|---|---|---|
| Stablecoin Alt Inflow 3D | YES | `SOURCE_OWNER_NOT_FOUND_BLOCKED` | Repository code/content search found no owner-grade `stablecoin_alt_inflow` or equivalent frozen 3D alt-inflow surface | A new explicit owner/source contract is required. Freeze universe, flow definition, 3D window, timestamp convention and source version before capture. No proxy substitution. |
| Large-cap Alt Volume Share 3D | YES | `SOURCE_OWNER_NOT_FOUND_BLOCKED` | Repository code/content search found no owner-grade large-cap-alt volume-share surface | A new explicit owner/source contract is required. Freeze large-cap universe, denominator, volume source, 3D calculation and cutoff before capture. No reconstruction from later outcomes. |
| ETH/BTC | YES | `OWNER_EVIDENCE_FOUND_BINDING_PENDING` | DATA PING machine summaries retain direct `ETHBTC_direct` with `snapshot_utc`; example `04_MARKET_LEARNING/data_ping/2026-07-27__run_18debd32__machine-summary.json` records Binance direct ETH/BTC | Bind the exact direct-pair source/provider, observation-versus-settlement convention, stale/missing rule and source version in the future machine-readable source-freeze receipt. |
| BTC dominance | YES | `SOURCE_IDENTITY_NOT_VERIFIED_BLOCKED` | No exact current owner/provider/denominator identity was established in this audit | Locate or create a point-in-time owner contract before activation. Historical/later source conflicts make implicit reuse forbidden. |
| Breadth context | CONTROL | `OWNER_EVIDENCE_FOUND_SEMANTICS_PENDING` | `04_MARKET_LEARNING/breadth/forward/2026-07-11__breadth-snapshot-forward-001-compact.csv` provides timestamped asset membership, exclusions and returns | Bind membership universe/version and a deterministic breadth-state transform before first eligible row. Existing snapshot proves a data surface, not the recovered `WEAK/PARTIAL/STRONG` semantics by itself. |
| Current-stack context | CONTROL | `AVAILABLE_REQUIRES_TIMESTAMP_BINDING` | Timestamped DATA PING machine summaries/framework reads exist | Bind exact contemporaneous artifact identity. Never use a later settled/revised artifact as the earlier observation state. |

PT-HS-001 remains blocked. It may not start eligible sample accumulation while either distinctive input lacks an owner-grade source, or while BTC dominance source identity is unresolved.

## PT-HS-002 readiness

PT-HS-002 inherits every PT-HS-001 blocker and additionally requires:

| Field | Required | Current readiness | Freeze requirement |
|---|---|---|---|
| Brief ETH/BTC improvement | YES | `SEMANTIC_FREEZE_REQUIRED` | Define the exact observation/change window before first case. The existing DATA PING 1h/4h/12h/24h/48h returns may be candidate primitives only, not a post-outcome choice. |
| High BTC.D | YES | `BLOCKED_BY_BTC_D_SOURCE_AND_SEMANTIC_FREEZE` | First resolve source identity, then freeze the recovered pattern meaning without outcome tuning. |
| Weak breadth | YES | `SEMANTIC_FREEZE_REQUIRED` | Freeze breadth state rule and membership universe from prospective owner-grade data. |
| Failure/confirmation label | YES | `LABEL_FREEZE_REQUIRED` | Define prospectively before first eligible Type 3 case. |

## Source audit conclusion

The repository now has credible prospective primitives for direct ETH/BTC and point-in-time breadth context, but it does **not** currently expose enough owner-grade evidence to activate the recovered legacy composite unchanged.

The scientific blockers are substantive, not administrative:

1. `Stablecoin Alt Inflow 3D` has no verified owner-grade source.
2. `Large-cap Alt Volume Share 3D` has no verified owner-grade source.
3. Exact BTC dominance source/provider/denominator identity remains unresolved.
4. Type 3 qualitative terms still require preregistered semantics.

Therefore the correct state is `NOT_READY_FOR_ELIGIBLE_ROWS`, not a synthetic source freeze.

## Universal no-lookahead rules

- Source timestamps must be at or before `information_cutoff_utc`.
- Missing data stays missing.
- No interpolation or proxy substitution unless that exact method is preregistered before the first eligible row.
- Later source revisions must create a new source-version boundary, not silently rewrite old rows.
- Outcome data must be joined only after the observation row is immutable.
- The eight maturation horizons are fixed and all remain reportable.

## Activation gate

Change registry status from `PREREGISTERED_DATA_READINESS_PENDING` to `ACTIVE_PROSPECTIVE_CAPTURE` only after a machine-readable source-freeze receipt exists containing:

1. source/provider identity for every required field,
2. exact calculation formula/window,
3. timestamp and settlement convention,
4. missing/stale-data policy,
5. source-version identifiers,
6. deterministic test fixture proving no lookahead,
7. first eligible observation time strictly after the freeze commit.

Until then, zero eligible rows is the correct scientific result.
