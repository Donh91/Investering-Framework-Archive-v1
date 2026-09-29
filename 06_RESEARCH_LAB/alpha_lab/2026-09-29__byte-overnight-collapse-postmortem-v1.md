# BYTE overnight collapse / postmortem checkpoint v1

Date: 2026-09-29 ~07:34 CEST
Status: LIVE FAILURE / POSTMORTEM CHECKPOINT
Owner: #1087 / Meme Alpha Supervisor
Token: BYTE
CA: 0xd5520D9D777a42D85f94834fbea162B17A197CfB
Pair: BYTE/MU
User reference entry: ~220K market cap
Trade authority: NONE

## Market state

Fresh DEX Screener read at checkpoint:
- market cap / FDV: ~$7.8K
- liquidity: ~$8.1K
- 1h: +24.61%
- 6h: -64.19%
- 24h: -97.83%
- 1h: 46 tx / 43 traders; 13 buys / 33 sells; ~$994 buy vol / ~$572 sell vol
- 6h: 204 tx / 169 traders; 64 buys / 140 sells; ~$2.3K buy vol / ~$5.0K sell vol
- 24h: 1,374 tx / 582 traders; 642 buys / 732 sells; ~$56K buy vol / ~$79K sell vol
- pooled BYTE: ~484.38M on DEX Screener snapshot
- holders displayed: ~503

User entry ~220K -> ~7.8K current MC = approximately -96.5% drawdown before slippage.
Recovery from 7.8K back to 220K would require roughly 28.2x.

This is an economic near-total wipeout even though the exact fraud / operator mechanism remains under investigation.

## Holder / pool structural change

Fresh Blockscout holder snapshot:
- PoolManager: ~428.40M BYTE (~42.84% supply)
- PonsV2LaunchLocker: ~81.63M (~8.16%)
- burn: ~57.36M (~5.74%)
- largest non-system holder: ~30.87M (~3.09%)
- next: ~26.40M (~2.64%)
- prior descendant early-cohort wallet A0686: ~9.997M remains

Earlier checkpoint:
- PoolManager: ~72.05M BYTE
- holders: ~635

Thus PoolManager inventory increased by roughly 356M BYTE while holder breadth fell materially.
This is consistent with massive aggregate selling / return of BYTE to the pool.

## Critical original-cohort update

The five originally identified pre-positioned wallets previously held:
~95.54M BYTE combined (~9.55%).

None of those five appears in the fresh top-50 holder snapshot.

The #50 holder in the fresh snapshot holds only ~1.424M BYTE.

Therefore each original wallet is now below ~1.424M BYTE, implying that at least ~88.4M BYTE of the previously observed ~95.54M has left those five addresses (>92% of their prior combined balance).

IMPORTANT:
This does NOT prove all ~88.4M was sold.
Some may have been transferred to descendant wallets.
The earlier crash-seller ancestry audit already proved that inventory can move through descendant wallets before market exit.

But the prior state "known five-wallet cohort still holds" is now decisively invalid.

## Classification update

CLASSIC LP RUG:
still not independently proven.

PUMP-AND-DUMP / RUG-LIKE ECONOMIC OUTCOME:
STRONGLY SUPPORTED.

ORIGINAL PRE-POSITIONED COHORT STILL HOLDING:
FALSE as of fresh top-holder snapshot.

COHORT INVENTORY MIGRATION / DISTRIBUTION:
CONFIRMED at address level; exact sell-vs-transfer decomposition pending.

MARKET CAPITULATION:
EXTREME.

PUBLIC DEMAND:
severely impaired.

ALPHA WINDOW:
CLOSED.

RECOVERY:
current 1h bounce is insufficient evidence; 6h/24h regime remains destructive.

## Framework failure / correction

The previous monitoring state treated unchanged balances in five known cohort addresses as strong evidence against a rug.
That was too narrow.

The correct state variable must be cluster-level beneficial inventory lineage:
- original cohort wallet;
- descendant wallet;
- transfer relays;
- router hops;
- final market exit.

A cohort cannot be marked HOLDING merely because original addresses did not directly sell.

## New hard research requirements

1. Reconstruct all descendants of the original five wallets after the last good snapshot.
2. Reconstruct all T+6m launch-minute buyers, not only the original five.
3. Attribute each descendant inventory unit to:
   - still held;
   - transferred;
   - market sold;
   - routed / protocol-only;
   - unknown.
4. Calculate cluster-level realized exit timing relative to marketing / catalyst messaging.
5. Freeze the earliest point where a cluster-level distribution warning would have been possible.
6. Backtest whether BENEFICIAL_INVENTORY_LINEAGE would have triggered before the ~70% first crash.
7. Add address-level-HOLDING state as forbidden evidence unless descendant graph is clear.

## Trading-learning conclusion

BYTE must count as a failed prospective adversarial-alpha case, not a success because early expansion existed.

The strategy failed to remove principal before the market collapsed.

The correct future objective is not merely finding coordinated early buyers.
It is finding them AND detecting the first economically meaningful inventory migration/distribution before public capitulation.

No retrospective alpha credit.
