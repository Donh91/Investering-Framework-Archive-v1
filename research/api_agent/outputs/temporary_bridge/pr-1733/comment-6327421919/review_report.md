## GPT-6.1 Sol API review — advisory, not formal approval
PR #1733, exact head 84febfffe547766ea38bd5856c357275a198766d
Base SHA 1acdc46a5d25cf3c1136b4d77e7c48f5b8bd1510, patch SHA-256 3db3e92f6fac535879ac26df61ca97896e9b2c8cb46325dc733cbc86c6c9e197
Review verdict: PASS_WITH_FINDINGS MODEL_USED=gpt-6.1-sol NO_CODE_WRITE_PERFORMED NO_AUTHORITY_CHANGE
Receipt: PASS, tokens 18616/9196, estimated cost USD 0.129192.
This analysis cannot replace CI, nonauthoring GitHub review or governance acceptance.

Findings:
- P3| scripts/learning/forward_price_shadow.py: The envelope validator checks math.isfinite(low + high), which can reject two individually finite, positive, ordered endpoints because their sum overflows. Falsification: use 253 contiguous, legally timestamped bars with low_usd=9e307, close_usd=1e308 and high_usd=1.1e308, and recompute the canonical row digest. The calculated endpoints remain finite, but their sum becomes infinity and triggers degenerate_empirical_envelope. Endpoint finiteness should be assessed individually. This is an extreme-value robustness defect, not evidence of realistic BT
- P3| tests/learning/test_forward_price_shadow.py: Successful-case tests do not assert expected numerical extrema, empirical quantiles or overlapping-window counts. Consequently, the core scientific calculation lacks a numerical regression oracle despite extensive validation tests. Falsification fixture: use 253 bars with close_i=100*(1.001**i), low_i=0.99*close_i and high_i=1.01*close_i. For each supported horizon h, expected endpoints are anchor*0.99*1.001 and anchor*1.01*(1.001**h), with 253-h overlapping windows. These assertions would expose, for example, replacing the lower excursion's min

Uncertainties:
- No tests were executed. Current CI results, exact-head test discovery, imported-suite execution and compatibility with surrounding code are unverified; only the supplied diff was reviewed.
- The supplied base/head identifiers, diff digest and GitHub provenance were not independently authenticated. Omitted repository files, source-owner contracts and governance records were not inspected.
- Actual provider publication/first-known evidence, USD denomination and venue provenance remain unverified. The implementation explicitly treats the proof flag as an assertion; canonical row hashing establishes consistency, not original provider availability.
- The two freshness checks permit a last-bar boundary up to 96 hours before issuance: up to 48 hours before cutoff, then up to 48 hours from cutoff to issue. Whether that combined age is intended is not established by the supplied source-owner contracts.
- Exact future target UTC intervals are absent by the stated Phase 1 design. These outputs therefore have not been assessed as issued, scoreable forecasts; future integration must establish their temporal interpretation.
- Author independence, independent reviewer/security/governance sign-off and real-data admissibility are unverified. Synthetic assertions and static review establish neither empirical calibration nor incremental forecasting skill, and this advisory provides no formal GitHub approval or merge certification.
