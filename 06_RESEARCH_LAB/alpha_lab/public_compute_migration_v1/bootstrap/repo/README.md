# Public Compute W1: Synthetic-only, zero-secret bootstrap

**Current state: NOT DEPLOYED, NO CHAIN SOURCE, NO WRITER, NO TRADING AUTHORITY.**

Source design: [Archive PR #1865](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1865). Existing Pons source owner: [Meme-Alpha-Lab #120](https://github.com/Donh91/Meme-Alpha-Lab/issues/120). Independent original design review: [Bridge #118](https://github.com/Donh91/Investering-AI-Audit-Bridge/pull/118).

This repository is deliberately safe to be public. It contains only a deterministic test harness, a **verbatim** 13,052-byte published JSON Schema (`contracts/public_receipt_v1.schema.json`, Git blob `179e6c224ad48682388b70be39205a30d798f426`), negative security tests and a single manually triggered synthetic-only job. There is **no** Pons RPC URL, public main push, private data, private selection, key, secret, real market scan, cron, paid provider, wallet/address case or live source. A successful synthetic receipt has `safe_for_private_import=false`, `canonical_alpha_census_recovered=false`, `original_machine_first_known_certified=false` and no trading permission.

## Local reproducibility

Run with Python 3.12+ in a clean isolated public environment:

```sh
python -m pip install -r requirements-ci.txt
python -m unittest discover -s tests -p 'test_*.py' -v
python tools/public_guard.py
python -m tools.produce_synthetic --out /tmp/w1-synthetic.json
python -m tools.validate_receipt /tmp/w1-synthetic.json --schema contracts/public_receipt_v1.schema.json
```

`jsonschema==4.26.0` and `PyYAML==6.0.3` are pinned for W1 test reproducibility; they have no access to private credentials. No code contacts the network. The runner's own package install and GitHub checkout necessarily use public network services. Test numbers and failure evidence must be logged from actual GitHub runner after setup, not inferred from local runs.

## Secure GitHub bootstrap, one-time infrastructure gate

1. Create an **empty, separate PUBLIC repository** exactly named `Donh91/investering-public-compute`. Never change visibility of `Meme-Alpha-Lab`, `Donh91/secrets`, Vault, or any existing private repo. Do **not** copy their Git histories or raw files.
2. Import **only** the contents of this `repo/` directory as the root of the new repository. The checked-in `.github/workflows/w1-synthetic-security.yml` must remain outside the original Archive's actual `.github/workflows` and never be activated inside Archive. Initial commit is an infrastructure/bootstrap event, not source-data admission.
3. Before granting additional actor write access, set **Actions default workflow permissions to read-only**, prohibit GitHub Actions from creating/approving PRs, permit only approved/pinned public Actions and disallow outside source secrets. Verify GitHub UI/readback, not README claims.
4. Enforce branch protection or an active repository ruleset on `main`: require PR, at least **one genuinely independent** qualified approving reviewer for changes to code/workflows, code-owner review, dismiss stale approvals, protect against force-push and deletion, and require relevant exact-head checks. `.github/CODEOWNERS` by itself **does not** enforce reviews. If GitHub account limitations prevent independent reviewer, keep the source branch unmerged. No automatic merge/write bypass. Never create a bypass role that lets the same runtime actor rewrite its guard.
5. Review the source and 42 positive/negative local regression tests, including duplicate YAML keys, private fields, job permissions, OIDC, fork-trigger class, unauthorized data/commands, cursor and clock paradoxes. Execute a **fork/untrusted PR** negative test as a separate required gate, since no local test simulates GitHub's actual permissions.
6. Trigger the single existing `W1 Public Compute Synthetic Security Only` `workflow_dispatch` on trusted `main` only after security bootstrapping. Read GitHub's actual workflow run, job steps, used runner, ref, conclusion and synthetic stdout. A PR should run **only the read-only tests**; the synthetic-receipt job is disabled on PR/forks.
7. Confirm every output path is temporary `/tmp`, and actual runner logs contain no private tokens, watchlists or credentials. Confirm no public artifacts/commits were written by this workflow and no private repository was accessed.
8. Only after separate hostile review of current HEAD, original #120 source disclosure approval and valid source-license rules should a future W2 PR add a bounded public-chain collector. **W1 does not authorize W2**. 48-72 hours of complete contemporaneous block evidence and pinned one-way private import are separate W2/W3 gates.

**If repository creation/branch rules/independent approvals are unavailable, state `W1_INFRASTRUCTURE_BLOCKED`; do not substitute the existing Archive.** The package is source-ready, not an active public compute service.

## Critical operating restrictions

- No `secrets.*`, OIDC write, `GITHUB_TOKEN` write, `pull_request_target`, `workflow_run`, `repository_dispatch`, cron, network RPC, Git push, artifact upload, private code, wallet cohorts or case-specific outputs in W1.
- The workflow is pinned to checkout SHA and `persist-credentials:false`, with minimum `contents:read` and no job permission overrides.
- The security guard parses YAML with duplicate-key rejection and an exact allowlist of supported jobs, commands and triggers. It is **not** a GitHub branch protection control and cannot prove safety if an attacker has unreviewed write access to `main`.
- Public GitHub logs/commits can be read by everybody. There is no secure way to run private algorithms on ordinary public runners. Do not publish private-derived identifiers, even their unsalted hashes.
- The original Pons historical cursor remains stale as of Oct 21 in source main. W1's fabricated block numbers and times are solely test fixtures and give **no** machine discovery, source recovery, data completeness or edge credit.
