# Compass Site v5 release checks

Required before merge:

```sh
node 05_CYCLE_NAVIGATOR/site/validate-v2.mjs
node 05_CYCLE_NAVIGATOR/site/build-public.mjs
node 05_CYCLE_NAVIGATOR/site/validate-compass-site-v5.mjs
node 05_CYCLE_NAVIGATOR/site/build-score-bundle.mjs
node 05_CYCLE_NAVIGATOR/site/build-live-observation.mjs
node 05_CYCLE_NAVIGATOR/site/validate-compass-site-v5.mjs
```

The second v5 validation is intentional: legacy bounded live-observation generation must not displace the official Compass renderer or mutate `data/compass.json`.
