# TechDev Forward Calibration Ledger v1

**Created:** 2026-07-11  
**Status:** ACTIVE_APPEND_ONLY / SOURCE_BACKED / OUTCOME_SEPARATED  
**Scope:** Step 4 requested by the user  
**Seed source:** TechDev Market Update Issue #95

## Purpose

New TechDev claims are scored prospectively instead of waiting for another multi-year retrospective audit. Every material claim receives a frozen original row before its outcome is known.

## Required fields

```text
row_id
source_id
publication_date
category
original_claim
original_window
original_invalidation_or_condition
framework_role
revision_parent
status
outcome_due
verified_actual_source
outcome
notes
```

## Seed rows

| Row ID | Source | Category | Frozen original claim | Window | Condition | Framework role | Status | Outcome / due |
|---|---|---|---|---|---|---|---|---|
| TD-FWD-001 | MU #95 | BTC_BOTTOM_RANGE | BTC reaches 57K-63K at end-June or early-July 2026 | 2026-06-20 to 2026-07-10 | Conservative business-cycle red-zone thesis | ROADMAP_SCENARIO | MATURED_SUPPORTED | User-verified W27 low 57,778.72, inside range |
| TD-FWD-002 | MU #95 | ETH_BOTTOM_RANGE | ETH reaches 1,400-1,600 at end-June or early-July 2026 | 2026-06-20 to 2026-07-10 | Same cycle condition | ROADMAP_SCENARIO | MATURED_SUPPORTED | User-verified W27 low 1,549.83, inside range |
| TD-FWD-003 | MU #95 | BTC_TARGET_RANGE | BTC reaches 94K-98K | Sep-Oct 2026 | Recovery follows the proposed bottom | ROADMAP_SCENARIO | OPEN | Due 2026-10-31 |
| TD-FWD-004 | MU #95 | ETH_TARGET_RANGE | ETH reaches 2,800-3,400 | Sep-Oct 2026 | Recovery follows the proposed bottom | ROADMAP_SCENARIO | OPEN | Due 2026-10-31 |
| TD-FWD-005 | MU #95 | BTC_TARGET_RANGE | BTC reaches 115K-125K | By 2026 year-end | Conservative red-zone path remains valid | ROADMAP_SCENARIO | OPEN | Due 2026-12-31 |
| TD-FWD-006 | MU #95 | ETH_TARGET_RANGE | ETH reaches 4,500-5,000 | By 2026 year-end | Conservative red-zone path remains valid | ROADMAP_SCENARIO | OPEN | Due 2026-12-31 |
| TD-FWD-007 | MU #95 | BTC_TARGET_RANGE | BTC reaches 140K-160K | By mid-2027 | Cup-and-handle and business-cycle path | ROADMAP_SCENARIO | OPEN | Due 2027-06-30 |
| TD-FWD-008 | MU #95 | ETH_TARGET_RANGE | ETH reaches 6,000-6,500 | By mid-2027 | Amazon analog and cycle path | ROADMAP_SCENARIO | OPEN | Due 2027-06-30 |
| TD-FWD-009 | MU #95 | RELATIVE_STRENGTH | ETH outperforms BTC through the recovery leg | Bottom window through mid-2027 | ETH/BTC expected bullish | SHADOW_ROTATION | OPEN | Evaluate at each target window and final 2027-06-30 |

## Actual-source binding for matured rows

```yaml
source_id: WEEKLY_RANGE_2026_27_20260705_2010
btc_low: 57778.72
eth_low: 1549.83
classification_rule: DAILY_INTRADAY_LOW_TOUCHES_FROZEN_RANGE
terminal_bottom_claim: NO_ADDITIONAL_CREDIT_UNTIL_LATER_LOW_RISK_IS_CLOSED
```

The two bottom rows receive range-touch support only. They do not prove that the terminal cycle bottom is permanently complete.

## Append protocol for every new TechDev article

1. Add only decision-relevant, falsifiable claims.
2. Preserve the exact confidence language, primary, secondary, conditional or speculative.
3. Freeze the original date, target, window and invalidation.
4. A revision creates a new row linked to the old row.
5. Never rewrite an expired row.
6. Use verified actuals independent of TechDev's own recap.
7. Score roadmap, timing, target, rotation, trade and framework impact separately.
8. Keep OPEN rows open until their original window matures.
9. Do not create portfolio action from a ledger row.

## Runtime status vocabulary

```text
OPEN
MATURED_SUPPORTED
MATURED_PARTIAL
MATURED_NOT_SUPPORTED
NOT_EVALUABLE
REVISED_NEW_ROW_CREATED
INVALIDATED
```

## Current schedule

```yaml
next_required_review: 2026-10-31
interim_review_allowed: SOURCE_REVISION_OR_EXPLICIT_INVALIDATION_ONLY
open_rows: 7
matured_supported_range_rows: 2
live_execution_authority: ZERO
```
