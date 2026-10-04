# Alpha Lab Lifecycle Durability / Mortality Learning v1

**Dato:** 2026-10-04  
**Status:** SHADOW_ONLY  
**Område:** Alpha Lab / lifecycle learning / negative benchmarks / durability  
**Primary folder:** `06_RESEARCH_LAB/alpha_lab/`  
**Depends on:** `research/api_agent/meme_alpha/ALPHA_LAB_LIFECYCLE_ENGINE_v1.json`, `.agents/skills/meme-alpha-supervisor/SKILL.md`

## Purpose

Preserve the reusable learning from the Blast shutdown case and matched-control research without creating a new scanner, engine, live threshold, market rule or portfolio authority.

This note is a public control-plane synthesis. The evidence-rich case material remains in the restricted data plane.

## Private evidence bindings

Primary negative benchmark:

- repository: `Donh91/secrets`
- immutable commit: `3c4784fc4ae089eb365d0977613874d363bde323`
- path: `private_research/memes_alpha/external_benchmarks/lifecycle/2026/10/04/blast_l2_mortality_case_v1.json`
- blob SHA: `6d93ca4df6dee66d60a8b4d13a3ac62045eb4b61`
- case id: `BLAST_L2_MORTALITY_2026`

Deep-research synthesis:

- immutable commit: `1092ffbd94b23f9dedb7eb4bc3729e620bb470b0`
- path: `private_research/memes_alpha/external_benchmarks/lifecycle/2026/10/04/blast_lifecycle_deep_research_synthesis_v2.json`
- blob SHA: `712dd0569b1735b4982b36cd810013504f996a82`

Matched-control preregistration:

- immutable commit: `b18cd0888fe11472f964fb7592bb3fa4cca6d034`
- path: `private_research/memes_alpha/research_leads/2026/10/04/blast_lifecycle_matched_control_program_v2.json`
- blob SHA: `762ff35128a2ea90f85efabf0278a455b12f1fea`

These paths are evidence/discovery bindings only. They do not promote private research into canonical live rules.

## Core learning

Alpha Lab must treat these as separate questions:

```text
LAUNCH_ALPHA
-> MOMENTUM_ALPHA
-> SURVIVAL_ALPHA
-> DURABILITY_ALPHA
```

A project can be excellent at launch and poor as a long-duration asset. Short-horizon executable alpha and long-horizon project survival must not be collapsed into one conviction score.

## Blast case

Blast is useful because it was not an obvious rug. It had strong funding, a known founder, large early TVL, real infrastructure and active development. It nevertheless announced a wind-down after its operating economics became unsustainable.

The case therefore teaches more than scam detection. It is a benchmark for distinguishing:

- capital acquisition from durable capital quality;
- incentivized activity from organic demand;
- technical maintenance from economic viability;
- token performance from protocol economics;
- protocol economics from full operator economics;
- narrative/brand prestige from empirical survival.

## Matched-control learning

### Optimism

Optimism's Airdrop 5 analysis used a regression-discontinuity design. Near the eligibility cutoff, receiving the reward increased 30-day retention by 4.2 percentage points and 60-day retention by 2.8 percentage points. A frequent-user bonus, however, reduced 30-day retention by 7.1 percentage points.

Learning:

```text
INCENTIVES != ONE VARIABLE
```

The relevant research question is what marginal behavior a reward buys and whether that behavior survives after the reward.

Primary source:
https://gov.optimism.io/t/did-op-airdrop-5-increase-user-retention-rates-a-regression-discontinuity-analysis/9610

### Arbitrum

OpenBlock Labs reported strong growth during STIP across TVL, DAU and transaction volume. It also observed that about 30% of identified claimed ARB had been sold in the post-claim activity analysis.

Learning:

Incentives can create real ecosystem growth while simultaneously producing extraction behavior. Raw TVL/DAU/volume growth during an incentive period is insufficient evidence of durable demand.

Primary sources:
https://forum.arbitrum.foundation/t/openblock-labs-stip-incentive-efficacy-update-12-29/20321
https://forum.arbitrum.foundation/t/openblocks-stip-incentive-efficacy-analysis/23687

### Polygon zkEVM

Polygon zkEVM is a useful counterexample to any binary ALIVE/DEAD label because a strategic sunset is not the same failure class as Blast's economic-unsustainability outcome.

Learning:

A lifecycle outcome requires a cause label, not only an endpoint label.

Primary source:
https://polygon.technology/polygon-zkevm

## Failure-mode taxonomy

Use at minimum:

```text
ECONOMIC_UNSUSTAINABILITY
STRATEGIC_SUNSET
SECURITY_FAILURE
LIQUIDITY_DEATH
USER_RETENTION_FAILURE
DEVELOPER_ECOSYSTEM_DECAY
TOKEN_VALUE_CAPTURE_FAILURE
GOVERNANCE_OR_OPERATOR_FAILURE
UNKNOWN
```

A shutdown or collapse may have multiple contributing causes, but the primary outcome class must remain explicit.

## Research features

### KEEP_FOR_RESEARCH

```text
POST_CATALYST_RETENTION_30_60_90_180_365D
REVENUE_SURVIVAL_SLOPE
INCENTIVE_TREATMENT_EFFECT
CAPITAL_QUALITY
SUBSIDY_ADJUSTED_ACTIVITY
LIQUIDITY_SURVIVAL
TOKEN_PROTOCOL_OPERATOR_DIVERGENCE
```

### WATCH

```text
DEVELOPER_APP_RETENTION
OPERATOR_ECONOMIC_MARGIN
REWARD_TO_REVENUE_RATIO
```

These require stronger longitudinal data and stable definitions before promotion.

### GOVERNANCE_ONLY

```text
PRESTIGE_NEUTRALIZER
```

Founder or VC prestige may influence priors but must never overrule deteriorating empirical survival evidence. Prestige is not itself a negative predictor.

### KILL_UNLESS_INCREMENTAL

```text
ROADMAP_PIVOT_DENSITY
UNIVERSAL_TVL_DRAWDOWN_THRESHOLD
UNIVERSAL_REVENUE_THRESHOLD
```

Do not keep features merely because they are narratively appealing. Require incremental discrimination after matching for age, market regime and incentive intensity.

## Natural-experiment principle

Major project events create useful post-treatment observation windows:

- TGE / airdrop;
- reward reduction;
- points end;
- unlock;
- migration;
- incentive redesign;
- major product pivot.

The preferred question is:

```text
WHAT REMAINED AFTER THE CATALYST?
```

Not:

```text
HOW LARGE WAS THE PROJECT BEFORE THE CATALYST?
```

## Lifecycle horizons

Existing short-horizon launch research remains unchanged:

```text
T+5m
T+1h
T+24h
T+72h
T+7d
```

Long-horizon durability research should observe separately:

```text
T+30d
T+60d
T+90d
T+180d
T+365d
```

These are research checkpoints, not execution gates.

## Anti-hindsight rules

- Never backfill shutdown/survival outcomes into earlier feature snapshots.
- Historical winners and failures generate hypotheses only.
- A retrospective case may not set a live threshold.
- Point-in-time availability must be explicit for every promoted feature.
- Missing historical data stays UNKNOWN.
- Provider methodology changes must be recorded rather than silently normalized.
- A project that later failed may still have been a valid launch-alpha trade.
- A project that survived may still have offered poor token value capture.

## Matched-control program

The first comparison cohort should include:

Survivors:
- Base
- Arbitrum
- Optimism
- Mantle

Negative / terminal controls:
- Blast as economic-unsustainability case
- Polygon zkEVM as strategic-sunset case
- additional failed/sunset cases when sufficiently comparable

Normalize for:

- project/chain age;
- launch cohort;
- market regime;
- incentive intensity;
- token existence;
- fee model;
- business model.

Do not call a feature predictive unless it adds discrimination beyond these controls.

## Agent decision rule

When future agents analyze an early project, token, chain or protocol, separate:

```text
Can it reprice?
Can it remain liquid and sellable?
Can users/activity survive the catalyst?
Can economics survive reduced subsidy?
Can the operator/project remain viable?
Does the token capture any of that value?
```

Do not answer all six with one score.

## Operational integration

Reuse existing owners:

```text
Moonshot Sentinel
-> ALPHA_LAB_LIFECYCLE_ENGINE_v1
-> Phoenix
```

No second scanner.
No second lifecycle engine.
No live threshold change from this research.
No automatic alert change.
No portfolio authority.
No automatic canonical promotion.

## Promotion standard

A feature may move beyond research only after:

1. exact point-in-time reconstruction;
2. matched survivors and failures;
3. false-positive and false-negative accounting;
4. normalization for age/regime/incentive intensity;
5. stable data definition;
6. prospective evidence where applicable;
7. existing Research Lab / scientific owner accepts the evidence.

## Durable principle

```text
Find the rocket.
Then separately measure whether the rocket survives.
```
