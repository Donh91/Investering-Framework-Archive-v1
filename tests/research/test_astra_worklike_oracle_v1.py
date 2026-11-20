import tempfile
import unittest
from pathlib import Path
from scripts.research import astra_worklike_oracle_v1 as o
from scripts.research import astra_worklike_pilot_v1 as p

class TestOracle(unittest.TestCase):
    def test_independent_oracle_not_self_report(self):
        actual = {p.sha(p.canonical(f)): expected for f, expected in o.cases()}
        def run(_candidate, fixture):
            return p.canonical({"status": actual[p.sha(p.canonical(fixture))]})
        r = o.compare(b"candidate", run=run)
        self.assertEqual(r["status"], "PASS")
        self.assertEqual(len(r["cases"]), 11)
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

if __name__ == "__main__":
    unittest.main()
