# Alpha Lab — Thread Handover 2026-09-19

Status: canonical handover candidate
Parent owner: #1087
Execution packet: #1134
Scope: Alpha Lab — Tokens & Moonshots

## Purpose

Preserve the decisions, falsifications, evidence rules and active experiments from the long Alpha Lab thread so a successor thread can continue without reconstructing context or accidentally resurrecting killed hypotheses.

This file is a handover, not a new owner, scanner, scorer or ledger. Where conflict exists, fresh main + #1087 + immutable prospective evidence outrank this summary.

## Permanent operating doctrine

Analysis order:

DATA INTEGRITY -> TOKEN/POOL -> WALLETS -> TOKENOMICS -> NARRATIVE/TECH -> CATALYSTS -> RISKS -> R/R -> ACTION -> OUTCOME -> LEARNING

Research loop:

DISCOVER -> FREEZE -> VERIFY -> DIFFERENTIATE -> ACTION -> OUTCOME -> LEARN -> IMPROVE

Rules:
- assume new alpha hypotheses do not work until prospective evidence says otherwise;
- rows beat theory; forward tests beat retrospective narratives;
- UNKNOWN != 0;
- MC != FDV;
- ticker/name are attributes, never identity;
- substring matching is forbidden;
- failed/partial/implausibly-empty queries are UNKNOWN/DEGRADED until coverage is proved;
- live canonical chain/pool evidence outranks stale web/social;
- conflicts quarantine the row;
- no retrospective edge credit;
- no capital automation/autonomous buying from research evidence;
- preserve false positives, false negatives and killed hypotheses permanently.

## ASKR ground-truth case

Project: heyaskr / ASKR
Chain: Robinhood Chain, chainId 4663 / 0x1237
CA: 0xa92768863a55d8A0591709f7f5E594A249d36Ea3
Pons V2 factory: 0x7eD598BcEf8bd9Edd8C97A195C6d13f40801EC7e
TokenLaunched topic0: 0x8d4aad4953d0ca700d468f3753aa14432d1b35b43ec6409f051fb6aa43a89607
Launch block: 66443556
Launch UTC: 2026-09-18T18:35:17Z
Launch tx: 0xa5ffe87bd1e9b6b91f84bb237c2d6408a7df39cb0651f85760004712074585f3
Curve: 0x18a08ece3e8c29df9ae497a09d2a08830561c59b
Deployer: 0x9d9258c2409c5cea1a8e24206a071ed34f3ca352
Router: 0xe33e9e479df8802cb0866d5d05258bec4cf62948
Supply: 1,000,000,000 ASKR
DexScreener pool: 0x90b75d6e9ac1e7efc3154c89e155121f7d7c0e54ebbd3dbba379650deb64d41e

Historical verdict: FALSE NEGATIVE / MISS. Alpha Lab receives ZERO autonomous discovery credit.

Forensics:
- the historical scanner process died roughly 85 seconds before launch;
- first eth_blockNumber call received HTTP 403;
- historical code used urllib.request without explicit User-Agent;
- later reproduction linked this client path to Cloudflare/WAF behavior;
- parser capability replayed PASS against exact ASKR event;
- repaired detector found correct ASKR, but replay/post-repair success does not rewrite history;
- runtime liveness, exact production client+headers and failover must be proven, not inferred from workflow existence.

BASKR negative fixture:
- BASKR is a different project;
- substring matching caused an identity false positive;
- even exact ticker/name are insufficient project identity;
- keep BASKR as permanent negative regression fixture.

## Claude adversarial Pons package — external research evidence

Treat measurements below as EXTERNAL_REVIEW_MEASURED until independently reproduced.

Reported denominator:
- 547,741 Pons launches over 46.4 days;
- 8,718 graduations;
- base graduation rate 1.592%.

Reported ASKR curve:
- T0 -> graduation 98 s;
- 199 trades;
- 35 wallets;
- 5.922 ETH in / 1.485 ETH out;
- FDV approx 1.832 -> 20.84 ETH;
- dev bought ~5.46% in launch block;
- nine wallets by T0+1s;
- first sell T0+3s.

Interpretation: latency was economically material, but curve depth/sellability mean headline multiples are not realizable PnL by default.

Seed wallet:
0x8f9e3737A602B1e51bD87c44B6eF7439eDC1c105
Explorer: https://robin.etherscan.io/address/0x8f9e3737A602B1e51bD87c44B6eF7439eDC1c105

Reported falsification:
- first ASKR touch ~T0+27,093s / 7.5h;
- two tokens in lifetime;
- one Pons launch;
- winner-selected holder, not evidence of repeatable alpha.
Do not track/promote it as smart money absent new independent evidence.

ASKR early-wallet finding:
- earliest observed wallets were broad high-frequency snipers/bots;
- reported broad sniper example entered 6,328 Pons launches at median ~0.7s;
- selective wallets in examined cohort were much later;
- apparent smart-money graduation lift is vulnerable to reverse causation/endogeneity because buyers help cause graduation.
Conclusion: DO NOT BUILD smart-wallet scorer from ASKR.

## Surviving challenger hypotheses

1. PRE-DISCLOSED PROJECT ADDRESS -> FUTURE DEPLOYER
STIMMY case: realworldstimmy.com reportedly disclosed a rewards wallet before launch and the same address later deployed STIMMY.
Status: HYPOTHESIS, n=1.
Needs prospective confirmations; no promotion from STIMMY itself.

2. DEV-BUY SIZE
Claude reports dev-buy >=0.15 ETH produced ~2.22x graduation lift (3.57% vs 1.61%) in a 1,000-launch discovery sample.
Status: CHALLENGER ONLY.
Must be independently reproduced and tested on a disjoint pre-registered OOS period before any authority.

3. DELTA_PUBLISH
Δ_publish = first-party CA publication time - canonical T0.
This is the decisive kill metric for VERIFIED-before-public.
STIMMY reportedly still showed no CA >7h after launch.
SHERWOOD previously stated first-party site would publish CA first.
Need >=30 genuinely pre-frozen eligible launches and a pre-registered external-edge budget.
If median Δ_publish misses budget, kill/re-scope VERIFIED-before-public rather than optimizing indefinitely.

## DEED

DEED is a forensic/passive-discovery control case, not prospective Alpha credit unless a valid pre-T0 Alpha Lab freeze is found.

User supplied pre-launch/around-launch social evidence from official @DeedEstate describing a Robinhood Chain real-estate/yield product and deed.estate.

Claude reported deed.estate had no attributable CA/chain/ticker/venue publication sufficient to bind the observed DEED tokens.
Treat attribution as UNKNOWN unless canonical evidence improves.

Research question: what public/project/ecosystem evidence existed before T0 that a passive discovery layer could have found?

## Pre-launch Robinhood/Pons cohort

Previously identified leads to re-verify before use:
- STIMMY — realworldstimmy.com
- SHERWOOD — sherwood.meme
- FRODO — thering.lol
- Hoodgraph / HDG — hoodgraph.space
- BLUECHIP — bluechipnvda.com
- Robin Index — robinindex.fun
- PonsTrack — ponstrack.fun
- AlphaHood AI / AHAI — alphahoodai.com
- BloxHood — bloxhood.fun
- Robinboob / BOOB — robinboob.lol
- HODO — hodo.lol
- Corvane — askcorvane.com/token, potentially non-Pons
- Umbrella Capital — umbrellacapital.money
- Pledge Finance — pledgedefi.com

Important contamination finding from Claude:
ticker reuse is common. Reported 53% of graduates share a ticker with another graduate. Some named leads already had same-ticker graduated tokens.
Therefore project identity must be pre-frozen from first-party provenance, never ticker search.

## Active scientific experiment order

Canonical child packet: #1134.

P1 / E1: disclosed-address -> deployer prospective test.
- freeze first-party page/content hash/address before T0;
- exact future deployer/receipt.from match;
- preserve misses/false links;
- STIMMY n=1 cannot count toward additional confirmation gate.

P2 / E3: Δ_publish prospective cohort.
- freeze exact first-party CA-publication surface before T0;
- record T0/Tpublish/Text/censoring;
- target >=30 eligible rows;
- kill/re-scope if median Δ_publish misses pre-registered external-edge budget.

P3 / E4: dev-buy OOS.
- independently reproduce denominator/extraction;
- freeze threshold and future/disjoint period before outcomes;
- discovery sample has no alert/score authority;
- require fresh OOS lift with uncertainty and healthy data before promotion.

P4 / E2: global early+selective wallet falsification.
- research only;
- correct for participation/endogeneity, insider/deployer links, Sybil clusters and indiscriminate snipers;
- wallet sensor remains blocked unless independent effect survives.

P5: human execution latency in parallel.
- measure alert -> acknowledgement -> CA visible -> venue -> ready-to-sign without capital;
- can kill seconds-critical manual execution;
- does not kill pre-T0 discovery research for slower/post-graduation opportunities.

## Proof supervisor / automation

PR #1131 introduced deterministic prospective-proof supervision concept:
- only PROSPECTIVE_PASS advances;
- bounded infrastructure retries;
- scientific FAIL cannot be retried until it passes;
- major-gate-only user escalation;
- temporary experiment schedules self-terminate on PASS/KILL/MAX_WINDOW;
- portfolio_execution=false;
- canonical_effect=false.

Before relying on it, verify current main/PR state and CI. Do not assume open PR == running automation.

Desired automatic state path:
hypothesis -> preregistration -> collection -> adjudication -> PASS/FAIL/KILL -> next experiment/engineering packet.

Do not create another supervisor if existing owner can be extended.

## Claude Round-2 runtime corrections retained

- topic[3] / tx.from is not reliable stand-alone identity;
- receipt.from may corroborate but does not establish project identity alone;
- token bytecode is not useful project identity;
- Pons factory + exact TokenLaunched topic establish venue-level token launch, not project-specific provenance;
- safe cursor must use multiple independent providers/transports, overlap/backfill and persisted state;
- never cursor=head blindly;
- restart must resume persisted cursor;
- 403 is permanent-class for that client/provider path until fingerprint/provider changes;
- 429 backs off provider;
- provider disagreement is DEGRADED/candidate, not VERIFIED;
- own monotonic clock for latency; block timestamps do not justify sub-second claims;
- GitHub workflow existence is not runtime-liveness proof.

## User-facing Alpha objective

Alpha Lab should surface genuinely valuable early information, not maximize alerts.

For meaningful candidate:
DATA INTEGRITY -> exact token/pool -> wallets -> tokenomics -> narrative/tech -> catalysts -> risks -> R/R -> ACTION.

Actions remain:
IGNORE / WATCH / DEEP DIVE / ENTRY CANDIDATE.

For ultra-fast launches, first alert may be a clearly uncertain CANDIDATE_RANKED state followed by VERIFIED_CA if provenance resolves. Never silently promote uncertainty.

## ASKR position context at handover

User reports entry around ~$200k market cap and had not sold as of 2026-09-19 morning. Screenshot around 10:22 CEST showed ~4.11M on 15m after a peak near ~7M. This is user position context, not a canonical Alpha Lab outcome and must not contaminate ASKR scanner evaluation.

Keep scanner/research outcome scoring separate from user's trading outcome.

## Success criterion for successor thread

Do not ask the user to reconstruct this work.

First:
1. read fresh #1087 and #1134;
2. verify #1131/related PR state on fresh main;
3. inspect newest prospective artifacts;
4. continue the highest-information experiment that is actually ready;
5. do not resurrect killed wallet/ticker hypotheses;
6. report only meaningful PASS/FAIL/KILL or actionable alpha to user, not hourly noise.

North star:
Build a machine that can prove when it knows something before the market does, and prove when it does not.
