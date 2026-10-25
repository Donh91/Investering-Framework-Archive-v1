# Grok research — public extract of PR #65

Original artifact and hashes are bound in [packet README](../README.md). Author of source claims: Grok-labelled report. Public-extract editor: ChatGPT, 2026-10-24. This is NOT a full verbatim original; private Alpha observations, private cross-repo detail and owner-local package paths are withheld. Source conclusions below remain advisory, not ChatGPT acceptance.

## Research thesis from Grok

Reuse the existing AUTO_TRADING research vault rather than creating another coordinator/bot. Accumulate small source-bound research packets through Bridge, let ChatGPT adjudicate them, and archive accepted/modified/negative evidence in the existing Research Lab. Potential future work concerns an application or bot, but current report role is advisory research only.

Grok proposes studying Claude's E0 -> E1 research progression and thin separation of intent, deterministic governor, paper broker, ledger and kill switch. It rejects direct production adoption of the reference kernel and recognizes that internal tests do not prove safe execution or predictive edge. It supports keeping AI outside the order path and preserving current governance.

## Proposed questions, not executed work

1. **P1 Compass-to-intent specification:** document one majors baseline's frozen input fields, clock/identity requirements and NO_TRADE behavior. Grok's falsifier: reject a mapping that needs LLM choices at execution time or cannot bind inputs to a frozen specification. No executor is supplied here.
2. **P2 dry-run realism:** later compare an external dry-run approach and reference paper broker on the same synthetic input stream for idempotency, partial fill, restart and governor bypass. Product docs, rights, source versions and admission must first be verified. Grok did not conduct this comparison in the report.
3. **P3 exit-primitive teardown:** later inspect permitted public product behavior/analogues for deterministic liquidity/rug-exit hypotheses against matched controls. No proprietary copying, wallet signing, orders or bot-cloning is proposed for implementation here. No teardown was executed in the report.

## Source-reported evidence and limitations

Grok reported running the supplied kernel's 46 internal tests and the REA skill's 27 tests; this extract does not independently reproduce those runs. A separate already-public [Claude kernel negative-control note](../../../source_notes/2026-10-23__claude_run002_kernel_adversarial_replay_v1.md) records substantive unsafe-reference-kernel findings. Grok did not rerun those RT controls, verify current venue/legal/tax suitability, establish after-cost edge, or build a running E1 pipeline in this report.

## Statements requiring adjudication

The original suggests E1 posture, inbox changes and unqualified zero cost. These are source proposals/claims, not authority. Read the separate ChatGPT adjudication before using them. No original proposal here authorizes paid calls, new routines, live orders or market/scoring changes.
