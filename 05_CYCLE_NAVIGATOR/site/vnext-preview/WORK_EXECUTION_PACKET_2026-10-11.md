# WORK EXECUTION PACKET — Cycle Navigator vNext (visual/product release audit)

**Prepared:** 2026-10-11 · **Execution owner:** one dedicated ChatGPT Work coordinator · **Priority:** P0 site release readiness, subordinate to actual pre-outcome W42 freeze integrity · **Status:** READY FOR WORK HANDOFF / NOT YET WORK-EXECUTED.

**One-line start:** Read this packet and [Archive coordination issue #1578](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1578), open [site design PR #1576](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1576), then inspect the functioning [isolated preview](https://cycle-navigator-vnext-preview-l1nbkq.v2.appdeploy.ai/). Carry out the end-to-end UI/QA and source-integration audit without taking the existing production website offline.

This packet is the **site/product-specific handover**; issue #1578 is the **cross-agent CN v2 Edge/Monday/score ledger coordinator**. Do not create a duplicate supervisor or competing source owner. The user specifically gave a broad remit to refine presentation, test comprehensively and fix visual/functional deficiencies, but authorized no irreversible changes to live market signals or historical scores.

## 0. Sources, ownership and exact entry points

| Authority / lane | Read | Safe action |
|---|---|---|
| Production website | https://donh91.github.io/Investering-Framework-Archive-v1/ | READ/compare. Do not break, replace or silently deploy |
| Isolated live premium preview | https://cycle-navigator-vnext-preview-l1nbkq.v2.appdeploy.ai/ | READ/QA; update only after GitHub source synchronized |
| Site code review | https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1576 | Keep Draft until all release criteria pass; make changes on its existing branch |
| Actual site folder | `05_CYCLE_NAVIGATOR/site/` | Canonical public presentation home; no rival public website or parallel codebase |
| Preview source files | `05_CYCLE_NAVIGATOR/site/vnext-preview/premium-index.html`, `premium.css`, `premium.js`, `premium-i18n.js`, `seed.json`, `check-premium.mjs`, `README.md` | Editable on PR #1576, preview snapshot is deliberately frozen and not live |
| Product requirements | `05_CYCLE_NAVIGATOR/site/VNEXT_PRODUCT_SPEC_2026-10-11.md`; `SITE_CONTRACT.md`; `DESIGN.md` | These and newer superseding W42 addendum govern; reconcile fresh main |
| New motion references | `05_CYCLE_NAVIGATOR/site/vnext-preview/MOTION_TOOLKIT_20_REPOS_AND_CN_DECISION.md`; `site/DESIGN_MOTION_REFERENCE_LIBRARY.md` | Already archived; prefer existing dependency-free range reveal, no 3D/audio bloat |
| Official weekly CN | `05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json`; `public_series/CN_PUBLIC_SERIES_INDEX.json`; per-week machine/freeze/receipts | Read-only public issue/week/state/ranges, never derive synthetic official phases |
| Official tactical Compass | `04_MARKET_LEARNING/handlekompas/official/PUBLIC_LATEST_COMPASS.json` + its exact public projection | Only official action/Capitalization/Protection/Sell/Reentry; preserve identity/freshness |
| Public verification scores | https://github.com/Donh91/CycleNavigator-scores | Read-only site integration; historical score mirror now main; immutable release proof separate |
| Source freeze & v2 scorebook | [Archive #1577](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1577) (MERGED), [Score engine #3](https://github.com/Donh91/CycleNavigator-scores/pull/3) (MERGED) | Do not duplicate their owner; grade claims only if genuinely typed, frozen and matured |
| Proof infrastructure gate | https://github.com/Donh91/CycleNavigator-scores/issues/2 | Separate blocker for immutable release, independent anchor and prospective proof |
| Other research owner | https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1573 | Ongoing Horizon Edge mission; do not absorb or rewrite unproven research |

### Last verified at packaging

- Preview includes DA/EN persistent toggle, 3 sections **Overblik / Kompas / Resultater**, new v2 price/direction/pullback public score chapter, 12–48h/7/14/21/28/56d checkpoints, and legacy public CN1–27/X history behind expandable disclosure.
- Historical true CN #27 2026-W40 price score **82.05%** with six BTC/ETH frozen-vs-actual rows; annual/methodological eras MUST NOT be mixed. Historic market-structure score is null from CN #27; no new artificial aggregate.
- Results has `Se animeret sammenligning` → expands CN #27 legacy and opens a 3-stage `FROZEN → ACTUAL → SCORE` comparison. Replay, BTC/ETH, DA/EN; original range endpoints never move; animation fully visible and nonanimated for reduced motion.
- Preview source `seed.json` is **point-in-time**: public CN #28/W41, WEEKLY DEGRADED, Official Compass `CMP-20261011-7d14a9ee5914` issued 2026-10-11T13:15:27Z, action HOLD_WAIT, pullback BUILDING. Site MUST NOT call this live; W42 claims were pending at last preview publication.
- GitHub site PR #1576 latest-head static and architecture checks were GREEN at previous verification (but verify CURRENT exact head anew, rather than trusting this sentence).
- AppDeploy last isolated deployment READY with no platform-detected frontend/network errors. **This is NOT proof of full iPhone UI acceptance or click-by-click E2E**.
- Independent Firecrawl browser session could not run because third-party credits were exhausted. **Work Cloud Browser is needed for independent visual/functional QA**, with supported permissions; do not ask the user to add Firecrawl credits unless there is truly no alternative.
- Production URL remains unchanged.
- More recent GitHub changes/workflows may exist by execution time: ALWAYS read fresh current main/PR state and avoid work overlap.

## 1. Work phase A — browser QA and truthful presentation (MANDATORY FIRST)

Use Work's own browser/computer interface to view the preview, take or record screenshots and inspect both responsive and actual iPhone Safari when available. Work cloud viewport simulation is not a guarantee of native Safari behavior; report which was verified. At minimum:

- 390×844 and 430×932 mobile, 768 tablet and 1280+ desktop; portrait; header, safe area and mobile bottom dock; no horizontal overflow, accidental overlay, text clipping, tiny controls or layout shift.
- Navigate **Overblik → Kompas → Resultater** in DA and EN; test toggling from each page and persistent language after reload.
- Check body copy, especially any untranslated mixed DA/EN content, datetime and decimal formatting, direction/action labels and aria descriptions. Numeric source values must remain unchanged by language.
- Fully expand/collapse market journey, Compass interpretation and risk details, all 27 historical scores, and source info dialog; verify logical focus order, keyboard operation, ESC close, accessible modal focus, touch targets, VoiceOver/readable labels.
- Results: confirm the NEW W42 Score Era is dominant, three primary score families show **PENDING/ABSTAIN** absent authenticated W42 scores, no implied edge. Test multi-horizon checkpoint line and pullback warning tape. Older scores must remain accessible behind disclosure, not lead as a fresh KPI.
- **Range reveal test:** press `Se animeret sammenligning`; verify disclosure opens and chart scrolls into view. Observe 0ms/frozen → ~350ms/actual → ~880ms/source score using recorded frames when supported. Replay at least twice; change BTC→ETH and back; check each interval is identical to `seed.json`. Test no animation mode with `prefers-reduced-motion:reduce`. Verify actual bars are only revealed, never simulated sliding endpoints or price-path direction.
- Validate source/quality semantics: CN #28 W41 DEGRADED not cosmetically hidden, Official Compass HOLD/WAIT despite near-term bullish direction, 4–8w unavailable, pullback BUILDING but SELL UNAVAILABLE, distribution UNKNOWN, re-entry INACTIVE. No site-derived BUY/SELL/ETA.
- UX task: a new visitor must answer **What direction? What action? Which time window? What invalidates? How can the historical claim be independently checked?** ideally under 10 seconds. A visual design that is beautiful but obscures any of these is not accepted.
- Save **before/after screenshots** to PR evidence and note visual defects precisely; prioritize fixes for confusing cycle timeline, excess repetition, accessibility, small-screen wrapping, chart legends/ranges, source date labels and score trust clarity. Compare production public site; do not assume all original functionality is obsolete.

## 2. Work phase B — code review, source and fail-closed tests

- Read `05_CYCLE_NAVIGATOR/site/SITE_CONTRACT.md`, the superseding W42 product-spec addendum and current `site/build-public.mjs` before deciding a production data path. The preview's frozen seed is *not* an acceptable continuous live source.
- Compare live production `data/latest.json`, `data/compass.json` and related public score payloads to CN weekly pointer/public-series, official public Compass pointer and public scorecard indices. Produce a **source-to-element mapping table** for everything the new 3-tab UI shows; no app-authored market forecasts.
- Explicit negative scenarios/fixtures: stale Compass but weekly fresh, weekly DEGRADED, both stale, missing price bars, mismatched CN public issue/week, stale or missing score proof, no valid microcap/meme source, unknown SELL, NO_WARNING vs BUILDING, stale translation data, late post-outcome freeze, missing source lineage, null score, unobservable pullback completion. In each case fail closed or show visibly bounded fallback.
- Preserve privacy allowlist: no wallet, API secret, user portfolio, personal identity, private-repo metadata or sensitive research dumped to public site or screenshots.
- Test static code and modular JS syntax/translation after changes; verify PR-scoped `.github/workflows/cn-vnext-preview-check.yml` and all established product/architecture workflows on **the exact latest commit**.
- Check multiweek claim scoreboard can keep a forecast open for **14/21/28/56d** while next week's forecast has separately frozen identity. Do not credit a pending or qualitative-only (`ABSTAIN`) claim as a 100.
- Pullback dates/impact visible only when canonical, prospective, bounded source permits. A `BUILDING` risk watch does not equate to a 5% material warning, and a pullback alone does not authorize SELL.
- **Proof display**: historic GitHub commit/score mirror does NOT mean externally ex-ante VERIFIED; use LEGACY_ATTESTED/PROVISIONAL/UNVERIFIABLE as appropriate. Proof issue #2 owns external timing settings.

## 3. Work phase C — improvements with bounded implementation

- Fix real visual bugs and semantic errors on existing `design/cn-vnext-public-proof-20261011` branch, ideally in small coherent commits. Keep the preview deployed from the canonical GitHub source, not an opaque second app-only copy.
- Make layout radically simpler and more elegant as long as source meaning and coverage remain. Use restrained Quiet Precision language, not giant 3D scenes, sound or over-animated finance charts. The 20 motion repo links are reference material only.
- Preserve one authoritative source per idea: official Compass **tactical action**, weekly CN **frozen cycle path**, score repo **public evaluation**, and public site **presentation**. No duplicate forecasting/scoring/trading owners.
- Create *bounded follow-on PR(s)* for native public-site integration only after a full NOW/PATH/WHY/PROOF content inventory. Avoid merging the whole design-preview PR into production; PR #1576 can remain an archive/prototype lane while a production-specific PR is independently reviewed.
- Do not add paid dependencies, new scheduled automations or change budgets without necessity and explicit accounting.
- Do not independently merge unrelated PRs, remove historical source files, retroactively certify W42, mutate position/SELL authorities, or rewrite prospectively frozen forecasts. If a major blocked release gate requires admin permissions, report exact UI/API action for user and leave runnable code/PR for existing owner.

## 4. Work phase D — acceptance + operator handoff (ALL REQUIRED)

Deliver in GitHub (PR comment plus issue #1578 update):

| Gate | Evidence required |
|---|---|
| DESIGN | before/after screenshots at mobile widths + desktop, readable UX/content inventory |
| FUNCTIONAL | click-by-click Overblik/Kompas/Resultater, replay, DA/EN, language persistence, zero accidental source changes |
| ACCESSIBILITY | reduced motion, focus, keyboard, VoiceOver equivalent disclosure, no horizontal overflow |
| DATA PARITY | source owner mapping + fixtures + stale/DEGRADED/fail-closed handling |
| SCORE HONESTY | Price Range separated; W42 new Edge scores pending until mature; original legacy records intact; proof status honest |
| CI | exact-head scoped checks plus existing CN site/Compass/architecture gates |
| DEPLOYMENT | isolated preview update verified; production remain unchanged until production-specific checklist/rollback is accepted |
| REMAINING BLOCKERS | exact owner, PR, link, SHA, external permission/settings and next action, no ambiguous "done" |

Success condition **for this Work mission**: visually/interaction-tested iPhone-first preview with traceable corrections and a production-ready *proposal/PR* that retains full data lineage and rollback. It does **not** automatically certify live production launch or 8-week measured predictive edge.

If a suitable browser cannot access a required page, use alternate supported Work browser tools, test exact running public URL, and document what could not be inspected. Never present a static smoke test as a full browser QA.

## 5. Copy/paste Work launch prompt

**KØR CYCLE NAVIGATOR VNEXT — FULL VISUAL AUDIT, SOURCE PARITY & RELEASE-READY HANDOVER**

Du er ansvarlig Work-koordinator med mandat til at gennemføre den samlede, dybdegående kvalitetssikring af vores nye Cycle Navigator-site.

START HER:
https://github.com/Donh91/Investering-Framework-Archive-v1/blob/design/cn-vnext-public-proof-20261011/05_CYCLE_NAVIGATOR/site/vnext-preview/WORK_EXECUTION_PACKET_2026-10-11.md

Læs derefter det overordnede koordinator-issue #1578, design-PR #1576, `SITE_CONTRACT.md`, den nyeste CN vNext-produktspecifikation og den fungerende preview:
https://cycle-navigator-vnext-preview-l1nbkq.v2.appdeploy.ai/

UDFØR, ikke blot planlæg: test alle tre sider på 390/430px mobil og desktop, dansk/engelsk, source/fail-closed, historiske CN-scoreoplysninger, den interaktive Frozen→Actual→Score-animation, replay, tilgængelighed og hele eksisterende indholdsdækning. Ret fundne fejl direkte på design-PR'ens branch; genkør CI og deploy isoleret preview. Hold den nuværende produktionshjemmeside urørt. Aflever screenshots, evidens, resultater, konkrete PR-ændringer og en prioriteret produktionsintegrationsplan i GitHub-issue #1578. Brug tilgængelige kodeagenter i afgrænsede parallelle spor, hvor det er effektivt, men ingen nye supervisorer eller dobbelt jobs. Fortsæt frem til gates er dokumenteret; rapportér kun reelle blockers og præcise resterende manuelle handlinger. Fastfrys ikke nye prognoser bagudrettet; respekter eksisterende official Compass, CN, Price Range og Score v2/Proof governance.

**Acceptance:** ingen opdigtede kurser/varsler/accuracy, ingen læk af privat data, velfungerende premium iPhone-design, verified source lineage, exact-head CI, tydeligt UDFØRT/VERIFICERET/RESTERER i GitHub. Work må ikke hævde, at W42 Edge allerede er dokumenteret.
