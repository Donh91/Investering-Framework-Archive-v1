# Claude OTA 2026-08-27 - Main Framework ingest review

**Reviewed against current `main`:** `7d14ba0905cfac1a399ebfee3fb122325e613e6e`  
**Source class:** external research input / non-authoritative  
**Canonical state change:** NONE  
**Portfolio authority:** NONE

## Executive disposition

The 2026-08-27 Claude OTA report contains useful descriptive context, but only a subset is admissible under current ratified governance. No market rule, threshold, state or portfolio action is changed by this ingest.

## Accepted as bounded research context

1. **ETH/BTC persistence above 0.0300** - retain as descriptive threshold-persistence context only. The report states eight settled closes above 0.0300 through 2026-08-26 and no settled close below the gate. This does not independently promote a state because canonical breadth/transmission and current framework confirmation remain separately owned.
2. **ETH relative leadership on 2026-08-26** - retain as context consistent with the rotation thesis, subject to canonical owner evidence. Do not use the Claude report itself as the deciding source.
3. **DVOL normalization** - retain as descriptive/backfillable research context only. Under the ratified Pullback Forensics pilot, DVOL remains DEFERRED because it is backfillable and therefore not perishable evidence.
4. **Source-QA statements** - archive as report-level QA metadata only. They do not supersede owner receipts or canonical source QA.

## Rejected as evidential learning

### PFE-001 Lane 3 order-book comparison

The report labels the 2026-08-27 order-book reading versus the 2026-08-21 baseline as the first genuine Lane 3 comparison. That claim is **not admissible as evidential Pullback Forensics learning** under current governance.

Current rules state:

- `PULLBACK_FORENSICS_PASSIVE_PILOT_v1.md`: Lane 3 order-book dynamics are **DEFERRED** because five-times-daily / OTA cadence cannot measure minute-scale depth evaporation, refill or cancellation dynamics.
- `CLAUDE_OTA_EXTENSION_PATCH_v0_2.md`: order-book snapshots are `CONTEXT_SNAPSHOT` / `INSTANTANEOUS` only, and change-versus-prior must not be reported when the prior observation is more than 60 minutes old.

The Claude comparison spans roughly six days. Therefore the reported BTC and ETHBTC depth deltas may be retained only as two unrelated instantaneous context snapshots. They must not be interpreted as accumulation, refill, recovery, market-maker return, directional liquidity improvement, or PFE-001 learning.

## ETF bridge resolution

Claude correctly avoided independent ETF retrieval. The GitHub Farside owner now resolves the report's `AWAITING_BRIDGE` state:

| Session | BTC net flow | ETH net flow | Status |
|---|---:|---:|---|
| 2026-08-26 | +$232.2M | +$192.4M | final, total parity PASS |
| 2026-08-27 | +$242.3M | +$225.8M | final, total parity PASS |

Source: `research/etf_owner/LATEST_FARSIDE_ETF_OWNER.json`, contract `FARSIDE_ETF_OWNER_SNAPSHOT_v4`.

These values replace `AWAITING_BRIDGE` in Claude's context only. They do not grant Claude ETF authority and do not create a new ETF owner.

## Open items

- `H-WIN-01 audit`: remains blocked unless the canonical/reference bridge exposes the required frozen window list.
- `decision-value research`: remains blocked unless historical decision points can be supplied from an authoritative bridge without hindsight contamination.
- PFE Lane 1: no new event in this report; no action.
- PFE Lane 4: no new catalyst; no action.

## Learning disposition

- new canonical rule: **NO**
- new threshold: **NO**
- portfolio action change: **NO**
- experiment promotion: **NO**
- PFE Lane 3 learning row: **NO**
- ETF bridge context resolved: **YES**
- useful threshold/relative-leadership context retained: **YES, bounded/non-authoritative**

The report is therefore useful primarily as a contextual cross-check and as evidence that the governance boundary correctly prevents a tempting but invalid six-day order-book comparison from becoming false learning.
