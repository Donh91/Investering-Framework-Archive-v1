# 07 · INDEPENDENT POPULATION BASELINES, POST-FREEZE

This new source review comes AFTER frozen case/hypothesis commit 5cca38e4c3ec2b5af1b43a5b0fa2566a1bff76fc. These are externally published research observations, **not** this project's independently recreated dataset, nor evidence any of the nine case-specific teams belong to a cabal. Source study dates and cohort sampling differ; never update the frozen 00 predictions in light of findings.

## B1 · Academic cross-chain manipulation baseline (NOT cabal prevalence)

Mongardini & Mei, A Midsummer Meme's Dream (2025 arXiv, 2026 USENIX Security): https://www.usenix.org/conference/usenixsecurity26/presentation/mongardini and https://arxiv.org/abs/2507.01963

Study reports **34,988** Ethereum, BNB Chain, Solana, Base token samples tracked for a 3-month interval. Within its **high-return (>100%)** subset, about **82.89%** were detected with algorithmic artificial-growth signatures such as wash trading or low-depth liquidity-pool price inflation. **Interpretation limitation:** Not 82.89% of ALL memecoins, not 82.89% of RHC, not a rate of identified malicious human insiders, not proof any of nine handpicked winners were manipulated; detection criteria and sample frame must be reproduced before applying.

Test: reserve-adjusted price impact and funded roundtrips vs equal-venue liquidity/age controls, avoid equating apparent high trading volume with economic utility.

## B2 · Solana Pump.fun initial bundles — large external cohort Oct10 2026

Bitquery, Pump.fun devs' bundles made $579M+, snipers just $31.5M: https://bitquery.io/investigations/pump-fun-snipers-bundles

8,212,568 new Pump.fun first-trade launches in the observable interval 2025-10-30 to 2026-10-07 (13 archive-gap days and part of May and October excluded). **38%** had a nondev wallet buying in initial block; **21%** had dev-associated buys in the first bundle according to defined heuristics; those bundles took median **10%** first tokens; **28%** contained repeat-launch sniper bots; developer first sale came within **1 minute in 65%**. For launches up to June only, dev+bundle realized at least **$579m** on sold positions versus sniper wallets **$31.5m** on sold positions (only $15.2m with unsold at zero). Authors explicitly omit Jito tips, failed fee tx and some downstream seller links, and classify wallet behavior NOT named human owners.

Method: dev's own tx, dev-paid fee or four slots after launch, with public Jito bundle validation of 185/186 first-four positions in sampled bundle day vs 0/139 beyond. **It does not prove wallet ownership; third-party bundling services can package different accounts.**

Crucially these 2025/26 observations CANNOT serve as directly matched original launch evidence for 2022 BONK, 2023 WIF or 2024 FARTCOIN. They suggest tests for future Solana cohorts, nothing more.

## B3 · Robinhood Chain synthetic buyer/seller rings

Bitquery, Robinhood Chain Wash Trading: 26,000 Wallets Faked $322.5M, sample 2026-08-24 to 2026-09-22: https://bitquery.io/investigations/robinhood-chain-wash-trading-hand-off-ring

For EIGHT investigated Robinhood memes, **25,916** wallets traded buy-only or sell-only, registering **$322.5m**, and **98.5%** of one-trade buys had equal-quantity one-trade sells around median 41 seconds later. Some transactions establish exact buy -> transfer -> separate wallet sell -> ETH recycling chain. Other $947m low-fee circular volumes were reported. **99.8% fake trading applies only to the eight specifically examined tokens, NOT all Robinhood liquidity.**

Novel false-positive trap: independent-EOA COUNT and self-wallet wash-detection both fail when fresh buyer A acquires, sends full amount to B, B sells and ETH is relayed to C. Need direct transfer graph/ETH reuse and exact causal sequence before labelling a synthetic ring; matching quantity and close timestamps alone can coincide in thin markets and do not establish a common person. Our ASKR/MINTFOLIO/HARMONIC cases are NOT individually proven members of this sample.

## B4 · Creator-funded Solana snipes as a bounded secondary research hypothesis

Pine Analytics, Exit Liquidity Machines (Apr21 2025): https://pineanalytics.substack.com/p/exit-liquidity-machines

Report claims more than 15k SOL realized profit from creator funding / rapid sniper-pattern sales across >15k launches with thousands of involved wallets. Useful as a method for same-block buy plus dev-source direct funder reconstruction. Cohort and exact wallets NOT independently reconstructed by this research, and cannot be used as proof of FARTCOIN's original creator selling behavior.

## Freeze-preserving new adversarial feature tests

| Candidate pattern | Falsifier/confirming source | Important confounder |
| --- | --- | --- |
| Creator + same launch bundle | Public launch/Jito tx commitment and sender fee payer | unrelated bundle submission service; no owner proof |
| Same funder prelaunch + close synchronized buys | Funding direction and source receipt | shared CEX/bridge/LP |
| Buyer transfers full tokens to different seller within 60s + ETH relay | Exact same token qty, recipient transfer and descendant ETH | OTC/normal treasury distribution, collisions |
| Volume high but liquidity shallow | Pool reserves and price impact per real swap | healthy small market early in discovery |
| Developer first sale vs independent retention | Actual first founder sales, retained independent buyers t+30m+6h | airdrop, LP graduation and bridging |
| Apparently smart wallet across coins | ALL eligible trades and realized exits including misses | survivorship / sample selected whales |

**No model promotion** without an independent, complete chain- and venue-matched control cohort and source timestamp verification; all labels from these providers are RESEARCH_INPUT_PENDING_RAW_VERIFICATION. Do not assign insider identity or criminal intent; neither high returns nor bundling alone is a conviction.

**Scientific direction:** specifically try to make a naive early-buyer-count system falsely pass synthetic relay-rings and compare with a transfer-flow adjusted persistence filter; pre-register missed-right-tail costs for organic winners and rate limits before deciding whether the extra data collection is worth doing. Existing Alpha Lab #88 and Archive #1340 only, no duplicate scanners.
