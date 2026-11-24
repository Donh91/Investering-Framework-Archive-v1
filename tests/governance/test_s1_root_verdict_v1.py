"""Mutants for the public-only shadow verdict; no GitHub calls."""
import copy
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "governance"))
from s1_root_verdict_v1 import build_root_verdict, digest, force_none, REQUIRED

H, M, C = "a"*40, "b"*40, "c"*40
def fixture():
    return {"main": M, "run_id": 1, "run_attempt": 1, "repo": {"identity": True}, "complete": True,
            "pins": {"ok": True, "contract_blob": C}, "verdict": {"source": "OK", "t2": "OK", "main": M, "contract_blob": C, "bootstrap_3b": C},
            "main_moved_during_build": False, "lane": {"state": "ON", "halt": None},
            "rulesets": {"stable": True, "census": []}, "open_intents": [],
            "next": [{"action": "MERGE_IF_CLAUDE_APPROVE", "pr": 9, "head": H}],
            "prs": [{"n": 9, "head": H, "open": [], "writer": None, "paths": ["docs/x.md"], "shrinks": [], "lane": {"eligible": True, "risk_floor": "LOW"},
                     "main_overlap": [], "ci": {"state": "GREEN", "privacy": "NO_RESTRICTED_CONTENT", "checks": {"green": True}, "tuples": {k: {"s": "PASS", "job": 1} for k in REQUIRED}},
                     "review": {"changes_requested": False, "unresolved_p0p1": 0}}]}
class TestRootVerdict(unittest.TestCase):
    def test_clean_shadow_still_no_write(self):
        v = build_root_verdict(fixture())
        self.assertEqual(v["next_action"], "NONE")
        self.assertEqual(v["candidate"]["head"], H)
        self.assertEqual(v["preconditions"]["ci"]["state"], "PASS")
        self.assertEqual(v["preconditions"]["private_approval_and_veto"]["state"], "FAIL")
        d = v.pop("evidence_sha256")
        self.assertEqual(d, digest(v))
    def test_mutants(self):
        mutants = [
            ("pins", lambda b: b["pins"].update(ok=False)),
            ("pins", lambda b: b["verdict"].update(bootstrap_3b="f"*40)),
            ("drift", lambda b: b.update(main_moved_during_build=True)),
            ("complete", lambda b: b.update(complete=False)),
            ("candidate", lambda b: b["next"][0].update(head="d"*40)),
            ("candidate", lambda b: b["prs"].append(copy.deepcopy(b["prs"][0]))),
            ("candidate", lambda b: b["prs"][0].update(open=["BLOCK"])),
            ("lane", lambda b: b["prs"][0]["lane"].update(risk_floor="HIGH_IMPACT")),
            ("lane", lambda b: b["lane"].update(halt=123)),
            ("ci", lambda b: b["prs"][0]["ci"]["tuples"].pop("gate")),
            ("ci", lambda b: b["prs"][0]["ci"]["tuples"]["gate"].update(job=True)),
            ("privacy", lambda b: b["prs"][0].update(gate_stale=["x"])),
            ("public_review", lambda b: b["prs"][0]["review"].update(changes_requested=True)),
            ("public_review", lambda b: b["prs"][0]["review"].update(unresolved_p0p1=False)),
            ("rulesets", lambda b: b["rulesets"].update(stable=False)),
            ("no_intents", lambda b: b.update(open_intents=[1])),
        ]
        for gate, mutate in mutants:
            with self.subTest(gate=gate, mutation=mutate):
                b=fixture(); mutate(b)
                v=build_root_verdict(b)
                self.assertEqual(v["next_action"], "NONE")
                self.assertEqual(v["preconditions"][gate]["state"], "FAIL")
    def test_private_and_untrusted_strings_never_serialized(self):
        b=fixture(); b["prs"][0]["private_review"]="DO_NOT_EMIT"; b["next"][0]["why"]="DO_NOT_EMIT"
        self.assertNotIn("DO_NOT_EMIT", json.dumps(build_root_verdict(b)))
    def test_shrink_recomputes_digest_and_erases_candidate(self):
        v=force_none(build_root_verdict(fixture()))
        self.assertEqual(v["candidate"]["kind"], "NONE")
        self.assertEqual(v.pop("evidence_sha256"), digest(v))
    def test_missing_and_malformed(self):
        for b in (None, [], {}, {"next":[{"action":[],"head":{},"pr":True}]}):
            self.assertEqual(build_root_verdict(b)["next_action"], "NONE")
