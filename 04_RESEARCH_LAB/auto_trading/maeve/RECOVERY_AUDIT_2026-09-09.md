# MAEVE RECOVERY AUDIT - 2026-09-09

Status: ACCEPTED AS HIGH-VALUE RESEARCH PACKAGE WITH CORRECTIONS
Scope: Provider-value-free audit summary only. Raw/normalized recovered CFGI trade values are not copied into the public control plane.

## Package received

User supplied a Claude-generated forensic recovery package containing the former public CFGI M.A.E.V.E dashboard reconstruction, normalized parent positions, fill-level data, social-post reconciliation, archive capture inventory, version timeline, source provenance and behavioral findings.

Local intake hashes verified in the ChatGPT session:
- `README.md` SHA-256 `90f048fc8ec3ee4e81d281ed38fae8390006349f9ceeb08ce497757748394bae`
- `MAEVE_LEDGER_RECOVERY.zip` SHA-256 `9770bcf968d9e03f97af7cfd0bcaaf6baad21c928d97b3b610a457dfb87343a5`
- `MAEVE_TRADES_NORMALIZED.csv` SHA-256 `532c858ba3d6f0c765419c6869f881bec278aa792108676a6d70933b08f94441`
- dashboard screenshot `IMG_6949.png` SHA-256 `e8d96bef6d181e8f8d0de4f6591d353fae9b8fe7837c3584cdda561b708a6605`

The standalone README and standalone normalized CSV are byte-identical to the copies inside the ZIP.

## Independently reproduced package facts

Using the supplied normalized files, the following headline package claims were independently reproduced:

- 432 parent positions total
- 426 closed positions and 6 open positions
- 1,073 fill rows
- 641 DCA legs, with parent `n_fills` summing exactly to 1,073
- internal fill IDs span 75 through 1151 with exactly four missing IDs: 127, 636, 1045 and 1046
- 426/426 closed positions have exit CFGI score greater than entry CFGI score
- median entry CFGI score = 17.0
- median exit CFGI score = 70.75
- zero closed parent positions have entry CFGI above 30
- site-convention win rate = 397/426 = 93.19%
- first-entry-only win rate = 286/426 = 67.14%
- USD-weighted win rate on the 209 positions with sizing data = 175/209 = 83.73%
- no-DCA first-entry win rate = 96.94%
- DCA-required first-entry win rate = 41.74%
- equal-weighted mean USD-weighted PNL on the 209 sizing-complete positions = 1.54185%
- capital-weighted PNL on those same positions = 0.76971%
- social reconciliation file contains 256 exact entry+exit-price matches, 62 Parent-ID matches and 47 unmatched posts
- all 256 exact close-result matches were posted after the ledger exit timestamp

This materially upgrades the MAEVE track from `INCOMPLETE RECONSTRUCTION` to `NEAR_COMPLETE ARCHIVED-ERA RECONSTRUCTION`, while remaining partial against later headline checkpoints that post-date available dashboard archives.

## Corrections / caveats before canonical research use

### 1. Entry-score band wording

The package headline `94.4% at CFGI 10-19` is correct only if the bin is interpreted as `10 <= score < 20`, because half-point values such as 19.5 exist. The literal interval `10 <= score <= 19` is 91.08%.

Use the explicit mathematical interval in future analysis.

### 2. Social-publication median

The supplied `SOCIAL_POST_RECONCILIATION.csv` yields a median `post_minus_exit_minutes` of `0.8` minutes for the 256 exact entry+exit-price close-result matches. The README text says `+0.7 minutes`.

Treat `0.8 min` as the reproduced CSV value unless a documented alternative rounding/calculation is supplied.

### 3. Stop-loss language

The package strongly supports that no stop-loss field or stop-triggered exit is visible in the recovered rows. It does NOT prove that proprietary MAEVE logic never contained a stop-loss mechanism.

Preferred wording:
`No stop-loss field or stop-loss exit is evidenced in the recovered ledger.`

Do not upgrade this to `MAEVE had no stop-loss anywhere` without primary implementation evidence.

### 4. Version-timeline CSV formatting defect

`MAEVE_VERSION_TIMELINE.csv` contains one malformed CSV row at the 2025-09-09 screenshot event because a comma in the evidence-strength field is not quoted. Standard CSV parsing skips that line unless permissive parsing is used.

Repair before machine ingestion. Preserve the original file hash as source evidence and create a corrected normalized derivative rather than silently rewriting the raw artifact.

### 5. `analisis_hora` look-ahead risk remains critical

The package itself correctly identifies a median ~59.5 minute lag from entry to `analisis_hora`. Until timestamp semantics are proven, impulse/volatility/volume sub-score fields must NOT be treated as clean entry-time features.

`cfgi_score_entry` is currently the cleanest recovered entry feature.

### 6. DCA and performance interpretation

The package supports a major distinction between position-level win rate and initial-signal quality. The 93.19% site-convention win rate is not equivalent to a 93.19% correct-entry rate.

Future Astra work must separately score:
- first-entry direction/quality
- DCA rescue contribution
- capital committed
- capital-weighted return
- holding time and opportunity cost
- portfolio-level drawdown/concurrency

## Research state after recovery

### Strong enough now
- entry/exit CFGI-level characterization
- DCA economics
- holding-time analysis
- asset/timeframe segmentation
- chronological version/regime segmentation
- public-post prospectivity validation
- behavioral-clone baselines using clean pre-entry variables only

### Not yet strong enough
- attribution across all ten CFGI algorithm families
- claiming the three recovered sub-scores are entry-time features
- reconstructing proprietary hidden/private MAEVE algorithms
- full-lifetime capital-weighted performance before venue sizing appears
- claiming complete coverage of the later 1,427-trade era

## Highest-value next evidence

The single highest-value addition remains the historical CFGI feature cube:

`asset x timestamp x {15m,1h,4h,1d} x 10 public algorithm families`

Once legitimately available, each MAEVE decision can be joined only to values observable at or before its frozen decision timestamp, enabling feature ablation, interaction testing, regime conditioning and interpretable behavioral cloning without look-ahead.

## Governance

This recovery is research evidence, not a live trading strategy and not a recovered proprietary algorithm.

Do not promote MAEVE-derived rules directly into execution. Use the existing AUTO_TRADING governance path:

`reconstructed evidence -> frozen hypothesis -> replay/backtest -> chronological walk-forward -> paper-forward record -> adversarial audit -> promote/revise/kill`
