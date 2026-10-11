# Motion Design Toolkit — X article full 20-repo index and CN adoption decision

**Captured:** 2026-10-11 from the user's 3 screenshot excerpts of a motion-design resources post by @beamnxw; image descriptions were provided by the user. This is a **reference index**, not an instruction to install 20 dependencies. Also see [DESIGN_MOTION_REFERENCE_LIBRARY.md](../DESIGN_MOTION_REFERENCE_LIBRARY.md) and [Quiet Precision authority](../DESIGN.md). Screenshots show all 20 numbered entries; snippets with truncated URLs have been normalized to official GitHub repository names only when verifiable or unambiguous. Not every project has been individually security-reviewed.

## Complete article index

| No. | Repository | Intended layer in article | Use in Cycle Navigator |
|---|---|---|---|
| 01 | [remotion-dev/remotion](https://github.com/remotion-dev/remotion) | Code-defined editable video | **Future**, weekly editorial mini-explainers, not in live site |
| 02 | [remotion-dev/skills](https://github.com/remotion-dev/skills) | Agent video composition workflows | Future media QA and render discipline |
| 03 | [motion-canvas/motion-canvas](https://github.com/motion-canvas/motion-canvas) | TS diagram and explainer animation | **Relevant** for optional offline clips/contact sheets, not a main-page runtime requirement |
| 04 | [motiondivision/ai-kit](https://github.com/motiondivision/ai-kit) | Motion AI agent instructions | **Relevant reference**; some advanced Motion+ features paid, not needed for current public site |
| 05 | [motiondivision/motion](https://github.com/motiondivision/motion) | UI transitions, gestures, animation | **Relevant** if future interactions outgrow native CSS; no dependency now |
| 06 | [greensock/GSAP](https://github.com/greensock/GSAP) | Precise timelines and SVG motion | **Relevant reference**; a lightweight, staged range reveal is sufficient for now |
| 07 | [juliangarnier/anime](https://github.com/juliangarnier/anime) | SVG/DOM motion | Optional alternative; do not combine competing runtime animation libraries |
| 08 | [greensock/gsap-skills](https://github.com/greensock/gsap-skills) | AI motion production skills | **Relevant** authoring/QA reference |
| 09 | [rive-app/rive-web](https://github.com/rive-app/rive-web) | Interactive state-driven vector animations | Future optional stage instrument only with proven explanatory value |
| 10 | [LottieFiles/dotlottie-web](https://github.com/LottieFiles/dotlottie-web) | Lottie player and state machine runtime | Future small pre-authored explainer asset, not on score data itself |
| 11 | [mrdoob/three.js](https://github.com/mrdoob/three.js) | 3D geometry/lighting | **Not for CN dashboard**: heavier and visually noisy |
| 12 | [pmndrs/react-three-fiber](https://github.com/pmndrs/react-three-fiber) | Three.js as React components | Not applicable to current vanilla static site |
| 13 | [pmndrs/drei](https://github.com/pmndrs/drei) | React Three Fiber utilities | Not applicable |
| 14 | [pmndrs/react-three-rapier](https://github.com/pmndrs/react-three-rapier) | 3D physics | Reject for price/market UI |
| 15 | [pmndrs/react-postprocessing](https://github.com/pmndrs/react-postprocessing) | Bloom, DOF, finishing effects | Reject for institutional dashboard (risk of low information-to-noise) |
| 16 | [svg/svgo](https://github.com/svg/svgo) | Clean/minify SVG files | **Recommended** for future vector asset build step; not a runtime dependency |
| 17 | [vercel/satori](https://github.com/vercel/satori) | JSX to SVG titles | **Relevant** for static CN score share cards, future X use optional |
| 18 | [goldfire/howler.js](https://github.com/goldfire/howler.js) | Sound effects/fades | Reject; finance website should not play unsolicited sound |
| 19 | [Vanilagy/mediabunny](https://github.com/Vanilagy/mediabunny) | In-browser media encoding | Future download/export tool only, not needed for score chart |
| 20 | [FFmpeg/FFmpeg](https://github.com/FFmpeg/FFmpeg) | Final video rendering/inspection | Future offline media QA, not on public website |

## Strict CN adoption policy

**Currently adopted: ZERO external runtime dependencies.** We take GSAP/Motion/Motion Canvas *design principles*, not dependency bloat. Tiny native CSS/JS stage transitions on frozen-vs-actual score bars achieve the same explanatory objective faster and more accessibly.

### CN range reveal — 3-step deterministic motion brief

Data from the completed, already frozen **public** scorecard (never from model fabrication):

1. Stage A **FROZEN**, 0–220ms: existing forecast bars are visible; data remain legible.
2. Stage B **REALIZED**, from ~350ms: reveal actual low–high bars *at their final values* using opacity/translate (NOT fake moving prices, interpolated paths or speculative time-progression).
3. Stage C **ASSESS**, from ~750ms: reveal the original source-graded score; no recomputation in the browser. Keep full status view afterward.

A small replay control repeats the same diagram; switch BTC/ETH repeats only on deliberate interaction. When `prefers-reduced-motion: reduce` is set, **all** data and score bars appear fully visible, no animation. No autoplay looping. If records are absent, show a safe no-data message.

### Motion QA acceptance

- Three semantic stages labelled DA/EN and tied to same public issue, forecast week, original freeze and original completed scorecard.
- Source values, relative scaling and score computation **unchanged** across stages.
- All controls keyboard-accessible, accessible text for both bands, no hover-only disclosure.
- Mobile Safari 390×844 + 430×932 with no sideways scroll, no jumpy layout; check frame stills at t=0, 200, 550, 900ms and end.
- One-scoring-era view only. Old X/legacy history remains in disclosure. No fake 'live feed', '100% accuracy', 'confirmed Edge', deterministic pullback ETA or fictitious bullish market progress.
- Do not deploy to production until site contract, score lineage, actual iPhone screenshots and source-based score-readback are green.

## Candidate future use if editorial video launch approved

If future CN weekly recap / X post needs a 5–12 second scoreproof clip, use Satori for static title art and Motion Canvas or Remotion for source-exact frozen → realized → score, then FFmpeg inspect/export. Exclude audio by default. Such an export must visibly include forecast public timestamp and score proof-state and never imply a post-hoc score existed beforehand.

## Parallel investigation references

- [Existing design source library](../DESIGN_MOTION_REFERENCE_LIBRARY.md)
- [CN vNext source and prototype contract](README.md)
- [Public score evidence repo](https://github.com/Donh91/CycleNavigator-scores)
