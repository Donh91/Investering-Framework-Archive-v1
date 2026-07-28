# Global Liquidity Causal Chain, agent work packages v1

## Control rule

Agents execute in order. A later package may prepare code but may not publish economic results before all prerequisite states pass.

## GLC-WP01, source recovery and contracts

**Owner:** Codex implementation, ChatGPT review.

Deliver:

- immutable source contract for every dataset in `SOURCE_REGISTRY_v1.json`;
- exact endpoint or archive path;
- units, frequency, observation period and publication lag;
- acquisition receipt and SHA-256;
- row-count, gaps, duplicates and revisions;
- rights and redistribution classification;
- owner, challenger or blocked status.

Priority:

1. recover the exact final master binary already named by Backtest Readiness;
2. Nasdaq official or FRED daily history;
3. BEA/FRED actual interest payments;
4. CBO projection vintages;
5. Treasury maturity and issuance;
6. BIS Global Liquidity Indicators;
7. official broad-money and central-bank series;
8. ALFRED or archived release vintages.

Stop instead of substituting when the original source contract cannot be met.

## GLC-WP02, point-in-time normalisation

Build:

- monthly and weekly owner tables;
- native-currency and USD models separately;
- FX contribution decomposition;
- `knowledge_at_utc` fields;
- publication-lag validation;
- no silent forward fill;
- local recent FRED ZIP as an engineering fixture only.

Pass requires deterministic source-to-normalised parity.

## GLC-WP03, statistical engine validation

Synthetic fixtures only until G15 passes.

Implement and test:

- unit-root and cointegration workflow;
- rolling correlation and beta;
- lag grid with block bootstrap;
- Holm, Benjamini-Hochberg and block-permutation family maximum;
- purged walk-forward and embargo;
- final holdout lock;
- regime and leave-one-era-out reports.

## GLC-WP04, graph validation

Metadata and synthetic fixtures only until G16 passes.

Implement:

- causal DAG validator;
- temporal dependency DAG;
- lead-lag network with corrected p-values;
- contradiction graph;
- Form Driver versus Edge Driver attribution.

## GLC-WP05, controlled economic execution

**Prerequisite:** G20 PASS plus immutable owner hashes.

Execute the frozen contract exactly once on development splits. Keep the final holdout sealed until the preregistered release step.

Required artifacts:

- levels versus returns;
- lead-lag;
- rolling regimes;
- fiscal-to-liquidity chain;
- Liquidity Requirement, Delivery and Delivery Gap;
- incremental value;
- sell and rebuy utility;
- BTC Liquidity Beta and Residual;
- all failed and null results.

## GLC-WP06, blind independent replication

Claude receives immutable inputs, contracts and hashes, but not ChatGPT economic outputs before submission.

Compare:

- row hashes;
- feature hashes;
- event and sample counts;
- coefficient and metric tolerances;
- classifications;
- discrepancies and adjudication.

## GLC-WP07, framework synthesis and prospective evidence

ChatGPT decides one of:

- redundant macro proxy;
- slow regime context;
- shadow sensor candidate;
- eligible governance challenger;
- rejection.

Any surviving candidate begins at zero live weight and uses the existing Daily Prospective Evidence owner. No new scheduler.

## Monitoring and escalation

The existing FMOS Ops + Codex Delivery automation owns daily monitoring.

Notify only for:

- remote agent delivery;
- failed source-integrity contract;
- G15 or G16 completion;
- G20 transition;
- immutable economic package;
- independent-replication disagreement;
- final governance ruling.

Routine no-change checks remain silent.
