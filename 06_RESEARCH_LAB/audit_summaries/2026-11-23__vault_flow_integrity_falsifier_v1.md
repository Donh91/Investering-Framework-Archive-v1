# Vault Return Integrity | independent flow-contamination falsifier v1

**Dato:** 2026-11-23  
**Status:** SHADOW_ONLY / SYNTHETIC_FALSIFIER_TESTED / NOT_PROVEN_ON_REAL_VAULTS  
**Område:** Research Lab, existing derivatives owner [#387](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/387), Research Lab [#1512](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1512) and Task 2 [#1596](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596) as potential later consumer.  
**Primary folder:** `06_RESEARCH_LAB/audit_summaries/`  
**Existing owner:** The 2026-11-11 FuturAI Hyperliquid vault source note in this folder. This is a *bounded code falsifier* for a specific missing accounting check, not a second vault research engine, scanner or statistical strategy trial.

## Narrow question

When external deposits and withdrawals are mixed into an account-value chart, can an independent offline check detect a misleading positive return or drawdown, while refusing incomplete and hindsight source evidence?

The original method, *before/after each witnessed external flow*: `subperiod return = equity_before_external_flow / previous_equity_after_external_flow - 1`. Chain these multiplicatively into a flow-neutral index. Compute an intentionally naive raw-account-value curve separately to expose the difference. Only use recorded external flows, exact same-unit equity checkpoints and timestamps known by a stated as-of clock. Require strict `equity_before + net_external_flow = equity_after`. Deposit/withdraw changes neither subperiod performance nor flow-neutral drawdown. This is NOT a reconstruction of the Hyperliquid virtual share ledger or an investor's after-all-fees realized PnL.

## First-party source basis and limitations

1. Vaults Analyser [API docs](https://vaults-analyser.com/docs): Hyperliquid vault and depositor API paths require authenticated Bearer token and a verified account. No key, API use or retained provider dataset in this test. Vendor reports `Rebuilded (TWR)` on public vault detail pages, but the reconstruction is vendor-reported, not independently audit-proven.
2. TradingStrategy.ai [vault data methodology](https://tradingstrategy.ai/docs/overview/defi-vault-data.html): native Hypercore share price is reconstructed from deposit/withdrawal history, NAV and minted/burned virtual shares, with epoch resets. Our formula checks *one simpler accounted cash-flow boundary* and cannot silently substitute for a complete virtual-share ledger, fees/lockup or intra-period unobserved flows.
3. [Hyperliquid official info endpoint](https://hyperliquid.gitbook.io/Hyperliquid-docs/for-developers/api/info-endpoint): public venue supports `vaultDetails`, but venue metadata and portfolio history alone do not constitute a deposit/withdraw-complete first-known sequence or independently executable investor return.
4. Pre-existing `2026-11-11__futurai-hyperliquid-vault-reverse-engineering__source-note.md`: already owns invisibly vetoed trades, period/strategy drift, maker-fill risk, correlated downside, flow-adjustment and the microcap non-transfer warning. Keep these findings, do not rewrite the old document or quote third-party PnL as our result.

## Implemented deterministic experiment (zero provider / paid / private data)

- `scripts/research/vault_flow_integrity_v1.py` is a standalone pure Python `evaluate(payload)` and explicit `EvidenceRefused` exception. No network, run schedule, new API or writer. It accepts only `SYNTHETIC_FIXTURE` or `UNATTESTED_RESEARCH`, and never yields live eligibility or a strategy rank.
- `tests/test_vault_flow_integrity_v1.py` tests 16 original synthetic paths: no-trade deposit, withdrawal-only fake drawdown, a genuine 10% loss concealed by flows, late backfill, impossible clock, missing cash flow, incomplete boundary, broken accounting conservation, duplicate clock, unknown fee conventions, bad numeric types/nonfinite amounts, late starting baseline, terminal bankruptcy, invalid LIVE_VERIFIED claim, recapitalisation epoch and redemption epoch.
- Command: `python -m unittest tests.test_vault_flow_integrity_v1 -v`. Local tests: **16/16 PASS** on the exact source/test bytes whose Git blobs are `eaf1ab6b79a17fe03c6e62766ab8fd839641cf29` and `801ea9acee1e17c855d9f4f01ddd964b7964ba5d`. Exact-head repository CI and independent review remain separate gates.

**Synthetic counterexample, not a real vault:** start $100, deposit $900 without trading, then portfolio falls to $900 before $800 withdrawal, ending $100. Raw-account total return: 0%; raw-account peak-to-end drawdown: 90%. With witnessed flow-neutral accounting: **-10% return and 10% drawdown**. This only validates that the simple math catches a known bookkeeping confound.

## Science, failure modes and explicit disposition

- A signed assertion that a flow boundary is complete is **not evidence of source custody**. Without immutable original source capture and complete deposit/withdraw + NAV state, outputs are `UNATTESTED_RESEARCH`. A late backfill, unsupported fee treatment, missing cash flow, malformed unit/clock, broken reconciliation, unknown epoch or no samples must ABSTAIN.
- Not computed: user-level cash flows, money-weighted IRR, net investor return after externalized fees, management/performance fee high-watermark, lockup/redeem rights, leverage/funding, actual share price, Sharpe/skill probability, allocation timing, full drawdown with unsampled interim prices, market forecast, ranking, Alpha Lab score or tradeable edge.
- The theoretical value is **avoiding false performance claims**, not proving an alpha-generating trading strategy. This is an incremental-method test only, with outcome denominator 0 real vaults and 0 prospective qualified decisions. Research classification: `STATIC_FALSIFIER_PASS / REAL_SOURCE_UNTESTED / ECONOMIC_EDGE_UNKNOWN`.
- If a future original owner makes complete lawful source-first-known deposit/withdraw and NAV evidence available, compare a **single same-vault same-period** reconstruction to a basic naive equity curve and official provider share history. If source clocks, fee accounting or withdrawals cannot be reconciled, stop rather than ranking vaults. Retain abstentions and failed/dead vaults for any later cohort test.
- Do **not** add a private datasource, new scheduled poller, wallet, custodian, automated copy trader, Vault backup coupling, price prediction, Kompas promotion, public dashboard or Alpha strategy manager. Existing P0 source completeness and paper-sellability blockers retain priority. Review the PR exact head before any merge; code publication is not run-time integration or real-world proof.
