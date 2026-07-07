# DATA PING Alert Router v0.1

**Date:** 2026-07-07  
**Status:** CANONICAL  
**Domain:** DATA PING / execution compression / alert hygiene  
**Purpose:** Add a thin decision-routing layer on top of the active DATA PING feed so the user is alerted only when a market state becomes decision-relevant.

---

## 1. Executive conclusion

DATA PING is already the daily operational truth layer. Do not create a competing daily engine.

Instead, every meaningful DATA PING should end with a compact Alert Router block that translates the full framework state into one practical output:

```text
Should the user do something, prepare something, or ignore the noise?
```

The Alert Router is not a new research system. It is a compression and notification layer.

---

## 2. Source governance

Hard hierarchy:

```text
DATA PING / current truth-layer data = live state
Chief / action labels = operational execution lens
Shadow = learning and diagnostics
Consensus = de-noising
Research Lab / Claude / Grok = audit or adversarial context only
GitHub archive = canonical memory and durable governance
ChatGPT = framework governance and ratification
```

DATA PING version rule:

```text
HIGHEST ACTIVE DATA PING VERSION WINS.
```

Older DATA PING versions remain archive context unless explicitly reactivated.

---

## 3. Problem this patch solves

The old daily concepts had useful ideas, but too much overlapping behavior:

- Inhouse Shadow Sentinel
- Regime Context Engine
- Intraday Crash Sentinel
- Early Rotation Pre-Trigger
- RAW Shadow Logger
- Pullback / rebuy logic
- Exit / trim warning logic

Do not reactivate all of them as separate automations.

Merge their useful output into one Alert Router that runs inside the DATA PING interpretation.

---

## 4. Router output taxonomy

Every DATA PING should internally classify the market into one of these states:

```text
NO_ACTION
WATCHLIST_ONLY
PREPARE_BUY_LARGE_CAPS
START_SMALL_LARGE_CAPS
BUILD_LARGE_CAPS
PULLBACK_RISK_5_7D
TRIM_A_BID
REBUY_WINDOW_FORMING
NO_BUY_REGIME
INVALIDATED
```

Only notify or emphasize when the state changes into a decision-relevant category.

---

## 5. Mandatory Alert Router block

Add this block to DATA PING outputs when relevant:

```text
ALERT ROUTER

Large-cap buy window:
NO / WATCH / PREPARE / START_SMALL / BUILD / INVALIDATED

5-7D pullback risk:
LOW / MEDIUM / HIGH / STORM / TSUNAMI

Sell-a-bid edge:
NO / SMALL_TRIM / TRIM / PROTECT

Rebuy status:
LOCKED / WATCH / BTC_ONLY / LARGE_CAPS / ROTATION

No-buy regime:
YES / NO

Alert state:
NO_ACTION / WATCHLIST_ONLY / PREPARE_BUY_LARGE_CAPS / START_SMALL_LARGE_CAPS / BUILD_LARGE_CAPS / PULLBACK_RISK_5_7D / TRIM_A_BID / REBUY_WINDOW_FORMING / NO_BUY_REGIME / INVALIDATED

One-line action:
[one clear sentence]
```

If nothing decision-relevant changed, keep the block compact or omit it depending on DATA PING format.

---

## 6. Large-cap buy window logic

The user wants to be alerted before broad altseason when large caps become attractive, without chasing fake rotation or small/micro pumps too early.

Large-cap buy window can only move from WATCH to PREPARE / START_SMALL / BUILD when most of the following are true:

1. BTC structure is stabilizing, reclaiming or absorbing after pullback, not breaking down.
2. ETF / spot pressure is stabilizing or improving.
3. ETH/BTC is stabilizing or improving with persistence, not just one spike.
4. BTC dominance is stable, decelerating, or falling without defensive reclaim.
5. Breadth stops deteriorating.
6. Large caps are improving before mid/small/micro.
7. Stablecoin / liquidity context is not defensive parking only.
8. Fake-rotation risk is not high.
9. Regime allows buying.

State mapping:

```text
NO = no actionable buy setup
WATCH = prepare list only
PREPARE = large-cap window is forming, no full deployment
START_SMALL = first cautious large-cap buys allowed by framework
BUILD = confirmed large-cap build phase
INVALIDATED = prior watch/setup failed
```

Hard rule:

```text
Pre-Trigger is not a buy signal by itself.
Pre-Trigger opens observation and readiness only.
```

---

## 7. Pullback / sell-rebuy logic

The user wants an effective 5-7 day warning when a pullback is likely enough to justify selling a bid and potentially rebuying lower.

The router must distinguish ordinary volatility from actionable pullback risk.

Pullback classification:

```text
Ripple = normal noise, no action
Wave = watch, do not overreact
Heavy Wave = small trim may be justified if confirmation improves
Storm = clear trim / protect mode
Tsunami = capital-protection mode
```

Action mapping:

```text
LOW = no action
MEDIUM = watch only
HIGH = prepare trim, do not chase buys
STORM = trim a bid / protect capital
TSUNAMI = capital protection first
```

Sell-a-bid signal requires confluence, not just fear:

- RAW 5-7d downside bias rising
- failed reclaim or rejection at key level
- ETF / spot flow deterioration
- breadth weakening
- ETH/BTC rolling over or failing persistence
- BTC.D defensive behavior
- funding / OI fragility or leverage stress
- liquidity / macro not supportive
- prior recovery attempt losing quality

Do not trigger TRIM_A_BID on moderate pullback alone.

---

## 8. No-buy regime override

No-buy regime overrides all buy windows.

Set `No-buy regime: YES` if any of the following dominate:

- active breakdown or unresolved flush
- crash / regime damage
- recovery failure
- accelerating ETF / spot deterioration
- breadth collapse
- ETH/BTC structural failure
- BTC dominance defensive reclaim
- liquidity/transmission failure
- late-cycle distribution risk
- source conflict too high for action
- verified data missing for critical decision

When no-buy regime is YES, allowed outputs are:

```text
NO_ACTION
WATCHLIST_ONLY
PULLBACK_RISK_5_7D
TRIM_A_BID
NO_BUY_REGIME
INVALIDATED
```

Not allowed:

```text
START_SMALL_LARGE_CAPS
BUILD_LARGE_CAPS
REBUY_WINDOW_FORMING as action
```

---

## 9. Rebuy window logic

Rebuy status is separate from buy-window status.

```text
LOCKED = no rebuy allowed
WATCH = conditions improving but not actionable
BTC_ONLY = only market-beta / BTC stabilization context, no alt deployment
LARGE_CAPS = selective large-cap rebuy allowed
ROTATION = broader rotation window confirmed
```

Rebuy may only unlock if:

- pullback pressure is absorbed or completed
- BTC reclaims or stabilizes above relevant structure
- ETH/BTC stops deteriorating
- ETF / spot pressure stabilizes
- breadth confirms survival
- no-buy regime is NO
- fakeout risk is acceptable

---

## 10. Segment hierarchy

Buy order during early improvement:

```text
Large caps first
Mid caps second
Small caps third
Microcaps fourth
Memes last
```

Protection order during drain / pullback:

```text
Memes first
Microcaps second
Small caps third
Mid caps fourth
Large caps last
```

Never treat microcap-only pumps as real rotation.

---

## 11. Notification hygiene

Do not alert for routine chop.

Alert only when one of these becomes true:

```text
PREPARE_BUY_LARGE_CAPS
START_SMALL_LARGE_CAPS
BUILD_LARGE_CAPS
PULLBACK_RISK_5_7D with HIGH or worse
TRIM_A_BID
REBUY_WINDOW_FORMING after prior lock
NO_BUY_REGIME change
INVALIDATED after prior watch/setup
```

If the state remains unchanged, compress output and avoid repetitive warnings.

---

## 12. DATA PING prompt patch

Paste into the active DATA PING system / handoff prompt:

```text
MANDATORY PATCH — DATA PING ALERT ROUTER v0.1

After interpreting the active DATA PING state, produce an Alert Router classification.

Purpose:
Convert the full framework state into a practical action/no-action label for the user without adding new noise or overriding the DATA PING truth layer.

Source governance:
- HIGHEST ACTIVE DATA PING VERSION WINS.
- DATA PING / current market data = truth layer.
- Chief = action lens.
- Shadow = learning.
- Consensus = de-noising.
- Claude/Grok/Research Lab = audit context only.
- GitHub archive = canonical memory.

Required classification:
- NO_ACTION
- WATCHLIST_ONLY
- PREPARE_BUY_LARGE_CAPS
- START_SMALL_LARGE_CAPS
- BUILD_LARGE_CAPS
- PULLBACK_RISK_5_7D
- TRIM_A_BID
- REBUY_WINDOW_FORMING
- NO_BUY_REGIME
- INVALIDATED

Required output block when relevant:
ALERT ROUTER
Large-cap buy window: NO / WATCH / PREPARE / START_SMALL / BUILD / INVALIDATED
5-7D pullback risk: LOW / MEDIUM / HIGH / STORM / TSUNAMI
Sell-a-bid edge: NO / SMALL_TRIM / TRIM / PROTECT
Rebuy status: LOCKED / WATCH / BTC_ONLY / LARGE_CAPS / ROTATION
No-buy regime: YES / NO
Alert state: <classification>
One-line action: <one clear sentence>

Large-cap buy window may only unlock when regime allows buying and there is persistent evidence of BTC stabilization, ETF/spot stabilization, ETH/BTC stabilization or improvement, BTC.D deceleration, breadth survival, large-cap leadership and low fake-rotation risk.

5-7D pullback warnings require confluence from RAW 5-7d downside bias, failed reclaim/rejection, flow deterioration, breadth weakness, ETH/BTC weakness, defensive BTC.D, leverage fragility or recovery-quality deterioration. Do not trigger trim on moderate pullback alone.

No-buy regime overrides all buy and rebuy outputs.

Pre-Trigger is not a buy signal by itself. It creates readiness only.

Never treat microcap-only pumps as rotation.

Keep routine states compact. Emphasize only decision-relevant changes.
```

---

## 13. Weekly operations integration

Weekly RAW Learning Snapshot should read Alert Router states as shadow learning inputs:

- whether PREPARE/START/BUILD states were useful
- whether HIGH/STORM/TSUNAMI pullback states led actual 5-7d downside
- false positives
- missed opportunities
- whether no-buy regime prevented bad entries

Master Monday should summarize Alert Router performance only if it materially changed weekly action or calibration.

GitHub Archive Sync should archive material Alert Router changes, not every routine block.

---

## 14. Archive rule

Archive Alert Router rows only when they are material:

- first PREPARE_BUY_LARGE_CAPS after a locked/no-buy period
- first START_SMALL_LARGE_CAPS
- first BUILD_LARGE_CAPS
- first HIGH/STORM/TSUNAMI pullback warning
- TRIM_A_BID
- REBUY_WINDOW_FORMING
- NO_BUY_REGIME transition
- invalidation of a previously active setup
- major false positive / false negative learning

Routine NO_ACTION and unchanged WATCHLIST_ONLY states are not archive-worthy except in weekly aggregate.

---

## 15. Boundary

The Alert Router must never:

- overrule DATA PING truth layer
- create portfolio decisions without framework action labels
- promote shadow diagnostics to official regime changes
- convert Pre-Trigger into full deployment
- use unverified ranges for scoring
- create noise by repeating unchanged states

The router’s job is to make the system feel automated by compressing complexity into the few moments where the user may actually need to act.
