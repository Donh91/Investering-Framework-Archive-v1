# RAW Shadow Direction Confidence Indicator v1

**Date:** 2026-08-30  
**Status:** CANONICAL_OPERATIONAL_PROTOCOL  
**Owner:** MAIN_FRAMEWORK / CHATGPT output routing  
**Scope:** Main-Framework interpretation of DATA PING and RAW market-data messages  
**Authority:** OUTPUT_DIAGNOSTIC_ONLY / SHADOW_ONLY  
**Depends on:** `02_DATA_PING/protocols/2026-08-25__three-horizon-action-compass-output-contract-v1__canonical.md`, `04_MARKET_LEARNING/intraday_execution/LATEST.json`, `04_MARKET_LEARNING/intraday_execution/config.json`  

## 1. Purpose

Expose the existing intraday research owner's prospective direction and calibration evidence in every Main-Framework DATA PING / RAW interpretation, so directional statements become increasingly evidence-bound and calibrated instead of being recreated as conversational guesses.

This protocol is an output diagnostic extension only. It does not create a new market engine, sensor, decision vocabulary, market state, threshold, portfolio action or execution authority. The Three-Horizon Action Compass remains the sole current decision vocabulary.

## 2. Mandatory scope

For every Main-Framework response whose primary input is a DATA PING packet or RAW market-data ingest, including fresh packets, replays, corrections and replacement threads:

1. resolve current framework authority normally;
2. apply the current Three-Horizon Action Compass owner;
3. read the latest eligible `04_MARKET_LEARNING/intraday_execution/LATEST.json`;
4. show one compact `SHADOW RETNINGSKONFIDENS` diagnostic block before the final `HANDLEKOMPAS`;
5. never insert this block into the immutable collector packet or collector wire format.

A replay does not create a new directional prediction merely because it is shown again. Prospective prediction creation and outcome maturation remain owned by the hourly intraday research workflow.

## 3. Mandatory diagnostic semantics

The block must preserve, when available:

- horizon: `1H`, `4H`, `24H`;
- target: `BTC`, `ETH`;
- direction: `UP`, `DOWN`, `NO_EDGE`;
- calibrated probability only when the owner exposes one;
- calibration maturity and independent calibration sample count;
- evidence agreement as a separate descriptive field;
- large-, mid- and small-cap transmission proxy state;
- explicit microcap evidence status.

`evidence_agreement_pct` is not a probability and must never be rendered as one.

## 4. Probability and confidence discipline

A numerical confidence percentage may be displayed only when the machine owner exposes `calibrated_probability` for the exact target, horizon, direction and calibration group.

If the owner reports `WARMUP`, `ABSTAIN_NO_EDGE`, missing probability, insufficient independent samples or stale/unavailable evidence, render the probability as `IKKE KALIBRERET` or omit it. Do not replace it with model intuition, conversation history or a subjective percentage.

The owner deliberately controls overlapping forecasts before counting independent calibration observations. A high raw observation count is not automatically a high independent sample count.

`99%` or equivalent highest-assurance wording may be used only when the machine owner explicitly reports `HIGH_ASSURANCE_99_ELIGIBLE`. ChatGPT may not self-declare that class.

## 5. NO_EDGE rule

`NO_EDGE` is a valid and preferred answer when directional evidence is split, incomplete, stale or not sufficiently calibrated.

Do not force `UP` or `DOWN` merely because the user asks a binary question. A useful response may state that the current machine evidence does not support a high-confidence binary call.

Missing data remains `UNKNOWN`, not negative evidence.

## 6. Large-cap to microcap decomposition

Current `breadth_rich` coverage supports Top-100 rank-segment transmission proxies only:

```text
large_cap_proxy: filtered_rank 3-25
mid_cap_proxy: filtered_rank 26-50
small_cap_proxy: filtered_rank 51-100
microcap: DATA_UNAVAILABLE / NO_EDGE
```

These rank segments are research transmission proxies and must not be described as canonical market-cap definitions.

Until an eligible microcap owner exists, `microcap` must remain `NO_EDGE` / `DATA_GAP`. BTC, ETH or Top-100 breadth may provide context but may not be silently converted into a calibrated microcap forecast.

When the user asks whether the altcoin market is expected to go up or down, answer separately across the available transmission layers. Do not collapse large-cap evidence into one blanket altcoin probability.

## 7. Prospective learning loop

The existing intraday research owner is responsible for this loop:

```text
RAW/hourly owner evidence
-> frozen shadow directional prediction
-> NO_EDGE abstention where appropriate
-> future owner evidence after the frozen horizon
-> matured HIT / MISS / ABSTAINED / CENSORED outcome
-> miss-family diagnostics
-> calibration group update
-> Brier/calibration diagnostics when probability existed at freeze
-> future probability display only after the minimum independent sample gate
```

A miss must remain visible. It may identify which evidence families aligned with the actual outcome and which opposed it, but it may not automatically change model weights or canonical thresholds. Reweighting or promotion requires separate governed evidence and review.

## 8. Human output format

Use a compact block similar to:

```markdown
### 🧪 SHADOW RETNINGSKONFIDENS
1H - BTC: UP | P: IKKE KALIBRERET | n=7 | evidens 5/6
1H - ETH: NO_EDGE | P: - | n=0 | evidens delt
Transmission: Large UP | Mid UP | Small NO_EDGE | Micro NO_EDGE (DATA_GAP)
Status: SHADOW_ONLY - ingen portfolio authority
```

When calibrated probability exists, use for example `P: 73% KALIBRERET`, together with the independent `n`. Do not round an evidence-agreement percentage into this probability field.

The block may be shortened when several horizons repeat the same status, but 1H/4H/24H machine state must remain recoverable in a machine-readable response when requested.

## 9. Staleness and failure behavior

If `04_MARKET_LEARNING/intraday_execution/LATEST.json` is missing, malformed or too stale to support the requested horizon:

```text
SHADOW RETNINGSKONFIDENS: UNAVAILABLE / STALE
P: IKKE TILGÆNGELIG
```

Do not invent a fallback percentage. The Main Framework may still interpret the underlying RAW packet under normal canonical rules and must still provide the mandatory Action Compass.

An intraday research failure does not transfer authority to another model or conversational estimate.

## 10. Authority boundary

```text
new engine: NO
new sensor: NO
new canonical market state: NO
new action vocabulary: NO
collector wire-format change: NO
automatic model reweighting: NO
automatic portfolio execution: NO
shadow diagnostic output: MANDATORY_FOR_RAW_INTERPRETATION
prospective learning: EXISTING_INTRADAY_OWNER_EXTENSION
numeric confidence before calibration gate: FORBIDDEN
microcap proxy substitution: FORBIDDEN
99 percent self-declaration: FORBIDDEN
```

The indicator can inform Main-Framework reasoning, but it cannot override current canonical evidence, gates, Action Compass semantics or portfolio authority.
