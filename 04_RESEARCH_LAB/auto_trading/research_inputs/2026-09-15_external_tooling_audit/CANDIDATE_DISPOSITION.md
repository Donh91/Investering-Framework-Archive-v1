# Candidate disposition - 2026-09-15 external tooling audit

Status: NON-CANONICAL RESEARCH TRIAGE. Current-main verification wins over this document.

## Preserve for Astra

### EXTRACT / investigate
- OxfordStrat: parameter-neighbourhood / sensitivity-surface artifact, `publish the surface, not only the point`.
- Freqtrade: lookahead-analysis and recursive-analysis as correctness-test references.

### BENCHMARK
- NautilusTrader: future event-driven execution, reconciliation and fill semantics, only after upstream evidence gates survive.
- QuantConnect/LEAN: broad reference implementation only, no adoption without a unique demonstrated gap.

### P1 RESEARCH / PROVE
- `bashtage/arch`: SPA, Reality Check, StepM and Model Confidence Set versus existing BH/FDR/bootstrap/effective-N controls.
- Same-universe shuffle/null control: verify absence first, then implement only if missing.

### PARK / REJECT FOR NOW
- VectorBT
- PyBroker
- Backtrader
- Backtesting.py
- Jesse
- Zipline-Reloaded
- OpenBB
- yfinance as evidence-grade source
- Alpha Vantage
- Nasdaq Data Link
- EODHD
- Tiingo
- other alternative engines/providers unless a unique current-main gap is proven

## P0 claim

Replication-integrity/no-op findings from the source audit are not accepted as canonical facts. They are a high-priority verification target. If confirmed on current main/current execution state, repair and independent recomputation integrity outrank all tooling work.

## Governing decision

Prefer mechanism-by-mechanism extraction into existing owners. Research throughput is not edge. Faster parameter search without stronger trial accounting, null controls, leakage defenses, multiplicity handling and independent replication can reduce epistemic quality.
