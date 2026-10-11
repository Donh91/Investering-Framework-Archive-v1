# Cycle Navigator vNext Work QA report — 11 October 2026

**Scope:** Work packet phases A–D for the isolated design preview on PR #1576.  
**Production:** unchanged. No merge, Pages deploy, live signal edit, score mutation, or automation change.  
**Preview:** https://cycle-navigator-vnext-preview-l1nbkq.v2.appdeploy.ai/  
**Branch:** `design/cn-vnext-public-proof-20261011`

## Status

| Gate | Result |
|---|---|
| DESIGN | Desktop Work Browser review completed; design findings fixed on branch. Baseline mobile and desktop QA screenshots are linked below. Post-fix screenshots are blocked because AppDeploy has paused new deployments until its 2026-10-12 00:00 UTC credit reset. |
| FUNCTIONAL | Navigation across Overblik / Kompas / Resultater, DA/EN switching, reload persistence, legacy disclosure, BTC/ETH range switch, replay, and Escape close were observed in Work Browser. |
| ACCESSIBILITY | Source dialog role and initial focus verified; focus escaped the modal on Tab. Added a focus loop and cycle disclosure `aria-expanded`. The updated behavior still needs a browser run after the isolated preview can be redeployed. No native iPhone Safari or 390/430 viewport after-fix verification yet. |
| DATA PARITY | Mapping and fail-closed fixtures are recorded below. The preview remains an archived sample, never a continuous/live source. |
| SCORE HONESTY | W42 score cards remain pending; legacy CN1–27 stays under disclosure; CN27 Market/Structure and aggregate stay null. The forecast proof is not labelled ex-ante verified. |
| CI | Local package-free check passed. GitHub exact-head workflow and product/architecture gates were still running at code head `acdda9f8a2d0c2aff345c8de5d46b3fa41abeebf` when checked; this report commit will create a newer head. Recheck that exact final head. |
| DEPLOYMENT | Isolated preview redeploy unavailable due AppDeploy daily credit limit. Current production remains unchanged. |
| RELEASE | Not approved. Keep PR #1576 Draft; do not merge it as a production upgrade. |

## Findings fixed in this PR

1. **DA/EN leakage:** visible labels and Compass explanations were mixed-language. Added explicit translations for score headings, checkpoint labels, action copy, source-provided risk explanations and detailed driver text.
2. **Mobile first viewport:** the approved mobile baseline placed the official action below the large hero. Added a compact, mobile-only `OFFICIAL ACTION` line, bound to `compass.action_now`, so direction and action can be read together without treating direction as a buy signal.
3. **Snapshot freshness:** the home source label previously showed only a date. It now displays the archived Compass timestamp in UTC and still identifies the page as a pinned preview, not live trading.
4. **Unconfirmed future public issue:** removed the hard assertion that W42 will be public CN #29. The next-series line now says the issue ID is pending.
5. **Source mismatch:** the preview validator now requires the exact W41 archived Compass ID and issued timestamp, in addition to the existing issue/week and history checks. A different or newer Compass snapshot fails closed.
6. **Keyboard accessibility:** the source dialog now traps Tab/Shift+Tab and retains Escape-to-close/focus return. The cycle disclosure now exposes and updates `aria-expanded`.
7. **Incomplete range data:** extracted price-row eligibility into a small pure helper; missing or malformed intervals are not scored.

## Current source mapping

| UI element | Authority/source | Current verified meaning |
|---|---|---|
| Public issue/week and weekly health | `LATEST_CYCLE_NAVIGATOR_POINTER.json`, `CN_PUBLIC_SERIES_INDEX.json`, W41 delivery pointer and public-series binding | Public CN #28 / 2026-W41; weekly status DEGRADED; machine issue 29 is an internal migration identity and is not displayed as public CN #29. Consumer receipt PASS. |
| Weekly BTC/ETH ranges | W41 `CYCLE_NAVIGATOR_FORECAST_FREEZE.json` | Frozen BTC $82,000–$92,000 and ETH $2,560–$2,960. These are scenario intervals, not spot prices or probabilities. |
| Preview tactical direction/action, horizon table and rotation | Pinned public projection `CMP-20261011-7d14a9ee5914`, issued 2026-10-11 13:15:27 UTC | The archived preview source says HOLD_WAIT; near horizons and capitalization ladder retain their source fields. Meme action is UNAVAILABLE. This is deliberately not the latest Compass: the current main pointer later referenced `CMP-20261011-50c5e8279ae0`, issued 20:19:43 UTC. The pinned sample remains timestamped and cannot be represented as live. |
| Pullback / distribution / sell / re-entry | Same pinned official Compass protection tracker and sell assessment | BUILDING is a watch, distribution is UNKNOWN, SELL is UNAVAILABLE, and re-entry is INACTIVE. No site-derived SELL or ETA. |
| Historic scorecard and chart replay | Public CN #27 / W40 score data carried in the pinned public snapshot; score history projection | Price Range 82.05%, BTC 82.27%, ETH 81.82%, 168 hours of coverage; Market/Structure and combined score null. Six BTC/ETH interval rows remain source-exact. |
| Legacy score list | Public history projection | 27 individual records retained under expandable archive; unlike eras are not averaged together. |
| W42 Edge cards / checkpoints | Public scorebook protocol and prospective freeze owner | All three score families remain PENDING; future public issue identity is not preclaimed. The preview does not consume or manufacture a matured W42 score. |
| Independent proof status | CycleNavigator-scores proof issue #2 | Independent immutable release/timestamp verification remains a separate gate; current UI remains LEGACY / PROVISIONAL. |

## Negative fixtures and local verification

`node 05_CYCLE_NAVIGATOR/site/vnext-preview/check-premium.mjs` passed from a clean temporary copy of the exact branch files.

The package-free checks now exercise:

- reject a LIVE label for the point-in-time archive, unexpected public issue/week, a different or later Compass ID/time, fabricated combined score, or incomplete 27-record history;
- accept the known W41 pinned sample while preserving visible DEGRADED status;
- preserve HOLD_WAIT, BUILDING, UNKNOWN distribution, unavailable SELL, inactive re-entry and unavailable MEMES;
- accept three valid BTC price windows, and exclude missing/partial/malformed bars instead of reporting a score;
- require bilingual wording for source-owned action/risk explanations and the W42 issue-ID-pending line;
- check modal keyboard containment, focus semantics, disclosure ARIA, mobile-only action layout, reduced-motion styling, dependency-free motion and JavaScript syntax.

The UI source and tests do **not** claim to simulate every live production failure mode. Production source parity, current public score proof consumption and 390/430 after-fix browser acceptance remain release gates.

## Browser review and evidence

Work Browser visually inspected the isolated preview at its available desktop viewport (1348×918). The desktop layout is calm and legible; frozen vs observed range bars preserve fixed endpoints and the recorded score reveal, and BTC/ETH switching changed to the expected six source rows. The three page routes and persistent DA/EN choice were inspected. The browser is not native iPhone Safari and this session did not expose a supported viewport-resize control.

The Work Browser also compared the unchanged production page. It still showed the original NOW / PATH / PROOF site and live-context surface.

Previous AppDeploy QA capture, **before this branch's fixes**:

- Mobile baseline: https://appdeployai-v2-qa-screenshots.s3.us-east-1.amazonaws.com/cycle-navigator-vnext-preview-l1nbkq/1791751671448/mobile.png
- Desktop baseline: https://appdeployai-v2-qa-screenshots.s3.us-east-1.amazonaws.com/cycle-navigator-vnext-preview-l1nbkq/1791751671448/web.png

AppDeploy instructions returned `CREDITS_USAGE_LIMIT_REACHED` and specify redeploy is paused until **2026-10-12 00:00 UTC**. Do not mistake those pre-fix images or the last READY deployment for proof of the new mobile action line, translations or modal fix.

## Remaining exact actions

1. After the AppDeploy UTC reset, redeploy only app `cycle-navigator-vnext-preview-l1nbkq` from the synchronized branch source; do not touch the separate production-delivery app.
2. Capture fresh mobile 390×844 and 430×932 plus desktop screenshots; verify action line appears in the first mobile viewport, DA/EN after reload, dialogs and disclosure keyboard behavior, reduced motion, and no overflow.
3. Re-run CI on the latest PR head after this report is committed. Record the exact workflow conclusions for the preview smoke check and the applicable CN product, contract and architecture gates.
4. Complete source-to-element review against the production `build-public.mjs` output and add only a separate, bounded production integration PR after inventory, source parity, rollback and exact-head gates are independently accepted.
5. Keep W42 score/proof and cross-repo owner work with existing #1578 and CycleNavigator-scores #2 owners. Do not backdate a freeze, score qualitative prose as 100, or change any live action.

