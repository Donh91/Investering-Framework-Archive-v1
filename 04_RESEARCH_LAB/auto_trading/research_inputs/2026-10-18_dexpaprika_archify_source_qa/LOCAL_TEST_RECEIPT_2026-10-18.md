# Local regression execution receipt, 18 October 2026

**Classification:** EXACT_BLOB_LOCAL_EXECUTION / SYNTHETIC_TESTS_ONLY / NOT_CI / RESEARCH_ONLY.

## Identity and environment
- Repository: `Donh91/Investering-Framework-Archive-v1`
- Research PR: [#1668](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1668)
- Branch: `research/2026-10-18-dexpaprika-archify-source-qa`
- Tested `source_qa_v1.py` Git blob SHA-1: `608c4a24a3ef973bd3e030c5bf00581bf2a943b8`
- Tested `test_source_qa_v1.py` Git blob SHA-1: `e3fd9f8af1e496bf9d077404c2fa41a01d6e2c62`
- Both SHA-1 blob identities verified against actual GitHub files via current branch readback, not merely filenames or byte counts.
- Environment: Linux, Python 3.13.5, Git 2.47.3.
- Standard-library only, no network access and no external API keys or third-party installs.

## Exact executed commands and results

```sh
python -m py_compile source_qa_v1.py test_source_qa_v1.py
python -m unittest discover -s . -p 'test_source_qa_v1.py' -q
git hash-object source_qa_v1.py
git hash-object test_source_qa_v1.py
```

- `python -m unittest`: **Ran 27 tests in 0.094s, OK.**
- `py_compile`: **PASS**, no syntax errors.
- Git hashes exactly matched PR files.
- Tests used constructed fixtures, not real historical observations or restricted/provider market payloads.
- No code was deployed or merged; no current Alpha Lab consumer called the research module.

The 27th unittest includes **1,200 deterministic malformed-provider mutations** with seed 20261018. All checks retained `sellability_proven=False`, `trade_signal=None` and hashed case references, and no unhandled exceptions occurred. This is *synthetic robustness testing*, not an observed provider SLA or production-quality guarantee.

## Evidence scope, important exclusions

This receipt proves exact-file execution of the 27 **synthetic** tests, not actual Alpha Lab value, correctness on arbitrary malformed records, real API provider availability, independent onchain verification, stream freshness, market liquidity, first launch block, sellability or portfolio performance. Existing GitHub status checks are not assumed to run this Python suite. The PR remains draft pending exact-head independent review and acceptance by the canonical domain owners.

## Next adversarial acceptance before any integration

- Add realistic *private/admitted* raw JSON schema fixtures through existing source owner, never public.
- Compare matched prospective provider observations to existing native-chain and DexScreener/GeckoTerminal evidence, respecting the first-known clock.
- Demonstrate actual additional *decision-relevant source health* without false assurance, not mere provider agreement.
- If the #1017 field-map precondition or review is not satisfied, the prototype stays research-only.

**Required state:** `SOURCE_QA_LOCAL_SYNTHETIC_TESTS_PASS` / `SOURCE_ADMISSION_NOT_PROVEN` / `TRADE_AUTHORITY_NONE`.
