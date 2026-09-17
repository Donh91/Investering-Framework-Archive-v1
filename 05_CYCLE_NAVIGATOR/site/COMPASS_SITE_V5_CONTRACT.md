# Cycle Navigator Compass Site v5

## Public authority split

- NOW and short-horizon navigation are rendered only from `data/compass.json`, which is a hash-verified copy of the official public Compass projection.
- Weekly Cycle Navigator remains the frozen weekly/cycle outlook and historical scoring authority.
- The browser does not synthesize a Compass call from prices, weekly prose, or legacy Handlekompas state.
- Missing or invalid Compass data fails closed to a public waiting state.

## Investor-facing output

NOW may show only the amount of Compass detail that improves the investor decision. The default v5 surface shows:

1. current action and market summary;
2. 12h, 1–3d and 5–7d paths with ETA;
3. BTC → ETH → large caps → mid caps → small caps → microcaps status, reason and ETA;
4. last Compass issuance, time to next daily freeze, and next meaningful-change window.

SELL/de-risk presentation is intentionally not promoted in this first public Compass binding. If an upstream action contains de-risk/exit semantics, v5 conservatively renders HOLD rather than inventing public sell guidance. A later change may expose SELL only after its prospective learning/governance lane is approved.

## Language

Public copy uses `Market Compass` / `Compass`, never `Handlekompas`, internal workflow names, thresholds, provider names, hashes or private evidence mappings.
