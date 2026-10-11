# Cycle Navigator vNext — Product Redesign and Public Proof Handover

Date: 2026-10-11. Status: DESIGN/PROTOTYPE ONLY; no automatic production deployment.
Parent authority: site/SITE_CONTRACT.md, site/DESIGN.md, visual-motion-design/SKILL.md.
Companion repository: https://github.com/Donh91/CycleNavigator-scores (public proof publication only).

## Product outcome

Cycle Navigator must be **radically simpler without removing evidence**: a visitor on a 390px iPhone must see the prevailing market direction, supported next confirmation, current Official Compass action and historical proof, without scrolling through duplicate market-phase, rotation, risk and decision-window copies.

The existing premium site contains substantial valid information but too many competing narrative surfaces. Simplify the **information architecture and presentation, not the underlying analysis or data**. No new state engine, prognostic classifier, scoring formula, threshold or trading instruction.

## Design authority

Preserve Quiet Precision: bright editorial white/off-white backgrounds; navy #07172f; CN blue #2f6fda; restrained amber for watch and red for documented risk; excellent typographic hierarchy, limited shadows, a consistent compass identity. Add nuanced SVG diagrams, financial visualization and deterministic micro-interactions only if explanatory. Existing production motion code is an asset, not a mandate to add spectacle. Reference bookmarks at DESIGN_MOTION_REFERENCE_LIBRARY.md.

## New information architecture: 3 primary destinations

### 1. OVERBLIK (Home; primary)

Hero top mobile viewport:
- timestamp and data-quality pill;
- **ONE** source-backed overall market direction and cycle-position headline, with explicit time horizon and "official weekly" attribution;
- a concise visible "My assessment" style summary grounded in the official public structured state, not an uncontrolled browser LLM;
- **NOW ACTION:** today's verified Official Compass posture, with current tactical horizon;
- **NEXT GATE:** one confirmation threshold/condition from typed official source, or "not established";
- **RISK WATCH:** pullback/distribution risk + separate SELL assessment and re-entry permission, with independently labelled statuses and timestamps.

Below first viewport, the *best part* of current CN:
- one elegant market PATH showing source-owned current checkpoint, next sequential checkpoint and subsequent roadmap; source-supported conditional ETA only;
- one compact BTC/ETH/large/mid/small/micro/meme transmission strip, clearly separating HOLD from ACTIVE/BUY;
- one clean mini forecast-vs-actual chart (price data and observation cutoff labelled);
- one read-only score credibility footer linking directly to public proof repo/PROOF destination.

Remove duplicated overview, separate decision windows inside PATH, independent altseason ladder, multiple stacked rotation cards, repeated risk interpretation and unrelated internal machine terminology.

### 2. KOMPAS (looks like ChatGPT's short answer)

One screen, responsive, compact and scannable. Required core tables:
A. "Mit taktiske Kompas" columns **Tid | Retning | Handling**; horizon rows 0–12h/24h, 1–3d, 5–7d, 2–3w, 4–8w as available. Do not infer missing horizons.
B. "Aktivklasser" columns **Aktiv | Status | Handling**; BTC, ETH, large, mid, small, micro and memes. Micro does not stand in for memes.

Below tables:
- "Min fortolkning — [horizon]" concise narrative, direction, likely path, confirmation / invalidation, no false precision;
- one expandable price-range detail, forecast timeline and risk clarification;
- separate "SELL / Swing" analysis section (not a market action inferred from pullback alone);
- "Evidence and health" disclosure explaining Official Compass live vs weekly CN frozen vs research-only Shadow;
- sell, trim and reentry remain unavailable unless explicitly source-permitted.

Do NOT copy chat-only arbitrary AI opinions into the public website. The narrative is an allowed deterministic/human-reviewed projection of typed official public data; if unavailable show exact status and source rather than fabricate. Chat no-widgets preference does not prohibit usable interactive site design.

### 3. DOKUMENTATION (Proof, methodology, archive)

- One latest completed **public** price-range score, with CN number and forecast week (not machine issue number).
- Distinct historic market/structure legacy section CN1–26; no market-structure percentage CN27 onward.
- Distinct frozen-claim precision audit and coverage; never an "overall CN accuracy" amalgam.
- Score chart by week and scoring-era tags; no fake continuity across measurement changes.
- Single week detail: original frozen forecast / source timestamp -> immutable receipt -> matched realized BTC/ETH observations -> exact scoring method -> independent verifier.
- AI-friendly "verify this score" link to the new public repo, machine-readable manifest and independent verification result. Show LEGACY_ATTESTED and PROVISIONAL clearly.
- Full technical audit/learning history in disclosures, not the home page.

## Common visible UX rules

- Every live signal needs fresh timestamp + owner + horizon.
- Every frozen signal needs public CN number + forecast week; live disagreements shown as "weekly baseline vs current reading", never blended.
- Every score is tied to explicit method and coverage. No unattributed percentages, no "accuracy" claim on structural score.
- DEGRADED / STALE / ABSENT states remain conspicuous; fail closed on mismatched Compass-to-CN lineage.
- No client-side countdown, interpolated forecast path or ETA from elapsed time.
- No paid library or unnecessarily heavy bundle; iPhone Safari 390x844 and 430x932 first.
- Touch targets, no horizontal overflow, sensible reduced-motion; keyboard/VoiceOver test.
- Danish and English labels through current source-agnostic translation flow, not duplicated logic.
- Privacy: don't expose repo username, wallet, secrets or raw internal source paths on the site.

## Known compatibility / governance issues to protect

- SITE_CONTRACT PATH v3 already retired duplicate decision windows and separate altseason ladders. Redesign should IMPLEMENT those simplifications rather than restore old v2 ideas.
- Official Compass is action owner; CN is weekly frozen state; Master Monday provides weekly evidence; public scores repo is publication/verification mirror.
- Existing historical CN public issue number can differ from migration-era machine issue; rely on public_series identity plus week and frozen source.
- Preserve verified frozen numeric ranges, their null/unavailable states, observation coverage and timestamp.
- Site readout must use existing typed Risk Protection Tracker, separate Sell Assessment and Re-entry status: a pullback warning is NOT authority to sell.
- The currently active Compass Horizon Edge research PR #1573 can inform later presentation after research admission; don't bake unproven forecast edge into vNext.

## Publication architecture and minimal migration

1. Add a read-only, allowlist-based exporter to existing **weekly CN forecast freeze owner**. Export prospectively before relevant measurement window starts, using exact-byte source SHA-256 and frozen public-series tuple.
2. Hook completion-only score export to the existing **public score materializer owner**; never create a second score engine or schedule.
3. Publish externally as new versioned releases in CycleNavigator-scores with immutable release+attestation+independent timestamp; verify within release job with fixture for after-the-fact attempt, wrong week join, tampered digest, incomplete actuals, NULL-method era and privacy leak.
4. Backfill legacy scorecards as historical/legacy with known timestamps; no retroactive proof claim.
5. Site PROOF links to immutable records and reports the verification state; site never decides or recomputes the score.
6. Site/Pages deploy remains independent of scoring repo availability. On failure, keep last verified score with STALE/PROVISIONAL label or display unavailable; don't disable Compass/site.

## Visual prototype acceptance

- Provide an isolated preview implementation, side-by-side iPhone screenshots of original and proposal and accessibility/reduced-motion checks.
- One clearly written critical market story per viewport. Avoid generic dashboard card spam or artificial motion.
- User can answer in under 10 seconds: What direction? What action? What time? What invalidates? Can I verify historical claim?
- Test no loss of content: map every existing NOW/PATH/WHY/Scoreboard/PROOF block to a new home, expandable detail, archive or justified removal; no deletion of underlying records.
- Test financial invariants (immutable forecast, source precedence, stale/offline cases, no unsupported ETA or SELL, historic score method separation).
- No production merge until original releases, QA, screenshot approval, authoritatively refreshed state and rollback verified.

## Delivery slices

A. Design reference library and this product spec, no production change.
B. Isolated polished mobile prototype and before/after screenshots.
C. Scores repo integrity protocol, schemas, dry-run tamper tests and guarded first prospective release.
D. Bounded CN exporter/consumer PRs with correct source owners, scored independent verification and audit.
E. Production-ready vNext branch, CI, full visual regression test and gated deployment.

No additional autonomous supervisor or recurring automation necessary; use existing owner/review and scheduling lanes.

## Definition of done

New CN site is simpler and materially more polished, works beautifully on actual iPhone, preserves ALL audited market/score semantics, connects Compass/pullback/direction, and displays verifiable proof evidence without using X as the verification dependency. A separate clean README of progress must distinguish DESIGN, IMPLEMENTED, VERIFIED and DEPLOYED.
