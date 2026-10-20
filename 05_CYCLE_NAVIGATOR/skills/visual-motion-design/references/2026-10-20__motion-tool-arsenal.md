# Cycle Navigator — Visual & Motion Tool Arsenal (reference only)

**Logged:** 2026-10-20  
**Source post:** https://x.com/Marlenuii/status/2111419391271186795 (Marlen, 2026-10-17)  
**Classification:** DESIGN_REFERENCE_ONLY, not a canonical site specification, component dependency, workflow, engine, or automatic installation.  
**Owner:** Existing Cycle Navigator `visual-motion-design` skill and `05_CYCLE_NAVIGATOR/site/DESIGN.md`.

## Why this is useful

The post curates 15 open-source repositories for programmable motion/video production. Cycle Navigator has two distinct design needs: (1) **existing iPhone-first static website** and (2) **optional social/X/Telegram explanatory media**. Most entries are more relevant to the second need. Preserve the approved Quiet Precision visual language and existing site architecture.

## Selective shortlist

| Tool | Source | Suitability and permitted consideration |
| --- | --- | --- |
| **Lucide** | https://github.com/lucide-icons/lucide | **HIGH, site visual reference**: consistent restrained line-icon geometry. Prefer existing CN SVG/icon assets first; use approved, licensed SVGs only if the existing semantic set lacks an icon. Do not insert an icon library solely for decoration. |
| **Remotion** | https://github.com/remotion-dev/remotion | **HIGH, optional off-site social-video prototype**: programmatic short weekly forecast-vs-observed or phase-explainer clips. If used, run in a separately validated media build, not the static public site. Review current licensing, render costs, and provenance first. |
| **FFmpeg** | https://github.com/FFmpeg/FFmpeg | **HIGH when exporting approved video**: encode/compress MP4, captions and inspect output after a reproducible build. Verify distribution/build licensing; no need for the live website. |
| **Excalidraw** | https://github.com/excalidraw/excalidraw | **MEDIUM, design workflow only**: outline a PATH/Kompas storyboard or information hierarchy before code. Not a runtime dependency. |
| **Penpot** | https://github.com/penpot/penpot | **MEDIUM, design workflow only**: reusable visual layouts and media storyboards when a genuine design iteration is needed. Do not replace approved `DESIGN.md`. |
| **GSAP** | https://github.com/greensock/GSAP | **CONDITIONAL, later**: synchronized multi-step animations only where plain CSS and the existing `motion.js` cannot communicate a true state/sequence transition. Check bundle size, license and reduced-motion behavior first. |

## Other links from the post: not adopted by default

- **Motion**: https://github.com/motiondivision/motion — useful React animation system, but the production site currently uses HTML/CSS/vanilla JS; do not introduce a React migration for motion.
- **Fontsource**: https://github.com/fontsource/fontsource — no current need: `DESIGN.md` already prefers the Apple/system font stack.
- **Three.js**: https://github.com/mrdoob/three.js — cinematic 3D is not appropriate for the core financial instrument.
- **React Three Fiber**: https://github.com/pmndrs/react-three-fiber — no 3D/React dependency justified.
- **Drei**: https://github.com/pmndrs/drei — no 3D helper stack justified.
- **Blender**: https://github.com/blender/blender — optional standalone video artwork only, no website dependency.
- **Lottie Web**: https://github.com/airbnb/lottie-web — only if a purposeful lightweight vector animation is demonstrably better than CSS/SVG.
- **Audacity**: https://github.com/audacity/audacity — only if a narrated video actually requires sound editing.
- **Whisper**: https://github.com/openai/whisper — only if an approved voiceover requires captions or timed transcription. Verify privacy and processing environment.

## Agent selection protocol

1. **Classify output**: public website UI, visual mockup, social infographic, or short video.
2. **Read current authority**: `AGENTS.md`, `05_CYCLE_NAVIGATOR/site/SITE_CONTRACT.md`, `DESIGN.md`, current site code, and the relevant frozen/verified public data pointer. Preserve existing Kompas vs PATH information boundaries.
3. **Default to native tooling**: existing HTML/CSS/vanilla JS, CN SVGs, existing graph and icon primitives. Consult this arsenal only for a *missing capability* and select at most the tools needed.
4. **For a weekly forecast visual**: forecast must stay prospectively frozen, observed series must use actual eligible source observations, and cutoffs, missing coverage, forecasts, actuals and scores remain visibly distinguishable. Never create motion that implies fabricated prices or false certainty.
5. **For any third-party package**: check upstream license/attribution, security maintenance, actual dependencies, runtime/bundle weight, free hosting/build compatibility, source provenance and reproducibility before recommending installation. A curated X post is discovery evidence, not verification of package quality.
6. **If altering the site**: respect iPhone Safari 390/430 px layouts, `prefers-reduced-motion`, no horizontal scroll, no performance regression, no decorative financial animation; follow existing PR/CI and review gates.
7. **If producing social videos**: use a separate optional export/prototype lane. No new automation, paid service, market-engine logic, production site dependency or workflow without separately justified owner approval and review.
8. **No auto-adoption**: the skill may consult these links automatically when a relevant design task arrives; it may not install, execute or promote a tool automatically based only on this reference.

## Classification / housekeeping

This is a **selective source reference**, not a requirement to use the listed tools. Keep a single local reference under the existing design skill; do not duplicate the list in the top-level canonical index, site runtime or Research Lab. Update it only when a real design use case or license/security review warrants it.
