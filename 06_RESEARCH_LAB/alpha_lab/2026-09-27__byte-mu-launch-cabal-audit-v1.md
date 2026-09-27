# BYTE / MU launch audit — cabal hypothesis v1

Date: 2026-09-27
Status: PRE-OUTCOME / SHADOW / MANUAL INTAKE
Owner: #1087 / Meme Alpha Supervisor
Pair ID: 0x32c33dfa9dad986f8d6ee85d7be1d5d0cc3f98e5c2fa6839cf586cc2e6cf6914
Token CA: 0xd5520D9D777a42D85f94834fbea162B17A197CfB
Pair token: MU 0xfF080c8ce2E5feadaCa0Da81314Ae59D232d4afD
Trade authority: NONE

## Snapshot

DEX Screener at audit time showed approximately:
- MC/FDV: ~$299K
- liquidity: ~$51K
- pair age: ~3h54m
- 6h change: +541%
- volume: ~$449K
- traders: 681
- buys/sells: 1,564 / 1,162
- buy/sell volume: ~$232K / ~$216K
- buyers/sellers: 469 / 493

Blockscout holder count at the same bounded audit: 482.

The token is paired with Micron Technology Robinhood Token ($MU), not ETH/USDG.

## First-party / narrative evidence

Website: https://www.thebytedog.com/
Claims:
- BYTE is "The AI Memory Dog";
- narrative is tied to prior Elon/xAI/Grok imagery/posts;
- paired with MU;
- independent community project, not affiliated with Micron, Robinhood, Elon Musk or xAI.

This is narrative provenance, not official Elon/xAI token provenance.

## Exact Pons launch-origin reproduction

Verified PonsV2LauncherToken.
Creation / launch tx:
0xbe7dc4222154b9100d5cb2f4304e623a52978d1c0f0cd89e4a9becb12d17bc5b

Launch time:
2026-09-27T16:42:09Z

Launch caller / recipient:
0xE142304Cc7A3F47106122f393DeB990F11C8D3d0

Pair token:
MU 0xfF080c8ce2E5feadaCa0Da81314Ae59D232d4afD

quoteIn:
0.225645123027501572 MU units before any UI-multiplier interpretation.

Initial BYTE to launcher:
57,356,025.32927156 / 1,000,000,000 = ~5.7356%

Snipe-tax exemptions:
0

This is materially different from the 15/25-exemption privileged surfaces seen in several prior Pons cases.

## Critical launch sequence

The launch wallet was brand new on-chain the same day.
First observed transaction:
2026-09-27T15:32:49Z.

Funding:
0xA5DF4D576A72DdBBB4296614aAF58Ed6696EBe61
-> launch wallet
~0.09899311 ETH.

Then:
- ~15:43:07Z: launcher swaps ~0.09201311 ETH through an exactInput route into MU;
- 16:21:52Z: launches BYTE CA 0x6C7b445aAE7259eC9aa276ACE642fdbEDC3a2167;
- 16:24:23Z: full ~57.356M initial BYTE position from that launch is moved out via a contract path;
- 16:30:56Z: launches another BYTE CA 0x7e7cf03C77981ac0b946f9E99B471dC6E7DF5341;
- 16:33:51Z: full ~57.356M initial position from that launch is moved out via a contract path;
- 16:42:09Z: launches the current BYTE CA 0xd5520...;
- 16:50:04Z: full ~57.356M initial creator position is sent to 0x000...dEaD.

Interpretation:
This is a clear multi-launch / relaunch sequence immediately before the canonical public token.

It is NOT by itself proof of a scam or cabal.
Possible explanations include launch retries, testing or deliberate cleanup.

However, it is exactly the kind of behavioral pattern that belongs in OPERATOR_LINEAGE / RELAUNCH_FAMILY evidence.

## Funding-hub anomaly

The funding address 0xA5DF4D576A72DdBBB4296614aAF58Ed6696EBe61 is not a normal fresh personal funding wallet.

Public explorer snapshots describe:
- ~8,985 transactions;
- large native ETH balance at the snapshot;
- many repeated inbound and outbound native transfers;
- multiple repeated-size transfers around ~0.088-0.16 ETH to/from many addresses.

This address therefore looks like a high-throughput funding/collection/service hub.

It must NOT yet be called a cabal wallet.
Alternative explanations include:
- exchange/service hot wallet;
- routing/funding infrastructure;
- automation/funding service;
- operator treasury / cabal hub.

Current evidence state:
FUNDING_HUB = REPRODUCED
CABAL_IDENTITY = UNPROVEN

No direct match was found against the current canonical Wazz/Atarashi seed registry during this audit.

## Positive anti-rug evidence

Several launch-origin facts are better than the extreme Wazz-ring cases:
- zero snipe-tax exemptions;
- only ~5.74% initial launcher position;
- the final launcher position was burned ~8 minutes after launch;
- hundreds of current holders/traders;
- current buy/sell volume is relatively balanced;
- liquidity is non-trivial relative to current MC.

These reduce one class of immediate privileged-supply risk.

They do NOT rule out:
- linked-wallet accumulation after launch;
- externally funded cabal buys;
- hidden connected holders;
- creator-fee extraction;
- coordinated distribution.

## Cabal hypothesis

Current state:
CABAL_HYPOTHESIS = ELEVATED_BUT_UNCONFIRMED

Reasons to investigate:
1. fresh launch wallet;
2. funded from a high-throughput hub;
3. two same-name launches immediately before the public CA;
4. staged conversion from ETH -> MU -> repeated Pons launches;
5. current token already experienced rapid large price expansion.

Evidence against immediate "classic privileged bundle" classification:
1. zero launch exemptions;
2. initial creator allocation only ~5.74%;
3. creator allocation was burned;
4. visible holder/trader breadth is materially wider than a tiny closed ring.

The cabal question has therefore moved from launch calldata to POST-LAUNCH WALLET GRAPH.

## Alpha interpretation

Current observed expansion is real in the market-data sense but already advanced.

The useful question is no longer whether BYTE can pump.
It already has.

Research question:
Is the remaining demand driven by independent public buyers or by a connected funded cohort that may later distribute?

Required next checks:
- top-holder graph excluding LP/dead/system addresses;
- funding ancestry of top 25-50 early buyers;
- overlap with A5DF-funded wallets;
- first-buy timestamps and synchronized clusters;
- realized exits and sell-through by those clusters;
- creator-fee recipient and subsequent proceeds;
- bounded-notional sellability/slippage;
- exact price path and realizable MFE from T+30s/T+2m/T+5m/T+15m;
- operator-lineage overlap with known Wazz ring.

## Shadow conclusion

PROJECT/NARRATIVE: MATERIAL MEME CATALYST
LAUNCH PRIVILEGE: LOWER THAN SEVERAL KNOWN PONS RUG CASES
FUNDING ANOMALY: HIGH
RELAUNCH ANOMALY: HIGH
CABAL EVIDENCE: ELEVATED / UNCONFIRMED
RUG RISK: NOT CLEARED
REALIZABLE ALPHA: ALREADY PARTLY CONSUMED; continuation requires wallet-graph confirmation
EXECUTION TOXICITY: UNKNOWN

Do not classify SAFE merely because security scanners show no contract issue.
Do not classify RUG solely from the relaunch sequence.
