# BYTE holder-graph / coordinated-cohort follow-up v1

Date: 2026-09-28
Status: SHADOW RESEARCH / MANUAL LIVE-CASE FOLLOW-UP
Owner: #1087 / Meme Alpha Supervisor
Token: BYTE
CA: 0xd5520D9D777a42D85f94834fbea162B17A197CfB
Prior packet: 06_RESEARCH_LAB/alpha_lab/2026-09-27__byte-mu-launch-cabal-audit-v1.md
Trade authority: NONE

## Executive update

The next-step holder/funding investigation materially upgrades one part of the prior hypothesis:

- CLASSIC_PONS_PRIVILEGED_BUNDLE: NOT SUPPORTED by launch calldata.
- RELAUNCH_FAMILY: REPRODUCED.
- FRESH_LAUNCHER / HUB-FUNDED: REPRODUCED.
- PRE-POSITIONED WALLET COHORT: STRONG EVIDENCE.
- COMMON REAL-WORLD OWNER / CABAL IDENTITY: NOT PROVEN.
- TOP-HOLDER COMMON FUNDING ROOT: PARTIALLY OBSERVED, but Relay infrastructure is a major false-positive surface.
- POST-LAUNCH COORDINATION: STRONG EVIDENCE for a sampled cohort.
- WASH-TRADING RING: NOT ESTABLISHED.
- OPERATOR-LINEAGE LINK TO KNOWN WAZZ RING: NOT ESTABLISHED.

The most important new evidence is behavioral, not merely common-funder evidence.

## Current holder distribution snapshot

Blockscout holder snapshot during the 2026-09-28 follow-up showed 635 holders.

Largest system / structural balances:
- PonsV2LaunchLocker 0x267444D099b10fB5Ed7c3Cc7B7c767AdcA574952: ~81.633M BYTE.
- Uniswap PoolManager 0x8366a39CC670B4001A1121B8F6A443A643e40951: ~72.054M BYTE.
- burn address: ~57.356M BYTE.

Top-50 balances summed to ~617.68M BYTE, but this raw figure is misleading because it includes locker, PoolManager and burn.

After excluding those three structural addresses:
- top 47 non-system addresses: ~406.64M BYTE = ~40.66% supply;
- top 10 non-system addresses: ~174.91M = ~17.49%;
- top 20 non-system addresses: ~264.28M = ~26.43%.

This is meaningful concentration, but it is NOT the ~80% launch-time privileged control observed in the strongest Wazz serial-extraction cases.

## Sampled top-holder cohort

We sampled seven of the largest non-system current holders.

Five of seven show an extremely similar pre-positioning and buy sequence:

A:
0x131219052b97972C6a3c8Bd2F63e4c154a07c136

B:
0x3F8D24D71e630cE555Bb70228D02f4fC211698FF

C:
0x9AEC8ECfb0AAB559FE64076222b589Dec9D12A1b

D:
0x0e622a55cE4048DF958EEF6d871A91950d04dD29

E:
0xe07af4e90680370F2986BEa68144b36021799A8E

### Funding / preparation pattern

A:
- funded 15:08:43Z with 0.0656545333 ETH by 0x370A7E2d300c14D79d4A7ee07aACA46c4B3012cF;
- successful ETH->MU route 15:32:27Z using ~0.0576463805 ETH.

B:
- funded 15:06:43Z with 0.0678414211 ETH by SAME 0x370A7E2d...;
- successful ETH->MU route 15:32:12Z using ~0.0598333317 ETH.

C:
- funded 15:04:43Z with 0.0665275921 ETH by 0xA5a5491bCa93dD4C076e4906e79E7673F4A5A142;
- successful ETH->MU route 15:31:58Z using ~0.0585192150 ETH.

D:
- funded 15:00:45Z with 0.0665296751 ETH by 0xf42b73d2e4D3912EAdE2A5f7AB39b54064c2acEc;
- successful ETH->MU route 15:31:15Z using ~0.0585216123 ETH.

E:
- funded 15:12:43Z with 0.0669691475 ETH by 0xa67D7Eb4dc68fa6ce8e34Ef8CaDaF075b9893FBb;
- successful ETH->MU route 15:31:35Z using ~0.0589609224 ETH.

All five therefore retain almost the same native ETH residual after the MU acquisition:
~0.0080081 ETH before subsequent gas.

This near-identical target residual is strong automation / shared-strategy evidence.

### Repeated pre-launch approvals

The same five wallets approve MU in near-lockstep in three waves:

Wave 1:
~15:41:37-15:42:21Z

Wave 2:
~16:29:16-16:29:59Z

Wave 3:
~16:40:39-16:41:17Z

The launcher itself produced three BYTE launches:
- BYTE #1 at 16:21:52Z;
- BYTE #2 at 16:30:56Z;
- final BYTE at 16:42:09Z.

The approval waves therefore track the relaunch sequence unusually closely.

This is stronger evidence than simple same-second public buying because the cohort was already preparing MU balances and approvals before the final launch existed.

## Final-launch coordinated acquisition

At T+~6m12s after the final BYTE launch, the same five wallets bought directly from the Pons curve contract 0x49a6E53ff586A7b29Fe4B9F42d73C2e89d095f60:

- A: 24.5710386M BYTE at 16:48:21Z
- B: 22.6056561M BYTE at 16:48:21Z
- C: 23.4830059M BYTE at 16:48:21Z
- D: 14.4394005M BYTE at 16:48:21Z
- E: 13.8703361M BYTE at 16:48:22Z

Total initial acquisition:
~98.9694M BYTE = ~9.90% of total supply.

A representative transaction was independently decoded:
- tx from the holder itself;
- holder sends MU to the Pons curve;
- Pons curve transfers BYTE to the same holder.

So these are not one aggregator contract merely making all five balances appear linked.

Immediately after their successful buys, the wallets show nearly identical failed repeat attempts at ~16:48:23-16:48:26Z.

This combination:
- same preparation asset;
- same near-identical native residual;
- repeated synchronized approvals;
- same-second successful acquisition;
- same retry cadence;
is strong evidence of shared automation or deliberate coordination.

It does NOT prove that one person controls all five wallets.

## Current retention / distribution

At the holder snapshot:
- A still held exactly ~24.5710M BYTE;
- B still held exactly ~22.6057M;
- D still held exactly ~14.4394M;
- E still held exactly ~13.8703M;
- C held ~20.0537M versus ~23.4830M acquired, a reduction of ~3.4293M or ~14.6%.

The five-wallet cohort therefore still held approximately:
~95.5402M BYTE = ~9.55% of total supply.

This is a material future distribution overhang.

Four of five sampled cohort members had not reduced their initial BYTE balance at the snapshot.

## Critical Relay false-positive correction

The apparent funding commonality MUST be interpreted carefully.

External explorer labels show:
- 0x370A7E2d... is a very high-throughput Relay solver address;
- 0xf42b73d2... is labelled Relay: Solver 21;
- 0xA5a5491b... has very high-throughput cross-chain / Relay-like history and shares upstream Relay-solver funding with 0x370A... in public explorer metadata;
- 0xa67D7Eb4... has prior Relay Approval Proxy activity.

The common upstream address 0xf70da97812CB96acDF810712Aa562db8dfA3dbEF is itself publicly labelled Relay: Solver.

Therefore:
RELAY_SOLVER -> WALLET funding edges are PROTOCOL_SHARED / ROUTING evidence by default.

They are NOT sufficient to infer common ownership.

However, Relay cannot explain away the entire pattern:
different destination wallets still executed extremely similar amounts, residuals, approvals and final Pons buys in lockstep.

Thus:
COMMON FUNDER EVIDENCE = WEAK / INFRASTRUCTURE-CONTAMINATED.
BEHAVIORAL COORDINATION EVIDENCE = STRONG.

This distinction should become a regression case for the operator-lineage layer.

## Other sampled large holders

Two sampled top holders did not show a BYTE acquisition inside the first ~48 minutes:
- 0x0a6B1858Cb885fDB4eFf074D83fA20EE0B4cC097
- 0x508e08D49DECd97Cc3C3e123de14E6d6A846E85a

At least one has clear prior cross-chain history and is not a fresh BYTE-only address.

This supports preserving a mixed population model:
coordinated pre-positioned cohort + later/possibly independent holders.

Do not turn all current holders into one cabal cluster.

## Market-state update

DEX Screener follow-up snapshot:
- price ~$0.000368;
- MC/FDV ~$346K;
- liquidity ~$54K;
- 24h move ~+642%;
- ~3,739 transactions;
- ~$626K volume;
- 880 traders;
- 2,120 buys / 1,619 sells;
- buy volume ~$321K / sell volume ~$304K;
- 659 buyers / 628 sellers.

There is also visible Telegram/KOL propagation around BYTE.

This means public demand is real enough that the entire market cannot be reduced to the five-wallet cohort from current evidence.

But screeners can overstate organic breadth if wallet rings are present, so raw trader count must remain a descriptive metric.

## Wash-trading benchmark

Bitquery's September 2026 Robinhood investigation provides a useful negative-control signature:
- one-direction wallets;
- exact token hand-offs;
- matching later sellers;
- median ~41s buy-to-matched-sale gap;
- first ETH often coming from another ring wallet.

BYTE's sampled five-wallet cohort currently does NOT reproduce that exact hand-off-ring signature:
- four sampled wallets retained their acquired BYTE rather than forwarding the exact amount to a fresh seller;
- one partially reduced instead of exact hand-off.

Therefore:
BITQUERY_HANDOFF_RING_MATCH = NOT ESTABLISHED.

This does not rule out another form of coordinated accumulation/distribution.

## Updated Alpha Lab classification

CLASSIC_PRIVILEGED_LAUNCH_RUG:
LOWER EVIDENCE / NOT SUPPORTED

RELAUNCH_FAMILY:
CONFIRMED

PRE_POSITIONED_COHORT:
STRONG

BEHAVIORAL_COORDINATION:
STRONG

COMMON_OWNERSHIP:
UNKNOWN

RELAY_INFRASTRUCTURE_CONTAMINATION:
CONFIRMED

WASH_HANDOFF_RING:
NOT ESTABLISHED

OPERATOR / EXTRACTION RISK:
ELEVATED, with a material ~9.55% observed coordinated-cohort overhang

REALIZABLE ADVERSARIAL ALPHA:
The early alpha window was real and materially realized by the pre-positioned cohort.
For a later public participant, much of the asymmetry is already consumed; continuation now depends on public demand versus cohort distribution.

EXECUTION TOXICITY:
UNKNOWN

## Framework learning

BYTE provides a particularly valuable adversarial lesson:

A naive common-funder model would falsely scream "same cabal" because several wallets are funded through Relay-related addresses.

A naive "no bundle/no exemptions" scanner would falsely call the launch clean.

The stronger signal is the temporal behavioral fingerprint:
fund -> convert to pair asset -> approve -> re-approve around relaunches -> final same-second buy -> identical retry cadence.

Candidate feature family:
COORDINATED_PREPOSITIONING_PATTERN

Required primitives:
- common target asset;
- funding time dispersion;
- normalized residual after asset conversion;
- approval timing relative to launch/relaunch;
- buy-time dispersion;
- same method/venue;
- retry-pattern similarity;
- subsequent sell-through / hand-off behavior;
- explicit protocol-infrastructure exclusion.

This feature should remain SHADOW until tested prospectively against matched Pons controls.
