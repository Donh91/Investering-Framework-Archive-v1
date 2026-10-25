# ChatGPT review — AT-GROK-20261023-002

Date: 2026-10-25. Disposition: **ADAPT the falsification question; REJECT the un-reproduced 18-row B1 result as an accepted empirical finding; preserve the negative review**. This is a source/document review, not science admission or external approval.

## Exact Bridge source and prior companion

- Grok artifact: `GROK-RESEARCH-20261023T220000Z-AUDIT-B-EDGE-COMPLETION`
- Current Bridge PR #63 head: `53696ac81d8f084ab7cf06fd16f5c577d73240d2`
- Grok report blob: `621ccea6c40e9a361f3641504bddf2c6058d7a7c`
- Report-declared body SHA-256: `d105318b5df86fa66286167a561df17684fdd43fec41af63af4c3e578737b91f`
- Attached ChatGPT review blob: `a99f87758dc342af5fd77a683baa8b7a935579a2`, which was written 2026-10-23 and targeted the earlier original PR head.
- Archive source snapshot independently read today: `1a2ccd71d854e0ae84cc29c229300106ea5f1e51`.

## Decision

**ACCEPT** the methodological question: containment can be inflated by wider bands, and categorical hit rates need matched cohorts/baselines. **REJECT acceptance** of Grok's specific 18-row B1 score comparison because the report's cited scripts are absent from the Bridge patch and the existing review explicitly did not replay the inputs.

The earlier ChatGPT review's B2 correction is arithmetic conditional on Grok-reported rows: if all 29 forecasts are SIDEWAYS and 27 outcomes count as hits, then the matched always-SIDEWAYS forecast on those same rows is also 27/29; the reported 0.93 versus a separate 0.79 climatology is not matched-row lift. The underlying rows, timestamps and outcome ledger were not independently regenerated.

The later Archive four-row control is a distinct descriptive cohort, not a reproduction of Grok's 18 rows. Its JSON labels `science_eligible_n=0`; it may illustrate score sensitivity, not predictive skill. It also uses a public-formula-style score and a 15% stress interval twice the width of CN; it is not a proper interval score or a valid emitted candidate. Keep all results `RESEARCH_ONLY` and do not alter Task 2, CN scoring or the current Compass.

## Review evidence and limitations

I read the current-main Archive note and exact JSON summary and the Bridge PR's source binding plus attached prior ChatGPT companion. I did not run either report's scratch scripts, fetch the underlying private MAL outcome ledger, rerun the 29-row cohort, or test a production scorer. The review's historical 8/8 assertions are only preserved as prior-review claims; they were not rerun here.

No new experiment or ChatGPT original research is claimed. No private Alpha values, wallets, or provider details are copied.

## Finite next gate

For any empirical adoption of B1/B2, require the complete source-row list and immutable first-known/outcome bindings, runnable script/dependencies/output digest, same-row comparison, and an independently reproducible proper metric with uncertainty that respects week/asset dependence. Until then keep empirical edge `UNPROVEN / NOT_ADMITTED`.
