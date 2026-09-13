# Memes v3 — FLYBRAIN Launch Replay Case v1

**Date:** 2026-09-11  
**Status:** `HIGH_PRIORITY_RESEARCH_CASE`  
**Authority:** `RESEARCH_ONLY / SHADOW_ONLY`  
**Provenance:** `USER_SUPPLIED_CASE + EXTERNAL_PRIMARY/SECONDARY VERIFICATION`  
**Parent owner:** `2026-09-09__memes-v3-autonomous-alpha-research-workstream-v1__operational.md`  
**Method owner:** `2026-09-11__memes-v3-empirical-hardening-adjudication-v1__research-addendum.md`

## Why this case matters

FLYBRAIN is not useful because it later became a famous winner. It is useful because unusually rich evidence existed **before and within minutes of launch**, allowing a serious replay of what Alpha Lab could have known without hindsight.

The case links four research layers:

1. pre-launch public artifact provenance;
2. exact chain-native launch mechanics;
3. very early third-party scanner state;
4. later social amplification, extreme expansion and first distribution.

The objective is to reconstruct information availability, execution and failure risk at each state, not to explain the winner retrospectively.

## Exact identity

- chain: Robinhood Chain
- chain id: `4663`
- token: `flybrain / FLYBRAIN`
- exact CA: `0x4eb990547bce4a982432ca88cf5fae7eed1a2d35`
- launch tx: `0x63b2164f3d784e46538cc81d3c48095bd7252a3d12398fdad9991870d12a4f1c`
- launch block: `59614342`
- launch timestamp from project code: `2026-09-10T18:23:09Z`
- creator: `0x6ce4085EfB52a6eBDb7d6989beb8860847f4b42A`
- supply: `1,000,000,000`
- pairing asset: `GOOGL`
- creator tax: `1.0%`

Primary implementation source: `https://github.com/fruitflydev/flycoinrh`

The exact identity above is externally inspectable and must be kept separate from same-name/copycat tokens.

## Scientific provenance — corrected framing

The underlying scientific event is real. The published MaleCNS resource describes the full male *Drosophila melanogaster* central nervous system with about 166.7k annotated neurons and a substantially larger raw connectome than the graph used by this project.

The Flybrain implementation reports a **processed simulation graph** of `165,122` neurons and `10,228,000` signed edges. Do not describe 10.228M as the total number of synaptic connections in the complete scientific MaleCNS dataset. It is the project's processed simulation representation.

This distinction matters because `NARRATIVE_TRUTH_DENSITY` must reward verifiable originality without rewarding simplified or exaggerated retellings.

## Agency decomposition — do not use binary “autonomous launch” language

The project itself explicitly discloses that the simulated fly did not independently complete every launch action.

Observed/project-documented division:

- the fly's connectome-driven visual/motor loop participates in navigation and form interaction;
- it reliably contributes the description, often the ticker and rarely the name;
- a script completes missing fields;
- the rig selects the pairing asset and creator tax;
- transaction signing/broadcast uses the surrounding wallet/runtime infrastructure.

Therefore the research label is:

`BIOLOGICAL_CONNECTOME_PARTICIPATED_IN_LAUNCH_WITH_HUMAN_SCRIPTED_RAILS`

not:

`FULLY_AUTONOMOUS_BRAIN_CREATED_ITS_OWN_TOKEN`.

This motivates an `AGENCY_FRACTION` / `AGENCY_DECOMPOSITION` feature for future AI/agent meme cases.

## Pre-launch artifact provenance — unusually important finding

GitHub repository metadata records `fruitflydev/flycoinrh` as created at `2026-09-10T17:32:56Z`, around 50 minutes before the recorded FLYBRAIN launch.

The repository's pre-launch history also contains launch-specific work before the token transaction, including:

- connectome-driven Pons launch rig;
- on-chain launch-flow completion;
- custom GOOGL pair selection and creator-tax configuration;
- receipt/token-page handling;
- X-handle and dark-mode handling.

Commit author/committer timestamps are useful provenance but must **not** automatically be treated as public availability timestamps. Repository creation/publication time, push visibility and artifact availability must remain separate fields.

### Research hypothesis: Pre-Launch Artifact Provenance

A public, executable artifact linked to an upcoming launch may be a higher-quality pre-token signal than social hype created after a token exists.

Candidate fields:

- `artifact_first_public_at`
- `launch_specific_code_visible_at`
- `artifact_to_launch_lead_seconds`
- `repo_age_at_launch`
- `shipping_velocity_pre_launch`
- `runnable_artifact_present`
- `chain_constants_present`
- `exact_launch_venue_present`
- `planned_pair_asset_present`
- `planned_creator_economics_present`
- `artifact_identity_link_strength`

This remains a hypothesis until tested against failed and non-launching repositories. GitHub activity alone must never become a positive signal.

## Chain-native execution mechanics

FLYBRAIN launched through Pons v2 and was paired against GOOGL. Pons v2 semantics materially change any replay.

### Curve -> pool state

A Pons v2 token begins on a bonding curve. At graduation it moves into a Uniswap v4 pool with permanently locked liquidity. Pre-graduation and post-graduation execution must therefore be represented as different venue states.

### Opening snipe tax

Current Pons v2 documentation states an opening buy tax starting at 99% and decaying exponentially to zero across the first five seconds, approximately 25% at one second and ~3% at two seconds. The launch carries its own copied terms.

Therefore a naive recorder that reports only raw T+1s/T+2s prices can manufacture fictitious alpha. A correct replay must preserve both:

- raw curve state;
- **executable quote after the recipient-specific opening tax, normal fee, creator tax, impact and latency**.

T+1/T+2/T+5 snapshots remain useful for market-structure research, but the first-second chart price is not an assumed achievable entry.

### Creator/team exemptions

Pons documents that the launcher and creator-fee recipient are automatically exempt from the opening snipe tax and that additional exemption addresses may be fixed at creation.

This creates a mandatory forensic question for every launch:

`OPENING_TAX_EXEMPT_ENTITY_SET`

A fair early-wallet comparison must distinguish exempt creator/team activity from ordinary public buyers.

### Custom quote asset

Because FLYBRAIN is priced in GOOGL, USD return must be decomposed into:

`FLYBRAIN/GOOGL relative return × GOOGL/USD return`

The existing `Quote Asset Beta Decomposition` hypothesis is therefore directly testable here. USD market-cap charts alone can confound meme alpha with movement in the tokenised equity used as quote asset.

## Earliest externally observed market state

A third-party GemTools alert preserved a public snapshot at token age approximately six minutes:

- MC: `$95.5K`
- holders: `245`
- raw Top10: `29%`
- DEV: `0%`
- Snipers: `0%`
- Bundled: `14%`
- Insiders: `0%`

The same alert stream later tracked the token from that frozen `$95.5K` reference to multiple higher milestones, including 2x within roughly 14 minutes and much larger expansions later.

These scanner labels are **external vendor features**, not deterministic truth. `Snipers 0%`, `Insiders 0%` and `Bundled 14%` must be reproduced or contradicted from chain evidence before they can become Alpha Lab features.

The key research value is the T0 packet itself: a ~6-minute state existed before the later massive social/capital expansion.

## Social propagation chronology

Later reports state that Marc Andreessen followed the project account around a period when FLYBRAIN was already trading at multi-million market cap, followed by a sharp one-hour expansion.

No verified endorsement or purchase is established.

Research classification:

`PUBLIC_VISIBILITY_EVENT / KOL_ECHO_OR_ACCELERATOR`

not:

`KOL_ORIGIN` or `KOL_ENDORSEMENT`.

This case should test whether the narrative was already independently accelerating before the high-profile follow and how much incremental flow appeared after visibility changed.

## Creator-fee reflexivity

The developer publicly claimed approximately `$106K` in creator rewards in about 6.5 hours.

Treat this as `EXTERNAL_CREATOR_CLAIM_PENDING_REPRODUCTION` until reconstructed from Pons fee events/escrow state and contemporaneous GOOGL/USD conversion.

The mechanism itself is real and research-relevant: a GOOGL-paired Pons launch pays creator fees in the quote asset. This can create an endogenous loop:

`TRADING ACTIVITY -> CREATOR QUOTE-ASSET FEES -> FUNDING FOR CONTINUED EXPERIMENT/CONTENT/TRADING -> NEW PUBLIC EVENTS -> ATTENTION -> TRADING ACTIVITY`

Call the candidate feature family `CREATOR_ECONOMIC_LOOP_INTENSITY`.

Do not assume it is price-supportive. It can also incentivise continued attention extraction without durable token value.

## Current distribution state

The owner-supplied 2026-09-11 screenshot shows a violent post-expansion retrace on the 1h chart, with current displayed price `0.01091` and repeated lower highs/lower lows after the initial vertical move.

Store this only as `USER_SUPPLIED_POST_EXPANSION_SNAPSHOT`. Do not infer exact USD market cap or exact all-time high from the chart because the displayed market is paired with GOOGL and external aggregators disagree materially during this fast-moving period.

This creates a live `FIRST_DISTRIBUTION_SURVIVAL` case:

- does real user/holder activity survive the first large unwind?
- does developer shipping continue after price collapse?
- do independent buyers replace launch-phase buyers?
- does public visibility stay high after the reflexive peak?
- does executable liquidity remain adequate?
- do derivative/copycat instances drain the original?

## New/strengthened Alpha Lab feature families

1. `PRE_LAUNCH_ARTIFACT_PROVENANCE`
2. `ARTIFACT_TO_TOKEN_LEAD_TIME`
3. `ARTIFACT_EXECUTABILITY`
4. `SHIPPING_VELOCITY_PRE_POST_LAUNCH`
5. `NARRATIVE_PREEXISTENCE_GAP`
6. `NARRATIVE_TRUTH_DENSITY`
7. `AGENCY_DECOMPOSITION`
8. `CHAIN_NATIVE_LAUNCH_MECHANICS`
9. `OPENING_TAX_EXEMPT_ENTITY_SET`
10. `QUOTE_ASSET_BETA_DECOMPOSITION`
11. `SCANNER_LEAD_TIME`
12. `PUBLIC_VISIBILITY_EVENT_GRAPH`
13. `CREATOR_ECONOMIC_LOOP_INTENSITY`
14. `FIRST_DISTRIBUTION_SURVIVAL`
15. `OPEN_SOURCE_FORKABILITY / COPYCAT_DILUTION`

All remain research/shadow features until prospective discrimination is demonstrated.

## The counterfactual we actually care about

Do **not** ask:

> Why did FLYBRAIN reach tens of millions?

Ask:

> At each point from pre-launch public artifact -> launch -> ~6-minute scanner snapshot -> early expansion -> later KOL visibility, what evidence was genuinely available, what entry was executable, and what unresolved risks remained?

The high-value replay windows are therefore:

- `PRE_TOKEN_PUBLIC_ARTIFACT`
- `LAUNCH_BLOCK`
- `T+1s / T+2s / T+5s / T+10s / T+30s / T+60s`
- `T+5m / first external scanner availability`
- `FIRST_GRADUATION_STATE`
- `FIRST_2X / 5X / 10X`
- `PRE_KOL_VISIBILITY`
- `POST_KOL_VISIBILITY`
- `FIRST_MAJOR_DISTRIBUTION`
- `POST_DISTRIBUTION_SURVIVAL`

Every window must preserve `observed_at`, `available_at`, `computed_at`, source provenance and whether an entry/exit was actually executable.

## Matched failures required

FLYBRAIN by itself cannot validate any feature.

Build controls from:

- Pons launches with public repos/artifacts that failed;
- Pons launches with strong narratives but no artifact;
- Pons launches with similar early holder/volume/liquidity state that died;
- copycat/derivative fruit-fly tokens;
- public agent experiments that never produced durable token demand;
- launches with creator-fee loops but poor post-distribution survival.

A feature is interesting only if it discriminates before outcome.

## Research verdict

`A_CASE_STUDY / HIGH_PRIORITY_REPLAY / NOT_A_RETROSPECTIVE_BUY_SIGNAL`

FLYBRAIN is one of the strongest current Alpha Lab cases because it gives the framework a rare chance to connect **pre-launch artifacts, exact venue mechanics, early scanner state, narrative originality, social amplification and violent distribution** in one reproducible timeline.

The most important new opportunity is not “find the next fly”. It is to test whether **public artifact provenance plus chain-native executable early confirmation** identifies unusually high-quality meme instances before mass visibility, and whether that survives matched failures.