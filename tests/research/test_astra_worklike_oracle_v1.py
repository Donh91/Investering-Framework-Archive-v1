import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from scripts.research import astra_worklike_oracle_v1 as o
from scripts.research import astra_worklike_pilot_v1 as p

class TestOracle(unittest.TestCase):
    def test_independent_oracle_not_self_report(self):
        actual = {p.sha(p.canonical(f)): expected for f, expected in o.cases()}
        def run(_candidate, fixture):
            return p.canonical({"status": actual[p.sha(p.canonical(fixture))]})
        r = o.compare(b"candidate", run=run)
        self.assertEqual(r["status"], "PASS")
        self.assertEqual(len(r["cases"]), 16)
        self.assertTrue(r["native_attestation_required"])
        self.assertFalse(r["release_authority"])
        self.assertEqual(o.compare(b"candidate", run=lambda *_: b'{"status":"ELIGIBLE"}')["status"], "TEST_FAILURE")

    def test_fails_closed_on_wrong_format(self):
        for data in (b'{"status":"PASS"}', b'{"status":"ELIGIBLE","extra":1}',
                     b'{"status":"UNKNOWN","status":"ELIGIBLE"}', b"garbage", b"x"*8193):
            with self.assertRaises(p.PilotBlocked):
                o.parse_answer(data)
        with self.assertRaises(p.PilotBlocked):
            o.compare(b"candidate", run=lambda *_: b'{"status":"PASS"}')

    def test_fixed_docker_arguments(self):
        with tempfile.TemporaryDirectory() as d:
            c = o.docker_command("python@sha256:"+"a"*64, "astra-pilot-"+"b"*32, Path(d))
            for arg in ("--read-only", "--cap-drop", "ALL", "--no-new-privileges", "--privileged"):
                if arg in ("--no-new-privileges", "--privileged"):
                    self.assertNotIn(arg, c)
                else:
                    self.assertIn(arg, c)
            self.assertEqual(c[c.index("--network")+1], "none")
            self.assertEqual(c[c.index("--pull")+1], "never")
            self.assertEqual(c[c.index("--user")+1], "65534:65534")
            self.assertEqual(c[c.index("--security-opt")+1], "no-new-privileges")
            self.assertTrue(c[c.index("--mount")+1].endswith(",dst=/candidate,readonly"))
            self.assertEqual(c[-4:], ["python", "-I", "-B", "/candidate/candidate.py"])
            for image in ("python:latest", "python:3.12", "other@sha256:"+"a"*64):
                with self.assertRaises(p.PilotBlocked):
                    o.docker_command(image, "astra-pilot-"+"b"*32, Path(d))


    def test_network_attempt_is_an_independent_negative_control(self):
        with mock.patch.object(o, "run_case",
                               return_value=b'{"status":"INVALID"}') as run:
            result = o.network_negative_control(o.PINNED_IMAGE)
            self.assertTrue(result["attempted"])
            self.assertEqual(result["outbound_connection"], "DENIED")
            self.assertEqual(run.call_count, 1)
            self.assertEqual(run.call_args.args[0], o.PINNED_IMAGE)
        with mock.patch.object(o, "run_case", return_value=b'{"status":"ELIGIBLE"}'):
            with self.assertRaisesRegex(p.PilotBlocked, "NETWORK_ATTEMPT_NOT_DENIED"):
                o.network_negative_control(o.PINNED_IMAGE)

    def test_strict_json_and_artifact_bounds(self):
        for data in (b'{"a":1,"a":2}', b'{"a":NaN}', b'{"a":Infinity}', b'garbage'):
            with self.assertRaises(p.PilotBlocked):
                o.strict_json(data)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root/"raw").write_bytes(b"ok")
            self.assertEqual(o.read_artifact(root, "raw", 2), b"ok")
            with self.assertRaises(p.PilotBlocked):
                o.read_artifact(root, "raw", 1)
            (root/"alias").symlink_to(root/"raw")
            with self.assertRaises(p.PilotBlocked):
                o.read_artifact(root, "alias", 2)

    def test_native_collected_binding_and_negative_controls(self):
        from scripts.research import owner_astra_mission_v1 as m
        mid = m.WORKLIKE_STAGE1
        expected = {"mission_dir": "06_RESEARCH_LAB/astra_missions/"+mid,
                    "request_sha256": "a"*64, "bundle_sha256": "b"*64,
                    "input_token_upper": 25000}
        head = "c"*40
        raw = p.canonical({"contract": "ASTRA_WORKLIKE_PROPOSAL_v1",
                           "files": [{"path": path, "preimage_sha256": None,
                                      "content": "pass\\n"} for path in p.PATHS]})
        receipt = {"contract": "ASTRA_MISSION_RECEIPT_V1", "mission_id": mid,
                   "work_id": mid, "run_id": "42", "release_main_sha": head,
                   "request_sha256": expected["request_sha256"],
                   "bundle_sha256": expected["bundle_sha256"],
                   "status": "completed", "incomplete_details": None,
                   "model": p.MODEL, "provider_model": p.MODEL,
                   "response_id": "resp_test1234", "reasoning_effort": p.EFFORT,
                   "provider_reasoning_effort": p.EFFORT, "no_retry": True,
                   "research_only": True, "owner_reserved_usd": 1.5,
                   "usage_valid": True, "usage": {"input_tokens": 1000,"output_tokens": 1000},
                   "estimated_upper_usd": m.estimate_cost(p.MODEL,1000,1000),
                   "output_file": "ASTRA_RAW_REPORT.md", "output_sha256": p.sha(raw),
                   "bytes": len(raw)}
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            archive = root/"archive"/expected["mission_dir"]/"results"
            archive.mkdir(parents=True)
            def write(r, meta=expected, payload=raw):
                for target in (root, archive):
                    (target/"receipt.json").write_bytes(p.canonical(r))
                    (target/"source_manifest.json").write_bytes(p.canonical(meta))
                (archive/"ASTRA_RAW_REPORT.md").write_bytes(payload)
            with mock.patch.object(m,"build_request",return_value=({},b"",expected)), \
                 mock.patch.object(m,"git_head",return_value=head), \
                 mock.patch.dict(os.environ,{"GITHUB_RUN_ID":"42"}):
                write(receipt)
                candidate,binding=o.admit_collected(root)
                self.assertEqual(candidate,b"pass\\n")
                self.assertEqual(binding["paid_run_id"],"42")
                for field,value in (("run_id","41"),("status","incomplete"),
                                    ("provider_reasoning_effort","max"),
                                    ("estimated_upper_usd",1.9),("output_sha256","f"*64),
                                    ("request_sha256","f"*64)):
                    write(dict(receipt,**{field:value}))
                    with self.assertRaises(p.PilotBlocked):
                        o.admit_collected(root)
                write(receipt, payload=raw+b"x")
                with self.assertRaises(p.PilotBlocked):
                    o.admit_collected(root)

if __name__ == "__main__":
    unittest.main()
