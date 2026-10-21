# Historical and current Alpha Lab research: deduplication, dormant-work recovery, preflight

**Audit date:** 2026-10-18  
**State:** SOURCE-ANCHORED ARCHIVAL SAMPLE / REUSE PRIORITIZED / NO LIVE PROMOTION  
**Machine inventory:** `ARCHIVE_OVERLAP_MATRIX_2026-10-18.json` (24 distinct source entries, H1–H7 overlap joins).  
**Existing authorities:** Archive [#1512](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1512), Meme Alpha Lab [#126](https://github.com/Donh91/Meme-Alpha-Lab/issues/126) / [#88](https://github.com/Donh91/Meme-Alpha-Lab/issues/88) / [#120](https://github.com/Donh91/Meme-Alpha-Lab/issues/120) / [#124](https://github.com/Donh91/Meme-Alpha-Lab/issues/124), Archive [#1087](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1087) and [#1340](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1340).  
**No new owners, jobs, scanners, provider spend, scored market data, framework trading authority or changes to original frozen experiments.**

## Key finding: we have a recovery-and-admission problem before an ideas problem

A 2026-10-18 indexed GitHub audit and direct file reads found **24 existing source artifacts / operational owners** overlapping the newly proposed premium specialist REA. This is a **bounded inventory, not an exhaustive claim that all historical branches, deleted files, archived chats, restricted evidence or legacy repositories were inspected**. It includes historical source files and branch/default-main code, publicly safe issue metadata, and *metadata only* for the Bridge private historical reports. Paths and source status are itemized in the machine matrix.

The active Meme Alpha Lab Research Genome `research/genome/METHOD_REGISTRY_V1.json` holds **40 named methods**. Its `ADAPTER_GAPS_V1.jsonl` holds **14 recorded adapter gaps** with mixed states: some implemented or partly evidenced; others not resolved. `METHOD_PERFORMANCE_V1.csv` has only **7 populated rows**, several with 70 runs but zero reported useful findings. **This does not prove zero actual alpha or failed production**: coverage is incomplete and the ledger may not be joined to all outcomes. It supports a narrow **P0 evidence/accountability question**: which registered methods really run, receive complete inputs, yield useful reproducible findings and become forward tests?

The existing Archive `scripts/research/research_memory_novelty_gate.py` is legitimate but **not an archive-wide duplicate detector**: `_prior_records()` reads its novelty ledger, machine verdicts under `06_RESEARCH_LAB`, and shadow sensor registry. In `classify()`, the near-duplicate matcher filters to `record_type == NOVELTY_LEDGER`; even other loaded sensor/verdicts are not compared there. It does not traverse the MAL method registry, Genome adapter gaps, decades of archived Markdown, nor private/manual Bridge reports. Therefore an old experiment can be mislabelled 'NOVEL' **in principle**. No on-run incorrect verdict is claimed. Its policy explicitly states historical archives are context, not grounds for automatic suppression; **retain this invariant**.

## Important existing work rediscovered — use rather than rebuild

| Research candidate / new premium inspiration | Existing old/new source and verified archive state | Disposition |
| --- | --- | --- |
| **Nansen smart wallets** | Archive `04_RESEARCH_LAB/auto_trading/NANSEN_ALPHA_LAB_ABLATION_V1.md` **2026-09-11 RESEARCH_QUEUED**. Already defines four arms baseline/free/Nansen augmented/Nansen only, budget and PIT control. Also MAL conditional wallet intelligence v1 **ACTIVE_OPEN_RESEARCH/SHADOW_ONLY**. | **DEFER NEW NANSEN PILOT**. First retrieve the old 4-arm plan and inspect existing receipts; open only the missing work under existing S2. |
| **Old Nansen/insider research in private Bridge** | `Donh91/Investering-AI-Audit-Bridge` two **SUBMITTED** September 29 Claude reports (`reports/claude/2026-09-29T200500Z_CLAUDE_NANSEN_ALPHA_SCAN_RESEARCH.md`, `...T201500Z_CLAUDE_INSIDER_NETWORK_SCAN_RESEARCH.md`). Bridge AGENTS.md **PAUSED / MANUAL_ONLY** from October 10. | **MANUAL_ADJUDICATION** under S2/S3 before any new call. Reports are unapproved and include data/missingness limitations. Do not copy their data tables into public Archive or awaken autonomous Bridge client. |
| **CrawlScan launch/early buyers** | MAL source audit and challenger already in main; 12/12 public transports; 3/12 scores; first two dated T0 freezes 2026-10-08 retained. MAL [#124](https://github.com/Donh91/Meme-Alpha-Lab/issues/124) says independent B1 and exact outcome coverage absent; [#120](https://github.com/Donh91/Meme-Alpha-Lab/issues/120) owns Pons delayed census. | **DO NOT RESTART PILOT**. Repair existing **B1 T0 independent baseline and outcome-ready coverage** and census before collecting 20–50 more unscoreable samples. Keep OPA/OFY as research controls not live predictions. |
| **Bubblemaps-style original/current entity graph** | MAL `scripts/forensics_relationship_resolver_v1.py` and Archive S3; prior `2026-10-01__conviction-cluster-detected-v0-preregistered-shadow.md`, plus conditional wallet program. Raw historical graph membership still partly blocked by independent source history. | **EXTEND S3** with `launch_origin` vs `current_exit` views of the SAME frozen source evidence, not a new cluster engine or “insider” score. |
| **Early launch and sniper bundling** | MAL `scripts/launch_execution_order_v1.py`, Archive 2026-09-27 Solana Moonshot method transfer, Sep/Oct adversarial operator research; S9. | **REUSE** tx-index/block/nonce grouping. Same block is not common control; preserve protocol-infrastructure exclusions. |
| **Solana bot-fingerprint and reusable operator patterns** | Archive `06_RESEARCH_LAB/alpha_lab/2026-10-02__zero-cost-solana-bot-fingerprint-alpha-extraction-v1__shadow.md` and [#1438](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1438), with public paper + replication references; archived v1 fingerprint hypotheses. | **PRIOR ART / NO NEW BOT IDENTIFIER**. Only an independent funding/control/recipient edge may support entity lineage; behavior similarity alone cannot prove owner. |
| **Wallet convergence and pre-KOL** | Archive `conviction-cluster-detected-v0-preregistered-shadow`, `wallet-precursor-execution-fidelity-prospective-experiment-v1__prereg.md`; MAL [#88](https://github.com/Donh91/Meme-Alpha-Lab/issues/88), MAL `research/fieldwork/ALPHA_PRE_KOL_RESEARCH_2026_10_15_V1.md`. | **REUSE OLD PREREGISTRATIONS**; do not create different thresholds/cherry-picked samples. Verify source/cutoff truth and negative denominator. |
| **Rick-style quickscan/CA cards + public visibility** | Archive `07_PROMPTS_AND_AGENTS/memes_alpha/2026-09-17__rick-bot-feature-extraction-alpha-lab-v1__research.md` and Archive #1087; visibility and first-seen plan already written. | **EXISTING UX OWNER ONLY**. No parallel report or independent public-visibility truth source; new askr design is a comparable product pattern. |
| **Phoenix / post-hype second-wave** | Archive 2026-09-23 `phoenix-post-hype-second-leg-challenger-v1.md` marked **PREREGISTERED**. Already includes retained demand, liquidity survival, re-entry and drawdown. | **DORMANT CHALLENGER**. Do not create a new phoenix/re-entry scanner from the same idea; examine baseline and existing forward rows first. |
| **UNIPCS and raw skill leaderboard** | MAL `research/benchmarks/UNIPCS_RESEARCH_PLAN.md`; Archive Nansen ablation; MAL #88 and 12-wallet cohort. | **EXISTING BENCHMARK**. Require all losers and realized-sell notional, no screenshots/retrospective win-rate promotion. |
| **Research Genome methods that resemble new ideas** | MAL `research/genome/METHOD_REGISTRY_V1.json`: `EARLY_BUYER_RETENTION`, `HOLDER_COHORT_SURVIVAL`, `FUNDING_ANCESTRY`, `WALLET_PORTFOLIO_REPLAY`, `KOL_RELIABILITY_LEDGER`, `ORGANIC_VS_PURCHASED_ATTENTION`, `EXIT_QUALITY_REPLAY`, `FEATURE_ABLATION`, `SOURCE_DRIFT_DETECTOR`, `METHOD_PERFORMANCE_AUDIT`. | **REUSE METHOD IDs AND STATES**, no duplicate method rows. 'Registered' does not mean data adapter works; check `ADAPTER_GAPS_V1.jsonl` first. |
| **GoPlus / Honeypot sellability and old prototypes** | S1 `S1_EXECUTABLE_SELLABILITY_TRUTH_V1.md`, past `research/api_agent/meme_alpha/experiments/red_sellability_aware_outcomes_v1.py`, MAL #98 and Genome gap `EVM_NEGATIVE_SELLABILITY_PROOF_V1` marked missing negative-route adapter. | **DO NOT BUILD ANOTHER SELLABILITY ORACLE**; continue existing S1 until independent no-route/revert data and fixed-notional reproducibility are proven. |
| **DexPaprika / market QA** | Merged Archive PR #1668, existing source QA research/adapter candidate, plus Archive #1017 source-field-map prerequisites. | **NO SECOND DATA ADAPTER**; exact chain/CA/pool/time; 'unknown ≠ zero'; future admission owner remains unchanged. |
| **Broader premium stacks** | MAL `research/discovery/USER_TOOLING_SCAN_TOP10_2026-10-05.md` already groups wallet, onchain, social, unlock, fundamentals and memory services. Canonical Archive 10-lane QUEUE owns ranking. | **SOURCE SHORTLIST, NOT VENDOR INSTALL LIST**; keep only narrower information improvements. |

## New design contribution after overlap: NOT a new method, an admission discipline

### Preflight before EVERY future vendor/REA promotion (in existing execution owner)

1. **Canonical owner lookup:** `AGENTS.md`, #1512 QUEUE, S1–S10, #126, #88, #1087 and existing exact issue. Stop if identical ongoing research already has an owner.
2. **Current-code fingerprint:** search MAL and Archive for existing scripts, tests, method IDs, actual merge/PR/CI and source contracts. Source `main` code or a merged PR ≠ active runtime or positive experiment.
3. **Historical trail:** search dated `06_RESEARCH_LAB/alpha_lab/`, `07_PROMPTS_AND_AGENTS/memes_alpha/`, `04_RESEARCH_LAB/auto_trading/`, archived research experiments and old PRs/comments; optionally Bridge submitted historical reports **only on explicit owner request** under manual-only policy. Do not silently drop old negative findings.
4. **Genome adapter reality:** compare all **40 registered methods**, **14 gap records** and performance ledger before proposing a new collector/method. If adapter partial, fix data/coverage first.
5. **Map to one of:** `EXACT_OVERLAP`, `PARTIAL_IMPLEMENTATION`, `ARCHIVED_NOT_EXECUTED`, `SUPERSEDED`, `CANCELED_OR_NEGATIVE`, `NOVEL_INCREMENTAL_PRIMITIVE`, `EVIDENCE_INSUFFICIENT`. Each classification cites the exact old path and current owner; **not** an automatic archive-veto.
6. **Marginal-information proof:** explain what the new proposal adds beyond baseline, 1–2 falsifiers, source/knowledge cutoffs, negative control, feasible cost and a measurable consumer. Where there is no new owner-grade data, choose **REUSE/NO_OP** rather than duplicate code.
7. **Research result and disposition:** append to existing owner issue and master #1512; no separate queue, cron, paid model, proxy authority or subscriber. Route Strategist ONLY through current admitted owner receipts. If non-admissible, archive method notes as `METHOD_ONLY` with no execution mandate.

### Specific likely engineering delta for a future owner-reviewed PR

A **read-only, optionally invoked** archival overlap preflight could augment the *existing* `research_memory_novelty_gate.py` with an explicit, bounded reference index and a separate `ARCHIVE_OVERLAP_REVIEW_REQUIRED` state. It must **not** automatically classify archived text as definitive duplicate or block a novel line from weak semantic similarity; `POLICY.json` already says historical archives are context, not automatic suppression.

First test fixtures:
- proposing a “new” Nansen Alpha Lab experiment finds 2026-09-11 4-arm ablation and private Bridge historical report metadata;
- proposing a new CrawlScan scanner finds MAL #124 B1 blocker, T0 freeze and zero qualified C3-vs-B1;
- proposing a new early-buyer retention method finds existing Genome method ID plus Pons receipt;
- proposing a new wallet bot-fingerprint engine finds Archive #1438 and avoids false identity inference;
- an actually novel first-party source transform with distinct provenance remains `REVIEW_NEW_PRIMITIVE`, never incorrectly auto-rejected;
- restricted-plane data remains inaccessible to public code; unresolved source returns UNKNOWN, not fabricated "no overlap".

**Engineering does NOT run yet.** It requires current owner code review, exact-head independent review, CI and no expanding the current scheduled/agent architecture.

## Routing H1–H7 without duplicate work

- **H1 origin-risk persistence:** O05/O06/O07/O09/O11/O13/O22. Existing S3/S4 / MAL #88, #126. **Reuse**.
- **H2 early-buyer independence:** O03/O04/O05/O09/O10/O14/O15. Existing S2/S4 / MAL #124; fix independent T0 B1 and history completeness.
- **H3 provider disagreement:** O03/O04/O17/O18/O20. Existing X0 and Source QA. Method candidate only when paired source flags exist.
- **H4 executable sellability:** O10/O15/O18/O23. Existing S1; negative proof blocked. No new simulator.
- **H5 social vs wallet flow:** O10/O11/O13/O14/O15. Existing S7 and KOL chronology; social first-publication knowledge time mandatory.
- **H6 operator distribution illusion:** O05/O06/O07/O08/O09. Existing S3/S6; do not assume all recipient addresses are sybils.
- **H7 mutable contract exit paths:** O18/O23. Existing S1 (proposed Slither/Echidna/trace method). New methodology, existing owner, no install before legal/cost/test review.

## Stop/routing decisions at this audit cutoff

- **Do now (research review):** prioritize existing MAL #120/#124 census and independent baseline, S1's missing negative route proof, S3's raw historical membership provenance, S2's wallet history/realized-exit completeness.
- **Archive-and-reactivate only with new evidence:** old Nansen four-arm design, privately submitted Claude report, bot fingerprints, Phoenix challenger, UNIPCS, old Rick cards and conviction-cluster metrics.
- **Do not start:** second memory/novelty engine; new Nansen subscriber; new live CrawlScan run before usable B1; second sellability engine; generic 'smart money' weighted-score model; premium contract-risk score as native truth; auto-buy or autonomous trading.
- **Existing Strategist:** receive no more than three bounded evidence-linked questions: (1) does a real origin-vs-current entity discrepancy survive controls, (2) is S1 no-route evidence measurable yet, (3) what Genome method actually has input+outcome trace versus 70 no-yield ticks? Its task is prioritization only.
- **Existing Supervisor:** evaluate PREEXISTING first, then source quality, then implementation marginal value. Keep first eligible forward Pons buyer cohort as queue's current next action. Respect one-heavy-lane rule and all earlier research freezes.

## Verification boundaries

Confirmed by connected GitHub **direct file reads** on 2026-10-18:
- Archive old Nansen AB, Solana fingerprint, conditional wallets, convictions, pre-KOL, Rick, Phoenix, sellability and governance novelty script.
- Meme Alpha Genome method registry, adapter gap log, performance ledger, forensics code, launch order code, CrawlScan prospective freeze/known blockers, and user tooling top-ten prior.
- Bridge AGENTS.md status **PAUSED/MANUAL_ONLY** and *historical report metadata* on owner-requested archive overlap, without copying private/raw data values into this public package.

**Not confirmed:** exhaustive repository or deleted-history coverage; private raw dataset truth/admissibility; current GitHub Actions run-to-method joins; actual live full-denominator coverage; real prospective precision/recall uplift; completeness of every historical Claude/Nansen query; or independent merge approval.

The follow-up question for Supervisor is not "which new tool should we install?". It is **"which formerly started piece of research can we complete most cheaply, reproducibly and without hindsight by reusing existing code and restoring missing evidence?"**.
