# DEED chain reproduction and adversarial learning v2

Date: 2026-09-23
Status: PARTIAL_CHAIN_REPRODUCTION / HISTORICAL_REGRESSION
Owner: #1087
Prospective credit: 0
Trade authority: none

## Executive result

The launch transaction materially strengthens the origin/distribution concern, but it does **not** prove every social allegation.

Exact launch:
- token: DEED
- chain: Robinhood Chain, chain id 4663
- token CA: 0x5E55f18453545d0D4314C5106a2D8Db934298E95
- launch tx: 0x36536d4e8bd99303b7782e88dfe965f2cd9be5e8169725400eb2b4e884f94bc7
- block: 69205683
- timestamp: 2026-09-21 23:51:56 UTC
- caller/recipient: 0x0052BB21E9CccfcB790913fe3D9bc52cC45d9dD9
- method: launchAndBuy
- quote sent: 0.053336 ETH
- initial DEED received by caller: 29,900,000 = 2.99% of fixed 1,000,000,000 supply.

This is stronger than a generic 'dev launched token' fact: the creator executed launchAndBuy and immediately held 2.99% of supply from the launch transaction itself.

## Launch calldata finding

The decoded input contains a 25-address array after project metadata. Robinscan identifies the method signature as:
launchAndBuy(..., address recipient, address[] snipeTaxExemptions).

The 25 addresses visible in calldata are therefore **candidate snipe-tax-exemption addresses**, not proof that they received tokens.

This is a high-value structural fact because a launch-time privileged/exempt address set is itself relevant to distribution-risk analysis. However:
- membership != token allocation;
- membership != common ownership;
- membership != insider;
- membership != paid promoter;
- membership != later sale.

Those relationships require per-address transfer/trade reproduction.

Candidate exemption addresses frozen from calldata:
0x1e9932ea2b1c8455c59e5b6470eef7add0e472c7
0xf136dc575dcd22a437fa6ffb6985a4b834ab6914
0x12d78d0f2bac3759e826921015d1970979a29d87
0xec48eb4b393b8530021834e691f752f7af21b22c
0x060919e2b74d97c27bf9b05af889f0d58926316d
0xf00d2ca97fbbe9be9c5fc8958796ceae52479f70
0xf05a2da7756ad3d9042d9f95ab8fa0c57cd73994
0xe8de9c1fe3ba56565e1404b1aa0b44c343311ddd
0x253da72c1fdf6b40ec1b6abeb303c4947202f899
0x1e201a4100fa04527b34ebd530fb2872b019a787
0x24ae6b0613e4ccda784639ef313912096b2ffb2c
0x0c43d76b707996048a8bae3e13fc11d07d241e44
0xe9a44288833f6e9705d0eb212184613939a40e48
0xfb989282a8f7d62d41f38cd3a6f85c48964bc30e
0xddbbd2a7adc8ea870344a7baf95f1779f768a8d3
0x0b94b32e8e8d1eb211dec7bdeb2db4a4760ea04a
0xf3633700da2b3b9c946503a947e64295e5b661fc
0x01fe01362ef57b1301d4718bc11bc9711dacf6bc
0x2d66eb921f1d337a19771b3416f662d7cdcc6086
0xda0af42774bca65e27b26b3c9891d8a1a521ac87
0xda0fad06709ea53ea001c96fa43eaabe35ba9367
0xf7281eef9ac490a67e5fcc9c91e7b524746e395d
0xddc11a7ec9d2bc8151d0ebcd7a2f689f28a49b78
0xecbf675d1044e888bf69ddb9a3779be9cd3f760b
0x1369167cf10ef789ae1fe6ada33cda9ffdaf2dc3

Neither frozen tracked-wallet address for unipcs nor DumbCrayonEater is literally present in this launch calldata list:
- unipcs 0x0a6ebed0155edb4b21d92ad02897a626cd90119e
- DumbCrayonEater 0x8f62a08537cede87d511aca6436274ab4ca080a3

Therefore any alleged allocation to those identities must have occurred through a different address, transfer, market buy, delegated account path or attribution mapping. Do not infer it from the launch calldata.

## Public-tape observations

Blockscout currently indexes thousands of DEED holders and tens of thousands of transfers. Current counts are mutable and should not be used as launch-state evidence.

A public wallet surface currently shows DumbCrayonEater's frozen address holding roughly 9.70M DEED. This proves current/observed exposure only. It does **not** establish how the position was acquired.

Public wallet analytics for unipcs establish the frozen address as an active Robinhood trader, but the accessible public search surfaces in this pass did not reproduce a DEED allocation/trade for that address.

Thus:
- DumbCrayonEater DEED exposure: OBSERVED, acquisition provenance UNKNOWN.
- unipcs DEED allocation: NOT REPRODUCED in this pass.
- social claim '1% sent to unipcs and DumbCrayonEater': NOT VERIFIED.
- social claim 'unipcs cashed out at ~$350k MC': NOT VERIFIED.
- social claim 'KOLs were paid': NOT VERIFIED.

## Market-path observation

Public surfaces show an extreme launch boom/bust, but different market/indexing venues disagree materially on exact high/current values and even expose multiple same-name DEED contracts. This is itself a data-integrity lesson.

Canonical market learning:
- exact CA must precede chart attribution;
- market cap vs FDV semantics must be explicit;
- pair/venue must be canonicalized;
- same-name contracts cannot be merged;
- current holder count and current price cannot reconstruct launch state;
- outcome claims must use timestamped exact-CA observations.

## Stronger pre-launch/launch risk model

The DEED case adds an important category between 'rug mechanics' and 'organic smart-wallet demand':

### PRIVILEGED_LAUNCH_SURFACE

A launch may be mechanically tradable and still have asymmetric distribution.

Evidence primitives:
1. launch caller initial supply percentage;
2. launch-time exemption/allowlist count;
3. exempt-address subsequent acquisition before broad public participation;
4. free/transfer allocation before public trading;
5. common funding roots;
6. creator fee rights and fee destinations;
7. pre-public social/caller coordination;
8. sell-through by launch recipients;
9. proceeds convergence;
10. divergence between public tokenomics narrative and actual launch distribution.

No single primitive proves fraud.

## New causal separation

Alpha Lab should distinguish four different questions:

Q1 DISCOVERY - did we find the project/token early?
Q2 IDENTITY - is this the exact canonical CA?
Q3 ACCESS FAIRNESS - who had privileged economic access before/at launch?
Q4 ECONOMIC QUALITY - after public market eligibility, was there realizable risk-adjusted opportunity?

A project can score well on Q1/Q2 and fail Q3/Q4.

This prevents 'we found it early' from being mistaken for 'we should have bought it'.

## Required launch receipt extension

For Pons-style launches, freeze at T0:
- launch_tx_hash
- launcher_version
- caller
- recipient
- quote_in
- initial_tokens_out
- initial_supply_pct
- snipe_tax_exemption_count
- exemption_addresses_hash
- exemption_addresses_if_budget_allows
- creator_tax_bps/percent
- pair token
- token supply
- project metadata hash
- first public CA timestamp
- first market-eligible timestamp

Then asynchronously enrich:
- exemption address token acquisition provenance;
- transfer-vs-buy;
- common funding/control;
- first sell and sell-through;
- creator fee claims/destinations;
- KOL/caller publication clock.

## Guardrail: do not overfit to 'fresh wallet' heuristics

The screenshot heuristic 'fresh single-use deployer funded through bridge' is useful as one weak feature, not a verdict. Legitimate launches can use fresh wallets, bridges, multisigs or delegated accounts.

Likewise:
- round-number balances are suspicious context, not proof;
- common sell timing can arise from common public news;
- common bridge destination can be infrastructure, not common owner;
- fee destinations can be contracts/treasuries with legitimate purpose;
- top-holder concentration must exclude LP/router/market infrastructure.

Require combinations plus transaction evidence.

## Strongest new learning

The launch itself exposes information that can exist **before the pump outcome**. In DEED, the 2.99% launchAndBuy allocation and 25-address snipe-tax-exemption array were knowable at T0.

That makes them legitimate prospective features for future Pons launches, unlike hindsight observations such as the later crash.

However, they must first be tested against a matched denominator of ordinary/successful Pons launches. If these fields are common launchpad defaults, they have little discriminative value.

## Matched-denominator experiment proposal

Historical representation only first:
- sample Pons launches across winners, losers, flat/noise and suspected coordinated launches;
- reproduce initial_supply_pct and exemption_count;
- compare subsequent exempt-address acquisition/sell-through;
- preserve launch age/regime;
- no outcome-derived threshold.

Only after representation works:
preregister a future challenger testing whether privileged-launch features improve avoidance of severe post-launch drawdowns / unsellable exits without destroying recall of realizable winners.

## Verdict

DEED is upgraded from generic postmortem to a high-value **launch-origin regression**.

Verified:
- exact CA/launch tx/time/caller;
- fixed 1B supply;
- creator launchAndBuy;
- 29.9M DEED to caller at launch = 2.99% supply;
- 25-address snipe-tax-exemption array in launch calldata;
- later observed DumbCrayonEater-address DEED exposure;
- severe boom/bust visible on public market surfaces, exact magnitude venue-dependent.

Not verified:
- 1% allocation to named tracked wallets;
- paid KOL allegation;
- unipcs exit at ~$350k MC;
- common ownership of exemption addresses;
- coordinated proceeds graph.

Framework action:
- preserve DEED as regression;
- add launch-origin/access-fairness fields to the **design contract**, not production weights;
- test these features against matched Pons denominator before any score/threshold;
- keep FOMO provenance fail-closed.
