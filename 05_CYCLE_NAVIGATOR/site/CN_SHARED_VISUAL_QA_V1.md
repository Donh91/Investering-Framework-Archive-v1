# Cycle Navigator, shared browser visual QA v1

**Scope:** read-only public Cycle Navigator presentation QA attached to the existing `cn-site-v2-gate.yml`, with no new workflow, schedule, token, secret, data engine, Pages writer or paid browser service.

## Reproducible evidence

The existing canonical product gate builds the official source-bound public bundle, runs its existing source/privacy and actual Chrome acceptance checks, then promotes the reviewed Graph B/Kompas PRO candidate into the temporary `dist` tree. The visual QA runs **after that promotion**, using exactly those public static files over ephemeral `127.0.0.1` HTTP with the real GitHub Pages repository prefix.

It uses Chrome already installed on GitHub Ubuntu, plus test-only pinned `playwright@1.56.1` and `axe-core@4.10.3` in the ephemeral runner. Four screenshots at 390, 430, 768, 1280 CSS pixels and focused graph screenshots at 390/1280 are saved with `report.json`, in the `cn-visual-qa` GitHub Actions artifact for 3 days. The browser interacts with actual BTC/ETH controls and checks loaded DOM, graph dimensions, JS exceptions, local HTTP failures and horizontal overflow.

The browser blocks outgoing third-party requests. No live market APIs, private plane, wallet, owner-email token, Cloudflare access credentials, Pages build outputs or scheduled task are needed. Screenshots are of **public CN data only** and never copied into the deployed bundle. The existing source-authority, freshness, official graph and publication privacy gates remain unchanged.

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
