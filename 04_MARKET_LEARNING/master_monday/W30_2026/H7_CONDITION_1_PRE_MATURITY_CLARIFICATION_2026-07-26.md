# H7 Condition 1 — Pre-Maturity Governance Clarification

**Date:** 2026-07-26  
**Decision context:** Issued after the OTA velocity flag timestamp `2026-07-26T15:43:25Z` and before H7 row 5 maturity at `2026-07-26T22:00:00Z`.  
**Status:** `CANONICAL_OPERATIONAL_CLARIFICATION / PARTIALLY_OBSERVED_PATH / NOT_CLAIMED_AS_RECOVERED_ORIGINAL_TEXT`  
**Scope:** H7 condition 1 only. Conditions 2 and 3 remain unchanged.

## 1. Provenance finding

The exact frozen H7 slope-condition wording could not be recovered from the authoritative W30 archive. The forecast ledger explicitly records that the frozen slope-condition text was unavailable and that final adjudication remained with the main framework.

Therefore this document does not claim to reconstruct the original preregistration.

Because four of five settled rows and a live indication for row 5 were already visible when this clarification was issued, the final H7 evidence must retain the qualification:

`PRE_MATURITY_CLARIFICATION_AFTER_PARTIAL_OBSERVATION`

It must not be represented later as a clean untouched preregistration.

## 2. Canonical operational wording for condition 1

Let `C1 ... C5` be the five full-precision, direct-market ETH/BTC settled CEST closes for H7 rows 1 through 5.

Define:

`d_i = ln(C_i) - ln(C_(i-1))`

for rows 2 through 5.

**H7 condition 1 passes only when the final three settled increments are all strictly positive:**

- `ln(C3) - ln(C2) > 0`
- `ln(C4) - ln(C3) > 0`
- `ln(C5) - ln(C4) > 0`

Because the natural logarithm is monotonic, this is equivalent to:

`C3 > C2 AND C4 > C3 AND C5 > C4`

For the current row structure, this means the settled ETH/BTC closes for 24 July, 25 July and 26 July must each be higher than the immediately preceding settled CEST close.

### Boundary rules

- Equality does not pass.
- Display-rounded values may not adjudicate the test.
- Use full source precision from the direct ETH/BTC market feed.
- A derived ETH/BTC ratio is observation-only and cannot hard-score condition 1.
- Partial or live candles never count as settled rows.

## 3. Five-row slope handling

The five-row OLS slope of `ln(ETH/BTC close)` against row number may be calculated once row 5 settles.

Its role is:

`DIAGNOSTIC_ONLY`

It may describe the overall five-row trajectory, but it may not replace, rescue or veto the consecutive-increment definition above.

This prevents an unspecified regression convention from silently changing the test after the path is visible.

## 4. H7 final labeling rule

After row 5 settles:

- If condition 1, condition 2 and condition 3 all pass, the maximum permitted label is:

`EARLY_TRANSMISSION_CANDIDATE_NOT_ROTATION_CONFIRMATION`

- If condition 1 fails, H7 does not trigger even if the five-row diagnostic slope is positive.
- If direct settled row 5 is unavailable or source-conflicted, final H7 status is `PENDING_SOURCE_RESOLUTION`, not pass or fail.

## 5. Authority boundary

Even if H7 meets all three conditions, it does not by itself change:

- `rotation = NO_ROTATION`
- `rebuy = LOCKED`
- `new_entry = NOT_ACTIVE`
- `large_caps = WATCH_ONLY`
- portfolio action
- the closed F4 result

F4 remains `MATURED / GATE_UNMET / CONFOUNDED / DO_NOT_REOPEN`.

H7 is an early transmission candidate test, not a rotation-confirmation gate.

## 6. Governance rationale

The strict consecutive-increment definition is selected because it is:

- deterministic;
- auditable;
- independent of regression implementation;
- resistant to rounded-value disputes;
- stricter than a loosely positive multi-row slope;
- consistent with reporting an emerging transmission sequence without promoting rotation.

The partial-observation qualification remains permanently attached to this H7 instance to prevent hindsight laundering.
