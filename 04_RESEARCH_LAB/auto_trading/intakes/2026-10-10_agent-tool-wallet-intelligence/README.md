# External Agent, Wallet Intelligence and Trading Tool Intake, 10 October 2026
artifact_id: RL-AT-20261010-EXTERNAL-INTAKE-001
maturity: RESEARCH / ADJUDICATION PROPOSAL / TEST DESIGN
authority: NONE
execution: FORBIDDEN
promotion: NONE
parent: 04_RESEARCH_LAB/auto_trading/README.md
scientific: existing lifecycle and issues #937, #1512, #1557
Claude companion: Donh91/Investering-AI-Audit-Bridge, programs/claude_auto_trading_research/runs/2026/10/2026-10-10T101034Z_RUN-001_FOUNDATION_RESEARCH/
Source snapshot: main 5f083e867b4907aae524889fb0ab9e3b11b4106a (10 October 2026)
Owner mandate: research, reverse engineering, critical screening and agent handover; **not** capital-execution promotion.

## Executive decision
**KEEP existing owners; attach a handful of falsifiable challengers.** The framework already has a reverse-engineering protocol, external-alpha owner #937, Meme Alpha Lab research lanes, Blockscout enrichment, Research Lab Red Team, agent skills and action/evidence ledgers. Therefore do NOT launch another supervisory agent, trading bot, private wallet crawler, market-state engine or scheduler.

| Rank | Finding | Existing owner | Decision | Proof needed |
|---|---|---|---|---|
| P0 | **Blockscout v12.0.0 compatibility** published for 7 Oct 2026: cursor/params, source args, JSON-RPC errors, optional RPC methods, token filtering | existing Blockscout API + secrets collector; #1512 routing | HIGH PRIORITY bounded regression audit | current consumer contract tests with actual v11/v12 fixture plus one live probe per relevant endpoint; record state unknown if rollout not reached |
| P1 | Claude D-01 executable **router quote vs CP approximation** | MAL paper-wallet v4 execution shadow | ACCEPT AS RESEARCH DESIGN, NOT CODEX_READY | as-of paired quote on same exact pool/time, buy and sell; record route, size, staleness, fees, 0-route |
| P1 | Claude D-02 failed-fill / sellability simulation | MAL S1 sellability, specialist-dissection #1512 | MERGE D-02 with S1 owner, no second simulation lane | distinguish simulation-unsupported, revert, no-route, missing state; no fabricated 0 loss |
| P1/P2 | Claude D-03 realized MEV haircut | MAL microstructure / execution shadow | REVISE: sandwich candidate detection is NOT yet victim-loss measurement | independently labeled trace, false positive rate, route matching, execution simulation, adequate sample |
| P2 | Telegram screenshot 14 tools | MAL Wallet Alpha / token safety / social / discovery | BORROW ATOMIC FEATURES, do not adopt credential-holding bots | prospective same-time controls, source latency, holder/funder/entity independence |
| P2 | Based Bot | MAL wallet/intel/decision UX; future iPhone frontend | BORROW workflow/card/take-profit visualization only | current docs support capabilities, but no operator economics or independent bot performance evidence |
| P2 | Trader.dev strategies | #1007 and existing 2026-09-29 Trader.dev audit | BENCHMARK / REJECT OPEN LEADERBOARD AS PROOF | full frozen attempt universe, OOS, costs, trade counts, multiplicity |
| P2 | Anthropic agent writing | existing skills + Bridge + Supervisor + Red Team | BORROW: evaluator independence, harness receipts, bounded subagent trust, cheaper decision filters | task-based eval where challenger outperforms current single-owner baseline |
| P3 | User X posts (5 distinct IDs) and extra 0xNevsky from Claude | #937 external alpha intake | INTAKE ONLY: direct pages unavailable (403/cache miss); content NOT READ | owner-supplied verbatim/screenshots or authorized verified capture and provenance |
| P3 | 0xRafy app design inspiration | CN/MAL prospective UX owner | IDEA ONLY, no UI work | actual post content/images, device-first design review and no impact on existing CN |

## Truth hierarchy
1. Existing repo source code, receipts, current main, actual native chain/RPC logs.
2. Official docs and public APIs, with version/date.
3. Claude's research artifact with independent spot checks.
4. X/Telegram author claims, screenshots and marketing are **NOT** proof of edge.
5. Our technical design hypotheses are proposals, **NOT** verified implementations.

## Actually inspected, direct
- `04_RESEARCH_LAB/auto_trading/README.md`: EVIDENCE MACHINE / RESEARCH ONLY / NO EXECUTION LAYER.
- `04_RESEARCH_LAB/auto_trading/EXTERNAL_STRATEGY_REVERSE_ENGINEERING_PROTOCOL_v1.md`: SOURCE, OBSERVABLE, COPYABLE, SCALABLE alpha separation.
- MAL `README.md`, `experiments/paper_wallet/POLICY_V4.json`: real_funds=false, wallet_signing=false, automatic_real_trade_execution=false; MEV and fail-model DEFERRED.
- `scripts/api_agent/meme_alpha_blockscout.py` and restricted `collectors/memes_alpha/moonshot_blockscout_enrichment.py`: existing bounded enrichment, NOT missing integration.
- `06_RESEARCH_LAB/alpha_lab/2026-09-25__blockscout-mcp-alpha-lab-admission-and-proof-v1.md`.
- `06_RESEARCH_LAB/audit_summaries/2026-09-29__research-stack-traderdev-capability-gap-audit__shadow.md`: overlap previously researched.
- Claude attached `AT_FOUNDATION_RESEARCH_RUN-001.zip`: 13 files, 47 external repos, 39 sources, 14 hypotheses, D-01..D-07, E0..E5. Metadata is Claude-reported and should remain distinguishable from independently reproduced evidence.
- Official Based Bot docs index; official Trader.dev browse and landing; Blockscout API docs and v12 release notes; Anthropic Engineering + agent articles.
- User screenshots dated X 9 Oct: 14 Telegram accounts and descriptions (claims not independent validation).
- X direct endpoints all inaccessible during this run: no claims about post content.

## Crucial new finding: Blockscout v12 compatibility
Official release notes: https://docs.blockscout.com/blockscout-v12-0-0-api-updates-and-breaking-changes . Release slated 2026-10-07 with gradual hosted rollout. Concrete API deltas:
* `items_count` now request page size; next_page_params no longer echoes it and sort/order/key; callers must preserve desired sort/order and size.
* `limit` removed on some lists; state_changes cursor renamed; constructor args receive 0x prefix.
* JSON-RPC errors now objects; `eth_getLogs` accepts hex block numbers/tags; `eth_call` can be disabled by host operator; summary endpoint may yield transient 503.
* Some scam-token filtering behavior changed.
No actual client breakage was verified here. Open a compatibility test using current production consumers. Explicitly do NOT describe the service as broken based on docs alone.

## One strong reverse-engineering route
Implement a provider-neutral **event and quote evidence adapter** *inside existing MAL source layer*, initially only for bounded current candidates:
`exact chain+CA -> factory/pool events (native RPC) -> decoded transfers/swap deltas -> pair same-time Blockscout -> trace confidence -> quote buy AND exit -> simulation -> unit-ledger adjustment -> matched controls`.
Native independent event decoding reduces coupling to Blockscout *presentation/index*, not dependence on an RPC provider. Ensure independent providers or consistency proofs when feasible. Point-in-time source timestamps, cursor guarantees, missing logs and reorg safety are mandatory. **NO** new 24/7 full-chain clone/indexer unless measured deficiency justifies cost.

## Execution realism guard
Do not confuse:
- router quote with executed fill,
- `eth_call` with permission to sell under *real transaction state*,
- proximity of same-block trades with proven sandwich attack,
- observed source profitability with copyable/scalable expectancy,
- Telegram bot feature list with audited third-party reliability.
Require null/unsupported values, negative controls, and explicit uncertainty.

## Security boundary
Never place wallet seed, exportable private key, signing session or private wallet positions in prompt, Bridge or public research. `Donh91/secrets` may in future host **restricted attribution mappings / observation receipts** only after owner-specific privacy admission. No signing or delegated trading is approved. The E0-E5 ladder in Claude is a PROPOSAL, not active stage change; do not import it as operational authority.

## Rejected
- Scraping, executing or importing arbitrary Telegram bot binaries.
- Direct AI/LLM-managed wallet and autonomous copy trading.
- Naive memecoin L0 sniping on free infra as default.
- Trader.dev leaderboard selection as validated alpha.
- Generic 10-agent swarm, new long-running Research Lab engine, new scheduler, duplicate signal ledger.
- Treating unread X posts as evidence.

## Follow-up references
- existing #937 (external strategy reverse engineering)
- existing #1512 (S1 executable sellability), #1557 (global trial denominator)
- #1007 Miles adversarial benchmark (different X post, not this new one)
- #1465 KOL identity attribution
- Claude Bridge RUN-001; preserve artifact status SUBMITTED until independent tests
- Anthropic: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- Anthropic: https://www.anthropic.com/engineering/how-we-contain-claude
- Anthropic: https://www.anthropic.com/engineering/harness-design-long-running-apps
- Anthropic: https://claude.com/resources/articles/common-workflow-patterns-for-ai-agents-and-when-to-use-them
- Anthropic: https://claude.com/blog/skills-explained
- Blockscout docs: https://docs.blockscout.com/devs/apis
- Based Bot: https://docs.basedbot.app/llms.txt
- Trader.dev: https://mcp-api.trader.dev/browse and https://trader.dev/

No core, framework pipeline, live trading, wallet authority, schedules, credentials or secrets were changed by this research. This page is a proposed intake for reviewer merge, not canonical proof.

## Addendum, 10 Oct 2026: Miles article text supplied and independently cross-checked
The user supplied the narrative text of the X article (status 2108584190979764314). This upgrades **content availability** for *that one article* to `USER_TRANSCRIBED`, while the original inline-image prompts and linked articles remain missing. Refer to `MILES_DEUTSCHER_FULL_TEXT_ADJUDICATION.md` and `MILES_GARCH_SOURCE_CODE_AUDIT.md` for the deduplicated source breakdown, official Robinhood MCP risk/eligibility check, and static GARCH review. **All other unread X posts remain UNKNOWN.** The main document's earlier `X direct endpoints all inaccessible` records the original fetch result, not the new user-supplied content. No trading authority, model adjustment or new research scheduler follows from this update.
