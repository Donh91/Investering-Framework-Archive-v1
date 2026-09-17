# Alpha Lab — Adversarial Maintenance Loop v1

Status: CANONICAL DESIGN ADDENDUM
Date: 2026-09-17

## Decision

Adopt a two-role maintenance pattern inside the EXISTING Meme Alpha/Alpha Lab architecture:

1. **Adversarial Maintainer** — actively tries to falsify/break the system and emits only evidence-backed observations.
2. **Independent Adjudication/Repair routing** — an existing owner decides whether the observation is an immediate fix, shadow observation, needs evidence, is falsified, duplicate, or accepted risk.

Do not create a second autonomous framework, scanner, scorer, ledger or trading authority.

## Why

The PONSCUPINE stale-action incident demonstrated a general maintenance problem: written data-integrity principles do not guarantee that the final action boundary enforces them. Similar hidden failures can arise from provider drift, stale caches, wrong pools, wallet attribution, source provenance, lookahead, survivorship bias, silent fallbacks and runtime degradation.

The system therefore needs a role whose explicit objective is to find ways the machine can be wrong, rather than another role optimized to produce more alpha findings.

## Architecture

```text
EXISTING ALPHA LAB
      |
      v
ADVERSARIAL MAINTAINER
  attack / falsify / reproduce
      |
      v
QUALIFIED OBSERVATION
      |
      +--> P0 reproduced -> immediate fail-closed containment where existing guardrail permits
      |
      +--> P1 reproduced -> bounded repair candidate + regression test
      |
      +--> P2/P3 -> SHADOW by default
      |
      v
EXISTING INDEPENDENT OWNER / RED-TEAM / CODE INTAKE
      |
      +--> AGREE_AND_FIX
      +--> AGREE_AND_CONTAIN
      +--> SHADOW_OBSERVE
      +--> NEEDS_MORE_EVIDENCE
      +--> FALSIFIED
      +--> DUPLICATE_ALREADY_OWNED
      +--> ACCEPTED_RISK
      |
      v
ADVERSARIAL RETEST
      |
      v
CLOSE + REGRESSION MEMORY
```

The adversarial role cannot adjudicate its own claims and cannot self-merge code.

## Noise control

No generic criticism stream. A finding is qualified only when it has a material claim, evidence or deterministic test path, affected existing owner, blast radius, reproduction, smallest defensible fix or shadow hypothesis, and regression test.

Success is not number of findings. Prefer NO_QUALIFIED_FINDING to low-quality output.

## Priority attack surfaces

1. current ACTION/live-state boundary;
2. data/provider freshness and semantic integrity;
3. wallet attribution and graph independence;
4. first-party/source provenance;
5. prospective/scientific leakage and survivorship;
6. sellability/realizable-return semantics;
7. queue/runtime/provider/dependency drift;
8. duplicate/orphaned owners and tests disconnected from production paths.

## Seed incident corpus

Use real failures as adversarial regression seeds:
- PONSCUPINE stale market state -> current action;
- RSTR stale indexed reference overriding fresher exact-asset evidence;
- provider stale-cache contradiction cases;
- token receipt/transfer misread as intentional wallet buy;
- provenance/look-alike source failures.

Each new incident should strengthen a compact taxonomy/test suite rather than grow prose indefinitely.

## Cadence

Event-driven first. Trigger after material corrections, provider/schema changes, new chains, action-gate changes, wallet/provenance changes, scientific promotion requests, repeated degraded states, and through the existing supervisor's authorized periodic maintenance cadence.

One bounded high-value attack per run. Empty queue is a no-op. No new ChatGPT app automation is required.

## Next implementation owner

The skill `.agents/skills/meme-alpha-adversarial-maintainer/SKILL.md` defines the role. Existing issue #1087 remains the current implementation owner for the P0 live-action gate and should absorb the first adversarial regression tests. Future findings route to their existing owner rather than spawning a permanent parallel repair engine.
