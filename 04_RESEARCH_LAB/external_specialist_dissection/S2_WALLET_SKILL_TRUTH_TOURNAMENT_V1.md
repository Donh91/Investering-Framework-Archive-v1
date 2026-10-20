# S2 - Wallet Skill Truth Tournament v1

Status: ACTIVE_RESEARCH_SPEC / P0 / RESEARCH_ONLY
Master queue: README.md
Master issue: #1512
Execution owner: Donh91/Meme-Alpha-Lab existing Wallet Alpha Protocol

## Trigger

External Specialist Dissection identified GMGN as a high-value public specialist.

Unlike many specialist products, GMGN publishes an MIT-licensed agent/CLI repository containing deterministic wallet-analysis and wallet-score logic:
- GMGNAI/gmgn-skills
- skills/gmgn-wallet-analysis/analyze.py
- skills/gmgn-wallet-score/SKILL.md
- skills/gmgn-wallet-style/SKILL.md
- skills/gmgn-track/SKILL.md

This lets Research Lab study exact public decision logic rather than infer it from UI behavior.

## Core decision

Do NOT import GMGN's Smart Money label or final wallet score as truth.

Transfer the strongest primitives into challenger research and benchmark them against Alpha Lab's complete wallet replay.

## Four dimensions worth separating

GMGN's wallet-analysis implementation explicitly separates:

1. AUTHENTICITY
   Is the reported record representative, or dominated by self-dealing / tiny sample / one lucky token / concentrated profit?

2. CURRENCY
   Is the historical edge still active now?

3. REACHABILITY / COPYABILITY
   Could an independent follower enter before the source wallet exits, at realistic size/friction?

4. SURVIVABILITY
   Does the wallet contain losses, or repeatedly ride positions toward zero?

This separation is more valuable than a blended Smart Money score.

## Existing Alpha overlap

Already owned:
- complete winner + loser portfolio replay target;
- median return and realizable exit;
- entry/exit percentile;
- funding/relationship evidence separated from skill;
- leader/follower research;
- skill decay;
- prospective wallet freeze;
- no insider label from early entry alone.

Therefore do not create a new wallet engine.

## Missing / underformalized primitives

### W1 PROFIT_CONCENTRATION_TRUTH

Question:
Is apparent wallet skill carried by one/few extreme winners?

GMGN public logic treats extreme concentration as an authenticity problem and explicitly rejects tiny samples.

Alpha implementation target:
freeze:
- total realized positive PnL;
- top-1/top-3 contribution to positive PnL;
- number of independently resolved tokens;
- winner count;
- loser count;
- concentration after realistic exit constraints.

Test:
Does concentration improve luck-vs-repeatable-edge discrimination beyond token count, median return and win rate?

Do not import GMGN's 75% threshold. Estimate/validate internally.

### W2 EDGE_CURRENCY / SKILL_DECAY

Question:
Is the wallet still good, not merely historically famous?

Candidate features:
- 1d/7d/30d/all-time realized expectancy;
- recent-vs-long-run delta;
- recent trade count;
- time since last qualifying edge event;
- decay after provider/market discovery;
- regime-conditioned performance.

Alpha already owns WALLET_SKILL_DECAY. This lane should strengthen that owner, not duplicate it.

### W3 COPY_WINDOW_V1

Strong transfer.

GMGN computes a copy window from first buy to first sell per token and uses the median across round trips.

Important public-code learning:
GMGN later warns against trusting API average holding period because unsold bags can inflate it massively. Median first-buy -> first-sell can be a much more faithful copyability measure.

Alpha target:
for each wallet/token round trip freeze:
- first qualifying buy timestamp;
- first sell timestamp;
- first full/meaningful exit timestamp where reconstructable;
- median and lower-quantile copy window;
- source-to-observer detection latency;
- follower routing/fill latency;
- entry price drift during that latency;
- available liquidity/capacity.

Core quantity:
`COPYABILITY_MARGIN = copy_window / end_to_end_observation_and_fill_latency`.

GMGN uses a 3x latency margin as a heuristic. Preserve it as an external challenger threshold only. Re-estimate from Alpha data.

### W4 ENTRY_REACHABILITY

Separate predictive selection from whether the source wallet entered at a price a follower could obtain.

Features:
- entry mcap distribution;
- entry percentile among independent buyers;
- liquidity at source entry;
- price drift at +5s/+15s/+30s/+60s;
- source trade size versus follower size;
- slippage and gas;
- pre-graduation / sniper state.

GMGN uses concrete heuristics such as very low median entry mcap, tiny average buys, high gas drag and extreme trades/day as copyability vetoes.

Treat these thresholds as hypotheses, not canon.

### W5 SURVIVABILITY / LOSS_DISCIPLINE

Question:
Does the wallet's positive expectancy survive its left tail?

Features:
- share of completed/resolved tokens below -50%;
- count/share below -90%;
- loss duration;
- zero-sell severe-loss positions;
- MFE surrendered;
- realized versus unrealized tail losses;
- liquidity-adjusted exit feasibility.

GMGN uses a >=35% heavy-loss-share heuristic and a >=3 ride-to-zero heuristic.

Do not import those cutoffs. Test continuous distributions and preregister thresholds later if justified.

### W6 SELF_AUTHORED_DEV_WALLET

A creator/deployer wallet trading its own launches must not be scored as an ordinary market selector.

This is strongly compatible with Alpha governance.

Freeze:
- share of traded tokens created/launched by the wallet/entity;
- creator/deployer/launcher identity confidence;
- outcomes of its own launches;
- trades in unrelated tokens separately.

Trading skill on self-authored tokens and developer reputation are distinct outcomes.

### W7 SECURITY_LABEL_FALSIFICATION

Useful cross-link to S1.

GMGN's public wallet analysis explicitly notes that a live "honeypot" holding can be a false positive if the wallet has completed sells in that same asset.

Alpha principle:
actual executable sell evidence can falsify a static unsellable label at the tested time/state.

Do not generalize a historical sell to current sellability without a fresh state check.

## Provider-label tournament

Provider labels to challenge where lawful/available:
- GMGN Smart Money;
- GMGN KOL;
- GMGN Sniper / Bundler / related tags;
- later Nansen/Fomo/Kolscan/Cielo challengers if source audit earns them.

For every frozen provider label:
- provider;
- wallet;
- chain;
- label;
- first observed UTC;
- provider evidence fields if exposed;
- internal wallet state at cutoff;
- later complete replay/maturation;
- disagreement class.

X0 DISAGREEMENT_ALPHA consumes disagreements.

## Cohort design

Start with three cohorts:

A. Alpha known candidates
Use existing TOP10_MEME_WALLET_ALPHA_V1 wallet seeds with exact addresses.

B. GMGN-labelled active wallets
Bounded prospective sample from public/platform-tagged Smart Money when source access is admitted.

C. Negative/control wallets
Matched active wallets by chain, token universe, activity level and approximate capital that are not selected merely because they became famous winners.

Exclude infrastructure and project treasuries from trader-skill scoring.

## Primary outcomes

- complete-history post-cost expectancy;
- median token return;
- hit distribution;
- top-1/top-3 profit concentration;
- left-tail loss share;
- MFE captured / surrendered;
- realized exit quality;
- copyability at fixed delays;
- skill persistence into forward-frozen trades;
- false-positive / false-negative rate of provider labels.

## What is immediately reusable without GMGN API admission

Because the public repo exposes deterministic method logic, these research methods can be specified now:
- PROFIT_CONCENTRATION_TRUTH;
- COPY_WINDOW;
- ENTRY_REACHABILITY;
- SELF_AUTHORED_DEV_WALLET separation;
- SURVIVABILITY decomposition;
- unmeasured != pass/fail discipline.

Actual GMGN labels/data remain source-audit dependent.

## Public-code operational learning

GMGN's public implementation also contains a useful non-alpha engineering pattern:
under rate limits, fetch verdict-critical inputs first and best-effort depth second.

This should inform source callers but does not constitute market edge.

## Falsifiers

Reject/demote a transferred primitive if:
- complete-history replay subsumes it;
- it is only a disguised activity/liquidity proxy;
- apparent effect disappears after matching on token universe and regime;
- copy-window adds no value once exact price-drift/capacity is modeled;
- provider label does not outperform matched unlabeled wallets prospectively;
- threshold effect is unstable around adjacent cutoffs.

## Next implementation

1. Extend WALLET_ALPHA_PROTOCOL with the four-axis distinction.
2. Register missing method IDs only if not already owned.
3. Build a deterministic copy-window/profit-concentration evaluator on existing replay rows when INDEXED_WALLET_PORTFOLIO_V1 is available.
4. Run GMGN source audit separately before ingesting live provider labels.
5. Freeze a bounded cohort and retain all disagreements.
6. No score promotion until forward outcomes mature.

## Authority

Research only.
No copy-trading.
No wallet signing.
No provider label becomes truth.
No automated trade execution.
