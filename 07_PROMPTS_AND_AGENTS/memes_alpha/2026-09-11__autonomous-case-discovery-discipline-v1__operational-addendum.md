# Memes v3 — Autonomous Case Discovery Discipline v1

**Date:** 2026-09-11  
**Status:** `OPERATIONAL_OWNER_APPROVED_RESEARCH_ADDENDUM`  
**Authority:** `RESEARCH_ONLY / SHADOW_ONLY`  
**Parent owner:** `2026-09-09__memes-v3-autonomous-alpha-research-workstream-v1__operational.md`  
**Method owner:** `2026-09-11__memes-v3-empirical-hardening-adjudication-v1__research-addendum.md`  
**Launch-replay owner:** `2026-09-11__flybrain-launch-replay-case-v1__research-addendum.md`

## Purpose

Make external case discovery a first-class Alpha Lab research discipline so the framework does not depend on the owner manually supplying every interesting meme, launch, wallet, narrative or public build artifact.

This addendum does **not** create a new engine, scanner, scheduler, signal path or portfolio authority. It defines how the existing Memes v3 / Alpha Lab research workstream should discover, verify, freeze, replay and compare unusual historical and prospective cases.

The standing objective is:

> Find cases early enough, or reconstruct them faithfully enough, to learn what information was genuinely available before the outcome was known.

The goal is not to collect famous winners. The goal is to build matched families of winners, failures, copycats, false positives and ambiguous cases that make Alpha Lab harder to fool.

## Core discovery families

Discovery should deliberately search beyond ordinary token scanners. High-value families include:

- real-world event or scientific novelty -> token embodiment;
- public software / GitHub artifact -> launch;
- AI-agent or autonomous-system participation -> token creation or propagation;
- biological / neural / robotics / hardware experiments -> token narrative;
- phrase capture / meme birth -> first exact token instances;
- one narrative -> multiple chains / venues / contracts;
- unusual quote-asset pairings and semantic pairing;
- public wallet / KOL disclosure -> post-disclosure behavior;
- creator-economic-loop launches where activity itself funds the creator/project;
- launchpad-native mechanics that alter early execution materially;
- public build logs, commits, websites, demos or scientific releases that predate token launch;
- tokens that looked exceptionally strong at T0 but failed;
- tokens that looked weak or absurd at T0 but survived and compounded.

FLYBRAIN is an anchor case, not a template to overfit.

## Lead lifecycle

Every externally discovered case must move through explicit states:

`DISCOVERED_UNVERIFIED`
→ `IDENTITY_VERIFIED`
→ `SOURCE_PROVENANCE_VERIFIED`
→ `REPLAY_CANDIDATE`
→ `MATCHED_FAMILY_BOUND`
→ `OUTCOME_BOUND`
→ `ADJUDICATED`

A lead may stop or be rejected at any state.

A case is not allowed to jump directly from an interesting article, X post, Telegram message, GitHub repo or dashboard to `QUALIFIED_ALPHA`.

## Discovery is not validation

Search and discovery systems are allowed to be high-recall and noisy.

Validation must remain conservative.

For every lead, the research packet should attempt to resolve, when applicable:

- exact chain + CA/mint;
- exact launch transaction / block / timestamp;
- venue and launch mechanics;
- creator / deployer / launcher identities and economic entities;
- supply, quote asset, tax / fee / graduation rules;
- earliest reproducible market state;
- earliest reproducible public artifact state;
- `public_at`, `observed_at`, `available_at`, `computed_at` separately;
- source class and source independence;
- executable rather than chart-only entry state;
- matched failures and same-narrative siblings;
- first-distribution and longer outcome checkpoints.

If exact identity or chronology cannot be resolved, the case remains a lead rather than evidence.

## Hindsight firewall

Discovery may happen after an outcome is known, but replay features must be frozen from evidence that can be shown to have existed at the relevant timestamp.

Never use later success to upgrade an earlier feature.

Examples:

- later GitHub commits do not prove earlier public artifact availability;
- later KOL mentions do not become T0 propagation;
- later wallet PnL cannot change an as-of wallet score;
- later ATH cannot become an executable early return;
- a successful token's current website cannot substitute for what the site exposed at launch.

When historical availability cannot be proven, mark the field `NOT_PROVEN_AS_OF` rather than infer it.

## Mandatory matched-family construction

The unit of learning is not the famous winner. It is the **family**.

For a high-priority winner, search for:

- same narrative, failed token;
- same chain / venue / launch period;
- similar liquidity / size / age;
- similar degree of public artifact evidence;
- similar agentic / scientific / creator story;
- copycats created after the narrative became visible;
- cases with strong public evidence but no capital acceleration;
- cases with strong capital acceleration but weak narrative provenance.

The system should actively prefer a useful failure over a tenth retrospective winner.

## Candidate research dimensions

External discovery may propose new Shadow features, but must not promote them automatically.

Examples now worth testing include:

- `PRE_LAUNCH_ARTIFACT_PROVENANCE`
- `ARTIFACT_TO_TOKEN_LEAD_TIME`
- `ARTIFACT_EXECUTABILITY`
- `SHIPPING_VELOCITY`
- `NARRATIVE_TRUTH_DENSITY`
- `AGENCY_DECOMPOSITION`
- `NARRATIVE_EMBODIMENT_SPEED`
- `SEMANTIC_QUOTE_ASSET_FIT`
- `CREATOR_ECONOMIC_LOOP_INTENSITY`
- `OPEN_SOURCE_FORKABILITY`
- `COPYCAT_DILUTION_PRESSURE`
- `SCANNER_LEAD_TIME`
- `PUBLIC_VISIBILITY_EVENT_GRAPH`
- `SIGNAL_CAPACITY_PRESSURE`
- `FIRST_DISTRIBUTION_SURVIVAL`

These are hypotheses / measurement candidates, not production factors.

## External-source hierarchy

Prefer, in order where available:

1. chain-native evidence and exact transactions;
2. original project / developer repositories and immutable releases;
3. protocol / launchpad documentation;
4. primary scientific / institutional sources;
5. original project website / social post with reproducible timestamp;
6. independent scanners / explorers / analytics providers;
7. reputable reporting;
8. secondary social commentary / aggregators.

Secondary sources can discover a case. They do not silently become the load-bearing truth source.

## Initial family leads

The first owner-approved discovery family is seeded around FLYBRAIN.

Initial leads include:

- FLYBRAIN — anchor / verified replay case;
- neuron / CL1 — biological-compute token lead;
- CLORD-1 — biological-compute / multi-system research lead;
- Anima — public artifact / living-neuron agent lead;
- LUM / Luminous — AI-agent-to-agent deployment lead;
- GRIFFAIN — autonomous-agent / spontaneous launch lead;
- GOAT / Truth Terminal — narrative-origin vs token-deployment agency control;
- BIOHACKING — semantic quote-asset / tokenized-equity pairing lead.

Except FLYBRAIN, these names are **discovery leads only** until their identity, chronology, source provenance and relevant early-state evidence are independently reconstructed. Their inclusion here must never be read as factual validation of prior social/media claims.

## Continuous-discovery behavior

Once the existing Memes v3 collector and launch-replay foundations are implemented, the research system may continuously surface cases from approved public sources and existing discovery feeds.

Expected behavior:

- discover broadly;
- deduplicate aggressively;
- verify exact identity before expensive work;
- preserve source provenance;
- prefer primary evidence;
- estimate value-of-information before deep research;
- escalate only cases that add new evidence, a useful matched control, or a genuinely new mechanism;
- archive rejected leads with reason codes so they can later serve as negatives.

Do not produce user alerts merely because a lead was found. Human-facing alerts should remain reserved for high information value under the existing Alpha Lab rules.

## Astra-era use

Astra should later audit this discovery discipline for both underreach and overreach.

High-value Astra tasks include:

- finding overlooked matched failures;
- constructing adversarial case families;
- source-conflict adjudication;
- causal / mechanism synthesis across chain, artifact, narrative and capital flow;
- blind bull vs kill-pass comparison on frozen evidence;
- asking whether an apparently unique feature survives out-of-sample family comparison;
- discovering new useful case taxonomies not anticipated here.

The present case families are waypoints, not limits. Astra may expand or replace this taxonomy if prospective evidence supports doing so.

## Hard boundaries

This discipline must not:

- emit automatic BUY / SELL / size;
- create a public wallet watchlist;
- promote a lead because it later pumped;
- treat GitHub activity, KOL following, raw holders, raw volume or vendor labels as standalone alpha;
- scrape authenticated/proprietary services in violation of terms;
- create a new independent scheduler when the existing research cadence can own the work;
- change API budget without owner authorization;
- automatically merge code or research promotions;
- rewrite historical snapshots.

## Success condition

The discipline is working when Alpha Lab increasingly answers:

> “What could we actually have known then, what similar cases failed, what was executable, and which features still discriminated before the outcome?”

rather than:

> “Why did this famous winner go up?”
