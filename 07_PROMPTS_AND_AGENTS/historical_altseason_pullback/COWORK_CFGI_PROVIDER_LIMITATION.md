# Mandatory CFGI provider limitation for Cowork

This file is mandatory preflight context for the historical altseason/pullback research task.

## Frozen result

The CFGI v3 provider publicly documents `MARKET` as the whole-crypto-market index. The authorized MARKET-only historical gap-fill was executed once against the frozen event windows, run `32463869226`, after BTC and ETH had already been preserved. The provider returned zero MARKET rows for both frozen historical windows.

The terminal interpretation is therefore:

- `BTC` CFGI historical slices: usable only where the v3.1 no-lookahead as-of coverage marks them available.
- `ETH` CFGI historical slices: usable only where the v3.1 no-lookahead as-of coverage marks them available.
- `MARKET` CFGI historical slices: `NOT_TESTABLE_PROVIDER_UNAVAILABLE`.
- Do not fill, interpolate, forward-fill beyond the declared one-hour cadence, proxy MARKET with BTC/ETH, or infer missing MARKET values.
- Do not request or recommend another paid CFGI retry for these frozen windows.
- Analyses requiring MARKET CFGI must be reported as unsupported/not testable. Analyses that can be answered from BTC, ETH, free historical data, or prospective framework evidence may proceed, while clearly separating observed evidence from unavailable slices.

## Billing provenance

Verified cumulative actual CFGI spend before the failed MARKET-only run is 10,518 credits. Because the MARKET run failed before a durable billing artifact was written, its exact header-derived spend is unknown. For governance, use the conservative upper bound instead of inventing a number:

- conservative additional upper bound: 2,663 credits
- conservative cumulative upper bound: 13,181 credits
- hard cap: 25,000 credits
- conservative remaining lower bound: 68,588 credits
- minimum reserve: 50,000 credits

This uncertainty is a provenance fact, not a reason to block the Cowork research task.

## Research authority

All historical findings remain research-only and may be classified at most `FORWARD_TEST`. No automatic promotion, portfolio action, market-rule change, threshold change, or policy-semantic change is authorized by this package.
