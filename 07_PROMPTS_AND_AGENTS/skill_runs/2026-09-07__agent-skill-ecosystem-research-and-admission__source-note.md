# Agent Skill Ecosystem Research and Admission Review

**Date:** 2026-09-07  
**Status:** SOURCE_NOTE / ADMISSION_REVIEW  
**Scope:** external agent-skill prior art, local skill-quality governance, source-recovery and MCP usability  
**Authority:** research only; no market, portfolio, threshold, weight or canonical market-state authority

## Question

Which mechanisms from current public agent-skill ecosystems materially improve the Investering framework, and which should be rejected as overlapping dependencies or generic skill inflation?

## Current framework baseline

The framework already owns a seven-skill stack under `00_ARCHIVE_CONTROL/SKILL_REGISTRY.md`, including a read-only `skill-quality-gate`, plus frozen baselines and representative cases at:

```text
07_PROMPTS_AND_AGENTS/skill_quality_gate/BASELINES.json
07_PROMPTS_AND_AGENTS/skill_quality_gate/EVAL_CASES.json
```

The local gate already requires immutable comparison binding, deterministic blockers, evaluator separation, positive/negative trigger cases, no-skill baseline review when possible, and fresh completion verification. Critical regressions cannot be averaged away.

## External sources inspected

### OpenAI plugin-eval

Repository: `openai/plugins`  
Inspected revision: `1e285826e604f66f7208f7ac4dba0fe8341d1f57`  
Primary inspected path: `plugins/plugin-eval/README.md`

Useful mechanisms:

- deterministic local analysis before live benchmarking;
- real `codex exec` benchmark runs in isolated temporary workspaces;
- before/after comparison;
- observed token/usage evidence when telemetry is available;
- rich run artifacts rather than a final-answer-only score;
- explicit distinction between static analysis and live measurement.

Disposition: `ADAPT`, not install as framework authority.

### Tardigrde agent-skill-eval

Repository: `tardigrde/agent-skill-eval`  
Inspected revision: `59de161f657b82bfaf8f6abe83dfff38552deb21`

Useful mechanisms found in the current public project:

- fresh workspace execution with and without a skill;
- deterministic state-diff grading before LLM rubric fallback;
- repeated runs and pass-distribution / pass@k style evidence;
- token and wall-time measurement when available;
- side-effect and cleanup evidence;
- validation/doctor style preflight before benchmarking.

Disposition: `ADAPT`. Strong runtime-harness prior art, but no external runtime dependency is admitted by this review.

### AWS sample-agent-skill-eval

Repository: `aws-samples/sample-agent-skill-eval`

Useful mechanisms:

- static safety and permissions checks;
- explicit relevant/irrelevant trigger tests;
- with-skill versus without-skill comparison;
- lifecycle/regression-oriented evaluation.

Rejected mechanism:

- a weighted overall score must not be allowed to average away a critical authority, safety or repository-governance regression.

Disposition: `EXTRACT_MECHANISMS_ONLY`.

### AI Evals course skills

Current maintained repository: `ai-evals-course/evals-skills`  
Inspected revision: `11d35781d43c281baddd3c6a766b12d81c274c29`  
Primary inspected path: `skills/validate-evaluator/SKILL.md`

The older `hamelsmu/evals-skills` repository was inspected at `22418da2bfb159f28a1b0dcf64e969e14ae56c99`; its README explicitly redirects to the maintained repository above.

Useful mechanisms:

- an LLM judge is not trusted merely because it returns a score;
- judge calibration uses human-labelled examples and disjoint train/dev/test data;
- TPR and TNR expose asymmetric judge failure better than raw accuracy;
- the held-out test set is not an iteration surface;
- model or judge-prompt changes invalidate prior calibration unless revalidated;
- confidence intervals and explicit uncertainty are preferable to point-estimate certainty.

External example thresholds are research guidance, not adopted as framework thresholds by this review.

Disposition: `ADAPT_EVALUATOR_CALIBRATION`.

### Vercel agent-browser derive-client

Repository: `vercel-labs/agent-browser`  
Inspected revision: `219c47a9dab1776f320d11e66ce934fd239b2cb7`  
Primary inspected path: `skill-data/derive-client/SKILL.md`

Useful mechanism:

```text
browser first-use -> observe network -> identify stable read-only source -> direct client/collector -> verify
```

Important upstream caveats are load-bearing: internal APIs may be unversioned, HAR files can contain credentials/session material, and terms/rate limits must be respected.

Framework adaptation therefore requires a stricter source-recovery boundary: official documented sources first, public/read-only observation only, no auth bypass, no mutation, no credential-bearing HAR in the control plane, and no recovered endpoint becoming canonical without a separate source-contract review.

Disposition: `ADAPT_AS_SOURCE_RECOVERY_POLICY`, not direct install.

### Planning With Files

Repository: `OthmanAdi/planning-with-files`  
Inspected revision: `0d21b6c4aa5f2c5bdd3d042e7473ee09f7fae9e7`

Useful mechanism: explicit durable working state can improve recovery after context loss in long-running tasks.

Current Investering already has Git-backed receipts, queues, `LATEST_HANDOFF.json`, immutable commits and task branches. A direct install would introduce overlapping state and hook behavior. No framework-local evidence was found in this review that context compaction is currently a repeated, measurable failure mode requiring another state system.

Disposition: `HOLD_FOR_OBSERVED_GAP`. Do not install or queue implementation now.

### MCP builder patterns

Public MCP-builder guidance was compared with the existing Investering MCP admission program.

Useful mechanisms:

- tool discoverability and concise descriptions;
- structured outputs;
- pagination/filtering;
- actionable errors;
- read-only/destructive/idempotent/open-world annotations where supported;
- evaluate whether an agent can actually solve realistic tasks with the tool, not merely whether the endpoint responds.

Investering already has bounded provider challenges, read-only admission, hard blockers, provenance, failure isolation and sequential pilots. The missing improvement is a more explicit agent-usability evidence contract, not a new MCP-builder skill.

Disposition: `REFINE_EXISTING_MCP_ADMISSION`.

## Synthesis

### Highest-value gap: executable skill evaluation

The local `skill-quality-gate` has strong governance but no framework-local executable runtime harness yet. Current runtime fields can therefore remain `NOT_EXECUTED` or `UNKNOWN`, and prior implementation receipts correctly deferred behavioral superiority claims.

The strongest bounded code task is to add a local harness that:

1. uses the existing frozen baseline and case set;
2. executes identical cases against baseline/candidate/no-skill conditions in isolated workspaces when runtime is available;
3. grades deterministic conditions before any subjective judge;
4. repeats stochastic conditions rather than treating one run as proof;
5. records pass distribution, failed runs, tool traces/side effects, cleanup, token/cost/time when available;
6. preserves `UNKNOWN` when telemetry is unavailable;
7. never lets aggregate improvement override a critical authority/safety regression;
8. treats an uncalibrated LLM judge as advisory only.

This is a bounded implementation gap and is appropriate for Codex intake.

### Evaluator calibration

A separate framework-local calibration contract is justified now because it closes a governance gap without requiring runtime code. It defines when an LLM judge may be treated as calibrated and prevents an unvalidated judge from becoming hidden release authority.

### Source recovery

A public/read-only source-recovery policy is justified now as a durable acquisition boundary. It converts the useful part of browser-to-direct-client prior art into a safe framework-local ladder without authorizing scraping around access controls or creating a new canonical data owner.

### Planning / context survival

No implementation is justified yet. The correct next evidence is an observed framework-local context-loss incident or measurable recovery-cost problem. Until then, adding another planning state system would be architecture inflation.

## Admission decisions

```yaml
keep_current_framework_architecture: YES
direct_install_15_skill_stack: NO
direct_install_external_eval_framework: NO
skill_quality_runtime_harness: CODEX_RESEARCH_CANDIDATE
evaluator_calibration_contract: INTERNAL_IMPLEMENTATION
public_read_only_source_recovery_policy: INTERNAL_IMPLEMENTATION
mcp_agent_usability_refinement: INTERNAL_CONTRACT_REFINEMENT_ONLY
planning_with_files_integration: HOLD_FOR_OBSERVED_GAP
new_market_engine: NO
new_shadow_layer: NO
new_portfolio_authority: NO
new_market_threshold_or_weight: NO
```

## Falsifiers / kill conditions

- Kill the runtime-harness implementation if it requires an external service or package to perform the core deterministic gate, cannot isolate workspace side effects, or cannot preserve critical-regression hard blockers.
- Keep LLM-judge verdicts advisory if calibration evidence is missing, stale or incompatible with the judge/model version used.
- Kill a recovered web endpoint as a collector candidate if access depends on bypassing controls, mutating calls, unstable session credentials, unresolvable terms/access uncertainty, or provenance cannot be preserved.
- Do not adopt planning-with-files style state unless real Investering tasks demonstrate repeated context-loss or recovery-cost failures that existing handoff/receipt machinery does not solve.
