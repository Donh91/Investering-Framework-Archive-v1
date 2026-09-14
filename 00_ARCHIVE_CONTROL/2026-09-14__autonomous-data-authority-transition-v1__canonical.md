# Autonomous Data Authority Transition v1

**Date:** 2026-09-14  
**Status:** CANONICAL_CURRENT_ROUTING_AUTHORITY  
**Scope:** Current-state routing for market data, Master Monday, Cycle Navigator, public site surfaces, and agent context resolution.

## Binding rule

The production framework no longer depends on manual user-submitted DATA PING packets as the upstream data feed for Master Monday or Cycle Navigator.

Current production routing is:

```text
autonomous collectors / GitHub Actions / governed source owners
-> current hash-bound machine outputs and pointers
-> main-framework interpretation / ratification
-> Master Monday weekly synthesis
-> Cycle Navigator public forecast/accountability output
-> public site and other presentation surfaces
```

For current-state questions, agents MUST resolve the newest eligible operational pointers and machine outputs first. A historical file name, folder name, protocol name, or payload containing `DATA_PING` does not make that artifact current production authority.

## DATA PING role after the transition

`02_DATA_PING/` remains valid and important for:

- historical protocol and compatibility records;
- explicit DATA PING or RAW packet interpretation;
- replay/correction/accountability work;
- source QA, collector diagnostics, and bounded protocol audits;
- historical lineage where an older frozen forecast actually depended on DATA PING.

It is NOT the default current upstream route for Master Monday, Cycle Navigator, the CN public site, or current-state short-horizon navigation.

A manual DATA PING packet is therefore **not a prerequisite** for a current Master Monday or Cycle Navigator run.

## Current-state precedence

For tasks asking what is current now, use this order unless a newer canonical owner explicitly supersedes this contract:

```text
1. Current operational cockpit and its exact hash-bound pointers.
2. Current autonomous machine outputs / current domain pointers named by those surfaces.
3. Main-framework accepted canonical state and runtime configuration.
4. Current canonical methodology/governance needed to interpret those outputs.
5. Explicit user-provided DATA PING/RAW packet only when the task itself is packet interpretation, replay, correction, or comparison.
6. Historical DATA PING, historical weekly artifacts, source material, shadow/challenger context, and memory.
```

`LATEST_OPERATIONS_DASHBOARD.json` and `LATEST_HANDOFF.json` are routing/observability surfaces, not independent market-rule authority. Follow the exact current target paths and hashes they expose.

## Master Monday

Current Master Monday must be resolved from the current autonomous weekly output chain and exact current pointer/receipt named by operational routing.

Historical compatibility files under `03_WEEKLY_OPERATIONS/master_monday/`, including `latest_master_monday.json`, may preserve older DATA PING-derived lineage. They must not be treated as the current production pointer unless a current operational surface explicitly routes to them.

## Cycle Navigator

Cycle Navigator remains a public output/accountability surface, not an independent market-state engine.

Current CN authority is resolved through the current CN pointer and referenced machine package after the framework's autonomous evidence and weekly/current-state machinery has produced the eligible state. CN does not wait for or require a manual DATA PING submission.

The public Cycle Navigator site must consume sanitized current CN/current-machine outputs. It must not revive a historical DATA PING runtime merely because a desired field is absent from the current public package.

For `NEXT DAYS` or other short-horizon fields: use an existing current autonomous canonical output if one exists and is fresh/public-safe. Otherwise fail closed to `NOT PUBLISHED`, `UNAVAILABLE`, or equivalent. Do not create a parallel forecast engine on the website.

## Explicit DATA PING / RAW packet exception

When the user's primary input really is a DATA PING packet or RAW packet/replay, the DATA PING-specific contracts remain applicable to that packet interpretation. In particular, the Three-Horizon Action Compass owner can still be mandatory for that explicit task class.

That exception does not restore DATA PING as the normal production upstream feed for CN or Master Monday.

## Legacy traps agents must reject

Do not infer current authority from:

- `Current active operational feed: DATA PING ...` prose preserved in older archive/index sections;
- `data_ping_derived_*` historical paths;
- `latest_master_monday.json` solely because its filename contains `latest`;
- old Custom GPT collector references;
- an old DATA PING version number or handoff;
- a Three-Horizon Action Compass receipt created from an explicit historical/manual packet when the task asks for current autonomous state.

For any such artifact, require a current pointer or current routing surface to name it before classifying it `OPERATIONAL_CURRENT`.

## No architecture expansion

This transition changes routing clarity only. It does not:

- create a new market engine;
- change thresholds or market-state definitions;
- increase website authority;
- grant automatic portfolio execution;
- invalidate historical DATA PING evidence for the periods in which it was genuinely upstream;
- authorize copying restricted values into the control plane.

## Agent invariant

```text
CURRENT STATE: FOLLOW CURRENT AUTONOMOUS POINTERS.
EXPLICIT DATA PING TASK: USE DATA PING CONTRACTS.
HISTORICAL DATA PING NAME ALONE: NEVER CURRENT AUTHORITY.
```
