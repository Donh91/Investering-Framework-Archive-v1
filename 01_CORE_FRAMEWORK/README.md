# 01_CORE_FRAMEWORK - Framework Architecture Mission Card

**Status:** NAVIGATION_ONLY  
**Authority:** NONE_BY_ITSELF  
**Folder role:** Durable framework architecture, governance and core engine ownership.

## Entering this folder

Read root `AGENTS.md`, current archive authority and this folder's exact current owners before interpreting historical engine or governance files.

Primary subdomains:

```text
architecture/
engines/
governance/
```

Do not assume the newest-looking engine file is active. Resolve status through the canonical index, addenda, rule/evidence registry and current framework state.

## What this folder is trying to achieve

The framework should turn verified evidence into bounded, falsifiable and accountable decisions without allowing one signal, model or narrative to silently become truth.

Mature work here should improve:

- architecture consistency;
- rule precedence;
- BTC vs alt permission separation;
- evidence-to-action boundaries;
- false-positive and false-negative accountability;
- rollback / kill criteria;
- reproducibility;
- model/agent authority boundaries;
- recovery safety.

## High-value mission seeds

### 1. Framework-wide contradiction audit

Find cases where architecture, governance, runtime code, current pointers and human-readable docs disagree about what the system actually does.

### 2. Minimum sufficient framework

Ask whether any active layer, rule, score or owner is now redundant because another current owner subsumes it. Prefer compression/retirement over adding concepts.

### 3. Governance -> behavior verification

For important written rules, find the exact code, workflow, CI gate or receipt that proves the rule is operational rather than merely documented.

### 4. Offensive/defensive calibration

Test whether the framework is appropriately conservative by asset class and horizon rather than uniformly defensive. Measure missed opportunity as well as avoided drawdown.

## Authority ceiling

Default mode is `READ_ONLY`.

Do not create a new engine, scoring family, shadow layer, market threshold or canonical owner during an audit pass. Strong models are expected to prove why existing owners cannot solve the problem first.

Any canonical framework change must use the existing owner where possible, go through task branch -> PR -> validation -> merge -> main readback, and obey the permanent safety owner.

## Permanent safety owner

```text
governance/2026-07-11__repository-safety-and-backup-policy-v1__canonical.md
```

The dedicated governance README contains the first Astra-class qualification mission.

See:

```text
governance/README.md
07_PROMPTS_AND_AGENTS/astra/README.md
```
