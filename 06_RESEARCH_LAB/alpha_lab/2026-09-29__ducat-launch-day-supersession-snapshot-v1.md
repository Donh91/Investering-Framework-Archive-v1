# DUCAT launch-day supersession snapshot v1

Date: 2026-09-29
Status: PROSPECTIVE PRE-LAUNCH / SUPERSEDES PRIOR LAUNCH-CLOCK ASSUMPTION ONLY
Owner: #1087 / Project→CA Autonomous Supervisor
Project: Ducat
Official X: @ducat_money
Official site: https://ducattreasury.com/
Official announced CA: 0xD0cA71118ca21D674f9018A53026a38A0AB54DbF
Trade authority: NONE

## Why this exists

The earlier 2026-09-24 prelaunch packet froze an announced 2026-09-25 launch window.
Fresh first-party communication and user-supplied screenshots now supersede that launch clock.

Do NOT rewrite the historical packet. Use this file as the current launch-day clock authority until authenticated first-party/onchain evidence supersedes it again.

## Fresh official launch timeline

Official @ducat_money post at 2026-09-29T04:04:12Z says:
"Less than 9 hours until Ducat is live. Here is your launch day timeline."

User-supplied timeline image states:

13:00 UTC, Tue 29 Sep
TOKEN LAUNCH
- pool opens;
- image says "The 90% launch tax decays to 2% inside the hour."

16:00 UTC, Tue 29 Sep
BONDS OPEN, FIRST AUCTION
- bootstrap begins;
- pass auction runs all three tiers;
- whitelist only.

00:00 UTC, Wed 30 Sep
FIRST PRINT
- pDUCAT and staked passes start earning;
- auctions open to bonders.

Europe/Copenhagen equivalents on 2026-09-29/30:
- 15:00 CEST token launch;
- 18:00 CEST bonds / first auction;
- 02:00 CEST 2026-09-30 first print.

The X prose also says "Tuesday at 9am EST". In late September, 09:00 New York local daylight time corresponds to 13:00 UTC, so the canonical operational clock should use the explicit UTC timeline, not the colloquial EST label.

## Uniswap hook / routing update

Official @ducat_money post dated 2026-09-28T19:21:17Z says:
- their custom Uniswap hook "has been approved ahead of launch";
- they thank Uniswap Labs for quick turnaround;
- they say proper routing is in place for launch.

Interpretation:
- ROUTING_READINESS_CLAIM = FIRST_PARTY_CONFIRMED;
- UNISWAP_INTERFACE/ROUTING_APPROVAL = CLAIMED BY PROJECT;
- SMART_CONTRACT_SECURITY_AUDIT / UNISWAP_ENDORSEMENT = NOT INFERRED.

The wording must not be upgraded into "Uniswap audited or endorsed DUCAT."

## Material tax-parameter conflict

This is a P0 launch-day verification item.

The user-supplied official launch timeline image says:
- opening levy 90%;
- decays to 2% inside the first hour.

But the current first-party whitepaper and roadmap say:
- opening levy starts at 90%;
- decays to the standing 3% rate within the first hour;
- standing buy levy 3% and sell levy 3%, plus pool fee / price impact.

Therefore:
LAUNCH_TAX_PARAMETER = CONFLICTED_PRELAUNCH
SCREENSHOT_CURRENT_OFFICIAL = 90% -> 2%
CURRENT_WHITEPAPER/ROADMAP = 90% -> 3%

No scanner or user-facing action may silently choose one.

At T0:
- read live hook / pool config;
- simulate exact buy and sell from a public account;
- freeze actual recipient-specific levy;
- preserve pool fee separately;
- compare to both published versions;
- if live value conflicts materially with current official communication, classify SOURCE_CONFLICT / HANDLE_GATE fail-closed until reconciled.

## Exact CA pre-launch check

Fresh Blockscout Robinhood Chain read on 2026-09-29 before launch:
0xD0cA71118ca21D674f9018A53026a38A0AB54DbF
- is_contract: false;
- no first transaction;
- no token transfers;
- no deployed token metadata.

Therefore:
CURRENT_HANDLE_GATE = R0_NO_ENTRY_YET
EXACT_CA_BINDING = AUTHENTICATED_FIRST_PARTY_BUT_NOT_DEPLOYED
COPYCAT_RULE = unchanged

Only this exact CA is eligible unless authenticated @ducat_money explicitly supersedes it.

## Launch-day scanner priorities

T0 / 15:00 CEST:
1. exact CA becomes deployed/readable;
2. deployment/launch tx/block/time;
3. source/bytecode and proxy/admin roles;
4. live DUCAT/USDG pool identity;
5. actual hook address + hook permissions;
6. actual opening buy levy;
7. actual opening sell levy;
8. pool fee and total executable round-trip cost;
9. buy AND sell simulation / bounded sellability;
10. genesis allocation, operations wallet, liquidity ownership/withdrawal authority;
11. holder/buyer breadth and pre-positioned cohorts;
12. funding ancestry / operator lineage;
13. any privileged wallet / whitelist / tax exemption behavior.

Do not treat the anti-snipe opening levy as protection against insiders.
A privileged or operator-controlled address may have different economics if exemptions/roles exist; verify live.

At 18:00 CEST:
- bonds live;
- reserve/reference/cover reads;
- bond capacity and post-settlement guard;
- first pass auction;
- whitelist-only semantics;
- treasury destinations.

At 02:00 CEST 2026-09-30:
- first print;
- pDUCAT/pass reward behavior;
- expansion accounting;
- first production evidence that the monetary engine behaves as published.

## BYTE-derived launch-day learning applied

DUCAT must also inherit the newly learned BYTE safeguards:
- address-level HOLDING is insufficient;
- track beneficial inventory lineage / descendant wallets;
- separate protocol-shared infrastructure from operator-specific edges;
- monitor whale cascade independently of known cohort;
- early buyer != insider;
- pre-positioning + synchronized execution + operator-link is stronger evidence than timing alone.

## Current pre-launch assessment

PROJECT / DESIGN INFORMATION: HIGH
FIRST-PARTY DOCUMENTATION: HIGH
EXACT CA: AUTHENTICATED, UNDEPLOYED
TEAM IDENTITY: still not independently verified
HOOK / ROUTING: project says approved / ready; live code/config pending
OPENING TAX: CONFLICTED (2% vs 3% destination)
ANTI-SNIPE MECHANISM: MATERIAL, but execution cost is extreme during decay
CURRENT HANDLE GATE: R0_NO_ENTRY_YET
ALPHA LAB RELEVANCE: VERY HIGH
