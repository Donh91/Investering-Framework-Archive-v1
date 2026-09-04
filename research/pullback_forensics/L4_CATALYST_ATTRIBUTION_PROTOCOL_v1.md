# L4 Catalyst / Confound Attribution Protocol v1

**Status:** PROSPECTIVE SHADOW EVALUATOR / NATIVE OWNER MIGRATION FAIL-CLOSED  
**Historical owner:** Claude OTA / external research lane  
**Recurring operator after 2026-09-04:** NONE_EXTERNAL; Native OTA readback consumes native catalyst discovery context  
**Native L4 tag owner:** NOT_YET_FROZEN  
**Canonical authority:** NONE  
**Portfolio authority:** NONE

## 2026-09-04 native migration addendum

The historical `Claude OTA / external research lane` owner designation no longer requires recurring Claude OTA pings.

Native framework infrastructure now supplies the recurring context that Claude OTA was expected to inspect:

- `03_DAILY_CAPTURE_LOGS/catalyst_overlay/situation_room/` provides prospective Situation Room discovery and primary-source verification;
- `03_DAILY_CAPTURE_LOGS/pullback_forensics/` provides the native forensic research context;
- `04_MARKET_LEARNING/ota_native/` provides deterministic readback/reconciliation after production activation.

This **does not** pretend that full L4 tagging is solved. Until a native producer freezes every required field and outcome window prospectively, L4 evidence-row production remains fail-closed. Native OTA reports the bridge as:

`PARTIAL_NATIVE_DISCOVERY_CONTEXT_NOT_FULL_L4_ATTRIBUTION_OWNER`

External Claude remains allowed as an on-demand challenger/auditor, but is no longer the required scheduled operator. An external model may not create retrospective L4 evidence from a headline discovered after the outcome window.

## Role

L4 is an evaluator for pullback research, not a competing market sensor. Its job is to separate internally generated market-structure events from moves materially confounded by external catalysts before outcomes are known.

## Anti-hindsight contract

A row is prospective evidence only if `classification_recorded_at_utc < outcome_window_end_utc`. `outcome_window_end_utc` is frozen when the tag is created and may never be extended after the result is visible.

If the classification is first written after the outcome window ends, mark:

`RETROSPECTIVE_TAG_NOT_EVIDENCE`

Existing rows are append-only. Later native or external research runs may add source receipts or follow-up observations but may not rewrite the original category, confidence, scheduled flag or confound status.

## Frozen taxonomy

- `MARKET_INTERNAL`
- `SCHEDULED_MACRO`
- `UNSCHEDULED_MACRO_GEOPOLITICAL`
- `CRYPTO_REGULATORY`
- `ETF_FLOW_OR_POLICY`
- `EXCHANGE_OR_MARKET_INFRASTRUCTURE`
- `SECURITY_HACK_EXPLOIT`
- `LARGE_ENTITY_TREASURY_OR_FLOW`
- `PROJECT_SPECIFIC`
- `MIXED`
- `UNKNOWN`

`UNKNOWN` and `MIXED` are valid outcomes and must not be forced into a cleaner story.

## Source hierarchy

1. official government / central bank / regulator
2. exchange / issuer / project primary source
3. established financial media / wire service
4. high-quality secondary research
5. social media as lead only, never final proof

For every source preserve publication timestamp, retrieval timestamp, source tier and whether the source is direct or derived.

## Temporal causality

Do not assign a catalyst because a headline and price move occurred on the same day. Record whether the market move began before the alleged event. If it did, the event cannot be claimed as the initiating cause; classification must reflect that uncertainty.

## Scheduled-event rule

`scheduled` must be resolved against a calendar frozen before the observation window. It is a lookup, not a retrospective judgement.

## Required fields

- `event_id`
- `event_timestamp_utc`
- `publication_timestamp_utc`
- `classification_recorded_at_utc`
- `outcome_window_end_utc`
- `category`
- `scheduled`
- `headline_summary`
- `primary_source`
- `source_tier`
- `confidence` (`HIGH|MEDIUM|LOW|UNKNOWN`)
- `market_move_started_before_event`
- `market_move_accelerated_after_event`
- `affected_assets`
- `confound_status` (`INTERNAL_CLEAN|EXTERNAL_CONFOUNDED|MIXED|UNKNOWN`)
- `notes`

## Native emission gate

A native producer may emit an L4 prospective evidence row only when all required fields above are materially present and the outcome window was frozen before the outcome is visible.

Situation Room `DISCOVERY_UNVERIFIED` items are discovery only and never qualify. A primary-source verified event is still insufficient if the move-before/move-after comparison or frozen outcome window is absent.

Missing required fields -> `L4_NOT_EMITTED_INSUFFICIENT_PROSPECTIVE_FIELDS`, not an inferred clean/internal event.

## Use in research

Candidate L1/L2b/existing market-structure features should eventually be compared separately inside `INTERNAL_CLEAN` and `EXTERNAL_CONFOUNDED` event sets. No incremental-value claim is valid merely because a feature appears before pooled pullbacks.

## Kill / quarantine conditions

- More than 60% LOW/UNKNOWN confidence over 20 tagged events -> retire or redesign.
- Any post-outcome edit of a frozen classification -> quarantine affected rows pending review.
- Fewer than 10 prospective tags in six months -> `INTENT_ONLY`.
- Taxonomy expansion without a version boundary -> invalid.
- Any native migration that manufactures rows from pre-migration headlines -> quarantine and revert to fail-closed.

## Authority

`can_affect_canonical_state: NO`  
`can_affect_portfolio_action: NO`