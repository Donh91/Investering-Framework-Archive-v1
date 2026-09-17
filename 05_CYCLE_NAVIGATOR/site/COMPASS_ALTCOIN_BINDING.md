# Compass altcoin public binding

The public site consumes `CYCLE_ALTCOINS_3_8W` from the canonical `PUBLIC_COMPASS_PROJECTION_v1` alongside `NEXT_12H`, `NEXT_1_3D`, and `NEXT_5_7D`.

Public hierarchy:
1. Market Compass = current whole-market action and short horizons.
2. Altcoin Action = canonical altcoin posture and 3–8 week state/window.
3. Capital Rotation = BTC → ETH → Large → Mid → Small → Micro status and ETA.
4. Weekly Cycle Navigator remains the frozen weekly outlook and is never rewritten by Compass.

The site does not synthesize an altcoin signal. Missing canonical altcoin evidence fails the release validator when Compass data status is OK. Public SELL remains intentionally suppressed in this release; de-risk/exit upstream states are rendered conservatively as HOLD until the prospective sell-learning lane is separately approved.
