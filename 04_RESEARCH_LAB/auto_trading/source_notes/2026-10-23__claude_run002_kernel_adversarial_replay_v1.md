# Claude AUTOTRADING RUN-002 — independent kernel negative-control replay

**2026-10-23 | RESEARCH_ONLY / OWNER-APPROVED / NO_EXECUTION / NO_NEW_ENGINE.**
**Owner:** existing `04_RESEARCH_LAB/auto_trading` under its binding `GOVERNANCE.md`. Related: trial-count integrity [#1557](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1557), experiment lifecycle #885, Research Lab method PR [#1762](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1762), Task 2 scientific #1596, Supervisor #1156. This note is the smallest durable *source audit and test specification*, not an installation, code merge, broker decision, trading system or new standing experiment.

## Source integrity, exact local tests, limitations

- Owner-supplied `AUTOTRADING_OG_REA_SKILL_2026-10-21.zip` SHA-256 `cffdcd8b0bccaf04ba26b40ded3f7045b2f680aa9e36683cb617bf04f8c6e1fc`. The file stays out of the public repository.
- Owner-supplied `crypto-product-rea!.zip` SHA-256 `41a44ff23d2f1fd28a5380b6d1c7ee402beabca98404a530bfe20abcc78fdebb`, identical to earlier REA copies. Included REA material in composite pack is the same skill, not a separate service/skill version.
- In isolated offline Python sandbox, unchanged `A_AUTO_TRADING_RUN-002/08_REFERENCE_KERNEL` tests: **46/46 pytest PASS**; standalone REA `tests/test_skill.py`: **27/27 unittest PASS**. These are internal contract tests, *not* evidence of broker execution correctness, live safety or predictive edge. Source files were inspected; unbundled upstream projects and all vendor terms were **not** re-audited.
- Independent local negative-control replay called the unchanged Python objects and returned the exact observed outcomes below. No exchange call, wallet, live credentials, network, orders or provider data were used. A synthetically issued paper `Fill` is not a real trade.
- Severity P0/P1 is **conditional if such a kernel were promoted to an execution boundary**; it is NOT a claim of an active Framework production P0 incident.

## Reproduced negative controls (unchanged user-supplied reference kernel)

| ID | Risk if an execution component | Deterministic input / observed output | Suspect module | Required eventual proof |
|---|---|---|---|---|
| RT-01 | P0 invalid limits | `Limits.validate()` accepted `max_daily_notional=-1`, `max_daily_orders=-1`, `cash_buffer_pct=-50` and `max_gross_exposure_pct=1000`. | `risk_governor.py` | All limits finite, bounded, cross-field coherent and bound to authentic host policy. |
| RT-02 | P0 unknown strategy approval | `strategy_id=NOT_REGISTERED_ANYWHERE`, 64-zero spec hash, `source_refs=[madeup:ref]` yielded `APPROVE` for otherwise valid BTC/EUR buy. | `intent.py`, `risk_governor.py` | Frozen allowed strategy ID + matching authentic spec blob, sources and original decision clocks verified, not just 64-hex syntax. |
| RT-03 | P0 inability to exit | SELL 0.1 BTC with 0.1 BTC held at EUR 80,000, `max_order_notional=500`: `SHRINK` to **0.00625 BTC**, i.e. 6.25% of intended exit. | `risk_governor.py` | Separate, verified reduce-only exit path without short/oversell, authorization bypass, unreal fills or spurious size ceiling. |
| RT-04 | P0 approval-execution disconnect | `PaperBroker.execute(intent, qty=1 BTC, ...)` issued a synthetic paper fill for 1 BTC without a matching governor-approved exact decision. | `paper_broker.py` | Consume-only bound approval token for exact venue/asset/side/qty/limit/TTL/account; no direct broker bypass; enforce at every adapter. |
| RT-05 | P1 stale other-asset prices | A BTC buy with ETH held and a numeric ETH mark but **no mark timestamp** yielded `APPROVE`. | `risk_governor.py` | Per-position clock/quote/source/health checks before exposure arithmetic. |
| RT-06 | P1 mixed buy/sell daily counting | `record_sent()` on 0.005 BTC SELL at EUR 80,000 changed `day_notional` by EUR 400 though buy cap enforcement consumes that counter. | `risk_governor.py` | Separate executed and reserved buy/sell budgets with atomic reconciliation and partial-fill handling. |
| RT-07 | P1 no externally proven history custody | Deleting the final complete entry of the local hash-chained ledger can leave `verify()=True` if no independently sealed checkpoint exists. | `ledger.py` | Immutable externally anchored sequence/head, antirollback, crash-safe durable writes and broker-level reconciliation. |
| RT-08 | P1 kill-state deletion semantics | `is_halted(nonexistent_path)` returned `False`; the file design cannot distinguish intentional first-time initialization from deletion. | `kill_switch.py` | Persistent fail-safe capability/grant state; test corrupted/deleted flag, host restart, network partition and authenticated resume. |
| RT-09 | P1 synthetic marks can distort equity | `apply_fill()` may value other positions using the current fill price when their mark is missing. | `paper_broker.py` | Per-asset mark health and consistent quote conversion, no fallback to unrelated asset price. |
| RT-10 | P1 no guaranteed atomic approval identity | Idempotency/account counters are in a memory-only State, not a documented atomic order reservation/acknowledgement protocol. | `risk_governor.py` | Restart, concurrent intent, timeout/unknown-submit, duplicate, delayed partial fill, exchange cancel and replay regressions. |
| RT-11 | P1 not comprehensive tax custody | `FifoLots` is a simplified calculation primitive, not reconciliation of all wallets, crypto-crypto exchanges, fees, transfer and currency vintages. | `ledger.py` | External accounting owner/legal method verification, no false blanket tax compliance. |
| RT-12 | P1 external adapter bypass remains unproven | No shown Freqtrade/native broker binding guarantees that all REST/manual/force commands pass governor. | future adapter only | Adversarial bypass proof before even a proposed external paper/live boundary. |

Reproducibility: source ZIP, file paths, fixed `NOW=2026-10-21T12:00:00Z`, BTC/EUR limit EUR 80,000, bid/ask EUR 79,990/80,010, local stdlib Decimal fixtures. Exports/logs above contain only synthetic inputs/results and no user accounts.

**Important nuance:** RT-07 and RT-10/12 are architecture/invariant deficits rather than proof of an observed exploit in running production; RT-01..06 and RT-08 are directly reproduced module outcomes. RT-09/11 are source-code contract/readiness findings. Do not count these twelve as twelve independent live failures.

## Framework-native disposition

1. **ADOPT CONCEPTS:** AI as bounded research/adversarial author; deterministic source/timestamp validation, no-trade and risk veto; complete trial denominators, negative evidence and future read-only audit receipts.
2. **REJECT DIRECT ADOPTION:** no import of the ZIP kernel into `main`, `Compass`, API gateway, execution handler or scheduler. No new `trader-skill`, Freqtrade service, Telegram approval system, trading API key or persistent host from this mandate.
3. **REUSE/DEDUPE:** current `AUTO_TRADING/GOVERNANCE.md`, E1/E1X leakage validation, existing #885/#911 research outcomes, sequential one-stage shadow queue and #1557 proposal-time global trial count. The latter is a **separate P1 blocker**, not solved by a kernel or strategy simulator; do not create `AT_TRIAL_LEDGER_v2` by default.
4. **TASK 2 FIREWALL:** #1596 owns R0-R7; this kernel supplies **no R1 PIT admission, R2 information gain, R3 action utility or reason to expand Task 2**. Retain original acceptance and blocked evidence states.
5. **CONDITIONAL FUTURE TEST:** only if an independently selected, source-admissible, preregistered economic hypothesis survives simple same-clock after-cost baselines, return to these RT controls as an offline research rubric. A prospective paper adapter is a separately gated owner choice; a live trade is an entirely separate explicit authorization.
6. **SUPERVISOR HANDOFF:** hand off this immutable source note via PR #1762, require exact-head CI/review/branch rules and postmerge blob readback before `ARCHIVED_ON_MAIN`. Existing #1557 owner may derive a bounded census from immutable receipts; do not imply the count is already fixed. No new actions spend while October GitHub-minutes status is constrained.

**Terminal verdict:** `RESEARCH_METHOD_ADOPT / KERNEL_NOT_PRODUCTION_SAFE / NO_EXECUTION_COMPONENT / NO_PREDICTIVE_EDGE_PROVEN`. Negative controls are useful whether or not the kernel is ever implemented. This evidence does not change current market state or authorize trading.
