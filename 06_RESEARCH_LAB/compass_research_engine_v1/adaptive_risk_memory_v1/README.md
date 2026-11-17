# Adaptive Risk Memory v1 — isolated development replay

**Authority: EXPOST_DEVELOPMENT_ONLY.** Original owners #1553 and #1596. Evidence and full 2024–2026 result tables: https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1553#issuecomment-6946148163. Original phases 1–4 remain unchanged.

This directory does not add a producer, scheduler, workflow, production import, policy, dependency, source, risk level or forecast. The candidate is NOT promoted. It is a reusable control for further research. The offline CLI accepts hourly public Binance BTCUSDT spot kline JSON, for calendar 2024, 2025 or 2026 through Nov16. Obtain pages via the documented public kline endpoint: limit 1000, start UTC year boundary plus 1000h*k, end min(next page,end boundary)-1ms. Do not archive restricted data or API credentials. Original source publication and consumer delivery not verified. No raw data redistributed. CLI records exact input file SHA256 for reproducibility of future runs; this session's historical API response was not frozen.

Run `python replay.py --self-test` and `python replay.py INPUT.json 2026`. Experiment A reproduces the 14-method phase5 comparison; experiment B reproduces the nonoverlap/shock comparator. The included receipt is the actual 2026 rerun using their shared function bodies in the JS isolate. 12 bounded controls passed; 4 selected previously reported Brier scores reproduced exactly. The original receipt is preserved unchanged; it documents the JS execution, not a full Python historical rerun. The Python port is the allowed CRE format. See PORT_VALIDATION.md for the separate actual validation and remaining gaps. Training is Jan-Feb with last outcome matured strictly before Mar1; later predictions only incorporate matured prior event labels. Features use modeled 4h lag. Final outcome maturity adds H+4h. The 30d recalibration of frozen model may initially include fitted historical training predictions, not prior live-issued predictions. No real original forecast or probabilities certified. B's Jan-Feb nonoverlap 72h support is small; apparent rates have substantial uncertainty. Capped prior and models are fixed experimental choices, not tuned official weights.

## Further 2026 check (72h, Brier lower better)

|Period|N|Hits|Fixed|Rolling full|Rolling nonoverlap|Shock blend|Expert mixture|
|---|---:|---:|---:|---:|---:|---:|---:|
|Mar-Jun|477|104|0.23285|0.17939|0.18623|0.19541|0.19576|
|Jul-Oct|481|21|0.2216|0.06639|0.05798|0.07947|0.07694|
|Nov-Dec|53|24|0.248|0.28353|0.2807|0.28413|0.28541|

## Required next disposition

1. Keep fixed and rolling30 / EWMA rates as diagnostic controls, not alert probabilities. Adaptation may reduce overstatement in calm markets while missing reversals. Reject automatic shock/volatility/ensemble promotion. Preserve nulls, negative results and all methods.
2. Original #1553/#1596 owner must first bind source, true issue and delivery, frozen original outcome definition and eligible outcome maturity, with existing CRE/Task2 scientific admission. Do not score sealed Round3 prematurely; no alternative collection lane.
3. Only after source admission, freeze a forward candidate on exact code/config with fixed comparator, paired matured rows, independent event-family grouping, abstention, Brier/logloss, reliability, discrimination and lead/false-alarm utility. Report per-horizon sample, calibration error and action costs separately. No promotion based on historical score or green tests alone. No live/threshold/weight/portfolio changes or new agent. No merge before normal independent review.
