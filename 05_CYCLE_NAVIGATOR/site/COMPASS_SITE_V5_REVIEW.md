# Compass Site v5 review

## Product / iPhone
PASS by design review. NOW answers action first, then 12h / 1–3d / 5–7d, then one vertical BTC→micro risk rail. ETA stays attached to the relevant horizon or segment. No parallel card wall is introduced.

## Data / lineage
PASS by construction. `build-public.mjs` resolves `PUBLIC_LATEST_COMPASS.json`, restricts the projection path to the public Compass root, verifies content SHA-256 and Compass ID, then publishes only the sanitized projection as `data/compass.json`.

## Adversarial / failure
PASS by contract. Missing, invalid, hash-mismatched or unpublished Compass data produces `NOT_PUBLISHED`; the renderer shows a waiting state and does not infer a short-horizon call from CoinGecko, weekly CN prose or legacy live observation. SELL/de-risk is not exposed in v5.
