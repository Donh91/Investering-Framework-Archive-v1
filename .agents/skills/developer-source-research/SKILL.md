---
name: developer-source-research
description: 'Find and verify upstream technical behavior from official docs, READMEs, issues and merged pull requests. Use for external library/API behavior, error diagnosis, bug-fix history, repository discovery or agent-skill research. Do not use for internal repository authority, market research or portfolio questions.'
---

# Developer Source Research

## Purpose

Resolve an external technical uncertainty from primary developer sources before code is changed. Prefer the installed Firecrawl Developer Index when it is callable, while keeping current local repository state and current upstream code or documentation authoritative.

This skill is read-only research. It does not authorize code changes, repository writes, new dependencies, credentials, workflows, market-state changes or portfolio actions.

For framework-related work, honor `00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md` before forming an external query. Restricted evidence stays in `Donh91/secrets`; credentials stay in the credential plane.

## Route

1. If the question is about this framework's current code, contract or governance, use `canonical-context-router` and inspect the current repository first.
2. Use `firecrawl_developer_search` for external library/API behavior, error strings, known bugs, merged fixes, documentation contracts, repository discovery or indexed agent skills.
3. Query with the invariant technical terms. Remove local paths, identifiers, addresses, tokens and private or restricted values before any external call.
4. Prefer the source type that answers the question:
   - current API contract or usage: official documentation or README;
   - reported failure: issue plus its resolution;
   - implemented fix: merged pull request, then current docs or code when behavior may have changed again;
   - repository discovery: repository README, license, maintenance state and current code;
   - agent-skill discovery: Developer Index skill-only search when the tool supports it.
5. Open and verify every load-bearing source URL. A matched passage is retrieval evidence, not proof that the result is current or applicable to the version in use.
6. If Firecrawl is unavailable, unindexed, rate-limited or inconclusive, continue with the GitHub connector/search and official documentation through web search. Record the fallback reason instead of blocking the task or requesting a credential.

## Source rules

- Current local code and canonical repository contracts beat an external index snapshot.
- Current official documentation or code beats an older issue or pull request for a present-tense behavior claim.
- A merged pull request is stronger evidence of what changed than an issue opener, but it may itself be superseded.
- General web pages, blogs and model recollection are context only when a primary developer source exists.
- Conflicting sources remain explicit. Do not silently choose the result that supports the intended patch.
- Absence from the index means `NOT_FOUND_OR_NOT_INDEXED`, not that the behavior or repository does not exist.

## Privacy and authority boundary

Never send credentials, private repository contents, restricted provider values, proprietary payloads, account data or unredacted logs to an external search provider. Public error messages may be searched only after volatile and sensitive fields are removed.

The Developer Index may inform diagnosis and implementation. It may not:

- replace current repository inspection or tests;
- set `CODEX_READY` or bypass `codex-intake`;
- create a canonical rule, market sensor, forecast or evidence row;
- enter DATA PING, Daily/Weekly Director or portfolio execution;
- become a required production dependency or scheduled workflow during the pilot;
- cause an API key or plugin credential to be committed.

## Result contract

Return or preserve a compact source bundle:

```yaml
question:
tool_status: FIRECRAWL | FALLBACK_GITHUB | FALLBACK_WEB | MIXED | UNRESOLVED
query_sanitized: YES | NO
primary_sources:
current_behavior_verified: YES | NO | PARTIAL | NOT_APPLICABLE
version_or_date_scope:
conflicts:
fallback_reason:
implementation_effect:
unresolved:
```

Do not archive raw result dumps. Preserve only citations and the smallest durable technical conclusion when the task already authorizes a repository write.

## Pilot validation

A qualified use is a real external technical uncertainty that materially affects diagnosis, design or implementation. Compare the Developer Index result with the native GitHub/web route only far enough to determine whether it added a primary source or reduced uncertainty.

After ten qualified uses, KEEP requires:

- at least eight load-bearing source bundles verified against their URLs;
- incremental primary-source value over the native route in at least three uses;
- zero restricted-data, credential, fabricated-source or authority incidents.

Modify or suspend the skill if Firecrawl is unavailable in more than half of qualified uses. Kill it if it adds incremental value in fewer than two of ten qualified uses or produces any uncorrected source-identity mismatch.
