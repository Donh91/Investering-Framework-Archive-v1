# TechDev Claim and Revision Extraction — Issues #81–#95

**Import date:** 2026-07-10  
**Status:** SOURCE_BACKED_EXTRACTION_V0_1 / UNSCORED  
**Owner:** Research Lab / TechDev Claim Ledger  
**Source manifest:** `08_SOURCE_MATERIAL/techdev/2026-07-10__techdev-issues-81-95__source-manifest.md`  
**Primary ledger:** `06_RESEARCH_LAB/forward_tests/2026-07-10__techdev-claim-ledger__operational.md`

## Extraction contract

This file freezes identifiable claims and revisions before outcome scoring.

```text
SCORING_PERFORMED: NO
OUTCOME_BACKFILL: NO
RETROSPECTIVE_REWRITE: FORBIDDEN
ORIGINAL_AND_REVISED_CLAIMS: PRESERVED_SIDE_BY_SIDE
TECHDEV_AUTHORITY: MACRO_COMPASS_NOT_EXECUTION_MOTOR
```

`final_outcome`, timing error, range error and trade return remain `PENDING_OUTCOME_PASS`.

## Claim rows

| Claim ID | Issue/date | Asset | Type | Source-backed claim | Target/level | Time window | Revision lineage | Status |
|---|---|---|---|---|---|---|---|---|
| TD81_MACRO_001 | #81 / 2025-11-03 | MACRO | ROADMAP | Business-cycle framework is at a bottom, not a top; the cycle should continue as a slow multi-year trunk rather than a clean parabola. | N/A | multi-year | NONE_AT_IMPORT | SOURCE_BACKED_UNSCORED |
| TD81_TIMING_001 | #81 / 2025-11-03 | BTC_ETH | TIMING_WINDOW | Two probable local-top windows were proposed: Q4 2025-Q1 2026 and Q4 2026-Q2 2027. | N/A | Q4 2025-Q1 2026; Q4 2026-Q2 2027 | NONE_AT_IMPORT | SOURCE_BACKED_UNSCORED |
| TD81_BTC_001 | #81 / 2025-11-03 | BTC | PRICE_RANGE | Nested cup-and-handle structures were said to imply roughly $150K for the smaller structure and $300K for the larger structure. | $150K; $300K | multi-year | NONE_AT_IMPORT | SOURCE_BACKED_UNSCORED |
| TD81_ETH_RSI_001 | #81 / 2025-11-03 | ETH_AND_ALT_PORTFOLIO | TRADE_POLICY | ETH 2-week RSI 76-80 was proposed as a local-top/de-risk zone and 53-57 as a local-bottom/reinvestment zone; suggested de-risking 60-80% while retaining 20-40% core. | RSI 76-80 top; RSI 53-57 bottom | through early 2027 | NONE_AT_IMPORT | SOURCE_BACKED_UNSCORED |
| TD82_MACRO_001 | #82 / 2025-11-17 | MACRO | ROADMAP | Macro direction remained strongly bullish, but the near-term path was revised to a market-wide corrective move before catch-up with the business cycle. | N/A | N/A | REVISES_TD81_MACRO_001 | SOURCE_BACKED_UNSCORED |
| TD82_ETH_001 | #82 / 2025-11-17 | ETH | PRICE_RANGE | ETH was projected to rally to $4,000-$4,200 by late December or early January, then fall to $2,000-$2,200 in Q1 2026. | $4,000-$4,200 then $2,000-$2,200 | late Dec 2025/early Jan 2026; Q1 2026 | NONE_AT_IMPORT | SOURCE_BACKED_UNSCORED |
| TD82_BTC_001 | #82 / 2025-11-17 | BTC | ROADMAP | BTC roadmap: $100K-$110K by end-2025, $85K-$95K in Q1 2026, $150K in H2 2026, $180K in H2 2027, and $300K in 2028. | $100-110K; $85-95K; $150K; $180K; $300K | EOY 2025; Q1 2026; H2 2026; H2 2027; 2028 | REFINES_TD81_BTC_001 | SOURCE_BACKED_UNSCORED |
| TD82_METER_001 | #82 / 2025-11-17 | ETH_MARKET | TRADE_POLICY | A Relief Rally Meter reading above 90 was proposed as a de-risk or avoid-adding signal near the expected ETH corrective high. | meter 90+ | late Dec 2025/early Jan 2026 | NONE_AT_IMPORT | SOURCE_BACKED_UNSCORED |
| TD83_BTC_001 | #83 / 2025-11-30 | BTC | ROADMAP | Roadmap repeated/adjusted to $100K-$110K end-2025, $85K-$95K Q1 2026, $150K H2 2026, $180K-$250K H2 2027, and $300K+ in 2028. | $100-110K; $85-95K; $150K; $180-250K; $300K+ | EOY 2025; Q1 2026; H2 2026; H2 2027; 2028 | REVISES_TD82_BTC_001 | SOURCE_BACKED_UNSCORED |
| TD83_MACRO_TIMING_001 | #83 / 2025-11-30 | MACRO | TIMING_WINDOW | If business-cycle symmetry held, the next red-bar peak was projected around end-2028. | N/A | end 2028 | EXTENDS_TD81_TIMING_001 | SOURCE_BACKED_UNSCORED |
| TD83_SUBCYCLE_001 | #83 / 2025-11-30 | BTC_MACRO | TIMING_WINDOW | A shorter liquidity cycle was said to point to late 2026 as a sub-cycle end, followed by roughly six months of sideways correction before a later surge. | N/A | late 2026 then ~6 months | NONE_AT_IMPORT | SOURCE_BACKED_UNSCORED |
| TD83_ALT_001 | #83 / 2025-11-30 | ALTCOINS | SECTOR | Altcoins were expected to receive their opportunity after current chop, especially across the back three quarters of 2026. | N/A | Q2-Q4 2026 | NONE_AT_IMPORT | SOURCE_BACKED_UNSCORED |
| TD84_PATH_001 | #84 / 2025-12-15 | BTC_ETH | ROADMAP | The Issue #82 relief-rally and double-bottom path was maintained: ETH $4,000-$4,200 then $2,000-$2,200; BTC $100K-$110K then $85K-$95K. | ETH $4.0-4.2K then $2.0-2.2K; BTC $100-110K then $85-95K | late Dec/early Jan; Q1 2026 | CONFIRMS_TD82_ETH_001_AND_TD82_BTC_001 | SOURCE_BACKED_UNSCORED |
| TD84_SECTOR_001 | #84 / 2025-12-15 | ALT_SECTORS | SECTOR | Sector hierarchy favored Layer 1 continuation probability first, DeFi next, AI as higher-risk/higher-reward, RWA as a compression breakout candidate, and DePIN as deepest-discount/highest-risk. | N/A | 12-24 months | NONE_AT_IMPORT | SOURCE_BACKED_UNSCORED |
| TD84_PORTFOLIO_001 | #84 / 2025-12-15 | ALT_PORTFOLIO | SECTOR | Five model portfolios were proposed across conservative-to-aggressive risk levels using the sector hierarchy. | N/A | 12-24 months | NONE_AT_IMPORT | SOURCE_BACKED_UNSCORED |
| TD85_MACRO_001 | #85 / 2025-12-28 | MACRO | ROADMAP | The overall setup was compared with H2 2020 and described as positioning for an imminent acceleration phase during 2026. | N/A | 2026 | NONE_AT_IMPORT | SOURCE_BACKED_UNSCORED |
| TD85_ISM_001 | #85 / 2025-12-28 | MACRO | TIMING_WINDOW | ISM Manufacturing was expected to accelerate and break above 50 as the business-cycle expansion began. | ISM >50 | approaching/2026 | NONE_AT_IMPORT | SOURCE_BACKED_UNSCORED |
| TD85_ETHBTC_001 | #85 / 2025-12-28 | ETHBTC | ROADMAP | An ETH/BTC flag analogous to H2 2020 was expected, if resolved similarly, to produce a substantial period of altcoin outperformance. | N/A | 2026 | NONE_AT_IMPORT | SOURCE_BACKED_UNSCORED |
| TD85_CROSS_ASSET_001 | #85 / 2025-12-28 | ALTCOINS | ROADMAP | Russell 2000 breakout, silver strength, business-cycle trough and ETH/BTC structure were presented as convergent evidence for a major crypto/alt move. | N/A | 2026 | NONE_AT_IMPORT | SOURCE_BACKED_UNSCORED |
| TD86_MACRO_001 | #86 / 2026-01-12 | MACRO | ROADMAP | Current Copper/Gold positioning was interpreted as analogous to the end of recessionary contraction rather than the start of a 2008-style crash. | N/A | months to years | NONE_AT_IMPORT | SOURCE_BACKED_UNSCORED |
| TD86_SCENARIO_001 | #86 / 2026-01-12 | BTC | ROADMAP | Two short-term BTC paths were defined: correction already complete, or one final expanded-flat leg toward roughly $60K. | current continuation or ~$60K | near term | NONE_AT_IMPORT | SOURCE_BACKED_UNSCORED |
| TD86_BTC_BULL_001 | #86 / 2026-01-12 | BTC | PRICE_RANGE | A sustained hold above $95K was defined as the bullish breaker confirming that the correction had ended. | >$95K sustained | near term | NONE_AT_IMPORT | SOURCE_BACKED_UNSCORED |
| TD86_BTC_BEAR_001 | #86 / 2026-01-12 | BTC | PRICE_RANGE | A break below $87K was defined as bearish confirmation for a final leg toward about $60K. | break <$87K then ~$60K | near term | BEAR_PATH_LATER_DEVELOPED_IN_TD89_BTC_001 | SOURCE_BACKED_UNSCORED |
| TD89_MACRO_001 | #89 / 2026-03-02 | BTC_MACRO | ROADMAP | The broader cycle was described as approximately halfway complete, with a possibility of continuing into the early 2030s. | N/A | early 2030s | EXTENDS_TD83_MACRO_TIMING_001 | SOURCE_BACKED_UNSCORED |
| TD89_BTC_001 | #89 / 2026-03-02 | BTC | PRICE_RANGE | One more BTC leg down was projected into $52K-$57K, with possible sub-$50K wicks but not sustained trading. | $52K-$57K; possible wick <50K | potentially starting the following week | REVISES_TD86_BTC_BEAR_001 | SOURCE_BACKED_UNSCORED |
| TD89_ETH_001 | #89 / 2026-03-02 | ETH | PRICE_RANGE | ETH was projected to complete a breakdown toward $1,400-$1,500. | $1,400-$1,500 | after current consolidation | REVISES_TD82_ETH_001 | SOURCE_BACKED_UNSCORED |
| TD89_REVERSAL_001 | #89 / 2026-03-02 | BTC_ETH | ROADMAP | After the final leg down, a sharper V-shaped reversal than the 2022 recovery was expected because of macro/liquidity conditions. | N/A | immediately after projected bottom | NONE_AT_IMPORT | SOURCE_BACKED_UNSCORED |
| TD89_ETHD_001 | #89 / 2026-03-02 | ETHD | TRADE | An inverse-ETF measured move was said to offer roughly 180% upside if ETH completed the projected final leg down. | ~180% measured move | short-duration final decline | NONE_AT_IMPORT | SOURCE_BACKED_UNSCORED |
| TD91_BTC_001 | #91 / 2026-03-29 | BTC | PRICE_RANGE | BTC downside termination zone was tightened to $51K-$57K from two flag projections. | $51K-$57K | final corrective leg | REVISES_TD89_BTC_001 | SOURCE_BACKED_UNSCORED |
| TD91_ETH_001 | #91 / 2026-03-29 | ETH | PRICE_RANGE | ETH target remained $1,400-$1,500 using Amazon analog and convergent Fibonacci projections. | $1,400-$1,500 | final corrective leg | CONFIRMS_TD89_ETH_001 | SOURCE_BACKED_UNSCORED |
| TD91_BITI_001 | #91 / 2026-03-29 | BITI | TRADE | Issue #90 BITI trade was reported open and profitable; target was revised to $32, about 25% above original entry, with stated risk/reward 4.6. | $32 | open as of 2026-03-29 | ORIGINAL_TRADE_SOURCE_ISSUE_90_MISSING | SOURCE_BACKED_UNSCORED |
| TD91_ETHD_001 | #91 / 2026-03-29 | ETHD | TRADE | Issue #90 ETHD trade was reported stopped out; re-entry proposed around $70, stop around $61.50, target $108, stated 54% upside and 4.5 risk/reward. | entry ~$70; stop ~$61.50; target $108 | from 2026-03-29 | ORIGINAL_TRADE_SOURCE_ISSUE_90_MISSING | SOURCE_BACKED_UNSCORED |
| TD91_MACRO_001 | #91 / 2026-03-29 | MACRO | ROADMAP | Copper/Gold and liquidity evidence were described as a generational business-cycle inflection preceding an unusually strong risk-asset advance. | N/A | coming months/years | NONE_AT_IMPORT | SOURCE_BACKED_UNSCORED |
| TD92_TIMING_001 | #92 / 2026-04-12 | BTC_ETH | TIMING_WINDOW | Breakdown from the extended BTC/ETH consolidation was expected around the week of April 19. | N/A | week of 2026-04-19 | TIMING_EXTENSION_OF_TD91_BTC_001_AND_TD91_ETH_001 | SOURCE_BACKED_UNSCORED |
| TD92_BTC_001 | #92 / 2026-04-12 | BTC | PRICE_RANGE | BTC correction target remained $51K-$57K. | $51K-$57K | after consolidation breakdown | CONFIRMS_TD91_BTC_001 | SOURCE_BACKED_UNSCORED |
| TD92_ETH_001 | #92 / 2026-04-12 | ETH | PRICE_RANGE | ETH target was widened from $1,400-$1,500 to $1,400-$1,600. | $1,400-$1,600 | after consolidation breakdown | REVISES_TD91_ETH_001 | SOURCE_BACKED_UNSCORED |
| TD92_BITI_001 | #92 / 2026-04-12 | BITI | TRADE | Prior BITI trade was reported stopped for about a 5% loss; re-entry proposed at about $24.11, stop $22.17, target $32.60, stated 35% upside. | entry ~$24.11; stop $22.17; target $32.60 | from 2026-04-12 | REVISES_TD91_BITI_001 | SOURCE_BACKED_UNSCORED |
| TD92_ETHD_001 | #92 / 2026-04-12 | ETHD | TRADE | ETHD was reported stopped again for about a 10% loss; another re-entry proposed at about $53.32, stop $44.89 and target about $130. | entry ~$53.32; stop ~$44.89; target ~$130 | from 2026-04-12 | REVISES_TD91_ETHD_001 | SOURCE_BACKED_UNSCORED |
| TD92_TRADE_POLICY_001 | #92 / 2026-04-12 | BITI_ETHD | TRADE_POLICY | The re-entries were described as the last attempts; if the expected breakdown failed, focus would move to the long side. | N/A | after week of 2026-04-19 | NONE_AT_IMPORT | SOURCE_BACKED_UNSCORED |
| TD93_ETH_001 | #93 / 2026-04-27 | ETH | PRICE_RANGE | ETH final leg was expected to terminate in the $1,400-$1,600 range with a sharp V-shaped recovery. | $1,400-$1,600 | next 4-6 weeks | CONFIRMS_TD92_ETH_001 | SOURCE_BACKED_UNSCORED |
| TD93_ETHD_001 | #93 / 2026-04-27 | ETHD | TRADE | ETHD setup restated around $51.45 entry, $43.35 stop and $130 target, described as about 150% gain potential. | entry ~$51.45; stop ~$43.35; target ~$130 | from 2026-04-27 | REVISES_TD92_ETHD_001 | SOURCE_BACKED_UNSCORED |
| TD93_ETHU_001 | #93 / 2026-04-27 | ETHU | TRADE | After ETH bottom, ETHU entry was projected near $13 in late May/early June with target $50-$60 by mid-August, described as about 350% gain. | entry ~$13; target $50-$60 | late May/early Jun 2026 to mid-Aug 2026 | NONE_AT_IMPORT | SOURCE_BACKED_UNSCORED |
| TD93_COMPOUND_001 | #93 / 2026-04-27 | ETHD_ETHU | ROADMAP | Capturing both the projected ETHD and ETHU legs was described as a conservative compounded path to roughly 10x capital by year-end. | ~10x | by end 2026 | NONE_AT_IMPORT | SOURCE_BACKED_UNSCORED |
| TD93_CONFIRM_001 | #93 / 2026-04-27 | ETH | TIMING_WINDOW | A few additional days were requested to confirm the breakdown before publishing the broader macro roadmap. | N/A | days after 2026-04-27 | NONE_AT_IMPORT | SOURCE_BACKED_UNSCORED |
| TD94_ETH_CONFIRM_001 | #94 / 2026-05-17 | ETH | ROADMAP | ETH bear-flag breakdown and RSI sequence were declared confirmed. | N/A | as of 2026-05-17 | STATE_UPDATE_TO_TD93_CONFIRM_001 | SOURCE_BACKED_UNSCORED |
| TD94_BTC_001 | #94 / 2026-05-17 | BTC | PRICE_RANGE | BTC bottom target was revised upward from $51K-$57K to $57K-$63K using a trend-based extension that accounts for deeper retracement. | $57K-$63K | final sub-leg | REVISES_TD92_BTC_001 | SOURCE_BACKED_UNSCORED |
| TD94_ETH_001 | #94 / 2026-05-17 | ETH | PRICE_RANGE | ETH target remained unchanged at $1,400-$1,600. | $1,400-$1,600 | final sub-leg | CONFIRMS_TD93_ETH_001 | SOURCE_BACKED_UNSCORED |
| TD94_MACRO_TIMING_001 | #94 / 2026-05-17 | MACRO | TIMING_WINDOW | The 2-month MACD was expected to print a red histogram bar within one to two candles, roughly two to four months. | N/A | 2-4 months from 2026-05-17 | NONE_AT_IMPORT | SOURCE_BACKED_UNSCORED |
| TD94_TWO_TRADE_001 | #94 / 2026-05-17 | ETHD_ETHU | TRADE_POLICY | The short-then-long two-trade plan from Issue #93 was stated to remain live. | N/A | through projected bottom and recovery | CONFIRMS_TD93_ETHD_001_TD93_ETHU_001_TD93_COMPOUND_001 | SOURCE_BACKED_UNSCORED |
| TD95_BOTTOM_001 | #95 / 2026-05-31 | BTC_ETH | TIMING_WINDOW | BTC and ETH bottoms were projected for end-June or early July, with BTC at $57K-$63K and ETH at $1,400-$1,600. | BTC $57K-$63K; ETH $1,400-$1,600 | end Jun/early Jul 2026 | ADDS_TIMING_TO_TD94_BTC_001_AND_TD94_ETH_001 | SOURCE_BACKED_UNSCORED |
| TD95_ETH_ROADMAP_001 | #95 / 2026-05-31 | ETH | ROADMAP | ETH roadmap: $2,800-$3,400 by September-October, $4,500-$5,000 by year-end, and $6,000-$6,500 by mid-2027. | $2.8-3.4K; $4.5-5.0K; $6.0-6.5K | Sep-Oct 2026; end 2026; mid-2027 | NONE_AT_IMPORT | SOURCE_BACKED_UNSCORED |
| TD95_BTC_ROADMAP_001 | #95 / 2026-05-31 | BTC | ROADMAP | BTC roadmap: $94K-$98K by September-October, $115K-$125K by year-end, and $140K-$160K by mid-2027. | $94-98K; $115-125K; $140-160K | Sep-Oct 2026; end 2026; mid-2027 | NONE_AT_IMPORT | SOURCE_BACKED_UNSCORED |
| TD95_RED_ZONE_001 | #95 / 2026-05-31 | MACRO | ROADMAP | The roadmap used a conservative assumption that the red impulse phase would resemble prior 10-12 month periods despite the unusually long green phase. | N/A | ~12 months from projected bottom | NONE_AT_IMPORT | SOURCE_BACKED_UNSCORED |
| TD95_REVISION_POLICY_001 | #95 / 2026-05-31 | MACRO | ROADMAP | The year-long roadmap would be revised and extended if later data showed the red phase stretching similarly to the green phase. | N/A | ongoing after macro impulse begins | NONE_AT_IMPORT | SOURCE_BACKED_UNSCORED |
| TD95_RELATIVE_001 | #95 / 2026-05-31 | ETHBTC | ROADMAP | ETH was expected to outperform BTC through the recovery, and the tactical plan remained to flip the ETHD short into an ETHU long near the projected bottom. | N/A | post-bottom through 2026 | CONFIRMS_TD94_TWO_TRADE_001 | SOURCE_BACKED_UNSCORED |

## Missing-source rows

```yaml
ISSUE_87:
  status: SOURCE_MISSING
  claims_extracted: 0
  inference_from_later_issues: FORBIDDEN

ISSUE_88:
  status: SOURCE_MISSING
  claims_extracted: 0
  inference_from_later_issues: FORBIDDEN

ISSUE_90:
  status: SOURCE_MISSING_CRITICAL
  claims_extracted: 0
  later_derivative_reports:
    - TD91_BITI_001
    - TD91_ETHD_001
  original_entry_stop_target_scoring: BLOCKED
```

## Revision chains frozen at import

### Near-term BTC path

```text
TD82_BTC_001: $100K-$110K end-2025 then $85K-$95K Q1 2026
→ TD86_BTC_BEAR_001: break below $87K points toward ~$60K
→ TD89_BTC_001: $52K-$57K, possible sub-$50K wick
→ TD91_BTC_001 / TD92_BTC_001: $51K-$57K
→ TD94_BTC_001 / TD95_BOTTOM_001: revised to $57K-$63K, end-Jun/early-Jul timing
```

### Near-term ETH path

```text
TD82_ETH_001 / TD84_PATH_001: $4,000-$4,200 relief then $2,000-$2,200 Q1 2026
→ TD89_ETH_001 / TD91_ETH_001: revised to $1,400-$1,500
→ TD92_ETH_001 onward: widened to $1,400-$1,600
→ TD95_BOTTOM_001: end-Jun/early-Jul timing added
```

### Tactical inverse/leveraged ETF chain

```text
Issue #90 original BITI/ETHD rows: SOURCE_MISSING
→ TD91_BITI_001 / TD91_ETHD_001: derivative outcome/re-entry reports
→ TD92_BITI_001 / TD92_ETHD_001: stop-outs and wider re-entries
→ TD93_ETHD_001 / TD93_ETHU_001 / TD93_COMPOUND_001: short-then-long and 10x claim
→ TD94_TWO_TRADE_001 / TD95_RELATIVE_001: plan reaffirmed
```

### Long-range roadmap chain

```text
TD81_BTC_001
→ TD82_BTC_001
→ TD83_BTC_001
→ TD95_BTC_ROADMAP_001

TD83_MACRO_TIMING_001
→ TD89_MACRO_001
→ TD94_MACRO_TIMING_001
→ TD95_RED_ZONE_001 / TD95_REVISION_POLICY_001
```

## Import summary

```yaml
issues_imported: 12
issues_missing: [87, 88, 90]
source_backed_claim_rows: 55
roadmap_rows: 20
timing_rows: 8
price_range_rows: 13
trade_rows: 7
trade_policy_rows: 4
sector_rows: 3
scored_rows: 0
final_outcomes_populated: 0
```

## Next allowed step

A separate outcome pass may later add:

- verified actuals;
- timing error;
- range error;
- trade result;
- revision usefulness;
- framework action impact.

It must not change the frozen source-backed claim text or erase earlier revisions.
