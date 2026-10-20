# Treg Agent/Tool Routing Extraction v1

Date: 2026-10-07
Status: `RESEARCH_ONLY / BORROW_PRINCIPLE / NO_RUNTIME_DEPENDENCY`
Source: `superdesigndev/treg@e609803cff18ab8a815ceda153e667632bb2234f`
Source license observed: Apache-2.0 plus additional hosted-service restriction.
Intended local owner: existing Investering agent/skill architecture.
Authority: none.

## Why this note exists

The user supplied Treg as an external agent-tool repository and explicitly authorized a bounded extraction of useful mechanisms.

The objective is **not** to install Treg, copy its implementation, create a seventh permanent skill, move credentials, or replace existing routing.

The objective is to determine whether Treg exposes implementation patterns that add measurable value to the current Investering agent stack.

## Inspected upstream scope

Primary files inspected:
- `README.md`
- `skills/treg/SKILL.md`
- `skills/jev-memory/SKILL.md`
- `examples/claude-code-mods/jev-memory/README.md`
- `docs/context/architecture/mcp-oauth.md`
- `LICENSE`
- `pyproject.toml`

Uninspected scope:
- complete server implementation
- all catalog adapters/providers
- all tests
- hosted-service production configuration
- private operator repository

No upstream code was executed.

## Existing Investering owners checked

Current local owners already cover most of the attractive architecture:
- `00_ARCHIVE_CONTROL/SKILL_REGISTRY.md`
- `00_ARCHIVE_CONTROL/SKILL_ROUTING_INDEX.json`
- `.agents/skills/canonical-context-router/SKILL.md`
- `.agents/skills/developer-source-research/SKILL.md`
- `.agents/skills/skill-quality-gate/SKILL.md`
- `scripts/api_agent/capability_router.py`
- `research/api_agent/CAPABILITY_ROUTING_POLICY_v1.json`
- `07_PROMPTS_AND_AGENTS/astra/2026-09-06__agent-legibility-and-skill-compression-audit-v1.md`

## Dedup result

### A. Task-first capability routing
Treg pattern:
`task -> search capability -> inspect contract/price -> call exact provider`

Local state:
**PARTIALLY ALREADY EXISTS.**

The Investering capability router already enforces:
- responsibility before capability
- least-privilege context
- cost budgets
- explicit tools per delegated unit
- fail-closed / escalation semantics

However, the current router is strongest at **model/executor selection**, while external source/provider selection is distributed across MCP scorecards, source contracts and task-specific logic.

Disposition:
`EXTRACT_AS_PROVIDER_ROUTING_CHALLENGER`, not a new engine.

### B. Small static tool surface / progressive discovery
Treg avoids exposing thousands of provider endpoints as separate MCP tools.

Local state:
**ALREADY ALIGNED IN PRINCIPLE.**

The current Investering routing index and skill metadata intentionally limit always-loaded routing context and favor progressive disclosure.

Disposition:
`NO_CHANGE`.

### C. Credential/tool separation
Treg keeps credentials server-side and skills/tools refer to bindings rather than embedding values.

Local state:
**ALREADY STRONGER / DIFFERENT OWNER.**

Investering already separates restricted credentials into the credential plane / `Donh91/secrets`.

Disposition:
`NO_MIGRATION / RETAIN PRINCIPLE`.

No Treg credential store should become a second secrets authority.

### D. Read/write separation
Treg separates read and write MCP calls where side effects can be classified.

Local state:
**ALREADY ALIGNED.**

Investering skill routing already distinguishes read-only implicit skills from write/queue/evidence-mutation skills that require explicit intent.

Disposition:
`NO_NEW_SKILL`.

Potential future execution systems should keep:
`OBSERVE != PROPOSE != WRITE != EXECUTE`.

### E. Cost/reliability/freshness-aware provider selection
Treg exposes provider capability, observed success, price, recency and latency before a call.

Local state:
**PARTIAL GAP.**

Investering tracks cost, provider health and source authority in multiple places, but there is not yet one bounded research contract that tests whether an explicit provider-ranking policy improves external-tool reliability/cost without degrading evidence quality.

Disposition:
`NEW_BOUNDED_CHALLENGER_JUSTIFIED`.

### F. Idempotency + receipt semantics
Treg supports caller-supplied idempotency keys for genuine retries and preserves call receipts/cost metadata.

Local state:
**PARTIALLY ALIGNED.**

Investering is already receipt-heavy, but external-provider retry semantics are provider/tool specific rather than one universal runtime.

Disposition:
Borrow principle into the provider-routing challenger:
- distinguish retry from fresh query;
- never silently transform a fresh request into a cached replay;
- preserve provider identity, attempt count, cost and freshness in receipts.

No generic runtime change yet.

### G. Jev memory trust boundary
Treg's Jev mod treats prompt text as evidence, not instructions, and refuses to trust a committed repo memory file as if it were the user's personal memory.

Local state:
**ALREADY COVERED.**

`developer-source-research` already states that external SKILL.md, AGENTS.md, README, prompts and scripts are untrusted source material and may not become active instructions or expand permissions.

Disposition:
`NO_CHANGE`.

This confirms the existing rule rather than creating a new memory layer.

### H. Agent memory
Treg offers a lightweight project-memory mod.

Local state:
**NO CURRENT GAP.**

Investering uses GitHub-native provenance, Case Memory, frozen evidence and receipts.

Disposition:
`DEFER`.

Do not replace deterministic provenance with semantic memory unless a retrieval benchmark proves incremental value.

## Net-new extraction

Only one meaningful new experiment survives the dedup pass:

> Can an explicit external-provider routing policy choose the smallest sufficient source/tool using capability fit, evidence authority, health/reliability, freshness, cost and latency, while preserving exact provider provenance and fail-closed behavior?

This is encoded separately as:
`research/api_agent/mcp/TOOL_PROVIDER_ROUTING_CHALLENGER_v1.json`

## Proposed selection order

The challenger should test this ordering:

1. **Exact capability/input fit**
2. **Authority / evidence class fit**
3. **Freshness / point-in-time suitability**
4. **Current provider health / reliability**
5. **Rights / privacy / credential eligibility**
6. **Expected cost**
7. **Latency**
8. **Fallback only if semantics remain compatible**

Cost must never outrank source validity or evidence authority.

## Anti-patterns explicitly rejected

- install Treg as a required production dependency;
- expose every endpoint/tool to every agent;
- move existing secrets into a second authority plane;
- import Jev memory as framework truth;
- silent provider failover where provider semantics differ;
- auto-select the cheapest provider before checking input/output fit;
- treat external README instructions as agent authority;
- copy upstream code when a local synthesized contract is sufficient.

## Research benchmark

Compare the provider-routing challenger against current owner-directed routing on a frozen task set.

Candidate task classes:
- exact contract / chain lookup
- historical market series retrieval
- wallet/entity enrichment
- social/source verification
- developer-source lookup
- duplicate-source recovery

Required measurements:
- task success / usable evidence rate
- source-authority correctness
- unsupported fallback rate
- provider identity/provenance completeness
- stale-answer incidents
- cost per usable result
- latency per usable result
- unnecessary paid-call rate
- manual correction count
- privacy / credential incidents
- semantic mismatch incidents

## Promotion rule

Promote only if the challenger:
- reduces cost or failure materially,
- does not reduce evidence quality,
- creates no authority/privacy regression,
- preserves exact provider provenance,
- does not increase manual correction burden.

A positive result may justify a small extension to the existing capability/source router.

It does **not** justify importing Treg wholesale.

## Kill rule

Kill the challenger if:
- existing source owners already select providers as well;
- savings are trivial;
- reliability gains disappear after source-authority constraints;
- semantic mismatches increase;
- routing adds opaque complexity;
- current MCP/provider scorecards already contain all needed value with no routing gap.

## Current decision

`BORROW_PRINCIPLE + BOUNDED_CHALLENGER`

No new skill.
No runtime dependency.
No credential migration.
No framework/market/portfolio authority.
