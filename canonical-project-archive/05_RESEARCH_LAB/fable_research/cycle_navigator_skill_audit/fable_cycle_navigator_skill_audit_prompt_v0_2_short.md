# Fable Cycle Navigator Skill Audit Prompt v0.2 Short

Date: 2026-07-07  
Status: READY_FOR_FABLE / SHORT HANDOFF PROMPT  
Purpose: Run a skeptical audit of Cycle Navigator forecast skill using the GitHub archive and ChatGPT inhouse research.

---

## Prompt for Fable

You are Fable Research Lab acting as an adversarial forecast-skill auditor for the Investering / Cycle Navigator framework.

You are not making market calls, portfolio recommendations, framework ratifications or public track-record updates. Your task is research only.

### Task

Audit the Cycle Navigator source-backed subset and determine whether the evidence supports:

- clear range skill,
- mixed provisional skill,
- stronger regime/rotation skill than price-range skill,
- or insufficient evidence.

### Required input files

Use these GitHub files as primary context:

1. `canonical-project-archive/06_CYCLE_NAVIGATOR/archive_manifests/cycle_navigator_forecast_actual_rows_sourcebacked_v0_2.csv`
2. `canonical-project-archive/06_CYCLE_NAVIGATOR/skill_audits/cycle_navigator_skill_audit_spec_v0_1.md`
3. `canonical-project-archive/06_CYCLE_NAVIGATOR/skill_audits/cycle_navigator_skill_audit_spec_v0_1_addendum_2026-07-07.md`
4. `canonical-project-archive/06_CYCLE_NAVIGATOR/skill_audits/cycle_navigator_actuals_reconciliation_report_v0_1.md`
5. `canonical-project-archive/06_CYCLE_NAVIGATOR/skill_audits/cycle_navigator_skill_audit_rows_v0_1.csv`
6. `canonical-project-archive/06_CYCLE_NAVIGATOR/skill_audits/cycle_navigator_provisional_skill_audit_summary_v0_1.md`
7. `canonical-project-archive/05_RESEARCH_LAB/inhouse_research/cycle_navigator_skill_audit/chatgpt_inhouse_cycle_navigator_skill_research_v0_1.md`
8. `canonical-project-archive/07_MASTER_MONDAY/archive_manifests/master_monday_sourcebacked_rows_v0_2.csv`
9. `canonical-project-archive/07_MASTER_MONDAY/archive_manifests/april_2026_master_monday_conflict_resolution.md`
10. `canonical-project-archive/07_MASTER_MONDAY/chat_memory_extractions/master_monday_chat_memory_extraction_2026-07-07.md`

### Known provisional row set

CN #2: BTC 65K-72K -> 66K-71K, displayed score 88, full containment, Jaccard 0.714.

CN #3: BTC 66K-73K -> 69K-76K, displayed score 83, high-side breach, Jaccard 0.400.

CN #4: BTC 73K-79K -> 74K-78.5K, displayed score 86, full containment, Jaccard 0.750.

CN #5: BTC 76.5K-83.5K -> 75.4K-80.3K, displayed score 85, low-side breach, Jaccard 0.469.

CN #6: BTC 79K-83.5K -> 78.5K-82.5K, displayed score 92, low-side breach, Jaccard 0.700.

CN #7: BTC 79.5K-84K -> 77.6K-82.3K, displayed score 91, low-side breach, Jaccard 0.438. ETH 2.28K-2.48K -> 2.16K-2.37K, low-side breach, Jaccard 0.281.

CN #8: forecast exists, but no next-week evaluation or actuals. Do not score it.

### Inhouse provisional finding to audit

ChatGPT inhouse research found:

- rows assessed: 6,
- full BTC containment: 2/6,
- partial BTC breach: 4/6,
- full miss: 0/6,
- low-side BTC breach: 3/6,
- high-side BTC breach: 1/6,
- mean BTC Jaccard: 0.578,
- mean BTC width ratio: 1.207,
- mean displayed public score: 87.5.

Provisional hypothesis:

`MIXED_SKILL_PROVISIONAL / RANGE_SKILL_NOT_PROVEN / REGIME_ROTATION_SKILL_STRONGER`

Audit this hypothesis. Do not assume it is correct.

### Critical rules

- Do not score memory-only rows.
- Do not treat displayed public score as pure price-range score.
- Do not claim statistical significance from six rows.
- Keep Master Monday and public Cycle Navigator separate.
- Do not use CN #11 contaminated values. Correct CN #11 is BTC 61K-69K and ETH 1.55K-1.90K. The 79.5K-84K / 2.28K-2.48K row is contamination.
- Do not score CN #8 until an evaluation or actual source is found.
- Public track-record update is not allowed.

### Required analysis

1. Validate the row set.
2. Recompute BTC and ETH range metrics.
3. Compare displayed public scores with independent range metrics.
4. Judge whether high scores are supported by phase/rotation rather than range.
5. Diagnose failure modes, especially low-side breach clustering after CN #5.
6. Design baseline tests: prior-week repeat, ATR band, fixed-percentage band and no-skill wide band.
7. List exact data needed before final track-record update.

### Required output

Return these sections:

1. Executive verdict.
2. Row validation table.
3. Independent range metrics.
4. Displayed score vs independent range assessment.
5. Phase / rotation audit.
6. Failure modes.
7. Baseline test plan.
8. Data requests.
9. Framework recommendations split into safe updates, shadow-only hypotheses and do-not-update-yet.
10. Final governance line.

Final governance line must be:

No market call. No portfolio action. No rule ratification. No public track-record update.
