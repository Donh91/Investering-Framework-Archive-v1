# AT-SRC-0013 — Outputlayer / copy-trading-min-latency external reproduction benchmark

Date captured: 2026-10-02
Status: DEEP_SCREENED / HIGH_VALUE_EXTERNAL_REPRODUCTION_BENCHMARK
Evidence class: PUBLIC CODE + PUBLIC RESEARCH ARTIFACTS + AUTHOR CLAIMS
Authority: RESEARCH / SHADOW ONLY
Related Alpha Lab owner: #1087 / #1436

## Frozen source

Repository:
`raghav-rathi/copy-trading-min-latency`

Frozen commit:
`63d37fd16be47df6321363e919228490b005c36b`

Relevant public artifacts:
- `docs/STRATEGY.md`
- `docs/research/operator-whale-wallets.md`
- `docs/research/whale-profiles.md`
- `data/whales_seed.json`

Exact executor under study:
`0x53a42d2d0fdd60bf8f833fb94841349095a74024`
Robinhood Chain 4663.

## Why this source matters

This repository is unusually relevant because it independently attacked the exact Outputlayer executor case that Alpha Lab began auditing on 2026-10-02.

It does not merely repeat the public performance screenshot.
It attempts episode-level reconstruction and target-wallet profiling.

That makes it a better research benchmark than social claims alone.

## External findings worth reproducing

The repo reports:

- 58 clear operator buy episodes found;
- 53 episodes attributed under a strict same-block preceding-target rule;
- 25 distinct target wallets recovered, not ~33;
- 4 examined episodes with no matching preceding same-block end recipient;
- 1 ambiguous episode excluded;
- operator buy episode methods 0x00000007 / 0x00000009;
- a separate method class excluded from copy-buy counting.

Attribution rule described by the repo:

operator receives a non-quote token
->
inspect earlier transaction/log order in the same block
->
same token reaches an end wallet
->
exclude router/pool/solver/hook infrastructure
->
candidate target wallet.

This is a reproducible hypothesis, not yet Alpha Lab truth.

## Most important falsification

The source reports that the top target set is not a collection of independent smart whales.

Six high-frequency target addresses reportedly share one funding root through Relay:

`0xf70da97812CB96acDF810712Aa562db8dfA3dbEF`

If independently reproduced, this means:

raw wallet count != independent information count.

The external research also reports that the most-copied wallet has poor closed performance and that the target-wallet closed records do not support the simple public narrative:

`+21.3k realized / 45 of 53 green`.

Important nuance:

This does NOT prove the executor itself was unprofitable.

The executor may:
- exit differently;
- size differently;
- exploit same-block price ordering;
- capture a short microstructure window;
- avoid following target exits.

Therefore separate:

`TARGET_WALLET_SKILL`

from:

`EXECUTOR_TIMING / MICROSTRUCTURE_EDGE`.

## Existing Framework comparison

The Investering framework already owns:

- FOMO Robinhood provenance observer;
- economic-entity collapse;
- recipient-spoof / seeded-transfer defenses;
- frozen cohort logic;
- sellability;
- realizable MFE/MAE;
- prospective rows;
- no-retroactive wallet scoring.

Therefore do NOT fork this repository wholesale.

The useful research delta is:

1. exact executor-episode reconstruction;
2. same-block target attribution;
3. target-vs-executor outcome separation;
4. external target-set negative control;
5. latency/execution-fidelity benchmarking.

## Architecture observations

The external repo describes a pipeline with:

- Solana-side precursor watcher;
- Robinhood sequencer timing measurement;
- wallet scoring;
- balance-diff conditional detector;
- exits;
- paper-first live gate.

The high-value idea for Alpha Lab is not autonomous copying.

It is the causal separation:

`PRECURSOR_EVENT_TIME`
->
`TARGET_FILL_TIME`
->
`EXECUTOR_ACTION_TIME`
->
`REALIZABLE_ENTRY`
->
`REALIZED_EXIT`.

This should be measured before considering any strategy semantics.

## What to borrow

Research primitives only:

- same-block episode reconstruction;
- target-address attribution with infrastructure exclusion;
- target/executor outcome separation;
- correlation/funding-root collapse;
- execution latency;
- explicit model-vs-realized result;
- paper/forward evidence before promotion.

## What not to import

- external COPY/FADE/PASS labels as truth;
- public wallet PnL rankings;
- target addresses as smart-money labels;
- autonomous copy execution;
- fixed thresholds from the external scorer;
- public +21.3k / 45-of-53 claim as verified performance;
- same-block activity as alpha without public-eligibility and sellability proof.

## Relationship to Risk Lab learning

Risk Lab's useful methodological lesson is compatible with this source:

strategy signal quality and execution fidelity are separate questions.

For this case, measure at minimum:

- target event time;
- first public-visible precursor time;
- executor action time;
- token;
- expected/model entry;
- realizable entry;
- realized exit;
- gas/slippage;
- MFE;
- MAE;
- model-vs-realized error.

## Current Alpha Lab state

`OUTPUTLAYER_TARGET_COHORT = EXTERNAL_LEAD`

`TARGET_WALLET_SKILL = UNPROVEN`

`EXECUTOR_EDGE = UNPROVEN`

`PUBLIC_PRECURSOR_EDGE = UNPROVEN`

`AUTO_EXECUTION = NO`

The correct next step is independent reproduction under #1436, not strategy deployment.
