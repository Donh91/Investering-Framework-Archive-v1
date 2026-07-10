# TechDev Claim and Revision Extraction Addendum — Issues #87, #88 and #90

**Import date:** 2026-07-10  
**Status:** SOURCE_BACKED_EXTRACTION_V0_2 / UNSCORED  
**Owner:** Research Lab / TechDev Claim Ledger  
**Parent extraction:** `2026-07-10__techdev-claims-issues-81-95__source-backed-extraction-v0-1.md`  
**Source manifest:** `08_SOURCE_MATERIAL/techdev/2026-07-10__techdev-issues-81-95__source-manifest.md`

## Extraction contract

```text
SCORING_PERFORMED: NO
OUTCOME_BACKFILL: NO
RETROSPECTIVE_REWRITE: FORBIDDEN
ORIGINAL_AND_REVISED_CLAIMS: PRESERVED_SIDE_BY_SIDE
TECHDEV_AUTHORITY: MACRO_COMPASS_NOT_EXECUTION_MOTOR
```

This addendum closes the missing-source gaps for Issues #87, #88 and #90. It adds 17 source-backed claim rows. Final outcomes, timing error, range error and trade returns remain pending a separate verified-actuals pass.

## Claim rows

| Claim ID | Issue/date | Asset | Type | Source-backed claim | Target/level | Time window | Revision lineage | Status |
|---|---|---|---|---|---|---|---|---|
| TD87_MACRO_001 | #87 / 2026-02-02 | MACRO | ROADMAP | The market was described as completing a wave 2 within wave 2, with wave 3 of wave 3 expected next as the business cycle reached its bottom line. | N/A | after final corrective leg | EXTENDS_TD86_MACRO_001 | SOURCE_BACKED_UNSCORED |
| TD87_ETH_LOW_001 | #87 / 2026-02-02 | ETH | PRICE_RANGE | ETH’s Amazon analog was projected to produce a final corrective low around $1,800-$2,000 in Q1 2026. | $1,800-$2,000 | Q1 2026 | REVISES_TD82_ETH_001 | SOURCE_BACKED_UNSCORED |
| TD87_ETH_ROADMAP_001 | #87 / 2026-02-02 | ETH | ROADMAP | ETH roadmap targets were stated as about $6,000 by H2 2026, $10,000 by H2 2027 and $15,000 by H2 2028. | $6K; $10K; $15K | H2 2026; H2 2027; H2 2028 | NONE_AT_IMPORT | SOURCE_BACKED_UNSCORED |
| TD87_USDTD_001 | #87 / 2026-02-02 | USDT_D_CRYPTO | TIMING_WINDOW | USDT dominance was said to lag DXY by roughly one year, implying one final corrective rise in Q1 2026 before a larger breakdown supporting crypto. | N/A | Q1 2026 then post-Q1 decline | NONE_AT_IMPORT | SOURCE_BACKED_UNSCORED |
| TD87_ALT_001 | #87 / 2026-02-02 | ALTCOINS | SECTOR | Rounded-top wave-2 structures in assets such as SOL and VELO were compared with ETH 2016-2017 and inverse DXY as setups preceding vertical wave-3 advances. | N/A | multi-year | EXTENDS_TD84_SECTOR_001 | SOURCE_BACKED_UNSCORED |
| TD88_ETH_001 | #88 / 2026-02-19 | ETH | PRICE_RANGE | ETH’s final low target was revised down from $1,800-$2,000 to $1,400-$1,500 based on new Fibonacci extensions and the Amazon analog. | $1,400-$1,500 | final corrective leg | REVISES_TD87_ETH_LOW_001 | SOURCE_BACKED_UNSCORED |
| TD88_BTC_001 | #88 / 2026-02-19 | BTC | PRICE_RANGE | BTC’s inverted rising-wedge structure was projected to terminate in the $52,000-$57,000 zone. | $52K-$57K | final corrective leg | REFINES_TD86_BTC_BEAR_001 | SOURCE_BACKED_UNSCORED |
| TD88_BTC_PUMP_001 | #88 / 2026-02-19 | BTC | PRICE_RANGE | Before the final decline, BTC was expected to produce a brief liquidity-grab rally toward $71,000-$74,000. | $71K-$74K then $52K-$57K | near term | PATH_COMPONENT_OF_TD88_BTC_001 | SOURCE_BACKED_UNSCORED |
| TD88_ETH_PUMP_001 | #88 / 2026-02-19 | ETH | PRICE_RANGE | Primary ETH path called for a rally to $2,150-$2,300 before reversal to $1,400-$1,500; a revisit of the high-$1,600s first would reduce the probability of the rally making a new local high. | $2,150-$2,300 then $1,400-$1,500 | near term | PATH_COMPONENT_OF_TD88_ETH_001 | SOURCE_BACKED_UNSCORED |
| TD88_INVALIDATION_001 | #88 / 2026-02-19 | BTC | TRADE_POLICY | A sustained weekly close back above the Bollinger Band basis without the projected final leg was defined as confirmation that the macro bottom was already in. | weekly basis reclaim | weeks | INVALIDATES_TD88_BTC_001_IF_MET | SOURCE_BACKED_UNSCORED |
| TD88_POSITIONING_001 | #88 / 2026-02-19 | BTC_ETH_PORTFOLIO | TRADE_POLICY | Personal positioning was described as closed short, then short-term long for the pump, then rotating fully short near the rally targets, followed by heavy long exposure at the projected macro bottom. | BTC $71-74K / ETH $2.15-2.30K flip zones | final-leg sequence | PRECURSOR_TO_TD90_BITI_001_AND_TD90_ETHD_001 | SOURCE_BACKED_UNSCORED |
| TD90_TIMING_001 | #90 / 2026-03-15 | BTC_ETH | TIMING_WINDOW | The final leg toward the projected BTC and ETH lows was expected to begin during the week of publication. | N/A | week of 2026-03-15 | EXTENDS_TD88_BTC_001_AND_TD88_ETH_001 | SOURCE_BACKED_UNSCORED |
| TD90_BTC_001 | #90 / 2026-03-15 | BTC | PRICE_RANGE | BTC’s final corrective target remained $52,000-$57,000. | $52K-$57K | final leg | CONFIRMS_TD88_BTC_001 | SOURCE_BACKED_UNSCORED |
| TD90_LIQUIDITY_001 | #90 / 2026-03-15 | BTC_MACRO | ROADMAP | The absence of a major liquidity-cycle peak was used to argue that the market remained mid-cycle and that the correction was not a cycle-ending event. | N/A | macro | EXTENDS_TD89_MACRO_001 | SOURCE_BACKED_UNSCORED |
| TD90_LEADLAG_001 | #90 / 2026-03-15 | BTC | TIMING_WINDOW | A prior mini-liquidity-cycle lead of about 16 bars or roughly 220 days was projected onto the current correction, placing the bottom in the current window. | ~16 bars / ~220 days | current March 2026 window | NONE_AT_IMPORT | SOURCE_BACKED_UNSCORED |
| TD90_BITI_001 | #90 / 2026-03-15 | BITI | TRADE | Original BITI setup: entry around $25.50, stop $24.23, target $33, stated risk about 5% and risk/reward about 6:1. | entry $25.50; stop $24.23; target $33 | short-term final leg | ORIGIN_FOR_TD91_BITI_001_AND_TD92_BITI_001 | SOURCE_BACKED_UNSCORED |
| TD90_ETHD_001 | #90 / 2026-03-15 | ETHD | TRADE | Original ETHD setup: entry around $67, stop $60, target about $130, stated risk about 10% and risk/reward about 9.5:1. | entry $67; stop $60; target ~$130 | short-term final leg | ORIGIN_FOR_TD91_ETHD_001_TD92_ETHD_001_AND_TD93_ETHD_001 | SOURCE_BACKED_UNSCORED |

## Repaired revision chains

### ETH near-term target

```text
TD87_ETH_LOW_001: $1,800-$2,000 Q1 2026
→ TD88_ETH_001: revised to $1,400-$1,500
→ TD89_ETH_001 / TD91_ETH_001: maintained $1,400-$1,500
→ TD92_ETH_001 onward: widened to $1,400-$1,600
```

### BTC final-leg path

```text
TD86_BTC_BEAR_001: break below $87K points toward ~$60K
→ TD88_BTC_001: $52K-$57K
→ TD89_BTC_001: $52K-$57K, possible sub-$50K wick
→ TD90_BTC_001: $52K-$57K
→ TD91_BTC_001 / TD92_BTC_001: $51K-$57K
→ TD94_BTC_001 / TD95_BOTTOM_001: revised to $57K-$63K
```

### Tactical trade origins

```text
TD88_POSITIONING_001: discretionary pump-long → final-leg short → heavy long at bottom
→ TD90_BITI_001: original formal BITI setup
→ TD91_BITI_001: open/profitable report and target revision
→ TD92_BITI_001: stop-out and re-entry

TD90_ETHD_001: original formal ETHD setup
→ TD91_ETHD_001: stop-out and re-entry
→ TD92_ETHD_001: second stop-out and wider re-entry
→ TD93_ETHD_001 / TD93_ETHU_001: short-then-long plan
```

## Import summary

```yaml
new_source_issues_imported: 3
new_source_backed_claim_rows: 17
cumulative_issues_imported_81_95: 15
cumulative_source_backed_claim_rows_81_95: 72
sequence_status: COMPLETE
scored_rows: 0
final_outcomes_populated: 0
```

## Next allowed step

A separate outcome pass may add verified actuals, timing error, range error, trade result, revision usefulness and framework action impact. It must not change the frozen source-backed claim text or erase earlier revisions.
