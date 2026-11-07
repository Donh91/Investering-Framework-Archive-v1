# L05, L06 companion | Independent historical balance-seizure evidence, OPTIPEPE
**Date:** 2026-11-08 Europe/Copenhagen
**Source classification:** `HISTORICAL_ONCHAIN_NEGATIVE_CONFIRMED / NOT_PROSPECTIVE / NOT_PREDICTIVE_LIFT`
**Owner:** existing Research Lab #1512, implementation/test at original Meme Alpha #98/#194, original [draft PR #200](https://github.com/Donh91/Meme-Alpha-Lab/pull/200).
**Execution:** Direct first-party Blockscout read-only source and three Ethereum transaction lookups during this ChatGPT interaction. No new GitHub workflow, no paid API, no code or deployed scanner change, no token purchase, no signing.

## Why this is important
An actual contract can be fully source-verified, have apparently benign buy/sell-tax and generic honeypot fields, and still allow a privileged origin to transfer unrelated holders' *token balances* due to an allowance-order bypass. This is a different risk category from an unsellable swap route. The protective question is whether the original Alpha S1/security surface can prove or abstain on **privileged transfer**, not whether a provider marketing score looks green.

## Original on-chain verification
- Chain: Ethereum mainnet, `chain_id=1`.
- Exact token: [OPTIPEPE `0x434D77C660c39bD2c4A2230b7E8D66dEC9f8c458`](https://eth.blockscout.com/address/0x434D77C660c39bd2c4a2230b7e8d66dec9f8c458?tab=contract), **fully verified** Solidity 0.8.23, flattened source `contracts/sample_flattened.sol`, no proxy according to Blockscout, verified `2026-10-28T23:12:46.908768Z`. "Verified source" is not "safe source."
- The verified source declares `isExile[msg.sender]=true` in constructor; `MAxTradingIdentifierLimits(from)` executes decorated transfer logic and then tests `isExile[tx.origin]`, invoking `returnTx()` with assembly `mstore(0, 1); return(0, 32)`. `transferFrom(from,to,value)` executes `_transfer(from,to,value)` **before** `_spendAllowance(from,spender,value)`. The creator-origin `RETURN` exits the token call frame after balance movement and before allowance validation. The RETURN is *not* termination of the whole parent transaction.
- [Verified successful direct creator transaction A](https://eth.blockscout.com/tx/0xe012b8c4c39717e343ecd06f1f9362853fae7a728f2ca4fc426e17c40ad0e028), `2026-10-29T12:27:59Z`: EOA `0x9014b03eD462D9056817105de3f3c20a03f703D1` calls decoded `transferFrom(other-holder, 0x...dEaD, amount)`. Token Transfer event confirms other holder -> dead.
- [Verified successful direct creator transaction B](https://eth.blockscout.com/tx/0x5e69708284fd1396bd3699015e0e067e2a05ea6735247575f015f5421f70e471), same second: another holder's token balance -> dead.
- [Verified helper transaction C](https://eth.blockscout.com/tx/0x038d5abb8bc27fd96726b23313cd327df5fbdb5f1f233a4eda72e1c25320b183), `2026-10-29T05:47:11Z`: creator calls helper `multicall` with token and holder array; resulting token transfer from selected holder -> dead.

This is **independent corroboration** of a portion of the existing [Alpha #200 forensic](https://github.com/Donh91/Meme-Alpha-Lab/pull/200). The prior claim of 24 transactions/27 addresses was **not** independently re-enumerated in this session. We did not inspect historical allowance storage for each holder, run a Foundry fork, or prove any **pre-harm** deployed alert. Successful creator-origin transfer from unrelated addresses and verified source control flow establish a strong public negative security case; the fork test remains necessary as a portable automated detector test.

## Distinct risk claims, not conflated
| Claim | Present status |
| --- | --- |
| Creator-origin transfer of another address's OPTIPEPE to dead | **VERIFIED**, three first-party tx reads and verified source path |
| GoPlus static label may look benign despite a privileged transfer bypass | **SOURCE-BACKED PRIOR CLAIM**, exact original API timestamp and normalized field payload need independent pair to establish same-clock false SAFE |
| All no-allowance holders were vulnerable at every block | **NOT COMPLETELY REPLAYED**, original control-flow evidence plus three successful transfers, historical state differences possible |
| Creator could steal a holder's unrelated ETH/USDC | **NOT SUPPORTED**; this is token-specific balance behavior |
| Alpha could have warned prospectively before creator behavior | **UNPROVEN**, past chain events do not establish first actual machine-observed timestamp |
| A new detector has measurable sensitivity/specificity/financial upside | **UNPROVEN**, no detector implementation, full denominator, controls or valid forward tests |

## Hypothesis, frozen baseline and falsifier for original S1
`HYPOTHESIS:` privileged transfer-return-path static/fork recognition catches otherwise apparently SAFE token balance-confiscation cases before action, without rejecting ordinary authorized ERC20 transfers or legitimate contract admin semantics.

- Native baseline: existing Alpha `scripts/sellability_provider_challenger_v1.py`, `scripts/sellability_cohort_v1.py`, #98 and #194 native exact-CA/security logic.
- Challenger: minimal original-owner AST/SlithIR detector for reachable late assembly RETURN and skipped allowance, with origin/role predicate, plus pinned historical fork simulation for independent holder `allowance=0`.
- Required negative controls: clean OpenZeppelin ERC20, normal user-approved transferFrom, false-positive safe tx.origin references, legitimate administrative freeze/blacklist semantics, unauthenticated caller, separate proxy and v4 hooks. Require matched rugs/nonrugs including low-liquidity untradeable cases.
- `KILL` as an independent new feature if all useful detections are already achieved by native S1/contract-authorization proof, if legitimate controls are falsely hard-vetoed, or if a true first-known signal cannot be produced before harm. Retain an adversarial regression fixture irrespective of predictive lift.
- No automatic threshold, buy, portfolio or alert changes. This finding remains research-only until original independent technical and CI tests and safety/admission gates.

## Current owner proof and handoff
- Native source-and-transaction readback summarized in [Alpha PR #200 issue comment #6714309009](https://github.com/Donh91/Meme-Alpha-Lab/pull/200#issuecomment-6714309009), with a compact [issue #98 handoff](https://github.com/Donh91/Meme-Alpha-Lab/issues/98#issuecomment-6714309350).
- **RETAIN:** original contract/tx trace as historical negative regression reference (not predictive credit).
- **MODIFY CANDIDATE:** add smallest original-owner detector regression *only* after fork/static tests, source rights, deterministic negative controls, and authorized CI readiness.
- **KILL:** generic "green tax/honeypot = safe token" semantic. This is a falsified safety inference, not proof of any particular vendor intentionally misleading users.
- **Next actual trigger:** confirmed source/code version and current Alpha #98/#194 source owner can run safe historical fork + static source test in available existing Actions budget, and Strategist #1157 decides independent decision usefulness. Never use Round3 restricted prospective payloads while its analysis gate is closed.

No real jobs, GitHub API executions, autonomous S1 merges or production scanner improvements are claimed by this L05 source receipt.
