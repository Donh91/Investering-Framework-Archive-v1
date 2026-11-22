# Cycle Navigator, shared browser visual QA v1

**Scope:** read-only public Cycle Navigator presentation QA, ready to run manually on the final promoted public build. **It is not attached to the existing `cn-site-v2-gate.yml` yet.** The workflow integration is held for the governed W5 `.github` pin re-chain. No new workflow, schedule, token, secret, data engine, Pages writer or paid browser service.

## Reproducible evidence

The canonical product gate builds the official source-bound public bundle, runs its existing source/privacy and Chrome acceptance checks, then promotes the reviewed Graph B/Kompas PRO candidate into temporary `dist`. The read-only test **must be invoked manually after that promotion** (or by a future reviewed CI hook). It uses the public built files over ephemeral `127.0.0.1` HTTP with the real GitHub Pages repository prefix.

It uses Chrome already installed on GitHub Ubuntu, plus test-only pinned `playwright@1.56.1` and `axe-core@4.10.3` in the ephemeral runner. Four screenshots at 390, 430, 768, 1280 CSS pixels, default Compass screens and focused Graph B screenshots are saved with `report.json` under `qa-visual-artifacts/`. The pre-W5 test run [45072537557](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/45072537557) captured an example GHA artifact. Future CI artifact publication is part of the deferred wiring. The browser interacts with actual BTC/ETH controls and checks loaded DOM, graph dimensions, JS exceptions, local HTTP failures and horizontal overflow.

The browser blocks outgoing third-party requests. No live market APIs, private plane, wallet, owner-email token, Cloudflare access credentials, Pages build outputs or scheduled task are needed. Screenshots are of **public CN data only** and never copied into the deployed bundle. The existing source-authority, freshness, official graph and publication privacy gates remain unchanged. No `.github` file changes are included in the merge-ready slice.

## Honest interpretation

- `visual_functional=PASS`: the four local Chrome renders and interactions completed. This is **not** a claim that the market predictions or data are fresh, nor that a physical iPhone Safari was tested.
- `accessibility=NEEDS_REMEDIATION`: axe found automated WCAG-rule issues. Existing contrast issues remain visible in receipts. A separate independent reviewer must resolve/accept these under the site's design and release policy. A green browser-functionality step never means complete WCAG PASS.
- `accessibility=NOT_VERIFIED`: the axe audit could not complete; stop asserting accessibility success.
- `visual_functional=FAIL`: JS/HTTP/overflow/interaction or browser startup failed. The existing product gate must fail closed; screenshots and the report are retained on failures.
- Empty/stale charts or `SOURCE_UNAVAILABLE` are legitimate evidence states and must never be filled with fabricated curves.

## Reuse

This reporter pattern can later be adapted to Navigator One and Alpha Lab, with separate owners, repo-limited source access and review. **Do not attach Cloudflare Git integration to Archive, MAL, secrets or Vault.** The canonical public CN website remains GitHub Pages and is not redeployed by this QA.

## Merge boundaries

This change touches an executable `.github/workflows/` gate. Require current-head CI and independent qualified review, existing privacy/recovery controls, and owner-authorized squash merge. Do not downgrade as low-risk documentation or bypass a failed/skipped required check.

## Safe manual invocation before W5

Run only on a temporary checked-out branch where the existing official CN gate has already built and promoted `05_CYCLE_NAVIGATOR/site/dist/` to its final root. This test does not build or publish it.

```sh
npm install --prefix 05_CYCLE_NAVIGATOR/site --no-save --no-package-lock --ignore-scripts --no-audit --no-fund playwright@1.56.1 axe-core@4.10.3
node 05_CYCLE_NAVIGATOR/site/tests/cn-shared-visual-qa.mjs
```

An installed Chromium or Google Chrome at `CHROME_BIN`, `/usr/bin/google-chrome` or `/usr/bin/chromium` is required. Do not modify canonical `dist` assets or use a private-market-data fixture. Output is local to `05_CYCLE_NAVIGATOR/site/qa-visual-artifacts/`; remove this ephemeral folder after exporting reports. A real Playwright click + source-bound refresh is tested, but **screenshots do not establish forecast accuracy or a successful investor outcome**.

**W5 follow-up:** the workflow hook attempted in PR #2308 was safely reverted because the S1 reviewed-merge lane pins the entire `.github` tree. Merging a changed `.github` tree alone failed six full-repository S1 governance checks. Reattach the pinned Chrome/axe test in the planned W5 owner-reviewed re-chain only, including updated switch/contract/bootstrap as defined by existing governance, qualified review, CI and independent backup. Never change, bypass or disable these tests to make the hook green.
