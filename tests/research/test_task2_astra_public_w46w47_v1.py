"""No-network and no-bill regression for distinct Task2 Astra public W46/W47 lane."""
from __future__ import annotations
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.research import task2_astra_public_w46w47_v1 as a


class TestAstraPublicOneShot(unittest.TestCase):
    def test_manual_only_distinct_from_consumed_routes(self):
        self.assertNotEqual(a.MISSION, "ASTRA-HIGH-TASK2-ALL-CN-HISTORICAL-20261113-ONE")
        self.assertNotEqual(a.MISSION, "ASTRA-HIGH-TASK2-SCIENTIFIC-20261113-ONE")
        self.assertNotEqual(a.MISSION, "ASTRA-HIGH-TASK2-REALDATA-V2-20261113-ONE")
        self.assertEqual(a.MODEL, "gpt-6-astra")
        self.assertEqual(a.MAX_COST, 10)
        self.assertEqual(a.ISSUE, 1596)

    def test_cost_upper_bound_and_no_tools(self):
        upper=(a.MAX_REQUEST_BYTES*a.INPUT_USD_M +
               a.MAX_OUTPUT_TOKENS*a.OUTPUT_USD_M)/1_000_000
        self.assertLessEqual(upper,a.MAX_COST)
        self.assertNotIn("code_interpreter", a.INSTRUCTIONS.lower())
        self.assertIn("NOT EVALUABLE", a.INSTRUCTIONS)
        self.assertIn("W47", a.INSTRUCTIONS)

    def test_authentic_source_inputs_and_real_evidence(self):
        text, sources = a.source_packet()
        self.assertEqual(len(sources),len(a.SOURCE))
        self.assertIn("W46",text)
        self.assertIn("W47",text)
        self.assertEqual(len({x["path"] for x in sources}),len(sources))
        self.assertTrue(all(len(x["sha256"])==64 and x["bytes"]>0 for x in sources))

    def test_preflight_no_network_and_no_provider_post(self):
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.dict(os.environ, {"GITHUB_SHA": "a"*40}):
                with mock.patch.object(a.core,"http_json",side_effect=AssertionError("network used")):
                    a.prepare(Path(d),preview=True)
            req=json.loads((Path(d)/"request.json").read_text())
            meta=json.loads((Path(d)/"source_manifest.json").read_text())
            self.assertEqual(req["model"],a.MODEL)
            self.assertEqual(req["reasoning"],{"effort":"high"})
            self.assertNotIn("tools",req)
            self.assertNotIn("tool_choice",req)
            self.assertLessEqual(meta["worst_case_text_only_usd"],a.MAX_COST)
            self.assertEqual(meta["source_count"],len(a.SOURCE))
            self.assertEqual(meta["source_main_sha"],"a"*40)

    def test_unauthenticated_owner_trigger_rejected(self):
        with mock.patch.dict(os.environ, {
            "GITHUB_EVENT_NAME":"issue_comment","GITHUB_ACTOR":"not-owner",
            "GITHUB_REPOSITORY":a.REPO,"GITHUB_REF":"refs/heads/main",
            "GITHUB_SHA":"a"*40},clear=True):
            with self.assertRaisesRegex(ValueError,"NATIVE_OWNER_EVENT_REQUIRED"):
                a.owner_event()

    def test_wrong_owner_comment_rejected_without_network(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"event.json"
            p.write_text(json.dumps({"action":"created",
                "issue":{"number":1596},
                "comment":{"body":a.TRIGGER+" EXTRA",
                           "user":{"login":"Donh91"},"author_association":"OWNER"}}))
            with mock.patch.dict(os.environ, {
                "GITHUB_EVENT_NAME":"issue_comment","GITHUB_ACTOR":"Donh91",
                "GITHUB_REPOSITORY":a.REPO,"GITHUB_REF":"refs/heads/main",
                "GITHUB_SHA":"a"*40,"GITHUB_EVENT_PATH":str(p)}):
                with self.assertRaisesRegex(ValueError,"EXACT_ONE_TIME"):
                    a.owner_event()

    def test_reservation_must_be_distinct_and_exact(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"ledger.json"
            p.write_text(json.dumps({"absolute_budget_usd":50,
                "owner_reservations":[{"work_id":a.MISSION,"status":"OWNER_RESERVED_PREHTTP",
                    "upper_usd":11,"one_paid_post_max":1,"reconciliation_required":True}]}))
            with mock.patch.object(a,"LEDGER",p):
                with self.assertRaisesRegex(ValueError,"10USD_RESERVATION_REQUIRED"):
                    a.check_reservation()

    def test_claim_and_attempt_one_use_binding(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)
            payload={"model":a.MODEL,"reasoning":{"effort":"high"},"max_output_tokens":a.MAX_OUTPUT_TOKENS}
            a.core.write_once(out/"request.json",payload)
            a.core.write_once(out/"claim.json",{"mission":a.MISSION,"run_id":"42",
                "source_main_sha":"a"*40,"request_sha256":a.digest(a.core.canonical(payload))})
            a.mark_attempt(out)
            row=json.loads((out/"attempt.json").read_text())
            self.assertTrue(row["never_retry_ambiguous"])
            with self.assertRaises(Exception):
                a.mark_attempt(out)


if __name__=="__main__":
    unittest.main()
