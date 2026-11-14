# L02 | Wallet quality, trader role, cohort survival and public attention
Question: Does early independent wallet behavior add feasible forward edge after full losers, real source clocks and copy delay?
Original owners: S2 Wallet Skill #88; S4 launch #120; S7 attention and original CLEAN_G3 (#1134).

Actual source audit:
- Wallet Alpha in src/skill-metrics.ts lines 204-369 requires matching 30d/90d PnL and 30d position page; positive realized PnL contributes 35% profitability, 35% consistency, 20% quality, 10% activity. Caps at 39 when 30d realised <=0 and at 49 when 90d <=0, 69 after earlier 60d loss.
- Positive profit concentration is measured as largest realized winning position / sum of positive realized position profits. Only a fetched page of positions is analyzed; missing positions, competing accounting modes and transfers can bias representative conclusions. This is not prospective copy-trade ROI.
- Wallet Style uses 7d/30d summary and position page and labels trade frequency and profitability; no direct hold-time or identity inference.
- Smart-money leaderboard ranks solely a user-supplied 1–10 address set, and its relative rank changes with candidate set. Not a global cohort or an absolute alpha score.
- First Buyers API's current hold/sell status cannot be used as historical t0 state. Rebuild cohort from native first-tradable event with first-machine-seen, actor identity, all sellers and failures, and post-venue migration reconciliation.
- KOL timeline buckets and smart-money cohort labels do not identify individual transactions or independent beneficial owners.

Original experiment, no new engine:
E1 Freeze eligible independent public wallets with completed pre-cutoff history and complete loser denominator. Separate CREATOR_OPERATOR vs unrelated TRADER_SKILL, no creator allocation PnL in independent trader claim. Follow self-initiated new entries only; measure net after-cost realistic latency and whole exits against matched same-chain source/age/market-cap/liquidity controls, at 15m/1h/6h/24h/72h/7d. Wallet #88 minimum prospective qualification: 30 entries, 10 reproducible realized exits, independent cases; still insufficient for confident causality if cohorts overlap.
E2 Frozen first10/50 cohort on first complete post-activation Pons first-known case; separately classify funded independent buyer, CEX/router, transfers and common-source unknown. Observe retention and first-sale latency without retrospective current-status leak. Existing #120 source P0 takes precedence.
E3 Public-visibility decay challenger: pre-/post-publication wallets, adjust for newly-available lookahead, latency and changes in market regime. Correlational result not causation.
Design-only invention: EXECUTABLE_COPY_WINDOW = qualified first-seen-to-feasible-exit interval, with actual feasible notional and source-clock censoring. Existing Wallet Alpha owner must preregister and measure incremental lift.
Falsifiers: apparent edge vanishes after one-hit concentration, realized-only survivors, first seen too late, creator distributions, independent duplicate correction, or slippage/full exit.
Evidence: https://github.com/birdeye-so/birdeye_cli/blob/2dcbd14cad32bcbb57f8d0c0c766d8c496597413/src/skill-metrics.ts#L204-L369 and #L372-L489, official First Buyers blog https://birdeye.so/data-api/blog/detail/new-api-token-first-buyers-identify-the-earliest-buyers-of-any-solana-token .
Source QA verified, future economic edge UNTESTED.
