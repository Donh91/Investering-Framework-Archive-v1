# MEME / EARLY-TOKEN RESEARCH PROFILE v1

**Status:** `PREPARED_NOT_ACTIVE`  
**Owner:** Meme Alpha Lab  
**Authority:** `RESEARCH_ONLY` / `NONE_BY_ITSELF`  
**Research idea:** `MAL-RI-0001`  
**Source inspiration:** `AT-SRC-0005`

## Canonical inheritance

This file is a **profile/adapter**, not a second research engine.

Canonical shared contract:

`04_RESEARCH_LAB/auto_trading/MICROCAP_RESEARCH_AGENT_CONTRACT_v1.md`

Canonical source note:

`04_RESEARCH_LAB/auto_trading/source_notes/AT-SRC-0005_563_CODEX_ROBINHOOD_RESEARCH_BUDDY.md`

If this profile conflicts with the canonical shared contract, the canonical contract wins unless the Meme Alpha Lab has a narrower safety rule.

The purpose of this profile is to specialize the shared microcap evidence model for memes, newly launched tokens, tiny-liquidity assets, CTO/community-takeover situations and other short-lived speculative setups where wallet behavior and market microstructure often matter more than durable fundamentals.

## No duplicate-data rule

Before collecting anything, resolve whether the requested field already exists in:

- the current Meme Alpha Lab case packet;
- wallet / cluster records;
- source records;
- existing on-chain captures;
- Framework market / regime state;
- a canonical upstream data owner.

Reuse point-in-time evidence when its provenance and `observable_at` make it valid for the decision timestamp.

Do **not** recollect the same evidence merely because this profile asks for it. New retrieval is justified only when:

- existing evidence is stale for the intended horizon;
- the field is absent;
- provenance is insufficient;
- a fresh state transition is itself the feature being measured.

## Meme-specific research objective

For decision timestamp `T`, freeze a reproducible packet answering:

> What was actually knowable before `T` about identity, contract control, executable liquidity, wallet behavior, distribution, organic-vs-coordinated participation, social propagation and temporary-demand mechanics?

The packet must remain separate from any later outcome.

## Profile pipeline

```text
BASELINE
-> DISCOVERY
-> ENTITY / CA DEDUPE
-> CLAIM DEDUPE
-> SAFETY + SELLABILITY GATE
-> WALLET / HOLDER ACCELERATION
-> SOCIAL / NARRATIVE ACCELERATION
-> CANONICAL MICROCAP RESEARCH CONTRACT
-> BLIND KILL CASE WHEN MATERIAL
-> SHADOW CANDIDATE / REJECT / WATCH / DATA_BLOCKED
-> IMMUTABLE OUTCOME MATURATION
```

The profile may enrich the existing Meme Alpha Lab workflow. It may not bypass `TOKEN_AUDIT_GUIDE.md`, `WALLET_ALPHA_RESEARCH_PROTOCOL.md` or lab governance.

## 1. Baseline before discovery

A current baseline is required so the lab does not rediscover old chatter as fresh momentum.

Freeze where available:

- tokens already discussed / audited;
- canonical contract addresses and chain;
- prior thesis / claims already seen;
- known creator / deployer / wallet clusters;
- current holder and unique-trader counts;
- current social-source set and narrative labels;
- current liquidity / market-cap state;
- current broad meme / alt / chain regime.

The baseline creates the comparison point for acceleration.

## 2. Identity and entity dedupe

Always key the asset by:

`chain + canonical contract address`

Ticker alone is never identity.

Collapse:

- duplicate tickers;
- cloned / impersonating contracts;
- repeated URLs pointing to the same contract;
- pool migrations when economically the same token is being tracked.

Preserve migrations as events rather than inventing a new independent asset.

## 3. Claim-level dedupe

Social repetition is not independent evidence.

Normalize materially equivalent posts into one claim event and separately preserve propagation metadata:

- earliest observable origin;
- number of independent accounts repeating it;
- account/source quality where supported;
- quote/repost vs independently sourced claim;
- propagation velocity;
- whether the claim is verifiable on-chain / in primary documentation.

Ten accounts repeating the same unsupported thesis are **one claim with wide propagation**, not ten confirmations.

## 4. Safety and sellability gate

Before narrative ranking, verify the market can actually be traded and exited.

Prioritize:

- CA / chain / pair certainty;
- transferability and sellability;
- mint / freeze / blacklist / tax / proxy / admin controls;
- LP ownership / lock / burn state;
- liquidity withdrawal risk;
- route dependence;
- quote-side liquidity;
- spread and realistic slippage;
- price impact at the intended research notionals;
- concentration of likely sellers;
- suspicious launch or privileged-wallet mechanics.

Failure on a hard safety field can terminate the candidate before expensive research.

## 5. Wallet and holder acceleration

Absolute counts are weaker than directional change when the opportunity is early.

Measure where reproducible:

- unique-buyer acceleration;
- unique-seller acceleration;
- holder growth velocity;
- holder concentration change;
- top-holder additions / reductions;
- recurring high-quality buyer participation;
- funding-source overlap;
- recurring wallet-cluster participation;
- deployer / creator / team-linked flows when provable;
- new-wallet share;
- wallet age distribution;
- LP additions / removals;
- accumulation vs distribution;
- buyer-size distribution;
- wash / self-trading indicators.

Do not call a wallet `smart money` from one winner. Reuse the lab's wallet evidence grades and historical records.

## 6. Social and narrative acceleration

Measure momentum as a change process rather than raw loudness.

Candidate features include:

- independent-claim count change;
- unique credible account growth;
- propagation velocity;
- origin diversity;
- KOL concentration;
- narrative crowding;
- organic community growth vs synchronized promotion;
- CTO / community-takeover evidence;
- catalyst verification status;
- chain-specific attention growth;
- sentiment direction only when source quality is known.

High mention volume with flat unique accounts or highly duplicated wording is a weak signal and may indicate spam/wash-like propagation.

## 7. Framework context

Consume, never recreate, upstream state such as:

- broad crypto risk regime;
- BTC / ETH leadership;
- alt / meme rotation;
- speculative breadth;
- chain activity / liquidity;
- volatility / stress state;
- execution-risk regime.

This context is conditioning evidence, not permission to weaken token-specific risk checks.

## 8. Bull thesis and kill case

A concise bull thesis may be generated **only after** the evidence packet is frozen.

For material candidates, the kill case should be independently produced under `BLIND_OPPOSITION` when practical.

Bull thesis asks:

- What temporary demand mechanism could persist?
- What evidence is improving rather than merely large?
- Which wallets / holders / users are expanding participation?
- What is differentiated versus similar memes?
- Why might attention or liquidity continue over the stated horizon?

Kill case asks:

- Which apparently positive evidence is circular, duplicated or manipulable?
- Who can become immediate exit liquidity?
- What contract / LP / concentration risk can invalidate price discovery?
- Is volume real relative to unique buyers and holder growth?
- Is the token already in distribution despite social acceleration?
- What single observable event should terminate the thesis?

Disagreement remains visible; do not average bull and kill case into fake certainty.

## 9. Output

This profile extends the canonical research packet with meme-specific optional features:

```text
baseline_ref
claim_clusters
claim_origin_count
propagation_velocity
kol_concentration
unique_buyer_velocity
unique_seller_velocity
holder_velocity
holder_concentration_delta
wallet_cluster_acceleration
funding_overlap
wash_risk_flags
sellability_state
quote_side_liquidity
slippage_bands
lp_change
cto_state
narrative_crowding
meme_rotation_context
kill_case_trigger
```

Keep unknown fields as `UNKNOWN`; never silently coerce missing evidence to neutral or safe.

## 10. Shadow outcome labeling

Every accepted point-in-time packet should mature against future outcomes without rewriting the original packet.

Use Meme Alpha Lab native horizons where available:

- +15m
- +1h
- +6h
- +24h
- +72h
- +7d

Additional 30d survival context may be retained when useful but is not the primary tactical horizon.

Preserve at minimum:

- forward return;
- MFE / MAE;
- time to 2x / 5x / 10x where reached;
- time to -50% / -80% where reached;
- peak / trough liquidity;
- peak market cap;
- post-peak drawdown;
- holder trajectory;
- unique-buyer trajectory;
- wallet-cluster continuation / exit;
- narrative persistence / decay;
- rug / liquidity-removal / migration / untradeable state;
- whether the original bull mechanism remained valid;
- whether the frozen kill criterion fired.

## 11. Astra research hypotheses

Astra should test this profile as a feature system, not assume it is superior.

Priority comparisons:

1. structured profile vs generic free-form token research;
2. raw volume / mentions vs unique-participant acceleration;
3. tweet/post count vs claim-deduplicated propagation;
4. token-only research vs wallet-cluster-enriched research;
5. bull-only reasoning vs blind bull + kill-case review;
6. headline liquidity vs executable sellability / slippage features;
7. fixed heuristics vs regime-conditioned features;
8. full profile vs ablated subsets to estimate marginal value per data/token cost.

Measure:

- hard-risk detection recall;
- false-positive candidate rate;
- false-negative missed asymmetry rate;
- reproducibility across repeated runs;
- forward outcome discrimination;
- calibration of uncertainty;
- marginal information added per token / data request / specialist call.

## Promotion rule

This profile remains `PREPARED_NOT_ACTIVE` until sufficient prospective or leakage-safe historical evidence exists.

Promotion must use existing Meme Alpha Lab learning governance and Framework adjudication. No single winner, source endorsement or impressive retrospective example is sufficient.

## Hard boundaries

This profile must never:

- place orders;
- connect execution permissions;
- coordinate market manipulation;
- recommend pumping a token;
- hide liquidity limitations;
- infer private identities from wallet behavior without evidence;
- treat a social source as proof;
- treat a later outcome as pre-decision evidence;
- create a second regime engine;
- fork the canonical Microcap Research Agent Contract merely for convenience.
