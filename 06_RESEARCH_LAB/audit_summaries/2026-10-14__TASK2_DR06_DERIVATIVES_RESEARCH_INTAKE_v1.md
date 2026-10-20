# Task 2 · Research 06 — Derivatives, leverage and cross-venue liquidity stress

**Intake:** 2026-10-14 · **Authority:** RESEARCH_ONLY, SECONDARY_REPORT, NO PIT ADMISSION OR TRADING AUTHORITY. **Pinned public main at intake:** `78fa73939e9df1ae3a783a14d65b6ebd44b3b87e`.

This is a **versioned addendum** to DR01–DR05; it does not replace the existing Task 2 R0–R7 handoff or DR05 negative-evidence intake. Original source: user-supplied **9-page** PDF *Derivativer, Gearede Positioner og Tværstedet Likviditetsstress*, SHA-256 `6aae0656031eb8bee5151009e27e08b8359921978e88a3bd01134bf5058a1b90`. Only public-safe research commentary is committed; full PDF, restricted provider records and private user data remain outside the public control plane.

## Key result (source-derived, not an independently reproduced simulation)

The report's executive scientific position on p. 1 and pp. 8–9 is **NO ESTABLISHED INCREMENTAL PREDICTIVE OR AFTER-COST ACTION EDGE** for derivatives/liquidity relative to price/volatility/volume controls. OI, funding, basis, liquidations and order-book depth are plausible *risk state* inputs; seeing contemporaneous price stress is NOT pre-event forecasting. No paper/external vendor's examples should be misrepresented as original framework PIT outcomes.

**Most promising conditional hypothesis:** price/volatility matched periods with high or rising leverage **plus deteriorating spot participation and/or liquidity depth** may have different future downside distributions versus price/volatility alone. Test same event families, same first-known clocks, same eligible observation population and compare calibration + OOS log loss/Brier, lead-versus-false-alarm burden, and finally after-cost HOLD (only when action evidence is admitted).

## Source-critical corrections / unresolved defects

1. **Not a completed inventory.** Sections B–C list source *categories* (Binance, OKX, Bybit, Deribit, Glassnode, etc.), but provide **no reproducible row-level dataset census** by exact source path/hash, instrument, date interval, coverage, gaps, collection provenance, first-known or vendor vintage. External vendors' general historical availability is not proof of availability in the user's restricted archive.
2. **Twenty experiments claimed, only six examples actually specified.** Section N (PDF p. 8) calls them "Top 20", writes Exp-1 through Exp-6, then an ellipsis. **Exp-7..Exp-20 are UNKNOWN / NOT SPECIFIED**, not executable tasks, and must not be invented or marked registered. Exp-1's source-labeled `READY_NOW` lacks an immutable verified input binding and is **NOT independently ready under Task 2**.
3. **Hypothesis ID collisions.** OI section H5 and Funding section H5–H7 reuse numbers; do not use bare `H5` as an immutable unique hypothesis ID. Keep discipline-local names until reconciled by existing owner.
4. **Model-count inconsistency.** Section L says "nine" comparative models but lists A–J plus K/L (12 named arms). This is a draft comparator menu, **not an executed 12-arm tournament**.
5. **Report literature is primarily context.** Generic examples from trading education/media and market-event illustrations cannot establish chronologically knowable forecast signals. Numerous bracketed `【16†...】` citations are not directly reproducible private source receipts. Source report pp. 1–2 may overstate `RAW_VERIFIED` / `HASH_VERIFIED`; require actual bound objects.
6. **Funding temporal semantics:** predicted/indicated funding vs realized/settled funding are distinct fields, with distinct first-known and revision times. No not-yet-settled realized funding can be replayed into an earlier decision. Normalize inverse USD/coin open-interest units, historical symbol rollover, venue outages and venue clock skew; don't use post hoc aligned crosses.
7. **Design scope:** a claimed stress precursor must precede the first causal price deterioration on a common decision clock. Liquidation bursts *after* a price break are amplifiers, not early warning. Check false positives during healthy rising-market regimes (report p. 3).

## Six concretely described experiment sketches (PDF p. 8)

| Report ID | Proposed comparison and horizon | Report readiness | Task 2 interpretation |
| --- | --- | --- | --- |
| Exp-1 | 4h OI change vs price-only, 24h price | `READY_NOW` (source claim) | **BLOCKED pending exact dataset/hash/PIT proof** |
| Exp-2 | Funding persistence vs price/ATR, 3d | Unspecified | Design-only; realized/forecast funding clock unresolved |
| Exp-3 | Spot/perp basis divergence vs price+vol, 12h | Unspecified | Design-only; synchronized venue/vintage unavailable here |
| Exp-4 | Breadth + funding vs breadth-only, 24h crash | Unspecified | Design-only; keep DR05 old broad alt-tail null |
| Exp-5 | Order-book depth withdrawal vs volatility, 1h | Unspecified | Design-only; snapshot continuity missing |
| Exp-6 | Earlier executed liquidations vs vol, outcome not specified | Unspecified | Design-only; execution-event first-known must be proven |

**No other fourteen experiments are defined in this source.** This intake preserves the gap rather than fabricating entries or declaring them ready.

## Task 2 routing, gated next work

**P0 — Existing owner action:** bind a derivatives/liquidity **data census**, with `provider | venue | instrument | market | source path | immutable SHA | capture clock | provider first-known | vintage | cadence | coverage | gap | completeness/PIT class`. Compare to existing authorized private source registry; never leak restricted rows into the public control plane. This is a coverage task, not a collector launch.

**P1 — Negative-control tournament:** use the existing T5 event-family compiler and the DR05 `T5-OI-FUNDING`, `T5-SPOT-DERIV-DIV`, `T5-DEPTH` and `T5-FALSE-ALARM` owner work packets. Keep price+volatility and price+momentum+volume as strong baselines; test single *conditional* feature families only when source clocks and event N permit. Report both failure and success, with prospective sealed holdout later.

**P2 — Microstructure:** if valid PIT coverage exists, compare OI/funding and spot/perp divergence; distinguish vulnerability state from trigger and post-trigger liquidation amplifier. Do not call market structure or derivative features validated by this PDF. BlockHorizon is slower regime context, not a 1h crash sensor.

**P3 — Investor wealth:** partial trim/re-entry after costs, missed upside, slippage, failed fills, microcap liquidity, funding and HOLD are *not* eligible until information and execution gates pass. No current M6 historical retro-label, trading rule, production Kompas weight, scheduled task, new engine or paid data subscription changes.

**Owner:** original Task 2 R0–R7 handoff + existing EDGE Governor #1530, Compass Risk-to-Action #1553 and Task 1.5 #1596. Read DR05 source intake first for the earlier finished no-edge nulls; avoid opening a competing cross-repo scientific authority.

**Forward research:** report pp. 8–9 recommends small preregistered conditional signal combinations and genuinely independent event families. Those are hypotheses only; the next research should ideally also compare AI versus simple mechanical rules on the exact same admitted chronology and after-cost outcomes.
