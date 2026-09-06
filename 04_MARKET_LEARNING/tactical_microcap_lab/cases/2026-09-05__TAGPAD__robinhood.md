# TAGPAD - Robinhood Chain - first Tactical Microcap Lab case

**Record type:** point-in-time audit + later outcome review  
**Initial audit date:** 2026-09-05  
**Follow-up:** 2026-09-06  
**Authority:** ADVISORY_ONLY

## Identity

```text
token: tagpad / TAGPAD
chain: Robinhood Chain
contract: 0x1998e567d1ea5aab594250db38522cdbe95bef0c
pair: 0xd2c134455e4e93f21ee67cafa763b6b1861bc701cb98f1141033d1bd9956632e
venue: Pons V2 launch -> Uniswap V4
```

## What the project was

TagPad offered a simple narrative: an authenticated social `@` could be launched as a token through Pons V2 on Robinhood Chain. TagPad itself claimed no custom launch contract in the transaction path, with the wallet interacting with Pons directly.

The narrative was easy to understand and potentially memeable, which made the project more interesting than a purely anonymous random microcap.

## Launch evidence

The TAGPAD launch transaction was observed at:

```text
2026-09-05T17:00:45Z
```

The token was created through the verified `PonsV2LaunchAndBuy` path. The creator / recipient wallet bought roughly 15 million TAGPAD at launch, around 1.5% of the 1 billion supply.

Three addresses were present as launch-time snipe-tax exemptions. In the first audit, the creator wallet and two of the three checked exempt wallets no longer held TAGPAD. The third exemption could not be reliably checked because the explorer request failed.

This did not prove an organized pump-and-dump, but it materially weakened the entry setup because privileged launch participants appeared to have already exited while price was still falling.

## Initial market snapshot

Approximate first-audit snapshot:

```text
market cap: ~$22.2k
liquidity: ~$13.8k
24h / since-launch volume: ~$28.6k
1h buys: 153
1h sells: 171
1h price change: ~-56.2%
```

The token was already extremely small and mathematically capable of violent upside, but the chart and wallet evidence showed active distribution rather than a credible base.

## Initial recommendation

```text
DECISION = WAIT
```

Reason:

```text
interesting narrative
+ very low market cap
+ technically legitimate launch path
- creator / privileged-wallet exit evidence
- sellers still dominant
- no base
- no reversal
- falling-knife structure
```

The preferred setup was to accept a higher market cap later if price first formed a base, higher low, reclaim and returning volume.

## Follow-up - 2026-09-06 around 21:45 CEST

User-provided Dexscreener screenshots showed approximately:

```text
market cap: $3.3k
FDV: $3.3k
liquidity: $5.4k
24h price change: -93.31%
6h price change: -2.31%
transactions: 536
buys: 226
sells: 310
volume: $44k
buy volume: $18k
sell volume: $25k
traders: 262
buyers: 137
sellers: 230
pooled TAGPAD: 787,698,861
pooled ETH: 1.080
```

The chart showed no meaningful reversal after the first audit. Instead it continued down from roughly the low-$20k market-cap area toward roughly $3.3k.

Approximate further decline after the first `WAIT` call:

```text
~$22.2k -> ~$3.3k = about -85%
```

## Decision-quality review

The outcome strongly supports the original `WAIT` decision, but the lesson is process-based rather than outcome-based.

The important evidence at the time was already available:

```text
large drawdown was not a bottom signal
privileged launch-wallet exits mattered
sell pressure had not exhausted
no base or higher low existed
low market cap did not compensate for structural distribution
```

The case should therefore be remembered as:

> A compelling meme narrative plus tiny market cap can still be a bad entry. In a falling microcap, confirmation can be worth paying a higher price for.

## Current tactical interpretation at follow-up

At roughly $3.3k market cap the token became more asymmetric as a pure revival lottery, but not automatically more investable.

A future speculative-buy case would require evidence of life, for example:

```text
base around the lows
volume returning
seller exhaustion
higher low
reclaim into roughly $5k-$6k+ market-cap territory
improving buyers versus sellers
fresh TagPad / Robinhood meme catalyst
```

Absent those changes, the correct state remained `WATCH / WAIT`, not `BUY_BECAUSE_DOWN_93_PERCENT`.

## Sources preserved

- TagPad documentation: https://www.tagpad.fun/#docs
- Robinhood Chain Blockscout token: https://robinhoodchain.blockscout.com/token/0x1998e567d1ea5aab594250db38522cdbe95bef0c
- Dexscreener pair: https://dexscreener.com/robinhood/0xd2c134455e4e93f21ee67cafa763b6b1861bc701cb98f1141033d1bd9956632e
- Initial and follow-up evidence discussed in the user token-audit thread on 2026-09-05 and 2026-09-06.

## Governance note

This case is learning evidence for speculative microcap analysis only. It does not alter canonical portfolio state, Master Monday, Data Ping, long-conviction holdings, thresholds or weights.
