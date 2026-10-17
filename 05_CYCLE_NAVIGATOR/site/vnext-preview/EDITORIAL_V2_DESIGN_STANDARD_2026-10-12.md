# Cycle Navigator · Editorial UI v2 — product design standard

**Date:** 2026-10-12 · **Owner:** existing Cycle Navigator vNext site branch PR #1576  
**Status:** Implemented in *isolated preview*, pending native iPhone acceptance and separate production integration. **Do not promote this design alone into live market/action authority.**

## Design correction: information should outweigh ornament

User feedback on the 12 October preview screenshot: the huge dark `CN / MARKET INSTRUMENT` radial/radar visualization dominated a phone screen while communicating nothing that the verified official signal labels could not convey more directly. A three-card `Decision Desk` then repeated the very same HOLD/WAIT action and risk labels. Decorative range progress corridors were not scaled to outcomes, and the compass graphic in the market-cycle panel was also unnecessary.

**Editorial v2 removes outright:** radar SVG and navy radar card; second set of action and risk cards; ornamental cycle compass image; fake BTC/ETH 'corridor' progress bars; unreadable wide labels; extra dark-heavy cycle section. Deprecated hero CSS is removed. No third-party runtime CSS, sound, animation, charts or WebGL is introduced.

### Visual hierarchy: 6-second test

1. **Market direction**: source-owned status, explicitly labeled 12h. This is NOT permission to trade.
2. **Official action now**: Official Compass sole owner, next to direction, on the very first information row.
3. **Next 1–3d** and **ETH/BTC + market breadth** conditional confirmation, still source-bounded. No unsupported ETA.
4. **Pullback risk**: official tracker state and one-sentence limitation, never interpreted as SELL.
5. **Source provenance**: actual fixed Compass UTC snapshot timestamp + weekly health + direct link to evidence. Preview stays clearly marked NON-LIVE.
6. Below this, a **meaningful textual** market-cycle phase sequence and two actual frozen weekly BTC/ETH scenario *numbers*. Historical scorecard reveal remains the only animation because it explains a measurable difference.

### Reference skill usage

The existing [13-link motion-agent source index](../DESIGN_MOTION_REFERENCE_LIBRARY.md) and [20-repository motion design/tool index](MOTION_TOOLKIT_20_REPOS_AND_CN_DECISION.md) were reviewed as engineering references. We deliberately **do not install GSAP, Remotion, Motion Canvas, React Three Fiber, Rive, Lottie or Sound** into the CN live dashboard. Motion is justified only when it communicates data: the source-exact frozen price range → actual range → independently calculated score sequence already meets that purpose in native CSS/JS. Every other section is quiet/static.

This is a **new design system**, not a request for a new CSS/animation vendor. We borrow clarity, restrained hierarchy and timing discipline from the archived professional design references.

### Tokens and component grammar

- Canvas: `#f6f7f8`; card: white; text `#13283e`; border `#dfe5eb`; accent used on significant text only, never decorative controls.
- Truth-bearing status color: source-defined direction; risk shown distinctly in muted amber without implying a sell instruction.
- Typography: native system sans; large but no display-size W42 gimmicks above decision content. Labels 9–10 px secondary, primary figures 18–30 px, copy 12–14 px with 1.6 line-height. Do not use all-caps for long prose.
- Layout: **one primary panel** on Overview, spacious but short enough to show decision and risk without scrolling past meaningless artwork. On mobile, two concise direction/action columns, three compact fact rows, thin inline source footer.
- No multiple redundant card borders, concentric circles, gradients representing no variable, fake price trajectories or status animations.
- Path stages remain textual and conditional, not 'we are here' claims invented by UI. Stage emphasis must trace to canonical source; if absent, display neutral context.
- Price Range forecast cards display the frozen numbers without pseudo-scaled bars. Evidence-backed completed score reveal is separate in Resultater > historical details.
- Pages: **Overblik | Kompas | Resultater**, persistent DA/EN switch, no new routes, signal owners or cron jobs.

### Fixed data separation

- Pinned demonstration bundle stays archival `CN28/W41` with Compass snapshot issued 2026-10-11T13:15:27Z; never dress it as Monday's live `CN29/W42`.
- Actual W42 currently public #29 / machine #30; latest completed Price Range is CN28/W41 at 49.56%, and first W42 v2 binary claim set is **10 ABSTAIN**. Public score/proof flags are still PROVISIONAL, not VERIFIED.
- The pure `official-feed-parity.mjs` is only the **planned** future production consumer for `site/build-public.mjs` generated `data/latest.json` and `data/compass.json`. No live frontend consumption or production merge is authorized without a bounded integration PR and proof/freshness review.

## Acceptance criteria

- [x] Remove radar instrument, duplicated decision panel, path compass picture and fake range bars in source.
- [x] Consolidate verified direction, action, pullback, confirmation and provenance in one responsive plain panel.
- [x] Preserve existing source-identity and fail-closed handling; no extra market logic.
- [x] Preserve full DA/EN including dynamic UTC/source labels and separated market text.
- [x] Pass exact-head PR smoke/source, Compass and architecture gates (recheck on every new head).
- [x] Deploy to the existing **isolated** public preview only, zero recorded frontend/network errors.
- [x] Independent browser interaction QA confirms radar, duplicate card removal; source labels, routes and language work. Browser viewport was tablet/desktop (1020–1280 px), **not native iPhone**.
- [ ] Visually inspect after-fix 390×844 / 430×932 in an independent mobile browser / real Safari, including overflow and keyboard.
- [ ] Compare NOW/PATH/WHY/PROOF information inventory before any production deployment.
- [ ] Current official feed consumer source tests + rollback in separate production PR; never use archived seed as live data.
- [ ] Verified immutable and externally anchored CN score attestation is owned by scores repo issue #2.

**Current deployment:** https://cycle-navigator-vnext-preview-l1nbkq.v2.appdeploy.ai/  
**Original unchanged production:** https://donh91.github.io/Investering-Framework-Archive-v1/  
**Work source/QA ownership:** https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1578
