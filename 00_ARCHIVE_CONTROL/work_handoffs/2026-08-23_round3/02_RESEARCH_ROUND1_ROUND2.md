# Claude Opus research record — Round 1 + Round 2

## Round 1
Claude Opus completed a large adversarial historical research package.

Reported scope:
- 46 objective pullback episodes, 45 in 2020–2021 and 1 in 2025–2026 under the frozen V0 catalogue.
- 45 matched continuation controls.
- 25,506 hourly aggregate rows.
- 1,944 hypotheses/transformations.
- 63 executable trim/reload configurations.
- 16 reload policies.

Key Round-1 results:
1. The strongest apparent free Fear & Greed signal was a control-design artefact. Config-literal controls produced AUC 0.984 with a flat lead profile; structurally matched time-calipered controls reduced it to 0.584. BH-FDR survivors fell from 118 to 1.
2. Breadth confirmed moves rather than leading them. No tested breadth feature produced a sustained actionable precursor; e.g. `breadth_6h` was ~0.642 before and ~0.936 after the top.
3. No trim/reload rule beat HOLD in the relevant 2020–2021 altseason slice. Apparent aggregate uplift was driven by the single 2025–2026 bearish window and exposure reduction rather than timing skill.
4. All 16 reload policies lost tokens with trim point fixed; best was about -0.60% with CI touching zero, and false/early reload remained substantial.
5. Family-wise selection tests rejected the apparent best cells: max-statistic permutation p≈0.250 and representation-family p≈0.532.
6. 0 FORWARD_TEST candidates. Several candidates were DESTROYED/FRAGILE; only an OBSERVE-level placebo-behaving item remained.

Round-1 methodological lessons:
- Flat lead profiles are a diagnostic for regime/calendar label leakage rather than true precursor information.
- Delay-monotonicity is a falsification test: if an apparent timing strategy improves when execution is delayed, it is likely exposure selection rather than timing edge.
- Many price/volume/breadth transforms are not independent information dimensions; they are alternate views of the same tape.

## Round 2
Round 2 was launched specifically because Round 1 could not access the per-asset bulk panel. The exact original `alt_hourly_panel.csv.gz` was recovered from GitHub Actions and byte-verified.

Verified panel facts:
- 851,882 per-asset hourly rows.
- 35 symbols.
- 25,506 distinct hours.
- LOW / MID / HIGH contemporaneous liquidity-cohort proxy.
- 46 pullback anchors + 45 matched controls = 91 inferential event units.
- SHA-256: `c55c37aa7038f7cd412267bfb8702ebbaf4eabce8db3a76df244bc25de563118`.
- Source free-stage run: `32462841592`.
- Source artifact id: `9439933916`.

Round-2 mandatory questions and answers:
1. Hidden per-asset/cohort precursor? NO. 52/700 symbol cells and 4/48 cohort cells met naive broad-window criteria, but permutation-null medians were 42 and 1. Family-wise p=0.339 and 0.219. Zero corrected survivors. In actionable T−24…T−1, 5 symbol cells met the naive criterion versus null median 12.
2. Any liquidity cohort surviving sustained >=3h, AUC>=0.65 after robustness/multiplicity? NO. Four naive cells occurred only far before the actionable window and none survived correction. Actionable window: 0/48.
3. Does “breadth confirms, not leads” survive? YES, unchanged and extended to per-asset, cohort and leader/laggard views. Top-5 concentration/narrowing was weakest before the top and strong after it.
4. Does trim/reload still lose to HOLD per asset/cohort? YES, more strongly. 17,578 roundtrips; 0/11 policies and 0/3 cohorts beat HOLD. Only 4/35 symbols were nominally positive and all CIs crossed zero. Best policy about -0.351%, CI [-0.455,-0.212].
5. Was aggregate null a composition artefact? NO. Panel reproduced Round-1 aggregate at r=1.000000. Across 42 tested universes, zero actionable LEADS.
6. Alternative episode definition worth separate label research? YES, V2 only as `RESEARCH_LABEL_CANDIDATE_ONLY`: current trigger, close at 0.75 recovery OR 336h, whichever first. It preserved ~95.7% of frozen catalogue and materially improved modern-era episode availability. It was NOT used to rescore old findings.
7. Important discovery: adjacent rolling-hour persistence is badly dependent. Random labels across the 700-cell family produced median longest runs of ~13h and median 42 criterion-meeting cells. A raw “3 consecutive hours” rule is therefore not a valid independent confirmation criterion.
8. FORWARD_TEST nominations: 0.

## Structural Round-2 interpretation
Median episode damage involved ~97.1% of assets falling; in 11/46 episodes all assets fell. The common market factor became highly discriminative only after the top (~0.894 AUC), while idiosyncratic structure stayed weak (~0.60). This supports the interpretation that these pullbacks are near-total common-factor events and explains why aggregate structure was close to a sufficient statistic rather than a lossy summary.

## Terminal conclusion
The broad historical `price / volume / taker-share` precursor-mining lane is closed for now. `HOLD` remains the undefeated benchmark under tested trim/reload constraints. This does NOT invalidate the broader framework, Master Monday, Cycle Navigator or prospective research layers. It only says the tested historical pullback-timing features did not prove robust incremental actionable edge.