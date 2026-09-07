# Skill Quality Gate Evaluation Contract Draft

**Dato:** 2026-09-07  
**Status:** SOURCE_NOTE  
**Område:** agent skill evaluation  
**Primary folder:** `07_PROMPTS_AND_AGENTS/skill_runs/`

This draft reserves the evaluation vocabulary for the proposed read-only meta-evaluator. It has no authority until registered through the normal skill registry path.

```yaml
skill_under_test:
baseline_ref:
candidate_ref:
case_set_ref:
evaluator_ref:
run_isolated: YES | NO | UNKNOWN
critical_regressions: []
deterministic_checks:
blind_comparative_checks:
trigger_precision:
trigger_recall:
authority_compliance:
autonomy:
actionability:
correctness:
safety:
concision:
token_cost_delta:
latency_delta:
baseline_without_skill_result:
completion_verification:
verdict: KEEP_BASELINE | ACCEPT_CANDIDATE | MODIFY_AND_RETEST | RETIRE_REVIEW | BLOCKED
```

Hard gates:

- no critical regression may be averaged away;
- authority or repository-safety regression blocks acceptance;
- missing evaluator separation blocks acceptance;
- incomplete or stale verification blocks completion claims;
- unavailable cost or latency evidence stays `UNKNOWN`, never inferred;
- `RETIRE_REVIEW` is advisory and cannot delete or disable a skill automatically.
