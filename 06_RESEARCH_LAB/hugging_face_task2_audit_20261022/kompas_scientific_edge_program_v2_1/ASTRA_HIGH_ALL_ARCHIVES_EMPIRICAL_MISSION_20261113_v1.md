# ASTRA HIGH · ALL CN / ALL MASTER MONDAYS / RESEARCH LAB · Empirical extension v1

**Source freeze:** Git blob tree `e484407e790fae260ef82796501bf28ea0bbbe4f` for indexing; refresh current main SHA at paid-model run, verify exact byte hashes of inputs. 2026-11-13. **Research-only. No official forecasts, risk score, trading or model promotion.**

**Scientific owner:** Archive Task2 #1596. Collaborators: CN #1516/#1593, Source #1827, Risk #1553, existing Research Parallel Lanes and HRE. **Non-overlap:** Fable 5.2 R1–R4 completed data/CI/release research, Fable R5 W47+ prospective PIT model test is DATA_GATED, R6 Alpha×Kompas after-cost also DATA_GATED, Claude original P0 reviews and Vault work are separate and must not be repeated.

## Source census actually located, indexed by Git blob, no hypothetical data

The adjacent `ASTRA_HIGH_COMPLETE_RESEARCH_CN_SOURCE_INDEX_20261113_v1.json` catalogs **2,559 native public Git blobs** in 7 families, from a pinned Git tree, including:
- **330 CN** archive, traceability, public/readiness, original/freeze and internal sources; every `05_CYCLE_NAVIGATOR/weekly/2026/W36..W46` plus recovered May–September published issues.
- **195** original external/method and alpha sources under `04_RESEARCH_LAB`.
- **793** full `06_RESEARCH_LAB`, including Task2/HuggingFace, Shadow, source recovery, Round3, matched-row tournament, M1–M7, high-value edge, past null results and progressive audits.
- **1,145** selected API agent research/weekly canonical generated outputs and candidate/confidence-source paths. Does NOT imply every output is an issued forecast.
- **56** Master Monday preflight and frozen lineage documents.
- **26** earlier original Master Monday documents in `03_WEEKLY_OPERATIONS/master_monday` including July W28–W31.
- **14** Historical Reality Engine native results / negative control / epidemic replay files.

The separate `ASTRA_HIGH_OUTCOME_AND_EARLY_WEEK_SOURCE_INDEX_20261113_v1.json` adds **53 native tree/blob entries** covering W31–W46 weekly raw outcomes, 2026 weekly-close packages, early official forecast ledgers and July/Aug legacy weekly output.

Legacy published CN: archived `published/2026` contains CN #06 2026-05-04, #10 2026-06-01, #16–28 up to 2026-10-05, some `RECOVERED`. Recovery presence is NOT proof of original first publication. Earliest Master Monday documents in present `03_WEEKLY_OPERATIONS/master_monday` dated 2026-07-06. Machine weekly freezes start W36; numeric range fields are absent W36–W38. Internal precision freezes appear W40–W46. **Missing and unissued forecasts must appear in the denominator, not be silently skipped.** 

## Real-data calculation is no longer missing

Reuse [Task2 PR #2113](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/2113) and native [CI run 43431179518](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/43431179518), **only as source-pinned *retrospective research*, never as original delivery-qualified proof**. Native CI:
- `task2-native-price-range-baselines` SUCCESS, output `task2-realdata-forecast-43431179518`: 112 rows, 28 matched asset/week/window observations across seven independent ISO weeks W39–W45. Original frozen CN bounds containment 75.0 %, prior-close full-width 85.714 %, but mean width 13.172 % vs 16.860 %, so raw coverage CANNOT be called superior. Diagnostic width-adjusted loss 23.539 CN vs 25.990 full-width, `a10` exploratory, no probabilistic 90% interval inference. Prior-close narrower variants also supplied. 28 matched observations are NOT 28 independent crash events; original first consumer delivery UNKNOWN.
- `task2-native-hourly-risk-negatives` SUCCESS, output `task2-realdata-risk-43431179518`: 270 price-only counterfactual rows from 1,176 hourly BTCUSDT/ETHUSDT bars, 45 daily decision origin dates per coin with 3 rules; `-8% low within 72h` outcome. BTC sample had zero positive events; thus no inference about severe crash warning. ETH only 4 positive origin days, up to 3 event clusters; 24h -3% caught 1, missed 3, with 2 false positives, and no verified after-cost advantage. These rules are **not** actual issued Kompas 3/5, 4/5 or 5/5 warning scores.
- Native artifacts are GitHub Actions artifacts, not files automatically available to Astra's Responses API context. The new researcher MUST **download, verify SHA and attach full CSV and summaries** before claiming any new test on them. Known per-file SHA256: `forecast_rows.csv=50cfcf031b788a9105b7867d43271fa0a3b1206c1949626421311ddd253c89f0`; `forecast_summary.json=6dd17a0391052a2d28f6e6562f8e98db727a5d24441b0b9013b557b8c369eea6`; `risk_rows.csv=1ca7bf42e4051f565fdb729f41dff901e40849f079297ecc421cd0b9b04eebe8`; `risk_summary.json=f47b02af921b7d23c36f169c031555f1c1656b7ae4fbad41a07d557e71226e71`. Mismatches -> STOP.

## Instructions for the next *research-grade* Astra HIGH session

**Do NOT replay prior 2026-11-13 Astra 8-document text-only response.** That completed 0.94522 USD run, but lacked external market tools and executable historical evidence. Its scientific verdict was `SOURCE_BLOCKED`.

1. **Precompute using real GitHub Actions Python:** combine source-pinned 112 forecast and 270 risk rows with every unique weekly CN freeze W36–W46, published May-Aug/Sept predecessor CN, W28–W46 Master Mondays, 2026 W31–W46 weekly raw market packs, internal claim freeze/precision scorecard, previous weekly close persistence, and HRE native episode/negative ledger. All inputs must pass independent hash/contract/time crosswalk. Build an exact per-week canonical issuance table and explicit first-known UNKNOWN, NEVER turn repository commit time into provider publication or user receipt.
2. **Full original claim census:** count frozen WEEKLY and DAY1-2/DAY3-4/DAY5-7/2–3w claims, split the 14 internal parameters into independent vs aliases, track missing/N/A/NO_DECISION, maturation and source issuer. Older published recovery files are conditional evidence only. Identify which forecasts can be compared to actual market outcomes and which cannot.
3. **For each qualified weekly observation:** compare original forecast vs contemporaneous closest cheap matched baselines with proper widths, outcome close vs range extremes, drawdown severity and no-event controls, not only high win rates. Report N *independent source weeks*, nested origins, and confidence, with W46 already research-exposed and incomplete on 13 November. W47 untouched prospective and Fable-owned.
4. **Warning research:** same-clock exact original risk scores where available; price-only proxy rules cannot support claim that original 3/5 should have been 4/5. Match shock and quiet cohorts, estimate cost false positives/short hedges/NO_TRADE and source lags; W39–W45 sample has no BTC `-8%/72h` events. Do NOT optimize thresholds on the failed W46 aftermath then call them forward.
5. **Historical HRE/Research Lab ablations:** reuse existing published HRE five-era risk episodes and true nulls, original Ironflow and shared-row source gate. Mechanism-based alternatives must survive negative controls and extra historical regimes. Avoid work already owned by Fable, Claude OT, S1 and Alpha #228.
6. **Independent science:** provide 10 supported findings with exact row/claim receipts, 5 falsified/NO_EDGE hypotheses, three *predeclared* shadow model arms max, output row-level compatible machine files, zero-lookahead controls, minimal original-owner implementation PR plan and precise what cannot be known.

### Research filing and safety

Budget: owner's explicit new cap **USD 10 total** for the one deeper Astra job. Existing automatic Sol-only dispatcher must not be altered; an owner-only, nonrecurring workflow action must have a separate one-use native durable claim before paid API POST, shared owner budget reserve, verified served model `gpt-6-astra` High, forecast prompt bytes and maximum output tokens capped so worst-case Standard token price is <= USD 10. One actual paid POST and GET-only recovery, no retries. **No source data/private secrets to model logs or public artifacts.** Output retains original raw artifacts plus hashes, separate Claude Bridge #173 independent review **only after actual output**, not a self-attested "research complete".

Outcome files used in Research Lab require public-safe source blobs only. No Python model "internet" is assumed unless explicitly linked; all external observations must be brought as source-pinned provider data via GitHub first. **An index of 2,559 paths is not itself an empirical analysis.** 

## Fable non-overlap and conditional handoff
- Fable R1–R4, existing mainline source/CI fixes and PR #2104 source-integrity review: OUT of scope.
- Fable R5 W47+ and R6 after-cost microcaps: only prospective when original data mature, owner has not booked them.
- Astra unique mandate: **Historical archived CN + all Master Mondays + HRE cross-era + source-provenance tests + simple baselines + missing/false alerts**, using existing native evidence and not market action.
