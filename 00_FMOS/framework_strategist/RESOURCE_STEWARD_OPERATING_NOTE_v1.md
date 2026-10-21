# Resource Steward v1 | existing Strategist and Supervisor only

**19 October 2026.** Scope: no new worker, cron, queue, paid model, credential, budget, approval power or primary truth source. The existing Framework Learning Supervisor already runs. This change adds a local deterministic resource advisory within that one existing job.

## Immediate state and hard limits
- Owner screenshot: GitHub Actions at 90% of 3,000 included minutes; 300 remain until 1 November. Codex Cloud 29% remaining, resets in about six days. These are *owner-reported snapshots*, not live authenticated GitHub/Codex billing.
- **GitHub Actions** standard hosted runners for public repositories are not the same billed pool as private runner usage. Private `secrets` and `Meme-Alpha-Lab` dominate relevant consumption. Skipped jobs are not treated as completed billed jobs.
- **Codex Cloud** passive delegation is DISABLED by owner instruction. Neither `CODEX_READY`, PR review comments, environment creation nor a GitHub `issue_comment` is authorization to start Codex Cloud. A single explicit bounded work packet must originate from the named Supervisor or a Chat agent and pass value, budget, source, freshness, independence and retry gates. No passive Cloud task or periodic poll.
- **OpenAI API** is a *separate* preexisting budgeted lane. It may be preferred to Codex Cloud only when an existing approved task, correct model/cap and independent receipts authorize it. No automatic displacement of one exhausted quota to another.
- **ChatGPT Work credits** are protected; this stage must not invoke Work.

## Current implementation
`scripts/framework_intelligence/resource_budget_guard_v1.py` is pure local/no-network and produces an advisory only. It is run before Strategist in the EXISTING `.github/workflows/framework-learning-supervisor.yml` during its ordinary runs. There is **no additional schedule**. Strategist ingests a SHA256-bound `FRAMEWORK_RESOURCE_BUDGET_ADVISORY_v1` as optional evidence. Critical status gets top priority among its maximum three questions; Supervisor retains existing execution governance. There is no automatic Cloud disabling switch in the Codex account; this document and advisory alone cannot change account-level host behavior.

Input contract: the existing owner may supply a fresh `RESOURCE_USAGE_SNAPSHOT_v1` with `as_of_utc`, `source_type`, numeric `github_actions.used_minutes`, `github_actions.included_minutes`, `codex.remaining_pct`. **Do not commit personal billing, tokens or private provider values to the public repository.** Import a snapshot only via an already authorized source/restricted receipt; absent credentials or verified billing, status is UNKNOWN after the temporary owner-declared conservation window. Source age >24h, future timestamp, NaN/Infinity, malformed schema, outside-root path or positive spending authority fail closed.

The policy `RESOURCE_CONSERVATION_POLICY_v1.json` records temporary conservation until 2026-11-01 for Actions, and through 2026-10-25 for Codex, without publishing account-level usage. It does not claim the percentages are continuously measured and it does not reopen cloud dispatch when those dates expire: unknown budget remains unknown.

## Release and safety
No future Chat/cloud task may bypass protected checks, scientific no-hindsight contracts, Round 3 collection-only policy, immutable records, independent recovery or required PR review. Actions budget status is NOT a permission to silently discard critical source captures. A changed collector cadence is logged as degraded coverage, not inferred continuous monitoring.

The resource advisor has **zero authority** to update workflows, deactivate data collectors, change cost budgets, pay, start agents, merge PRs, accept research claims or notify users without existing authorization. It may only recommend: NORMAL, CONSERVE, CRITICAL or UNKNOWN, with an evidence-bound why and an existing owner. The canonical Strategist/Supervisor is the only consumer.

### Conditions for actual live resource governance
1. Read current budget from authenticated GitHub billing or owner-provided evidence. The GitHub repository-scoped token does not itself prove access to account billing or Codex quota.
2. Read current private workflow run durations; distinguish scheduled runners, jobs skipped, free public runners and billable private Linux runners. Project monthly burn using verified billing intervals.
3. Compare planned task business value, scientific/operational criticality, expected cost, source continuity and remaining time to reset. Require a known owner-issued bounded Cloud mission. Unknown -> no new paid work.
4. Send a compact prioritized recommendation to existing Supervisor and Strategist, not a new async agent. Determine whether a spike is temporary approved work or structural repeated spend by matching immutable task IDs, start/end and actual job receipts.
5. Demonstrate source-limited proof and actual savings on postmerge billing readback before claiming the optimization is effective. No autonomous stop of a required collector.

## External billing action (not executable through the available GitHub connector)
Set a hard GitHub Actions budget in account Billing & Licensing, if no extra costs are allowed; or explicitly approve a small capped overage while collection is protected. Available repository tools cannot mutate account billing. A repo change alone does not impose a spend ceiling. Owner retains that choice.

## Observed tradeoff
**Actual verified same-day release status:** Private `secrets#198` MERGED (Moonshot 36/day -> 2/day, background schedule paused), `secrets#199` MERGED (three Round 3 collectors down to 2/day), and `Meme-Alpha-Lab#184` MERGED (Census hourly -> 2/day; automatic issue-comment wake paused). All three changes are visible on their respective `main` branches after merge. Scientific/first-seen coverage is degraded by design. No verified account billing readback yet, so lower scheduled run counts are not a certified dollar saving. Do not falsely report that cost is now controlled until owner billing + all private jobs have been read back.
