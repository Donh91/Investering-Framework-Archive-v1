# FRONTIER source annex — Scientific verification transfer from solved-conjectures

**Dato:** 2026-11-26  
**Status:** SHADOW_ONLY / SOURCE_NOTE / one reproduced research-code counterexample family, not production authority  
**Område:** M7 open-source method harvest / PROJECT FRONTIER  
**Primary folder:** 06_RESEARCH_LAB/m7_open_source_validation_harvest/  
**Owner:** existing #1512; scientific adjudication #1157; original S1 ROOT #2321 under #1156.  
**Depends on:** existing Research Package method; Frontier #2330 at 7fa12a704b1629ff55c3d8730e57a2a235eccc5a (draft, not merged authority). This is a source annex, not a competing generation, queue or implementation PR. Keep #2330 exact head unchanged. No new agent, scheduler, paid call, trading, scoring, source admission, production or private-data access.

## Question, source clocks and provenance

Can an independently scoped, executable claim and adversarial proof-obligation check add incremental safety beyond existing tests, without another agent/engine? Simplest baseline: current original-owner test and conformance suite. First known in this session 2026-11-26; upstream original publication dates not established. Archive main observed 9fb89fc0d65bbb5f330f09ed6f0e9f8b6a0ade70. Public upstream source: Cinna Davis and GPT-6.2 Astra, https://itsdavis.com/ and https://github.com/1337isnot1337/solved-conjectures/tree/a3303aadb9774243d8f456a258986c3889bfce36 (repository-reported attribution, not independent proof of model identity or mathematical novelty). MIT license verified at that revision, blob eba45986aaa349db6fd1c7c865c588cda9df28ce. No third-party code copied into Framework or executed.

Pinned inspected upstream files (paths relative to the above commit):
- AGENTS.md 45a638ccb6bfec1908de42d356b7a984aef44f6a — policy separates exploratory research from scoped publication, reconciles claims to issue and deployed site, checks duplicate target identity and explicit scope.
- scripts/verify_lean.sh 9ca151436d513187ae5dac9b3cea7aeffe8a7311 — explicit module registry; inspected initial section, not full execution.
- scripts/audit_lean_all_owned.py 57dfaa9d09e8f4e653b817843df7fa9826358f41 — explicit accepted closure and axiom whitelist, inspected beginning.
- scripts/replay_lean.py 06b809d9833514957a442ec983267908c96e7af6 — source import closure and replay plan, inspected beginning.
- .github/workflows/lean.yml 4bd82104d7fc4615e5828fedafd2c721d95def2d — planner failure does not skip verification; workflow source, not proof of successful run.
- .github/workflows/site.yml f96467d170d4ae40169b3c68618623212da01c3d — read-only source build, separate hosting deployment.
- scripts/check_readme_verification.py 3a107ceefcc80adcbeda8a4c0b2fdff089e0a72e — display-status syntax and duplicate slug validation; not semantic proof of theorem.
- lean/lean-toolchain a6aff065db2882c535684f8c5bcd4f16e9a23915 — Lean v4.35.0.
- Public verification docs https://github.com/1337isnot1337/solved-conjectures/blob/main/docs/verification.md read selectively (moving ref; source-reported scope only).

External evidence grade C: inspected method/code. No theorem/kernel verification independently reproduced; no market effect. No endorsement of external claims. One upstream policy accepts a specific VP vs VNP result as a standing premise; reject importing assumed authority. Any imported claim must expose assumptions, not convert a proof conditional on an axiom into an unconditional result. Workflow dependencies use version tags rather than immutable action hashes in inspected files; do not import supply-chain assumptions. Formal proofs can still formalize the wrong specification; exact statement, inputs, assumptions, dependency closure and boundary mapping need independent review. A valid proof is not empirical alpha.

## Overlap and transfer decision

Read existing Research Lab README, M7 OSS harvest, Research Package to Reviewed PR, Frontier METHOD and G001 at #2330, #1512 and #1157, public control-plane boundaries, and current open PR inventory. Repository code search for solved-conjectures returned no hits; search and recursive inventory are not exhaustive (tree was truncated). Existing owners take precedence:
- Research/promotion/negative evidence/dedup/closure: ALREADY_IMPLEMENTED as documented method; do not build another research controller.
- Exact publication tree and consumer readback: IN_PROGRESS via #2312/#2317 and existing CN owners; not a new CDN engine.
- S1 scientific simulation: #2321 exact head f23e1e0a7a6e68641e5e33f1e02d7ca929d37256 already includes transaction, ledger and tree tests; #2337 active independent thin-client PR head observed 43669239b8396fcde2535c0bf96e51f74d4b73b7. Do not modify either author branch in this task.
- Kompas memory custody #2345 already has test coverage for boolean integer substitution, invalid data and receipt authority separation. No new forecast engine.
- Novel candidate: type-strict equivalence of the ledger and its derived current view. A direct source-bound falsifier survives below; one action only: ask original #2321 owner to assess and add strict typed equality plus independent regression fixtures to existing suite if appropriate. Not a new heavy handoff; no claim of production vulnerability or CODEX_READY.

## Local controlled reproduction (grade B, scoped engineering only)

Exact pinned original code:
https://github.com/Donh91/Investering-Framework-Archive-v1/blob/f23e1e0a7a6e68641e5e33f1e02d7ca929d37256/research/s1_root_v2/ledger_screen.py
Git blob d68a87f063e8911b24511d39fdd76a8016dfc94c matched local UTF-8 source bytes before execution. Baseline tests inspected: tests/governance/test_s1_root_v2_ledger_screen.py blob 827b971486b60ff4f29ffc176bc4b85c536ca9f0; ledger_conformance.py blob ef431c19dc68f20e1c78f1ebb6befb39fcb4ddee. Existing tests cover boolean PR, missing evidence, stale head, veto and many malformed inputs, but the six view-only type substitutions below were not found in those files.

Claim: current-view equivalence is type-sensitive for all mirrored keys, not merely Python equality. Counterexample: ledger receipt_comment=1 with view receipt_comment=true passes equality. Ledger remains byte-identical and hashed, so this tests a noncanonical derived view, not hash tampering. A canonical strict view ought to reject malformed type substitution with UNKNOWN (proposed specification clarification). It returns EXACT_APPROVAL_ONLY, not merge authorization. Even lane_eligible=NO can yield EXACT_APPROVAL_ONLY by design, as the existing test explicitly confirms. Do not conflate the evidence class with authority.

Reproduce offline from the exact pinned original (run from repo checkout or supply path):
```python
import hashlib, json
from pathlib import Path
src = Path("research/s1_root_v2/ledger_screen.py").read_bytes()
assert hashlib.sha1(b"blob " + str(len(src)).encode() + b"\0" + src).hexdigest() == "d68a87f063e8911b24511d39fdd76a8016dfc94c"
baseline, candidate = {}, {}
exec(src, baseline)
# Local proof-of-concept only; no repository code change.
old = b"r[k] != current[0][k]"
new = b"(type(r[k]) is not type(current[0][k]) or r[k] != current[0][k])"
assert src.count(old) == 1
exec(src.replace(old, new), candidate)
r = dict(seq=1, repo="example/repo", pr=1, head="a"*40,
         verdict="APPROVE", verdict_line_exact=True, receipt_comment=1,
         report_blob="b"*40, bridge_commit="c"*40, lane_eligible="NO")
def run(screen, view_delta, ledger_delta):
    rr = {**r, **ledger_delta}
    raw = json.dumps(rr).encode() + b"\n"
    s = dict(schema="CLAUDE_APPROVAL_CURRENT_v1",
             ledger_sha256=hashlib.sha256(raw).hexdigest(),
             ledger_last_seq=1, entries=[{**rr, **view_delta}])
    return screen(json.dumps(s).encode(), raw, "example/repo", 1, "a"*40, 1)
cases = [
    ("valid", {}, {}, "EXACT_APPROVAL_ONLY"),
    ("seq_bool", {"seq": True}, {}, "UNKNOWN"),
    ("seq_float", {"seq": 1.0}, {}, "UNKNOWN"),
    ("receipt_bool", {"receipt_comment": True}, {}, "UNKNOWN"),
    ("receipt_float", {"receipt_comment": 1.0}, {}, "UNKNOWN"),
    ("exact_int", {"verdict_line_exact": 1}, {}, "UNKNOWN"),
    ("exact_float", {"verdict_line_exact": 1.0}, {}, "UNKNOWN"),
    ("pr_bool", {"pr": True}, {}, "UNKNOWN"),
    ("changed_head", {"head": "d"*40}, {}, "UNKNOWN"),
    ("veto", {}, {"verdict": "BLOCK"}, "HOLD"),
    ("ledger_receipt_bool", {}, {"receipt_comment": True}, "UNKNOWN"),
]
for name, v, l, expected in cases:
    print(name, expected, run(baseline["screen"], v, l),
          run(candidate["screen"], v, l))
```

Observed baseline 5/11, candidate 11/11 under the proposed strict-view oracle. Six malformed view-only cases accepted in baseline; all six rejected by candidate. Five controls unchanged. This is one type-confusion family, not six independent defects, not a statistical significance claim. Local code executed only on owner repository's research source; no network, real receipts or mutation of original PR. The proposed patch has NOT passed original-owner full suite or CI, independent review or integration. Does not prove that all malformed types, nested objects, provenance or trust boundaries are handled. Strong countercase: if consumer intentionally permits numerically equivalent JSON views, existing behavior may be intentional; confirm typed contract and downstream consumption first. If schema is explicitly permissive, reject this change and document why. Scope: integrity/diagnostics in draft shadow only. No production severity asserted.

## Transfer roadmap, not extra dispatches

1. P0-adjacent original S1 ROOT owner: add six table-driven view-mismatch cases to existing conformance family, strict schema/type check for mirrored fields where required, run existing full tests and mutation removing type check. Verify native review/veto remain independent, no new authority. Success: all original tests pass, six strict cases fail before and pass after; removing guard is caught. Stop if equivalent coverage exists, schema intentionally permits coercion, or change collides with original owner. USD0, no separate paid run.
2. CN forecast/range invariant examples, advisory only: finite values, lower <= central <= upper, honest source/availability time, frozen vintage, unavailable != neutral; property tests first, Lean only if a persistent complex arithmetic/state invariant justifies cost. Formal validity is not forecast skill; compare empirical outcomes against persistence on valid original cohorts only after authorized gates.
3. Alpha paper-wallet examples, advisory only: conservation of balances/fees, no fills after decision time unless defined execution simulation, no double debit on retries; execution realism, slippage, capacity and out-of-sample economics remain separate. Existing Alpha owners, no new test or paper wallet.
4. Scientific research: explicitly distinguish statement/specification, deterministic proof, assumptions, held-out evidence, independent review, release and observed consumer effect. Existing lifecycle already defines these; proposed improvement is a concrete adversarial test, not another taxonomy engine.

Lean adoption decision: HOLD / NOT_DECISION_USEFUL as a new dependency today. Compare simplest Python property/finite-state tests versus a selective formal model on one stable high-risk invariant only if existing tests cannot cover it. Require a specification-to-code refinement mapping, no custom unreviewed assumptions, pinned toolchain, independent replay, negative mutants, measured extra defects per engineering cost and retirement if no incremental value. Do not install or port upstream code. No market predictions or financial action.

## Closure and authority

Public-only research; Round 3 PROSPECTIVE_COLLECTION_ONLY, hypothesis testing and outcome scoring OFF, no R1/R2 reopening, no restricted values or credentials. No automation, paid spend or production changes. Parallel independent source reads in one interactive assistant, no separate AI-agent runs. Source screening complete within stated coverage; controlled narrow reproduction complete; all-market/Lean/independent-review/runtime lanes NOT_EXECUTED. Actual next: notify #2321 and #1512 and Bridge #173 with exact evidence and propose original-owner disposition. No second implementation branch, no self-approval or merge. Original owner can reject/dedup/repair within existing handoff capacity. No full audit, no confirmed live economic benefit. Review readiness is not implementation or production closure.
