# Rick research adjudication -> Alpha Lab design v1

Date: 2026-09-17
Owner: existing Meme Alpha / Alpha Lab stack
Implementation owner: issue #1087
Status: ADJUDICATED DESIGN — no parallel engine authority

## Decision

The GPT Deep Research feature harvest and Claude adversarial review are complementary, but Claude's architecture objection controls: Alpha Lab must NOT build a Rick clone. The repository already owns prospective evidence, wallet/cabal forensics, source authentication, outcome maturation, sellability and red-team controls.

Rick is best treated as a **public visibility benchmark/instrument**. Its high-density scan demonstrates which marginal/public facts a large population can see quickly. Alpha Lab should reproduce only the useful visibility projection, then spend research depth on the information gap that public cards cannot resolve: graph structure, provenance, coordination, deployer lineage, realizability, source quality and prospective outcomes.

## Canonical design

```text
DISCOVERY / CA
  -> DATA INTEGRITY GATE
  -> PUBLIC VISIBILITY SNAPSHOT (Rick-parity benchmark)
  -> IMMUTABLE FIRST-SEEN FREEZE
  -> VISIBILITY GAP
  -> deterministic information-value escalation
      -> existing wallet/cabal/source/deployer Deep Dive
  -> existing prospective outcome maturation
  -> existing realizability / MFE / MAE / missed-winner machinery
  -> research/red-team adjudication
```

No new competing scanner, scorer, ledger or forecast owner is created.

## P0 — rows before features

The first engineering priority is to verify and, if needed, repair the existing birth-tape/census/prospective collection path. A sophisticated feature set without point-in-time rows cannot establish incremental information value.

Required properties:
- exact observation timestamp;
- exact CA/chain/pool identity;
- source lineage/hash where required;
- immutable first-seen values;
- UNKNOWN remains UNKNOWN;
- failures and missed winners remain in denominator;
- later outcomes never rewrite original observations.

If a provider returns implausibly byte-identical market payloads after material elapsed time despite reported activity, classify the affected measurement as `SUSPECTED_STALE_CACHE` and quarantine it. Presence/absence may be retained only if independently valid for that question. `NOT_RUN` is never `PASS`.

## P1 — Public Visibility Snapshot

Add/derive a compact projection from EXISTING data owners where available:

- token / exact CA / chain / canonical pool;
- observation age;
- price;
- MC and FDV as separate explicitly sourced semantics;
- liquidity;
- volume and transaction activity;
- buy/sell activity when source-backed;
- holder count;
- raw holder concentration, explicitly marked `PUBLIC_MARGINAL`;
- wallet-age/fresh-wallet aggregates when source-backed, explicitly marked `PUBLIC_MARGINAL`;
- current vs prior peak with exact time basis where point-in-time evidence permits;
- bytecode uniqueness/copy similarity;
- recycled social account / deleted-post evidence;
- source/caller identity and first-seen timestamp;
- DATA HEALTH / conflict/staleness state.

These fields are descriptive. They do not become alpha weights merely because they are easy to calculate or popular in Telegram scanners.

## P2 — Visibility Gap

The decision-useful distinction is:

```text
PUBLIC / MARGINAL INFORMATION
!=
GRAPH / COORDINATION / PROVENANCE INFORMATION
```

Raw top-holder percentages cannot distinguish independent holders from coordinated wallets with a common funder. Therefore a low TH/top-10 number is never a safety proof.

Deep evidence remains with existing wallet/cabal owners and includes, where evidence permits:

- self-initiated trade vs router attribution vs direct transfer/dust;
- common funders and wallet clusters;
- synchronized entries/exits;
- deployer proximity and historical launch graph;
- repeat/known alpha wallets with point-in-time reputation;
- pre-call vs post-call timing;
- accumulation vs distribution;
- source authentication / first-party provenance;
- liquidity and sellability;
- realizable rather than touched returns.

## Deterministic escalation

Escalate QuickScan to existing Deep Dive when at least one material trigger exists:

- DATA_CONFLICT or suspected stale source;
- suspicious holder/funder cluster;
- known or recurring wallet with point-in-time evidence;
- deployer anomaly/history worth resolving;
- exceptional liquidity/volume/holder velocity requiring explanation;
- first-party/provenance claim;
- high-information caller/source;
- public card appears benign while graph evidence is unresolved;
- unusual bytecode/social-account provenance;
- asymmetric R/R makes additional information economically valuable.

Absence of a trigger should conserve API/model spend.

## Source/caller learning

Preserve caller/source at first observation. Later evaluation must separate:

- discovery quality: how early/usefully the source surfaced the asset;
- timing quality: state at first sight relative to realizable later outcomes.

Do not import ATH-only leaderboards or reward maximum favorable excursion without MAE, liquidity and realizability. Existing outcome/sellability owners remain authoritative.

## PVP / analog engine

KEEP AS SHADOW RESEARCH ONLY until enough prospective rows exist.

Any future analog cohort must be:
- point-in-time;
- age matched;
- chain/venue/context aware;
- leakage safe;
- inclusive of failures/dead pools;
- based on frozen features available at the comparison time;
- evaluated with realizable outcomes, not retrospective peak-only labels.

No 2x/5x/10x conditional probabilities may be promoted from a retrospectively selected cohort.

## Rick ideas accepted

1. High-density mobile scan as a presentation benchmark.
2. Peak-relative context, only with explicit timestamp/window semantics.
3. Bytecode uniqueness/copy-contract evidence.
4. Recycled social-account/deleted-post evidence.
5. Deployer-history presentation backed by existing graph evidence.
6. Source/caller attribution and prospective evaluation.
7. PVP only as a hypothesis for later leakage-safe testing.

## Rejected

- Rick clone / parallel Telegram scanner as architecture goal;
- parallel wallet engine, evidence ledger or scorer;
- raw TH/top-10 as safety/quality score;
- fresh-wallet percentage as standalone alpha;
- social popularity as alpha;
- ATH-only caller ranking;
- retrospective analog hit rates;
- undocumented/private Rick implementation assumptions;
- feature weights before prospective evidence.

## Data integrity contract

Before market conclusions:

```text
exact CA
-> chain
-> active/canonical pool
-> quote asset
-> live DEX price
-> supply
-> MC/FDV with explicit semantics
-> liquidity
-> timestamp + source
```

Rules:
- missing != zero;
- MC != FDV unless explicitly equal by verified supply semantics;
- never silently substitute FDV for missing MC;
- material source disagreement => DATA_CONFLICT;
- stale/suspected cached measurements cannot enter scored evidence;
- screenshots/live pool data can outrank stale indexed web material when timestamped and exact-CA matched.

## Required regression gates for implementation

- UNKNOWN cannot serialize/normalize to zero;
- missing MC cannot silently receive FDV;
- stale-cache condition quarantines affected measurement;
- first-seen visibility fields are immutable after outcome;
- caller evaluation cannot use ATH-only success;
- public concentration cannot be promoted as coordination proof;
- implementation does not create a second scanner/scorer/ledger owner;
- PVP remains shadow-only until prospective evidence gate is satisfied.

## Build order

```text
P0 verify/repair birth-tape rows
P1 immutable Public Visibility Snapshot
P2 Visibility Gap + deterministic Deep-Dive escalation
P3 caller/source first-seen attribution into existing outcome machinery
P4 shadow PVP/analog research after sufficient prospective rows
```

## Acceptance test

The design is successful only if Alpha Lab becomes faster at falsification AND accumulates better point-in-time evidence without increasing architectural duplication. Feature count is not a success metric.

The highest-leverage immediate step is **real prospective rows flowing reliably**. Rick-parity presentation is secondary; empirical learning is primary.
