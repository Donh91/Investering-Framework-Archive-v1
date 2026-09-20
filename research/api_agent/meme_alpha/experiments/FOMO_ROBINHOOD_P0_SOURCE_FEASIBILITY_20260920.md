# FOMO / Robinhood Alpha P0 Source Feasibility Receipt

Date: 2026-09-20
Owner: #1087
Authority: RESEARCH_ONLY / SHADOW_ONLY
Status: PARTIAL_PASS_WITH_PROVIDER_GAP

## Question

Can the newly supplied FOMO ecosystem provide denominator-scale, point-in-time identity / leaderboard / trade / position data suitable for a prospective Robinhood/Arc wallet cohort without relying on manual screenshots?

## Findings

### 1. Fomoscope

Current direct retrieval was not available from the research environment. Independent current web indexing also reports the service as unreachable / down during September 2026.

Verdict: DEGRADED_PROVIDER / DO_NOT_DEPEND.

The claimed leaderboards/trades/positions API remains a useful lead, but it cannot be the P0 dependency until live health and API semantics are independently reproduced.

### 2. FomoScan API

Public current OpenAPI documentation is reachable.

Documented capabilities include:
- handle -> verified Solana/EVM wallet identity
- wallet -> FOMO user(s)
- stable user-id lookup
- live handle resolution
- thesis feed by token / user with backward pagination and mandatory id dedupe
- leaderboard snapshots for traders, clans, most-held, trending and graduated tokens
- historical leaderboard lookup using an `at` instant
- leaderboard snapshots sampled every 30 seconds according to provider docs
- account endpoint for entitlement/usage introspection

Important semantics:
- provider claims returned addresses are verified matches
- API is authenticated
- public pricing shown by provider begins at $79/month; therefore no paid dependency is authorized by this receipt
- identity claims still require independent on-chain cross-check before canonical Alpha Lab identity

Verdict: STRONG_IDENTITY_AND_PIT_LEADERBOARD_CHALLENGER, but authenticated live-response validation is still required.

### 3. FomoAPI / public implementation evidence

A current public implementation repository (`ShaikhNabeelShabbir/genie-fomo-api`) exposes a much richer contract than Fomoscope was claimed to provide.

Documented routes include:
- trader directory and profiles
- resolved wallets and trust checks
- open positions
- scorecards with denominator, win rate, best/worst trade, hold time, money in/out, fees, per-token multiples and market caps
- banked vs unrealized PnL
- resolved swaps / trades
- raw transactions
- AUM history and current AUM
- event feed
- token holders/concentration/security/activity/price history
- creator/deployer ledger
- market regime
- health/freshness, per-chain staleness, row counts and capabilities

The implementation explicitly exposes data-health semantics and partial/suspect pricing rather than silently treating incomplete valuation as truth.

The public repository was created 2026-08-31 and was pushed 2026-09-19. It has no declared repository license in the GitHub metadata observed during this review. Therefore code reuse/import is NOT authorized by this receipt.

Verdict: HIGH_VALUE_CONTRACT / ARCHITECTURE / POSSIBLE_DATA_SOURCE, requiring endpoint/auth/terms/license validation before dependency.

### 4. Existing FOMO Robinhood Radar

The already archived `cvxv666/fomo-robinhood-radar` remains useful as a read-only benchmark. Current public repository metadata shows MIT license and active updates. Its documentation says FOMO data is sourced through fomoapi.io and sources fail soft.

This is not a new finding and does not create a new owner.

## P0 adjudication

P0 is NOT blocked by Fomoscope being down.

The source stack should be evaluated in this order:

1. existing deterministic/on-chain framework sources
2. FomoScan for identity + point-in-time leaderboard history, if authenticated validation passes and cost is justified
3. FomoAPI-style data for positions/trades/full-history denominator, subject to access/terms/data-health validation
4. Fomoscope only if it returns and passes the same checks
5. manual/browser scraping only for gaps, never as canonical default

## Hard data contract for P1

No wallet may enter the prospective cohort unless the row can carry:
- observation timestamp
- source + source health
- FOMO stable id / handle where available
- claimed EVM/Solana address
- independent on-chain identity/role verification state
- address role / economic entity state
- chain
- point-in-time leaderboard/source membership
- wallet-set membership frozen before outcome
- provenance for later trades/positions
- UNKNOWN/DEGRADED rather than zero on missing provider data

## Current blocker

Authenticated API keys are not present in this research context. Therefore this pass can validate public contracts and source health, but cannot truthfully claim live authenticated response fidelity, historical completeness or rate-limit behavior.

Do not buy a subscription or create credentials automatically.

## Next smallest defensible action

Run a no-cost / already-authorized authenticated validation if an existing FOMOAPI/FomoScan credential is already present in the framework secret plane. If none exists, keep P1 on public/on-chain verification and treat paid provider activation as an explicit owner decision.

In parallel, define the first prospective cohort from independently re-pulled identities, not screenshot-transcribed addresses.

## Result

P0_SOURCE_FEASIBILITY = PARTIAL_PASS
FOMOSCOPE = DEGRADED
FOMOSCAN = QUALIFIED_CHALLENGER_PENDING_AUTH_TEST
FOMOAPI_CONTRACT = HIGH_VALUE_PENDING_ACCESS_TERMS_VALIDATION
P1_CAN_PROCEED_WITHOUT_FOMOSCOPE = TRUE
TRADE_AUTHORITY = FALSE
