# Alpha Lab — Adversarial CA Intake + On-Demand Launch Scan v1

Date: 2026-10-01
Status: ACTIVE_OPERATIONAL_ADDENDUM
Parent owners:
- `2026-09-16__alpha-lab-tokens-moonshots-standing-mandate-v1__policy.md`
- `meme-alpha-supervisor`
- `OPERATOR_RISK_ADVERSARIAL_ALPHA_SHADOW_CONTRACT_v1`
- existing Moonshot / Project->CA / lifecycle owners

Authority:
- research / warning / review: YES
- automatic trading: NO
- automatic buy/sell: NO
- new scanner owner: NO

## Purpose

Operationalize Adversarial Operator Anticipation in two user-facing modes:

1. **CA INTAKE ADVERSARIAL OVERLAY**
   Whenever the owner supplies an exact token CA/mint for Alpha Lab analysis, test whether the token is part of a known or newly emerging cabal/operator/extraction setup even if the owner did not ask about that risk explicitly.

2. **ON-DEMAND ADVERSARIAL LAUNCH SCAN**
   When the owner asks to scan new launches, upcoming launches, likely insider/cabal/pump schemes, or similar, use the existing discovery owners to surface the highest-value suspicious cases for review.

This addendum does not authorize execution or front-running.

## Mode A — CA intake adversarial overlay

### Trigger

Apply automatically when the owner supplies:
- an exact CA/mint;
- a DEX/pool link that resolves to an exact token;
- a named fresh token where exact identity can be resolved;
- a launch screenshot containing an exact CA.

The overlay is part of the normal token audit and should not require the owner to say "check cabal".

### Required order

`EXACT_IDENTITY`
-> `LIVE_MARKET/SELLABILITY`
-> `LAUNCH_ORIGIN`
-> `OPERATOR_LINEAGE`
-> `PREPOSITIONING/COHORT`
-> `PRIVILEGED_SURFACE`
-> `DISTRIBUTION_STATE`
-> `BENIGN_INFRA_EXCLUSION`
-> `WARNING / REVIEW STATE`

Where source capability permits, inspect:

- deployer / launch caller;
- funding ancestry;
- wallet age / activation timing;
- same-quote preparation;
- unusually similar residual balances;
- approvals / relaunch / retry family;
- snipe-tax exemptions / privileged lists;
- bundle / early-beneficial-inventory concentration;
- recurring wallet/entity cohort;
- known prior proceeds -> future launch funding;
- collector/proceeds convergence;
- creator-fee destination;
- coordinated sell-through;
- descendant inventory after transfers;
- known operator seed registry matches;
- Relay/router/bridge/CEX/factory false-positive paths.

### Warning states

Use evidence states, not moral labels:

`ADVERSARIAL_PATTERN = UNKNOWN | NO_MATERIAL_MATCH | WATCH | STRONG_MATCH | DIRECT_LINEAGE`

A prominent warning is required when state is `STRONG_MATCH` or `DIRECT_LINEAGE`.

Recommended user-facing form:

`⚠️ ADVERSARIAL / CABAL PATTERN WARNING`

Then state:
- what exact behavior matched;
- whether the evidence is direct or inferential;
- what benign infrastructure was excluded;
- whether extraction risk is elevated;
- whether sellability still exists;
- whether any short public expansion window is only a SHADOW research hypothesis.

Do NOT write "insider", "scam", "rug" or "same operator" as fact unless the evidence supports that exact claim.

### Dual-axis output

Always keep separate:

`OPERATOR / EXTRACTION RISK`

from:

`REALIZABLE PUBLIC ALPHA WINDOW`

A strong operator match may coexist with short-term price expansion.

It must never silently become a bullish score.

## Mode B — on-demand adversarial launch scan

### Trigger phrases

Examples include:
- "scan nye launches";
- "hvad launcher snart";
- "find insider/cabal launches";
- "pump schemes";
- "hvilke nye tokens ligner BYTE";
- "find næste serial-extractor launch";
- equivalent natural-language requests.

### Search universe

Reuse existing owners and current live sources.

Prioritize:
- Robinhood/Pons launch and prelaunch surfaces;
- project-first upcoming launches;
- exact-CA launch feeds;
- fresh token/pool feeds where origin can be resolved;
- known operator-lineage seeds;
- fresh-wallet/prepositioning activity;
- user/Claude/Wazz/Bando-derived research seeds only as leads;
- Solana/Pump.fun creator/deployer cases where current owners support them.

Do not create a new scanner merely for this request.

### Scan result classes

Return a small shortlist, normally 0-5 cases:

`DIRECT_OPERATOR_LINEAGE`
- direct prior-proceeds -> new launch funding or same non-infrastructure operator evidence.

`COORDINATED_PRELAUNCH_WAKEUP`
- fresh/dormant cohort, funding/quote prep/residual/approval pattern before broad propagation.

`PRIVILEGED_LAUNCH_SURFACE`
- exemptions, bundled inventory, linked early cohort or other privileged launch mechanics.

`SERIAL_DEPLOYER / CREATOR WATCH`
- point-in-time deployer evidence, but only when denominator and current semantics are known.

`FALSE_POSITIVE_INFRA`
- suspicious-looking pattern explained by Relay/router/bridge/CEX/protocol infrastructure.

`NO_QUALIFIED_CASE`
- no current case clears the evidence threshold.

### Per-case output

For each surfaced case state:

- exact CA/mint if known;
- launch/upcoming state;
- why it was surfaced;
- evidence available **before** broad propagation;
- operator/extraction-risk state;
- independent-demand state;
- liquidity/sellability state;
- likely first-distribution risk;
- key falsifier;
- whether the case is merely avoidance-risk or also a `SHADOW_WINDOW_CANDIDATE`.

Never rank "most likely scam" from social labels alone.

## Interaction behavior

When the owner shares a CA:
- do the overlay automatically;
- if there is no material match, say so briefly;
- if there is a strong match, put the warning near the top of the answer;
- do not hide the warning because the project/product thesis looks attractive.

When the owner requests an adversarial launch scan:
- search current data fresh;
- return only the best-qualified cases;
- prefer `NO_QUALIFIED_CASE` to filler;
- distinguish upcoming/prelaunch from already-pumped post-T0 cases;
- preserve all surfaced cases for outcome learning where material.

## Relationship to the adversarial first-pump research goal

This operational addendum may surface a token with:
- elevated extraction risk;
- plus a possible short, public, sellable expansion window.

Until prospective evidence matures, the correct state is:

`TIME_SENSITIVE_REVIEW_NOW`

or

`SHADOW_WINDOW_CANDIDATE`.

Not:
`ENTRY CANDIDATE` solely because an extractive operator may pump it.

Any future promotion of an adversarial-alpha window must pass the existing prospective matched-control and sellability gates.

## No duplication

Implementation must reuse:
- existing Moonshot/Pons discovery;
- Project->CA memory;
- Blockscout exact-CA enrichment;
- wallet/entity memory;
- operator-risk shadow contract;
- prospective evidence/outcome owners;
- existing adversarial runtime wiring.

No new scheduler, queue, scanner, score, ledger or trading engine.

## Success condition

This addendum is working correctly when:

1. a user-supplied CA with meaningful operator/cabal evidence produces a clear evidence-backed warning without requiring a special prompt;
2. a user request to scan new/upcoming suspicious launches returns a bounded shortlist or an honest no-hit;
3. Relay/router/bridge/shared-factory false positives are suppressed;
4. exact-wallet rotation does not defeat operator-pattern memory;
5. risk and tradeable-window research remain separate;
6. every material hit becomes prospective learning rather than disappearing after chat.
