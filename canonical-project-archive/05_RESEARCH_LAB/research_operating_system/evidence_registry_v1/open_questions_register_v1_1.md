# Open Questions Register v1.1

Date: 2026-07-07  
Status: EXECUTED / ACTIONABLE OPEN QUESTIONS BOARD  
Supersedes: `open_questions_register_v1.md` as active open-question board  
Scope: Open research questions, priority, required data, owner, next action and ready-to-use prompt direction.

---

## 0. Purpose

This file tracks what is still unproven, what must not be frozen, and what research should happen next.

It is designed to prevent open hypotheses from becoming live rules through repetition.

Each open item must have:

- current status
- decision relevance
- evidence gap
- required data
- priority
- owner
- next action
- promotion criteria
- kill criteria

---

## 1. Priority framework

| Priority | Meaning | Action style |
|---|---|---|
| P0 | Blocks major governance decision or prevents misuse of live language. | Must remain visible until resolved. |
| P1 | High decision value and should be near-term research. | Prepare/run next. |
| P2 | Useful calibration, not urgent. | Queue after P1. |
| P3 | Optional/future enhancement. | Do not distract current research. |

---

## 2. Owner framework

| Owner | Role |
|---|---|
| ChatGPT governance | Build registry, ratify, archive, define constraints. |
| Custom GPT sensor | Extract and structure data only. No governance. |
| Claude/Fable research | Execute narrow tests. No ratification. |
| GitHub archive | Persistent source of truth / extended archive. |

---

## 3. Open questions board

| ID | Priority | Question | Current status | Why it matters | Required data | Owner | Next action | Promotion criteria | Kill / downgrade criteria |
|---|---|---|---|---|---|---|---|---|---|
| OQ-001 | P1 | Is Cycle Navigator weekly range skill better than dumb baselines? | OPEN. Verified weekly actuals exist partially, but no systematic skill audit. | Public credibility and forecast usefulness depend on this. | Weekly forecasts, actual BTC/ETH highs/lows, prior-week range, ATR baseline, score. | ChatGPT inhouse first, Claude later if dataset ready. | Build forecast/actual table and run baseline comparison. | Beats prior-week/ATR baseline on containment, width efficiency, breach direction and Jaccard. | Does not beat dumb baselines or score has no relation to outcomes. |
| OQ-002 | P1 | Does ETH/BTC persistence validate 0.0275 and 0.0300 gates? | UNTESTED. 0.0275 is reclaim pressure only. | Rotation language depends on this. | Direct ETHBTC daily pair preferred; same-source ETH/BTC fallback. | Claude/Fable after data prep. | Run E2 ETH/BTC persistence test. | 1/2/3-close persistence improves false reclaim profile and forward ETH/BTC outcomes. | No improvement vs baseline or thresholds unstable across regimes. |
| OQ-003 | P1 | Can ETF stabilization formula be frozen? | OPEN. Farside BTC flow ingestion succeeded, formula not tested. | ETF flow is a current main blocker and must be separated from single print noise. | Farside BTC/ETH daily flows, trailing flow windows, BTC OHLC. | Claude/Fable. | Run ETF regime/stabilization study. | Stable trend/streak feature improves state classification or reduces false recovery. | Formula is window-sensitive, overfit or not better than simple net-flow baseline. |
| OQ-004 | P1 | Would v0.2 improve actual historical framework decisions in replay? | Supported mechanically by P1/P1b, not replayed against actual DATA PING rows. | Gate can be mechanically good but operationally noisy. | DATA PING rows, BTC OHLC, ETF flow, state labels. | ChatGPT inhouse replay. | Run no-hindsight daily replay for 2026-06-02 to 2026-07-02 first. | Reduces false deaths/churn without delaying true breakdown. | Adds confusing state churn or does not improve over binary baseline. |
| OQ-005 | P1 | Does FNP ledger improve decisions without creating rebuy pressure? | FNP prior supported, live replay untested. | FNP must reveal waiting cost without becoming emotional signal. | Historical lows, permitted entries, live state rows, outcomes. | ChatGPT inhouse replay. | Add FNP Meter A/B to replay rows. | Tracks cost accurately and improves governance awareness. | Causes premature action framing or unstable cost estimates. |
| OQ-006 | P1/P2 | Are funding/OI/leverage thresholds decision-useful? | DATA-CONSTRAINED. | Needed to distinguish squeeze from genuine repair. | Historical funding, OI, long/short and liquidation data. | Custom GPT source search first, Claude later. | Find viable historical source; do not test until data exists. | Leverage features improve false recovery classification. | Historical source unavailable or feature adds noise. |
| OQ-007 | P1/P2 | What separates Rotation Watch from Rotation Confirmed? | Not empirically validated. | Prevents false altseason/rotation language. | ETH/BTC, breadth, BTC.D, deployment proxy, ETF/flow. | ChatGPT spec then Claude. | Define matrix and test components separately. | Matrix reduces false rotation calls and improves forward alt/ETH outcomes. | No component adds predictive or classification value. |
| OQ-008 | P2 | Does breadth rescue close-persistence when ETF flow did not? | UNKNOWN. | 2/3-close may still be useful under breadth, but this is not proven. | Historical breadth proxy. | Data sourcing first. | Identify breadth proxy and run E3-breadth. | N=2/3 improves only in breadth-positive regime. | Same result as ETF-flow: no rescue or inverted signal. |
| OQ-009 | P2 | Does stablecoin supply / TVL improve liquidity regime classification? | SOURCE-MAPPED only. | Could improve macro-liquidity and risk appetite context. | DeFiLlama stablecoin and TVL daily series. | Claude/Fable later. | Run E12 liquidity feature study. | Adds stable regime classification beyond price/ETF. | No incremental value or large lag/noise. |
| OQ-010 | P2 | Does DATA PING output compression preserve critical information? | Rule exists, not audited. | Compression must not hide main blocker or state/rebuy status. | Sample DATA PING outputs before/after compression. | ChatGPT inhouse. | Output audit. | State, rebuy, blocker and flow line always preserved. | Any critical line repeatedly disappears. |
| OQ-011 | P2 | Is the Cycle Navigator displayed score meaningful? | Unknown. | Public score should not be cosmetic. | Score history, forecasts, actual outcomes. | ChatGPT inhouse. | Score reliability audit. | Score correlates with containment/baseline delta. | Score is unrelated to actual forecast quality. |
| OQ-012 | P2/P3 | Does perp/spot wick-gap add signal? | Diagnostic-only today. | Could improve flush/stress detection. | Same-time spot/perp OHLC, wick gaps. | Claude later if data exists. | Dedicated E9-style wick-gap test. | Adds stress signal without corrupting canonical lows. | Overfit or no stable effect. |
| OQ-013 | P3 | Do options/Deribit signals improve squeeze/gamma context? | Not tested. | Potential context layer, not core. | Deribit IV/skew/OI/options chain history. | Later only. | Defer. | Improves squeeze classification. | Paid/complex data with low incremental value. |
| OQ-014 | P3 | Should FRED/macro become part of DATA PING? | Source-mapped only. | Useful broad regime, lower direct gate relevance. | FRED liquidity/rate/yield series. | Later. | Defer until core replay works. | Adds regime stability. | Distracts core model or adds slow lag. |
| OQ-015 | P1 | Is highest DATA PING version always discoverable in GitHub/archive? | Rule active, automation reliability unknown. | Prevents stale source-governance errors. | DATA PING manifest/index. | ChatGPT inhouse + Custom GPT sensor. | Build version manifest. | Highest active version can be auto-found. | Manual ambiguity persists. |

---

## 4. Immediate action queue

### Action 1 — Cycle Navigator Range Skill Audit

Priority: P1  
Mode: inhouse first  
Reason: likely highest archive-value because weekly forecasts and actuals already exist across many files.

Required first output:

- `cycle_navigator_forecast_actual_manifest_v0_1.md`
- `weekly_range_skill_audit_spec_v0_1.md`

Do not send to Claude until forecast/actual rows are structured.

### Action 2 — No-Hindsight Daily Replay v0.1

Priority: P1  
Mode: inhouse  
First window:

`2026-06-02 to 2026-07-02`

Reason:

This is the window directly touched by P1/P1b, v0.2, 59.0K, FNP and ETF flow.

Required first output:

- daily replay row schema
- current-window row template
- rule_helped/rule_hurt logic

### Action 3 — Custom GPT Data Supplement

Priority: P1  
Mode: Custom GPT sensor only

Use:

`custom_gpt_data_request_prompt_v1.md`

Purpose:

Extract structured manifests for DATA PING, Master Monday, Cycle Navigator and verified weekly actuals.

### Action 4 — Claude/Fable E2 ETH/BTC Test

Priority: P1, but only after data is ready.

Do not run until direct or same-source ETHBTC series exists.

---

## 5. Ready-to-use prompt direction: Claude E2 ETH/BTC

Use only after ETHBTC data source is ready.

```text
You are Claude/Fable Research Lab.

Task:
Run E2 ETH/BTC persistence test for the Investering Framework.

Scope:
- ETH/BTC daily data only.
- Test 0.0275 and 0.0300 gates.
- Test 1/2/3 close persistence.
- Separate reclaim attempt, Rotation Watch and Rotation Confirmed.
- Do not validate altseason without breadth/deployment matrix.

Required outputs:
- source manifest
- data gaps
- hit/whipsaw rates
- forward ETHBTC returns
- forward ETH and BTC relative returns
- false reclaim rate
- regime split
- negative controls
- recommendation rows

Rules:
- no hindsight
- do not invent missing data
- derived ETHBTC must be labeled derived
- direct pair preferred
- result is non-binding
- no portfolio action
```

---

## 6. Ready-to-use prompt direction: Claude ETF Stabilization

Use after Farside BTC/ETH flow files are canonicalized.

```text
You are Claude/Fable Research Lab.

Task:
Run ETF stabilization regime study for the Investering Framework.

Scope:
- Farside BTC ETF flows, and ETH ETF flows if available.
- Align flows to BTC OHLC.
- Separate ETF print, ETF trend, ETF streak and ETF improvement.
- Test whether ETF stabilization improves Recovery Attempt / Recovery Confirmed classification.

Required tests:
- 1-day print vs trailing 3/5/7/10 day trend
- negative streak ending
- improving but still negative flow
- nonnegative flow
- strong positive flow
- interaction with BTC reclaim levels

Required outputs:
- source manifest
- flow regime definitions
- negative controls
- forward return / drawdown outcomes
- framework recommendation rows

Rules:
- ETF-era only
- no hindsight
- no formula freeze unless robust vs simple baseline
- non-binding
- no portfolio action
```

---

## 7. Ready-to-use prompt direction: Custom GPT sensor

Use the existing file:

`custom_gpt_data_request_prompt_v1.md`

Custom GPT must only collect and structure data.

It must not ratify rules.

---

## 8. Promotion and freeze rules

A rule may be promoted only if:

1. It has a clear data source.
2. It passes fabrication/sanity gates.
3. It beats relevant dumb baseline.
4. It survives negative controls.
5. It has known failure modes.
6. It has a layer assignment: LIVE, LEDGER, GOV or SHADOW.
7. It has explicit kill criteria.

A rule must stay shadow-only if:

- data is missing
- sample is too small
- it is regime-specific only
- it fails baseline
- it cannot be replayed without hindsight
- it risks portfolio action leakage

---

## 9. Current “do not freeze” list

Do not freeze these yet:

- ETH/BTC persistence counts
- Rotation Confirmed matrix
- ETF stabilization formula
- breadth thresholds
- leverage thresholds
- stablecoin/TVL trigger
- Cycle Navigator score methodology
- options/gamma trigger
- macro trigger

---

## 10. Current “safe to use” list

Safe to use with caveats:

- v0.2 hybrid gate as BTC-tier state-gate
- 59.0K hard-death with tight-buffer annotation
- FNP ~9% [7-12] as ledger prior
- 2/3-close as discipline only
- ETF flow status line as mandatory output context
- highest DATA PING version wins
- LIVE/LEDGER/GOV/SHADOW output split

---

## 11. Final status

This v1.1 register is the active open-questions board.

It should be reviewed before any new Fable/Claude prompt or Custom GPT data request is launched.
