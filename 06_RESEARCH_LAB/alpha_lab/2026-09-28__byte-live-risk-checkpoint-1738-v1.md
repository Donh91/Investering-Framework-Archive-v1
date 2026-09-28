# BYTE live risk checkpoint — 2026-09-28 17:38 CEST

Status: LIVE POSITION MONITORING / SHADOW
Owner: #1087 / Meme Alpha Supervisor
Token: BYTE
CA: 0xd5520D9D777a42D85f94834fbea162B17A197CfB
Pair: BYTE/MU
User reference entry: ~220K market cap
Trade authority: NONE

## Live market snapshot

DEX Screener at checkpoint:
- price: ~$0.0002462
- market cap / FDV: ~$232K
- liquidity: ~$43K
- pair age: ~22h
- 1h: -8.98%
- 6h: -17.43%
- 24h: +396%
- 24h volume: ~$689K
- 24h traders: 971
- 24h buys/sells: 2,421 / 1,921
- 24h buy/sell volume: ~$351K / ~$338K
- 6h: 185 buys / 193 sells; ~$19K buy / ~$21K sell
- 1h: 16 buys / 15 sells; ~$810 buy / ~$1.5K sell
- last 5m snapshot: 3 buys / 3 sells; ~$56 buy / ~$934 sell

Interpretation:
- short-term sell pressure is elevated;
- this is a material pullback from earlier ~346K checkpoint;
- current MC is still close to the user's ~220K reference entry;
- no evidence of a liquidity-removal rug solely from this Dexscreener state.

Displayed liquidity fell from the earlier ~$54K checkpoint to ~$43K, but Uniswap v4 concentrated liquidity and price movement can change displayed active liquidity. This is not sufficient by itself to infer LP removal.

## Known coordinated cohort: fresh balance check

Current Blockscout holder snapshot:
- A 0x131219...: 24.5710386M BYTE
- B 0x3F8D24...: 22.6056561M BYTE
- C 0x9AEC8E...: 20.0537347M BYTE
- D 0x0e622a...: 14.4394005M BYTE
- E 0xe07af4...: 13.8703361M BYTE

Combined:
~95.5402M BYTE = ~9.55% total supply.

These balances are unchanged versus the previous coordinated-cohort snapshot.

Fresh BYTE transfer query since 2026-09-28T00:00Z:
- A: no BYTE transfer
- B: no BYTE transfer
- D: no BYTE transfer
- E: no BYTE transfer
- C: one small incoming ~0.34208M BYTE at 02:49:48Z; this was already reflected in the previous snapshot.

Therefore:
KNOWN_COHORT_COORDINATED_DISTRIBUTION = NOT OBSERVED

This is the strongest current evidence against calling the present pullback a rug by the known cohort.

## Holder breadth

Blockscout token metadata at the fresh query showed ~591 holders versus ~635 during the earlier follow-up.

This suggests holder count has contracted by roughly 7% from that earlier observation.

Do not equate holder count with independent buyers: wallet rings, EIP-7702 wallets and system addresses remain confounders.

## New operator-link evidence

The launch wallet transferred BYTE creator-fee-recipient rights at 2026-09-27T16:59:55Z.

Decoded transaction:
0xa93ce0b08e8af571375d1fd8ba00040de3b3d7acd0cf5c48d73bf690cde27a60

Token:
0xd5520D9D777a42D85f94834fbea162B17A197CfB

New creator-fee recipient:
0xB3a5f38A73b611C78FE40E0c0CF182428c877322

Important:
This same B3a5f... address had already appeared repeatedly in the sampled cohort wallet histories as the sender of ERC-8056 activity to multiple cohort members at synchronized times after launch.

This materially strengthens the hypothesis that the cohort and token operator share an economic/automation relationship.

It does NOT prove common legal ownership or fraud.

Current state:
OPERATOR_COHORT_LINK = STRONGER_THAN_PRIOR
COMMON_OWNER_IDENTITY = UNKNOWN

## Rug / distribution assessment

CLASSIC LIQUIDITY RUG:
NOT OBSERVED

KNOWN COHORT DUMP:
NOT OBSERVED

CREATOR INITIAL SUPPLY DUMP:
NOT OBSERVED; original ~5.74% creator allocation was burned.

OPERATOR / CABAL EVIDENCE:
ELEVATED -> STRONGER, due creator-fee-recipient link plus prior synchronized behavior.

SHORT-TERM SELL PRESSURE:
ELEVATED

HOLDER ATTRITION:
ELEVATED / WATCH

PUBLIC DEMAND:
still present over 24h, but recent windows are weaker.

## Current shadow state

RUG_NOW = NO_EVIDENCE_OF_CONFIRMED_RUG
RUG_RISK = ELEVATED
DISTRIBUTION_RISK = ELEVATED_BUT_NOT_TRIGGERED_BY_KNOWN_COHORT
ALPHA_WINDOW = NARROWER_THAN_EARLIER
COHORT_OVERHANG = ~9.55%
MARKETING_CATALYST = ANNOUNCED_AND_FUNDED
CREATOR_FEE_COHORT_LINK = STRONG_EVIDENCE

## Critical next trigger

Escalate to DISTRIBUTION_ALERT if any of:
- 2+ known cohort wallets reduce materially within a short interval;
- combined cohort balance falls >10% from ~95.54M without benign explanation;
- B3a5f-linked proceeds / creator fees converge with cohort exits;
- liquidity falls sharply together with linked selling;
- holder breadth and independent demand collapse while cohort distributes.

Until then, a falling chart alone is not enough to label the event a rug.
