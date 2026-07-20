# TechDev Issue #98 Prospective Calibration v1

**Dato:** 2026-07-20  
**Status:** ACTIVE_FORWARD_TEST_EXTENSION_SHADOW_ONLY  
**Område:** TechDev claim calibration / trigger tracking / Gem Score outcomes / weekly evidence production  
**Primary folder:** `06_RESEARCH_LAB/forward_tests/`  
**Depends on:** `06_RESEARCH_LAB/forward_tests/2026-07-10__active-test-registry__canonical.md`, `06_RESEARCH_LAB/forward_tests/2026-07-13__techdev-category-outcome-calibration-v1__canonical-addendum.md`, `01_CORE_FRAMEWORK/governance/2026-07-13__prospective-evidence-cooldown-and-next-audit-gate-v1__canonical.md`  
**Source:** `08_SOURCE_MATERIAL/techdev/2026-07-20__techdev-market-update-98__source-manifest.md`  
**Test owner:** `TECHDEV_CLAIM_LEDGER`  
**Rotation cross-reference:** `ROTATION_SURVIVAL_FORWARD`

## 1. Purpose

Freeze and track the testable claims in TechDev Market Update #98 before their future outcomes mature.

This is an extension of registered test T7. It is not a new engine, scoring authority, trading system or portfolio signal. The ETH/BTC lane is cross-routed to registered test T6 for comparison with the framework's existing rotation-survival requirements.

## 2. Authority boundary

```yaml
techdev_role: MACRO_COMPASS_AND_SOURCE_CLAIM_PROVIDER
techdev_execution_authority: ZERO
techdev_rotation_authority: SHADOW_ONLY
gem_score_framework_authority: ZERO
main_framework_state_authority: SOLE
portfolio_action_from_this_package: FORBIDDEN
automatic_rule_promotion: FORBIDDEN
current_framework_action_changed: NO
```

Issue #98 may strengthen context, produce prospective evidence and improve future calibration. It may not independently open the broad-alt basket, rebuy permission, deployment or a new entry.

## 3. Causal freeze and lineage

```yaml
source_issue_date: 2026-07-19
source_exact_publication_time: NOT_AVAILABLE_IN_CAPTURE
repository_freeze_date: 2026-07-20
freeze_receipt: GITHUB_COMMIT_TIMESTAMP_AND_PR_HISTORY
source_pdf_sha256: 693a08409eb66b6a11b3f4948f4ff340c38ca8b41d99c8b34b71d06057a36c5d
source_manifest: 08_SOURCE_MATERIAL/techdev/2026-07-20__techdev-market-update-98__source-manifest.md
frozen_claim_rows: 06_RESEARCH_LAB/forward_tests/techdev_issue_98/TECHDEV_ISSUE_98_FROZEN_CLAIM_ROWS.csv
gem_score_baseline: 06_RESEARCH_LAB/forward_tests/techdev_issue_98/TECHDEV_ISSUE_98_GEM_SCORE_BASELINE.csv
initialization_row: 06_RESEARCH_LAB/forward_tests/techdev_issue_98/weekly/2026-W30__initialization.json
latest_state_pointer: 06_RESEARCH_LAB/forward_tests/techdev_issue_98/LATEST_STATE.json
```

No outcome before the repository freeze may be counted as prospective evidence. Source statements remain frozen. Later TechDev revisions must be appended and scored separately under the existing revision-cost rules.

## 4. Tracking lanes

### TD98-A - Major trend confirmation

Question: Do the BTC and ETH 3-day Supertrend flips identify a durable major-market trend change?

Frozen source state:

```yaml
btc_3d_supertrend: RED
btc_approx_flip_level_at_source: 71400_USD
eth_3d_supertrend: RED
eth_approx_flip_level_at_source: 2020_USD
bottom_confirmation_definition: BOTH_MAJORS_GREEN
levels_dynamic: YES_WALK_WITH_EACH_3D_BAR
```

Weekly fields:

```text
BTC and ETH Supertrend state
actual flip date and settled 3-day close
single versus dual flip
price and threshold at flip
7D, 14D, 30D and 60D return after dual confirmation
maximum adverse and favorable excursion
loss or survival of the confirmed state
revision or override by TechDev
```

A dual flip confirms only the TechDev major-recovery claim. It does not automatically confirm broad rotation.

### TD98-B - ETH/BTC rotation confirmation

Question: Does TechDev's confirmed ETH/BTC flag breakout precede durable multi-axis rotation?

Frozen source state:

```yaml
flag_breakout_at_source: NOT_CONFIRMED
source_numeric_flag_boundary: NOT_DISCLOSED_IN_TEXT
source_target_after_confirmed_breakout: APPROX_0_08
broad_alt_basket_at_source: NOT_OPEN
```

The source's chart-defined flag breakout must not be silently replaced by the framework's numeric thresholds. They remain separate observations:

```yaml
framework_ethbtc_repair_context: 0.0275
framework_ethbtc_confirmation_context: 0.0300
techdev_trigger: CHART_DEFINED_CONFIRMED_FLAG_BREAKOUT
```

At a claimed breakout, T6 must inspect survival rather than first-cross alone:

```text
settled weekly confirmation
retest result
5D, 12-session and 30D survival
ETH/BTC persistence
BTC.D direction and convention
TOTAL2 and TOTAL3 structure
breadth state and membership stability
stablecoin deployment when source-complete
spot and futures flow congruence
DeFi and RWA relative strength
exit-side outcome and fakeout status
```

### TD98-C - Roadmap and sequence outcomes

Track separately:

```text
ETH 2800-3400 in Sep-Oct 2026
ETH 4500-5000 in Dec 2026-Jan 2027
ETH 6000-6500 in May-Jul 2027
BTC 94000-98000 in Sep-Oct 2026
BTC 115000-125000 in Dec 2026-Jan 2027
BTC 140000-160000 by mid-2027
BTC near-term sequence: low 70Ks, consolidation, then 80Ks
ETH near-term sequence: consolidation at mature diagonal, then breakout
H2-2020-versus-late-2018 macro analogy
```

For every roadmap row preserve:

```text
original claim result
latest revision result
revision count and delay
adverse move before revision
invalidation change
revision value and cost
timing error
range error
path error
maximum adverse excursion
whether a zone was only touched or durably established
```

A later correct revision may not repair the original claim score.

### TD98-D - Gem Score public calibration

The TechDev Gem Score is tracked as an external source score, not adopted as a framework score.

For every published candidate and every later rerun capture:

```text
asset and sector
market cap and volume when disclosed or independently verified
Gem Score total and five source sub-scores when disclosed
score delta from previous issue
source flag status
price delta since prior board
spam share and unique-account breadth when disclosed
catalyst and attention type
incentive contamination class
7D, 14D, 30D and 60D returns from the frozen observation point
maximum adverse excursion and maximum favorable excursion
performance against BTC, ETH and a liquid-alt benchmark
candidate survival, delisting or liquidity failure
```

No score threshold creates framework entry permission.

## 5. Incentive contamination metadata

A proposed numerical 0-5 score is not activated during the new-engine freeze. The permitted field is descriptive metadata only:

```text
NONE
LOW
MEDIUM
HIGH
UNKNOWN
```

Initial source-backed classification:

```yaml
BNKR: HIGH - explicit posting rewards materially contaminate raw mentions
SUSHI: HIGH - bounty and airdrop hunting plus reported 59 percent spam share
DGB: LOW - low reported spam and no comparable posting-reward mechanism disclosed
other_candidates: UNKNOWN_UNTIL_SOURCE_BACKED
```

This metadata does not alter TechDev's published score. Any future numerical adjustment requires post-freeze governance and evidence.

## 6. Robinhood Chain venue context

Robinhood Chain is recorded as venue-level context inside T7, not as a new sensor engine.

Weekly fields, only when source-backed:

```text
new launches
TVL
stablecoin liquidity
bridge inflows
DEX volume
active addresses
launch-token survival
organic versus incentivized participation
social acceleration across unrelated projects
source quality and timestamp
```

Missing fields remain `DATA_MISSING`. No pseudo-row or inferred zero is permitted.

## 7. Weekly operating cadence

Run once weekly after the settled Master Monday package is available.

Each weekly run must:

1. read the current Issue #98 latest-state pointer;
2. preserve all frozen source fields;
3. add one immutable file under `techdev_issue_98/weekly/`;
4. attach only settled, source-backed observations;
5. leave immature horizons pending;
6. compare Gem Score reruns with the debut board;
7. record TechDev revisions separately from original claims;
8. update `LATEST_STATE.json` to the new immutable weekly file;
9. keep row validity, coverage readiness and promotion status separate;
10. report no market or portfolio action from this research lane.

Suggested filename:

```text
YYYY-Www__weekly-calibration.json
```

## 8. Weekly JSON contract

Every weekly file must expose at least:

```yaml
week_id:
as_of_utc:
source_cutoff:
test_id: TECHDEV_CLAIM_LEDGER
source_issue: TECHDEV_98
previous_week_path:
major_confirmation:
rotation_confirmation:
roadmap_status:
gem_score_board_status:
sector_tailwinds:
robinhood_chain_context:
techdev_revisions:
missing_data:
row_validity:
coverage_readiness:
edge_or_promotion_status:
framework_state_changed_by_test: NO
portfolio_action_from_test: NONE
next_review:
```

## 9. Maturity and review gates

```yaml
weekly_review: AFTER_MASTER_MONDAY
major_flip_outcomes: 7D_14D_30D_60D_AFTER_DUAL_FLIP
rotation_outcomes: 5D_12_SESSION_30D_AFTER_CONFIRMED_BREAKOUT
gem_score_outcomes: 7D_14D_30D_60D_FROM_EACH_PUBLISHED_BOARD
roadmap_outcomes: AT_FROZEN_WINDOW_CLOSE
next_major_techdev_audit_earliest: 2026-08-10_SUBJECT_TO_EXISTING_READINESS
hard_stop_evidence_review: 2026-09-07
```

Gem Score may be considered for a governance review only after at least four to six published boards or approximately 75 to 100 source-backed candidate observations with mature outcomes. This permits review only. It does not authorize promotion.

## 10. Promotion and kill conditions

```yaml
promotion_condition: EXISTING_T7_GOVERNANCE_ONLY_AFTER_MATURE_CATEGORY_SPECIFIC_OUTCOMES_AND_FORMAL_REVIEW
kill_or_suspend_conditions:
  - source scoring methodology becomes materially non-reproducible
  - score history is not published consistently
  - revisions overwrite original rows
  - incentive contamination cannot be separated from organic breadth
  - the lane produces no decision-value divergence after sufficient mature rows
  - the lane is used to bypass main-framework authority
```

## 11. Initial verdict

```yaml
row_validity: PASS_SOURCE_FREEZE
coverage_readiness: NOT_READY_OUTCOMES_IMMATURE
edge_or_promotion_status: NO_CHANGE
framework_action: HOLD_EXISTING_STATE
portfolio_action: NONE
```

No market call. No portfolio action. No rule promotion. No TechDev weight change from initialization alone.
