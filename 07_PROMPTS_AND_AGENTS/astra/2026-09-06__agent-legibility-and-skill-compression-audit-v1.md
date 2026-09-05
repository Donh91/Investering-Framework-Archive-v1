# Astra Agent Legibility and Skill Compression Addendum v1

**Dato:** 2026-09-06  
**Status:** READ_ONLY_AUDIT_ADDENDUM  
**Authority:** NONE BY ITSELF  
**Parent mission:** `07_PROMPTS_AND_AGENTS/astra/ASTRA_SKILLS_AND_AGENTS_AUDIT_MISSION_v1.md`  
**Scope:** only the new machine-routing metadata, OpenAI-facing skill metadata, Finding Disproof Pass and progressive-disclosure decisions  

## Non-duplication rule

This file is **not** a second Astra skills mission.

Run the existing `ASTRA_SKILLS_AND_AGENTS_AUDIT_MISSION_v1.md` as the owner mission. Use this addendum only when that mission reaches metadata routing, context efficiency, skill-body compression or agent legibility.

Do not create a seventh permanent skill from this addendum.

## New artifacts to audit

Read current main first, then inspect:

```text
00_ARCHIVE_CONTROL/SKILL_ROUTING_INDEX.json
.agents/skills/canonical-context-router/agents/openai.yaml
.agents/skills/developer-source-research/agents/openai.yaml
.agents/skills/research-lab-red-team/agents/openai.yaml
.agents/skills/prospective-evidence-ledger/agents/openai.yaml
.agents/skills/codex-intake/agents/openai.yaml
.agents/skills/archive-governance/agents/openai.yaml
scripts/agent_skills/validate_skill_architecture.py
```

`00_ARCHIVE_CONTROL/SKILL_REGISTRY.md` remains the canonical skill registry. The JSON routing index and `agents/openai.yaml` files are discovery/interface surfaces only and must never override repository authority.

## Additional agent-legibility dimensions

In addition to the parent mission's frozen dimensions, explicitly test:

```yaml
discoverability:
authority_visibility:
context_locality:
impact_predictability:
intent_signalling:
hidden_knowledge:
progressive_disclosure_quality:
```

Interpretation:

- **discoverability**: can a fresh model reliably find the correct skill?
- **authority_visibility**: can it immediately see what the skill may not decide, score, promote or write?
- **context_locality**: is always-loaded text limited to instructions needed on most invocations?
- **impact_predictability**: can the agent predict READ_ONLY vs external retrieval vs queue/evidence/repository write before invocation?
- **intent_signalling**: do triggers and `do_not_use_for` rules prevent overlap?
- **hidden_knowledge**: does safe execution depend on chat memory or obscure unlinked files?
- **progressive_disclosure_quality**: can rare conditional detail move to shallow references without weakening core safety?

## Machine-routing safety checks

Verify all of the following:

```yaml
routing_index_status_is_derived_only: YES
routing_index_authority_is_none: YES
markdown_registry_remains_owner: YES
all_six_active_skills_present_exactly_once: YES
all_skill_paths_exist: YES
all_metadata_paths_exist: YES
side_effect_levels_explicit: YES
write_or_queue_capable_skills_implicit_invocation: MUST_BE_NO
market_thresholds_or_live_state_copied_into_metadata: MUST_BE_NO
metadata_broadens_skill_authority: MUST_BE_NO
```

Current intended implicit-routing policy is deliberately asymmetric:

```text
canonical-context-router -> allowed, read-only
 developer-source-research -> allowed, read-only external retrieval
 research-lab-red-team -> explicit
 prospective-evidence-ledger -> explicit
 codex-intake -> explicit
 archive-governance -> explicit
```

Treat any proposal to make a write-, queue- or evidence-mutation-capable skill implicitly invokable as a security finding requiring strong justification.

## Progressive-disclosure gate

A section may be extracted from a SKILL body into `references/` only when every field below is satisfied:

```yaml
needed_on_minority_of_invocations: YES
semantics_preserved_losslessly: YES
safe_reference_trigger_is_clear: YES
core_authority_boundary_remains_in_SKILL: YES
core_failure_semantics_remain_in_SKILL: YES
reference_depth_after_change: ONE_LEVEL
parallel_owner_created: NO
measurable_context_or_legibility_gain: YES
```

Never move these behind an optional reference merely to reduce tokens:

- explicit write authorization;
- no-direct-main rule;
- destructive-authority separation;
- no self-promotion / no portfolio authority;
- frozen-field integrity for prospective evidence;
- material missing-data-as-UNKNOWN rules;
- primary stop/fail-closed conditions;
- canonical-owner precedence.

Starting hypotheses, not conclusions:

1. `archive-governance` and `prospective-evidence-ledger` are the strongest compression candidates because their current bodies exceed the validator warning threshold.
2. `developer-source-research` and `research-lab-red-team` may already be compact enough that rewriting them has negative value.
3. `canonical-context-router` may contain conditionally loadable DATA PING detail, but owner resolution and conflict logic should remain core.
4. `codex-intake` may benefit from metadata/frontmatter normalization, but its queue and `CODEX_READY` authority boundary must remain unchanged.

## Finding Disproof Pass

Every proposed architecture finding must be challenged before it is accepted.

For each finding record:

```yaml
finding_id:
claim:
agent_failure_mode_if_unfixed:
evidence:
counter_evidence_searched:
strongest_reason_finding_may_be_false:
disproof_result: SURVIVES | REJECTED | NARROWED
smallest_practical_change:
change_not_needed_if:
authority_risk:
measurable_context_or_legibility_gain:
```

Reject findings that reduce to stylistic preference, file-count preference or admiration of another repository.

## Validator scope

Review or run:

```bash
python scripts/agent_skills/validate_skill_architecture.py
```

The validator is intentionally structural. Its PASS means only that routing metadata, file presence and side-effect policy are internally consistent.

It does **not** prove:

- that a skill should be kept;
- that routing is scientifically optimal;
- that market/framework semantics are correct;
- that progressive disclosure is beneficial;
- that CI enforcement should be added.

Before proposing CI integration, identify likely validator false positives and false negatives. Do not modify GitHub Actions during the first read-only audit.

## Required addendum output

Append these sections to the parent mission's report:

```markdown
## Machine-routing index assessment

## agents/openai.yaml assessment

## Agent-legibility findings

## Progressive-disclosure candidates

## Findings rejected or narrowed by the disproof pass

## Validator false-positive / false-negative risks

## Explicit NO-CHANGE decisions
```

A valid outcome may be that no SKILL body should be changed.
