# Cycle Navigator Skill Audit Spec v0.1 — Addendum 2026-07-07

Status: ACTIVE ADDENDUM  
Purpose: Add Master Monday chat-memory extraction findings, CN #11 contamination correction and CN #12 scoring upgrade to the audit spec.

---

## 1. April Master Monday separation rule

April Master Monday and Cycle Navigator Week 3 must not be merged.

Rows must be separated as:

- `MM_2026_04_14_DRAFT_HIGH_1552`
- `MM_2026_04_14_V3_CN_1553`
- `MM_2026_04_14_PRICE_CORRECTION_1555`
- `MM_2026_04_14_CORRECTED_VERIFIED_1603`
- `MM_2026_04_14_FORMAT_UPGRADE_1728`
- `CN_WEEK3_PUBLIC_DRAFT_1910`

Only the public CN row belongs in Cycle Navigator public scoring.

Only the corrected 16:03 row is the current best April Master Monday candidate, and it remains provisional until raw source is found.

---

## 2. CN #11 contamination rule

CN #11 has a known copy-paste contamination risk.

Correct internal CN #11 row:

- BTC: 61K-69K
- ETH: 1.55K-1.90K

Contaminated row that must not be used for CN #11:

- BTC: 79.5K-84K
- ETH: 2.28K-2.48K

Reason:

The contaminated values belong to CN #7 and must not be duplicated into CN #11.

Any CN #11 audit row using 79.5K-84K / 2.28K-2.48K must be marked:

`CN11_COPY_PASTE_CONTAMINATION_FAIL`

---

## 3. CN #12 scoring method upgrade

From CN #12 onward, range scoring should use the upgraded method found in chat memory from 2026-06-15:

- weekly Jaccard
- daily containment
- breach count
- range width penalty
- dumb vol-band benchmark

Rules:

- Apply prospectively from CN #12 onward.
- Do not overwrite historical public CN scores before CN #12.
- For earlier CN rows, these metrics may be calculated as an independent audit overlay only.
- Public displayed score and independent audit score must remain separate.

---

## 4. Draft-row exclusion rule

Rows labeled as any of the following may not be final-scored:

- DRAFT_OR_PRE_CORRECTION
- PRICE_VERIFICATION_CORRECTION
- FORMAT_UPGRADE
- CONTAMINATION_CORRECTION
- SCORING_METHOD_UPGRADE
- DATE_CORRECTION_AND_DRAFT

They may only be used for reconstruction, chronology and governance explanation.

---

## 5. Updated next action

After this addendum, the next execution step is:

`cycle_navigator_actuals_reconciliation_report_v0_1.md`

Purpose:

Resolve or separate actual-source conflicts for:

- W22
- W23
- W24
- W25 if needed
- W27

No final skill scoring should occur before actual conflicts are labeled.

---

## 6. Governance conclusion

The audit structure is now stronger because it separates:

- drafts
- verified corrections
- public CN outputs
- contamination corrections
- scoring-method upgrades

This prevents false accuracy claims and false conflicts.

No market call.
No portfolio action.
No rule ratification.
