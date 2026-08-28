# Developer Source Research and Firecrawl Developer Index Implementation Receipt

**Date:** 2026-08-28
**Status:** RECEIPT_PASS_WITH_LIVE_SMOKE_PENDING
**Scope:** repository-local developer-source routing / Firecrawl Developer Index / DevDex evaluation
**Authority:** research infrastructure only
**Primary owner:** `00_ARCHIVE_CONTROL/SKILL_REGISTRY.md`

## Decision

```yaml
verdict: PILOT_ACTIVE_READ_ONLY
implementation: NEW_REPOSITORY_LOCAL_SKILL
new_engine: false
new_market_sensor: false
market_provider_queue_change: false
scheduled_workflow_added: false
production_dependency_added: false
credential_added: false
data_ping_change: false
framework_semantics_change: false
portfolio_authority: false
```

The Firecrawl Developer Index is relevant for upstream technical research used by Codex and repository-aware agents. It is not relevant as a market-data source, framework sensor or Daily/Weekly Director input.

## Existing-owner and redundancy result

No existing skill owned external developer-source retrieval. `canonical-context-router` resolves internal repository authority, `research-lab-red-team` evaluates claims, and `codex-intake` packages reproducible defects after they are found. The existing MCP Connection Evaluation Program is a sequential market-provider queue and is intentionally unchanged.

The implementation therefore adds one bounded routing skill and updates the existing skill registry. It does not add a second MCP program, API gateway, scheduled collector or persistent result store.

## Upstream evidence frozen for the evaluation

```yaml
firecrawl_developer_index_docs: https://docs.firecrawl.dev/features/developer
firecrawl_official_skill_repository: https://github.com/firecrawl/cli/tree/main/skills/firecrawl-developer-index
firecrawl_official_skill_commit: 86aaf06cb139029ff5ad2a249670f42b01d40b13
devdex_repository: https://github.com/firecrawl/benchmark-devdex
devdex_commit: 24e60473887d33960bf155a9e73affcd07d288a3
devdex_license: MIT
devdex_public_items: 594
devdex_full_items_claimed: 1179
```

The official documentation states that the index retrieves public issues, merged pull requests, READMEs and curated documentation; matched passages include stable source URLs; most sources are refreshed daily; developer search costs two credits per ten results; and keyless use is rate-limited. The upstream skill uses the Developer Index first for primary developer sources and general web search as fallback.

## Benchmark interpretation

Firecrawl reports DevDex Recall@10 of `0.631` overall against native web search at `0.454`, with strongest relative value on the issue/pull-request track. The benchmark uses deterministic URL matching, a no-tool memorization gate, equal tool depth and a held-back half-dataset.

These results support a pilot, not unconditional adoption:

- Firecrawl supplies both the evaluated product and the published benchmark.
- Only 594 of 1,179 items are public.
- The reported driver is Claude Opus 4.8, not this framework's Codex/Work execution environment.
- DevDex tests developer retrieval, not implementation correctness or framework-specific decision value.
- The published overall lead does not imply a statistically distinct win on every individual track.
- A full arm is reported to cost about USD 165, so no recurring full benchmark is justified for this personal framework.

## Local verification and limitation

```yaml
upstream_repositories_cloned: PASS
upstream_commits_recorded: PASS
public_dataset_count_check: PASS
official_skill_inspected: PASS
full_devdex_execution: NOT_RUN_EXTERNAL_DEPENDENCIES_AND_COST
installed_plugin_reported_by_user: YES
plugin_tool_visible_in_active_work_session: NO
keyless_rest_smoke: BLOCKED_SUSPICIOUS_SHARED_IP
live_firecrawl_result_smoke: PENDING_NEXT_CALLABLE_SESSION
```

The installed Firecrawl plugin did not become callable inside the already-active Work session. A direct keyless REST smoke returned Firecrawl's shared-IP rejection and no search result. No credential was requested, copied or persisted. The skill therefore treats Firecrawl availability as optional and falls back to native GitHub and official web sources.

## Pilot falsifier and kill criteria

```yaml
minimum_qualified_uses: 10
keep_verified_source_bundles_min: 8
keep_incremental_over_native_min: 3
modify_if_firecrawl_unavailable_gt: 5_of_10
kill_if_incremental_value_lt: 2_of_10
immediate_suspend_on:
  - restricted_or_credential_disclosure
  - uncorrected_source_identity_mismatch
  - local_or_current_upstream_authority_replaced_by_index_result
  - market_or_portfolio_authority_created
```

## Paths

```yaml
created:
  - .agents/skills/developer-source-research/SKILL.md
  - 07_PROMPTS_AND_AGENTS/skill_runs/2026-08-28__developer-source-research-firecrawl__implementation-receipt.md
updated:
  - 00_ARCHIVE_CONTROL/SKILL_REGISTRY.md
  - scripts/governance/validate_cross_repo_agent_context.py
canonical_index_changed: false
index_addendum_created: false
addendum_registry_changed: false
high_impact_gate: NOT_REQUIRED
backup_product: NONE
source_main_sha: aa680daebd8a4d6972da56d0ae33eca3bc8baae1
task_branch: agent/task-20260828-developer-source-research
branch_assertion: PASS
```

Discoverability is provided through the existing canonical operational Skill Registry, which is already a mandatory repository read. No canonical-index edit or new addendum is required.

## Validation result

```yaml
skill_creator_quick_validate: PASS
python_compile_cross_repo_validators: PASS
cross_repo_agent_context_validator: PASS
round3_runtime_reconciliation: PASS
path_and_registry_assertions: PASS
git_diff_check: PASS
declared_path_count: 4
pull_request_ci: PENDING_AT_RECEIPT_CREATION
merge_policy: PR_AND_PASSING_CHECKS_REQUIRED
```
