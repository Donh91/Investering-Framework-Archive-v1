# Task 2 · original MATURED 314 · first non-duplicative stratified diagnosis

**As of 2026-10-16 · RESEARCH_ONLY / EX_POST_DEVELOPMENT / NOT_CERTIFIED_PIT.**
This **adds** to already merged #1655/#1656; it does not re-run their 16 or 824 pooled comparisons, change historical outcomes or reopen the closed earlier Round2 Pullback experiments. Existing owner [#1596](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596).

## Exact original-source execution, not invented missing data

Original GH Actions run `38427468434`, artifact `11829371964` (expires 2026-10-27 16:07 UTC) was **downloaded and read in full**; original outer ZIP SHA256 `4bce43736374b8fcff7aa9ffd1fdac18c303d8b2264b8291bb6e0b80fcde23ae`, inner original CSV SHA256 `616e70fd87a79acf126591c1f8e704c74da7a2bd3b3aa181838ac5f861fea5d9`. Original count = 1,140 forecast×asset×horizon slots. The source ZIP stays in its existing verified owner/Library custody; **do not add original private/provider-level or market raw rows to this public control repository**.

Usage after private authorized or owner-supplied download:
```bash
python 04_MARKET_LEARNING/handlekompas/research/2026-10-16__task2_matured314_reproduce_v1.py \
  --artifact /path/to/original-task15-actions.zip \
  --published-receipt 04_MARKET_LEARNING/handlekompas/research/2026-10-16__TASK2_TASK15_ORIGINAL_MATURED314_STRATIFIED_DEV_v1.json
```
Script **fails closed** on original ZIP or CSV SHA mismatch, missing 1,140-roster or duplicated prediction ID, unexpected original maturity/censor/receipt split, missing 44 abstentions, original HIT/MISS vs tape inconsistency and published cell/cluster count drift. Prints **only aggregates**, no original provider/price rows. No API expense, schedule, credentials, market/portfolio powers or remote historical provider first-known claims.

## NEW separate original-maturity calculation

Original 1,140-row status: **358 MATURED**, **570 CENSORED**, **212 NO_ORIGINAL_RECEIPT** before tape joins and forecast abstention filter. Only 824 rows were later matched to a price outcome: **314 original MATURED**, 500 original CENSORED, 10 original NO_ORIGINAL_RECEIPT. **44 of the original 358 MATURED were honest NO_EDGE abstentions** and MUST remain in the issuance/coverage denominator: 1H 4, 4H 18, 24H 22, NOT counted as incorrect or secretly removed as if no forecast. The publication's 314 is the **conditional issued directional decision** analysis.

On only 314 originally MATURED matched decisions: **Compass 145/314 (46.18%)**, prior-packet-price-sign baseline **142/314 (45.22%)**, apparent **+3 hits / +0.96 percentage points**. They chose the same direction 203 times and differed 111; in those 111 disagreements, Compass alone won **57**, baseline alone **54**. Both correct 88; both wrong 115. **Not a proven advantage.** No action return after cost is measured.

| Cohort | Paired N | Compass | Prior-price | Difference (pp) |
| --- | ---: | ---: | ---: | ---: |
| BTC 1H | 18 | 10 | 9 | +5.56 |
| BTC 4H | 63 | 30 | 26 | +6.35 |
| BTC 24H | 76 | 41 | 38 | +3.95 |
| ETH 1H | 20 | 10 | 14 | -20.00 |
| ETH 4H | 65 | 22 | 25 | -4.62 |
| ETH 24H | 72 | 32 | 30 | +2.78 |
| BTC total | 157 | 81 | 73 | +5.10 |
| ETH total | 157 | 64 | 69 | -3.18 |

**Exploratory dependence sensitivity:** 125 distinct exact original issue clocks but only 28 UTC issue dates and **zero independently certified market shock families**. Seeded 8,000-resample issue-clock cluster bootstrap indicative lift interval **[-7.099,+8.555] pp**; by UTC issue date **[-7.895,+10.063] pp**. Market-day clusters overlap from UTC date to next on 24H horizons, while BTC and ETH are correlated. Thus these ranges are sensitivity diagnostics, **not valid confirmatory confidence bounds or independently exchangeable causal-event inference**.

**Observed exit/rotation diagnostic NOT ex ante:** Among the 142 outcomes where the *retrospectively known* next return continued the prior-packet direction, the price baseline scored 142 and Compass 88; among 172 next-return reversals, price baseline scored 0 and Compass 57. The Compass divergences are therefore potentially useful when reversal occurs, but many are **false reversals** when momentum continues: 57 versus 54. This is a hypothesis for a frozen prospective regime controller, not an outcome-free market regime label or a licensed strategy.

**Material availability bias:** original MATURED paired coverage by horizon differs substantially: BTC/ETH 1H 18/86 and 20/86 (20.93% and 23.26%); 24H 76/162 and 72/156 (46.91% and 46.15%). 4H intermediate. Cross-horizon hit-rate comparison is **selection-confounded** by outcomes original owner managed to publish, not necessarily by model differences.

## Additional actual-original-source data test: archive arrival delays

Read the **separate full original** `TASK15_R1_OWNER_PUBLICATION_FULL_CENSUS.json` 717,189-byte member, SHA256 `b30d8e515221314a217b5add128f0918f9eeaf6d99d2c682d142482a9f3d4776`, ledger-bound to the same original CSV SHA. ALL **814** original eligible source-publication cases are documented: **314** first-archived by due+90 minutes and **500** first-archived after. Original 500/814 = **61.4%** fail the archive's 90-minute publication-class condition; original archival evidence alone has `scorer_would_have_received_source=UNVERIFIED_EXECUTION_CONTEXT` for **all 814**.

| First archive commit relative to original forecast's target time | N | Median delay (lower midpoint) | 90th percentile |
| --- | ---: | ---: | ---: |
| Original MATURED cohort ≤90 min | 314 | 39.617 min | 80.350 min |
| Original CENSORED cohort >90 min | 500 | 164.333 min | 313.033 min |

The original 814 rows cover 175 distinct published Git commit IDs and 29 source paths, **NOT** 814 independent providers/events. Horizon split 1H 38/170 on time, 4H 128/328, 24H 148/316. This is a **documented original-publication coverage/censor mechanism**, not proof that the upstream vendor was late, that the scorer read the file, or that fixing the Git arrival clock would have yielded more accurate predictions.

**Information-value-based collection priority:** Address *original on-time source and execution receipt latency* as a large measured scientific coverage limitation before buying expensive extra feature histories. The potential number of better-verifiable future outcomes is material, but the **marginal directional information or after-cost PnL benefit remains UNKNOWN**, to be measured prospectively. This entire source-clock analysis is classified **PUBLICATION_GIT_COMMIT_TIME_ONLY**, never as original vendor `FIRST_KNOWN`.

## What next, without blocking on perfect provider vintage

1. **DONE for this bounded question:** extract original-MATURED 314, paired asset×horizon divergence, error taxonomy, 44 NO_EDGE coverage, 28-day/125-issue dependency and 1H/24H maturity selection. Result is small/no robust Compass increment; no repeated pooled 824 run.
2. **Next not-yet-tested original-data question:** the existing original frozen-vote file `TASK15_FROZEN_VOTE_ABLATION_DEV_v1.json` reports *wider 824 matched* voting subsets. Its published aggregate summaries **cannot be re-filtered to the original-MATURED 314 by subtraction**; need exact row IDs and original vote vectors to run a *same-clock* one-family-at-a-time BTC/ETH×horizon ablation with explicit abstention/dropout and negative time-shift controls. If frozen source vectors unavailable, mark `SOURCE_ROWS_UNAVAILABLE_FOR_JOIN` and do not hallucinate family lift.
3. **Follow other populations separately:** originally frozen CN weekly, M6 warnings/real warning absence, 851,882 altseason-hourly/context rows, public ETF/CFGI and restricted owner-approved raw feeds. No pooling without compatible original vintage, horizons, market-event and sample denominator. Missing vendor first-publication, original alert delivery and fill timestamps are **priority acquisition for certified precision and investor-action edge**, not barriers to development diagnostics.
4. Any vendor data retrieved now without authenticated original vintage is `RECONSTRUCTED_EX_POST` with provider/endpoint, query/response bytes hash, fetched-at and publication/revision distinctions. Do not spend paid Sol on frozen old 16/824/314 data; only new source-bound complex falsification with the existing audited budget lane.

Full aggregate machine receipt: `2026-10-16__TASK2_TASK15_ORIGINAL_MATURED314_STRATIFIED_DEV_v1.json`. This is a **development research artifact**, not a revision of Original Official Compass outcomes and not an admission to R2 or a portfolio trade.
