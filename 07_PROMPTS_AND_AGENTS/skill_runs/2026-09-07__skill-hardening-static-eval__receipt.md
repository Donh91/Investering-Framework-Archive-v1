# Skill Hardening Static Evaluation Receipt

**Dato:** 2026-09-07  
**Status:** RECEIPT  
**Område:** agent skill quality / safety hardening  
**Primary folder:** `07_PROMPTS_AND_AGENTS/skill_runs/`

## Evaluation authority

Evaluator procedure: `.agents/skills/skill-quality-gate/SKILL.md`  
Evaluation mode: `STATIC_ONLY`  
Baseline manifest: `07_PROMPTS_AND_AGENTS/skill_quality_gate/BASELINES.json`  
Representative case set: `07_PROMPTS_AND_AGENTS/skill_quality_gate/EVAL_CASES.json`  
Candidate branch base: `db69f28678ea1e8ae01bf6e6a2b4645cce12940e`  
Candidate file state verified through commit: `549295cf8ad417d4e51ef93a1c5216eaac99b143`

This receipt does not claim runtime A/B execution, token/cost improvement, trigger precision/recall improvement or no-skill baseline superiority.

## Candidate 1 - developer-source-research

```yaml
skill_name: developer-source-research
evaluation_mode: STATIC_ONLY
baseline_blob_sha: 11165d3dbb5748702795c72e6a9c929d3c67c430
candidate_blob_sha: 66557167d9204dd165cce35d2e8320ccc2459be0
evaluator_separated: YES
deterministic_blockers: []
critical_regressions: []
trigger_result: NOT_EXECUTED
correctness_result: NOT_EXECUTED
authority_result: PASS
safety_result: PASS
autonomy_result: NOT_EXECUTED
cost_context_result: UNKNOWN
baseline_without_skill_result: NOT_EXECUTED
completion_verification: PASS_STATIC_SCOPE_ONLY
verdict: ACCEPT_CANDIDATE
acceptance_basis: SAFETY_AND_SOURCE_QUALIFICATION_SPEC_HARDENING_ONLY
behavioral_improvement_claimed: NO
```

Deterministic comparison findings:

- Existing read-only authority is preserved.
- Existing primary-source and current-behavior precedence is preserved.
- Added source qualification binds immutable revision when available, license state, inspected/uninspected scope and reuse granularity.
- Added external-instruction trust boundary explicitly prevents third-party SKILL.md/AGENTS.md/README content from expanding permissions or becoming active authority.
- Added rules prefer smallest useful mechanism over overlapping whole-skill imports.
- No market, evidence-row, code-write, portfolio or credential authority was added.

## Candidate 2 - codex-intake

```yaml
skill_name: codex-intake
evaluation_mode: STATIC_ONLY
baseline_blob_sha: 581af55e65b4c0a6dad038daca05c9a55c35d355
candidate_blob_sha: d908a540a96c33de7dd9098c08d9547760024bc7
evaluator_separated: YES
deterministic_blockers: []
critical_regressions: []
trigger_result: NOT_EXECUTED
correctness_result: NOT_EXECUTED
authority_result: PASS
safety_result: PASS
autonomy_result: NOT_EXECUTED
cost_context_result: UNKNOWN
baseline_without_skill_result: NOT_EXECUTED
completion_verification: PASS_STATIC_SCOPE_ONLY
verdict: ACCEPT_CANDIDATE
acceptance_basis: ROOT_CAUSE_AND_FRESH_COMPLETION_EVIDENCE_GATES_ONLY
behavioral_improvement_claimed: NO
```

Deterministic comparison findings:

- Existing routing-only authority and `LATEST_CODEX_READY_TASKS.json` queue authority are preserved.
- The public version label remains `v1`, consistent with the current skill registry; this is additive hardening, not a new authority generation.
- No candidate schema field was invented; the hardening explicitly reuses existing objective, evidence, reproduction and acceptance-test surfaces.
- Added discipline separates observed symptom from suspected root cause and blocks speculative fix bundles.
- Repeated failed fixes now trigger architectural escalation instead of unlimited patch attempts.
- Completion now requires fresh evidence from the final merged state against the original symptom plus positive/negative bounded tests.
- Existing prohibitions on market, threshold, portfolio, canonical-authority and self-merge changes remain intact.

## Gate conclusion

```yaml
runtime_ab_executed: NO
static_authority_regression: NO
static_safety_regression: NO
external_runtime_dependency_added: NO
new_engine_created: NO
new_shadow_layer_created: NO
new_market_or_portfolio_authority: NO
merge_recommendation: PERMITTED_FOR_SAFETY_SPEC_HARDENING
runtime_behavioral_claim: DEFERRED_UNTIL_QUALIFIED_EVAL
```

The merge recommendation is limited to explicit safety, provenance and verification specification hardening. It must not be cited as proof that runtime agent performance, trigger precision, token cost or autonomy improved.
