"""K01 (2026-11-19): the altseason false-PASS quarantine manifest is deterministic, complete and never edits packets."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.learning import altseason_false_pass_quarantine_v1 as Q

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / Q.DEFAULT_OUT


def packet(health, bc, generated="2026-11-01T00:00:00Z"):
    return {"packet_generated_at_utc": generated, "packet_sha256": "p" * 64,
            "source_health": {"altseason_context": {"status": health}},
            "normalized_state": {"altseason_context": {"blockchaincenter_altcoin_season": bc} if bc is not None else {}}}


class QuarantineRuleTests(unittest.TestCase):
    def test_rule(self):
        good = {"status": "PASS", "horizons": {"90": {"published_score": 41}}}
        self.assertFalse(Q.is_false_pass(packet("PASS", good)))
        self.assertFalse(Q.is_false_pass(packet("PASS", dict(good, horizons={"90": {"published_score": 0}}))))
        self.assertTrue(Q.is_false_pass(packet("PASS", {"status": "DEGRADED", "failure_state": "BLOCKCHAINCENTER_SCHEMA_DRIFT", "horizons": {}})))
        self.assertTrue(Q.is_false_pass(packet("PASS", None)))
        self.assertTrue(Q.is_false_pass(packet("PASS", dict(good, horizons={"90": {"published_score": True}}))))
        self.assertFalse(Q.is_false_pass(packet("UNAVAILABLE", None)))          # honest health is not quarantined
        self.assertFalse(Q.is_false_pass(packet("DEGRADED_CARRY", None)))

    def test_build_is_deterministic_and_respects_coverage_end(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            d = root / Q.RUNS / "2026/11/19"
            d.mkdir(parents=True)
            (d / "a.json").write_text(json.dumps(packet("PASS", None, "2026-11-19T08:00:00Z")))
            (d / "b.json").write_text(json.dumps(packet("PASS", None, "2026-11-19T10:00:00Z")))   # after coverage end
            (d / "c.json").write_text(json.dumps(packet("PASS", {"status": "PASS", "horizons": {"90": {"published_score": 3}}})))
            m1, m2 = Q.build(root), Q.build(root)
            self.assertEqual(m1, m2)
            self.assertEqual([r["path"].split("/")[-1] for r in m1["packets"]], ["a.json"])
            self.assertEqual(m1["packets"][0]["file_sha256"], hashlib.sha256((d / "a.json").read_bytes()).hexdigest())


class CommittedManifestTests(unittest.TestCase):
    def setUp(self):
        if not MANIFEST.is_file():
            self.skipTest("manifest not in this checkout")
        self.m = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_manifest_is_the_41_packets_and_inert(self):
        self.assertEqual(self.m["contract"], Q.CONTRACT)
        self.assertEqual(self.m["count"], 41)
        self.assertEqual(len(self.m["packets"]), 41)
        self.assertEqual(self.m["authority"], {"rewrites_packets": False, "changes_official_compass": False, "research_only": True})

    def test_every_listed_packet_is_unchanged_and_regenerates_identically(self):
        runs = ROOT / Q.RUNS
        if not any(runs.glob("2026/09/26/*.json")):
            self.skipTest("packet history not in this checkout")
        for row in self.m["packets"]:
            self.assertEqual(hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest(), row["file_sha256"], row["path"])
        self.assertEqual(Q.build(ROOT), self.m)


if __name__ == "__main__":
    unittest.main()
