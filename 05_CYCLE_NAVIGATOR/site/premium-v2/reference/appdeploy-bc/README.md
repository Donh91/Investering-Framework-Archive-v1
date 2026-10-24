# Exact AppDeploy Graph B/C design-source snapshot · quarantined

**Status:** REFERENCE SOURCE ONLY · NEVER SHIP OR BUILD AS THE OFFICIAL SITE  
**Source app:** `cycle-navigator-b-c-design-lab-ypjsxz` · **snapshot:** `1792595071401`  
**Original route:** https://cycle-navigator-b-c-design-lab-ypjsxz.v2.appdeploy.ai/#b

The nine files in this folder were copied from the AppDeploy source snapshot at the pinned version **without rewriting** them. They preserve the actual HTML/SVG card anatomy, typography, Tailwind selectors, module wiring and deterministic demo behavior so that the approved geometry can be compared at source level with a properly typed new consumer. This snapshot deliberately includes **synthetic BTC/ETH data**: `src/main.ts::points()` uses `Math.sin` and produces 168-point mock forecast, upper/lower band and actual streams. **NEVER import, compile, ship, expose, or promote these fake prices as a verified forecast, factual market history, Proof, Kompas or CN state.**

In addition, this source includes a B/C design switch and an AppDeploy external alternative link, both **development only** and not suitable for the canonical Pages product. No real backend or price feed is present in these nine files. The pinned `package.json` expresses only Vite/TypeScript/Tailwind/PostCSS/Lucide design-time dependencies; production adoption requires separate lockfile, dependency/security and compatibility review.

The real production-grade frontend must be implemented in a separate `premium-v2` source lane, using these **exact design structure and style definitions**, adapted only via reviewed code and fed from the existing canonical first-party read-only public snapshot. A blue oscillating prospective price series remains unavailable for W43.

**The current `site/build-public.mjs` has an explicit public-asset allowlist and DOES NOT copy this reference folder. Do not amend that allowlist to include the quarantine.**

Original files: 
- `index.html` (14317 UTF-8 JS string units, 367 lines)
- `package.json` (479 UTF-8 JS string units, 25 lines)
- `postcss.config.js` (81 UTF-8 JS string units, 7 lines)
- `src/main.ts` (13059 UTF-8 JS string units, 368 lines)
- `src/styles.css` (15170 UTF-8 JS string units, 823 lines)
- `tailwind.config.js` (155 UTF-8 JS string units, 7 lines)
- `tests/tests.json` (2973 UTF-8 JS string units, 71 lines)
- `tsconfig.json` (485 UTF-8 JS string units, 20 lines)
- `vite.config.ts` (310 UTF-8 JS string units, 14 lines)

Ownership: existing SITE #1578, Supervisor #1156. User-approved project work but **no root release without separate acceptance**.
