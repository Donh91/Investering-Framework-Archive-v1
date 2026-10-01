# Adversarial Operator Research — Claude adjudication + Bitquery cross-check v1

Date: 2026-10-01
Status: SHADOW_RESEARCH / CONTINUE_SHADOW
Owner: #1087
Authority: RESEARCH_ONLY
Automatic trading: NO
New scanner: NO

## Inputs

Claude Bridge:
- `AUDIT-20261001-064500Z-CLAUDE-ADVERSARIAL-ALPHA-WINDOW`
- ChatGPT adjudication:
  `REVIEW-20261001-071500Z-CLAUDE-ADVERSARIAL-ALPHA-WINDOW`

Canonical Alpha inputs:
- `2026-09-30__byte-post-exit-relay-falsifier-prelaunch-wakeup-v1.md`
- `2026-09-27__wazz-robinhood-serial-extraction-operator-fingerprint-audit-v1.md`
- `OPERATOR_RISK_ADVERSARIAL_ALPHA_SHADOW_CONTRACT_v1.json`
- `2026-10-01__alpha-meme-lab-goals-and-dreams-v1-1__vision-addendum.md`
- `2026-10-01__adversarial-ca-intake-and-on-demand-launch-scan-v1__operational-addendum.md`

Independent external cross-check:
- Bitquery investigation:
  `https://bitquery.io/investigations/robinhood-chain-rug-pull-crew`
  published/verified 2026-09-28.

## Accepted Claude findings

### 1. Launch denominator is very large

Claude reproduced:
- 2,912 Pons launch events in ~3.5h on 2026-09-08, ~830/h;
- a late-September observed rate around ~260/h;
- order-of-magnitude launch flow in the thousands/day.

Interpretation:
a generic 99%-specific classifier can still create an unusably large daily review queue.

Therefore operator detection must be highly selective.

### 2. Relaunch/retry is weak by itself

In Claude's measured window:
- 34.8% of launches came from deployers with >=2 launches;
- 17.3% from deployers with >=6;
- 53.8% of consecutive same-deployer gaps were <=5m.

Therefore:
`RELAUNCH_RETRY != OPERATOR_SIGNATURE`

Likewise:
`COMMON_QUOTE_ASSET != OPERATOR_SIGNATURE`

These remain context, not load-bearing evidence.

### 3. Coarse first-pump paths are descriptive only

Claude's coarse 5m Nansen paths showed fast expansion in BYTE/CRUMBS/DRAFT but cannot establish a realizable public trade:
- ex-post selected seeds;
- close-only 5m bars;
- no exact public entry;
- no slippage/gas/MEV;
- no sellability reconstruction;
- no matched controls.

State:
`REALIZABLE_FIRST_PUMP_WINDOW = NOT_PROVEN`.

## Independent Bitquery evidence

Bitquery independently rebuilt the Wazz case from Robinhood Chain archive data and reports:

- 56 launches linked to one crew, July 10 to Sept 23;
- ~$15.5M net take;
- 43/56 directly linked by money flow;
- DEED: a funding path paid 92 fresh wallets around 40m before launch;
- launch transaction exempted 26 wallets from Pons snipe tax;
- 25 of the funded/exempt wallets bought about two-thirds of supply in the next block;
- hand-offs started seconds after launch;
- collectors often funded the next launch;
- half of the coins peaked within ~15m;
- on most launches the crew had completed about half its trading by ~15m;
- median peak-to-later decline ~99%;
- 467 other groups used the same broad Pons playbook.

This materially strengthens:
`REPEAT_EXTRACTIVE_OPERATOR_PATTERN_EXISTS`

but also shows:
`BROAD_PONS_BUNDLE_PATTERN_IS_NOT_SELECTIVE_ENOUGH`.

## Fingerprint hierarchy

### Weak/context-only

Do not qualify on these alone:
- same launchpad;
- same token name/ticker;
- relaunch/retry;
- common quote asset;
- high transaction count;
- many fresh wallets without economic linkage.

### High-information

Prioritize:
- direct proceeds from prior operator launch -> new launch funding key;
- non-benign common funder of fresh prelaunch wallets;
- privileged snipe-tax exemption list matching funded wallets;
- synchronized next-block/bundle inventory acquisition;
- materially similar prelaunch residual balances;
- descendant inventory hand-off followed by coordinated sell-through;
- recurring collector that is not Relay/router/bridge/CEX/protocol infrastructure.

## Counting gate v1

The counting gate is an **operational review-budget test**, not a universal scientific truth.

### Stage 1

Freeze the broad candidate rule before outcomes.

A `PRELAUNCH_COHORT_WAKEUP` candidate requires:

1. exact launch identity / T0;
2. observable pre-T0 wallet preparation within T-60m;
3. benign-infrastructure exclusions applied;
4. at least one of:
   - direct known-operator proceeds -> launch funding lineage; OR
   - non-benign common funding + privileged exemption/bundle evidence; OR
   - non-benign common funding + synchronized beneficial inventory + residual-similarity evidence.

Relaunch/retry and quote asset may support context but cannot satisfy the rule.

Count:
- raw fires/day;
- qualified fires/day after infra exclusion;
- infra-contamination share;
- known adversarial seed overlap;
- ordinary-control overlap.

### Operational gate

If Stage 1 produces:
- <=10 qualified cases/day; and
- <50% raw-fire benign-infra contamination;

then:
`REVIEW_BUDGET_PASS`.

If >10/day:
do not automatically reject the scientific hypothesis.

Freeze Stage 2 before outcome inspection.

### Stage 2

Require either:
- `DIRECT_OPERATOR_LINEAGE`; OR
- privileged exemption/bundle evidence + non-benign common funding + synchronized beneficial inventory.

If Stage 2 still produces >10/day under the intended time-sensitive human review budget:
`AUTONOMOUS_TIME_SENSITIVE_REVIEW = OPERATIONALLY_UNVIABLE`.

If >=50% of Stage-1 raw fires are benign infrastructure:
`INFRA_EXCLUSION_INADEQUATE`
and promotion is blocked until fixed.

## Exact-identity caution

PINK and LEGS have many same-ticker/same-name contracts.

Bitquery anchors:
- PINK final profitable launch: 2026-09-07 21:56 UTC;
- LEGS: 2026-09-03 21:03 UTC.

Do not bind a CA by ticker search alone.

Identity remains UNKNOWN until contract launch timestamp / source list matches.

## Runtime decision

The existing:
`codex-research-alpha-adversarial-runtime-wiring-v1`

is already:
`CODEX_READY`
signature:
`b62105cfe794e5c80c70`.

No duplicate runtime candidate is authorized.

## Current state

- OPERATOR_PATTERN_EXISTENCE: STRONGLY_SUPPORTED
- BROAD_RELAUNCH_SIGNAL: REJECTED_AS_STANDALONE
- BROAD_QUOTE_SIGNAL: REJECTED_AS_STANDALONE
- PRELAUNCH_COHORT_WAKEUP: CONTINUE_SHADOW
- COUNTING_GATE: READY_FOR_BOUNDED_EXECUTION
- REALIZABLE_FIRST_PUMP_WINDOW: NOT_PROVEN
- NANSEN_TOPUP_REQUIRED: NO
- NEW_SCANNER: NO
- AUTO_BUY/AUTO_SELL: NO
