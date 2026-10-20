# AT-SRC-0017 - Ocellus Rule Ablation and Launch Intelligence

Date captured: 2026-10-05
Status: `RESEARCH_ONLY / ARCHITECTURE_AND_METHOD_INSPIRATION / NO_EXECUTION_AUTHORITY`
Source:
- https://ocellus.app/tokens
- https://ocellus.app/launches
- https://ocellus.app/agent
- https://ocellus.app/roadmap
- https://ocellus.app/changelog
- https://ocellus.app/developers

## Source classification

Ocellus is an external crypto-token research product with:
- launch and token-state monitoring;
- wallet/creator/holder features;
- change-between-scan reporting;
- public caller tracking;
- multiple simulated paper accounts that share one opportunity stream but vary individual decision rules.

This note does not treat Ocellus performance claims, scores or wallet labels as verified trading evidence.

The strongest transferable material is experimental design.

## Primary transfer 1 - Refusal Opportunity Ledger

AUTO_TRADING already requires complete opportunity sets and no-trade controls.

Ocellus adds a useful operational detail:
record all rules that rejected an opportunity, not only the final trade/no-trade decision.

Proposed reusable research primitive:
`REFUSAL_OPPORTUNITY_LEDGER_V1`

For every decision opportunity preserve:
- opportunity_id;
- strategy/version;
- decision timestamp;
- all eligible features at cutoff;
- all gates evaluated;
- every gate returning REFUSE;
- whether each gate was the sole blocker;
- hypothetical eligibility with that single gate removed;
- actual champion action;
- matured outcome under frozen grading rules;
- cost-adjusted counterfactual outcome.

Research questions:
- Which gates genuinely remove negative expectancy?
- Which gates mostly remove winners?
- Which gates are redundant with other gates?
- Which gates have regime-specific value?
- Does a gate's benefit survive realistic costs and latency?

This is a direct extension of existing ablation, FNP and no-trade-denominator discipline.

## Primary transfer 2 - One-rule-off shadow portfolios

Ocellus' six-account experiment is a clean causal template:
same market stream, same observation time, one rule changed.

AUTO_TRADING should retain this as a general prospective evaluation pattern.

Proposed contract:
`SINGLE_RULE_SHADOW_PORTFOLIO_V1`

Required controls:
- common opportunity universe;
- common clock;
- point-in-time identical inputs;
- common fill and cost model;
- common capital convention;
- frozen champion;
- challenger changes exactly one rule;
- all variants run prospectively;
- variant definitions frozen before outcomes;
- trial counter includes failures and retired variants.

Candidate comparisons:
- entry delay / confirmation wait;
- concentration or liquidity veto;
- minimum evidence requirement;
- exit horizon;
- take-profit / stop convention;
- no-trade gate;
- regime gate;
- risk-veto threshold.

A one-rule challenger is not promoted because it has higher short-window PnL. It must improve relevant risk-adjusted metrics across enough independent opportunities and survive audit.

## Primary transfer 3 - Exit-horizon counterfactual lane

One Ocellus paper variant differs mainly by holding longer.

The reusable idea is not the exact horizon. It is to isolate exit-policy contribution from selection skill.

For a frozen entry set compare, prospectively:
- champion exit logic;
- fixed short horizon;
- fixed medium horizon;
- fixed long horizon;
- optional trailing/risk exit when already specified.

Measure:
- return after costs;
- MFE captured;
- MAE;
- giveback from peak;
- drawdown;
- time in market;
- capital occupancy;
- tail-loss contribution.

Purpose:
distinguish a good selector with poor exits from a strategy whose apparent edge comes only from a favorable holding-period choice.

## Primary transfer 4 - Refusal behavior as a first-class paper-test target

Paper evaluation should explicitly grade:
- correct trades;
- incorrect trades;
- correct refusals;
- incorrect refusals;
- opportunities refused by exactly one gate;
- opportunities refused by many correlated gates.

This prevents a strategy with excellent loss avoidance but excessive opportunity cost from being misclassified as robust.

It also prevents a permissive strategy from looking strong merely because a short sample contained many rising assets.

## Primary transfer 5 - Null-safe state and stale-data gates

Ocellus exposes scan timestamps, scan-to-scan changes and stale-source handling.

AUTO_TRADING should preserve the same principle through existing data-quality owners:

- missing is UNKNOWN, never zero;
- a delta exists only when both endpoints are observed under comparable semantics;
- stale inputs cannot silently satisfy a trading gate;
- source timestamp and decision timestamp remain separate;
- a source becoming stale is itself an operational/data-quality event.

This is a reinforcement of current governance, not a new engine.

## Launch/creator material

Ocellus also exposes creator history, graduation progress, holder concentration, wallet categories and sellability fields.

These are more directly relevant to Meme Alpha Lab than generic AUTO_TRADING.

AUTO_TRADING may consume only components that later survive Alpha Lab ablation and are represented as frozen features with clear timestamp semantics.

No Ocellus composite score or wallet label is admitted directly.

## Why this adds incremental value

AUTO_TRADING already has:
- feature ablation;
- opportunity-set reconstruction;
- false-negative accounting;
- paper/frozen-forward stages;
- baseline comparisons;
- no-execution governance.

The incremental addition is a sharper prospective causal test for decision gates:

`same opportunities + same clock + same costs + one rule changed`

combined with:

`record every refusal + identify sole blockers + mature outcomes later`.

That gives a direct estimate of what each rule earns or costs.

## Falsifiers / kill criteria

Reject or retire this methodology if:
- common-clock/common-fill construction cannot be maintained;
- variants leak information across decision times;
- too few independent opportunities make attribution meaningless;
- rule interactions dominate so strongly that single-rule ablation is misleading;
- results vanish after fees/slippage/capacity;
- challenger advantage disappears out of sample;
- experiment maintenance cost exceeds expected information value.

If interactions are dominant, move from one-rule ablation to pre-registered factorial/interaction research rather than interpreting isolated variants.

## Explicit non-transfer

Do not adopt:
- Ocellus current paper PnL as evidence;
- exact numeric thresholds;
- Ocellus risk-score weights;
- Ocellus smart-wallet labels as truth;
- proprietary analyst/skeptic prompting;
- a new parallel execution engine;
- live order authority.

## Research priority

Priority: HIGH for methodology.

Recommended owner:
existing experiment lifecycle and AUTO_TRADING governance.

Recommended next use:
apply the refusal-ledger + one-rule-off design to the first strategy family that reaches a sufficiently mature PAPER_LIVE or frozen-forward candidate set.

No new scheduler, execution adapter or capital authority is justified by this source.
