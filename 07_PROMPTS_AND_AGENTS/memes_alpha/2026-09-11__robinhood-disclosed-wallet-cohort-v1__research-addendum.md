# Memes v3 — Robinhood Disclosed Wallet Cohort v1

**Date:** 2026-09-11  
**Status:** OWNER-APPROVED RESEARCH INPUT  
**Authority:** RESEARCH ONLY  
**Parent owner:** `2026-09-09__memes-v3-autonomous-alpha-research-workstream-v1__operational.md`  
**Method owner:** `2026-09-11__memes-v3-empirical-hardening-adjudication-v1__research-addendum.md`

## Purpose

Bind a newly user-supplied Robinhood Chain wallet cohort into the existing Memes v3 / Alpha Lab research workstream without publishing the exact competitive wallet list and without creating a parallel scanner, scheduler, signal engine or trade path.

The source is an X post by `@rektfencer` that publicly disclosed six Robinhood Chain wallets associated by the author with unusually early CASHCAT and/or PONS activity. The source itself explicitly allows that the results may be luck. Therefore the cohort enters as a **research lead**, not as qualified smart money.

Primary source:

`https://x.com/rektfencer/status/2098040577686454764?s=46`

Deterministic disclosure anchor from the X status Snowflake:

`2026-09-10T13:27:08.086Z`

## Restricted binding

Exact wallet identifiers and source-level performance claims are stored only in the restricted data plane:

`Donh91/secrets:private_research/memes_alpha/wallet_research/2026/09/11/rektfencer_robinhood_disclosed_cohort_v1.json`

The current cumulative private seed is:

`Donh91/secrets:private_research/memes_alpha/seeds/2026/09/11/seed.json`

The 2026-09-09 predecessor seed remains immutable historical evidence and must not be rewritten.

## Research state

The cohort is:

`PROVISIONAL_KOL_DISCLOSED_RH_WALLET_COHORT`

Research state:

`WATCH`

This means:

- include the cohort in the existing watched-wallet research universe;
- do not qualify any wallet from the KOL post alone;
- deterministically distinguish intentional buys from passive receipts / dust / spam;
- freeze a prospective research row when a watched wallet intentionally acquires a previously unseen token;
- escalate to entity/convergence research when multiple cohort wallets buy the same token;
- treat funding-source overlap or graph evidence as a reason to reduce assumed independence;
- mature 1h / 6h / 24h / 7d outcomes under the existing outcome loop;
- keep exact wallet values private in public health, logs, issues, PRs and artifacts.

No separate ChatGPT app automation is created by this addendum. Existing GitHub-native Memes v3 research cadence remains the intended execution owner once implemented/active.

## Primary experiment

This cohort is particularly useful because the public disclosure creates a clean visibility anchor.

Main question:

> Did the wallets have repeatable conditional edge before public disclosure, and does that edge persist, decay or invert after the wallets become broadly visible?

The workstream should therefore separate:

1. **Pre-disclosure reconstruction** — historical intentional acquisitions, including failures and dead tokens, exact entry state, entity links and executable outcomes.
2. **Post-disclosure prospective observation** — freeze new acquisitions after the public visibility anchor before later outcomes are known.
3. **Matched controls** — compare against Robinhood Chain wallets/tokens matched by period, venue, token age, liquidity and size where possible.
4. **Visibility/capacity** — test whether any performance change is related to public visibility and estimated follower notional relative to executable depth rather than raw follower counts.

Candidate quantity:

`signal_capacity_pressure = estimated_follower_notional / executable_depth`

It remains a SHADOW research feature until prospectively validated.

## Required anti-survivorship work

Do not start from CASHCAT/PONS winners and infer wallet skill.

For each wallet, reconstruct at least the last 20-50 intentional acquisitions where data permits and include:

- losses;
- dead/untradeable tokens;
- ordinary returns;
- post-pump entries;
- passive-receipt exclusions;
- position/route executability;
- entry class;
- common funders / entity links;
- outlier-ablation results.

Historical source-reported PnL is a lead to reproduce, not ground truth.

## Address-role gate for leaderboard and PnL candidates

A 2026-09-12 owner-supplied Robinhood Chain 7D realized-PnL leaderboard exposed a material failure mode: addresses associated with launchpad/protocol inventory can appear as extremely profitable "traders" when generic wallet-PnL logic does not identify address role first.

Therefore **no leaderboard/PnL-discovered address may enter `WATCH` merely because it ranks highly.**

Before qualification, classify the address from chain-native evidence as one of:

- `EOA_TRADER`;
- `SMART_ACCOUNT_TRADER`;
- `PROTOCOL_SERVICE`;
- `CURVE_OR_LAUNCHPAD_INVENTORY`;
- `ROUTER`;
- `POOL_OR_LP_INFRASTRUCTURE`;
- `FEE_COLLECTOR`;
- `DEPLOYER_OR_CREATOR_INFRASTRUCTURE`;
- `BRIDGE_OR_SETTLEMENT`;
- `UNKNOWN`.

`UNKNOWN` cannot be promoted to wallet-alpha watch status.

Service / inventory / router / pool / fee-collector flows must be excluded from discretionary PnL and intentional-buy evidence. Role classification must precede realized-PnL reproduction, entity clustering and conditional-skill scoring.

The preferred sequence is:

`ADDRESS ROLE -> INTENTIONAL SWAP FILTER -> SERVICE EXCLUSION -> ENTITY CLUSTERING -> PNL REPRODUCTION -> OUTLIER ABLATION -> CONDITIONAL SKILL -> VISIBILITY/CAPACITY -> PROSPECTIVE WATCH`

Detailed exact-address evidence for the 2026-09-12 leaderboard audit remains restricted. Public methodology provenance is recorded in:

`04_RESEARCH_LAB/auto_trading/source_notes/AT-SRC-0010_MARAN_RH_TOOL_STACK_AND_WALLET_LEADERBOARD_AUDIT.md`

## Promotion boundary

This cohort may contribute to:

- Conditional Wallet Intelligence;
- visibility/adverse-selection research;
- signal-capacity research;
- Multi-Wallet Convergence research;
- Robinhood Chain entity-graph research;
- Early Confirmation research.

It may not by itself create:

- `QUALIFIED_ALPHA` status;
- BUY/SELL/sizing output;
- portfolio authority;
- new public watchlist disclosure;
- a canonical wallet score;
- a new scheduler or research-governance stack.

Existing Memes v3 promotion, alert, privacy and governance rules remain authoritative.

## Seed resolution rule

Future Memes v3 collectors must not hard-code the original 2026-09-09 private seed as the permanent watchlist.

Resolve the latest valid cumulative `MEMES_ALPHA_PRIVATE_SEED_V1` snapshot, preserve its predecessor lineage, and fail closed on schema/provenance ambiguity. Public readback must remain provider-value-free and identifier-free.

This rule ensures newly owner-approved research wallets can enter the ongoing research set without rewriting historical seeds or requiring manual GitHub administration.
