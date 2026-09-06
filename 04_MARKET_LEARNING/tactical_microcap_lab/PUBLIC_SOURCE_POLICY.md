# Meme Alpha Public Source Policy

## Principle

The lab should be useful from an iPhone and should not require paid analytics subscriptions to function.

Prefer reproducible public/on-chain evidence. Premium services may improve convenience later, but no core decision may depend on a source the user cannot access or independently cross-check.

## Preferred source roles

### Primary transaction evidence

Use native chain data and reputable explorers / APIs where available for:

- transaction hashes;
- block timestamps;
- transfers;
- contract creation;
- contract verification;
- holder balances;
- event logs;
- deployer / creator relationships.

### Market microstructure

Use sources such as Dexscreener, launchpad endpoints and DEX/pool data for:

- pair identity;
- market cap / FDV;
- liquidity;
- volume;
- transaction counts;
- price path;
- buy/sell flow;
- pair age.

### Wallet enrichment

Public/free wallet analytics can add labels, PnL context and discovery leads.

Nansen may be used on free/public surfaces when accessible. It is especially useful where its free product exposes wallet PnL, Smart Money behavior, holder analysis or labels. Coverage and free-tier access can vary by chain and product surface, so Nansen is an enrichment source rather than a hard dependency.

Rules:

```text
NANSEN_PREMIUM_REQUIRED = false
PAYWALL_CIRCUMVENTION = forbidden
ABSENT_NANSEN_LABEL = not_negative_evidence
NANSEN_LABEL = external_claim_until_cross_checked
```

Where a label matters to the decision, record chain, wallet, label, source URL or screen context and observation timestamp.

### Public dashboards

Dune and similar public dashboards may be used when:

- methodology is visible or inferable;
- data provenance is adequate;
- the dashboard is current enough for the claim;
- a dashboard-derived label is not mistaken for direct chain evidence.

## Evidence hierarchy

For a disputed wallet relationship, prefer:

```text
1. direct transaction / event evidence
2. verified contract / launch configuration
3. reproducible explorer / RPC evidence
4. independent analytics cross-check
5. public labels
6. social claim
7. anonymous / private-source claim
```

Lower layers can create hypotheses. They do not overrule stronger contradictory evidence.

## Private Telegram information

The main framework repository is public.

Never store in it:

- private group invite links;
- private messages copied verbatim unless already public and necessary;
- private names / usernames supplied in confidence;
- identifying source-performance records;
- screenshots containing sensitive private metadata.

Use a non-identifying alias such as `TG_SOURCE_A` in public case records if source timing matters.

If persistent identity-level source tracking later becomes valuable, use the private `secrets` plane and expose only a pseudonymous reference to the public learning layer.

## Data freshness

For live entry advice, historical wallet research can persist but rapidly changing fields must be refreshed:

```text
price
market cap
liquidity
volume
holder count
wallet balances
current transfers
buy/sell flow
social catalyst state
```

A screenshot supplied by the user is useful point-in-time evidence but does not prove the market is unchanged at response time.

## Source expansion rule

New free/public services can be added when they improve a defined problem such as wallet-history reconstruction, cluster detection or realistic liquidity analysis.

Do not add sources merely to increase source count.
