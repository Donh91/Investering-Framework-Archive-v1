"""Synthetic fail-closed tests; original Actions ZIP is checked in gated PR CI."""
import hashlib
import re
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"04_MARKET_LEARNING/handlekompas/research/2026-10-16__task2_matured314_original_frozen_votes_v1.py"
spec=importlib.util.spec_from_file_location("matured_vote_314",SOURCE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
votes=m.source_module(ROOT)

def complete(taker="UP",cross="UP"):
    names=[*votes.PRICE,*votes.TAKER,*votes.ETH_CROSS]
    return {"votes":[{"family":n,"direction":("UP" if n in votes.PRICE else taker if n in votes.TAKER else cross)}
                     for n in names]}

class MatchedFrozenVoteTests(unittest.TestCase):
    def test_original_pre_registered_price_taker_and_eth_cross(self):
        c=m.family_choices(complete(),"ETH","UP",votes)
        self.assertEqual(set(c),set(m.CANDIDATES))
        self.assertTrue(all(c[n]=="UP" for n in m.CANDIDATES))
        b=m.family_choices(complete(),"BTC","UP",votes)
        self.assertIsNone(b["ETHBTC_BREADTH_ONLY"])
        self.assertIsNone(b["PRICE_TAKER_ETH_CROSS_CONFIRM"])

    def test_taker_conflict_and_cross_missing_are_not_imputed(self):
        c=m.family_choices(complete(taker="DOWN"),"ETH","UP",votes)
        self.assertEqual(c["PRICE_FAMILY_MAJORITY"],"UP")
        self.assertEqual(c["TAKER_ONLY"],"DOWN")
        self.assertIsNone(c["PRICE_AND_TAKER_CONFIRM"])
        self.assertIsNone(c["PRICE_TAKER_ETH_CROSS_CONFIRM"])
        missing=m.family_choices({"votes":[]},"ETH","UP",votes)
        self.assertTrue(all(v is None for v in missing.values()))

    def test_duplicate_indicator_cannot_earn_more_votes(self):
        obj=complete()
        obj["votes"].append(obj["votes"][0].copy())
        c=m.family_choices(obj,"ETH","UP",votes)
        self.assertIsNone(c["PRICE_FAMILY_MAJORITY"])
        self.assertIsNone(c["PRICE_AND_TAKER_CONFIRM"])

    def test_available_case_rate_matches_same_clock_controls(self):
        rows=[
            {"candidate":{"TAKER_ONLY":"UP"},"observed_direction":"UP",
             "baseline_direction":"DOWN","baseline_hit":"False","descriptive_hit":"True"},
            {"candidate":{"TAKER_ONLY":"DOWN"},"observed_direction":"UP",
             "baseline_direction":"UP","baseline_hit":"True","descriptive_hit":"False"},
            {"candidate":{"TAKER_ONLY":None},"observed_direction":"UP",
             "baseline_direction":"UP","baseline_hit":"True","descriptive_hit":"True"}]
        s=m.summarize(rows,"TAKER_ONLY")
        self.assertEqual(s["original_matured_directional_n"],3)
        self.assertEqual(s["available_n"],2)
        self.assertEqual(s["coverage_pct"],66.667)
        self.assertEqual(s["candidate_hits"],1)
        self.assertEqual(s["same_clock_price_hits"],1)
        self.assertEqual((s["candidate_only_hits"],s["price_only_hits"]),(1,1))
        self.assertEqual(s["direction_disagreements_vs_price"],2)

    def test_wrong_actions_zip_fails_before_parsing(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"fake.zip"
            p.write_bytes(b"not-the-original")
            with self.assertRaisesRegex(ValueError,"ORIGINAL_ZIP_SHA_MISMATCH"):
                m.read_artifact(p)

    def test_forecast_blob_mismatch_and_unsafe_path_fail_closed(self):
        path=m.PREFIX+"2026/09/15/p.json"
        row={"prediction_id":path+"#1H:BTC","prediction_sha256":"0"*64}
        with mock.patch.object(m.subprocess,"check_output",return_value=b'{"horizons":{}}'):
            with self.assertRaisesRegex(ValueError,"ORIGINAL_FORECAST_SHA256_MISMATCH"):
                m.original_files(ROOT,[row])
        row["prediction_id"]=m.PREFIX+"../escape.json#1H:BTC"
        with self.assertRaisesRegex(ValueError,"UNSAFE_ISSUED_FORECAST_PATH"):
            m.original_files(ROOT,[row])

    def test_pr_research_validation_token_is_read_only(self):
        # A PR may execute its own source code. It must not inherit the
        # production main-writer token while replaying the source ZIP.
        workflow=(ROOT/".github/workflows/native-handlekompas.yml").read_text()
        self.assertIn("permissions:\\n  actions: write\\n  contents: write\\n  issues: write", workflow)
        validate=workflow.split("\\n  validate:\\n",1)[1].split("\\n  readback:\\n",1)[0]
        self.assertRegex(validate,r"(?m)^    permissions:\\n      actions: read\\n      contents: read\\n")
        self.assertNotRegex(validate,r"(?m)^      (?:actions|contents|issues): write$")
        readback=workflow.split("\\n  readback:\\n",1)[1].split("\\n  incident:\\n",1)[0]
        self.assertNotIn("\\n    permissions:",readback)

    def test_research_receipt_only_pr_change_triggers_original_source_replay(self):
        # Previous workflow guard omitted the published JSON receipt: a future
        # receipt-only edit could have escaped immutable source replay.
        workflow=(ROOT/".github/workflows/native-handlekompas.yml").read_text()
        match=re.search(r"replay_pattern='([^']+)'", workflow)
        self.assertIsNotNone(match, "Original-source replay path guard is missing")
        pattern=match.group(1)
        receipt="04_MARKET_LEARNING/handlekompas/research/2026-10-16__TASK2_ORIGINAL_MATURED314_FROZEN_VOTE_FAMILY_RECEIPT_v1.json"
        source="04_MARKET_LEARNING/handlekompas/research/2026-10-16__task2_matured314_original_frozen_votes_v1.py"
        test="tests/research/test_task2_matured314_original_frozen_votes.py"
        for path in (receipt, source, test):
            with self.subTest(path=path):
                self.assertIsNotNone(re.search(pattern, path))
        for path in ("docs/unrelated.md", "04_MARKET_LEARNING/handlekompas/LATEST.json"):
            with self.subTest(unrelated=path):
                self.assertIsNone(re.search(pattern, path))

    def test_historical_modification_is_not_an_executable_authority(self):
        self.assertIn("EXPOST",m.STATUS)
        self.assertEqual(len(m.CANDIDATES),5)

if __name__=="__main__":
    unittest.main()
