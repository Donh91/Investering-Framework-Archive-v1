# Breadth Universe QA — Final Targeted Gap-Fill

## Verdict

```yaml
mechanical_filter_execution: PASS
membership_hash_reproduction: PASS
sidecar_materialization: PASS
framework_universe_acceptance: PARTIAL_UNIVERSE_CONTAMINATION
absolute_gate_authority: SUSPENDED_PENDING_CLEAN_RERUN
longitudinal_transition_authority: NOT_AUTHORIZED
DCR_extension_acceptance: PARTIAL_NOT_PASS
```

The supplied hash is internally consistent with the supplied 90 included IDs. The problem is not SHA-256 execution. The problem is the economic universe represented by those IDs.

## Registry intent versus observed sidecar

The source plan requires local executable filtering of registry-listed stablecoins, wrapped/staking assets and tokenized-asset proxies. The supplied sidecar nevertheless includes multiple obvious cash-like, stable-value or tokenized fund/credit rows.

Conservative candidate exclusion set observed directly in the supplied sidecar:

```yaml
- figure-heloc
- global-dollar
- hashnote-usyc
- blackrock-usd-institutional-digital-liquidity-fund
- ondo-us-dollar-yield
- ripple-usd
- falcon-finance
- bfusd
- usdgo
- united-stables
- blockchain-capital
- spiko-amundi-overnight-swap-fund-eur
- eutbl
- superstate-short-duration-us-government-securities-fund-ustb
- janus-henderson-anemoy-treasury-fund
- janus-henderson-anemoy-aaa-clo-fund
- gho
- ylds
- usual-usd
- usx
```

These twenty rows consist, from the sidecar classifications, of 1 advancer, 3 decliners and 16 unchanged rows.

## Materiality

Supplied universe:

```yaml
included: 90
advancers: 26
decliners: 45
unchanged: 19
advance_ratio: 28.8889_PERCENT
gate_35: false
```

Illustrative conservative removal of the twenty candidate non-risk rows:

```yaml
included: 70
advancers: 25
decliners: 42
unchanged: 3
illustrative_advance_ratio: 35.7143_PERCENT
illustrative_gate_35: true
```

This is not promoted as the corrected canonical breadth because the exclusion registry must first be formally patched and the hash recomputed. It demonstrates that the contamination is decision-material: the 35% gate can flip.

## Cause

The current v1 registry contains a finite exact ID/symbol list and narrow name tokens. It does not yet cover the newer stable-value and tokenized-fund constituents visible in the current CoinGecko top-100 universe. The collector followed the literal list, but the list no longer fully implements the stated economic exclusion intent.

## Required repair

1. Patch the local exclusion registry with the reviewed exact IDs/symbols for current stablecoins and tokenized-asset proxies.
2. Preserve a versioned filter ID; do not silently change v1 historical membership.
3. Rerun the same frozen source rows if available, otherwise fetch a fresh two-page owner snapshot and label it with its own timestamp.
4. Return new constituent and exclusion sidecars, membership hash and gates.
5. Keep both v1 and corrected-universe results for calibration; do not overwrite the original evidence.

Until repaired, the supplied 28.9% reading is retained as `DIAGNOSTIC_CONTAMINATED_UNIVERSE_ONLY` and cannot close the final breadth gate.