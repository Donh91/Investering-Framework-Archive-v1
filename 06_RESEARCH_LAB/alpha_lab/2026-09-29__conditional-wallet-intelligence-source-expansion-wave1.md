# Conditional Wallet Intelligence — Source Expansion Wave 1

Date: 2026-09-29
Status: SHADOW_RESEARCH / OPEN_SOURCE_EXPANSION
Parent: 06_RESEARCH_LAB/alpha_lab/2026-09-29__conditional-wallet-intelligence-open-research-program-v1.md
Owners: #1087 / #1134
Authority: RESEARCH_ONLY
New scanner: NO
New scheduled workflow: NO
Trading authority: NONE

## Purpose

Expand wallet/deployer/early-information research beyond the two owner-supplied Bando lists.

The Bando posts are seeds, not the source universe.

The goal is to discover additional:
- public wallet lists;
- deployer cohorts;
- first-buyer datasets;
- KOL / trader histories;
- funding / cluster sources;
- point-in-time deployer reputation;
- native-chain buyer/deployer events;
- open-source research methods;

and route only reproducible incremental evidence into existing Conditional Wallet Intelligence / CLEAN_G3.

## 1. Intelligence routing

Current framework API routing already exposes active:
- `gpt-6-luna`
- `gpt-6-sol`

Current bounded role split for this research:

### GPT-6 Luna
Use for high-volume, low-cost work:
- source discovery triage;
- URL/repository inventory;
- field extraction;
- address normalization;
- duplicate detection;
- simple point-in-time metadata checks;
- compact candidate packets;
- negative-control bookkeeping.

Luna output remains research evidence, not signal authority.

### GPT-6 Sol
Use selectively for high-information tasks:
- adversarial source audit;
- hard entity / common-control ambiguity;
- conflicting evidence adjudication;
- experiment / falsifier design;
- source-of-source synthesis;
- semantic reconciliation of realized vs unrealized / marked PnL;
- post-research senior review when a candidate could materially affect G3.

Do not use Sol merely to repeat Luna's inventory.

### Claude / Audit Bridge
Use for independent, broad, source-expansion research:
- large cross-source scans;
- source-of-source discovery;
- alternative hypothesis search;
- denominator reconstruction;
- adversarial review of wallet/deployer narratives;
- public X / Telegram / GitHub / provider-doc discovery;
- provider/tool capability audits.

Claude remains Bridge-only and cannot promote or mutate framework truth.

## 2. Source discovery Wave 1

These are DISCOVERY LEADS only. No provider integration is authorized.

### S1 — Birdeye First Buyers API

Public Birdeye documentation, July 2026, describes:
`GET /token/v1/first-buyers`

Candidate value:
- earliest Solana token buyers;
- current position classification;
- direct candidate support for first-buyer / exit-quality reconstruction.

Research questions:
- exact timestamp/block granularity;
- completeness;
- historical query semantics;
- current-state leakage;
- cost / retention;
- whether native chain reconstruction is cheaper / more authoritative.

Disposition:
`HIGH_VALUE_SOURCE_LEAD / BENCHMARK_BEFORE_USE`

### S2 — MadeOnSol SDK / API

Inspected public SDK:
`MadeOnSol/madeonsol-sdk@393f00ef9aa163631fba752c963b97efba940a38`

This is a particularly relevant new lead.

Public SDK exposes/claims:
- KOL trade feed;
- KOL leaderboard / wallet PnL;
- KOL affinity pairs / coordination;
- "first KOL buy on a fresh token" events;
- Pump.fun deployer alerts;
- deployer token history;
- wallet tracker;
- exact market cap at trade;
- point-in-time deployer reputation through an `as-of` endpoint;
- 180-day KOL retention;
- explicit null / unknown semantics in several endpoints.

Notable methodological claim in example code:
S-tier first-touch scouts are described as having follow-on KOL behavior materially above a baseline in a 38-day backtest.

This must NOT be accepted without reproduction.

Why this source is interesting:
the `deployerAsOf` concept directly attacks one of CLEAN_G3's hardest problems: historical label leakage.

Required benchmark:
- verify point-in-time snapshot semantics;
- reproduce a small deployer cohort independently;
- compare "first touch" vs native first buyer truth;
- test KOL coordination after entity collapse;
- inspect whether current rankings are outcome-derived;
- price / credits / terms;
- matched failures.

Disposition:
`VERY_HIGH_VALUE_SHADOW_AUDIT_CANDIDATE`

### S3 — PumpScope

Public Chrome listing claims:
- ~100 "elite" wallets;
- historical early-buy graduation precision;
- monthly rebuild;
- smart-wallet counts over token pages;
- comparison to a low graduation base rate.

Potential value:
- externally curated wallet cohort;
- published precision methodology candidate.

Major risk:
- opaque wallet selection;
- graduation is not sellable alpha;
- monthly rebuild can create retrospective label leakage;
- browser-extension output may not have reproducible historical state.

Disposition:
`RESEARCH_SOURCE / METHODOLOGY_AUDIT_ONLY`

### S4 — Bonding Terminal

Public site claims:
- pump.fun + stonk.fun + Pons coverage;
- 2,430+ smart-money / KOL wallets;
- alerts with entry price and timestamp;
- weekly winner ledger;
- bonding-curve + market-cap + volume + holder + wallet behavior.

Potential value:
- cross-venue prospective call ledger;
- Pons relevance;
- source/caller discovery;
- external alert timing benchmark.

Major risk:
- winner-oriented public presentation;
- unknown denominator;
- opaque wallet qualification;
- unclear immutable history and missed-call accounting.

Disposition:
`PROSPECTIVE_LEDGER_CHALLENGER / DENOMINATOR_REQUIRED`

### S5 — KolScan / GMGN aggregation through open-source tooling

New public repository lead:
`nirholas/kol-quest@f7e4911f95dbcb6f093065409524050f4a0d6f3e`

Observed capabilities:
- KolScan leaderboard ingestion;
- wallet detail;
- GMGN wallet categories such as smart_degen, kol, sniper, fresh_wallet, top_dev, pump_smart;
- X profile enrichment;
- Pump.fun / Jupiter / Raydium / Jito source combination;
- MCP surface.

Potential value:
- source inventory;
- address discovery;
- negative-control candidate generation;
- methodology harvesting.

Risks:
- scraped / derived provider data;
- provider label opacity;
- terms and historical label timing;
- current leaderboard survivorship.

Disposition:
`SOURCE-HARVEST / NO SCORE IMPORT`

Existing GMGN/FOMO research remains the primary local owner for overlap.

### S6 — CabalSpy ecosystem

GitHub discovery surfaced:
- `CabalSpy/CabalSpy-MCP-Server`
- language SDKs;
- KOL realtime holder table.

Potential value:
- clustering / cabal methodology;
- holder / KOL intersection;
- possible MCP-accessible research primitives.

State:
not audited in this wave.

Disposition:
`DISCOVERY_LEAD / AUDIT_REQUIRED`

### S7 — Pump.fun native public rankings

Pump.fun itself exposes current public top-trader / profit surfaces.

Potential value:
- raw candidate generation;
- public-exposure timestamp;
- benchmark against third-party KOL/smart-wallet lists.

Risks:
- current leaderboard survivorship;
- current profit != prior point-in-time edge;
- social/copy-trading contamination.

Disposition:
`NEGATIVE-CONTROL / DISCOVERY_ONLY`

## 3. Search mandate

Do not stop at the above providers.

Continuously search for:
- public X wallet threads;
- Telegram wallet/deployer lists;
- public call channels with immutable timestamps;
- GitHub wallet analytics;
- launchpad-specific developer histories;
- first-buyer datasets;
- cabal / funding graph research;
- KOL list archives;
- transparent negative result studies;
- providers with historical "as-of" labels;
- raw event APIs that can replace derived scores.

For every new source record:
- discovered_at;
- source URL / repository;
- exact revision/date where possible;
- what fields are available;
- whether fields are point-in-time;
- whether source is current-only;
- whether there is a denominator;
- provider / licensing boundary;
- overlap with existing sources;
- cheapest decisive falsifier.

## 4. Source acceptance rules

A source is valuable only if it adds at least one of:

1. earlier information;
2. cleaner point-in-time history;
3. better economic-entity resolution;
4. broader denominator;
5. better exit / realized-outcome evidence;
6. better cross-source falsification;
7. lower cost / latency for an already-needed fact.

Reject or deprioritize if it only adds:
- another opaque smart-wallet score;
- another winner leaderboard;
- another current PnL label;
- another copy-trading interface;
- the same data in prettier UI.

## 5. Public-list discovery and contamination

External wallet lists are dual-purpose evidence:

Before publication:
- possible independent wallet edge.

After publication:
- the wallet may become a copied signal;
- follower activity may change price impact;
- public visibility can destroy or alter edge.

Therefore every public list should preserve:
`PUBLIC_WALLET_LIST_EXPOSURE_AT`.

Do not merge pre- and post-publication observations.

## 6. API / model efficiency

The objective is not maximal model usage.

Preferred order:

`deterministic/native read -> GPT-6 Luna extraction/triage -> GPT-6 Sol only for hard ambiguity/high-value synthesis -> Claude independent challenge when marginal value is high`.

Use parallel model work only when roles are orthogonal.

Examples:
- Luna builds 100-source candidate inventory;
- Claude independently searches for missing source families and attacks source quality;
- Sol adjudicates the 5 highest-value conflicts/test designs.

Avoid:
- Sol summarizing 100 ordinary pages;
- Claude repeating deterministic GitHub inventories;
- three models independently rewriting the same source note.

## 7. Current infrastructure constraint

GitHub Actions included minutes are exhausted on 2026-09-29 and reset is expected 2026-10-01.

Therefore Wave 1:
- creates no new scheduled Actions;
- may use existing app/API/Bridge research lanes;
- preserves source leads for post-reset bounded testing;
- does not infer scanner/model failure from missing runtime observations during the quota hard stop.

## 8. Next highest-value audits

Current research ordering:

1. **MadeOnSol** — point-in-time deployer + first-touch / KOL convergence semantics.
2. **Birdeye First Buyers** — deterministic earliest-buyer and exit-state usefulness.
3. **CabalSpy** — clustering/entity methodology.
4. **Bonding Terminal** — immutable-call / denominator audit.
5. **PumpScope** — wallet-selection / graduation-methodology audit.
6. **KolScan/kol-quest** — source harvest and candidate expansion only.

This ordering is research priority, not provider endorsement.

## 9. Success condition

Wave 1 succeeds only if it yields:
- new independent wallet/deployer seeds with denominator;
- a materially better point-in-time field;
- a better entity/control test;
- or a source that improves prospective CLEAN_G3 measurement.

Finding more wallet names alone is not success.
