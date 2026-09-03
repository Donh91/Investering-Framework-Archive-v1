# DATA PING Handlekompas Output Binding v1 — Canonical

Effective: 2026-09-03

Status: CANONICAL OUTPUT BINDING

Prompt authority:
`07_PROMPTS_AND_AGENTS/prompts/HANDLEKOMPAS_v1.md`

## Binding rule

Every interpreted DATA PING response shown to the user MUST end with `HANDLEKOMPAS v1` as its final decision surface.

This binding supersedes all earlier Handlekompas presentation formats. It does not supersede or modify DATA PING collection, validation, source, state, market-rule, risk, rotation, portfolio-authority or promotion contracts.

## Mandatory horizons

Render exactly these decision horizons in vertical mobile format:
1. `NU → 24T`
2. `1–3 DAGE`
3. `5–7 DAGE`
4. `2–3 UGER`

Each horizon must include, when supportable from eligible evidence:
- market direction;
- ordered expected path;
- BTC expected USD range;
- microcap/altcoin expected percentage range from reference level;
- expected pullback magnitude and timing;
- one clear action;
- forecast confidence.

Finish with:
- `MICROCAP ACTION`
- `NÆSTE FORVENTEDE MOVE`

No horizontal tables are allowed in the Handlekompas block.

## Decision emphasis

The visible decision surface is optimized for the user's practical choices in high-beta altcoins/microcaps/memes:
- BUY
- BUY DIP
- HOLD
- SWING-REDUCE
- SELL / CASH

BTC direction remains a primary market regime input, but altcoin/microcap action must be independently explicit because BTC and high-beta altcoins can be in different states.

## Evidence and fail-closed behavior

The renderer must respect the existing authority hierarchy and source quality of the DATA PING and framework.

A valid DATA PING with a partial or unavailable lane may still be interpreted within existing rules, but Handlekompas must not disguise the missing evidence.

If a numeric BTC range, microcap range, pullback range or timing window cannot be responsibly supported, render `NOT RELIABLY ESTIMABLE` and reduce confidence. Never fabricate precision to satisfy the template.

If the DATA PING itself is invalid for main-thread ingest, the previous accepted packet remains authoritative and Handlekompas must explicitly bind to that previous accepted state rather than treating the invalid packet as new truth.

## Forecast semantics

All ranges, timing windows, ordered paths and confidence values are forecasts. They are not canonical thresholds and cannot modify framework state by themselves.

Where downstream forecast-accountability machinery supports persistence, the forecast should be frozen prospectively and later compared with realized outcomes. No hindsight rewrite is allowed.

## Standalone reuse

The same contract governs the separate user prompt `handlekompas`. The standalone response should use the freshest eligible accepted DATA PING plus latest complete Hourly owner evidence and return the compact Handlekompas block without unnecessary exposition.

## Supersession

Supersedes earlier user-facing Handlekompas rendering instructions only.

Does NOT alter:
- market thresholds;
- breadth thresholds;
- liquidity vetoes;
- ETH/BTC confirmation rules;
- source ownership;
- canonical market state;
- portfolio execution authority;
- research/shadow authority boundaries.