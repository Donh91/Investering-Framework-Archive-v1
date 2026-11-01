# KOMPAS PRO · 14d freeze-to-outcome audit + all-history research v1

**As-of source cutoff:** 2026-10-31T07:00:00Z. **Investigator:** owner-authorized research. **Status:** EX-POST, NOT certified original-first-known/PIT, NOT an approved model change, NOT independent statistical edge. **Code:** PR #1859, \`scripts/learning/compass_rolling_14d_audit.py\`. **Owners:** Existing Official Compass Outcomes, #1553 Risk-to-Action, #1596 scientific admission, #1827 source clocks. **No new cron or Supervisor.**

## Scope and population

- 14-day replay over actual original *immutable* Official Compass freeze documents with \`issued_at_utc\` in \`[2026-10-17T07:00:00Z, 2026-10-31T07:00:00Z]\`. Never infer the issue time from the filename. PR validation has parsed **149** freezes, first-per-fixed-UTC-12h bucket **29** (NOT independent market episodes or the two scheduled Copenhagen daily slots).
- Full official history through the same cutoff: **340** freezes, **84** first-issuance-per-fixed-UTC-12h buckets. Older v1/v2 scoring contracts are not retrofitted to v3. **47 of 84** selected buckets were quarantined as legacy scoring contracts in the first validation. Shadow v2, Strategic and CN are separate contract owners: do NOT pool their slots with Official direction accuracy. These other owners remain outside this particular Official audit's denominator.
- Source BTC/ETH Hourly close-price tape checked from **2026-10-17 07:00Z to 2026-10-31 07:00Z**: 337/337 consecutive UTC hourly closes, spot quality PASS, no contradictory candle identities in the reviewed snapshot. Hourly clocks are candle OPENS; closes are OPEN+1h, not collector \`source_window_end_utc\`.
- A persisted historical freeze file + valid \`issued_at_utc\` field is NOT independent proof of first Git publication or exchange source first-seen. Verified publication chronology / legal original PIT remains UNKNOWN.
- Official issued \`NEXT_12H\` is evaluated against its **reference candle close +12h**; because reference may predate publication, every per-event row now exposes the actual *effective forward hours from issued_at*. Do NOT silently treat this as exactly 12h after issuance. The issued 1–3d is anchored to +72h and 5–7d to +168h under the current official scoring contract. Auxiliary +6/+24/+72h returns are observed paths, **not fabricated frozen forecasts**.
- First 12h UTC-block issuance is a reproducible **sensitivity reduction** for frequent event-driven reissues; it does not certify independent forecasts, purge outcome overlap or aligned local calendar slots.

## Historical market path from exact public Hourly CSV snapshots

At 17 October 07:00 UTC: BTC $81,640; ETH $2,433.27; ETH/BTC ~0.02981.
At 31 October 07:00 UTC: BTC $77,388.85; ETH $2,245.92; ETH/BTC ~0.02902.

| Quantity | 14d observed |
| --- | ---: |
| BTC close-to-close | **-5.207%** |
| ETH close-to-close | **-7.700%** |
| ETH/BTC close-to-close | **-2.650%** |
| BTC observed intrahour high, 21 Oct 17:00Z bar-close clock | **$84,898.00** |
| BTC observed intrahour low, 30 Oct 19:00Z bar-close clock | **$76,325.98** |
| Intraperiod high-to-low span | approx. **-10.10%** |

**Source day-file Git blob SHA identities** from the reviewed main checkout: 16 Oct \`127094125f712c5eed06972aaade46054cce5293\`, 17 \`8a5f675e475d537162b55cf4cf39293627824e7c\`, 18 \`0a8a66405ee90b38d8d379c5c3af82091b9fabdd\`, 19 \`8f4fdef8ff23c0c9a5dfeb2a69ec35a5ba571cbd\`, 20 \`14b69ca05ac77d0746517760e2e22cbd162b2081\`, 21 \`fc69c76b86da6c0af6ea8e2971c23d6950463024\`, 22 \`b8acc37486523519e080caca32c2c7b593ccc282\`, 23 \`beddb7dc1a6afbf25f8cc3b8e28dd6c590bff12d\`, 24 \`4141c9d77992fade862b61f05cdebc7289a234da\`, 25 \`5ff99a1f531056d77a4ddf67d5aa76cb4434dd8a\`, 26 \`9866e34b490d1684514ed31eddf35000db131ec4\`, 27 \`8cb948f024418d6be3497968f11eedc62e0f0a1d\`, 28 \`fb34cd6299b9e1a97b7a06e70f7070cf38b6eb85\`, 29 \`a7ab3bd312ef5ecc5a40ab0d3996540671afc59c\`, 30 \`3ee37647a78c7ad5705fc683a4d7d4c2dae5c284\`, 31 \`209b6efa3350a109fed348c39e91baf1ea9b148e\`. Git blobs are immutable versions; later moving main may contain different bytes. The automated audit additionally persists **SHA-256 of every included original freeze and hourly source file**.

### Daily anchor tape, BTC close returns from each 07:00 UTC reference

| Initial UTC date | BTC +24h | BTC +72h if mature |
| --- | ---: | ---: |
| 17 Oct | +0.103% | +0.206% |
| 18 Oct | +1.381% | +1.328% |
| 19 Oct | -1.261% | -0.436% |
| 20 Oct | +1.223% | +0.102% |
| 21 Oct | -0.383% | -2.438% |
| 22 Oct | -0.727% | -2.419% |
| 23 Oct | -1.346% | -2.152% |
| 24 Oct | -0.364% | -1.386% |
| 25 Oct | -0.455% | +0.462% |
| 26 Oct | -0.574% | -0.201% |
| 27 Oct | +1.503% | -1.278% |
| 28 Oct | -1.111% | -4.302% |
| 29 Oct | -1.647% | PENDING |
| 30 Oct | -1.606% | PENDING |

*This price table is independent of Kompas issuance. It is a series of retrospective time-fixed observations, not 14 frozen daily predictions.*

## Observed Official Compass behavior

First PR validation receipt from actual \`Official Compass Outcomes\` workflow (source head before later purely analytical additions): rolling 149 frozen Official issuances, 29 deduplicated 12h UTC blocks, **24 mature testable directional 12h calls, 10 correct and 14 wrong = 41.7%** descriptive direction accuracy. Four of the 29 slots abstained rather than offering a falsifiable UP/DOWN; one 12h slot was pending at cutoff. All 149 original issuance rows: **143 HOLD_WAIT, six HOLD_WAIT_DATA_DEGRADED**, and **143 ELEVATED protection states, six UNAVAILABLE**. The official risk status was therefore highly concentrated; this is not proof that HIGH/4-5 was required at every point, but it raises severity discrimination and lead-time questions.

All-history first PR validation: 340 frozen original Official issuances, 84 first-UTC12h blocks, 47 legacy-scoring quarantines, 36 mature v3 12h observations, one pending, **32 directional testable with 17 correct, 15 wrong = 53.1%** descriptive direction accuracy. Do NOT mix this all-history result with the 14-day v3-only rate as a stationary out-of-sample difference; policy, source, contract and market regimes changed.

**High-value event examples:**
- 21 Oct 07Z: BTC gained +0.839% over the following 6h but fell -0.383% at +24h and -2.438% at +72h.
- 27 Oct 07Z: BTC gained +1.503% over the next 24h, then the original 72h outcome from that clock was -1.278%. Recovery is not identical to sustained trend improvement.
- 28 Oct 07Z: BTC -1.111% after +24h, -4.302% after +72h; evaluate whether actual issued protection warnings could have escalated early. Do not invent an earlier HIGH warning from these ex-post prices.
- 29 Oct 07Z and 30 Oct 07Z: BTC next 24h -1.647% and -1.606%, respectively. Daily intrahour trading range from 29 Oct 07Z 24h window ~7.151%, indicating severe intraday volatility even where daily close-to-close returns looked smaller.

## Diagnostic research hypotheses and P0 priorities

1. **12h nowcast versus 12h true forecast:** 10/24 direction results over this 14-day sample is an audit alarm. Compare emitted expected direction with frozen preceding BTC momentum on the same clock. Record incremental hit rate only on paired clocks with present original frozen momentum. No baseline availability means UNKNOWN, not zero. Use original publication issuance vs reference-candle target effective lead, per-row.
2. **Risk severity saturation:** 143/149 ELEVATED while BTC fell 5.2% over 14d, and peak-to-trough approx. 10.1%. Test WHEN the existing official risk state changed and whether alert lead time, false alarms and subsequent MAE justify any new level. Do not infer severity 4/5 from realized trough or restore retired ETHBTC/breadth action proxies.
3. **Rebound and second-leg hazard:** compare recovered (+6h/+24h) paths with +72h outcomes and continuation/retest; use one true episode per shock, no overlapping same-cohort backtest accuracy.
4. **Breadth/ETHBTC participation:** ETH underperformed BTC by ~2.65% relative across the window. Check whether ETH/BTC and genuinely independent alt breadth actually added information to *frozen* official calls. ETHBTC and spot buy flow are not independent families. No source-qualified breadth = UNAVAILABLE.
5. **Investor utility instead of only direction:** action HOLD_WAIT persisted while price fell. For a potential new purchase, waiting could have reduced adverse entry risk, but for an existing held portfolio HOLD is NOT a realized protective exit. Without investor entry/size, actual quotes, spreads and executable decision authority, no after-cost P&L claim.
6. **Learning controls:** before any proposed weight/threshold change require >= one non-overlapping preregistered forward cohort, source first-known, matched-clock baseline, placebo/permutation, holdout calibration and independent review. Legacy contracts remain separate.

## Permanent implementation, isolated from Master Monday

In the EXISTING \`.github/workflows/compass-outcomes.yml\` hourly outcome workflow, the proposed gated release checks once per Copenhagen calendar day for an already-published 14d report and writes at most one new \`rolling_14d/daily/YYYY/MM/DD/YYYY-MM-DD_ROLLING14.json\` when due. Every Sunday, using the SAME schedule, a full-history Official snapshot is written under \`rolling_14d/all_history/YYYY/MM/DD\`. No new cron, API spending, supervisor, forecast or parallel writer. Existing main-serializing concurrency, source-hash manifests, remote commit/readback and CI tests are retained. Old reports are never rewritten. Report metadata shows no original-first-known admission and no automatic model reweighting. This only becomes operational after independent code/release review and merge of PR #1859; the draft PR alone does NOT activate the recurring job.

## Formal assessment

- Historical price path: reproducible within the hash-bound public daily CSV snapshot.
- Original Official freeze coverage: PR integration readback produced 149 rolling14 and 340 full-history; later heads must be revalidated and full file manifest inspected.
- Direction correctness: **descriptive only**, not independently verified original forecast publication timestamps and not demonstrated market edge.
- AI/model parameter change: **BLOCKED**. Keep Compass live weights and action governance unchanged; use daily calibration research flags as an investigation queue, never automatic model-control input.
- Scientific/production gate: await exact-head CI, independent Grok/Codex review of writer change and first live daily GitHub main readback before marking as LIVE.
