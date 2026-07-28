# Claude OTA source record — standalone run

```yaml
source_type: USER_PROVIDED_CLAUDE_OUTPUT
run_timestamp_utc: 2026-07-28T18:49:39.660Z
operating_mode: STANDALONE_OTA
reference_bridge_present: NO
reference_data_ping_run_id: NOT_PROVIDED
previous_claude_ota_reference: CLAUDE-OTA-2026-07-28T18:44:13.167Z
new_information_count: 2
matured_claude_experiment_count: 0
falsified_hypothesis_count: 0
source_qa_event_count: 2
canonical_authority: NONE
portfolio_authority: NONE
```

## Context-boundary correction

Claude explicitly withdrew prior claims about what DATA PING contains because no DATA PING payload or bridge had been supplied. Framework state was correctly returned as unknown and no canonical effect was claimed.

## Source and experiment observations

- Cache guard labelled the run current and fresh across four venues.
- H7 row 7 had not formed at the source query time. Empty Binance one-hour arrays were classified as `CANDLE_NOT_FORMED`, not as zero or missing market evidence.
- No experiment matured during the 5.5-minute interval.
- Closed F1, F4 and F5 windows were not rescored or retriggered.

## Hypothesis updates

```yaml
H-SRC-01:
  claim: Farside freshness follows edge-node IP
  status: FALSIFIED

H-SRC-02:
  claim: Farside is more likely fresh after approximately 16:00Z
  status: UNPROVEN_PROSPECTIVE
  observations_logged: 2
  minimum: 10
  preferred: 20

H-ETF-01:
  claim: ETH ETF flow intensity exceeds BTC after size normalization
  status: WEAKENED
  reason: prior denominator was cumulative net flow, not AUM

H-WIN-01:
  claim: fixed experiment windows may close immediately before the tested move
  status: UNPROVEN_LOW_CONFIDENCE
  sample_size: 2
```

## Direct ETH/BTC UTC rows supplied by Claude

Source identifier:
`data-api.binance.vision/api/v3/klines?symbol=ETHBTC&interval=1d`

Retrieval:
`2026-07-28T18:49:41.796Z`

Response SHA-256:
`f9e094c127cca325e40380a697b6f165d7970aad4bb684caca9474d34c7202be`

| UTC session | Open | High | Low | Settled close | Touched 0.0300 | Closed above 0.0300 | Authority |
|---|---:|---:|---:|---:|---|---|---|
| 2026-07-24 | 0.02885 | 0.02910 | 0.02870 | 0.02902 | No | No | DIRECT_SETTLED |
| 2026-07-25 | 0.02902 | 0.02915 | 0.02898 | 0.02913 | No | No | DIRECT_SETTLED |
| 2026-07-26 | 0.02912 | 0.03000 | 0.02912 | 0.02989 | Yes | No | DIRECT_SETTLED |
| 2026-07-27 | 0.02990 | 0.03020 | 0.02958 | 0.02967 | Yes | No | DIRECT_SETTLED |
| 2026-07-28 | 0.02968 | 0.03010 | 0.02953 | In progress | Yes | Not assessable | IN_PROGRESS |

Claude classified the two completed UTC sessions as a rejection sequence. Framework relevance was left unassessed because no bridge was supplied.

## Reconciliation items supplied

1. `R-01 DERIVED_FEATURE_DEFECT`: Farside Total values had previously been mislabeled as AUM. Claude withdrew the 4.5x AUM-normalized magnitude.
2. `R-02 ETF_STRUCTURE`: BTC 20-session flow sum reported as -230.9 US$m for 2026-06-29 through 2026-07-27. ETH remained unknown because only 13 sessions were present in the retrieved payload.
3. `R-03 THRESHOLD_SEQUENCE`: two completed UTC sessions touched 0.0300 with zero closes above.
4. `R-04 SOURCE_QA`: a dash denotes not reported, while an all-dash row can still render Total as 0.0.
5. `R-05 SOURCE_QA`: deterministic edge-node freshness hypothesis falsified.
6. `R-06 DESIGN_OBSERVATION`: F1 and F4 post-window boundary stress, no score changes.
7. `R-07 SOURCE_QA`: Claude corrected its own context-boundary overreach.

## Unresolved queue supplied

- true BTC and ETH ETF AUM denominators;
- 2026-07-28 ETF prints;
- CFGI series access;
- F4 venue, basis and close convention;
- F1 threshold attribution;
- W30 start-measurement venue.

All remained quarantined from canonical state changes.