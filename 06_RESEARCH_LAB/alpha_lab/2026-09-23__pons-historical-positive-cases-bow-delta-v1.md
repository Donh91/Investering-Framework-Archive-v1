# Pons historical positive cases - BOW + DELTA v1

Date: 2026-09-23
Status: HISTORICAL_RESEARCH_ONLY
Authority: learning/falsification only
Prospective credit: 0
Parent research: Pons V2 launch-origin denominator / Alpha Lab

## Purpose

Preserve two Pons-launched tokens that reached multi-million-dollar market capitalizations as historical positive cases for outcome-blind reconstruction against the full Pons denominator.

These are not BUY calls, prospective wins, thresholds, or proof of Alpha Lab edge.

## Case H-PONS-BOW

Project/token: Longbow / BOW
Chain: Robinhood Chain
CA: 0x451b42A15100C340CA12F7c66DE06fac5EA2D751
Launch relation: identified through Pons launchpad public surface.
Observed later scale: multi-million-dollar market capitalization. Public market data cited during intake showed an ATH price near $0.01257 with 1B supply, implying roughly $12.6M fully diluted/market-cap scale if circulating supply equaled total supply.
Historical low cited during intake: approximately $0.0001431 on 2026-08-18.
Important caveat: the low price is not automatically launch market cap and must not be treated as such without point-in-time supply/market reconstruction.

Research value:
- genuine Pons positive-outcome candidate;
- project/product context rather than pure ticker narrative;
- suitable for T0 and early-threshold reconstruction;
- useful matched-positive against failed Pons launches.

## Case H-PONS-DELTA

Project/token: DELTA
Chain: Robinhood Chain
CA: 0xe8ffd7e24187F72afB08d75B1bb13088A989a791
Launch relation: public market/source material identifies a Pons launch around 2026-07-31.
Observed later scale: a prior historical scan cited during intake recorded approximately $19.1M market capitalization.
Important caveat: this value must be reproduced from timestamped market/on-chain evidence before it is used quantitatively.

Research value:
- second independent multi-million Pons positive case;
- helps prevent overfitting to BOW;
- useful for launch-origin/access-fairness and early-traction reconstruction.

## Required reconstruction

For each case reconstruct only evidence available at each historical checkpoint:
T0 / launch
~$100k MC
~$250k MC
~$500k MC
~$1M MC
first multi-million observation

If a checkpoint cannot be reproduced, mark UNKNOWN. Do not interpolate it into existence.

Capture where available:
- exact launch tx/block/time;
- Pons version/factory;
- creator/deployer/caller;
- launchAndBuy or equivalent initial allocation;
- exemption/privileged launch surface;
- quote asset and initial quote amount;
- supply and MC-vs-FDV semantics;
- liquidity and sellability;
- volume and transaction velocity;
- buyer breadth/concentration;
- holder concentration;
- transfer-vs-buy provenance;
- project existence before token;
- first-party CA publication timing;
- social/caller propagation timing;
- material catalyst timing;
- wallet convergence;
- source health and evidence refs.

## Falsification requirement

Do not ask only what BOW and DELTA shared.

For every candidate feature, query matched failed/ordinary Pons launches from the denominator. A feature is interesting only if it separates outcomes prospectively or improves a preregistered challenger.

Explicitly test whether apparent separation disappears after controlling for:
- launch age;
- Pons-native mechanics;
- liquidity;
- sellability;
- market regime;
- project-first existence;
- broad social propagation;
- privileged/free allocations;
- mechanical or seeded wallet activity.

## Anti-hindsight rules

- Historical winners generate hypotheses only.
- No Alpha Lab credit.
- No thresholds fitted from BOW/DELTA outcomes may enter live routing directly.
- No ATH-only caller/source leaderboard.
- Missing evidence is UNKNOWN, never zero.
- Preserve negative denominator and failed launches.
- Any useful hypothesis must be preregistered and tested on future launches before promotion.

## Initial research question

Could a point-in-time observer have distinguished BOW and DELTA from ordinary/failing Pons launches before $1M market cap using reproducible project, launch-origin, liquidity/sellability, buyer-breadth, provenance, catalyst and independent-demand evidence?

The desired output is not a narrative explanation of why they won. It is a small set of falsifiable challenger features that can be tested prospectively on unseen Pons launches.

## Current verdict

LOGGED_HISTORICAL_POSITIVE_CASES
EDGE_UNPROVEN
NEXT: OUTCOME_BLIND_RECONSTRUCTION + MATCHED_NEGATIVE_COMPARISON
