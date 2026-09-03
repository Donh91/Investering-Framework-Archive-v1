# HANDLEKOMPAS v1

## Purpose

Permanent iPhone-first decision output for the Investering Framework.

Trigger names:
- `handlekompas`
- `Handlekompas`
- `HANDLEKOMPAS`

The same block is mandatory at the very end of every DATA PING interpretation.

This is an OUTPUT / FORECAST-ACCOUNTABILITY contract only. It does not change canonical market rules, thresholds, weights, source authority, portfolio execution authority, or promotion governance.

## User goal

Make the next action obvious for a high-beta crypto portfolio, especially small-cap and microcap altcoins/memes, where the key choices are:
- BUY
- BUY DIP
- HOLD
- SWING-REDUCE
- SELL / CASH

The user values prediction of direction, pullbacks, timing and ranges more than explanatory prose. Heavy analysis belongs in the machinery, not the visible output.

## Input priority

Use the freshest eligible evidence available under existing framework authority. Prefer:
1. latest accepted DATA PING packet;
2. latest complete Hourly owner/directional sequence;
3. current canonical/owner market, breadth, liquidity, derivatives and rotation evidence already available to the framework;
4. shadow/research evidence only within its existing non-binding authority.

Never upgrade stale, partial, proxy, research-only or discovery-only evidence into canonical confirmation.

If a required input is unavailable, state the specific limitation and reduce confidence. Do not invent a range merely to fill the template.

## Mandatory rendering rules

- Vertical mobile layout only. Never use a horizontal table.
- Extremely concise. No long explanatory sections inside HANDLEKOMPAS.
- Clear language. No ambiguous hedging without an explicit action.
- Separate BTC market direction from altcoin/microcap behavior.
- For BTC use concrete USD ranges when supported.
- For generic microcaps use percentage move ranges from the forecast reference level. If a specific coin is being analyzed, use its price or market-cap range when supported.
- Every range is a forecast interval, not a canonical threshold.
- Every horizon must include: direction, expected path/order of moves, expected range, pullback expectation, action and confidence.
- Forecast ordering matters. Examples: `↘ → ↗`, `↗ → ↘`, `↗ → ↗`, `↘ → ↘`, `→ → ↗`.
- When evidence is insufficient for a responsible numeric range, write `RANGE: NOT RELIABLY ESTIMABLE` rather than fabricating precision.

## Permanent output format

# 🧭 HANDLEKOMPAS

### NU → 24T
**Marked:** <↑ BULLISH | → SIDEWAYS | ↓ BEARISH>
**Forløb:** <ordered path, e.g. ↘ → ↗>
**BTC-range:** <USD range or NOT RELIABLY ESTIMABLE>
**Microcaps:** <expected % range from current/reference level>
**Pullback:** <expected % range + most likely timing window>
**Handling:** **<BUY | BUY DIP | HOLD | SWING-REDUCE | SELL / CASH>**
**Confidence:** <0–100%>

### 1–3 DAGE
**Marked:** <↑ | → | ↓>
**Forløb:** <ordered path>
**BTC-range:** <USD range or NOT RELIABLY ESTIMABLE>
**Microcaps:** <expected % range>
**Pullback:** <expected % range + timing>
**Handling:** **<one clear action>**
**Confidence:** <0–100%>

### 5–7 DAGE
**Marked:** <↑ | → | ↓>
**Forløb:** <ordered path>
**BTC-range:** <USD range or NOT RELIABLY ESTIMABLE>
**Microcaps:** <expected % range>
**Pullback:** <expected % range + timing>
**Handling:** **<one clear action>**
**Confidence:** <0–100%>

### 2–3 UGER
**Marked:** <↑ | → | ↓>
**Forløb:** <ordered path>
**BTC-range:** <USD range or NOT RELIABLY ESTIMABLE>
**Microcaps:** <expected % range>
**Pullback:** <expected % range + timing>
**Handling:** **<one clear action>**
**Confidence:** <0–100%>

### 🎯 MICROCAP ACTION
**<BUY | BUY DIP | HOLD | SWING-REDUCE | SELL / CASH>**

### ⚡ NÆSTE FORVENTEDE MOVE
**<tight timing window>: <expected immediate sequence and action implication>.**

## Action semantics

- `BUY`: risk/reward favors immediate deployment; waiting is more likely to lose entry quality than improve it.
- `BUY DIP`: bullish structure, but a retrace is expected to offer materially better R/R.
- `HOLD`: existing exposure is preferred; trading around the position has no demonstrated edge.
- `SWING-REDUCE`: downside/pullback risk is high enough to justify taking partial profit into strength with intent to rebuy lower if confirmation remains intact.
- `SELL / CASH`: downside risk dominates and capital preservation has priority.

## Forecast accountability

Price/range, pullback and timing forecasts should be preservable for later scoring against realized outcomes. Where the framework supports it, record:
- forecast reference timestamp;
- reference BTC price;
- horizon;
- BTC expected range;
- microcap expected percentage range;
- expected pullback range;
- expected pullback timing window;
- expected ordered path;
- confidence;
- realized outcome after maturity.

Do not rewrite an issued forecast after the fact. Revisions are new forecasts with new timestamps.

## Standalone prompt behavior

When the user asks only `handlekompas`, return the HANDLEKOMPAS block and at most one short source/quality note if materially necessary. Do not prepend a market essay.

## DATA PING behavior

Every DATA PING interpretation must end with this HANDLEKOMPAS v1 block. It supersedes all earlier Handlekompas rendering formats. The DATA PING body may remain detailed when needed, but this block is the final user-facing decision surface.