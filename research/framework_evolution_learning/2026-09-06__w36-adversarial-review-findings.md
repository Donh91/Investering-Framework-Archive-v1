# W36 Adversarial Review Findings — Pre-Master Monday 2026-09-06

## Authority

Research-only. Non-canonical. No threshold changes. No portfolio or execution authority. No proxy promotion. No new collector. No parallel signal engine.

## Source

Independent Claude adversarial review of W36 using repository current-main snapshot at `1086cf9c9be59633844d3b9cffa188ac440ffb67` with evidence cutoff 2026-09-06T21:16:30Z. Current main may be newer; every consuming agent MUST prefer fresher native-owner data when available.

This file is a bounded findings archive and routing aid, not a replacement for native owner outputs.

## Core conclusion

Best-supported interpretation at the source cutoff: **H4 — deleveraging-led constructive reset; the genuine rotation test has not yet been completed.**

The existing framework stance — `Rotation Watch`, `participation is not transmission`, confirmation incomplete — was assessed as **APPROPRIATELY_CAUTIOUS**.

The most important finding is operational rather than directional:

> **Fix derivation/wiring, not thresholds.**

The review found existing owner data that was either not read, read from a stale capture, or derived incompletely. This is primarily an `OTA_CONTEXT_GAP`, not evidence that the framework needs more collectors.

## Material findings to preserve

1. **Breadth freshness:** the previously quoted 0.56 breadth print was stale versus fresher same-day owner outputs. Latest in the Claude snapshot was ~0.52. Consuming agents must always use the freshest eligible capture, not the most constructive capture.

2. **Stablecoin data existed:** fresh owner output supported approximately `7d +0.511%`, `30d +1.453%`, total ~$310.586bn. The correct classification was `OTA_CONTEXT_GAP`, not `FRAMEWORK_DATA_GAP`. The lane remained non-canonical / non-confirming and must not be used to infer deployment from supply.

3. **ETHBTC persistence was understated:** the prior 168-hour figure was a query-window cap. Owner data supported approximately **438 consecutive hourly closes / 18 settled sessions at or above 0.0300**. This is structurally constructive, but is not by itself directional rotation confirmation.

4. **Settled ETH leadership remained weak:** around the cutoff, ETH-led settled sessions were only **1/4** and **2/6**, with a negative trailing settled ETHBTC-margin slope. Structural survival above 0.0300 and directional ETH leadership must remain separate concepts.

5. **W36 temporal ordering did not match clean BTC→ETH→alts transmission.** The reconstructed sequence was closer to:

   `BTC breakout (ETH lagging) → beta breadth expansion → deleveraging → ETH + alt catch-up → decay / retest`

6. **Alt outperformance was real and robust:** cap-weighted alt performance materially exceeded BTC over the bounded window and survived top-decile removal, large-cap decomposition, and the Sep-4 pullback test. This is genuine evidence and must not be discarded merely because canonical rotation confirmation is incomplete.

7. **But the ETH link was the weak link.** On the Sep-3 breakout ETH lagged BTC; W36 ETF allocation tilted strongly toward BTC rather than ETH; settled ETH leadership was sparse. Therefore broad alt strength should not be silently relabeled as proven ETH-mediated ladder transmission.

8. **Breadth deterioration was not explained by universe churn.** Fixed-basket checks largely reproduced the decline. Rolling-window mechanics explained part, but residual deterioration in alt-minus-BTC / alt-minus-ETH relative spreads was real enough to classify as an early warning of failed transmission, not a settled failure conclusion.

9. **Leverage interpretation:** BTC looked more like an orderly deleveraging/reset than destructive distribution: OI fell far more than price damage, funding remained modest, and the Sep-3 BTC expansion was not strongly leverage-driven. ETH was more ambiguous, with signs consistent with squeeze mechanics / re-accumulating leverage rather than clean spot-led leadership.

10. **No incremental missing perspective was identified.** The review explicitly concluded `NO_INCREMENTAL_MISSING_PERSPECTIVE`. Existing owners already cover the high-value questions. The bottleneck is derivation and routing.

## Master Monday usage contract

Master Monday MUST NOT ingest this note as canonical market evidence. It should use it as a **research/adversarial interpretation layer** and then re-derive all decision-relevant facts from fresh native owners after W36 is fully settled.

For the next Master Monday run:

- Freeze W36 only after Sep-6 is fully settled.
- Read the freshest eligible breadth capture and explicitly difference out BTC/ETH before interpreting transmission.
- Derive settled ETH leadership from the hourly owner using registered definitions; do not use rolling 24h windows as substitutes.
- Recompute true ETHBTC persistence from owner history; do not inherit a query-window cap.
- Read stablecoin owner before declaring liquidity data unavailable.
- Read `btc_d_cmc` / dominance owner for Sep-6/7 before concluding whether the late-week cap-share move generalized beyond the Top100 proxy.
- Keep `structural ETHBTC survival` separate from `directional ETH leadership`.
- Keep `alt outperformance` separate from `ETH-mediated transmission`.
- Preserve `UNKNOWN` when canonical breadth or other authority-compatible evidence is absent.
- Do not change thresholds based on this review.
- Do not add a collector merely to resolve a context/derivation gap.

## Highest-value next confirmation

The most informative near-term confirmation remains:

**ETH-led settled sessions reaching roughly 3/4 (or equivalent registered persistence), with positive settled ETH−BTC relative performance and a recovering/positive trailing ETHBTC-margin slope.**

Second-order confirmation: daily dominance owner showing BTC.D decline with ETH.D improvement and persistent alt relative strength after settlement.

## Cycle Navigator relevance

CN #23 becomes genuinely scoreable only once its W36 forecast window is fully complete. Any score must use the frozen deterministic scoring method and preserve Price Range Precision as a separate category if/when that category is implemented in the production scoring path.

Do not convert descriptive proximity to a range into a hindsight-tuned score.

## Situation Room update after Claude cutoff

The Claude review treated the Sep-6 tanker-strike discovery as `DISCOVERY_UNVERIFIED`. After its cutoff, a separate Situation Room manual-review receipt verified the event against a U.S. Central Command primary source. This changes **event verification**, not market-reaction status. Event context must remain separate from a risk-off market-state inference unless a market-reaction lane independently verifies that transmission.

## Agent routing

Agents working on any of the following SHOULD read this file before proposing new collection or threshold changes:

- Master Monday
- Cycle Navigator scoring / retrospective
- Native OTA reconciliation
- rotation / breadth interpretation
- stablecoin-liquidity availability checks
- ETHBTC persistence / leadership derivations
- agent-context routing / evidence wiring audits

Agents MUST still prefer fresher current-main native-owner data over numerical values frozen in this research note.
