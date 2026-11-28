# L03 | Coverage-safe risk, true temporal liquidity, contract contradiction
Question: Can method-derived safeguards detect score overconfidence and liquidity path misclassification before paper-wallet evaluation?
Original owners S1 #98 execution and X0 disagreement; publication through #228 only after valid source gate.

SOURCE-CODE FINDING 1, coverage:
Birdeye reconstructed DD pillar() in src/token-dd-score.ts lines 59-68 computes a score from PRESENT signals only, while separately recording available declared weight. Final score in lines 613-640 renormalizes PRESENT pillars to sum to 100%; hardBlock isHoneypot=true does set final=0. Standard/Advanced modes vary materially; absent LST and canonical-mint checks are N/A. A score of 100 with a critical safety field missing can look same as 100 with all fields present if one ignores coverage. Official CLI caveat already warns modes and coverage not comparable.
Proposed independent method: COVERAGE_SAFE_HULL: declare all weights before seeing values; for missing score bound 0..100, compute full-weight lower and upper possible score, plus observed-only mean and coverage fraction. UNKNOWN_CRITICAL always blocks safety endorsement regardless of optimistic observed mean; this is an uncertainty/QA overlay, NOT a risk trading score.
Synthetic input: 20%-weighted activity score 100, critical 80%-weighted security unknown -> observed 100, conservative score interval [20,100], status UNKNOWN_CRITICAL. Test passes.

SOURCE-CODE FINDING 2, chronology:
Birdeye reconstructed liquidityStats src/token-dd-score.ts lines 86-114 calls (max(series)-min(series))/max(series) 'drawdown_pct'. This statistic ignores sequence order, hence a monotone increasing series [100,150,200] yields reported 50% drawdown though actual maximum chronological peak-to-later-trough drawdown is 0%. A separate current-from-peak stat correctly gives 0% in this example. This unordered spread feeds DD 'stability' in lines 448-457. This is a reproducible *reference-algorithm semantic mismatch*, NOT evidence Birdeye live scores or Alpha Lab current code have mispredicted an actual token.
Proposed independent method: TEMPORAL_LIQUIDITY_PATH: compute full real chronological peak-to-subsequent-trough maximum decline and track source last-known quote liquidity; separate USD valuation movement from actual on-chain quote reserve net flows. Native on-chain two-sided $100/$500/$1000 routes remain indispensable.
Synthetic ascending [100,150,200] => unordered 50%, temporal drawdown 0%; descending [200,150,100] => both 50%; rebound [100,200,150,190] => max drawdown 25%, current-from-peak 5%. All three tests pass.

SOURCE-CODE FINDING 3, contradictory authority evidence:
src/security-controls.ts lines 12-35 uses explicit provider boolean first and falls back to mint/freeze authority when absent. If those two supplied fields contradict, precedence can hide conflicting source evidence; the reference does not infer a verified SAFE label from that check, so call it a *conflict audit candidate*, not a proven bug. Existing S3 infra conflict regression should motivate a conflict=UNKNOWN negative case rather than a new classification engine.

Proposed falsifiers:
- Negative safety labels insufficiently sampled may look safer than fully sampled tokens: test correction vs current missingness baseline on both legitimate and rug cohorts.
- Temporal method adds zero improvement after directly observed quote-reserve stability and priced full exit: RETIRE candidate.
- CEX/bridge/shared-issuer funder contradiction cannot be made definite without native independent evidence: abstain.
No model promotions, no retrospective market labels, no data access or extra score system.
Source: https://github.com/birdeye-so/birdeye_cli/blob/2dcbd14cad32bcbb57f8d0c0c766d8c496597413/src/token-dd-score.ts#L90-L114 ; https://github.com/birdeye-so/birdeye_cli/blob/2dcbd14cad32bcbb57f8d0c0c766d8c496597413/src/token-dd-score.ts#L613-L721 .
