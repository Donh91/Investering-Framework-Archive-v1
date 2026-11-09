# Existing Research Governance -> Claude Bridge advisory feed

**Status:** proposed integration, original Research Governance `main` workflow extension only after exact-head PR merge. **Not a Claude runtime or new queue owner.**

The original daily `.github/workflows/autonomous-research-governance-loop.yml` can now run `scripts/research/build_claude_advisory_feed_v1.py` *after* the original novelty, VOI, sentinel, and meta-orchestration stages. It creates `LATEST.json` with source-locked original-owner audit candidate information, no Claude API calls, no scheduling, no new competing GitHub Actions workflow, no model/threshold/trading authority. The original governance main-writer and commit rules remain unchanged.

The feed is automatically refreshed **at the already-existing daily governance cadence** only after a qualified merge and real workflow readback. It is NOT a promised hourly Claude execution; Claude's own approved external scheduled client must read it and independently substantiate every candidate before a submitted review.

- Canonical source: `meta_orchestrator_v1/STATE.json`, one current original-selected action + SHA256; `05_CYCLE_NAVIGATOR/internal_learning/STATE.json`, original four-settlement weak families; `compounding_learning_v1/NEXT_BEST_EXPERIMENT.json`, current eligible scientific proposal status.
- All three source files are schema/authority checked. Missing/stale/unsafe original files fail closed, do not fabricate an empty valid research queue. Read-only `--dry-run` does not write.
- The output indicates `claude_invoked=false`, `automatic_execution=false`, `automatic_paid_dispatch=false`, `automatic_canonical_promotion=false`; may carry original `execution_proof` if present but never forges a native run.
- The Bridge intake is separate, existing private `Donh91/Investering-AI-Audit-Bridge/tasks/claude/CLAUDE_MAX_AUDIT_INTAKE_v1.json` in Bridge PR #167 at preparation. It is *not* a second priority runner; the original issue/PR/CI always supersedes stale candidate views.
- Claimed progress requires: Claude actual provider session and report -> existing Bridge receipt -> ChatGPT/S1 independent validation -> original code PR exact-head tests/review/merge/main -> natural consumer -> due-only scientific outcome and calibrated shadow change/rejection.
- S1 must not replace its hourly task, drift out of the existing read-only window, or treat `LATEST.json` as a command. It may read the feed as a *hint* when otherwise eligible under its original supervisor contract, provided client activation is verified.
- Privacy: only public-safe original owner references, aggregate 4-week weakness, source SHA256. No wallet, raw private labels, credentials or Vault recovery tokens.

**Test:** existing `tests/research/test_claude_advisory_feed_v1.py` validates source fingerprint/authority, zero dispatch, missing source fail-closed, dishonest primary, semantic fingerprint stability, no implicit action receipt. Existing governance CI gate and daily governance workflow run the tests, no additional workflow or recurring task.

**Known limitation:** This read-only feed does not yet *execute* the `RECOVER_EVALUATOR` original action. That gap remains with original #1157 / S1 #1156 and Code PR #2057. Claude should falsify and design the minimum executable original-owner repair. Do not claim end-to-end learning until actual prospective outcome and scientifically admitted calibration are evidenced.
