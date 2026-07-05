# FABLE 5 RESEARCH — P1b STATUS / INTERRUPTED RUN

Date: 2026-07-03  
Status: P1b approved, guardrails locked, execution interrupted by Fable usage limit  
Archive classification: Research execution state / pending continuation  
Folder: `/canonical-project-archive/05_RESEARCH_LAB/fable_research/p1b_ohlc_flow_upgrade/`

---

## 1. Context

Fable 5 Research P1 v0.2 was accepted as an executed close-only research artifact.

P1 v0.2 produced three important governance outcomes:

1. **E3 Close-Persistence Doctrine**
   - Result: NOT SUPPORTED as price-edge.
   - Governance impact:
     - Keep 2/3-close doctrine as ratified discipline only.
     - Do not describe it as historically proven.
     - Cap persistence at N <= 3 unless future flow-conditioned testing proves otherwise.

2. **E5 Hybrid Gate Integrity**
   - Result: SUPPORTED on close-only data.
   - Governance impact:
     - v0.2 hybrid soft-breach / hard-death design remains supported.
     - Hard-death level 59.0K is operationally ratified with medium confidence.
     - OHLC re-test remains required.

3. **E8 FNP Monte Carlo**
   - Result: SUPPORTED as measurement.
   - Governance impact:
     - Old 5-7% FNP opportunity-cost heuristic is replaced by approximately 9% [7-12], p90 approximately 12%.
     - This is ledger-prior only.
     - It is not a rebuy signal.
     - It does not authorize portfolio action.

Current standing rules remain:

- REBUY: LOCKED
- v0.2 can classify and measure, but cannot buy
- no portfolio action
- no official v0.2 row until final freeze exists
- FNP is measurement only
- 2/3-close is discipline, not proven alpha

---

## 2. Why P1b Exists

P1 v0.2 was useful but limited.

Its main limitation was that it used BTC close-only data:

- no true high / low
- no true ATR14
- no wick / sweep validation
- no historical ETF flow conditioning
- no ETH/BTC ingestion
- no breadth / funding / OI history

Therefore, P1b was approved to upgrade the evidence quality.

The goal of P1b is not new theory.

The goal is to move from:

`CLOSE-ONLY evidence`

toward:

`OHLC / FLOW-conditioned evidence`

---

## 3. Approved P1b Scope

P1b scope is narrow and locked.

### Priority 1 — E5-OHLC

Purpose:  
Re-run the hybrid gate test using real OHLC high/low and real Wilder ATR14 instead of close-only ATRproxy.

Primary question:  
Does v0.2 hybrid gate still beat v0.1.1 binary-death design when wick/high-low behavior is included?

Required outputs:

- binary vs hybrid deaths
- false deaths
- re-freezes
- probation days
- extra adverse move
- whether wick-driven deaths reverse ranking
- whether the 0.5-1.0 ATR hard-death band still holds
- whether 59.0K remains defensible

Governance relevance:  
This directly tests whether 59.0K hard-death and the hybrid gate design remain valid after OHLC upgrade.

### Priority 2 — E3-FULL

Purpose:  
Re-run close-persistence doctrine with ETF / spot-flow conditioning if Farside ingestion succeeds.

Primary question:  
Does 2/3-close persistence gain value only when ETF / spot-flow improves?

Required subsets:

- ETF negative
- ETF neutral / non-negative
- ETF improving
- ETF unavailable

Required output:

- whether 2/3-close doctrine remains only governance discipline
- whether it becomes empirically stronger under flow-positive conditions
- whether flow-negative regimes explain prior weak E3 result

Governance relevance:  
This tests whether close-persistence is useless as price-edge generally, or only useless without flow conditioning.

### Priority 3 — E8-FULL

Purpose:  
Update FNP opportunity-cost estimates with ETF / flow-conditioned environments if data alignment permits.

Required outputs:

- METER_B median
- p75 / p90
- false-negative count
- flow-negative vs flow-neutral/positive cost
- whether the new ~9% [7-12] FNP prior holds

Governance relevance:  
This tests whether the new FNP prior should remain ~9% [7-12] or be regime/flow-conditioned.

---

## 4. Approved Data Source Priority

P1b data priority was approved as:

1. **FMP eod-full OHLC**
   - Sanctioned fallback if Binance / Kraken cannot be used.
   - Must be logged as FMP composite OHLC, not Binance primary.

2. **Farside ETF flow**
   - Used for ETF / spot-flow conditioning.
   - Can be scrape/reference style if logged clearly.

3. **Binance Futures funding / OI**
   - Only if historical access is available.
   - Otherwise mark DATA-CONSTRAINED.

4. **DeFiLlama stablecoin / TVL**
   - Useful for later E12 / liquidity context.
   - Not required for P1b core.

5. **ETH/BTC direct pair**
   - Relevant for E2 later.
   - Not required for P1b core unless added cleanly.

Do not expand P1b into options, macro, DEX, sentiment or paid on-chain tools.

---

## 5. What Happened in the Interrupted Run

Fable received the P1b GO and locked the guardrails.

The run began with the approved execution order:

1. OHLC source first
2. Farside attempt second
3. experiment engine after ingestion

Fable attempted to use Kraken as exchange-primary OHLC source first, but the Kraken fetch failed / was blocked.

This is consistent with earlier source-health warnings that Kraken was unreliable or stale for current-window work.

Fable then planned to fall back to FMP-full OHLC, as approved.

Execution was interrupted before completion because the Fable usage limit was reached.

Screenshot status:

- P1b GO received
- guardrails locked
- OHLC source first
- Kraken attempt failed
- fallback path still pending
- run must resume after Fable limit reset

---

## 6. Current P1b Status

Current status:

`P1b APPROVED / EXECUTION STARTED / INTERRUPTED BY FABLE LIMIT`

Not completed.

No P1b results are ratified yet.

No new parameters should be frozen from the interrupted run.

No changes to rebuy, v0.2, FNP, path-weight or close-persistence doctrine should be made until P1b produces executable outputs.

---

## 7. Governance Constraints During Pause

Until P1b completes:

- Rebuy remains LOCKED.
- v0.2 remains BTC-tier state-gate only.
- v0.2 cannot buy.
- 59.0K hard-death remains operationally ratified, but OHLC retest is still pending.
- FNP prior remains ~9% [7-12], p90 ~12%, ledger-only.
- 2/3-close doctrine remains ratified discipline, price-edge unproven.
- No portfolio action.
- No rotation confirmation.
- No recovery confirmation from P1b until actual results exist.

---

## 8. Required Continuation Prompt When Fable Limit Resets

When Fable becomes available again, resume P1b with this instruction:

```text
Continue P1b from the interrupted run.

Do not restart broad research.

Do not expand scope.

Use the existing guardrails.

Execution order:

1. Try approved OHLC source.
2. If Kraken failed or is stale, use FMP eod-full OHLC as sanctioned fallback.
3. Run E5-OHLC first.
4. Attempt Farside ETF-flow ingestion.
5. If Farside succeeds, run E3-FULL and E8-FULL with flow-conditioned subsets.
6. If Farside fails, return fetch-fail and partial OHLC-only results.
7. Return only P1b outputs.

Mandatory deliverables:

- short report
- experiment_results.json
- experiment_results.csv
- source_manifest.csv
- missing_data_report.md
- framework_recommendation_rows.md

Mandatory labels:

- FULL-GRADE
- PARTIAL-GRADE
- OHLC-GRADE
- CLOSE-ONLY
- PRICE-ONLY
- DATA-CONSTRAINED

Do not produce a new broad theory report.
```

---

## 9. Archive Conclusion

P1b is now the correct next research step.

The framework should not request more theoretical Fable research until P1b completes or fails with a precise runtime/data checklist.

The key open empirical questions are:

1. Does v0.2 hybrid gate still outperform binary death with true OHLC and real ATR?
2. Does 59.0K hard-death remain defensible after OHLC retest?
3. Does close-persistence gain empirical value when ETF / spot-flow is non-negative?
4. Does the ~9% [7-12] FNP prior hold under flow-conditioned testing?

Until then, the current ratified state remains unchanged.

Final status:  
P1b pending continuation after Fable limit reset.
