# Compass Decision Presentation, Full Rotation Ladder & Sell Learning v1

Status: CANONICAL PRESENTATION / LEARNING REQUIREMENT
Date: 2026-09-17
Owner: existing Native Handlekompas + Official Daily Compass accountability layer
Authority ceiling: OFFICIAL_NAVIGATION_OUTPUT. No portfolio execution authority.

## Purpose

Every user-facing Compass must be factual, concise, mobile-readable and unambiguous. It must not turn uncertainty into a bullish or bearish story. If direction is unknown or mixed, say that plainly.

Compass treats BUY/TOP-UP, HOLD and SELL as separate decisions. WAIT or HARD_WAIT for new capital must never be rendered as an instruction to sell existing exposure.

The machine must preserve materially more detail internally than is shown to the user. Internal detail is prospective evidence for later pattern analysis, agent consumption, audit and outcome learning; user-facing Compass is a compact decision surface.

## Canonical user-facing ON_DEMAND layout

Render in this order:

1. `STATUS NOW` — one plain-language state and one sentence saying what it means.
2. `12 HOURS` — direction/risk/path, action, horizon and ETA.
3. `1–3 DAYS` — direction/risk/path, action, horizon and ETA.
4. `5–7 DAYS` — direction/risk/path, action, horizon and ETA.
5. `ROTATION` — compact full-chain ladder, always present.
6. `BUY/TRIGGER` — exact governed confirmation/deterioration conditions where available.
7. `SELL` — separate high-evidence block with state, horizon and ETA.
8. `ACTION NOW` — one unambiguous operational sentence.

No filler, false precision or euphemism. `UNKNOWN` is preferable to invented precision.

## Permanent full altcoin / risk ladder

Every genuine Compass decision freeze MUST preserve the full ladder:

`BTC → ETH → LARGE_CAPS → MID_CAPS → SMALL_CAPS → MICROCAPS → MEMES`

For every rung, preserve at minimum:

- `segment`
- `status` (machine state)
- `action` (what the navigation layer says to do)
- `direction`
- `horizon`
- `eta`
- `confidence` or explicit null/UNKNOWN
- `upgrade_trigger`
- `deterioration_trigger`
- evidence/source binding sufficient to reproduce the assessment

Where available, preserve reason, freshness and eligibility as well. Missing remains null/UNKNOWN, never zero.

`status` and `action` are deliberately separate. They may have the same wording, but must not be collapsed because later analysis must be able to test whether a state translated into an appropriate action.

### MEMES semantics

MEMES is a separate risk/rotation rung rather than being silently merged into MICROCAPS. It exists because meme deployment can have materially different eligibility and risk behavior from non-meme microcaps.

`A+ ONLY`, if used by an eligible governed owner, is an action/deployment policy — not a market state and not a quality claim invented by presentation. If the machine lacks eligible meme-specific evidence, preserve `UNAVAILABLE`/`UNKNOWN`; do not infer a meme signal from MICROCAPS.

## Compact ON_DEMAND rotation rendering

The full ladder is mandatory in every on-demand Compass, but it must remain compact. Preferred rendering is two lines, for example:

`ROTATION: BTC HOLD · ETH HOLD · Large PREPARE · Mid/Small WAIT · Micro NO DEPLOY · Memes A+ ONLY`
`ETA: Large–Small 1–3d · Micro/Memes 5–7d`

This is a rendering compression only. The underlying freeze must retain every rung independently with its complete fields and evidence bindings.

Do not merge rungs in the frozen data merely because the presentation combines them (`Mid/Small`, `Micro/Memes`, etc.). Combine labels only when their current user-facing action/ETA semantics genuinely match.

ETA means time to the next relevant assessment/trigger window, not a promise that the rung will upgrade or become buyable at that time. `WAIT + ETA 1–3d` must never be interpreted as `BUY IN 1–3d`.

## Agent/data-consumption invariant

Compass is a machine-readable source, not only a chat rendering. Any agent that consumes the canonical Compass must be able to retrieve the complete per-rung ladder and its prospective evidence from the canonical Compass artifact/source bindings without scraping prose or reconstructing it from a screenshot.

The full ladder must therefore be part of the canonical internal freeze/schema and, where safe for public consumption, the sanitized projection. User-facing compression must never delete the underlying machine-readable observations.

Later research must be able to study, among other things, transition order and lag (`BTC → ETH → LARGE → MID → SMALL → MICRO → MEMES`), WAIT/PREPARE/HOLD persistence, upgrade/deterioration timing, drawdown protection, opportunity cost and whether lower-cap transmission survived pullbacks. These are analysis targets, not assumptions that such patterns exist.

## Freshness and ON_DEMAND invariant

The 24/7 upstream machine remains autonomous. DAILY Compass remains an immutable benchmark. Genuine `Kompas` requests are ON_DEMAND decision points.

Freshness is horizon-specific. If the relevant short horizon is no longer defensibly fresh, the system must refresh/re-read eligible governed upstream state and create a separate immutable `run_reason=ON_DEMAND` freeze. Never overwrite DAILY.

A new timestamp must never launder stale evidence. If upstream state cannot be refreshed, fail closed with DEGRADED/UNAVAILABLE for the affected horizon while preserving longer horizons that remain eligible.

Official prospective freezes are DAILY + genuine ON_DEMAND decision points + governed meaningful state changes, rather than mechanically freezing every collector tick. Freeze type/reason must be retained so learning can stratify correlated observations rather than treating them as independent predictions.

## Preferred language semantics

- `UNCLEAR` / `MIXED` means there is no defensible directional edge. Do not silently translate it into UP or DOWN.
- `WAIT/HARD_WAIT` means no new deployment/top-up in that lane unless the artifact explicitly says otherwise.
- `HOLD` means retain existing exposure at the navigation layer; it is not a new-buy instruction.
- `PREPARE` is not BUY; it means the relevant governed trigger window is approaching or partially satisfied.
- `NO DEPLOY` is a new-capital restriction, not SELL.
- SELL must be stated only when eligible governed evidence supports it.

## Asymmetric SELL rule

BUY and SELL errors are not symmetric. A premature exit can create irreversible opportunity cost if a temporary pullback is followed by a large continuation/altseason move. Therefore a short bearish interval, weak breadth, a pullback, WAIT, HARD_WAIT or HOLD_DEFENSIVE_WAIT must not by itself be promoted to SELL.

SELL is a separate compact block using controlled states:

- `NO_SELL`
- `SWING_TRIM_SMALL`
- `SWING_TRIM_LARGE`
- `FULL_EXIT`
- `NO_EDGE` / `UNAVAILABLE` where required

Every SELL assessment includes the applicable horizon and ETA. If no defensible ETA exists, use UNKNOWN.

## Prospective decision-learning requirement

Every genuine Compass freeze must preserve enough information to evaluate BUY/TOP-UP, HOLD, the full rotation ladder and SELL prospectively. Outcome learning remains separate from immutable forecasts.

For each matured horizon (+12h, +72h, +168h), preserve where reproducible: terminal return, MFE, MAE, trigger timing, upgrade/deterioration timing, HOLD/abstention quality, downside potentially preserved, upside foregone, false/premature sell, missed/late de-risk and whether a registered lower re-entry became available after a swing-trim assessment.

Do not claim a successful swing merely because price initially fell. Re-entry must be tied to registered prospective confirmation rather than a hindsight low. Do not collapse outcomes into one flattering score.

A recommendation must never be retrospectively invented. Only the decision frozen at issuance may be judged as prospective advice. Missing outcome evidence remains missing, never zero and never an automatic miss.

## Learning boundary

Existing descriptive exit calibration remains non-authoritative until prospective sample size and governance justify any threshold/rule change. Learning may propose calibration changes through normal governance, but must not silently mutate historical forecasts, thresholds, model weights, source authority or portfolio execution.

## Rendering invariant

The user-facing result stays short even though the internal artifact is rich. A normal ON_DEMAND Compass should fit the approved structure and show the complete chain in compressed form:

`STATUS NOW → 12H → 1–3D → 5–7D → ROTATION (full chain, compact) → BUY/TRIGGER → SELL → ACTION NOW`

The words shown to the user must be derived from the canonical artifact. Presentation may compress wording but may not change the underlying state.