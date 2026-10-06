# EDGE-001 Prospective Primitive Owner Binding v1

Status: FROZEN_OWNER_BINDING / COLLECTION_PARTIAL
Date: 2026-10-07
Authority: RESEARCH_ONLY / ZERO_LIVE_ACTION_AUTHORITY

## Principle

The A0-A3 ablation may only consume point-in-time fields already captured by legitimate owners. July thresholds are not imported. Missing owner semantics produce UNKNOWN, not a substitute.

## Primary opportunity owner

M6 Lane C remains primary. Eligible primary warnings are ELEVATED, HIGH, CONFIRMED from Official Daily Compass protection_tracker with data_quality=OK. BUILDING remains watch/control only.

Outcome owner: M6_WARNING_EVENT_OUTCOME_v1.

## Point-in-time tape owner

03_DAILY_CAPTURE_LOGS/hourly/
Required row health for primitive extraction:
- spot_status=PASS for spot price/taker/ETHBTC fields
- derivatives_status=PASS for OI/funding fields
- source_window_end_utc is the legal availability time when valid; never use row values before that time

Available native fields include BTC/ETH OHLC, taker buy/sell quote volume and buy share, ETHBTC OHLC, BTC/ETH OI and OI change, long/short ratios, funding events, price/OI state.

## Binding

### A0 PRICE_RECLAIM_CONTEXT_ONLY
Status: BLOCKED_AS_BINARY_PRIMITIVE.
Reason: current production owner does not expose a canonical generic "reclaim deterioration" threshold equivalent to July 63.3K. Importing 63.3K into future markets would be nonsensical.
Allowed shadow data: contemporaneous BTC price path and returns only.
No binary A0 state may be invented.

### A1 STRUCTURE_DEPTH
Status: BLOCKED_AS_BINARY_PRIMITIVE.
Reason: July 61.9K was event-specific structure, not a portable prospective threshold. Current M6 adverse barriers are outcome labels, not warning-time features.
Allowed future route: consume an explicit canonical structure-state owner if one is introduced independently of EDGE-001 outcomes.
Do not derive a threshold from future outcomes.

### A2 BREADTH_PERSISTENCE_TRANSLATION
Status: UNKNOWN_FOR_CANONICAL_ABLATION.
Current rich breadth owner declares PROXY_ONLY, canonical_compatible=false, registered_threshold_compatibility=UNCONFIRMED and NO_HIDDEN_SUBSTITUTION.
It may be logged as research context with provenance, but cannot score A2 incremental value.

### A3 FLOW_CONFIRMATION
Status: AVAILABLE_AS_CONTINUOUS_SHADOW_FEATURES, NOT BINARY.
From healthy hourly tape, freeze continuous fields without threshold:
- btc_taker_buy_quote_share
- eth_taker_buy_quote_share
- btc_oi_change_1h_pct
- eth_oi_change_1h_pct
- funding values when present
No buy-share or OI cutoff is defined. A3 cannot yet become a pass/fail confirmation layer.

### M1 LEVERAGE_STRESS_CONTEXT
Status: AVAILABLE_CONTINUOUS / PARTIAL.
Use OI changes, funding values and price_oi_state only with derivatives_status=PASS. Missing funding remains missing.

### M2 ETHBTC_REPAIR_CONTEXT
Status: AVAILABLE_CONTINUOUS.
Use direct ethbtc_close and returns with spot_status=PASS. The historical 0.0275/0.030 gates are not portable prospective thresholds and are not imported by EDGE-001.

### M3 DATA_MISSINGNESS_CONFIDENCE_BRAKE
Status: ACTIVE_GOVERNANCE_PRIMITIVE.
Any unavailable required owner remains UNKNOWN. Proxy-only breadth cannot silently fill canonical breadth. Missing funding cannot be converted to zero.

## Scientific consequence

The previously frozen hierarchy remains a research question, but current owner coverage is insufficient to honestly score A0->A3 as binary levels.

Therefore:
- do not build a fake A0-A3 classifier;
- start a prospective FEATURE LEDGER bound to natural M6 opportunities;
- log continuous point-in-time price/ETHBTC/taker/OI/funding context and explicit breadth availability/proxy status;
- retain M6 outcomes separately;
- define any future transformation only in a new preregistration before inspecting its outcome association.

This is a successful fail-closed result. It prevents July-specific thresholds and noncanonical breadth from contaminating the prospective test.

CLAIM_LEVEL=HYPOTHESIS
ABLATION_SCORING_READY=NO
FEATURE_COLLECTION_READY=YES
WARNING_IS_SELL=FALSE
LIVE_EXIT_RULE=NONE
