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

## Follow-up research: After Effects challengers and stronger repo candidates (2026-10-20)

**Owner request:** Search for tools that can replace After Effects, compare them against the original 15-project list, and log relevance to Cycle Navigator. This is a *research/selection extension* to the existing Arsenal, not a new site requirement or an automatic adoption decision.

**Boundary:** No single verified open-source repo is an exact end-to-end After Effects replacement across 2D layer motion, compositing, VFX, 3D, editing, expressions, and Adobe project/plugin compatibility. Choose by specific output. Do not promise After Effects project compatibility.

| Candidate | Official source | Decision for CN | Evidence / limits |
| --- | --- | --- | --- |
| **Motion Canvas** | https://github.com/motion-canvas/motion-canvas | **HIGH: code-driven explainers / social media** | MIT-licensed TypeScript generator-based 2D motion graphics and preview editor. Suitable for explicit, reproducible explanatory animations of frozen forecasts vs observed values, and phase timelines. Specialized vector-animation tool, *not* a full video editor or After Effects replacement. |
| **Manim Community Edition** | https://github.com/ManimCommunity/manim | **HIGH: research/calibration explainers** | Community-maintained Python mathematical animation library. Strong for verified curves, score explainers, uncertainty/coverage diagrams, and time-series education. Requires separate production environment and animation engineering; not a general GUI compositing tool. Prefer community edition over 3b1b's distinct personal ManimGL for general maintenance/onboarding. |
| **Friction Graphics** | https://github.com/friction2d/friction | **MEDIUM-HIGH: manual 2D motion and logo animation** | GPL-3.0-only standalone desktop application for vector/raster motion graphics. More direct creative After Effects-like 2D workflow than code-first tools, but weaker for integrated high-end VFX. Exports SVG/SMIL, **not Lottie**; exported SVG supports only a subset of editor features. Validate output in destination viewer/browser. |
| **Natron** | https://github.com/NatronGitHub/Natron | **MEDIUM, VFX only** | Open-source node-based video compositor, keying, rotoscoping, tracking, OpenFX; closest conceptual tool for compositing (not for CN dashboard UX). Not a single solution for procedural infographic videos or 3D scenes. |
| **Kdenlive** | https://github.com/KDE/kdenlive | **MEDIUM: optional final editing** | Free/open-source multitrack editing, titles, masks, audio, transitions and export. Used after motion renders, not as a replacement for a full motion compositor. GitHub is a mirror; upstream contributions are hosted on KDE Invent. |
| **Blender** (already listed above) | https://github.com/blender/blender | **MEDIUM: standalone cinematic/3D visual assets** | Broadest free/open-source all-round creative 3D, animation and compositing candidate, but unnecessary and potentially expensive in compute/time for routine CN market explainers. Not a site JS dependency. |
| **Remotion** (already listed above) | https://github.com/remotion-dev/remotion | **VERY HIGH: repeatable branded weekly X/Telegram video** | Strong React/JS video-rendering option when the same existing verified/frozen CN figures must be rendered into repeatable video templates. **Special license**: individuals and certain small companies can qualify for free use, but larger for-profit entities may need a company license. Check current rules *before* production. |
| **Cavalry by Canva** (non-repo product) | https://cavalry.studio/ | **HIGH: manual After Effects-style 2D design** | Officially offered free with Canva account on macOS/Windows; procedural/data-driven motion graphics, Lottie exports. **Proprietary desktop app, not an open-source GitHub repo, not executable on iPhone alone**. Best outside-code visual-production challenger; no integration decision. |
| **Maxon Autograph** (non-repo product) | https://www.maxon.net/en/autograph | **MEDIUM-HIGH: manual 2D/3D and compositing** | Officially free motion design, VFX/compositing, shape and text animation. Desktop, **proprietary**, and some integrations/plugins require separate licenses. Potential broader AE-like GUI alternative, but do not depend on it for public-site builds. |

### Practical selection for actual CN deliverables

1. **Static Cycle Navigator / Kompas / PATH UI:** existing approved HTML/CSS/SVG/motion.js primitives. **No new framework.** Mobile-first, restrained Quiet Precision, reduced-motion, no additional runtime dependencies.
2. **Repeated weekly CN video from verified, immutable forecast data:** **Remotion (first feasibility candidate)** with existing FFmpeg. Compare Motion Canvas only if vector explainer quality significantly improves; don't build both pipelines concurrently. A prospective prototype must reuse frozen inputs, show observation cutoff and missing observations honestly, label forecast and actual distinctly, render deterministic frames and record input hashes.
3. **Explanatory research diagrams / score education:** Motion Canvas for TypeScript-first workflow; ManimCE only when code-generated math/graphs add an actual advantage. These are alternatives, not mandatory combined dependencies.
4. **Distinctive logo animation or manual promotional artwork:** evaluate Cavalry (desktop/proprietary) or Friction (open source); Blender only for real 3D. Never mutate the approved compass mark or existing design system.
5. **Heavy compositing / green screen / VFX:** Natron or free Maxon Autograph; not a present CN site requirement. **Edit/final delivery:** Kdenlive/FFmpeg if needed.

### Exclusions and known traps

- Do **not** adopt an entire 'AI video studio' or promise one prompt to film-quality 4K MP4: listed repos provide ingredients, not a proven turnkey production stack.
- Do **not** confuse available open-source Rive **runtimes** with a fully open-source **editor**; no evidence for an open-editor After Effects replacement.
- Do **not** use Friction -> Lottie as an assumed export path: Friction explicitly documents SVG/SMIL instead of Lottie.
- Do **not** introduce heavy 3D or React framework migration into the GitHub Pages site to enable promotional animations.
- Do **not** auto-render from unverified live market values, infer missing points, animate scoring into certainty, or replace current frozen weekly graph with a video.
- Do **not** install or schedule anything by logging this comparison; tooling needs separate sandbox, dependency/license review, security validation, export-quality assessment, and explicit production scope.
- iPhone-only editing is not a viable assumption for desktop GUI alternatives (Cavalry, Autograph, Friction, Natron, Blender, Kdenlive). Programmatic tools require a build host if ever approved.

### Primary evidence read during evaluation

- Motion Canvas scope: https://github.com/motion-canvas/motion-canvas and https://github.com/motion-canvas/motion-canvas/blob/main/packages/docs/docs/intro.md
- Manim Community scope: https://github.com/ManimCommunity/manim
- Friction scope/licensing/export: https://github.com/friction2d/friction , https://friction.graphics/documentation/faq.html , https://friction.graphics/documentation/export.html
- Natron official source: https://github.com/NatronGitHub/Natron
- Kdenlive source and upstream disclaimer: https://github.com/KDE/kdenlive
- Remotion licensing: https://www.remotion.dev/docs/license and https://github.com/remotion-dev/remotion/blob/main/packages/core/LICENSE.md
- Cavalry product and terms: https://cavalry.studio/ and https://www.canva.com/en_gb/help/free-cavalry-access/
- Maxon Autograph product and terms: https://www.maxon.net/en/autograph

**State:** RESEARCH_REFERENCE_ONLY / NO_RUNTIME_ADOPTION / NO_NEW_AUTOMATION / NO_MARKET_LOGIC_CHANGE. This appendix records an independent relative suitability evaluation, not a benchmark, successful video render or production validation.
