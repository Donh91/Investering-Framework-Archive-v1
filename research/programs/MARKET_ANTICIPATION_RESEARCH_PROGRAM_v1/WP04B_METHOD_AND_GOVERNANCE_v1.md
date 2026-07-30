# MAR-WP04B — Prospective Trigger Addendum

## Decision

`COMPLETE_TRIGGER_LOGIC_FROZEN`

WP04B closes the trigger-definition gap identified by WP04A. It does not enumerate history and does not inspect outcomes.

## Design principle

Rules are scale-adaptive and source-aware. Macro and leverage states use robust trailing median/MAD standardization with fixed windows and fixed cutoffs. This avoids choosing raw-value thresholds after seeing event history while preserving comparability across regimes.

## Macro-to-crypto chain

The macro state requires at least two of three stress components to remain active for two consecutive eligible publication days: stronger USD, higher rates and elevated volatility. Crypto transmission must then occur within three settled crypto days through a BTC lower-tail daily return and negative ETH/BTC daily return. Breadth is confirmation only; its absence cannot fabricate or veto a trigger.

The event freezes at the first settled crypto row satisfying transmission after the macro state qualifies. The cluster resets only after five eligible days without active macro stress or transmission.

## Leverage-to-spot chain

The leverage state requires extreme funding behavior and an extreme four-hour OI transition in the same or adjacent settled hours. Taker flow is optional confirmation. Spot transmission requires a robust-z extreme four-hour BTC or ETH move in the deleveraging direction within four settled hours.

The event freezes at the first common settled UTC hour satisfying transmission. The cluster resets only after funding and OI normalize for twelve consecutive eligible hours.

## Availability and lineage

A row is eligible only when the owner timestamp, publication or exchange timestamp, retrieval timestamp, method version and source identity are retained. No forward fill, interpolation or post-freeze source call is allowed. Missing breadth is `UNAVAILABLE`, not neutral. Missing trigger inputs make the candidate `UNKNOWN` and non-enumerable.

## Historical boundary

The addendum becomes effective at its issue creation time. Historical enumeration may occur only in the next work package and must apply this exact contract unchanged. Any modification requires a new version before looking at resulting event counts.

## Governance

No forward returns, hit rates, drawdowns, economic labels, ranking, model weights, framework promotion, final-holdout access or portfolio action are authorized by WP04B.
