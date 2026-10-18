# REA Method Transfer into Inhouse Alpha Lab Source QA
Date: 2026-10-18
Status: RESEARCH_ONLY / NO_EXTERNAL_REA_INSTALL / NO_PRODUCTION_AUTHORITY

## 1. External reference, without tool adoption

Official: https://github.com/morluto/rea
REA means Reverse Engineer Anything. Its useful methodological ingredients are evidence-rich investigation, bounded source selection, replay, explicit unavailable/unknown states, passive browser/HAR and offline code inspection.

REA was **not installed or executed** here. Public source code and published API contracts were inspected with ordinary authorized tools, and a *new* independent Python component was implemented. We did not collect a browser HAR, run native code analysis or decrypt/inject into applications.

## 2. Actual transfer matrix

| Method | Inhouse transfer | Present evidence | Not established |
| --- | --- | --- | --- |
| Evidence survives failure | Deterministic SHA-256 of response JSON, unavailable/parse flags | Synthetic positive/negative tests | Provider authenticity/immutable capture |
| UNKNOWN vs unavailable | Missing != zero, stale/429/invalid => explicit flags | Negative controls | Economic loss avoided |
| Replay | Input-only, offline deterministic CLI | Unit tests | Historical point-in-time acceptance |
| Bounded selection | One case, at most one observation per provider, no network I/O | Static inspection | Full universe recall |
| HAR/API inference | Minimal parser for published DexPaprika, DexScreener and GeckoTerminal response fields | Source-code/API contract audit | No HAR or proprietary behavior observation |
| Offline EVM metadata | Not implemented | Existing chain-native investigators own this | No bytecode security/sellability proof |

## 3. Inhouse implementation

File: source_qa_v1.py
Test: test_source_qa_v1.py
Run tests: python -m unittest discover -s . -p 'test_source_qa_v1.py' -v
Run offline: python source_qa_v1.py --input LOCAL_CASE.json --output LOCAL_SOURCE_QA.json

The implementation uses only Python standard library and does not call network, wallets or exchanges. It emits provider-value-free comparison flags plus stable payload digests. It does not persist raw payloads, normalized prices, liquidity amounts or token identifiers. It is deliberately **not** a live adapter/scanner or sellability engine. Input data must remain local to its authorized evidence plane.

Twenty-four local synthetic regression tests passed on 2026-10-18, checking valid tri-provider structure, missing vs zero, bad/negative/NaN/bool values, token role conflicts, Solana case sensitivity, creation-time dispute, HTTP429, stale/future time, malformed payloads, deterministic digest, output-leak check, duplicate source rejection, no second source, capture-window mismatch, chain identity and no sellability inference. CI and merged-main readback have not yet been proven.

## 4. OBSERVED / INFERRED / UNKNOWN / UNAVAILABLE

OBSERVED:
- External unauthenticated public endpoint checks showed the DexPaprika network set contains Robinhood Chain, Solana and Ethereum.
- Across one thin/withdrawn pool and one healthy Solana pool, DexPaprika and two existing market aggregators were broadly consistent in their current reported liquidity situations.
- DexScreener omitted a liquidity value for a Robinhood V4 pool where DexPaprika reported zero. An omission is NOT corroboration of zero.
- GeckoTerminal gave a different creation timestamp for a selected Orca pool than DexPaprika/DexScreener. No one source established original onchain pool genesis.
- Local **synthetic** code tests passed. These are not empirical source-uplift results.

INFERRED: a source QA guard may reduce false SAFE or premature alpha assumptions when liquidity is unknown, timestamps disagree or a market-data provider is stale.

UNKNOWN: matched prospective lead-time/coverage lift, sellability at any notional, faster pool discovery, first-block presence, economic alpha, independent shared-venue failure modes and any historical Task 2 improvement.

UNAVAILABLE: admitted frozen private source snapshots for a full prospective cohort; independent onchain creation proofs for the observed pool birth discrepancy; exact-matched historical source-capture times across all sources.

## 5. Existing owner, governance and stop rules

Owner reuse: Archive #1017 source adapter (requires frozen cross-chain field map), #1087 Alpha Lab data health, #1340 prospective denominator, Meme-Alpha-Lab #126, S1 executable sellability truth and master Research Lab #1512. The new prototype owns nothing in production.

This is a research candidate in the existing research folder, no new queue/agent/scheduler. It must not be imported into live scoring until existing source-map and governance preconditions, risk-adjusted review and controlled prospective evidence pass.

Forbidden:
- Moving raw/normalized restricted source values into the public control plane.
- Claiming aggregator agreement is independent onchain truth.
- Converting pool age into token genesis or trailing volume into available sell-side liquidity.
- Treating missing field as 0, unknown as safe, or observed sellability as a buy/sell signal.
- Charging a paid API, running REA setup, opening an always-on provider collector, or changing any canonical Alpha Lab thresholds.
- Promoting synthetic tests as market outcomes, or using future provider snapshots for historical decisions.

## 6. Next valid experiment (only under admitted owner)

After checking exact current #1017 field-map and the existing source receipts, freeze a bounded panel across ETH, Solana and Robinhood including both early/ordinary and drained/untradeable pools. Compute source availability, field-missing rate, pair/time inconsistencies, freshness, point-in-time coverage and unique incremental information against the existing GeckoTerminal/DexScreener owner. Source identity and potential execution require chain-native evidence. Negative/no-gain remains an acceptable result. If source owner duplicates the capability, stop as a clean no-op.

## 7. Archify replacement

A simple public-safe source-bound Mermaid diagram is supplied in INHOUSE_SOURCE_BOUNDARY_MAP.md. It reuses existing file/issue references rather than installing Archify or permitting external code to crawl private repositories. Diagram rendering is a human-communication aid, not an execution or governance engine.
