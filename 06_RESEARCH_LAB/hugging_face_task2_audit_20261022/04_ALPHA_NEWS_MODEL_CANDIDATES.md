# Phase 4/5 | Alpha Lab, news and open-model challenger audit

**Status:** research hypotheses only; no buy/sell, token promotion, alpha report claim or live integration.

## Alpha Lab: the highest-value HF use case beyond Task 2
### A. pump.fun prospective-shaped cohort [HF-005]
Repository https://huggingface.co/datasets/Tr4m0ryp/trenches-pumpfun-forward-2026-08.
Native HF Hub inspected config structure: 85.4K features (103 fields), 84.6K labels (17), 730.9K observations (124), 3.7K truth_set (19). Key preview columns: `decision_ms`, `tau__vendor_audit`, `reach_lag_ms`, `reach_derivable_at_decision`, `top_10_holder_rate`, `creator_balance_rate`, `fresh_wallet_rate`; labels `path_status`, `graduated`, `exit_impossible`, `first_seen_ms`. Real preview includes a `path_status=error:not_pulled` and incomplete outcome. This makes explicit error/censor stratification imperative.

Research protocol: age-of-wallet/creator, recycled metadata, funding concentration, early liquidity, T0 creator self-buys and delegated EOA patterns, late API fields, source-visible timestamp. Compare simple prelaunch/screening rules to independently timed labels, with *rug false positives*, launch selection bias, transaction costs, failed exit cases and survivors omitted from launch feeds. Do not blindly train on 103 features. License explicitly **PolyForm Noncommercial 1.0.0**, not a generic unrestricted 'other' license. Source README/DATASHEET disclose 69.09-hour gap, degenerate y_theta_70 label, zero overlap between old curve trade paths and captured tokens, and unavailable at-decision post-reach data. **Do not operationalize or commercially reuse** before license/legal review and independent timestamp/chain validation. See `06_SOURCE_DOCUMENT_RED_TEAM_DELTA.md`. No restricted API data in public repo.

### B. existing Chain of Title continuity [HF-007]
Existing canonical Alpha Lab source-boundary:
`research/api_agent/meme_alpha/CHAIN_OF_TITLE_SOURCE_BOUNDARY_v1.json` and source harvest files. The historical Hugging Face repository `chainoftitle/chain-of-title` currently returned exists=false via connected HF `stat`. This is **SOURCE_ACCESS_ANOMALY**, not proof of deletion, fraud or dataset falsity. Historical frozen deposit reportedly used CC0; subsequent *live* website/API licensing changed. Do not migrate or copy recent live data under older deposit rights. Confirm independent source of the frozen deposit or preserve unavailable status; do not fabricate fallback rows.

### C. ETH/Robinhood/SOL caveat
HF-005 is pump.fun/Solana oriented. It is NOT direct validation of Ethereum, Base or Robinhood Chain first-block alpha; maintain chain-specific smart contracts, fee markets, mempool semantics, block/transaction order and social announcement timestamp. Do not present ETH/Base wallet finding as proven for RH. Expand only through verified comparable source.

## News/Situation Room and narrative controls
- HF-009 `edaschau/bitcoin_news`: scraped Yahoo-linked BTC news, 210.8K rows (2025 last modified). Great for story clustering and negative examples, **weak** as historical first-delivered timestamp. Original publication may differ from scraping.
- HF-010 `zeroshot/twitter-financial-news-sentiment`: 11.9K labelled tweets, MIT-tagged. Good for sentiment label QA and class imbalance, not a predictive trading benchmark.
- Ensure media URL, canonical original publisher, first-publication, our first retrieve time, vendor revision, asset tagging, story family hash, and provenance/confidence are separately recorded. Absent actual first-known must remain unknown.
- Compare against zero-news price-only baseline; test same headline first available after market price move, contradictory/false reports and repeated wire article stories. News from HF is not automatically a Situation Room feed and no live news pipeline is modified.

## Model candidates, open weights / independent critics
| Candidate | Link / task | Initial verdict |
|---|---|---|
| Amazon Chronos-Bolt-Small, 47.7M parameters, Apache-2.0 | https://huggingface.co/amazon/chronos-bolt-small | **P2 research-only time-series baseline**, seasonal-naive vs Chronos with stringent walk-forward and pretraining contamination checks; no production forecast authority. |
| Amazon Chronos-2 / small | https://huggingface.co/amazon/chronos-2 ; https://huggingface.co/autogluon/chronos-2-small | **P3**, broader time-series challenger with higher compute; avoid when a much simpler control answers the question. |
| ProsusAI/finbert, ~109.5M parameters, CC-BY-NC-SA-4.0 tag | https://huggingface.co/ProsusAI/finbert | **RESEARCH/LICENSING HOLD**: non-commercial/share-alike license must be reviewed for our intended use; English finance domain ≠ crypto causality. |
| yiyanghkust/finbert-tone | https://huggingface.co/yiyanghkust/finbert-tone | **P2 research** sentiment challenger; pin licensing from model card before deployment. |
| sentence-transformers/all-MiniLM-L6-v2 | https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 | **P1 candidate** cheap semantic near-duplicate clustering/embeddings for news and source notes, provided license and infra pass. Compare simple normalized-URL/title hash first. |

## Evaluation not model worship
A transformer can be a useful *tool to detect duplicates* without providing market alpha. Require adversarial holdout set, real no-lookahead news arrival, latency budget, rate/cost budget, false positives, abstention, negative-control pass and license acceptance. Freeze training data time boundary and exclude duplicates across train/test. A code demo, popular model or market forecast demo Space is not an independently validated trading strategy.

## Security and sandbox rules
All third-party HF repository files/model weights/dataset scripts are untrusted. Do not execute arbitrary dataset loader remote code or Space demos with private tokens, GitHub write credentials or restricted market data. Prefer `parquet` direct read with schema validation and revisions pinned. Review `trust_remote_code` and external code paths explicitly. No auto deployment, training or paid inference from connector merely because scopes say `jobs` or `inference-api`.
