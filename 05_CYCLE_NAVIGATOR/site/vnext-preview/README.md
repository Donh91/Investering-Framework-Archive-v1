# Cycle Navigator vNext - Interactive design preview (2026-10-11)

## 17 October 2026 — current/public readback integration (supersedes source-status descriptions below)

**State: ISOLATED_PREVIEW_WITH_OPTIONAL_CURRENT_PUBLIC_READBACK / NOT A PRODUCTION RELEASE.** The first Overblik viewport now reads only the existing public `site/build-public.mjs` output contracts at `https://donh91.github.io/Investering-Framework-Archive-v1/data/latest.json` and `compass.json`, via `current-public-panel.mjs` -> `official-feed-parity.mjs`. The two HTTP files are source-joined and must pass the current week, correct issue number, delivery timestamp, original verified Official owner expiry and Compass identity. Current action, 12h direction, risk and PATH gate are either sourced from this authenticated readback or shown as `UNAVAILABLE/UNKNOWN`; no synthetic market prediction, score, ETA or SELL permission. The UI rechecks the expiry of its cached readback every minute **without extra HTTP polling**.

**The existing `seed.json` stays a frozen W41/CN28 plus W40/CN27 historical archive**, with its source-owned BTC/ETH actual-versus-frozen PATH and all 27 historical records. It is visually separated by a HISTORISK DESIGNARKIV barrier; it is never the fallback for a failed current feed. The Vite multi-file preview and portable single-file demo contain the same client readback code. Portable `file://` and restricted CI browsers may block cross-origin HTTP; the **verified expected state there is `UNAVAILABLE`**, not proof the public website is live. Normal browser on the canonical host, cross-origin access, native Safari, qualified review, production Pages build/deploy and rollback remain unverified requirements.

**Evidence:** existing `check-premium.mjs`/ `test-official-feed-parity.mjs` synthetic and canonical local `build-public.mjs` readback; existing `verify-vite-bundle.mjs` includes the two new source consumers in its immutable preview artifact manifest; existing Chromium `browser-preview-qa.mjs` verifies 390/430 current unavailable-versus-archived label separation, 320–1440 no overflow, but is **not native Safari**. Check current exact PR #1576 SHA and CI before citing any pass. No Work, AppDeploy, extra workflow or production main change.

---

## Current authority / delivery · superseding 2026-10-15 update

**Current preview delivery:** GitHub Actions artifacts, built on the existing Draft PR [#1576](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1576), not AppDeploy. The current check's `cn-vnext-source-preview-<run_id>` artifact contains `CYCLE_NAVIGATOR_OFFLINE_PREVIEW.html` (single-file archived interactive demo, verified offline in Chromium), ordinary Vite files, and a SHA-256 `PREVIEW_MANIFEST.json`. `cn-vnext-browser-qa-<run_id>` contains real rendered mobile/tablet/desktop screenshots. Find the latest successful `static-preview` in the PR's Checks tab and download its artifacts; they expire after seven days and can be rebuilt from the exact branch source.

**Delivery status:** `HISTORICAL_DEMO_ONLY / ARCHIVED_CN28_W41_AND_COMPLETED_CN27_W40 / NOT_LIVE / NOT_GITHUB_PAGES_PRODUCTION`. GitHub CI has source tests, actual browser checks for 320–580px phones, 801–940px tablet, 1024–1440px desktop, keyboard focus/Escape/Enter, reduced motion, DA/EN BTC/ETH, readable WCAG AA evidence labels, exact source cutoff and no site overflow. Chromium browser-emulated iPhone viewport **is not native iPhone Safari/VoiceOver signoff**.

**Hard release boundary:** The existing public GitHub Pages site remains separate and unchanged. Current W42+ source consumer, matching Official Compass and CN identities/freshness, immutable score evidence, independent review and approved release/rollback are separate requirements owned by existing [release issue #1578](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1578). The preview's public source seed is fixed at the 2026-10-11 issuance, and the W40 graph uses only genuine three frozen range windows and seven observed daily closes; its dashed midpoint is an **illustrative derived guide**, not seven originally frozen daily price forecasts. Source-specific cutoff and Monday pre-freeze caveat remain mandatory. Do not invent current market actions, profitable edge or independent verification.

**No AppDeploy:** User directed discontinuation of AppDeploy for this work on 15 October. Historical AppDeploy URLs and deployment statements *below this heading* are retained as dated archival evidence only; they are **not** present deployment instructions. Do not redeploy the old app, create an extra host, pay for a new provider or spawn another scheduler.

**Design precedent:** The October 12 Quiet Precision editorial standard rejects redundant decorative market gauges. The current GitHub preview leads with source-owned direction and Official Compass action in one decision row, retains the approved simple BTC/ETH PATH comparison chart, and exposes source-native disclosures. Any aesthetically inspired alternative may only show the three real frozen range windows against observed low/high using exact source data; proposed option and user direction are recorded in release [issue #1578](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1578#issuecomment-6202599679). No new chart mode has yet been accepted or published.

**Baseline verified before this documentation-only update:** [GitHub CI run 38810417062](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/38810417062), exact source head `4a94c3271a156c4109074bb13d1419a405236edb`, 9 relevant SUCCESS, 3 inapplicable SKIPPED, 0 failure. Always verify current head/checks rather than treating this as a timeless release claim.

---

## Historical 11–12 October project notes (superseded for preview delivery)

**Historical AppDeploy preview (not current):** https://cycle-navigator-vnext-preview-l1nbkq.v2.appdeploy.ai/

**Historical status:** ISOLATED INTERACTIVE PREVIEW / CURRENT PRODUCTION UNCHANGED / NOT CONTINUOUS LIVE SIGNAL

## Latest v2 result-page evolution (Sunday 2026-10-11)

- **DA/EN toggle** now appears in the desktop/iPhone header and persists the selected language; the new W42 score story has bilingual catalog entries.
- The HOME proof teaser no longer promotes the historical CN27 82.05% figure as the leading metric. It instead introduces the **new W42 forward accuracy / direction / pullback Edge era**, with explicit PENDING status.
- RESULTS now leads with **Price Range weekly + intradays**, **Direction/Rotation claims**, and **Pullback Edge warnings**, all individually gated by prospective freeze/outcome completion.
- A clear 12–48h / 7d / 14d / 21d / 28d / 56d claim checkpoint rail explains that longer original forecasts remain open across subsequent CN issues.
- Pullback tape distinguishes explicit warning vs no-warning, possible onset, severity, recovery and independent altcoin basket impact. Each absent source observation is UNKNOWN / ABSTAIN, not 100 or 0.
- The existing CN1–27 and X-era score summary, frozen-vs-actual BTC/ETH comparison chart and historical rows are preserved **behind a Legacy Scores disclosure**, not deleted.
- Preview remains pinned to CN28/W41 and official Compass 11 Oct; **none of the v2 W42 scores or facts have yet been fabricated or graded**.

Implemented and merged scoring core: https://github.com/Donh91/CycleNavigator-scores/pull/3 . Existing weekly CN now has source-bound new-era freeze step: https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1577 . Neither feature creates a new scheduled worker. Work-owned integration and source-test roadmap: https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1578 .

## How to preview

For the **current** preview, download and unpack the GitHub Actions source-preview artifact; try the single-file HTML on a desktop browser. Native iPhone Safari still requires manual verification. The navigation description below remains a design inventory from the archived October 11 snapshot:

1. **Overblik** - current-source official direction vs action, Compass authority, pullback protection, one simplified market-cycle journey, frozen BTC/ETH W41 scenario corridors and latest public score credibility.
2. **Kompas** - exactly two narrow three-column action tables (five horizons and seven independent capitalization rungs), official source permission, compact interpretation, separate SELL/Distribution/Re-entry.
3. **Resultater** - CN #27 completed public score (W40), observed-vs-frozen price corridor chart with BTC/ETH toggle, all 27 historical public score claims with method-era labels, and link to independent score repo.

## Preview source receipt

The preview uses a pinned, allowlisted, source-derived JSON seed saved as `seed.json`:

- Weekly CN public #28, forecast week **2026-W41**, from `05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json`, official source status **DEGRADED** and its frozen machine package for W41. No downgrade status is concealed.
- Official Compass ID **CMP-20261011-7d14a9ee5914**, published **2026-10-11T13:15:27Z**, `data_status=OK`, `action_now=HOLD_WAIT`; 12h direction UP and 1-3D/5-7D/2-3W MIXED, 4-8W UNAVAILABLE. The snapshot is a time-stamped point-in-time source, not an auto-refreshing market recommendation.
- Protection tracker: pullback BUILDING with low-quality risk evidence and uncertain ETA; distribution UNKNOWN; separate SELL assessment UNAVAILABLE; re-entry INACTIVE.
- Public completed CN #27, **2026-W40**, Price Range Precision **82.05%**; BTC **82.27%**, ETH **81.82%**; market/structure accuracy percentage **UNDEFINED** from CN #27; frozen claim evaluation is separate. Graph uses the exact six public range scorecard rows, no simulated prices.
- Original `05_CYCLE_NAVIGATOR/site/history-scoreboard.json` CN #1-27, kept as original separate-era score claims. Modern scorecards for CN #23-27 and all historic 27 issue entries are now public in `https://github.com/Donh91/CycleNavigator-scores`, but do not have independent cryptographic proof of forecast-before-outcome. No claim that Git commits are immutable.

No keys, wallets, private holdings, hidden repo data or non-public research included in the preview seed.

## Files

- `premium-index.html`: semantic layout for three views, custom inline SVG identity/artwork, source/a11y dialog, touch navigation and chart controls.
- `premium.css`: mobile-first Quiet Precision visual system, custom chart grammar and reduced-motion.
- `premium.js`: read-only source contract validation and navigation, explanation/score rendering, transcript-copy interaction; fails closed on missing/invalid seed. Danish editorial translations are guarded by exact Compass ID+forecast week to avoid translating changed/new source as if it were the frozen snapshot.
- `seed.json`: source-derived public material with exact model/data identity.
- `check-premium.mjs`: zero-dependency CI integrity/safe-DOM/syntax check.
- Earlier `index.html`/`check-preview.mjs` are retained for design comparison only and are NOT the polished public AppDeploy preview.
- `../DESIGN_MOTION_REFERENCE_LIBRARY.md`: all links from motion-design inspiration article.

## Design principles / limitations

- One actionable narrative at a time. Official Compass decides today's action; weekly CN remains independently frozen; the frontend never becomes a new signal/score generator.
- The static illustrated cycle journey is a sequence of possible gates, **not** a dynamically confirmed 4–8-week cycle checkpoint or an ETA.
- The 7D scenario corridors are *published forecast ranges*, not probabilities or point forecasts.
- Historic range bars plot published frozen and realized extrema only; they are not synthesized price trajectories.
- All exposed data must show source time, owner role and stale/degraded limitations.
- Preview deployment is independent from the GitHub Pages production site; current production code, build pipeline and user automations have NOT been modified.

## Next release gates

1. Capture and review actual Safari iPhone screenshots at 390 and 430 widths and desktop; compare with current live pages. QA snapshot URLs are supplied by the standalone preview host but independent human review is still pending.
2. Source/API parity tests against actual production public `data/latest.json` and `data/compass.json`, including stale/misaligned/partial fixtures, i18n and projected current status. Do not use this pinned preview seed in a production hot-reload feed.
3. Check content inventory: move every present NOW/PATH/WHY/PROOF section to appropriate visible, expandable or archived destination; no unintentional omission.
4. Integrate source-locked score navigation with published `CycleNavigator-scores` release integrity when attestation and external timing gates exist; never claim proof prematurely.
5. Merge any bounded site production work only after fresh-main contract review and product/visual acceptance, independent of any other running Work/Codex missions.

**Scored historical public claims are not investment returns or a demonstrated profit-making trading edge.**

## vNext Motion QA update · 2026-10-11

- A second X article supplied a complete list of 20 motion-design repositories. The complete links, product fit and future adoption decisions are frozen in [MOTION_TOOLKIT_20_REPOS_AND_CN_DECISION.md](MOTION_TOOLKIT_20_REPOS_AND_CN_DECISION.md) and cross-linked from the canonical site design reference library.
- The **Resultater** page now provides a source-honest `Se animeret sammenligning` action, opening the older CN #27 source comparison inside the Legacy section without promoting that historical result as a new v2 Edge metric.
- Animation is deterministic and **data-invariant**: frozen range bars (source scorecard) are revealed, then observed low–high bars, then the precomputed score. Existing endpoints, price scales, grade formula and 6 source rows never change.
- A small in-place `Afspil sammenligning` button makes it repeatable; BTC/ETH switch and DA/EN switch remain source-driven. No sound, 3D, vendor CDN or new framework/dependency.
- All historical data and score metrics are fully visible when `prefers-reduced-motion: reduce` is active; default motion finishes after ~880ms and does not loop.
- The score visual stays folded in the Legacy disclosure as required by the new Score Era product concept. One tasteful direct link in the v2 section makes it discoverable when desired.
- Programmatic source contract and motion smoke tests are included in `check-premium.mjs`, checked on PR #1576. Standalone AppDeploy reports ready and no frontend/network errors as of the last deployment. Native iPhone Safari visual/manual sign-off and production owner mapping remain pending.

**Guardrails**: This animation is historical educational visualization, not a simulated market progression, forecast path, trading signal, independent cryptographic attestation or demonstration of statistically significant profitable Edge.

## Single Work handover packet

**START HERE:** [WORK_EXECUTION_PACKET_2026-10-11.md](WORK_EXECUTION_PACKET_2026-10-11.md) — step-by-step Work browser/Safari UI audit, original-vs-new IA inventory, source parity, proof/risk semantics, exact screenshot/CI gates, production safety and complete ready-to-copy launch prompt. Coordinates with [Archive issue #1578](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1578). **Prepared, not independently run yet.**

## Kompas minimal interface · user-approved direction (12 October 2026)

[Read the new Kompas Minimal UI Contract](KOMPAS_MINIMAL_UI_CONTRACT_2026-10-12.md): retain the current ChatGPT Kompas decision logic with **official action + 0–12h direction and immediate pullback/SELL/distribution visible**, exactly two compact decision tables (5 horizons + 7 asset classes), and only two **closed-by-default** native disclosures for market reasoning and detailed protection/re-entry. Nothing decorative or nonactionable remains above the tables. Source / forecast / scoring ownership remains unchanged.

The currently published [isolated preview Kompas](https://cycle-navigator-vnext-preview-l1nbkq.v2.appdeploy.ai/#kompas) contains this source-bound, bilingual implementation; production is not changed. Independent desktop browser interaction QA passed but native 390px iPhone acceptance still needs to be completed by Work.

## Pullback ETA contextualization and deploy gate · 2026-10-12

The user has approved the minimalist site but requests that **Pullback status always includes an ETA/time-window qualification**. [Read the Pullback ETA release note, source guardrails and exact post-quota deployment instructions](PULLBACK_ETA_RELEASE_NOTE_2026-10-12.md).

**Status:** Code, 13 strict ETA tests, 35 live feed parity tests and Vite production bundle PASSED in PR #1576. The archived W41 preview source supports only a *possible* 7–11 October window, not a verified downturn. The latest W42 Official Compass has a possible retest this week with **no supported specific start/end**. Risk is not SELL authority. The app hosting credits are temporarily exhausted until **2026-10-13 00:00 UTC**, so the ETA changes are **not deployed** to preview yet. The previous stable AppDeploy v12 remains READY. The existing supervisor issue #1578 owns the retry after reset; no extra automation or paid upgrade is necessary.
