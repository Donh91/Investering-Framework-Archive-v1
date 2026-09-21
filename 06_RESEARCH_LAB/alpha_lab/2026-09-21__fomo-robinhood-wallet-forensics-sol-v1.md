# FOMO Robinhood Wallet Forensics - Sol High v1

Date: 2026-09-21
Status: EXTERNAL_SNAPSHOT_RESEARCH / SHADOW_ONLY
Owner: #1087 / #1134
Authority: no trade, no copy-trade, no cohort mutation, no model-weight change

## Scope

Adversarially test whether the frozen eight-wallet cohort contains one coherent 'smart wallet' signal. It does not. Public FOMO Robinhood Radar snapshots show materially different behavioral archetypes, outcome visibility and holding periods. This packet is current external evidence and does not rewrite the frozen cohort.

## Source caveat

FOMO Radar is an external derived analytics source. Its trader scores, PnL estimates and labels are not canonical truth. The site itself notes incomplete tape windows and distinguishes held/unsized positions where entry predates observation. Use it for hypothesis generation and current forensic context, not as ground truth for prospective promotion.

## Cohort findings with directly surfaced public evidence

### unipcs
Frozen CA: `0x0a6ebed0155edb4b21d92ad02897a626cd90119e`
External snapshot: score 96 / follow, sniper-holder archetype.
Reported: 107 early entries across 269 tokens; large open bases in multiple names; 7/9 exited positions profitable; same-name overlap includes insentos.
Interpretation: strongest candidate for an information/conviction sensor, but large 'held' rows may predate the public tape. Do not convert reported PnL into framework edge.

### The__Solstice
Frozen CA: `0xd1c77a04b87393e98a1220532e72e8f7d0a31c5a`
External snapshot: score 89 / follow, holder-swing.
Reported: concentrated 30d gains driven heavily by STONK, plus Basecat/STONKEX; 3/7 sold positions profitable; median hold around 19h in source narrative.
Interpretation: potential slower conviction/holding archetype, not equivalent to early-launch sniper.

### himgajria
Frozen CA: `0xd4cf04bc9d7c80b49c6c30a633f7b9bd5370b4d6`
External snapshot: score 81 / follow, holder-swing.
Reported: 106 own buys, larger median sizing, current book contains both large winners and substantial losers; source reports 0/5 fully exited positions profitable while also reporting positive realised aggregate, illustrating why simple win-rate/PnL labels can conflict.
Interpretation: useful as size/conviction context only after full outcome semantics are reproduced.

### remusofmars
Frozen CA: `0x8ab8c0843d9738885d6273dfe3de86c56eea364c`
External snapshot: score 45, scalper.
Reported: 473 fills across 195 tokens, ~40m median hold, 25 early entries; 78/142 sold positions profitable; broad losing open tail.
Interpretation: high discovery coverage but likely high false-positive burden. Potential recall sensor, poor candidate for standalone conviction.

### insentos
Frozen CA: `0x93c006f2051cb72168cf8c27cafe0fb2d71682c8`
External snapshot: score 45/watch, sniper-scalper.
Reported: 23 early entries, ~5m median hold across 77 tokens; 29/48 exited positions profitable; overlaps heavily with unipcs and other tracked traders.
Interpretation: timing sensor candidate, not conviction sensor. Independence must be proven per event because shared-name overlap is high.

### DumbCrayonEater
Frozen CA: `0x8f62a08537cede87d511aca6436274ab4ca080a3`
External leaderboard snapshot: score 84/follow, sniper-holder.
Reported: 20 of 77 own buys inside ten minutes of launch and ~30h holding; large reported outcome driven partly by AI.
Interpretation: promising early+hold archetype, but the headline is outcome-selected and cannot promote the wallet retrospectively.

### PoorGoat_
Frozen CA: `0x9ce0cb4a193acbce0dca3283972341aed6f3f614`
Current public forensic detail was not surfaced in this pass. Preserve UNKNOWN.

### fibs / owner screenshot alias flbs
Frozen CA: `0x80f3b0b712a82172a67e454e313ba6e2b0e7ae64`
Alias remains unresolved in canonical cohort. Public overlap surfaces use `fibs` but that does not resolve owner-screenshot identity by itself. Preserve identity ambiguity and do not use as independent convergence until resolved.

## Main forensic result

The frozen cohort is heterogeneous. A single wallet score or one convergence rule discards useful structure.

Candidate archetypes for **measurement only**:
- EARLY_DISCOVERY: fast/early launch coverage, potentially high FP - remusofmars, insentos.
- EARLY_PLUS_HOLD: early entries plus materially longer holding - DumbCrayonEater.
- CONVICTION_HOLDER: larger sizing/longer book behavior - unipcs, The__Solstice, himgajria.
- UNKNOWN/IDENTITY_PENDING: PoorGoat_, fibs/flbs until evidence improves.

These labels are not cohort changes and not weights.

## Critical independence problem

Public same-name overlap is substantial:
- unipcs and insentos share many names;
- unipcs overlaps with multiple high-ranked traders;
- The__Solstice overlaps with unipcs/ogle/frankdegods;
- himgajria overlaps with unipcs/frankdegods/AvgJoesCrypto.

Therefore `two cohort wallets bought token X` cannot establish two independent information sources.

Per-event independence must consider:
1. distinct economic entity;
2. self-initiated receipt provenance;
3. funding/control relationship if observable;
4. temporal spacing and ordering;
5. whether buys are responses to the same public catalyst/caller;
6. whether one wallet received/transferred rather than independently bought;
7. repeated co-trading baseline between the pair.

A pair that co-trades constantly should contribute less evidence than a rare cross-archetype convergence, but no numeric discount is authorized until prospective data exists.

## Better prospective challenger hypothesis

Replace the informal idea 'smart wallets converge' with:

> Does **independently reproduced, self-initiated cross-archetype convergence** add early discovery information beyond the existing champion and beyond each wallet archetype alone?

Primary comparison should preserve:
A. champion only;
B. any two verified independent cohort entities;
C. cross-archetype verified independent convergence.

This is a research challenger concept only. Do not change the frozen #1134 experiment until governance explicitly preregisters a new child comparison.

## Negative-control requirement

Prospective wallet learning must retain:
- all cohort buys that fail provenance;
- all eligible self-initiated buys that never converge;
- convergences into unsellable/illiquid tokens;
- convergences that occur after champion/public discovery;
- high-score wallet entries that lose;
- gift/dust/seeded recipient events;
- pairs with chronic co-trading.

Without these, wallet intelligence will be winner-selected.

## Immediate implications

1. Keep the original eight-wallet cohort immutable.
2. Do not promote/drop members from current FOMO Radar scores.
3. Add archetype as a shadow descriptive field only after source-backed reproduction.
4. Make event-level independence, not wallet reputation, the core gate.
5. Compare cross-archetype convergence against same-archetype convergence prospectively.
6. Keep PoorGoat_ UNKNOWN and fibs/flbs identity-pending.
7. Treat external trader scores and PnL as research evidence, not labels.

## Conclusion

Wallet data remains potentially valuable, but not as 'copy the smart wallet'. The plausible edge is earlier information from rare, independently reproduced convergence across behaviorally different entities. This is narrower, more falsifiable and less vulnerable to one-hit-winner and correlated-crowd bias.
