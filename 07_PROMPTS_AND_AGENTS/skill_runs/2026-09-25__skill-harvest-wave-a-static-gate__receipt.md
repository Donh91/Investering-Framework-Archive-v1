# Skill Harvest Wave A - Static Gate Receipt

**Date:** 2026-09-25  
**Status:** RECEIPT  
**Evaluation mode:** `STATIC_ONLY`  
**Activation status:** `BLOCKED_PENDING_BLIND_RUNTIME_AB`  
**Baseline commit:** `5e1bc63858f2cc6a7a4895845633f412d0f67616`  
**Task branch:** `agent/task-20260925-skill-harvest-wave-a`

## Scope

Wave A materializes the first three analytical mechanisms from `SKILL_HARVEST_CANDIDATES_v1.json` as non-active candidate skill files:

1. cheapest decisive falsifier;
2. source independence groups;
3. bounded source-of-source chasing.

The active skill files are intentionally unchanged.

## Immutable baseline bindings

| Skill | Active path | Baseline blob |
|---|---|---|
| research-lab-red-team | `.agents/skills/research-lab-red-team/SKILL.md` | `20a990ddd603953b965c17101dad873e603c158b` |
| meme-alpha-supervisor | `.agents/skills/meme-alpha-supervisor/SKILL.md` | `4542c642043c88226b98fb15703d5228bb3cb8b7` |
| developer-source-research | `.agents/skills/developer-source-research/SKILL.md` | `66557167d9204dd165cce35d2e8320ccc2459be0` |

Fresh branch readback confirmed all three active paths have exactly the same blob SHA as the baseline commit.

## Candidate bindings

| Mechanism | Candidate path | Candidate blob |
|---|---|---|
| cheapest decisive falsifier / red team | `07_PROMPTS_AND_AGENTS/skill_quality_gate/candidates/2026-09-25-wave-a/research-lab-red-team__cheapest-decisive-falsifier/SKILL.md` | `b797f4b380b44abdfe4217ce44ec9a338f427918` |
| cheapest decisive falsifier / Alpha Lab | `07_PROMPTS_AND_AGENTS/skill_quality_gate/candidates/2026-09-25-wave-a/meme-alpha-supervisor__cheapest-decisive-falsifier/SKILL.md` | `0799410ab57b13acb7d4b7dc0920175d92047a47` |
| source independence groups | `07_PROMPTS_AND_AGENTS/skill_quality_gate/candidates/2026-09-25-wave-a/developer-source-research__source-independence-groups/SKILL.md` | `c050cc2adbe3e9de6c3fea9b0aa21a89e8da6c50` |
| bounded source chasing | `07_PROMPTS_AND_AGENTS/skill_quality_gate/candidates/2026-09-25-wave-a/developer-source-research__bounded-source-chasing/SKILL.md` | `eee6b464efec1540d1a66e2b74350dc0b2a33fbb` |

## Frozen evaluation cases

Case-set blob after Wave A additions: `a3bd9890916b7c2b03be977c395c8db86db7bc60`.

Added cases:

- `redteam-cheapest-falsifier-004`
- `memealpha-cheapest-falsifier-001`
- `devsource-independence-004`
- `devsource-sourcechain-005`

These include negative semantics for unavailable evidence, authority boundaries, source-dependence and bounded-crawl behavior.

## Static checks

```yaml
candidate_names_match_active_skills: PASS
active_skill_files_unchanged: PASS
cheapest_falsifier_is_decisive_not_merely_cheap: PASS
missing_or_unavailable_evidence_remains_unknown: PASS
passed_falsifier_does_not_prove_whole_thesis: PASS
source_independence_counts_evidence_roots_not_domains: PASS
bounded_source_chase_has_depth_and_retrieval_cap: PASS
blocked_primary_source_is_coverage_gap_not_disproof: PASS
portfolio_or_trading_authority_added: NO
canonical_promotion_authority_added: NO
self_merge_authority_added: NO
third_party_code_imported_or_executed: NO
```

## Skill Quality Gate result

```yaml
SKILL_QUALITY_GATE_VERDICT:
  evaluation_mode: STATIC_ONLY
  baseline_ref: 5e1bc63858f2cc6a7a4895845633f412d0f67616
  candidate_ref: agent/task-20260925-skill-harvest-wave-a
  case_set_ref: a3bd9890916b7c2b03be977c395c8db86db7bc60
  evaluator_separated: YES_FOR_STATIC_REVIEW
  evaluator_calibration_state: NOT_USED
  deterministic_blockers: []
  critical_regressions: []
  trigger_result: NOT_EXECUTED
  correctness_result: NOT_EXECUTED
  authority_result: PASS
  autonomy_result: NOT_EXECUTED
  safety_result: PASS
  cost_context_result: UNKNOWN
  baseline_without_skill_result: NOT_EXECUTED
  completion_verification: PARTIAL
  verdict: BLOCKED
  missing_evidence:
    - BLIND_BASELINE_VS_CANDIDATE_RUNTIME_AB
    - BEHAVIORAL_CORRECTNESS_ON_FROZEN_CASES
    - COST_OR_TOKEN_DELTA_IF_AVAILABLE
  next_evidence_action: Run blind baseline-vs-candidate runtime A/B through the existing skill-quality harness with a separately authorized trusted live adapter.
```

The `BLOCKED` verdict is intentional. The candidates passed the static safety/governance gate, but the local quality contract forbids `ACCEPT_CANDIDATE` from static inspection when the claimed benefit is behavioral.

## Queue binding

Candidate queue blob: `1d55f7c1175acf734728538124117e0dc8e91ce4`.

No production skill is activated by this receipt. No market or portfolio semantics change.
