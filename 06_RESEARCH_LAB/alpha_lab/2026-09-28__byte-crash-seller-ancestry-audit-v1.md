# BYTE crash seller ancestry audit v1

Date: 2026-09-28
Status: SHADOW RESEARCH / LIVE-CASE FAILURE ANALYSIS
Owner: #1087 / Meme Alpha Supervisor
Token: BYTE
CA: 0xd5520D9D777a42D85f94834fbea162B17A197CfB
Trade authority: NONE

## Executive conclusion

The ~70% crash from the user's ~220K reference entry was NOT caused by the previously tracked five-wallet ~9.55% cohort.

Instead, the crash was driven by a broader whale / holder cascade, including several wallets that can be traced back to launch-minute buyers and several later public traders.

Critical correction:
EARLY BUYER != INSIDER.

However, multiple crash-exit wallets trace one hop back to wallets that bought directly from the Pons curve at 16:48:21-22Z, ~6m12s after final launch.

This materially expands the suspected coordinated cohort beyond the original five wallets and shows why monitoring current holder addresses alone is insufficient.

## Crash flow

Window:
2026-09-28T15:30:00Z to 15:50:30Z

BYTE into PoolManager:
~143.052M BYTE

BYTE out of PoolManager:
~98.895M BYTE

Net BYTE into pool:
~44.157M BYTE

The most severe first sell wave was approximately 15:32-15:35Z:
- 15:32 net +14.07M BYTE into pool
- 15:33 net +46.48M
- 15:34 net +22.50M
- 15:35 net +4.00M

Combined:
~87.06M BYTE net into pool in ~4 minutes.

This is sufficient to explain a large portion of the price collapse in a thin-liquidity pool.

## Largest identified seller / seller-chain examples

### 1. 0x0a6B1858... — largest direct dump

Sold:
~24.291M BYTE (~2.43% supply) at 15:32:49Z.

This wallet had been a large holder before the crash.

Important:
its BYTE accumulation began hours after launch through repeated routed market acquisitions.
Observed inbound BYTE includes activity from ~21:41Z onward and into the next day.

Address first transaction on Robinhood Chain:
2026-09-17.

Classification:
BYTE whale = YES.
Launch insider evidence = LOW.
Likely sophisticated trader / automated account = more plausible than launch insider from current evidence.

It is an EIP-7702 SemiModularAccount.

### 2. 0x73dEd664... — genuinely early public buyer

Sold:
~8.437M BYTE (~0.84% supply) at 15:33:45Z.

Direct buys from PoolManager:
- 3.7166M at 17:06:02Z
- 4.3169M at 17:06:52Z
- 0.4039M at 20:12:54Z

Final launch:
16:42:09Z

Therefore first BYTE acquisition:
~T+24m.

Wallet first transaction:
2026-09-25.

Classification:
EARLY BUYER = YES.
INSIDER = NOT PROVEN.
Fresh-ish wallet + early acquisition merits watch, but T+24m is publicly accessible timing.

### 3. 0xd0488550... — downstream exit wallet from a T+6m buyer

Crash sale:
~6.583M BYTE at 15:33:30Z.
It had already sold ~1.417M earlier.

Initial 8.0M BYTE received:
17:13:46Z from
0x8f05545689Ef68194d36c18328d165D122FE78DB.

Trace one hop upstream:
0x8f055456... bought
~8.262768M BYTE directly from Pons curve at
16:48:22Z,
~T+6m13s after final launch.

Then:
8f055... -> d048... = 8.0M BYTE.

Classification:
d048 itself = downstream exit wallet.
8f055 upstream = launch-minute early buyer / high-priority cohort candidate.
INSIDER = NOT PROVEN.
COORDINATED EARLY POSITIONING = materially more plausible.

### 4. 0xb2666F0d... — downstream wallet fed by multiple early sources

Crash sale routed:
~7.664M BYTE at 15:34:33Z.
Also sold smaller pieces earlier and bought ~4.592M back during crash.

Inbound:
- 7.653669M from 0x5f5b1Fc... at 18:23:25Z
- 3.0M from 0xdC63cA7... at 18:24:22Z

Trace:
0x5f5b1Fc... bought exactly
7.653669M BYTE from Pons curve at 16:48:22Z (~T+6m13s).

Therefore part of b266's crash inventory is directly descended from a same-second launch-minute buyer.

Classification:
b266 = active trading / exit wallet.
5f5b = early-cohort candidate.
Common beneficial ownership = UNKNOWN.

### 5. 0xdC63cA7... — major newly discovered launch-minute buyer

Direct Pons-curve buy:
~21.508469M BYTE at 16:48:21Z (~T+6m12s).

Subsequent distribution:
- 3.0M -> b2666F0d...
- 9.994573M -> 0xA0686aFB...
- 7.025077M -> 0xCE58A25... -> 0x6F864b65...
- sold ~1.850847M itself

This is a crucial entity-graph finding:
a large launch-minute buyer split inventory across multiple downstream wallets, some of which later sold into the crash.

0xA0686aFB... was still a large current holder in prior holder snapshots.

### 6. 0x6F864b65... — downstream exit branch from dC63

Received:
~7.025077M BYTE from 0xCE58A25... at 20:04:59Z.

CE58 received the exact same amount from dC63 ~32 seconds earlier.

Crash-period sales:
~6.435M BYTE across two transactions around 15:32:50-15:33:29Z.

Thus:
dC63 (T+6m direct buyer)
-> CE58 relay
-> 6F864 exit wallet
-> crash sell.

This is strong inventory-lineage evidence.

### 7. 0x9fb1c3cD... and 0x7572D267...

Both sold ~6M-scale positions during the crash.

Observed acquisition history is substantially later than launch:
- 9fb1 receives routed BYTE from ~23:05Z onward.
- 7572 receives routed BYTE primarily the next morning.

Classification:
later active traders / automation more plausible than launch insiders.

### 8. 0xC10EA890...

Sold:
~5.991M BYTE at 15:44:20Z.

Then BOUGHT:
~8.536M BYTE at 15:46:58Z.

Therefore this address is not well described as a one-way insider exit.
It behaved as an active trader / dip buyer during the crash.

## Expanded cohort implication

Original sampled same-second / pre-positioned cohort:
~98.97M BYTE across five wallets.

Newly traced launch-minute buyers:
- 0x8f055... ~8.263M
- 0x5f5b1... ~7.654M
- 0xdC63... ~21.508M

These three alone add:
~37.425M BYTE.

Original five + these three:
at least ~136.39M BYTE = ~13.64% of total supply acquired around the same launch-minute cluster.

This does NOT yet prove all eight are controlled by one operator.

But the original five already had strong synchronized pre-positioning evidence.
The three new addresses bought from the same Pons curve in the same 1-2 second launch window and later distributed inventory into wallets that participated in the crash.

Therefore:
COHORT_BOUNDARY = INCOMPLETE_PREVIOUSLY
COORDINATED_LAUNCH_MINUTE_INVENTORY = STRONGER
COMMON_OWNER = UNKNOWN
PRIVATE_INSIDER_KNOWLEDGE = UNPROVEN

## Critical semantic lesson

Do not use:
EARLY_BUYER -> INSIDER.

Use a hierarchy:

EARLY PUBLIC BUYER
- bought after public launch;
- no private linkage.

PRE-POSITIONED BUYER
- funded / pair-asset ready / approvals prepared before launch.

COORDINATED COHORT MEMBER
- synchronized funding, approvals, buy time, retry pattern, downstream inventory linkage.

OPERATOR-LINKED
- direct economic / creator / collector / funding relationship to project operator.

INSIDER-LIKE
- strong evidence of pre-public knowledge or privileged access.

Actual "insider" should remain unclaimed unless evidence supports private knowledge / project-control relationship.

## Major framework failure discovered

Monitoring only the five original holder addresses missed downstream inventory lineage.

An early wallet can:
BUY
-> TRANSFER
-> SPLIT
-> RELAY
-> EXIT FROM DESCENDANT WALLET.

Therefore operator / cabal risk must track:
BENEFICIAL_INVENTORY_LINEAGE
or
DESCENDANT_INVENTORY_GRAPH

rather than only current wallet balances.

A wallet should remain economically linked to its descendant inventory until:
- bona fide market sale breaks lineage;
- transfer is identified as protocol routing;
- evidence expires / conflicts.

## New trigger candidates

1. EARLY_COHORT_DESCENDANT_SELL
A descendant wallet of a frozen launch-minute cohort sells.

2. WHALE_CASCADE_TRIGGER
Multiple holders sell >X% supply / active liquidity in a short window even when known operator wallets are static.

3. INVENTORY_SPLIT_RISK
A launch-minute buyer fragments inventory across multiple wallets.

4. BENEFICIAL_BALANCE
Track cluster-level economic inventory instead of address-level current balance.

5. MARKET_CAPITULATION_TRIGGER
Already proposed; now supported by direct crash-flow evidence.

## Current interpretation

Was the crash caused by "insiders"?
NOT PROVEN.

Was it caused only by random retail?
NO.

Evidence supports a MIXED cascade:
- one very large later whale (0a6B) dumped ~2.43% supply;
- several additional holders liquidated;
- some crash seller inventory can be traced directly back to T+6m launch-minute buyers;
- known original five-wallet cohort did not sell directly.

The correct Alpha Lab conclusion is:
COORDINATED_EARLY_INVENTORY PARTICIPATED INDIRECTLY IN THE CRASH,
while later large traders amplified the move.
