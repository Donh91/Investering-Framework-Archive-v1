# Premium v2.1 · Phase A, non-destructive recovery baseline

**Date:** 23 October 2026 · **Status:** SOURCE_AND_HTTP_PREFLIGHT_ONLY, native Safari/legacy dynamic data NOT VERIFIED  
**Owner:** [SITE #1578](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1578), Supervisor #1156  
**Pinned start main:** `12d1b7fc96a7cee30f6a527cb680ff85e61068d7`

## Production safety hold
- GitHub Pages root `https://donh91.github.io/Investering-Framework-Archive-v1/` is the sole canonical live product. **DO NOT rewrite root or deploy a new design without independent release approval.**
- `site/build-public.mjs` produces `site/dist/index.html` using `premium-release.mjs::releasePremiumShell` and stages `dist/legacy/index.html` using `preserveLegacyShell` from `site/index.html`. The older shell is still present in source, but *neither the route nor its functional readiness is a verified rollback*.
- Read-only HTTP extracted text from current `/`, `/vnext/`, `/legacy/` (Oct 23) returned all three routes; legacy initial text displayed **"Loading..."**, which is **not proof of working data-fetch/runtime controls**.
- Production root has previously regressed from the owner-approved AppDeploy B card after merges #1765/#1768. Chrome checks validated selective selectors/interactions, **not image similarity to owner screenshots**. No rollback based on the existence of a route alone.
- Real official `data/latest.json` has `schema=CN_PUBLIC_SNAPSHOT_V2`, `public_live_precision.contract=CN_PUBLIC_LIVE_PRICE_PRECISION_v1`, public CN #30/W43, 111 BTC+ETH eligible hourly samples each at observed through 15:00 UTC during this audit. W43 `CN_FROZEN_DAILY_PRICE_PATH_v1` for both assets is `UNAVAILABLE` with zero prospective expected-close points. `data/compass.json` is a **separately issued** official state; never infer alignment from HTTP 200 alone. `publication-lineage.json` reported `STALE_AT_BUNDLE_TIME` even though source-to-public equality was already proven elsewhere. Freshness remediation is separate from presentation and owned upstream.
- No private data plane access, no backend, no root mutation, no CI override.

## Mandatory recovery test before optional root rollback
1. Freeze exact current `main`, current Pages-run release SHA, and fingerprint all real publicly served root/legacy assets (including CSS, JS, latest and Compass). Confirm same root+legacy first-party source.
2. Run each official NOW, Kompas, PATH, Proof, DA/EN and 390/430px Safari flow against both roots. Capture paired before/after screenshots and readable, comparable status/action/source timestamps; trace bug reproductions.
3. Verify archived `site/index.html` still supports full current Compass and latest CN contracts; older code cannot be assumed compatible with changed JSON.
4. Choose exact *frontend-only* recovery delta if needed, retaining current data writers and all immutable historical records. Independent review and rollback proof required.
5. **No root homepage change under this v2.1 authorization alone.**

## Current known/unproven
| Gate | State | Evidence/next |
| --- | --- | --- |
| Current official Pages root online | HTTP content read | Need native visual acceptance |
| Legacy path exists | HTTP text readable | Needs functional current-feed test |
| Original 12 Oct minimal Kompas spec | Source located | Compare screenshot + 5/7 row parity |
| PATH v3 contract | Source located | Compare true 10 nodes and one rotation rail |
| Approved B original component source | AppDeploy version pinned | Extract unchanged source in quarantined reference directory |
| Real W43 blue expected daily line | **UNAVAILABLE** | Prospectively issued next week only |
| Source freshness | **DEGRADED** | Existing Supervisor #1156 |
| Final root cutover | **BLOCKED** | Separate owner approval + release/readback |

Historical score percentage and 168-hour coverage are **different quantities**. Absence of prospective directional edge remains ABSTAIN; no visual VERIFIED badge can upgrade this.
