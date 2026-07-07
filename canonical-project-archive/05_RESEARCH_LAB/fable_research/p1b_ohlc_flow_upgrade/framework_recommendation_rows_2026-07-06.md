# FRAMEWORK RECOMMENDATION ROWS — P1b EXECUTED (E5-OHLC / E3-FULL / E8-FULL)

Non-binding. Requires ChatGPT ratification. Sources: FMP composite OHLC (not Binance primary) + Farside ETF flows 2024-2026 (sum-verified).

## FC-E5-OHLC — HYBRID GATE, TRUE OHLC (retest of hard-death ratification)
- Ranking under TRUE close-trigger: binary 50 deaths / 24 false vs hybrid-h1.0 28/16. Under WICK-trigger (intraday low): binary 83 / hybrid-h1.0 53. **Hybrid beats binary under BOTH triggers — ranking NOT reversed by wicks.**
- 59.0K check: at current true-ATR14 (~2339.7), 59.0K sits only 0.171 ATR below the 59.4K shelf — i.e. a TIGHT hard-death, closer to the soft-breach than the 0.5-1.0 ATR band the sim found effective. Because h=0.5 vs h=1.0 gave near-identical death counts (parameter second-order) AND the "2 consecutive closes <59.4K" leg carries most of the work, 59.0K remains DEFENSIBLE — but governance should read it as "1 clear close below shelf / 2 consecutive at shelf," not a wide buffer.
- Verdict: SUPPORTED (v0.2 hybrid holds under true OHLC). freeze: KEEP 59.0K hard-death ratification; note true-ATR tightness. Confidence: MEDIUM->MEDIUM-HIGH (now OHLC-based). What would change my mind: a longer OHLC sample reversing wick-death ranking (did not occur here).

## FC-E3-FULL — CLOSE-PERSISTENCE, OHLC + FLOW-CONDITIONED (ETF-era only)
- True-OHLC whipsaw (intraday low hits stop) pushes hit-rates BELOW P1 close-only: ETF-era N1/N2/N3 = 0.344/0.44/0.409. Close-only P1 understated whipsaw.
- **KEY governance question answered — "does 2/3-close persistence gain value only when flow improves?" ANSWER: NO, the opposite.** Flow-NEGATIVE: N1/N2/N3 = 0.444/0.5/0.667 (n=9); flow-NONNEG: 0.455/0.556/0.375 (n=11); flow-IMPROVING: 0.167/0.25/0.25 (n=12). The flow-IMPROVING subset — where the doctrine predicts most value — has the WORST reclaim hit-rates.
- Verdict: NOT SUPPORTED as price edge, even flow-conditioned. The doctrine's stated rationale (wait for flow confirmation) receives no empirical support and may be backwards. CAVEAT: cells tiny (9-12 events), ETF-era only, "IMPROVING" is one operationalization — directional, not freezable.
- freeze: NO. keep current rule: YES as governance discipline only. Language: continue banning "historically proven"; ADD "flow-conditioning did not rescue the edge." Confidence: MEDIUM (small cells). What would change my mind: larger multi-cycle OHLC+flow sample where flow-improving reclaims outperform.

## FC-E8-FULL — FNP COST, FLOW-CONDITIONED (verdict basis METER_B)
- Overall METER_B median 7.8% [CI 6.6-10.3%], p25/p75/p90 = 6.7/10.0/11.8%, FN 1/13. Flow-conditioned: negative-recovery median 7.8% vs nonneg/pos 7.1%.
- Verdict: SUPPORTED. **~9% [7-12] prior HOLDS** — median 7.8% sits inside the band, CI contains 9%, and negative-flow recoveries do NOT cost less (7.8%), so no reduction is justified (respects governance no-reduction rule). 
- freeze: KEEP ~9% [7-12] prior, p90 ~12%, ledger-only. Do NOT reduce. Confidence: MEDIUM (n=11 entries). What would change my mind: larger flow-positive sample showing systematically lower cost.

## FINAL P1b TABLE
| Rule/component | Gov status | P1b evidence | Recommendation | Conf | Layer | Ratify? | CustomGPT direct? |
|---|---|---|---|---|---|---|---|
| v0.2 hybrid integrity | ratified | SUPPORTED on true OHLC; wick no-reverse (E5-OHLC) | keep; upgrade confidence | MED-HIGH | LEDGER/GOV | confirm | NO |
| 59.0K hard-death | ratified close-only | OHLC retest: defensible but tight (0.17 trueATR) | keep; annotate tightness | MED-HIGH | GOV | confirm | NO |
| 2/3-close doctrine | discipline, unproven | NOT SUPPORTED even flow-conditioned (E3-FULL) | keep discipline; strengthen language ban | MED | GOV+LIVE lang | NO | NO |
| FNP ~9%[7-12] prior | ratified prior | HOLDS (E8-FULL 7.8% median, CI incl 9%) | keep; do not reduce | MED | LEDGER | NO | NO |
| leverage thresholds | UNDECIDED | DATA-CONSTRAINED (no funding/OI) | do not freeze | LOW | SHADOW | pending data | NO |
| ETHBTC persistence | UNDECIDED | not tested (no ETH data) | P2 | LOW | SHADOW | pending data | NO |
