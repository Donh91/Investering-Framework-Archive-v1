# S7 Execution Receipt - 2026-10-06

Status: ATTENTION_EVENT_TRUTH_MERGED / RESPONSE_JOIN_PENDING / RESEARCH_ONLY
Master issue: #1512
Execution issue: Meme Alpha #109
Merged PR: Meme Alpha #110
Merge commit: 3f365f20fca9f2876204ddb29a07e8782b8c609e

## Result

S7 now has a deterministic on-demand attention-event normalizer over the existing canonical v4 ephemeral tape.

No duplicate attention database was created.

Supported raw surfaces:
- DexScreener PROFILE
- DexScreener BOOST
- GeckoTerminal TREND / SOL_TREND

Normalized event semantics:
- first machine-observed state;
- later changed state;
- unchanged consecutive state suppressed;
- A -> B -> A state reversions preserved.

## Full-tape readiness result

CI replay of the existing prospective archive produced:

- total normalized attention events: 13,706
- unique chain + token pairs: 6,696
- first-observed events: 7,153
- change events: 6,553

By class:
- DEX_PROFILE_FIRST_OBSERVED: 4,098
- DEX_BOOST_FIRST_OBSERVED: 2,438
- DEX_BOOST_CHANGE_OBSERVED: 534
- GECKOTERMINAL_TREND_FIRST_OBSERVED: 617
- GECKOTERMINAL_TREND_CHANGE_OBSERVED: 6,019

By chain:
- base: 1,704
- bnb-chain: 1,909
- ethereum-mainnet: 1,833
- robinhood-chain: 2,234
- solana: 6,026

## Important semantic boundaries

PROFILE != PAID_PROFILE.
BOOST != organic attention.
observed_at_utc != exact upstream activation time.
embedded social links != verified social-post timestamps.
raw ephemeral v4 tape remains canonical.

A full-tape CI failure initially exposed nested archive layout (v4/YYYY/MM/DD.csv); normalizer was corrected to recursive scanning. A second audit also corrected dedupe so A -> B -> A state changes are retained.

## Next evidence

The event denominator is ready.

Next S7 research should join these frozen attention events to:
- qualified-wallet arrival/exit;
- Pons buyer/retention flow on Robinhood where available;
- liquidity/price outcomes;
- S6 egress/distribution;
- verified social timestamps when independently available.

Only after those joins can states such as WALLET_LED_PRE_ATTENTION, ATTENTION_LED_CONVERSION, DISTRIBUTION_INTO_ATTENTION or LATE_ATTENTION_AFTER_MOVE be evaluated.

Current edge state:
INSUFFICIENT_JOINED_OUTCOME_EVIDENCE.

## Authority

No portfolio action.
No alert authority.
No auto execution.
No candidate promotion.
