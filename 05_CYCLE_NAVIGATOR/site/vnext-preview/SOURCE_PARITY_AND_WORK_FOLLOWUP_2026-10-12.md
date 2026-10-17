# Cycle Navigator vNext — Source/Work Follow-up Audit · 2026-10-12

**Source review:** GitHub main and live read-only AppDeploy preview; independent browser Safari visual signoff still pending.

## Delta since Work's 2026-10-11 review

The Work QA and Supervisor status in issue #1578 were checked first (do not overwrite that work). Work completed functional fixes at site-PR head `59c919806154c582e9106dad91cecccb6cf498ae` but its AppDeploy redeploy was blocked by credits. The subsequent Supervisor bootstrap correctly did not claim a live Work execution or merge.

**FIXED:** The same isolated AppDeploy preview ID `cycle-navigator-vnext-preview-l1nbkq` was redeployed from Work's GitHub branch sources after the resource reset. The returned deployment status was **READY** and the automated QA snapshot reported **zero frontend errors and zero network errors**.

- Preview URL: https://cycle-navigator-vnext-preview-l1nbkq.v2.appdeploy.ai/
- Updated host mobile QA screenshot: https://appdeployai-v2-qa-screenshots.s3.us-east-1.amazonaws.com/cycle-navigator-vnext-preview-l1nbkq/1791799121161/mobile.png
- Updated host desktop QA screenshot: https://appdeployai-v2-qa-screenshots.s3.us-east-1.amazonaws.com/cycle-navigator-vnext-preview-l1nbkq/1791799121161/web.png
- **Qualification:** screenshot generation is not native iPhone Safari, complete 390/430 interaction E2E, or accessibility certification. Nothing was changed in the current GitHub Pages production code or deployment.

## Newly confirmed public identity, current market and scoring records

**Monday CN public #29** / 2026-W42 is now frozen. Do not confuse its internal machine issue number #30 with public issue #29.

| Source | Exact confirmed data |
|---|---|
| `05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json` | Public issue 29; machine issue 30; W42; weekly DEGRADED / COVERAGE_LIMITATION; delivery consumer receipt PASS |
| W42 canonical public freeze receipt | Frozen 2026-10-12T06:32:25Z; first eligible full scored hour 2026-10-12T07:00:00Z; range-score method unchanged at 70% containment + 30% Jaccard |
| W42 frozen weekly range | BTC **$78,000–$88,000**; ETH **$2,260–$2,720** |
| W42 `CYCLE_NAVIGATOR_V2_EDGE_FREEZE.json` | 10 claims; **0 eligible** typed 100/0 claims; **10 ABSTAIN**. At freeze, Official Compass pullback was BUILDING (watch only) |
| Latest Official Compass checked | `CMP-20261012-5ee3762df330` issued 2026-10-12T09:35:11Z; NOW market BEARISH and 0–12h DOWN, canonical action HOLD_WAIT, current pullback ELEVATED, distribution UNKNOWN, SELL unavailable, reentry inactive |
| Compass→CN lineage | The internal Compass canonical `source_bindings.cycle_navigator` references machine issue 30 / W42 and exact matching canonical machine-package SHA-256 `ee32dccb91b6c79d6b4bed8e26b79294d7cd63609bf0a9821eac8d1d71131ceb` with status PASS |
| Latest completed public score | **CN28 / 2026-W41 Price Range 49.56%** (BTC 62.94%, ETH 36.17%), 168 eligible hourly observations, Market/Structure and overall null; frozen claims separate from Price Range |
| Public score repo | Source-exact CN28 score mirror and provisional CN29/W42 readback published via [CycleNavigator-scores PR #5](https://github.com/Donh91/CycleNavigator-scores/pull/5), now merged and CI green |
| Proof gating | GitHub blob/manifest hashes exist; independent immutable release, third-party prospective anchor and outcome reproduction NOT done. CN29 binary Edge score still null |

**Do not silently update the isolated Work preview's pinned Sunday bullish sample as if it were live.** Its archived #28/W41 and Sunday Compass identity remain intentionally fixed, and the UI must visibly disclose its timestamp and non-live preview status. Production source adapter below is intentionally a separate unmerged proposal.

## Code audit and new source wiring: no new market owner

The existing production `05_CYCLE_NAVIGATOR/site/build-public.mjs` already emits:

1. `dist/data/latest.json` (`CN_PUBLIC_SNAPSHOT_V2`) with sanitized weekly pointer + machine package, public-series numbering, source-exact completed scorecard, and weekly ranges;
2. `dist/data/compass.json` (`PUBLIC_COMPASS_PROJECTION_v1`) with independently governed NOW action, separate risk, SELL and reentry, and source-verified `weekly_context` alignment to official CN;
3. `dist/data/compass-event.json` independently, which is NOT a scorer or free authorization to SELL.

New files in **the existing site design PR #1576 branch**:

- `05_CYCLE_NAVIGATOR/site/vnext-preview/official-feed-parity.mjs` — PURE, read-only, source-bounded transformation of the actual public builder's output schemas. Never reclassifies markets or computes a score.
- `05_CYCLE_NAVIGATOR/site/vnext-preview/test-official-feed-parity.mjs` — **30 deterministic tests**, including fake public CN issue, machine/public offset, W42 vs W41 score misjoin, stale delivery, mismatched weekly alignment, Compass postdated after bundle, null forecast values, duplicate/missing price windows, missing 168h coverage, fake structure score, false automated SELL or unsealed score.
- The existing `.github/workflows/cn-vnext-preview-check.yml` now runs the additional source parity suite in the SAME draft-branch CI (no cron or production change).

Latest site PR exact head after the tests: `6fafbefbf4f51b47aac55ee467486b7bf86d5e6b`. Nine existing site/Compass/architecture/GitHub checks passed, including the new scoped preview smoke run (GitHub Actions job `static-preview`). **These are static/source tests, not real iPhone release approval.**

Important truth boundaries:

- A public scorecard is last **completed**, not the current CN forecast. Its public issue identity and price score must match the index, 168h evidence, original scoring formula and six BTC/ETH windows; else unavailable.
- Weekly DEGRADED is preserved; stale site delivery cannot masquerade as a fresh Official Compass NOW.
- A fresh independent Official Compass NOW may remain an action reference even if its weekly lineage is UNVERIFIED, but that misalignment blocks PATH live gates.
- No binary Direction/Pullback scores can be inferred merely from qualitative weekly prose or BUILDING/ELEVATED watch text; they remain ABSTAIN pending prospectively frozen numeric predicates.
- New Scorebook v2 receipt created after the first eligible W42 market hour **cannot be treated as proof** that external publication was immutable before that hour.
- The public score repo now contains CN28 and CN29 provisional readback, but that repository is still **NOT externally proof-sealed**.

## Next execution gates / ownership

1. **Work browser visual QA**: actual 390×844 and 430×932 post-Work deployment interaction checks in both languages (DA/EN), all three page routes, modal Tab/Shift+Tab/Escape focus loop, source-age badges, frozen-range animation and replay, reduced-motion. Attach after-fix screenshot and failures to #1578.
2. **Product/data wiring**: use only the current `site/build-public.mjs` generated data output and the new parity adapter as design input; do not fetch private repos or replace the official CN/Compass originator. The preview's archived `seed.json` must NOT be used as a production live feed. Do a bounded new production consumer PR after preserving NOW/PATH/WHY content coverage.
3. **True new Edge predicates**: owner #1578, not browser UI. The initial W42 qualitative-only 10x ABSTAIN is an honest record but gives ZERO statistical Edge evidence. Future weekly + tactical freezes need typed, measurable predicates, reproducible outcomes, long-horizon anti-overlap stats and no false-alarm/miss hiding.
4. **Public independent proof**: score repo issue #2 must establish immutable release settings, third-party timestamp anchors and independent recomputations before any v2 VERIFIED badges.
5. Keep site PR #1576 Draft until independent review, fresh-main reconciliation, source parity and mobile QA pass. Existing production remains unchanged.

Status: **Work fixes PREVIEW DEPLOYED, source parity CODED/CI VERIFIED, Score repo CN28/29 readback PUBLISHED PROVISIONAL, full site RELEASE + Edge proof NOT DONE.**
