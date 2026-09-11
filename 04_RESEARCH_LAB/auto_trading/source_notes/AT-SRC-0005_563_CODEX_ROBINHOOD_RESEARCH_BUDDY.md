# AT-SRC-0005 — 563 Codex Robinhood Chain Research Buddy

Status: `SCREENED_PARTIAL`
Captured: 2026-09-11
Source type: X / prompt-engineering / research-workflow inspiration
Primary source: https://x.com/563defi/status/2097731184402759902?s=46
Author: `@563defi` / 563, Head of Research at blocmates
Evidence class: `WORKFLOW_INSPIRATION_NOT_SIGNAL_EVIDENCE`

## What is directly visible

The captured X post embeds an article/card titled:

> One Prompt to Turn Codex into your Robinhood Chain Research Buddy

The visible preview says the workflow is intended to make AI part of the research process and refers to a copy/paste three-part prompt.

A second visible post from `@hooeem` says they put the `@563defi` prompts into their agent and describes the result as a strong "shitcoin analyst". The same post says the desired presentation style is a concise bull thesis similar to `@AgentChud` bull posts.

These are anecdotal user claims about usefulness, not performance evidence.

## What is independently corroborated

563 is publicly identified by blocmates as its Head of Research and authored the July 24, 2026 article `Robinhood Chain Projects We're Watching Closely`, which performs chain-specific project research across launchpads, lending, prediction markets, tokenized-stock/meme structures, AI-agent infrastructure and execution protocols.

Reference:
https://www.blocmates.com/articles/robinhood-chain-projects-were-watching-closely

This supports the relevance of the source as a Robinhood Chain research-workflow inspiration. It does not reveal the exact three-part prompt.

## Important limitation

The full three-part prompt body was not recoverable from the supplied screenshot or current indexed web results at capture time.

Do **not** reconstruct or quote unseen prompt sections from inference.

If the original prompt body becomes publicly recoverable later, preserve it as a separate raw evidence artifact and diff it against the internal contract below.

## What we retain

1. **Chain-specific research agents beat generic token prompts as a research design hypothesis.** The agent should know the chain's explorer, liquidity venues, tokenized-asset mechanics, common launch patterns and chain-specific failure modes.
2. **Research should compile into a repeatable packet, not an improvised chat answer.** The same asset researched twice should produce comparable fields and provenance.
3. **A bull thesis is useful as an output format, not as the research objective.** Evidence collection and falsification must happen before any persuasive thesis is generated.
4. **Small-cap / microcap research needs executable-market data, contract-control checks and wallet-distribution evidence before narrative scoring.**
5. **The research agent is an upstream evidence producer.** It has no trade, portfolio or signal-promotion authority.
6. **Historical research packets should become labeled data.** Later Astra work can test which pre-decision features actually predicted forward outcomes instead of relying on memorable winners.

## Framework adaptation

The source inspiration is implemented internally as:

`04_RESEARCH_LAB/auto_trading/MICROCAP_RESEARCH_AGENT_CONTRACT_v1.md`

That contract deliberately goes beyond the visible source by adding Investering Framework governance, point-in-time evidence controls, explicit falsification, execution-risk checks and future outcome labeling.

## Astra follow-up

When Astra takes over this research track:

1. Attempt source recovery for the exact original three-part prompt.
2. Extract only components that are genuinely absent from our internal contract.
3. Test whether a structured chain-specific contract improves factual completeness, reproducibility and forward research quality versus a generic free-form LLM prompt.
4. Keep `bull thesis` generation downstream of evidence and adversarial review.
5. Never treat social praise of the prompt as trading-performance evidence.
