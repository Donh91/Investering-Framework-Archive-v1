# CYCLE NAVIGATOR · Vite → GitHub Pages · HANDOFF TO NEW CHAT
Date: 2026-10-23 late Europe/Copenhagen
Owner mandate: SITE #1578, Supervisor #1156
Scope: continue source-first Premium v2.1 without modifying canonical GitHub Pages homepage until separate documented release acceptance.

## OWNER DECISION (DO NOT REOPEN WITHOUT EVIDENCE)
- **GitHub Pages** (`https://donh91.github.io/Investering-Framework-Archive-v1/`) is the ONLY canonical production website.
- **AppDeploy** is prototyping/development/QA ONLY, NOT equivalent source, deploy, data authority or production backend.
- **Priority: finish Vite as the GitHub frontend build bridge FIRST**, not CSS mockup/imitation, unless source-reproducible build/rendered iPhone parity fails specific, documented criteria.
- Vite/TypeScript, native browser CSS/SVG, Canvas, JS and packages build to static HTML/CSS/JS; GitHub Pages serves built frontend. Node/TS run at BUILD time, not as live Pages backend. Existing canonical JSON first-party feeds remain the market truth. Any future server functions/backend are a separately reviewed decision, NOT prerequisite to Graph B.
- In a Fallback, reproduce approved B visual via owned SVG/CSS/Canvas/Lightweight Charts without copying synthetic app fixture, but NOT before objectively falsifying source-based Vite transfer.

## KNOWN-GOOD WORK + LIVE EVIDENCE
- Draft PR **#1769**: https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1769
- Draft branch `agent/site-premium-v21-source-registry-20261023`; on handoff `e984896a15100ffdeb5c8830924353928a8243ad` (later handoff commit advances SHA).
- Current main readback `0fbc860f25d3e402f6382b52397ddb2307763e02` when checked; **always refetch main and exact head**. Branch had 30 unrelated commits behind main with 36 PR files all under `05_CYCLE_NAVIGATOR/site/premium-v2/`.
- Exact-head existing GitHub checks: 6 SUCCESS, 3 SKIPPED, no failures at the pre-handoff PR commit. **Existing checks DO NOT YET execute new premium-v2 Node suite.** Do not claim production release acceptance.
- Full source/design authority: `05_CYCLE_NAVIGATOR/site/premium-v2/design-registry.json`. READ `README.md`, `QUALITY_AND_RELEASE_GATES.md`, `RECOVERY_BASELINE.md`, `reference/appdeploy-bc/README.md`, SITE `DESIGN.md`, `KOMPAS_MINIMAL_UI_CONTRACT_2026-10-12.md`, `PATH_V3_CYCLE_ROTATION_PRODUCT_SPEC.md`, SITE AGENTS.md and root AGENTS.md before touching.
- Original approved B source archived unmodified (9 files), app `cycle-navigator-b-c-design-lab-ypjsxz` snapshot `1792595071401`, and Graph B source-only HTML/SVG/CSS development implementation.
- Original AppDeploy reference has `Math.sin()` synthetic 168-point timeseries, not allowed in prod or source-bound preview! Modern W43 lacks genuine pre-outcome seven-point BTC/ETH expected-close daily curve: BLUE dashed price curve MUST be absent, not inferred from W43 observed hours or midpoints. Frozen genuine source low/high windows and green observed hourly source curve are allowed.
- `graph-b/official-source-adapter.mjs`, `proof/price-range-proof.mjs`, `proof/public-source-links.mjs`, `compass/official-compass-path.mjs` are pure read-only proof/source adapters; source validity+expiry gates, exact 70/30 Price Range, Edge ABSTAIN, official HOLD_WAIT, 5 horizons, 7 tiers, 10 PATH phases. No issuer, forecast, market API writer, new confidence.
- Corrected real original B accent `span.alt-token` not flattened by i18n; removed demo screenshot timestamp and misleading SVG title; canonical `CN_LOGO.svg` added to prototype. Legacy `/legacy/` read-only browser smoke worked but not certified rollback.

### AppDeploy development QA (separate from production)
- URL: https://cycle-navigator-premium-v2-1-github-source-qa-71fr1g.v2.appdeploy.ai/
- App ID `cycle-navigator-premium-v2-1-github-source-qa-71fr1g`; latest checked READY version `1792789076700` with 0 reported QA frontend/network errors.
- Its 11 UI HTML/JS/CSS source files are based on GitHub Draft #1769, with **explicit QA-only absolute CORS first-party** `https://donh91.github.io/Investering-Framework-Archive-v1/data/{latest,compass,publication-lineage}.json`. AppDeploy normalizes source formatting; no byte-identical runtime claim.
- First AppDeploy READY produced `NoSuchKey` at nested `/graph-b/source-graph-b.html` because Vite default build only emitted index.html. Fixed by root Graph B entry, then true Vite MULTI-PAGE input for root and nested graph B. External readback confirmed both hosted paths now serve content.
- Independent live browser QA run `e41a6d8b-1822-42d6-a477-76e2c8919a57`: B badge/navy card, real hourly green BTC/ETH and scrub, absent source-unissued blue daily, Proof 01/02/03 with W43 source-reported provisional scores and pinned public GitHub original links, minimal Official Compass HOLD_WAIT, PATH 10 unselected stages, 7 rotation tiers, DA/EN indicators; no obvious overflow. **Not physical iPhone Safari nor pixel matched screenshots.** Browser agent did not prove CORS by inspecting network; AppDeploy QA claimed no network errors, and values visibly rendered.
- Source/behavior tests on branch: 24/24 adversarial domain V8 PASS, 6/6 preflight V8 PASS; existing CI green is NOT same as running all these new tests in actual Node.
- Firecrawl screenshots were blocked by external provider credits; do not claim they ran or add paid credits without authorization.

## VITE PATH ALREADY WRITTEN ON DRAFT BRANCH
`premium-v2/package.json`: pinned Vite v6.3.6, TypeScript v5.7.3, build script.
`premium-v2/vite.config.mjs`: root=Premium folder, `publicDir:false`, `base:'/Investering-Framework-Archive-v1/next/'`, rollup input for `index.html` and `graph-b/source-graph-b.html`, outDir `site/dist/next`.
`premium-v2/index.html`, `assets/CN_LOGO.svg`: clean candidate entry/real original branding.
`premium-v2/build-next.mjs`: alternative compile-free 12-source-asset allowlist. Do not mix both artifact producers without one explicit deterministic output contract.
`premium-v2/build-next.test.mjs`, `QUALITY_AND_RELEASE_GATES.md`: staged build boundary, original source restrictions.

## NEXT THREAD: EXECUTION PRIORITIES
1. Re-read current GitHub main/AGENTS.md + Draft #1769 files + checks + design authority. Avoid overlapping SITE-owner active changes. Retain Draft branch as working lane; **do not force-push/rewrite** history. Compare for upstream impact and reconcile safely through proper PR governance.
2. Run real `npm ci` after generating and reviewing a commit-pinned lockfile (no surprise npm scripts or paid packages). Run real `node --test` all premium-v2 tests. Run a reproducible Vite build **from GitHub source** and inspect final emitted dist file inventory and hashed import/asset basepaths. Prove root + nested graph B and original canonical JSON readback; catch exactly the historical `NoSuchKey` regression. Verify no `Math.sin()` or quarantined reference file slips into dist.
3. Integrate ONLY the reviewed `dist/next/` output into the EXISTING publishing artifact with source isolation. Do NOT create a competing Pages workflow, replace the full artifact, wipe existing `dist`, change `/`, `vnext/` or `legacy/`, or bypass GitHub Actions quota, main reviews/protections. A noncanonical Pages `/next/` deployment must pass governed staged release acceptance; no canonical root switch.
4. Compare rendered **true GitHub Pages** `/next/` to exact owner-approved B/C AppDeploy visual baseline side by side at **390x844 and 430x932** with real screenshots. Verify graph size and plot geometry, lightweight UI, original small B badge, original CN logo, Plot navy, source colors/lines, green hourly, frozen ranges and real-source absent BLUE, no horizontal overflow or folded text; exact browsers and cache-proof asset URLs. Check all real Graph B controls, Proof, Oct 12 minimalist Kompas and PATH, DA/EN, accessibility, time-clock expiry and no unauthorized action.
5. Independent adversarial review, source provenance, original score/proof readback, no private wallet/secret exposure, current live status/ack, test root/legacy rollback. Evaluate user value, design polish and quiet first viewport. No giant radar/gaudy generic cards.
6. Only after user separately accepts visual + source + iPhone product, propose isolated canonical root release PR with exact head, file/hash/readback and rollback plan. DO NOT call the product complete before the source truth supports it.

## ALTERNATIVE ONLY IF VITE IS FACTUALLY BLOCKED
Replicate approved Graph B using first-party standalone SVG/HTML/CSS/Canvas or current TradingView Lightweight Charts, with appropriate original palette/proportions and the SAME official adapters. Require side-by-side screenshots and maintain responsive + DA/EN + 7/14/21 horizon honesty. AppDeploy and GitHub Pages are not fundamentally incompatible languages; the issue is build/publish and source authority, not Pages inability to render React, TypeScript-compiled JS or SVG.

## PASS/FAIL HANDOFF FORMAT
Per objective, report `DONE` / `BLOCKED` / `NOT VERIFIED` separately with exact commit SHA, build manifest/hashes, data source clocks, actual URL, browser type and screenshot if available. Never replace this with app READY, '6/6 CI' or generic status. Continue concrete bounded work, use no new workflow/supervisor/paid dependency, record to SITE #1578 and Supervisor #1156, and leave root release on hold.

Final objective: ONE correct official product on GitHub Pages, with premium design and honest independent source data; AppDeploy only a laboratory.
