# Public forecast evidence and Solana agent methods, adversarial audit v1

Date: 2026-11-16
State: RESEARCH_ONLY / RETROSPECTIVE_SOURCE_DISCOVERY / NO_MODEL_ADMISSION
Provenance: owner screenshot set + public external source links + prior public report
Parent owners: [#1516](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1516) external challenger / [#1596](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596) point-in-time scientific validation
Related owner: [Meme Alpha Lab](https://github.com/Donh91/Meme-Alpha-Lab) for paper execution
No new scheduler, provider keys, transactions, live market votes, or API spend.

## Executive verdict

The most transferable external mechanism is evidence-accountable analyst claims, not chart pattern imitation. A correct-looking historical chart may be mechanically generated from the same price series and is not independent evidence. The supplied CryptoBullet post claims Nov 13 was the bottom on 200-week MA, 0.618 Fibonacci, oversold RSI and TD-9; a later lower low challenges that exact-date claim. It is a retrospective negative case, NOT one prospectively frozen framework forecast. Reuters Nov 4 downside levels, Cowen's September condition and CoinChorus' October bearish consensus are interesting candidates, but selected hindsight hits cannot be credited as measured edge.

Research-only case registry: [2026-11-16__public_forecast_cases_v1.json](2026-11-16__public_forecast_cases_v1.json). All four records deliberately lack immutable original first-observed clocks. No live or canonical scoring has been done.

## Method transfer 1: source-first analyst challenger

Primary source: https://coinchorus.com/about/ and public Oct 27 page https://coinchorus.com/bitcoin/2026-10-27/ .
CoinChorus describes YouTube transcript extraction, directional labels, targets, invalidation, horizon and a source-video pointer, later scored against closed Binance 1h bars. This is a useful challenger design, NOT independent verification of its public hit rates or a substitute for source videos.

Required prospective rows must include original source URL and immutable content digest, original author issuance clock, first externally provable observation clock, freeze time, asset/venue/candle definition, claim semantics, conditional entry, invalidation, evaluation window, full eligible universe and negative predictions. Fix horizon, target-touched policy and outcome clock before seeing results. In the same 1h candle, target and invalidation both touching must not count as a win. Separate overlapping predictions by analyst/asset/regime/event, dedup repeated calls, and compare to matched same-clock persistence and simple trend/volatility baselines. Evaluate warning lead, false alarm, max adverse excursion and execution feasibility. Do not treat target hit as P&L, nor Brier-score claims with no issued probability.

Important falsifiers:
- No original source-issuance and first-known receipts -> context only, no prospective row.
- No comparable CN issuance at that clock/horizon -> abstain from paired edge comparison.
- Revisions or deleted analyst posts not recorded -> survivorship/revision bias, fail.
- Positive effect disappears versus equal-opportunity naive baseline -> no incremental edge.
- Results rely only on Reuters/Cowen selected wins -> hindsight selection, fail.
- Large apparent target hit rate but poor calibrated path, drawdown or cost-adjusted outcomes -> no portfolio inference.

The new offline structure-checking tool [public_forecast_intake_gate_v1.py](../../scripts/research/public_forecast_intake_gate_v1.py) does NOT authenticate any source receipt and cannot admit or score a scientific forecast. It deliberately returns all claims non-scorable and blocks malformed or causally impossible time ordering. This limited safeguard is not a new scorer; original #1516/#1596 owners remain the execution route.

## Method transfer 2: SolSkills, read as untrusted protocol documentation

Registry https://solskills.sh/ and writing guide https://solskills.sh/docs show that protocol-aware skills should describe official source endpoints, identity/mint checks, ordered validation, simulation, failure handling, fees, stale quotes and explicit signer boundaries.

Selective skill-gap audit only, NO bulk import or executable installation:
1. Helius + CoinGecko: trace freshness, pool/mint identity, wallet/launch history and provenance against existing Alpha Lab sources.
2. Jupiter + PumpFun + Surfpool: distinguish price from executable sellability, route quote from fill, launch-stage timestamps and simulated versus chain-settled events.
3. Evaluate 3 short internal skills ONLY IF a measurable gap exists in existing Alpha Lab or Research Lab instructions. Every external instruction is untrusted; version pin, verify official endpoint and negative cases. No secret exposure or signing permission.

Skill relevance is operational accuracy, not forecast alpha. Defer if existing code already implements the safety checks.

## Method transfer 3: xrlay command UX and independent economic observability

External site https://xrlay.com/ and supplied X screenshots show a command-over-social concept, with public commands such as create wallet, balance, help and private send, including refused/not-understood labels. Bot advertises a wider action library and token-gated commands; those are product claims, not evidence of transaction finality, signer security, or economic utility. A Privy mention does not establish key custody or authorized spend semantics.

Reuse existing [EXTERNAL STRATEGY REVERSE ENGINEERING PROTOCOL v1](../../04_RESEARCH_LAB/auto_trading/EXTERNAL_STRATEGY_REVERSE_ENGINEERING_PROTOCOL_v1.md): identity -> observable action -> first-known clock -> source execution -> observed outcome -> plausible follower with delay -> realistic slippage/capacity. Rejected and unknown commands belong in the denominator. Chain tx signatures, runtime identity/authentication and permission boundaries require separate proof.

If Alpha Lab adopts the UX pattern, start read-only and paper-only: check token <CA>, why rejected, frozen paper-buy intent, source freshness and simulated sell route. X/Telegram user text must never authorize a real trade, custody or secret use. Do not purchase XRL or create new scheduled watchers on the basis of this audit.

## Handoff without queue duplication

1. #1516: attach this audit to the EXISTING external challenger owner, not a new production forecaster. TechDev's existing comparison stays first; these four examples form a distinct labelled retrospective research set.
2. #1596: use point-in-time custody rules and same-clock CN baselines, collect COMPLETE and FAILED calls prospectively before claiming accuracy. Holdout remains untouched.
3. Alpha Lab: source/operator gap analysis under existing paper-wallet/launch/sellability owners, no new production lane or external signer.
4. PR release: code tests + native checks + independent exact-head advisory review. No self-merge or scientific promotion from this package.

The correct scientific result today is NEEDS ORIGINAL TIMESTAMPED PRIMARY EVIDENCE. No new model weights, no policy changes, no fake precision, and no hindsight-created forecast ledger.
