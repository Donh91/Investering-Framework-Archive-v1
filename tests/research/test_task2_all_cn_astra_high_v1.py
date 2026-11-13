"""One-shot public empirical Astra High transport with no network or paid calls."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts.research import task2_all_cn_astra_high_v1 as a
from scripts.api_agent import manual_astra_task2_high_v1 as core

ENV={"GITHUB_ACTOR":"Donh91","GITHUB_EVENT_NAME":"issue_comment",
     "GITHUB_REF":"refs/heads/main","GITHUB_REPOSITORY":"Donh91/Investering-Framework-Archive-v1",
     "GITHUB_RUN_ID":"11111111111","GITHUB_SHA":"f"*40,
     "GITHUB_TOKEN":"INERT_TEST","OPENAI_API_KEY":"INERT_TEST"}

class OwnerLongitudinalHighTests(unittest.TestCase):
    def setUp(self):
        d=tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        self.root=Path(d.name)
        self.out=self.root/"run"
        self.out.mkdir(parents=True)
        self.an=self.root/"analysis"
        self.an.mkdir(parents=True)
        self.event=self.root/"event.json"
        self.event.write_text(json.dumps({"action":"created","issue":{"number":1596},
                     "comment":{"id":123,"body":a.TRIGGER,"user":{"login":"Donh91"}}}))
        self.env=patch.dict(os.environ,{**ENV,"GITHUB_EVENT_PATH":str(self.event)})
        self.env.start();self.addCleanup(self.env.stop)
        ledger=self.root/"ledger.json"
        ledger.write_text(json.dumps({"owner_reservations":[{
             "work_id":a.MISSION,"status":"OWNER_RESERVED_PREHTTP","upper_usd":10,
             "one_paid_post_max":1,"reconciliation_required":True}]}))
        self.lp=patch.object(a,"CANONICAL_LEDGER",ledger)
        self.lp.start();self.addCleanup(self.lp.stop)

    def test_only_specific_owner_issue_comment(self):
        self.assertEqual(a.owner_event()["comment"]["id"],123)
        self.event.write_text(json.dumps({"action":"created","issue":{"number":1596},
                         "comment":{"id":123,"body":"wrong","user":{"login":"Donh91"}}}))
        with self.assertRaisesRegex(ValueError,"EXACT_OWNER_TRIGGER_NOT_MATCHED"):
            a.owner_event()

    def test_other_actor_or_branch_fails_before_paid(self):
        with patch.dict(os.environ,{"GITHUB_ACTOR":"github-actions[bot]"}):
            with self.assertRaisesRegex(ValueError,"OWNER_EVENT_GATE_FAILED"):
                a.owner_event()
        with patch.dict(os.environ,{"GITHUB_REF":"refs/heads/claude/log"}):
            with self.assertRaisesRegex(ValueError,"OWNER_EVENT_GATE_FAILED"):
                a.owner_event()

    def test_unique_mission_and_claim_not_consumed_old(self):
        self.assertNotEqual(a.MISSION,core.MISSION)
        self.assertNotEqual(a.CLAIM_MARKER,core.CLAIM_MARKER if hasattr(core,"CLAIM_MARKER") else "")
        self.assertEqual(a.MAX_COST_USD,10)

    def test_reservation_absence_fails(self):
        self.assertIsNone(a.check_reserve())
        a.CANONICAL_LEDGER.write_text(json.dumps({"owner_reservations":[]}))
        with self.assertRaisesRegex(ValueError,"EXACT_ALLCN_10USD_RESERVATION_MISSING"):
            a.check_reserve()

    def test_existing_durable_claim_blocks_paid_repeat(self):
        with patch.object(a,"http",return_value=[{"body":a.CLAIM_MARKER+" stored"}]):
            with self.assertRaisesRegex(ValueError,"ALLCN_ONE_USE_CLAIM_ALREADY_CONSUMED"):
                a.census("inert")

    def test_expired_artifact_still_prevents_repeat(self):
        with patch.object(a,"http",return_value={"artifacts":[{"name":a.ARTIFACT_CLAIM,"expired":True}]}):
            with self.assertRaisesRegex(ValueError,"ALLCN_ONE_USE_ARTIFACT_ALREADY_EXISTS"):
                a.artifact_census("inert")

    def _claim(self):
        meta={"mission":a.MISSION,"source_main_sha":ENV["GITHUB_SHA"],"request_sha256":"abc",
              "github_run_id":ENV["GITHUB_RUN_ID"],"native_claim_comment_id":777}
        core.write_once(self.out/"claim.json",meta)
        req={"model":a.MODEL,"reasoning":{"effort":"high"},"background":True,"store":True}
        request_hash=core.sha(core.canonical(req)) if hasattr(core,"sha") else a.sha(core.canonical(req))
        meta["request_sha256"]=request_hash
        (self.out/"claim.json").write_bytes(core.canonical(meta))
        core.write_once(self.out/"request.json",req)
        core.write_once(self.out/"prepared.json",{"request_sha256":request_hash})
        return req

    def test_billed_post_never_replayed_on_ambiguous_timeout(self):
        self._claim()
        with patch.object(a,"http",side_effect=TimeoutError("synthetic")):
            with self.assertRaises(TimeoutError):
                a.submit(self.out)
        self.assertTrue((self.out/"attempt.json").exists())
        with self.assertRaisesRegex(ValueError,"ONE_USE_RECORD_ALREADY_EXISTS"):
            a.submit(self.out)

    def test_one_real_response_handle_and_get_only(self):
        self._claim()
        with patch.object(a,"http",return_value={"id":"resp_SYNTHETIC_ONE","model":a.MODEL,"status":"in_progress"}):
            a.submit(self.out)
        completed={"id":"resp_SYNTHETIC_ONE","model":a.MODEL,"status":"completed",
                   "output_text":"SYNTHETIC ALLCN NO VERIFIED EDGE",
                   "usage":{"input_tokens":111,"output_tokens":222}}
        with patch.object(a,"http",return_value=completed) as hit:
            self.assertEqual(a.collect(self.out),0)
            self.assertEqual(hit.call_args.args[0],"GET")
        receipt=core.read(self.out/"receipt.json")
        self.assertFalse(receipt["scientific_skill_promoted"])
        self.assertGreater(receipt["estimated_token_price_usd"],0)
        self.assertIn("SYNTHETIC", (self.out/"ASTRA_HIGH_ALL_CN_FULL_HISTORICAL_RESEARCH.md").read_text())

    def test_budget_formula_conservative_and_bounded(self):
        worst=(a.MAX_INPUT_REQUEST_BYTES*a.TOKEN_PRICE_INPUT+a.MAX_OUTPUT_TOKENS*a.TOKEN_PRICE_OUTPUT)/1_000_000
        self.assertLessEqual(worst,a.MAX_COST_USD)
        self.assertEqual(a.MODEL,"gpt-6-astra")
        self.assertEqual(a.EFFORT,"high")

if __name__=="__main__":
    unittest.main()
