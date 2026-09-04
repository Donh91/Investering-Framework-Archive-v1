# 07_PROMPTS_AND_AGENTS - Agent Capability & Handoff Mission Card

**Status:** NAVIGATION_ONLY  
**Authority:** NONE_BY_ITSELF  
**Folder role:** Reusable agent procedures, prompts, handoffs, capability routing and model-specific operating briefs.

## Entering this folder

Prompts are procedures, not market authority.

A newer prompt does not supersede canonical framework truth unless the governing owner explicitly says so.

Prefer repository-local Skills and machine routing over copying large conversation prompts between threads.

## Main objective

Make capable models useful without making the system dependent on one chat, one provider or one model generation.

Good agent infrastructure should preserve:

```text
scope
source authority
write boundaries
reproducibility
handoff continuity
failure honesty
model replaceability
least privilege
```

## Astra / successor model entrypoint

```text
astra/README.md
astra/ASTRA_REPOSITORY_MISSION_ROUTER_v1.json
```

These files let a stronger model reconstruct missions from GitHub rather than waiting for a separate instruction in every thread.

They do **not** grant write authority.

## High-value mission seeds

### 1. Capability routing

Determine which tasks genuinely benefit from a frontier long-horizon model versus cheaper deterministic code, existing API agents, Codex or normal reasoning models.

Do not use the strongest model merely because it exists.

### 2. Qualification and regression testing

Build frozen model-evaluation tasks from real framework failures and hard cases. Re-run after meaningful model/tool changes.

### 3. Context compression

Reduce prompt/context load while preserving exact authority routing, state lineage and failure semantics.

### 4. Handoff robustness

Test whether a fresh model can reconstruct current work solely from GitHub without conversation memory.

### 5. Tool/agent separation

Ensure researcher, code writer, verifier, merger and recovery roles are not collapsed into one unreviewed authority path.

## Authority ceiling

Default mode is `READ_ONLY`.

Prompts may tell agents how to act inside existing authority. They must not silently create new source, portfolio, canonical or recovery authority.

A model-specific brief must remain subordinate to:

```text
AGENTS.md
canonical governance
current domain owners
cross-repo boundary
verified receipts
```

## Design test

A good prompt/agent architecture should answer:

```text
Can a fresh capable model understand the task without chat history?
Can it identify what it is not allowed to do?
Can it prove which repository/file is authoritative?
Can it fail honestly when evidence is missing?
Can another model reproduce the result?
Can the model be replaced without losing the framework's memory?
```

If not, improve the routing rather than adding more prose.
