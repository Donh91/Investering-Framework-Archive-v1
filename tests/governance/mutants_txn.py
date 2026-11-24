"""Mutation check for research/s1_root_v2/txn.py.

Each mutant is one exact textual replacement applied to a COPY of the tree in a
temp dir; the unmutated copy must pass and every mutant must fail the test file.
Run: python3 tests/governance/mutants_txn.py   (exit 0 only if all are killed)
"""
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
FILES = ("research/s1_root_v2/txn.py", "research/s1_root_v2/txn_sim.py",
         "tests/governance/test_s1_root_v2_txn.py")
OFF = "if False:"

MUTANTS = [  # (name, old, new)
    ("allow_merge_retry", 'if mine and "merge" not in run:', 'if mine and run.get("merge") != "OK":'),
    ("skip_intent", 'return act(POST_INTENT, "qualified", key=key, **b)',
     'return act(MERGE, "no_intent", pr=b["pr"], sha=b["head"], method="squash")'),
    ("login_only_attribution", 'if pr.get("merged_by") != S1_LOGIN:\n        return FOREIGN, "other_actor"',
     'if pr.get("merged_by") == S1_LOGIN:\n        return OWN, "login"'),
    ("unknown_treated_as_own", "if cls == UNKNOWN:\n        return act(HALT_UNKNOWN",
     "if cls == UNKNOWN and False:\n        return act(HALT_UNKNOWN"),
    ("merge_without_exact_head", 'sha=intent["head"], method="squash")', 'sha=None, method="squash")'),
    ("rebind_intent_to_new_head", 'if pr.get("head") != cand["head"]:\n            return act(NOOP, "head_changed")',
     'if pr.get("head") != cand["head"]:\n            b["head"] = pr["head"]\n'
     '            key = idempotency_key(**b)'),
    ("reconcile_ignores_head", 'if pr.get("head") != intent["head"]:\n        return FOREIGN, "other_head"',
     OFF + '\n        return FOREIGN, "other_head"'),
    ("drop_single_parent", 'if len(c["parents"]) != 1:', OFF),
    ("drop_merged_after_intent", 'if t < intent["created_at"]:', OFF),
    ("drop_same_second", 'if t == intent["created_at"]:', OFF),
    ("drop_origin_window", 'if t > intent["created_at"] + WINDOW_S:', OFF),
    ("drop_subject_check", 'if not str(c.get("subject", "")).endswith("(#%d)" % intent["pr"]):', OFF),
    ("drop_blob_check", 'if not obs["head_blobs"] or c.get("files") != obs["head_blobs"]:', OFF),
    ("drop_main_ancestry", 'if obs["on_main"] not in ("ahead", "identical"):', OFF),
    ("drop_bypass_check", 'if obs["rule_suite"] != "pass":', OFF),
    ("drop_owner_marker", "if cls == OWN and not mine and owner_marker(led, intent):", OFF),
    ("drop_settle_delay", 'if now - intent["created_at"] < SETTLE_S:', OFF),
    ("drop_duplicate_tiebreak", 'if dup:\n            return act(ABANDON, "DUPLICATE")\n        if lane_halted(led):',
     "if lane_halted(led):"),
    ("drop_key_spent", 'if any(i["key"] == key for i in intents(led)):', OFF),
    ("drop_merge_deadline", 'if now - intent["created_at"] > DEADLINE_S:', OFF),
    ("reconciled_claims_s1_run", 'origin="S1_RUN" if mine else "UNKNOWN")', 'origin="S1_RUN")'),
    ("accept_edited_intent", 'if comment.get("created_at") != comment.get("updated_at"):', OFF),
    ("accept_forged_key", '!= f["key"]:\n            return None', '!= f["key"] and False:\n            return None'),
    ("merge_past_lane_halt", 'if lane_halted(led):\n            return act(ABANDON, "lane_halted")',
     OFF + '\n            return act(ABANDON, "lane_halted")'),
    ("intent_past_lane_halt", 'if lane_halted(led):\n            return act(NOOP, "lane_halted")',
     OFF + '\n            return act(NOOP, "lane_halted")'),
    ("ambiguous_key_encoding", "repo_id=%d\\npr=%d\\n", "%d%d"),
    ("key_ignores_base_main", "base_main=%s\\nloop_blob=%s\\n", "base_main=%.0s\\nloop_blob=%s\\n"),
    ("key_accepts_uppercase", '"0123456789abcdef"', '"0123456789abcdefABCDEF"'),
    ("closure_after_ledger_receipt", "RECEIPT_ORDER = (ITEM, CLOSURE, MERGE_RCPT)",
     "RECEIPT_ORDER = (MERGE_RCPT, ITEM, CLOSURE)"),
    ("foreign_halts_lane", "if cls == FOREIGN:\n        return act(RECONCILE_FOREIGN, why)",
     'if cls == FOREIGN:\n        return act(HALT_UNKNOWN, why, halt="reconcile_readback")'),
]


def run_tests(tree):
    r = subprocess.run([sys.executable, "-m", "unittest", "-f", "tests.governance.test_s1_root_v2_txn"],
                       cwd=tree, env={"PYTHONPATH": str(tree), "PATH": "/usr/bin:/bin"},
                       capture_output=True, text=True, timeout=600)
    first = next((ln for ln in r.stderr.splitlines() if ln.startswith(("FAIL:", "ERROR:"))), "")
    return r.returncode == 0, first.split(" (")[0]


def main():
    src = (ROOT / FILES[0]).read_text()
    killed = 0
    with tempfile.TemporaryDirectory() as d:
        tree = pathlib.Path(d)
        for f in FILES:
            (tree / f).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(ROOT / f, tree / f)
        ok, _ = run_tests(tree)
        print("baseline (unmutated): %s" % ("PASS" if ok else "FAIL"))
        if not ok:
            return 2
        for name, old, new in MUTANTS:
            if src.count(old) != 1:
                print("%-30s NOT APPLICABLE (%d matches)" % (name, src.count(old)))
                continue
            (tree / FILES[0]).write_text(src.replace(old, new))
            ok, first = run_tests(tree)
            killed += not ok
            print("%-30s %s  %s" % (name, "SURVIVED" if ok else "killed", first))
    print("killed %d/%d" % (killed, len(MUTANTS)))
    return 0 if killed == len(MUTANTS) else 1


if __name__ == "__main__":
    sys.exit(main())
