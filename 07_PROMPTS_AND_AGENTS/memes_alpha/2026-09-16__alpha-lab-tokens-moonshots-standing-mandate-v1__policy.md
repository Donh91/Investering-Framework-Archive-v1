# Alpha Lab - Tokens & Moonshots — Standing Mandate v1

Status: ACTIVE / STANDING
Effective: 2026-09-16
Scope: all Alpha Lab token and moonshot research, including memes, microcaps, early tokens, mispriced assets, migrations/relaunches and special situations.

## Purpose
Alpha Lab is not meme-only. Its purpose is to identify, falsify, document and learn from tokens with potentially asymmetric risk/reward. This policy is outcome-independent and must be discoverable by future agents and threads working from the repository.

## Standing authority
The operator has granted standing authority to log and archive relevant Alpha Lab findings without requesting case-by-case approval. Agents should autonomously choose research depth according to expected information value, uncertainty, risk/reward and the possibility that deeper wallet/project work can materially change the conclusion.

## Mandatory analysis order
DATA INTEGRITY -> TOKEN/POOL -> WALLETS -> TOKENOMICS -> NARRATIVE/TECH -> CATALYSTS -> RISKS/FALSIFIERS -> R/R -> ACTION.

For new-chain and microcap assets, DATA INTEGRITY is fail-first. Verify exact CA, chain, active/canonical pool, quote asset, live DEX price, supply, market cap/FDV, liquidity and observation timestamp/source before allowing the thesis or action layer to rely on the numbers. Prefer current pool/on-chain observations over stale web-indexed aggregator values. CoinGecko/CMC and similar aggregators are cross-checks, not live authority when a fresher canonical DEX observation is available. Material conflicts must be recorded as DATA CONFLICT, never silently resolved by choosing the more convenient number.\n\nFor Robinhood Chain exact-CA cases, run bounded Blockscout enrichment after exact candidate resolution and before relying on launch-origin, contract or holder facts. In ChatGPT use the Blockscout connector when available; in repository/runtime work use `scripts/api_agent/meme_alpha_blockscout.py`, preferring runtime-only `BLOCKSCOUT_API_KEY` and allowing the governed public explorer fallback. Blockscout verifies chain facts but does not prove project ownership, current market quality or sellability.

## Mandatory pre-outcome record
For every meaningful candidate, preserve a timestamped pre-outcome snapshot before the outcome is known. At minimum, where observable, record:

- exact CA, chain and canonical/most relevant pool
- observation timestamp and source provenance
- live price, MC, FDV, supply, liquidity and relevant volume/transaction context
- holder concentration with contracts, LP, bridges, exchanges, protocol/migration wallets and EOAs classified separately where possible
- wallet-forensics observations, including accumulation/distribution, recurring-wallet clusters, provenance, overlap and cost-basis evidence where defensible
- project/product/technology thesis and evidence quality
- likely short-, medium- or long-term horizon
- catalysts and explicit falsifiers
- market-regime/context relevant to the token
- current ACTION assessment and rationale
- contemporaneous qualitative prediction or moonshot intuition, including uncertainty and the reasons that created it

The record must preserve what was knowable at the time. Do not backfill later information into an earlier prediction as though it had been known.

## Adaptive wallet forensics
Wallet research is not a fixed checklist. The agent owns the decision to go deeper when the expected information gain is high. Examples include suspicious top-holder concentration, wallets that accumulated before a move, recurring profitable cohorts, deployer/team relationships, migration flows, linked funding sources, coordinated timing, distribution into strength, or evidence that apparent whales are actually protocol infrastructure.

Raw top-holder percentages must not be treated as free-float whale concentration until known contracts/LP/bridge/exchange/protocol addresses have been separated where feasible.

## Outcome learning loop
Every sufficiently material logged case should be eligible for later review at an appropriate horizon. Compare the frozen pre-outcome thesis with what actually happened. Evaluate price/MC path, liquidity and exitability, wallet behavior, catalysts, falsifiers, project execution and market regime.

Failures are first-class evidence. Never silently discard failed calls, delete inconvenient cases, move the original baseline, or rewrite the original rationale after the outcome. A failed moonshot intuition with a well-preserved rationale may have greater learning value than a winner.

Postmortems should ask which observations were genuinely predictive, which were coincidental, which risks were underweighted, whether data integrity failed, whether wallet patterns had information value, and whether the signal only worked in a particular market regime. Convert repeated evidence into candidate reusable rules only after enough observations exist to justify them.

## Action vocabulary
Use clear operational states such as IGNORE, WATCH, DEEP DIVE and ENTRY CANDIDATE, with risk qualifiers where useful. Always state what evidence would upgrade, downgrade or falsify the current assessment. ACTION is an analytical research classification, not a guarantee of future returns.

## Anti-hindsight rule
The pre-outcome timestamp, baseline and reasoning are immutable historical evidence. Later corrections may be appended with their own timestamp, but must not overwrite what the system actually believed or observed earlier. Successes and failures must be judged against the original evidence set and contemporaneous market conditions.

## Agent handoff rule
Any future agent working on Alpha Lab / memes_alpha should read and follow this standing mandate before materially evaluating, logging or postmorteming a token. Existing narrower meme research remains valid where compatible, but this broader Tokens & Moonshots mandate governs scope and learning discipline from 2026-09-16 onward.
