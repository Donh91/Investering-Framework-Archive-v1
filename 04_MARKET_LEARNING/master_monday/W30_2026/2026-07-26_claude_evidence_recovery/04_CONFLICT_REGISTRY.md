# W30 Evidence Recovery — Conflict Registry

**Status:** `OPEN / NON_CANONICAL`  
**Rule:** No conflict is silently resolved during archive ingest.

## C-01 — F1 threshold lineage

- `62,200` is the frozen truth-layer threshold in the July 14 case card.
- `62,342` is a later refinement with unresolved provenance.
- Binance UTC 2026-07-13 close `62,334.52` is the nearest identified numeric match, but numeric proximity does not prove lineage.
- Archive handling: preserve both; frozen `62,200` retains test authority unless governance explicitly changes it.

## C-02 — Fed chair source conflict

- The package reports several sources naming Kevin Warsh.
- One older calendar source names Powell.
- Archive handling: preserve the conflict; no role-holder adjudication is performed by this ingest.

## C-03 — BTC dominance basis

- CoinGecko total-market basis is approximately `56.5%`.
- Ex-stablecoin calculations can yield approximately `58–59%`.
- Archive handling: method-tag both; never compare or merge without basis normalization.

## C-04 — UTC versus CEST close basis

- Dual-basis closes differ because of session convention.
- Archive handling: preserve both; each forecast must use its preregistered basis.

## C-05 — Derivatives venue continuity

- OKX was used because Binance Futures returned HTTP 451 and Bybit HTTP 403.
- OKX OI, funding, basis and ratios are not interchangeable with Binance series.
- Archive handling: `VENUE_TAG_REQUIRED / LONGITUDINAL_COMPARABILITY_PARTIAL`.

## C-06 — Bitstamp ETH/BTC trade versus midpoint

- Last trade lagged the live midpoint.
- Midpoint was used in venue convergence.
- Archive handling: preserve both where available.

## C-07 — Publication lag

- VIX and yield series were only available through 2026-07-23.
- Archive handling: `EXPECTED_PUBLICATION_LAG`, not automatic stale-source failure.

## C-08 — Provisional versus settled Farside values

- No current conflict was found for the settled 2026-07-24 rows.
- Archive handling: settled primary-table rows outrank provisional media totals.

## C-09 — Low-vol arithmetic conflict

The package contains two incompatible result sets:

- Main report sections 1 and 6 and the embedded final JSON: `1D -1.54%`, `3D -2.63%`.
- Forecast maturity CSV, CN/RAW bridge and report footer: `1D +0.10%`, `3D -0.26%`.

Status: `UNRESOLVED_INTERNAL_ARITHMETIC_CONFLICT`.

Required action: recompute directly from the frozen anchor and settled close rows before Master Monday adjudication. Neither set is promoted to canonical truth.

## C-10 — Stage-1 persistence count conflict

- Main report narrative: `3` consecutive settled UTC closes below `65,600`, beginning 2026-07-23.
- Forecast maturity CSV and handoff summary: `4` consecutive closes, beginning 2026-07-22.

Status: `UNRESOLVED_SESSION_BASIS_OR_COUNT_CONFLICT`.

Stage-1 remains `GOVERNANCE_PENDING`.

## C-11 — Stablecoin depeg summary conflict

- Executive summary says no top-15 depeg above 1%.
- Detailed stablecoin section lists USYC and USDY deviations above 1%.

Status: `UNRESOLVED_DEPEG_FILTER_OR_LABEL_CONFLICT`.

Required action: recompute from the preserved raw stablecoin payload using an explicit price-deviation definition and eligibility universe.

## C-12 — ETF leader and concentration formatting

The BTC ETF section contains malformed or incomplete output for leader and concentration. Session totals remain usable because they match Farside and DATA PING, but leader/concentration fields are blocked until recomputed.

## Governance effect

These conflicts do not alter canonical state, portfolio state, rebuy state or entry permissions. They are retained to prevent accidental certainty and hindsight repair.