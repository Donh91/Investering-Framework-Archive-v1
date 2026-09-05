# Astra Agent Legibility and Skill Compression Audit v1

**Dato:** 2026-09-06  
**Status:** READ_ONLY_QUALIFICATION_MISSION  
**Authority:** NONE BY ITSELF  
**Område:** agent routing / skill architecture / context compression / repository legibility  
**Primary folder:** `07_PROMPTS_AND_AGENTS/astra/`  
**Depends on:** `AGENTS.md`, `00_ARCHIVE_CONTROL/SKILL_REGISTRY.md`, `00_ARCHIVE_CONTROL/SKILL_ROUTING_INDEX.json`, the six active `.agents/skills/*/SKILL.md` files  

## Mission

Determine whether a future strong repository-aware model can discover, understand, compose and safely evolve the active skill stack with minimal ambiguity, unnecessary context and authority risk.

This is an audit of **agent legibility**, not a request to redesign the framework and not authorization to rewrite the skills.

Start in:

```text
MODE = READ_ONLY_QUALIFICATION
SOURCE_WRITE_AUTHORITY = NONE
RECOVERY_DESTRUCTIVE_AUTHORITY = NEVER
NEW_SKILL_AUTHORITY = NONE
```

## Why this mission exists

The active skill stack already has strong governance and authority boundaries. The remaining question is whether those protections are expressed in the most legible and context-efficient way for Astra and future agents.

The target is not fewer words at any cost. The target is:

```text
less irrelevant context
+ faster owner discovery
+ clearer side-effect boundaries
+ no loss of safety or authority semantics
+ no duplicate agent layer
```

## Mandatory inputs

Read in this order:

1. `AGENTS.md`
2. `00_ARCHIVE_CONTROL/SKILL_REGISTRY.md`
3. `00_ARCHIVE_CONTROL/SKILL_ROUTING_INDEX.json`
4. `.agents/skills/canonical-context-router/SKILL.md`
5. `.agents/skills/developer-source-research/SKILL.md`
6. `.agents/skills/research-lab-red-team/SKILL.md`
7. `.agents/skills/prospective-evidence-ledger/SKILL.md`
8. `.agents/skills/codex-intake/SKILL.md`
9. `.agents/skills/archive-governance/SKILL.md`
10. each `.agents/skills/*/agents/openai.yaml`
11. `scripts/agent_skills/validate_skill_architecture.py`

Do not infer repository state from this mission file. Resolve current main and current owners first.

## Audit dimensions

Score every active skill on the following dimensions:

### 1. Discoverability

Can an agent reliably know that the skill exists and when it applies without loading unrelated prose?

### 2. Authority visibility

Can an agent immediately see what the skill may and may not decide, write, score, promote or execute?

### 3. Context locality

Is the always-loaded SKILL body limited to instructions needed on most invocations, while rare or domain-specific detail can be loaded only when relevant?

### 4. Impact predictability

Before invoking the skill, can an agent predict whether the operation is read-only, externally retrieving, queue-writing, evidence-writing or repository-writing?

### 5. Intent signalling

Do triggers and `do_not_use_for` rules separate nearby skills cleanly enough to avoid accidental composition or duplicate work?

### 6. Hidden knowledge

Does safe execution depend on unwritten assumptions, prior chat context, one model's memory or obscure files that are not discoverable from the current routing surfaces?

### 7. Composition clarity

Can an agent determine the correct sequence among router, task-specific reasoning, developer research, evidence ledger, red team, Codex intake and archive governance?

### 8. Progressive-disclosure quality

Identify sections that are large, conditional and mechanically separable into shallow `references/` files without weakening the default safety envelope.

## Progressive-disclosure rule

A section is a valid extraction candidate only when **all** of these are true:

```yaml
needed_on_minority_of_invocations: YES
semantics_can_be_preserved_verbatim_or_losslessly: YES
safe_trigger_for_loading_reference_is_clear: YES
core_authority_boundary_remains_in_SKILL: YES
core_failure_semantics_remain_in_SKILL: YES
reference_depth_after_change: ONE_LEVEL
new_parallel_owner_created: NO
```

Never move these behind an optional reference solely to save tokens:

- write authorization requirements;
- no-direct-main rule;
- destructive-authority separation;
- no self-promotion / no portfolio authority;
- missing-data-as-UNKNOWN rule when material to the skill;
- frozen-field integrity for prospective evidence;
- the skill's primary stop/fail-closed conditions;
- canonical-owner precedence.

## Current hypotheses to test, not conclusions

The following are starting hypotheses and must be disproved or confirmed from current main:

1. `archive-governance` may contain conditional document-normalization, backup and high-impact detail that can be progressively disclosed while keeping branch/write safety in the core.
2. `prospective-evidence-ledger` may contain domain-specific Transmission Matrix and optional scoring/coverage detail that can move to references while preserving causal, maturity, lineage and frozen-field rules in the core.
3. `canonical-context-router` may have DATA PING-specific detail that should be conditional, but its mandatory owner-resolution and conflict logic should remain core.
4. `developer-source-research` is already compact enough that a refactor may have negative value.
5. `research-lab-red-team` is likely compact enough that routing metadata may be more valuable than body compression.
6. `codex-intake` may benefit from metadata/frontmatter normalization, but any rewrite must preserve its current queue and CODEX_READY authority boundary.

## Finding Disproof Pass

Every proposed finding must survive a separate disproof pass before it is accepted.

For each finding:

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
context_saving_or_legibility_gain:
```

Reject findings that are merely stylistic preference, file-count preference or admiration of another repository's architecture.

## New-skill prohibition

Do not recommend a seventh permanent skill unless the candidate satisfies the existing `SKILL_REGISTRY.md` expansion rule:

```text
failure mode observed
repeated task frequency
why existing skills cannot cover it
inputs
outputs
validation loop
authority boundary
kill criterion
```

A one-off legibility audit is not enough to justify a new skill.

## Machine-routing audit

Evaluate `00_ARCHIVE_CONTROL/SKILL_ROUTING_INDEX.json` as a derived surface only.

Verify:

- it never claims canonical authority;
- every skill is present exactly once;
- every referenced SKILL and metadata path exists;
- side-effect levels are explicit;
- write/queue-capable skills do not allow implicit invocation;
- the Markdown registry remains the canonical owner;
- machine metadata does not contain market thresholds, scoring rules or live state;
- `agents/openai.yaml` metadata aligns with the routing index;
- no metadata field silently broadens skill authority.

## Validator audit

Run or independently review:

```bash
python scripts/agent_skills/validate_skill_architecture.py
```

Treat validator PASS as structural evidence only. It does not prove the routing is scientifically correct or that a skill should be kept.

Identify false-positive and false-negative cases for the validator before proposing stronger enforcement or CI integration.

Do **not** add or modify a GitHub Actions workflow during this read-only mission.

## Required output

Return:

```markdown
# ASTRA AGENT LEGIBILITY VERDICT

## Current main SHA

## Active skill stack reconstructed from authority

## Routing and authority map

## Skill-by-skill legibility scorecard

## Progressive-disclosure candidates

## Findings rejected by the disproof pass

## Machine-routing index assessment

## agents/openai.yaml assessment

## Validator assessment

## Hidden-knowledge risks

## Duplicate or unnecessary agent concepts

## Changes that would make the system worse

## Ranked minimal-change recommendations

## Recommended first patch, if any

## Explicit NO-CHANGE decisions
```

## Acceptance standard

A strong audit should be able to conclude `NO_CHANGE` for some or all skills.

The mission succeeds when it improves confidence in **what should remain untouched** as much as in what should change.

Do not optimize for maximum compression, maximum file count or maximum agent autonomy. Optimize for minimum ambiguity and minimum unnecessary context at unchanged authority.
