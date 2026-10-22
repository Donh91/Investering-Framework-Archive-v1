# 12 | Execution architecture: R0–R7, lanes, dependencies and bounded Codex packets
**Status:** proposed execution after separate owner approval. **Read master:** [11](11_EXTREME_WORK_MISSION_MASTER.md). All existing owners and frozen contracts override this planning packet.

## Overall operating model: one coordinator, many small proofs
**Work** takes responsibility for cross-domain source reconciliation, method, prioritization, independent challenge coordination, execution receipts and closure. **Codex** is Work's PRIMARY technical implementation, adversarial regression-test and source review partner, subject to actual available usage and current release authority. Codex is not a separate research decision owner. If Codex code-review quota is temporarily unavailable, label BLOCKED_REVIEW_QUOTA and preserve the correct review gate, never fabricate a pass or exhaust Work on repeated identical review requests. **GitHub connector / local deterministic scripts** perform cheaper scoped inspections. **Research Lab** tries to falsify claims but does not become a new upstream signal source. **#1596** owns Task 2 scientific outcome; **#1156** owns PR reliability, closure and escalation; **#1530/#1553** own EDGE/risk/action; **Alpha Lab**, **Situation Room** and **CN/Kompas** preserve their current authorities. Do not create parallel agents, tasks, scheduled jobs, model routers, workflows or registries.

### First ten evidence gates on an approved Work run, ordered by dependencies rather than clock
1. Freeze current main SHA; AGENTS, cross-repo boundary, authority/health/cost and registry; classify public/restricted.
2. Enumerate ALL open PRs using live GitHub, exact head hashes, changed files, freshness, and reviews; identify who owns each. The v1.0 snapshot listed six, but the later v1.1 audit found only #1747 and #1733 OPEN; #1746/#1748/#1736/#1732 were CLOSED. **CLOSED does not mean MERGED or healthy**, and neither count remains current without a new read.
3. Reconcile which older Task 2 PRs (#1573, #1597, #1617, #1627, #1644, #1675 and #1740/#1743/#1744/#1745) are genuinely merged/closed and whether current main reflects the intended fix. Do not double-repair a merged file.
4. FIRST classify #1746 and #1748 as MERGED/CLOSED_UNMERGED/SUPERSEDED/UNKNOWN. If merged, check exact main objects and original negative tests plus natural monitor/consumer readback. Only if a defect survives should Work assign a bounded Codex remediation. Closed PR != implemented fix, but don't re-implement proven code.
5. Read #1747 as a *Draft research package*, never assume a citation or dataset card passes T1. The extra files 11–15 in this same PR are planning only. Do not merge all HF research because of urgency of other P0 Task 2 PRs.
6. Establish Task2 evidence scoreboard from **original** archive, private authority (only if authorized), actual verified source/issue/outcome clocks, complete attempt denominator and publication lineage, with zero reconstruction of original missing fields.
7. Identify cheapest **one** cohort whose actual admission can be tested without recursive source hunting, and **one** clear falsifier whose outcome can be independently computed.
8. Run local deterministic source QA tests and ledger/original-sha verification before model analysis. Record exact commands and test counts, including failing fixtures.
9. If R1 is still empty, do source rescue work only. Do not call a baseline `R2` or GPU fit without R1.
10. Assess and report public-safe status with before/after row counts, independent events, statuses and proof pointers. Continue down R stages only through satisfied gates.

## Work + Codex operating agreement, revision 1.2
**Capacity fact:** owner reports **96% of Work/Codex usage remaining** after reset. This is owner-reported, not independently read by this connector. Treat Work and Codex as a coordinated resource pool; record observed product capacity or `UNVERIFIED`. Do not treat a previously failed Codex code-review quota as proof that all Codex execution is unavailable now.

**Explicit division of labor**
- Work: scientific owner crosswalk, original-file evidence access, prioritization, trial definition, source provenance, checkpoint quality, private/public handling, technical review orchestration, authorized integration, decision-value conclusion and final receipts.
- Codex: technical change design and implementation on isolated PR branches, targeted source parser/clock guards, source-manifest pinning and negative tests, runnable reproducibility scripts and deterministic comparison harnesses, *plus adversarial independent code review when actual usable review capacity exists*.
- Work is accountable for reviewing Codex results rather than copying its status claims. Codex output needs exact source SHA, test command and fresh PR review. A model in another session is an advisory independent critique, not formal GitHub APPROVED.

**Make the large Work run productive, not a microtask loop**
Run one coherent Work mission across the following **value waves**. Work should maintain a finite *decision backlog* of at most three active packages: (A) highest severity source/clock integrity gap, (B) one science original-cohort admission, (C) one directly useful HF source pilot. Codex can implement the independent package A while Work researches B and prepares C; Work integrates evidence before moving down R3–R7. Do not spawn 15 disconnected Codex tasks simply because they are listed in the mission.
- Wave 0, reconnaissance: current main and close/merge truth, usage, current owners, exact blocked scientific gate. Output current truth table and exact head hash.
- Wave 1, repair & trust: if a true P0 remains, Codex produces failing fixture and minimal repair while Work verifies original evidence and source semantics. If all P0 repaired, skip immediately.
- Wave 2, first R1 scientific admission: Work binds one original issuable set and complete denominator. Codex audits/implements *only reproducible missing validator or deterministic replay*, no hindsight original issue reconstruction.
- Wave 3, selected HF source proof: Work chooses single pinned small actual file and rights; Codex runs small immutable revision/source QA where permitted, including wrong clock and mutation traps. No GPU, no massive downloads.
- Wave 4, first R2/R3 economic and information challenge: ONLY when true R1 admissible original and prereg exist; compare to zero/persistence/price-only, missingness, issuer delay and holder vs cash where evidence allows. Codex builds reproducible baseline code; Work independently verifies outputs and negative result interpretation.
- Wave 5, frontier: allocate remaining usable capacity to highest-yield permitted R4–R7/Alpha/News source or model *only when a clearly observed gap persists*. Do not pretend prospective observations have matured. Close duplicates and produce durable stage scorecard.

**Codex dispatch modality is conditional, not assumed.** If the Work session can use the user's authorized Codex workflow directly, Work may dispatch bounded packets there within the approved plan. If Work cannot actually invoke Codex in the connected host, Work must instead prepare exact-head code/test task packets in the existing Codex intake or PR, then the owner can run Codex in the separately authorized Codex context. No imaginary direct Work-to-Codex delegation and no claims of Codex completion based only on a prepared packet. Work may independently continue valuable R0/R1 source research while the Codex handoff is pending, without disguising the missing executor.

**Every Codex deliverable**: reproducible evidence packet, frozen baseline/head and expected failure, exact allowed file list, minimal diff, tests that fail when guard removed, reviewer feedback, status of real CI, cost/usage and merge+consumer provenance if authorized. Do not launch a Codex task if no executable defect or verifiable output.

**Capacity guidance, not a commitment:** reserve most of the available effort for actual research and code, not speculative reviews. Aim conceptually ~35% original R0/R1 custody and research, ~25% Codex implementation/test hardening, ~15% genuine admitted R2/R3 comparisons, ~10% HF source custody and model/source screening, ~10% review/integration/readback and ~5% uncertainty reserve. These are **planning shares, not live quotas or expected usage**; adapt after Wave 1 according to the next actual scientific blocker and verified credits. A high-impact R1 unlock can justify reallocating major capacity away from model exploration.

**Stop and redirect:** if the next activity cannot yield a new admissible row, independent baseline, reproducible bug/fix, explicit justified rejection or resolved consumer readback, don't burn usage on it. Maximum two attempts on unchanged head/fingerprint without new material evidence. Follow approvals, spend caps and current AGENTS every time.

## Scientific decision tree
```text
CURRENT MAIN/PR TRUTH VERIFIED?
  no -> resolve source/authority; stop code changes until truthful
  yes -> ORIGINAL ISSUED FORECAST/AVAILABLE SOURCE CERTIFIABLE?
    no -> reproducible R1 gap ledger; repair only actual source custody flaw
    yes -> REAL ADMITTED R1 COHORT?
      no -> admit original attempts or explain precise scientific blocker
      yes -> preregister matched cheap baseline; run R2 without tuning on outcome
        -> only genuine first-actionability + fill lets R3 claim action edge
HF PARALLEL: pinned small file + rights + true clock + real owner value?
  no -> SOURCE_ONLY/REJECT
  yes -> T1 FILE QA; T2/T3 gated separately
```

### Lane R0 | Truth acquisition, environment & replay integrity
**Falsifier:** original forecast or source lineage cannot be bound to the advertised immutable object/time. Build source roster by asset/horizon/engine version/collector/source cadence, Git SHA, source provenance and original issue. Verify source vs code effective dates and output mirrors. Explicitly identify 2026-07-08 CFGI algorithm-era break, newer scorer version shifts, old PDF example paths, and false Git author timestamp inference.
**Tests:** deleted source, wrong tree, moving main, stale git object, duplicate ID, future clock, fake ancestry, original source wrong SHA.
**Output:** `R0_SOURCE_AUTHORITY_AND_GAP_MATRIX`; canonical original inventory **not** blanket provider PIT admission.
**Kill:** absence of immutable original authority for a claimed historic path -> NOT_IDENTIFIABLE, not filled by external HF.
**Codex if needed:** only a reproducible bounded original-source validator bug with a failing fixture, pass through existing intake.

### Lane R1 | True time of knowledge and complete denominators
Frozen original `source_first_known_at`, `source_observed_at`, `collector_available_at`, `original_forecast_issued_at`, `delivered_at` and `outcome_due_at` separately, with provider clock certainty and version. For each original eligible attempt include censored, absent, abstain, rejected, no-issue/neutral and invalid. A fresh verification timestamp is not a fresh market print (#1748), and source row labels without original SHA are not tournament evidence (#1746).
**Tests:** earlier historical prices re-uploaded today; candle closes after prediction; release vintage retroactively revised; ETH/BTC joins at mismatched clock; later consumer receipt used as early source; symbol migration/delist; missing underlying original document; no-signal dropped from denominator.
**Output:** `R1_ADMISSION_LEDGER`, per-family admitted/blocked counts and reasons, independent original family grouping. Original 11 native-v3/0 admitted checkpoint from Oct15 is not a ceiling nor a verified current admission count.
**Kill:** no independently confirmable first-known or genuine original issue -> no scientific score claim.

### Lane R2 | Information advantage beyond cheap models
Prerequisite: **positive, verified subset of R1 admitted original issue rows**, and frozen target/issuer/source version. Experimental arms: original framework as-issued; naive price-last sign; previous market packet delta; zero change/abstain; sign persistence; simple ATR/vol bands; one-family vs all-families ablations; delayed-one-bar negative control; scrambled within independent event blocks as placebo; do not select controls post hoc. Balance BTC/ETH, Official vs Shadow, 1H/4H/12H/24H/72H/168H and 7d/14d/21d only when exact versions and clocks permit.
**Outcomes:** log loss/Brier for authentic issued probabilities only, balanced accuracy and directional confusion, interval coverage+width and proper interval score, breaches, abstention/coverage and selective risk, cluster-adjusted uncertainty. Deflate empirical wins for multiple comparisons and correlated horizons.
**Output:** executable pinned recipe, `R2_ORIGINAL_VS_CHEAP_BASELINE` and honest null/inconclusive result.
**Kill:** no incremental value over same-clock cheap baseline in genuinely eligible holdout or unstable regime / low N -> do not promote.

### Lane R3 | Highest economic value: distribution / tsunami / reentry
Keep existing Round2 negative study (46 anchors / 45 controls, 11 reload strategies 0 beating HOLD) intact. Keep the frozen 20 R4P adverse cases and 144 synthetic variants as stress mechanics, **not historical observations**. Reconstruct every *actionable* original warning and corresponding NO_WARNING exposure; distinguish the information warning from first user visibility and actual executable opportunity.
**Separate investor states:** already-held BTC/ETH or microcap vs new unallocated cash; watch/hold/trim/sell/defensive/rebuy counterfactuals only where existing policy and data permit. Model next feasible fill, spreads, slippage, fees, partial fills, liquidity drought, reentry delay, taxes only if owner has permitted reliable basis, and missed upside in V-rebounds.
**Metrics:** first warning lead and survival, missed crashes, false-alarm rate/hour, max drawdown avoided, net wealth delta vs HOLD and WAIT, realized risk adjusted returns, wrong early sale cost, regret distribution, fresh start costs, regime grouped results.
**Kill:** optimized after-event exits, non-delivered warning, unfillable token, no reentry discipline or worse net after-cost utility.
**Output:** `R3_HOLDER_AND_NEW_CASH_DECISION_LEDGER` with both wins and false negatives. No LIVE_EXIT_RULE.

### Lane R4 | Structural adversary and minimal sensor stack
Challenge correlation inflation between ETH/BTC, BTC.D, breadth, TVL, ETF and stablecoins. Test ETF-era default against F12/F12.5 falsifiers and genuine alternative regimes. Stability cases: ETF absorbs BTC while alts die, alt rally begins without standard ETH gate, compressed gamma regime, explosive news/ETF flush, rapid stablecoin parking, market-wide deleveraging, stale broad index, sudden economic revision. Identify whether a few shared latent factors dominate 20 named signals.
**Method:** leave-one-regime/asset/sensor-family-out, version/venue/date blocking, conditional attribution, feature-cluster bootstrap; no unreviewed causal claims from SHAP importance or narrative.
**Output:** decision-relevant compression / sensor kill table, reversible shadow candidates only.

### Lane R5 | Model and AI challenge tournament
Challenge small baseline, plain deterministic rules, existing framework and external pretrained methods on exact same admissible time split and clock. No default 'bigger is better'. Model cards may provide architectures, not proof of edge. Strict train/validation/test chronological separation, embargo, group isolation, untouched holdout, no training on later models claiming earlier efficacy; meaningful compute-vs-lift comparison. Measure cost, calibration, abstention and decision divergence. Prefer model-free source QA where actual original source is missing.
**Output:** `R5_AI_VS_SIMPLE_AFTER_COST_TRIBUNAL`; report when AI adds ZERO actionable value.

### Lane R6 | Prospective challenger and natural delivery proof
Existing owner must preregister independent forecasts, issue/delivery, source SHA, action permission, invalidators, event definitions, comparator, case censoring and scorer. **Frozen prospective floor: 2026-10-24T12:00:00Z** as current contract reported by #1746; verify fresh current owner before use. First due row is not an already matured forecast. Collect only, until eligibility and analysis gates are genuinely open; Round3 still `PROSPECTIVE_COLLECTION_ONLY`.
**Output:** valid frozen real rows; count eligible versus censored/pending separately; natural producer and consumer readback. If none: `NO_MATURED_ELIGIBLE_OUTCOMES`, not synthetic substitutes.

### Lane R7 | Formal evaluation, economics and complexity retirement
Independent red-team verifies whether improvement changes actual decisions more than it costs. Compare defensive foregone downside vs offensive missed upside, especially late rotation to mid/small/micro. Report distribution by asset, regime, issue horizon, source version, independent event family, abstention and reliability. Decide `CONTINUE / MODIFY_ONCE / HOLD / REJECT / RETIRE` for each variant, with explicit conditions and decision owner.
No thresholds/weights/gates promoted without future owner action and science release.

## Scope-specific Codex implementation packets, *conditional only*
**C1 [P0 only if defect remains] Shared Row eligibility / activation:** historical #1746 is CLOSED as of v1.1. Work must prove merge/current-main implementation and consumer truth before sending any Codex work. If failing, use original wrong SHA and owner-floor fixture, small fix, targeted regressions and natural postmerge verification. No duplicate PR without exact open defect.
**C2 [P0 only if defect remains] CMC settled MARKET PRINT stale replay:** historical #1748 is CLOSED as of v1.1. Work must verify main guard and provenance before any Codex task. If missing, original stale-print reverified-today fixture and a bounded repair; 72h is data-availability guard, not an investment threshold.
**C3 [P1] HF source manifest & pinning:** only after #1747 reviews. Expose revision SHA, file SHA, expected manifest digest, UTC coverage and zero data assumptions. A static/pure one-file QA helper only if no current owner already provides it.
**C4 [P1] Alpha HF PIT ablation repair:** existing Alpha Lab owner, source + train-only columns, late-feature availability, `resolve/main` mutation and split disjointness. Do **not** open a second Alpha workflow. Compute allowed only after license/rights and freeze gate.
**C5 [P1] Admission/scorer fail-close:** existing Task2/EDGE owner, only after an original R1 reproducible code bug is demonstrated. No semantic threshold change. Avoid queueing mere hypotheses as `CODEX_READY`.
**C6 [P2] Reproducible report/readback:** existing work owner; only necessary deterministic summary or test fixture wiring, zero new scheduled CI under October cap.

Every Codex packet records: owner, exact file paths/head SHA, frozen correct behavior, reproducer, expected failing negative test, minimal edit, no-change boundaries, max risk/cost, review requirement, postmerge source+consumer readback and fallback if Codex usage is unavailable. Existing `.agents/skills/codex-intake/SKILL.md` controls admission. **No Codex call is initiated by these documents.**

## Adaptive ordering across multiple approved Work sessions
On each run read live owner and PR state; continue the highest-utility unblocked P0/P1 and retire stale handoffs. Do not promise background continuation from this planning document. If blocked by unavailable private data, minutes, un-matured outcomes or account usage, produce a concrete proof-gap instead of idle loops. After Nov 1 check actual Actions restored and use only scoped CI, never assume reset occurs at a particular hour. Work finishes by durable evidence and explicit owner decision, not prose length.
