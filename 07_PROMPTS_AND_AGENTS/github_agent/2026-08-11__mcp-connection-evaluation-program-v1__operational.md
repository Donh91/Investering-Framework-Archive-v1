# MCP Connection Evaluation Program v1

**Date:** 2026-08-11  
**Status:** OPERATIONAL_SEQUENTIAL_PILOT  
**Authority:** research infrastructure only  
**Owner:** existing Research Intake -> API Agent -> Research Lab Red Team path

## Purpose

Operationalize the user-approved evaluation of Dune, LunarCrush, CoinMarketCap, The Graph, altFINS and Binance Agent Native after the already-implemented CoinGecko MCP sidecar.

The objective is not to accumulate MCP servers. The objective is to retain only connections that demonstrate incremental, reproducible research value while preserving the framework's deterministic owners and authority boundaries.

## Architecture

```text
external official provider docs
-> provider-specific MCP contract
-> no-execution MCP tool discovery
-> deterministic read-only allowlist
-> bounded live research challenge
-> pilot receipt
-> deterministic infrastructure evaluator
-> Research Lab Red Team
-> bounded KEEP / SHADOW / HOLD / KILL class
-> next provider in queue
```

The queue owner is:

```text
research/api_agent/mcp/MCP_CONNECTION_EVALUATION_PROGRAM_v1.json
```

The current machine state is:

```text
research/api_agent/mcp/evaluations/LATEST_MCP_CONNECTION_SCORECARD.json
```

## OpenAI remote MCP bridge

The framework's existing OpenAI API agent can reach verified remote MCP servers through a separate bounded research gateway:

```text
scripts/api_agent/mcp_research_gateway.py
```

This gateway is deliberately separate from `api_gateway.py`. Existing daily and weekly API-agent behavior is therefore unchanged unless a future evidence-backed integration is separately approved.

The gateway:

- loads exactly one provider contract;
- uses credentials only from runtime environment variables;
- never persists or echoes credentials;
- first discovers tools with no provider tool execution;
- requires affirmative read-only tool annotations;
- filters tool names/descriptions through provider-specific deny fragments;
- passes an explicit allowed-tool list to the live research call;
- rejects unexpected approvals or calls outside the allowlist;
- records tool/call metadata and hashes, not secret material;
- caps OpenAI-side cost per run;
- emits research context and an auditable pilot receipt only.

## Sequential rule

At most one provider trial may be active.

The fixed order is:

```text
CoinGecko baseline
-> Dune
-> LunarCrush
-> CoinMarketCap
-> The Graph
-> altFINS
-> Binance Agent Native
```

A missing credential or other external dependency becomes a visible blocked provider state and advances the queue. It must not cause the framework to stop, and it must not be bypassed through an unofficial MCP server.

## Provider roles and ceilings

### Dune

Role: onchain research and recovery.  
Ceiling: `KEEP_RESEARCH_ACTIVE`.

Dune's official server can expose provider-state management functions, so tool discovery and read-only allowlisting are mandatory before any live call.

### LunarCrush

Role: social attention/sentiment research.  
Ceiling: `SHADOW_OBSERVATION`.

A shadow result is not a new sensor. Any later sensor proposal requires separate prospective evidence and governance.

### CoinMarketCap

Role: independent market crosscheck and recovery.  
Ceiling: `KEEP_CROSSCHECK_ONLY`.

CMC x402/pay-per-request is disabled. Existing owners win conflicts.

### The Graph

Role: protocol/contract-level onchain research when it adds value beyond Dune.  
Ceiling: `KEEP_RESEARCH_ACTIVE`.

### altFINS

Role: candidate discovery and technical crosscheck.  
Ceiling: `CANDIDATE_DISCOVERY_ONLY`.

Portfolio tools are forbidden. Provider technical signals are provider context, not framework permission.

### Binance Agent Native

Role: public market-data/API diagnostics only.  
Ceiling: `DIAGNOSTICS_ONLY`.

Binance currently remains blocked because official docs announce an MCP Server but the exact official endpoint/tool surface has not been verified. No unofficial Binance MCP may substitute.

## Promotion and integration boundary

The program may automatically classify and route research infrastructure. It may not automatically:

- alter market rules, thresholds, weights or policy semantics;
- create a new engine;
- create a new framework sensor;
- replace a canonical data owner;
- change DATA PING, Master Monday, Weekly Backbone or Cycle Navigator authority;
- produce portfolio action;
- self-merge a market-semantic change.

A retained connection can become research-active, crosscheck-only, shadow-observation, candidate-discovery-only or diagnostics-only within its predeclared ceiling.

## Validation

The existing `API Agent Gateway Gate` already runs `tests/api_agent/test_api_gateway.py` for changes under `research/api_agent/**`, `scripts/api_agent/**` and `tests/api_agent/**`.

This program therefore adds its deterministic boundary and evaluator tests to the existing gate without changing GitHub workflow files.

No new scheduled workflow is introduced during the initial pilot. This avoids turning untested external MCP dependencies into production infrastructure before they earn retention.
