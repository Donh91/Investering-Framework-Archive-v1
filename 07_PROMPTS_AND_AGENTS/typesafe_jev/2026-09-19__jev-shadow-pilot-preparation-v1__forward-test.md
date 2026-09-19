# Jev Shadow Pilot Preparation v1

**Dato:** 2026-09-19  
**Status:** FORWARD_TEST  
**Område:** TypeSafe / Jev / Alpha Lab / agent routing  
**Primary folder:** `07_PROMPTS_AND_AGENTS/typesafe_jev/`  
**Related folders:** `07_PROMPTS_AND_AGENTS/memes_alpha/`, `06_RESEARCH_LAB/`, `08_SOURCE_MATERIAL/typesafe_jev/`  
**Depends on:** Alpha Lab standing mandate, Skill Registry, cross-repo boundary, TypeSafe live docs and pinned upstream skill snapshot

## Frozen proposition

Jev may reduce frontier-model compute and improve semantic triage/routing while preserving or improving critical evidence retention versus the current baseline.

This proposition is unproven.

## Why shadow-only

TypeSafe documents Jev as a System One model for typed probabilistic judgments, not generation or multi-step reasoning. The current Jev 1.13 documentation explicitly lists literal reading, numerical precision, date comparison, indirection, large irrelevant state and adversarial content as known failure modes.

The framework therefore keeps deterministic facts and calculations outside Jev and treats Jev outputs as challenger features until target-domain evidence exists.

## Non-negotiable invariants

- no credentials in repository files, logs, issues or PR text;
- no raw restricted provider values sent from the public control plane;
- no automatic portfolio or trade action;
- no hidden outcome information in retrospective evaluation state;
- no math/date/identity/provenance invariant delegated to Jev;
- no production threshold copied from examples or social posts;
- no silent DROP on uncertain high-information observations;
- full Jev distributions / Noul probabilities, returned model ID, token usage, latency, route and downstream outcome must be logged;
- question contract and composition policy are separately versioned;
- model version is pinned for calibrated comparisons;
- every external action rebuilds state from fresh evidence before another decision;
- typed output is not treated as truth.

## Stage 0 - source and contract readiness

Required before live API use:

- official docs read and recorded;
- upstream skill pinned by immutable blob/commit evidence;
- current SDK version verified;
- model/version and known jaggedness verified;
- credential location selected in GitHub Actions Secrets or approved runtime secret manager;
- no secret value committed;
- sanitized smoke dataset prepared;
- evaluation contract frozen before looking at outcomes.

## Stage 1 - sanitized smoke test

Purpose: verify authentication, response schema, model identity, logging and error handling.

Use non-sensitive synthetic states only.

Pass requires:

- correct typed responses for Choice / Score / Noul;
- model ID captured;
- usage captured;
- bounded retry behavior on 429 / 529;
- no credential leakage;
- exact request/response trace redacted of secrets.

A pass proves connectivity only, not intelligence or alpha.

## Stage 2 - Alpha Lab historical blind replay

Use frozen pre-outcome records only. Strip all post-outcome fields before Jev sees state.

Candidate atomic judgments include:

- genuine novelty;
- evidence materiality;
- source independence;
- evidence conflict;
- wallet-behavior anomaly;
- likely coordinated/insider pattern;
- narrative differentiation;
- information density;
- deep-dive value;
- preserve-verbatim value;
- frontier-review need.

These are candidate dimensions, not yet canonical questions or thresholds.

The exact questions must be frozen before the held-out replay.

## Challengers

Compare at minimum:

1. existing Alpha Lab baseline;
2. deterministic-only rules where applicable;
3. System One Adapter using a fixed general-model configuration;
4. Jev using a pinned version.

No challenger receives outcomes during inference.

## Metrics

Primary safety metrics:

- critical-evidence-drop rate;
- false-negative rate on later material cases;
- incorrect auto-discard rate;
- authority / invariant violations;
- data-conflict miss rate.

Efficiency metrics:

- frontier calls avoided;
- input tokens saved downstream;
- end-to-end latency;
- TypeSafe input tokens and estimated cost;
- escalation rate.

Decision-quality metrics:

- discrimination of later high-value vs low-value cases;
- calibration / reliability of Noul probabilities where labels permit;
- Brier score or equivalent for binary outcomes when scientifically valid;
- stability across repeated calls;
- performance by regime, chain, liquidity band and observation age when sample sizes permit.

## Fail / kill conditions

The candidate is not promotable if any of the following survives investigation:

- critical immutable evidence is silently dropped;
- outcome leakage is found;
- Jev adds no material value over deterministic/simple baselines;
- calibration is unstable on the target domain;
- gains disappear under held-out replay;
- the workflow requires sending restricted values contrary to the cross-repo boundary;
- complexity and operational risk exceed measured savings;
- a simpler existing owner can deliver the same decision value.

## Promotion path

```text
SOURCE_NOTE
-> SHADOW PILOT
-> frozen replay
-> held-out / prospective rows
-> Research Lab falsification
-> governance review
-> narrowly bounded operational candidate
```

No stage self-promotes.

