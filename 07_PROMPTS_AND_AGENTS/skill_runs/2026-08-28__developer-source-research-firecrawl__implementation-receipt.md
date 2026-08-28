# Developer Source Research and Firecrawl Developer Index Implementation Receipt

**Date:** 2026-08-28
**Status:** RECEIPT_PASS_LIVE_SMOKE_VERIFIED
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

The official documentation states that the index retrieves public issues, merged pull requests, READMEs and curated documentation; matched passages include stable source URLs; developer search costs two credits per ten results; and keyless use is available subject to rate limits. The upstream skill uses the Developer Index first for primary developer sources and general web search as fallback.

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
plugin_tool_visible_in_current_session: YES
keyless_rest_smoke_historical: BLOCKED_SUSPICIOUS_SHARED_IP
live_firecrawl_result_smoke: PASS
load_bearing_sources_opened: PASS
credential_requested_or_persisted: NO
```

The original implementation session could not call the installed plugin and a direct keyless REST smoke was blocked by Firecrawl's shared-IP guard. That limitation is now superseded for tool availability: in a later callable session on 2026-08-28, `firecrawl_developer_search` returned ranked Developer Index results successfully.

The live result was verified against current upstream sources rather than accepted from the matched passage alone:

- current Firecrawl Developer Index documentation confirms the dedicated developer-search surface, source classes and result contract;
- merged `firecrawl/firecrawl-mcp-server#344` confirms the MCP implementation of `firecrawl_developer_search` and the `developer` search category;
- current `firecrawl/benchmark-devdex` README confirms the benchmark tracks, deterministic scoring, public/held-back split and published cost estimate.

No credential, private repository content, restricted provider value or unredacted private log was sent to Firecrawl.

## Qualified pilot use 1 of 10

```yaml
run_date: 2026-08-28
question_class: AGENT_SKILL
question: Evaluate whether Firecrawl Developer Index / DevDex should be used in the Investering framework and verify the callable MCP behavior before relying on the pilot.
firecrawl_tool_status: AVAILABLE
query_sanitized: YES
primary_source_hit: YES
load_bearing_source_opened: YES
current_behavior_verified: YES
fallback_used: GITHUB
incremental_over_native_route: YES
source_identity_mismatch: NO
restricted_or_credential_incident: NO
authority_incident: NO
implementation_effect: LIVE_SMOKE_CLOSED_AND_PILOT_REMAINS_READ_ONLY
```

Incremental value is credited because the Developer Index surfaced the exact current Firecrawl documentation and merged MCP implementation needed to resolve the tool contract, reducing uncertainty before native GitHub readback verified the sources. This does not count as evidence that Firecrawl should become a production dependency.

Pilot progress after this use:

```yaml
qualified_uses_completed: 1
qualified_uses_required: 10
verified_source_bundles: 1
incremental_over_native_uses: 1
availability_failures_counted_in_qualified_uses: 0
incidents: 0
keep_decision: NOT_YET_ELIGIBLE
```

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
implementation_pull_request: 631
implementation_pull_request_ci: PASS
implementation_merge_sha: 69bc36f5660bbb48c0f6de12368aca41ef3b2a88
live_smoke_followup: PASS
merge_policy: PR_AND_PASSING_CHECKS_REQUIRED
```
