# Cycle Navigator · Premium v2.1

**APPROVED MISSION, NOT APPROVED PRODUCTION RELEASE**

This folder is an **isolated development lane** under SITE #1578 and Supervisor #1156. It is deliberately NOT copied by the existing `05_CYCLE_NAVIGATOR/site/build-public.mjs` (which currently enumerates its public site assets). Nothing in this folder should appear on the official GitHub Pages homepage until separately reviewed and released.

Read in order:

1. `design-registry.json`: exact authority ordering, source paths, approved vs rejected art direction and references.
2. `RECOVERY_BASELINE.md`: P0 source-bound baseline, actual HTTP-readback evidence and unverified legacy behavior.
3. `reference/appdeploy-bc/README.md`: exact AppDeploy B/C snapshot context; the copied visual source is a deliberately quarantined DEMO, NEVER a canonical price source.
4. `graph-b/official-source-adapter.mjs` and tests: pure, source-only data gate, no HTTP or market decisions.
5. SITE `DESIGN.md`, `SITE_CONTRACT.md`, `PATH_V3_CYCLE_ROTATION_PRODUCT_SPEC.md` and the older Kompas Minimal contract before extending components.

Release progression: **RECOVERY → SOURCE_FREEZE → COMPONENT_PORT → DATA_ADAPTER → B+PROOF+KOMPAS+PATH → MULTIVIEWPORT_DIFF → NATIVE_SAFARI → REVIEW/CI → EXPLICIT_RELEASE_DECISION → CDN_READBACK.**

AppDeploy is exclusively DESIGN AND TEST; GitHub is version control; Pages remains one canonical public site. Port actual source components rather than layering more overrides on the wrong frontend. Tests must reject demo sine wave or post-hoc blue price interpolation, mismatched CN issue, stale/retracted records, fake historical precision and source masks.

No new GitHub Actions workflows, paid design packages, external API keys, backend, scheduler, DB or additional supervisor are authorized in this lane. The existing October 2026 GitHub Actions minutes constraints remain binding.

**Never mistake files written to this isolated folder, a Draft PR, or a passing syntax test for a visually approved live website.**
