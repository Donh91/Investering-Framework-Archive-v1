# Weekly Skill Calibration, existing Framework Learning Supervisor

**Date:** 2026-11-13  
**Owner:** existing Framework Learning Supervisor, Strategist and Skill Quality Gate #1157.  
**Status:** deterministic code candidate pending native tests, governed merge and natural Monday run.  
**Authority:** ADVISORY_ONLY, no market, portfolio, signal, release, skill-promotion or autonomous code-change authority.

## Why this is an evolving weekly loop, not a new watcher

`00_FMOS/FRAMEWORK_INTELLIGENCE_AND_LEARNING_LOOP_v1.md` already assigns cross-week learning and Meta Learning to the existing Supervisor. The existing `.github/workflows/framework-learning-supervisor.yml` runs daily and on Monday after weekly forensics FINAL. This work reuses that **same schedule and current main writer**. It does not add a new cron, model call, GitHub identity, queue, separate Supervisor, or background task.

**Method:** last completed ISO week FINAL -> current skill registry -> optional source-bound usage observations -> previous week's **frozen** scorecard -> one P0/P1/P2 improvement hypothesis -> existing owner/quality gate -> next week's new evidence. Do not automatically rewrite rule weights, skill instructions, workflows or scientific claims.

## Automated output

The actual producer is the existing script `scripts/framework_intelligence/framework_learning_supervisor.py`, which invokes `scripts/framework_intelligence/weekly_skill_calibration_v1.py` only on Monday in `Europe/Copenhagen`.

- `research/framework_learning/LATEST_SKILL_CALIBRATION.json` is produced on Monday and continues to point at the same frozen completed-week report on subsequent daily Supervisor runs, without counting those re-reads as new observations.
- `research/framework_learning/skill_calibration/weeks/YYYY-Www.json` freezes a completed report. No historic overwrite on later re-runs.
- `research/framework_learning/LATEST_SUPERVISOR_STATE.json:skill_calibration` gets a compact read-only status/owner/action link.
- `research/framework_learning/LATEST_MASTER_MONDAY_LEARNING_PACKET.json:skill_calibration_advisory` carries the completed-week scorecard path and exact SHA256, with status and original owner, including later daily runs. This is shadow-only, never a live CN or trading instruction. A hash-bound field in a packet is **not** proof that the GitHub Master Monday publisher or the separate S2 Chat task actually consumed it.
- The existing workflow's `git add research/framework_learning` already persists it, with existing main-readback procedures for its canonical output files. No new workflow edit.

A report is never a scheduled-run receipt until genuine workflow execution/commit and main readback are checked.

### Native Master Monday timing and genuine consumption

Existing source-confirmed schedules (Europe/Copenhagen): `sunday-market-close-and-cfgi.yml` has Monday 02:05 FINAL; `weekly-api-calibration-shadow.yml` begins Monday 02:40 and may publish the GitHub Master Monday machine package; `framework-learning-supervisor.yml` has Monday 04:35 and 09:35 runs. The separate Chat S2 Master Monday is scheduled 10:00. Github Actions may be delayed. **A scorecard produced at 04:35/09:35 cannot retroactively influence a Master Monday machine forecast frozen earlier at 02:40.** No artificial lookahead or reissuing the original weekly forecast.

The advisory packet preserves the exact source and SHA256 for the separate S2 10:00 consumer or a later independent Master Monday post-issuance report. S2's **actual saved task prompt and authenticated source readback** must be separately verified. If its run occurred before this week's scorecard was durably published to main, show `ADVISORY_UNAVAILABLE_AT_S2_CUTOFF`, do not infer completion and do not edit a frozen forecast. Actual S2 receipt with original packet SHA + read timestamp is required to claim `S2_CONSUMED`; until then `S2_CONSUMPTION=UNKNOWN`.

The existing GitHub Master Monday publisher `scripts/master_monday/publish_master_monday_outputs.py` reads the learning packet for its separate `LEARNING_DECISION_IMPACT_v1` shadow assessment. **It does not currently independently attest consumption of the new nested skill advisory**. That potential consumer adapter is a separate guarded original-owner task, not falsely described as complete.



## KPI definitions, source quality first

| KPI | Numerator / denominator | Missing evidence |
| --- | --- | --- |
| Skill inventory | Verified derived registry entries, categorized nonpilot/pilot/implicit | CATALOG_BLOCKED |
| Inventory week-on-week delta | Current eligible registry size minus prior frozen weekly registry size | null |
| Source-bound use observations | Unique invocation + skill claims with valid source digest, matching week, safe path, matching skill digest | null when no observation census |
| Reported phase mix | Reported `SUGGESTED_ONLY` / `READ_CONFIRMED` / `PROCEDURE_APPLIED` over valid source-bound observations | null |
| Duplicate reports | Repeated invocation+skill keys; never treated as independent samples | null when no observation census |
| Invalid reports | Files failing source/time/authority/proof constraints | null when no observation census |
| Unauthorized pilot-use alerts | Reported `PROCEDURE_APPLIED` against unaccepted pilot | Requires native investigation, self-report is not proof |
| Verified skill adoption rate | **Native** actually executed skill loads / eligible native invocations | null until a reliable eligible-run denominator exists |
| Marginal useful output | Independent original-owner adjudicated incremental outcomes / comparable completed baseline cases | null until separate skill-quality-gate / AICL evidence |
| False positive/negative trigger rate | Evaluator-labeled misroutes / representative eligible cases | null before independent labels |
| Token/cost/latency impact | Observed same-case model/tool telemetry baseline vs with skill | null without matched actual telemetry |
| Real closure contribution | Native original-PR closed/merged outcome bound to actual skill-use, not an issue comment | null without native run+causal evidence |

A report claiming a skill was used is NOT independently verified usage. Neither registry count nor a source-bound self-report is economic benefit. Never convert unavailable denominator to zero. First four weeks provide a baseline, not a validated claim of improvement. Compare after at least two independently eligible weeks; accept/change skills only via existing independent skill-quality-gate and governing owner.

## Source-bound self-report observation adapter (optional, existing-owner receipts)

Original-domain owners may provide a limited, public-safe advisory sidecar under:

`research/framework_learning/skill_usage/observations/YYYY-Www/<stable-invocation>.json`

```json
{
  "contract": "SKILL_USE_OBSERVATION_v1",
  "authority": "ADVISORY_SELF_REPORT_ONLY",
  "automatic_skill_activation": false,
  "week": "2026-W46",
  "observed_at_utc": "2026-11-12T12:45:00Z",
  "invocation_id": "native-original-run-id",
  "skill_name": "canonical-context-router",
  "use_phase": "READ_CONFIRMED",
  "execution_receipt_path": "research/framework_learning/operational_memory/verified-original-receipt.json",
  "execution_receipt_sha256": "<SHA256 of actually present original receipt bytes>",
  "skill_sha256": "<SHA256 of exact currently present skill file>"
}
```

This is a **schema example, not an existing execution claim**. Do not commit placeholders. Observation files can be created only by already authorized original-owner writers from real run evidence. A self-report with hash matching is still labeled `SOURCE_BOUND_SELF_REPORTS_NOT_INDEPENDENT_PROOF`. Native job/use attestation and actual incremental-effect evaluation must occur through existing owners before any metrics become VERIFIED. Maximum 200 observations/week, no private material, no arbitrary paths, duplicate/invalid receipts do not improve performance denominator.

## Weekly deterministic calibration and improvement action

- **SOURCE_BLOCKED**: matching FINAL weekly forensics is missing/stale, preserve status/UNKNOWN; repair existing source/weekly owner.
- **BASELINE_ONLY_NATIVE_USAGE_UNKNOWN**: no eligible observations, propose exactly one P1 `INSTRUMENT_NATIVE_SKILL_USAGE` through the existing owner. No new monitor.
- **SOURCE_BOUND_REPORTS_ADVISORY_ONLY**: qualified self-reports exist, propose a bounded independent `skill-quality-gate` comparison with no-skill baseline and negative trigger cases.
- **SOURCE_QUALITY_BLOCKED**: malformed/oversize inputs, propose specific source integrity repair, never fabricate sample count.
- **P0 pilot anomaly**: a source-bound claim of using an unapproved pilot deserves native verification and qualified remediation, no automatic skill disabling or market/release changes.
- **Calibration result can propose, never self-promote.** No automatic paid model and no extra recurring manual requirement. Current unresolved action remains in the existing owner #1157, dedup by week and action code.

## Success and stop

After four qualified weeks, review: rate of real native skill receipts, independent comparison completion, justified priority corrections, useful code/PR closures, false activation, missed useful skill, repeated duplicate research, and measured costs. The objective is **more verified useful work per cost**, not more skills or more reports. A missing native denominator is an instrumentation gap, never success.

Stop/narrow if the new reading causes significant existing-S1 closure delay, any pilot is activated without permission, repeated scans give no measurable value or the meta-layer becomes a second repair queue. Changes to a skill require normal branch/PR/CI and independent skill-quality-gate; no automatic release, trading or scientific promotion.

**First actual calibration week after a qualified merge:** the next real Monday with matching FINAL forensics, not an artificially reconstructed historical week.