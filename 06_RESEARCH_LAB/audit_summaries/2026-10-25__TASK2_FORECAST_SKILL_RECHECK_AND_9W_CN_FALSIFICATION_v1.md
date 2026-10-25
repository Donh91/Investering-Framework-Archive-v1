# Task 2 · Forecast Skill v1.0 · kritisk genkontrol og ni ugers CN-falsifikation
**Dato:** 2026-10-25 · **Status:** RESEARCH_ONLY / RESTROSPECTIVE_DIAGNOSTIC / SCIENCE_R1_NOT_ADMITTED / ZERO_MODEL_PROMOTION.
**Ejer-godkendelse:** [Supervisor #1156](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1156#issuecomment-6394770993).
**Eksisterende ejere:** Task2 #1596, Forward Price #1516, Adaptive #1157, original source #1593; dette er INGEN ny issue-/workflow-/scorer- eller markedsejer.
**Maskinmatrix:** [2026-10-25__task2_cn_weekly_retrospective_originals_v1.json](2026-10-25__task2_cn_weekly_retrospective_originals_v1.json). Original source file paths, original current Git blobs og forecast-/outcome-rækker er bevaret i matrixen.

## A · Den ekstra kritiske kontrol: fire potentielle falske succeser

1. **God intervaldækning kan skabes ved at gøre intervallet stort.** Kræv fælles LOW+HIGH-containment, relativ bredde, tail-breaches og identiske baseline-vinduer. CN's public 70% containment + 30% Jaccard er et legitimt kontinuitetsmål, **ikke** dokumenteret predictive alpha. M3 5 Oct afviste stabil CN-dominans mod DUMB1.5/DUMB2.0 på de undersøgte episoder. Særligt W39 BTC gav et koncentreret heldigt plus; eksklusion ændrede den normaliserede Winkler-rangering.
2. **En nominal 80%-LOW/HIGH-prognose kan ikke skabes af q10-minimum og q90-maksimum.** Det er to marginale skøn. Brug individuel pinball når kvantiler er korrekt udstedt; evaluér LOW/HIGH som en *fælles* realiseret bane. Formel for en scalar `IS_alpha(L,U;y)` kan kun kaldes proper under sin prædefinerede scalar/nominal-score-kontrakt, aldrig automatisk for et høj/lav-par. Vælg tabsfunktion på forhånd og vælg ikke 'bedste baseline' efter at se testugen.
3. **Tidlig offentliggørelse er ikke bekræftet af et filnavn eller en dato alene.** W33 CN20 er `RECOVERED` i september; W36 CN23 er dateret 1 Sep, efter W36 start 31 Aug. W39 machine freeze er 21 Sep **18:13:41Z**, W40 site freeze 28 Sep **05:53:37Z**, W41 5 Oct **06:14:06Z** og W42 12 Oct **06:32:25Z**. ISO day1–2 starter alle mandag 00:00Z, altså *før* freeze for mindst W39–W42. Den fulde ISO-windowscore er derfor **ikke** en ren original fremadrettet score; den officielle public scorer bruger for W41/W42 andet `FIRST_COMPLETE_UTC_HOUR_AT_OR_AFTER_FREEZE` window-policy. Dens officielle tal og denne falsifikationsmatrix må ikke blandes.
4. **Samme prischok giver mange 'hits'.** BTC+ETH og DAY1/DAY3/DAY5 i samme uge, og mange 12-timers Kompas-prognoser, er afhængige. N_raw=54 vinduespar betyder IKKE N_independent=54. For disse 9 uger er independent effective N ukendt og mindre, og **0** rækker er R1-kildemæssigt PIT-admitted. Ingen p-værdi, konfidens for investeringsalpha eller kalibreret joint dækning her.

## B · Faktisk udført historisk data-replay, både godt og dårligt

Reproduceret ved læsning af nuværende original-frysefil eller ordret arkiveret offentlig tekst for hver uge, og modstillede `03_DAILY_CAPTURE_LOGS/weekly/2026/Wxx.json` (168/168 timer, 48/48/72 UTC-timer) med parvis LOW/HIGH. For ældre X-tekster er de publicerede vinduer transskriberet; hver kilde er bundet til Git blob SHA i maskinmatrixen. Dette er deskriptiv rekonstruktion og kræver uafhængig teknisk re-review før forskningsmæssig frigivelse. Den originale CN bruger USD-dollar-bånd; de arkiverede markedsserier er Binance BTCUSDT/ETHUSDT. **Quote-paritet er ikke dokumenteret for et ægte USD-forcast.**

**Tilgængelighed:** W31 mangler fuldt ugedatapanel; W32 har kun 40/168 timer; W33–W42 har **10 komplette markedsuger**, hvor W35 CN22's publicerede tekst mangler numeriske kortsigtede kursprognoser. Dermed **9 uger med seks konkrete BTC/ETH-vinduespar**. W43 er endnu ikke slutafregnet pr. 25 Oct. Ældre May–July 'RECOVERED' CN-poster er ikke automatisk aktuelt originalt forecast-/outcome-admitted sample, selv om deres tekster eksisterer.

| Uge | Andel dækkede BTC+ETH D1–2/D3–4/D5–7 ISO-vinduer | Konkret problem / klassifikation |
|---|---:|---|
| W33 | **5/6** | Aug-10 CN20 bruger sept.-recovered X original; ETH D1–2 HIGH $1,931.57 over $1,930 med $1.57. BTC full-week LOW $62,535.24 under $63,000, men de 6 vinduer alene giver 5/6. |
| W34 | **1/6** | **Ekstrem bullish breakout-miss:** CN21 BTC weekly $61,800–65,800 mod faktisk HIGH **$79,500** = **+$13,700** over loft; ETH weekly $1,810–2,000 mod faktisk HIGH **$2,546.78** = **+$546.78** over loft. D3–4 BTC HIGH $73,400 mod $65,200 (+$8,200); D5–7 BTC HIGH $79,500 mod $65,800 (+$13,700). |
| W36 | **3/6** | CN23 1 Sep after week started: BTC D1–2 LOW $76,420 under $77,000 med $580; ETH $2,383.34 under $2,400; BTC D3–4 HIGH $82,300 over $81,000 (+$1,300). |
| W37 | **4/6** | BTC D3–4 LOW $76,464 mod $76,500 (-$36), D5–7 LOW $76,046.58 mod $77,000 (-$953.42). |
| W38 | **2/6** | **Tidlig downside undervurderet:** BTC D1–2 LOW **$74,967.97** mod $77,000 (-$2,032.03); BTC D3–4 $75,064.82 mod $75,500 (-$435.18), ETH LOW under de første to intervaller. |
| W39 | **4/6** | BTC D1–2 brød **begge** grænser (LOW $80,850.22 under $81,345; HIGH $87,395.67 over $86,099), D3–4 BTC HIGH $87,278.54 over $87,155. Source freeze Monday 18:13Z, full first window straddles issue. |
| W40 | **6/6** | Alle seks fulde ISO-window-envelopes holdt. Det er ægte deskriptiv containment, ikke bevis for superior range width. Site freeze Monday 05:53Z. |
| W41 | **2/6** | **Alvorlig downside-miss:** D3–4 BTC LOW $80,393.56 mod $83,000 (-$2,606.44); ETH LOW $2,406.11 mod $2,600 (-$193.89). Weekly BTC $82k–92k actual min $80,393.56 og ETH $2,560–2,960 actual min $2,406.11: **begge weekly bands fejlede**. |
| W42 | **5/6** | Bedring, men D3–4 ETH LOW $2,318 mod $2,320 (-$2). BTC/ETH weekly bands begge holdt. |

**Totals for this one, non-canonical, non-PIT retrospective matrix:** **32/54 = 59.26%** full-ISO-window joint containment, **21/36 = 58.33%** for D3–4/D5–7 only (later windows, but still no independent source/true issue clock proof). **7/12** weekly BTC/ETH envelopes held among only the six original-source weekly-pair examples. All counts descriptive, assets/windows nonindependent. W35 is **unavailable**, not failure or success; W32 **excluded**, not silently imputed.

**Critically: original CN public scores are different measurements!** Published price-range score for W38=71.51, W39=81.85, W40=82.05, W41=49.56, W42=85.25, using **70% containment+30% Jaccard** and versioned window policy. W36/W37 public scorecards `FINAL_PUBLISHED_LEGACY` contain incomparable earlier aggregations. Weekly 8-envelope strict containment published W39 75%, W40 100%, W41 25%, W42 87.5%; don't average it with this six-window ISO retrospective. Store every series on its own named scale.

## C · Existing cheap B1 compared to CN W41 and W42 (4 asset-week rows)

**Original, stored, price-only 4W B1 baselines**, NOT same as M3's ex-post-reconstructed ATR DUMB1.5/2.0. Baseline files:
- `05_CYCLE_NAVIGATOR/range_baselines/forecasts/2026/W41.json` (W37–W40 lookback) and `.../scores/2026/W41.json`.
- `05_CYCLE_NAVIGATOR/range_baselines/forecasts/2026/W42.json` (W38–W41 lookback) and `.../scores/2026/W42.json`.

| Asset-week | CN contained? | B1 contained? | CN width/anchor | B1 width/anchor | Important caveat |
|---|---|---|---:|---:|---|
| W41 BTC | NO | NO | 11.56% | 7.30% | CN underpredicted downside by 1.857% of anchor, B1 4.742%. |
| W41 ETH | NO | NO | 14.67% | 9.22% | CN lower breach 5.643% of anchor, B1 8.620%. |
| W42 BTC | YES | NO | 11.94% | 7.30% | CN wider; B1 misses lower boundary by 2.393% of anchor. |
| W42 ETH | YES | NO | 18.13% | 8.08% | CN over twice as wide; B1 misses lower boundary by 5.259% of anchor. |

**Interpretation:** CN 2/4 joint containment vs B1 0/4 on these FOUR correlated recent asset-week cases, but achieves this partly via larger width; does not undo M3 earlier adverse DUMB comparison, does not demonstrate statistical superior sharpness, and stored B1 original publication/PIT at exact issuance still needs independent chronology proof. No composite winner or model change declared.

## D · Original Compass 12h crosscheck

Prior owner review of **all 52** matured 12h Official forecast outcomes for **18–24 Oct**: BTC **20 correct / 18 incorrect / 14 abstained**, so 20/38 = 52.63% direction **conditional on issued UP/DOWN** and 38/52=73.08% sign-prediction coverage. This result is **from matched outcome JSONs**, not original provider-first-known approved data; overlapping issue windows and same target make effective N unknown. On 21 Oct, late issued DOWN signals preceded 22 Oct downside, while 18 Oct 0/5 direction calls hit. Against price-persistence / always-DOWN / base rate, count all attempts and exact source clock. A simple same-hour observation of the 22 Oct move must not be counted as early-warning skill. A prior isolated R1 nine-forecast diagnostic found 16/16 emitted asset directions matching a cheap preceding-packet-delta sign comparator: existing `04_MARKET_LEARNING/handlekompas/research/2026-10-14__TASK2_R1_EXPLORATORY_BASELINE_AND_SIMULATION_RELEASE_v1.md`. No incremental sign-alpha established.

## E · Research/release acceptance, now owner-authorized

**Definition:** A model is `PREDICTIVELY_STRONG` only after source-admissible real original prospective issues, correct-target and -unit scoring, properly quantified uncertainty, matched simple same-clock baselines, historical false/abstain denominator, block/event-cluster uncertainty, and independent held-out multi-regime repeatable incremental improvement. Investor value is **separate**: after-cost, after-slippage capital-matched HOLD/WAIT vs false exit/reentry and missed-upside regret.

**Success is NOT:** code CI green, 100% overly broad interval, R1 guard synthetic PASS, previous-week scorecard, model disagreement, recovered X text alone, retrospective numerical training, arbitrary 30 raw overlapping rows.

**Adjudication order:** use existing Task2 #1596 R0/R1 PIT → R2 matched baselines → R3/R4 ablation/adverse controls → R5 after-cost decisions → R6/R7 display/promote. Preserve original issued SHA, provider original published/revision times, receiver first-observed, actual issue and target start, and every missing/no-forecast/ABSTAIN, including prior bad weeks. Existing [Forecast Skill Acceptance v1.0](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596#issuecomment-6394692764) remains the full specification; this paper records *actual bounded historical falsification*, not a duplicate policy or changed score family.

**Pre-merge test requirements for Supervisor/Codex:** independently review public raw frozen-source vs extracted matrix row-by-row (source Git SHA + times); recompute 54 bounds, 32 hits, 36 late-window pairs/21 hits, 12 weekly/7 hits; mutate any LOW/HIGH, flip asset, remove W34/W41, change 168h coverage, and verify exact mismatch is detected. Check all baseline examples and the different public scorecard methods; read AGENTS.md; run exact-head risk-adjusted tests and independent review, merge owner-authorized research-only add-only documentation+matrix when clean, main blob readback. Do **not** merge source authority, change seller/portfolio actions, rewrite historical freezes or claim natural live-scoring from this report.

## F · Dependencies / honesty contract

- **This report did not run a source-admitted historical R2 backtest.** It ran an auditable original-text + archived-outcome replay with known publication-time and USD-vs-USDT deficiencies. Publication class, Git SHA and all errors are explicit.
- **No original daily CLOSE path or 14/21-day quantitative BTC forward forecast** can be inferred from these weekly ranges.
- **P0 science and custody gates remain:** original provider first-known/vintage and independent recovery authority. Current user-approved receiver-first-observed source clarification is FUTURE-only with its own existing #1516 governance, not retroactive eligibility for this report.
- **No auto-reweight, model tuning, live action, new budget or automation.** Deliver findings to #1596, source #1516, Supervisor #1156 and adaptive #1157 only after evidence gate.

**Key supporting sources:** `05_CYCLE_NAVIGATOR/weekly/2026/W39..W42/CYCLE_NAVIGATOR_FORECAST_FREEZE.json`, `05_CYCLE_NAVIGATOR/published/2026/CYCLE_NAVIGATOR_{20,21,23,24,25}_X_*.md`, `03_DAILY_CAPTURE_LOGS/weekly/2026/W33..W42.json`, existing `06_RESEARCH_LAB/m3_checkpoints/2026-10-05__RL-CN-SKILL-BASELINE-003__FINAL_ADJUDICATION_v1.md`, `06_RESEARCH_LAB/m3_replay/2026-10-05__RL-CN-SKILL-BASELINE-003__reconstructed-baseline-v1.json`, `05_CYCLE_NAVIGATOR/public_scorecards/2026/W38..W42`, and Task2 [#1596](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596).
