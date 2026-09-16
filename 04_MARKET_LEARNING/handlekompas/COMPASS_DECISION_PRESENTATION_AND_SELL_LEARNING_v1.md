# Compass Decision Presentation & Sell Learning v1

Status: CANONICAL PRESENTATION / LEARNING REQUIREMENT
Date: 2026-09-16
Owner: existing Native Handlekompas + Official Daily Compass accountability layer
Authority ceiling: OFFICIAL_NAVIGATION_OUTPUT. No portfolio execution authority.

## Purpose

Every user-facing Compass must be factual, concise, mobile-readable and unambiguous. It must not turn uncertainty into a bullish or bearish story. If direction is unknown or mixed, say that plainly.

Compass must treat BUY, HOLD and SELL as separate decisions. A WAIT or HARD_WAIT state for new capital must never be rendered as an instruction to sell an existing position.

## Canonical user-facing layout

Render in this order:

1. `STATUS NOW` — one plain-language state and one sentence saying what it means.
2. `12 HOURS` — direction, risk/path, explicit action.
3. `1–3 DAYS` — direction, risk/path, explicit action.
4. `5–7 DAYS` — direction, risk/path, explicit action.
5. `ROTATION` — BTC → ETH → LARGE_CAPS → MID_CAPS → SMALL_CAPS → MICROCAPS.
6. `WHAT CHANGES THE SIGNAL?` — exact confirmation and deterioration conditions where governed.
7. `DECISION NOW` — three explicit fields: BUY, HOLD, SELL.
8. `CONCLUSION` — one unambiguous sentence. No filler, false precision or euphemism.

Preferred language semantics:

- `UNCLEAR` means there is no defensible directional edge. Do not silently translate it into UP or DOWN.
- `WAIT/HARD_WAIT` means no new deployment/top-up in that lane unless the artifact explicitly says otherwise.
- `HOLD` means retain existing exposure at the navigation layer; it is not a new-buy instruction.
- `SELL/DE_RISK` must be stated only when an eligible governed exit/de-risk owner actually supports it.
- If SELL evidence is insufficient, say `SELL: NOT TRIGGERED` rather than implying safety.

## Asymmetric decision-error rule

BUY and SELL errors are not treated as symmetric.

A premature top-up can create drawdown but may remain recoverable if the thesis survives. A premature exit can create irreversible opportunity cost if a temporary pullback is followed by a large continuation/altseason move. Therefore a short bearish interval, weak breadth, a pullback, WAIT, HARD_WAIT, or HOLD_DEFENSIVE_WAIT must not by itself be promoted to SELL.

This is not a rule to never sell. SELL is a first-class Compass decision and must be surfaced clearly when evidence warrants it. The system must distinguish at least:

`HOLD → DE_RISK_WATCH → PARTIAL_DE_RISK → EXIT`

Any promotion beyond HOLD requires explicit eligible evidence and must preserve the exact prospective evidence snapshot. No new thresholds are created by this presentation contract.

## Prospective sell-learning requirement

Every Official Daily Compass freeze must preserve enough information to evaluate SELL/de-risk advice prospectively. Outcome learning must remain separate from the immutable forecast.

For each matured horizon (+12h, +72h, +168h), when governed evidence exists, measure separately:

- decision at issuance: HOLD / DE_RISK_WATCH / PARTIAL_DE_RISK / EXIT / NO_EDGE;
- subsequent terminal return;
- maximum adverse excursion after the decision;
- maximum favorable excursion after the decision;
- time to trough and time to subsequent recovery/high where reproducible;
- capital-preservation reference from reducing/exiting;
- upside/opportunity cost that would have been forfeited by reducing/exiting;
- whether deterioration/exit confirmation actually fired, and when;
- false-sell / premature-exit events;
- missed-de-risk / late-exit events;
- abstention/HOLD quality.

Do not collapse these into one flattering score. Preserve components so later calibration can compare downside protected against upside forfeited.

A SELL recommendation must never be retrospectively invented. Only the decision frozen at issuance may be judged as prospective advice. Missing outcome evidence remains missing, never zero and never an automatic miss.

## Learning boundary

The existing `scripts/learning/action_compass_exit_calibration.py` is descriptive evidence and already measures post-signal upside, drawdown and full-exit opportunity-cost references. It must remain non-authoritative until prospective sample size and governance justify any threshold/rule change.

The Official Daily Compass outcome layer must learn from its own immutable prospective decisions as observations mature. Learning may propose calibration changes through normal governance, but must not silently mutate historical forecasts, thresholds, model weights, source authority, or portfolio execution.

## Rendering invariant

The final line must be operationally unambiguous, for example:

`DECISION NOW: BUY — NO | HOLD — YES | SELL — NOT TRIGGERED.`

The words must be derived from the canonical artifact. Presentation may simplify wording but may not change the underlying state.