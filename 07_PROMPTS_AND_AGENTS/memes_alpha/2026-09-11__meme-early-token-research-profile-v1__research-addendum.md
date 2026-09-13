# Meme / Early-Token Research Profile v1

**Date:** 2026-09-11  
**Status:** SHADOW_RESEARCH_PROFILE  
**Area:** Memes v3 / Alpha Lab  
**Authority:** RESEARCH_ONLY  
**Canonical parent contract:** `04_RESEARCH_LAB/auto_trading/MICROCAP_RESEARCH_AGENT_CONTRACT_v1.md`  
**Source provenance:** `04_RESEARCH_LAB/auto_trading/source_notes/AT-SRC-0005_563_CODEX_ROBINHOOD_RESEARCH_BUDDY.md`

## 1. Purpose

Adapt the canonical microcap research contract to meme coins and very early tokens without creating a second research engine.

This profile belongs operationally to Memes v3 / Alpha Lab because its highest-value use is early-token triage, wallet/holder research, liquidity-quality analysis, propagation analysis and prospective outcome learning.

The parent microcap contract remains the single source of truth for evidence discipline, point-in-time research, falsification and allowed statuses. This file only changes emphasis and adds meme-specific fields.

No BUY, SELL, sizing, leverage or execution authority is created.

## 2. Integration with the existing Memes v3 workstream

Use this profile inside the existing flow documented in:

`07_PROMPTS_AND_AGENTS/memes_alpha/2026-09-09__memes-v3-autonomous-alpha-research-workstream-v1__operational.md`

It does not replace the existing wallet/event collectors, source contracts, Research Governance, Compounding Learning Controller, capability routing or private-data boundary.

Recommended placement in the existing research flow:

```text
baseline
-> discovery / watched-wallet event
-> token + chain + contract normalization
-> claim/entity dedupe
-> deterministic safety gate
-> wallet / holder / liquidity / social acceleration
-> MICROCAP_RESEARCH_AGENT_CONTRACT_v1 with this MEME profile
-> independent kill-case review when load-bearing
-> SHADOW candidate / WATCH / REJECT / DATA_BLOCKED
-> frozen outcome observation
-> existing Compounding Learning Controller
```

## 3. Meme-specific priority ordering

For meme and early-token cases, research priority is intentionally different from a mature protocol.

### Priority 1 — Identity and tradability

Verify before narrative analysis:

- exact chain;
- canonical contract address / mint;
- duplicate same-ticker contracts;
- canonical pair and quote asset;
- pool creation time;
- actual transferability and sellability;
- whether the apparent market is the real market rather than a spoof/duplicate pair;
- token migration / relaunch / CTO history where relevant.

If identity is unresolved, stop as `DATA_BLOCKED`.

### Priority 2 — Liquidity and execution quality

Capture at `decision_at`:

- real pool liquidity;
- liquidity concentration by venue;
- buy/sell depth asymmetry;
- spread / quote quality;
- estimated impact at predefined notional sizes;
- sell-route viability;
- LP ownership, lock/burn state and withdrawal risk;
- liquidity additions/removals and migration;
- volume relative to real liquidity;
- suspicious volume that is not supported by unique-user growth.

Headline market cap or volume alone is never enough.

### Priority 3 — Contract / creator / supply control

Prioritize:

- deployer / creator;
- first funder and funding-source relationships;
- mint authority;
- freeze / pause / blacklist capability;
- transfer restrictions / tax mechanics;
- proxy / upgrade authority;
- LP control;
- top-holder concentration after known pools/treasury exclusions where justified;
- creator/team-linked wallets where provenance is strong;
- supply concentration changes since launch.

Unknown control rights remain `UNKNOWN`, never implicitly safe.

### Priority 4 — Wallet behavior and holder acceleration

High-value research fields include:

- recurring intentional buyers;
- independently funded wallet convergence;
- common-funder clusters;
- historical wallet hit-rate coverage;
- entry earliness;
- holder-count acceleration;
- unique-buyer acceleration;
- concentration trend;
- accumulation persistence;
- coordinated distribution;
- new-wallet share;
- deployer/team-linked transfers;
- wash / self-trading indicators;
- passive receipt / dust / airdrop separation.

One winning trade never establishes a smart-money label.

### Priority 5 — Propagation and meme formation

Measure propagation rather than merely counting posts:

- first observable narrative/source;
- ordering of on-chain activity versus social propagation;
- unique accounts rather than raw mentions;
- claim-level deduplication across reposts/screenshots/paraphrases;
- account-quality/provenance buckets;
- mention acceleration versus the prior baseline;
- KOL concentration;
- CTO/community-takeover formation;
- phrase/meme capture and derivatives;
- paid boosts versus organic propagation where observable;
- narrative crowding;
- chain-native narrative fit;
- semantic stock/token pairing where relevant to Robinhood Chain.

Ten accounts repeating one thesis are one propagated claim with ten propagation observations, not ten independent signals.

## 4. Baseline-before-discovery rule

Every recurring discovery run should preserve a prior baseline so old chatter cannot be rediscovered as fresh momentum.

At minimum preserve:

- tokens already discussed / watched;
- prior social-source set;
- prior wallet/holder state;
- prior liquidity state;
- prior narrative claims;
- prior origin timestamps.

Freshness should be measured as change from baseline, not raw level.

Candidate acceleration features may include:

```text
unique_buyer_velocity
holder_velocity
qualified_wallet_convergence_delta
liquidity_growth_rate
organic_unique_account_velocity
claim_propagation_velocity
onchain_to_social_lead_lag
concentration_delta
```

These are research features, not buy scores.

## 5. Deterministic safety before ranking

No candidate should be ranked for research attractiveness before deterministic disqualifiers are checked where technically available.

Examples:

- unverifiable contract/mint;
- inability to sell;
- dangerous mint/freeze/blacklist authority without an explained structure;
- extreme owner/deployer control;
- removable/unreliable liquidity;
- obvious duplicate/impostor contract;
- severe wash pattern;
- irreconcilable holder/supply data;
- misleading or unavailable primary market route.

Passing the gate means only `NOT_DISQUALIFIED_BY_AVAILABLE_CHECKS`, never `SAFE`.

## 6. Bull thesis is a downstream presentation artifact

The 563 inspiration includes concise bull-thesis presentation. Alpha Lab may generate such a summary only after the evidence packet exists.

Required order:

```text
facts
-> coverage / missingness
-> risk and executability
-> behavioral evidence
-> framework context
-> independent bull case
-> independent kill case
-> synthesis
-> optional concise thesis
```

A persuasive narrative must never be used to fill a missing field.

## 7. Blind opposition for high-value cases

Use the Astra landing-zone `BLIND_OPPOSITION` mode only when expected research value justifies it.

Both passes receive the same frozen evidence package.

### Bull pass

Identify the strongest mechanism-supported case for continued expansion.

### Kill pass

Independently identify manipulation, control, distribution, liquidity, timing and narrative failure mechanisms.

Do not show one pass to the other before commit. Preserve disagreement as evidence; do not average it away.

## 8. Frozen point-in-time research packet

Every meaningful case should be joinable to later outcomes without hindsight.

Use the parent contract's point-in-time discipline and preserve `decision_at` plus source observation timestamps.

Meme-profile feature snapshot should include, where available:

```text
identity_confidence
pool_age
liquidity_usd
liquidity_concentration
estimated_slippage_buckets
sellability_state
lp_control_state
mint_freeze_blacklist_state
holder_count
holder_velocity
holder_concentration
concentration_delta
unique_buyers
unique_buyer_velocity
qualified_wallet_count
wallet_convergence_delta
common_funder_evidence
accumulation_persistence
wash_risk_evidence
organic_unique_accounts
social_velocity
claim_dedupe_count
kol_concentration
onchain_to_social_lead_lag
cto_state
narrative_crowding
framework_regime
meme_rotation_state
coverage_missingness
```

Unavailable data stays null/unknown and carries provenance.

## 9. Outcome labels for Astra learning

Reuse the parent contract and existing Memes v3 outcome loop. Do not build a parallel learning controller.

Preferred fixed windows for early tokens:

```text
1h
4h
24h
3d
7d
30d
```

Attach where reproducible:

- forward return;
- MFE;
- MAE;
- liquidity change;
- volume change;
- holder-count and concentration change;
- qualified-wallet continuation/distribution;
- social/narrative persistence;
- migration / untradeable / rug state;
- whether the original bull thesis survived;
- whether a predeclared kill condition fired.

The research objective is not to remember spectacular winners. It is to learn which pre-decision features discriminate winners, failures and manipulated/noisy cases prospectively.

## 10. Research hypotheses this profile enables

Astra may later test, under existing Research Lab governance:

1. Whether qualified-wallet convergence adds information beyond raw wallet count.
2. Whether unique-buyer/holder acceleration is more useful than volume acceleration.
3. Whether on-chain-first propagation outperforms social-first propagation after liquidity/risk controls.
4. Whether common-funder clustering predicts coordinated manipulation or legitimate early communities.
5. Whether organic propagation breadth adds value beyond KOL-heavy propagation.
6. Whether liquidity growth plus improving distribution is more robust than market-cap momentum alone.
7. Whether CTO formation is constructive only under specific holder/liquidity conditions.
8. Whether meme/alt regime context materially changes the value of early-token features.
9. Which risk features most strongly predict rugs, migrations, untradeability or severe MAE.
10. Whether the structured profile improves failure detection and reproducibility versus generic free-form token research.

Every hypothesis needs a frozen data contract, baseline, falsifier and prospective/out-of-time test before promotion.

## 11. Alpha Lab decision boundary

Allowed research outcomes remain:

```text
REJECT
WATCH
RESEARCH_QUEUED
DATA_BLOCKED
```

If an existing Alpha Lab layer uses additional non-execution Shadow classifications, this profile may map into them only through that existing owner.

This file cannot create a portfolio action or change an existing portfolio permission.

## 12. Duplication rule

Do not copy the canonical microcap contract into this folder.

The ownership model is:

```text
04_RESEARCH_LAB/auto_trading/MICROCAP_RESEARCH_AGENT_CONTRACT_v1.md
    = canonical generic microcap research contract

07_PROMPTS_AND_AGENTS/memes_alpha/2026-09-11__meme-early-token-research-profile-v1__research-addendum.md
    = meme / early-token profile and Alpha Lab integration

07_PROMPTS_AND_AGENTS/memes_alpha/2026-09-09__memes-v3-autonomous-alpha-research-workstream-v1__operational.md
    = existing autonomous Alpha Lab research owner
```

If the parent contract changes, this profile should be compatibility-audited rather than forked.