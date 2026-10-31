# PROPOSED preregistration: Kompas NEXT_12H vs persistence

**State:** DRAFT_NOT_RATIFIED, no holdout opened, no tests scored as prospective.

**Hypothesis:** Eligible Kompas Pro 12-hour direction contains information beyond the sign of the most recent market momentum available strictly before issuance. Null hypothesis: no additional paired directional correctness.

**Population:** Newly issued Kompas Pro NEXT_12H UP/DOWN forecasts, each anchored to original immutable issuance evidence, a verifiably first-known market baseline at issuance, fixed target definition, matured horizon and a distinct issuance/target cluster. Count all abstentions, missing timestamps and unverified rows; never choose first eligible after discarding an earlier quarantined issuance for the same cluster. Never treat 168 hourly forecasts in the same week as 168 independent weeks.

**Primary outcome:** Pairwise correctness on identical admissible clusters, with McNemar discordance counts, sample size, coverage, uncertainty and conditional independence limitations. Publish baseline, forecast-only and baseline-only wins. No positive edge conclusion until preregistered prospective cohort, independent replication and applicable multiplicity/regime checks exist.

**Mandatory controls:** Persistence sign, class prevalence, UP-only/DOWN-only, randomized direction seeded in the preregistration, null-label permutation within regime/cohort, missingness and abstention sensitivity. Do not recompute past model outputs with newer weights, and do not treat a full-history retrospective score as a forward holdout.

**Frozen parameters to be accepted before any prospective run:** issuance source contract/version, baseline exact feature/time field, target market and horizon, target price source/clock, cluster definition, positive/negative selection handling, minimum effective sample, sequential test stopping rule, fixed random seed, multiplicity family budget, evaluation publication schedule, private-data availability gate and owner/S1 acceptance SHA. Any change requires a new ID, not an edit to the original test after outcomes are visible.

**Mandatory falsifiers:** Model matched accuracy <= baseline; apparent benefit vanishes after source timestamp integrity; model outperformance is fully explained by abstention/coverage, broad intervals or correlated windows; statistical interval includes null or negative improvement; performance reverses out of sample. No model promotion on a historical win.

**Current known historical evidence (advisory only):** Grok Bridge #104 reports 10/24 matched on the rolling14 cohort and 17/32 all-history for BOTH Kompas and the naive momentum sign. It is not certification of current source PIT or incremental edge. Run the prospective test only after owner/S1 preregistration is actually merged and separately verified.
