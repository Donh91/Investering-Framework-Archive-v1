# DATA PING versus Claude OTA coverage map v1

| Domain | DATA PING owner | Claude OTA role | Long-term artifact |
|---|---|---|---|
| Current spot, book, mark, index | Yes | Do not duplicate except for threshold or conflict | DATA PING ledger |
| Funding, OI, taker ratios | Yes | Cross-sensor interpretation and contradiction analysis | Derived interpretation ledger |
| Current breadth | Yes | Conditional breadth, sequence and regime comparison | Breadth event ledger |
| Latest settled ETF row | Yes | Multi-window, AUM-normalized, issuer composition, revision tracking | ETF structural ledger |
| FRED current observations | Yes | Release semantics, revisions, historical context and event confounds | Macro catalyst ledger |
| Stablecoin and TVL current data | Partial | Source methodology, outage diagnosis and structural interpretation | Source-QA ledger |
| Direct ETH/BTC current value | Yes | Row-level rejection/acceptance sequence and cross-source adjudication | Rotation sequence ledger |
| Experiment calendar | No | Primary role | Experiment maturity ledger |
| No-retrigger and overlap clusters | Partial framework layer | Independent audit | Event lineage ledger |
| Hypothesis lifecycle | No | Primary role | Hypothesis and falsification ledger |
| Source publication schedule | No | Primary role | Source timing study |
| Stale-cache causal analysis | No | Primary role | Source-QA learning ledger |
| News, regulation and protocol catalysts | No | Primary role using primary sources | Catalyst map |
| Post-window near misses | No | Primary role without rescoring | Design-observation ledger |
| Unresolved provenance queue | Partial | Primary maintenance and research | Provenance queue |
| Framework challenge | No | Mandatory adversarial section | Challenge ledger |
| Canonical state and portfolio action | Main framework only | Forbidden | Governance ledger |

## Highest-value Claude-only priorities

### Tier 1: Mandatory every relevant OTA run

1. Experiment maturation and no-retrigger audit.
2. Hypothesis update or explicit `NO_HYPOTHESIS_CHANGE`.
3. Source-QA learning and self-falsification.
4. Multi-session and normalized ETF flow package.
5. Direct ETH/BTC settled rejection/acceptance sequence.
6. Strongest framework challenge.
7. Next three exact events.

### Tier 2: Triggered when relevant

1. Primary-source catalyst research.
2. Cross-source conflict adjudication.
3. Post-window boundary stress.
4. Source revision and backfill detection.
5. Flow-price lag and divergence.
6. Spot-led versus leverage-led move classification.

### Tier 3: Periodic longitudinal research

1. Source publication timing studies.
2. ETF AUM-denominator maintenance.
3. Hypothesis calibration and retirement review.
4. Experiment false-positive and false-negative review.
5. Threshold and window specification challenge.
6. Narrative-to-price lag database.

## Duplication rule

Claude should not spend tokens reproducing fields already present in DATA PING. A repeated field must carry one of these reason codes:

- `THRESHOLD_PROOF`
- `MATURITY_PROOF`
- `CONFLICT_EVIDENCE`
- `DERIVATION_INPUT`
- `SOURCE_QA_EVIDENCE`

Any repeated field without a reason code should be removed from the OTA output.