# L4 Catalyst / Confound Attribution Protocol v1

**Status:** PROSPECTIVE SHADOW EVALUATOR  
**Owner:** Claude OTA / external research lane  
**Canonical authority:** NONE  
**Portfolio authority:** NONE

## Role

L4 is an evaluator for pullback research, not a competing market sensor. Its job is to separate internally generated market-structure events from moves materially confounded by external catalysts before outcomes are known.

## Anti-hindsight contract

A row is prospective evidence only if `classification_recorded_at_utc < outcome_window_end_utc`. `outcome_window_end_utc` is frozen when the tag is created and may never be extended after the result is visible.

If the classification is first written after the outcome window ends, mark:

`RETROSPECTIVE_TAG_NOT_EVIDENCE`

Existing rows are append-only. Later OTA runs may add source receipts or follow-up observations but may not rewrite the original category, confidence, scheduled flag or confound status.

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

## Use in research

Candidate L1/L2b/existing market-structure features should eventually be compared separately inside `INTERNAL_CLEAN` and `EXTERNAL_CONFOUNDED` event sets. No incremental-value claim is valid merely because a feature appears before pooled pullbacks.

## Kill / quarantine conditions

- More than 60% LOW/UNKNOWN confidence over 20 tagged events -> retire or redesign.
- Any post-outcome edit of a frozen classification -> quarantine affected rows pending review.
- Fewer than 10 prospective tags in six months -> `INTENT_ONLY`.
- Taxonomy expansion without a version boundary -> invalid.

## Authority

`can_affect_canonical_state: NO`  
`can_affect_portfolio_action: NO`
