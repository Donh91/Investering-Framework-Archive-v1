# MCP Connection Evaluation Method v1

**Status:** OPERATIONAL_SEQUENTIAL_PILOT  
**Date:** 2026-08-11  
**Scope:** bounded agent-data connection research under the existing API-agent / Research Intake architecture

## Objective

Determine whether each approved connection adds reproducible research value to the Investering framework without creating a parallel truth layer, a new engine, automatic market semantics, trading authority, or a production dependency.

This is infrastructure evaluation. It is not a market backtest and no provider score is a trading signal.

## Fixed queue

The queue is deliberately sequential with at most one active provider trial:

1. Dune
2. LunarCrush
3. CoinMarketCap
4. The Graph
5. altFINS
6. Binance Agent Native

CoinGecko is the already-active bounded research/recovery baseline.

If a provider is blocked by an external dependency such as a missing credential, an unverified official endpoint, an unusable read-only tool surface or provider outage, preserve the blocked state and advance to the next provider. Do not stall the whole program and do not work around the block with an unofficial server.

## Stage 1 - official source verification

Before any tool connection:

- verify the provider documentation is official;
- verify the exact remote MCP endpoint and authentication method;
- record whether the surface can mutate provider state or expose account/portfolio/trading functions;
- reject community wrappers when an official server is required by the provider contract;
- Binance remains blocked until its official MCP endpoint and tool surface are directly verifiable.

X posts, screenshots and model memory are discovery inputs only. Official provider documentation is installation authority.

## Stage 2 - secret and authority boundary

Secrets may exist only in the runtime environment. They must never be echoed, committed, included in an artifact, written to a receipt or embedded in an MCP config committed to the repository.

Every provider contract has zero authority for:

- canonical data ownership;
- framework state;
- market rules, thresholds, weights or policy semantics;
- DATA PING;
- Master Monday;
- Weekly Backbone;
- Cycle Navigator;
- portfolio actions.

No root `.mcp.json` or `mcp_config.json` is created.

## Stage 3 - MCP tool discovery with no provider tool execution

Use the OpenAI Responses API remote MCP capability only through `scripts/api_agent/mcp_research_gateway.py` or an equivalently bounded MCP-capable agent.

The discovery request uses `require_approval=always` and `tool_choice=none`. The returned `mcp_list_tools` inventory is preserved without secret material.

The tool inventory is treated as untrusted provider metadata until filtered.

## Stage 4 - deterministic read-only allowlist

A tool may enter the execution allowlist only when all conditions hold:

1. it is exposed by the verified official server;
2. the provider supplies an affirmative read-only annotation recognized by the gateway;
3. neither tool name nor description contains a provider-contract forbidden fragment;
4. the provider contract permits the use class;
5. no payment, trade, fund movement, account, portfolio or provider-state mutation is required.

The research request receives the explicit resulting tool-name allowlist. A changed tool surface forces rediscovery before execution.

Dune receives extra caution because its official MCP can manage queries, visualizations and dashboards. Only read-only discovered tools that survive the denylist may execute.

## Stage 5 - bounded live smoke and research challenge

Each provider has three predeclared research challenges in its contract. Run them one at a time. Each run must:

- use at least one MCP call from the explicit read-only allowlist;
- preserve provider, endpoint class, tool name, timestamps/freshness where available and query context;
- record call success/failure and a hash of returned provider output;
- cap OpenAI-side cost per gateway run;
- treat provider output as `SOURCE_CONTEXT_ONLY`;
- produce no portfolio action, framework action or canonical promotion.

A provider error, rate limit or malformed result degrades only that provider trial.

## Stage 6 - redundancy and incremental value

Compare the provider with the existing owner or the strongest previously retained connection.

Count separately:

- research questions answered;
- unique value items that could not be obtained from the current owner/baseline at comparable effort;
- overlap items that merely duplicate an existing capability;
- contradictions or semantic mismatches;
- manual interventions;
- repeat consistency;
- crosscheck quality;
- provider cost status.

More data is not automatically more value. A provider that mostly duplicates CoinGecko, Binance, CFGI, Farside, FRED or another retained connection should remain crosscheck-only, be held, or be killed.

## Stage 7 - deterministic evaluation

`evaluate_mcp_connection_receipt.py` calculates a bounded infrastructure score from:

- connection reliability: 20
- research-question coverage: 20
- incremental information value: 20
- provenance/reproducibility: 15
- crosscheck quality: 10
- operational friction: 5
- cost fit: 5
- failure isolation: 5

Hard safety blockers override the score.

This score measures connection usefulness and operability only. It is not a market indicator and may not become a framework weight.

## Stage 8 - AI red-team review

A surviving provider is reviewed under the existing `research-lab-red-team` skill.

The reviewer must ask:

- What capability is genuinely new?
- Which current owner or retained MCP already answers the same question?
- Is the evidence reproducible?
- Can the capability be killed if it adds no measurable value?
- Does it improve research precision, source recovery, coverage or falsification?
- Does it merely make a nice explanation easier?
- What is the false-positive cost of retaining it?
- What is the false-negative cost of killing it?

AI review cannot override a hard safety blocker and cannot exceed the provider's promotion ceiling.

## Stage 9 - allowed integration outcomes

Only these bounded outcomes exist:

- `KEEP_RESEARCH_ACTIVE`
- `KEEP_CROSSCHECK_ONLY`
- `SHADOW_OBSERVATION`
- `CANDIDATE_DISCOVERY_ONLY`
- `DIAGNOSTICS_ONLY`
- `HOLD`
- `KILL`
- `DATA_BLOCKED`

None changes canonical market semantics.

LunarCrush may reach `SHADOW_OBSERVATION`, but becoming a framework sensor requires separate prospective evidence and governance. altFINS may nominate research candidates, but provider trade signals are never framework permissions. CMC may crosscheck but not replace existing owners. Binance Agent Native may at most become public/read-only diagnostics unless a later separately governed decision changes that boundary.

## Stage 10 - queue advancement

`advance_mcp_connection_scorecard.py` records the terminal pilot class and advances the next queued provider.

The program intentionally stops architectural expansion after the approved queue. New connections require a new demonstrated gap rather than collection for its own sake.
