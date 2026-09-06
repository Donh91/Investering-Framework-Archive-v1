# Token Audit Guide v1

**Role:** minimum audit guide for high-risk tactical microcap / meme / YOLO / casino plays.  
**Mode:** evidence-first, short-horizon, non-conviction.  
**Rule:** this guide is a floor, not a ceiling. Follow additional evidence whenever it becomes relevant.

## 1. Identity and legitimacy

Confirm before analysis:

- correct chain;
- exact contract address;
- exact trading pair / launch venue;
- token name and symbol;
- official site and social links where available;
- whether the token is original, copied, impersonated or ambiguous.

Never rely on ticker or branding alone.

## 2. Contract and control risk

Inspect, where applicable:

- verified source / known factory;
- proxy / upgradeability;
- mint authority;
- freeze / blacklist / pause;
- transfer restrictions;
- tax / fee controls;
- owner privileges;
- honeypot-like restrictions;
- liquidity / pool mechanics;
- launchpad-specific behavior.

Known launch factories may reduce custom-contract risk, but they do not remove market, insider or liquidity risk.

## 3. Launch forensics

Capture the launch as a point-in-time event:

- launch timestamp;
- launch transaction;
- deployer / creator;
- opening buy size;
- launch configuration;
- privileged / tax-exempt / bundled wallets;
- initial distribution;
- bonding-curve graduation if relevant;
- initial liquidity migration.

Then inspect what those wallets did afterward.

## 4. Wallet graph and insider evidence

Trace the economically relevant wallets, not just the top-holder list.

Check for:

- common funding source;
- synchronized buys or sells;
- repeated launch participation;
- shared counterparties;
- transfers between wallets;
- tax exemptions or whitelist relationships;
- creator funding of third-party wallets;
- prior tokens launched or traded by the same wallets;
- current balances versus launch balances.

Use graded language:

```text
CONFIRMED_RELATIONSHIP
STRONGLY_LINKED
PROBABLE_CLUSTER
POSSIBLE_LINK
UNKNOWN
```

Do not call a wallet an insider merely because it bought early.

## 5. Holder structure

Report holder concentration after separating addresses that can distort the picture:

- LP / pool manager;
- launch locker;
- burn address;
- bridges;
- protocol contracts;
- known exchange / vault contracts.

Then evaluate real-wallet concentration and whether a small number of actors can dominate the exit.

## 6. Market state now

Use fresh data whenever the decision concerns an entry now.

Capture at least:

- price;
- market cap / FDV;
- liquidity;
- quote-side liquidity if obtainable;
- 5m / 1h / 6h / 24h price path as relevant;
- volume;
- buys versus sells;
- buy volume versus sell volume;
- unique buyers versus sellers;
- holder count / holder trend when available;
- age of pair;
- current chart structure.

Do not infer a bottom from percentage drawdown alone.

## 7. Liquidity and realistic exit

Estimate whether the intended trade size can actually be entered and exited.

Important questions:

- How large is quote liquidity?
- What share of pool liquidity would the intended order consume?
- Is displayed market cap mostly theoretical?
- What slippage is plausible on entry and exit?
- Could several holders front-run the exit?
- Is liquidity rising, stable or being removed?

Treat an unrealizable paper multiple as lower-quality upside.

## 8. Narrative and distribution

Explain the idea in one sentence.

Then test:

- Is it understandable instantly?
- Is it memeable?
- Is the chain / sector / celebrity / event narrative active now?
- Is there an identifiable catalyst?
- Is social activity organic or mostly promotional?
- Are KOLs / Telegram sources early, late or likely exit liquidity?
- Is the token the cleanest expression of the narrative or merely one copy among many?

A good story is a distribution advantage, not proof of value.

## 9. Telegram / connected-source context

A well-connected call is useful as a discovery and timing signal, not as independent proof.

When a play originates from Telegram or another private group, record only the decision-relevant context supplied by the user, for example:

- when it was shared;
- whether the source claims insider / team access;
- expected catalyst;
- expected time horizon;
- whether the source historically appears early or late.

Never convert an unverifiable claim of insider access into confirmed evidence. On-chain behavior should be used to challenge or support the claim where possible.

## 10. Entry quality

For a falling knife, look for evidence of actual transition rather than hope:

```text
base
seller exhaustion
higher low
reclaim
volume return
better buyer/seller balance
holder stabilization
new catalyst
narrative revival
```

A higher confirmed entry can have better expected value than an earlier, cheaper entry into continuing distribution.

## 11. Exit logic

These are temporary trades by default.

Before calling an entry attractive, identify:

- what invalidates the setup;
- what would make immediate de-risking rational;
- where liquidity becomes the binding constraint;
- whether partial profit-taking into strength is preferable to waiting for a single target;
- what evidence would justify holding beyond the original short horizon.

Do not silently convert a failed swing into a long-term investment thesis.

## 12. Asymmetry

Translate market cap into simple scenario math where useful:

```text
2x target market cap
5x target market cap
10x target market cap
25x target market cap
100x target market cap
```

Then ask whether those levels are plausible given:

- liquidity;
- historical peak;
- narrative reach;
- holder structure;
- comparable tokens;
- chain activity;
- available catalysts.

A mathematically possible 100x is not automatically a realistic 100x.

## 13. Decision vocabulary

Every full audit ends with one of:

```text
BUY
SPECULATIVE_BUY
WAIT
REJECT
```

And should state, in plain language:

- why;
- what would change the decision;
- the major invalidation;
- the main upside mechanism;
- the largest hidden risk found.

## 14. Default user-facing output

Keep the visible answer easy to act on even when the underlying investigation is deep.

Preferred order:

1. one-line verdict;
2. what the token actually is;
3. current numbers;
4. strongest positive evidence;
5. strongest red flags;
6. wallet / insider findings;
7. entry assessment;
8. simple upside math;
9. exact `BUY / SPECULATIVE_BUY / WAIT / REJECT` conclusion.

Avoid filling the answer with framework jargon unless it directly improves the decision.

## 15. Learning record

For each material audit, preserve enough contemporaneous evidence to evaluate the advice later without hindsight.

Minimum record:

```text
snapshot_utc
chain
contract_address
pair_address
market_cap
liquidity
volume
price_path
wallet_findings
narrative_state
recommendation
recommendation_reason
invalidation
source timestamps / URLs where available
```

Outcome review should distinguish:

```text
good decision + good outcome
good decision + bad outcome
bad decision + good outcome
bad decision + bad outcome
```

The purpose is to improve decision process, not maximize hindsight hit-rate.
