# TypeSafe skill and documentation audit v1

**Dato:** 2026-09-19  
**Status:** SOURCE_NOTE  
**Område:** TypeSafe / Jev / agent skill review  
**Primary folder:** `07_PROMPTS_AND_AGENTS/typesafe_jev/`  
**Related folders:** `08_SOURCE_MATERIAL/typesafe_jev/`, `.agents/skills/`

## Finding

The upstream TypeSafe skill is useful external prior art and is broadly compatible with the Investering architecture because it keeps code in control, treats TypeSafe as narrow semantic judgment, asks atomic questions, encourages batching, preserves raw probability distributions, recommends risk-specific confidence handling, and requires target-domain validation.

It must not be copied into the active local skill stack without local governance because it does not know Investering-specific authority, cross-repository restrictions, Round 3 firewalls, Alpha Lab anti-hindsight rules, immutable evidence requirements, portfolio limits, or local write governance.

## Live documentation findings frozen for this review

At review time, TypeSafe documented:

- current model: `jev-1.13.0`;
- `jev-latest` and `jev-preview` both resolved to that model;
- price: $42/Btok, $0.042/Mtok of input;
- output tokens free;
- rate limits shown as 250,000 tokens/sec and 1,200 requests/min, explicitly described as dynamically adjustable;
- request context: 64k tokens total and 32k for state plus the longest question;
- text-only input;
- primary training language: English;
- Python SDK observed at v0.7.0;
- System One Adapter observed at v0.2.0.

These are source observations, not permanent framework constants. Re-read live docs before implementation.

## Jev 1.13 known jaggedness converted into local test obligations

TypeSafe explicitly documents weaker behavior for:

- literal / underspecified instructions;
- arithmetic and counting;
- date and time comparisons;
- multiple levels of indirection;
- large state with irrelevant detail;
- adversarial content in state;
- contradictory instructions and criteria;
- assumed structural identities between separate question formulations;
- text generation.

Local implication: every pilot must deliberately include these failure classes as adversarial eval cases.

## Local adoption decision

```text
UPSTREAM_SKILL_STATUS: PINNED_SOURCE_ONLY
ACTIVE_LOCAL_SKILL: NO
JEV_RUNTIME: NO
SHADOW_PILOT: PREPARED
TRADE_AUTHORITY: ZERO
```

Preferred adoption shape:

```text
local canonical router / data-boundary enforcement
-> deterministic state builder
-> upstream-informed TypeSafe question contract
-> Jev
-> deterministic composer and risk gate
-> existing framework handler
-> immutable trace and outcome evaluation
```

Do not let the upstream skill become a second governance stack.

## Static skill-quality observations

Strengths:
- explicit live-doc source of truth;
- correct Choice / Score / Noul distinctions;
- atomic question discipline;
- structured-state guidance;
- batching/speculative fan-out;
- explicit separation of semantic judgment from arithmetic and hard rules;
- confidence/probability treated as routing signals rather than truth;
- evaluation against representative cases.

Local gaps requiring a wrapper or surrounding governance:
- no Investering authority resolution;
- no public/restricted/credential plane boundary;
- no anti-hindsight market replay rule;
- no mandatory immutable pre-outcome freeze;
- no portfolio/trade prohibition;
- no local branch/PR write-safety gate;
- no current-owner / duplicate-engine check.

Verdict for now: preserve upstream source and use its mechanisms in the shadow design, but do not register it as an active local skill until a full local Skill Quality Gate has run.

