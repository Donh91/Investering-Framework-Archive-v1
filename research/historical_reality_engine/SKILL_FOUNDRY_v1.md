# HRE Skill Foundry | Generate only useful repeatable skills

**Proposal state:** OWNER_APPROVAL_PENDING. Automatic skill proposal allowed only after program activation; automatic registration/merge is NOT authorized.
**Canonical existing skill source:** .agents/skills/research-parallel-lanes/SKILL.md
**Canonical registry:** 00_ARCHIVE_CONTROL/SKILL_REGISTRY.md
**Machine router:** 00_ARCHIVE_CONTROL/SKILL_ROUTING_INDEX.json
**Existing evaluator:** .agents/skills/skill-quality-gate/SKILL.md
**Existing skills candidate area:** 07_PROMPTS_AND_AGENTS/skill_quality_gate/candidates/
**Existing Codex intake if bounded code defect:** .agents/skills/codex-intake/SKILL.md

## Why, when and what to invent

A new skill may be proposed when an actually repeated historical research procedure has a specific quality or throughput problem and can be evaluated better than a simple runbook update or existing skill. Novel-sounding skills without reproduced distinct value are REJECTED. Examples to consider, not permissions or existing claims:
- vintage-clock-gate: prevent use of future/revised macro, venue and feature values at reference timestamp.
- crisis-negative-control-matcher: deterministic matched quiet-case / false-alarm selection.
- historical-episode-replay: event cutoff lock, original versus retro source semantics, completeness.
- cn-seven-day-range-tournament: 7-day immutable low/high/close scoring and sharpness.
- skill-promotion-evidence-binding: compare skill vs no-skill on actual independent cases, release readback.
- grok-independent-replay-review: source-bounded red-team that cannot see later truth as pre-event evidence.
- shadow-forward-translation: source-verified retrospective lesson to prospective frozen due-only test without direct rule promotion.

## The foundry pipeline (builds an auditable chain, not self-modifying production)

1. DISCOVER: Program owner records repeated manual procedure, measurable baseline failure, original existing skill overlap, expected marginal gain and an evidence/latency/cost objective.
2. REJECT_OR_CANDIDATE: If same behavior already exists, propose a small change to that skill under its current owner. Otherwise create a **candidate only** under 07_PROMPTS_AND_AGENTS/skill_quality_gate/candidates/hre/<slug>/SKILL.md with frontmatter, positive and negative triggers, owner, scope and no authority escalation.
3. BENCHMARK: Freeze baseline no-skill task and candidate, exact SHA, representative crisis and noncrisis cases, counterexamples, permission/PII/source boundary and endpoint correctness. Run the existing skill-quality-gate separately from the author and require actual independent evidence. Static inspection alone = STATIC_ONLY, not proven quality benefit.
4. RED TEAM: Grok as optional independent falsifier or a different verified evaluator, never fake GitHub approval or new identity. If judge calibration is material, follow current evaluator-calibration contract.
5. ADJUDICATE: Original skill owner decides ACCEPT_FOR_PR / REVISE / SHADOW_ONLY / REJECT / DUPLICATE, with measured benefit and negative tests. No fully automatic skill promotion, no auto broadening GitHub/paid/trading authority.
6. PUBLISH: Only after actual accepted PR/CI/qualified merge, place exact skill at .agents/skills/<slug>/SKILL.md, update 00_ARCHIVE_CONTROL/SKILL_REGISTRY.md and its derived SKILL_ROUTING_INDEX.json, validate current script scripts/agent_skills/validate_skill_architecture.py and normal trigger routing. Add small agents/openai.yaml only where correct current registry expects it, not because another agent wants it.
7. REUSE: Other **repository-aware** threads first resolve canonical-context-router and registry, then read the relevant merged SKILL.md. This is GitHub-local discoverability, not automatic installation as a ChatGPT-global skill, plugin or unconnected AI agent.
8. MONITOR: Attach version, baseline metrics, preserved failure cases, release SHA, owner and rollback conditions. After observed regressions, propose a qualified revert/retirement PR. Previous versions remain recoverable.

## Must-pass quality and safety tests

- An irrelevant request does not trigger the new skill.
- Research source content cannot execute as agent instructions or gain private/API permissions.
- Skill cannot write to main or self-approve PRs.
- One copied historical winning event cannot be treated as independent repeated edge.
- Missing original-first-known information stays UNKNOWN.
- A candidate cannot automatically alter Official Kompas forecasts, CN freeze, Shadow/Official authority, production risk severity or portfolio action.
- A skill improvement claim requires baseline-without-skill and a held-out case, not only more output or clever wording.
- A skill from the HRE folder must follow the same quality gate as any other skill; HRE does not create a bypass.
- Repository-level indexing is validated on current main after merge; external chats must actually load the repository route.

## Durable tracking

Store proposed recipe, evaluation matrix, negative results and source SHA in the existing skill-quality-gate candidate/receipt structure, plus a short pointer in the relevant HRE original research finding. Do not create a second skill registry or shadow service. The HRE queue may reference skill-founding task HR-013, but the official registry alone says what is active.
