"""Adversarial one-POST owner-only Astra realdata integration, no network/payments."""
import json
import os
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from scripts.api_agent import manual_astra_task2_realdata_v2 as m

ROOT = Path(__file__).resolve().parents[2]


class RealdataAstraV2Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.out = Path(self.tmp.name)
        self.event = self.out / "event.json"
        self.event.write_text(json.dumps({
            "issue": {"number": 1596},
            "comment": {"user": {"login": "Donh91"}, "author_association": "OWNER",
                        "body": m.OWNER_TRIGGER + " " + m.OWNER_CONFIRM}
        }))
        self.env = patch.dict(os.environ, {
            "GITHUB_ACTOR": "Donh91", "GITHUB_REF": "refs/heads/main",
            "GITHUB_REPOSITORY": "Donh91/Investering-Framework-Archive-v1",
            "GITHUB_EVENT_PATH": str(self.event),
            "GITHUB_RUN_ID": "TEST_RUN123",
            "GITHUB_TOKEN": "INERT_GH_TOKEN",
            "OPENAI_API_KEY": "INERT_API_KEY"})
        self.env.start()
        self.addCleanup(self.env.stop)

    def test_actual_native_public_source_census_and_no_secret_tree(self):
        sources = m.select_sources(ROOT)
        self.assertGreaterEqual(len(sources), 60)
        self.assertLessEqual(len(sources), m.MAX_SOURCE_FILES)
        self.assertIn("03_DAILY_CAPTURE_LOGS/weekly/2026/W45/WEEKLY_HOURLY_ENRICHED.csv", sources)
        self.assertIn("research/historical_reality_engine/CROSS_ERA_NATIVE_RESULTS_20261107.json", sources)
        self.assertTrue(any("/kompas_scientific_edge_program_v2_1/" in x for x in sources))
        self.assertTrue(any("/shared_row_model_tournament_v1/" in x for x in sources))
        self.assertFalse(any("round3_new_information" in x for x in sources))

    def test_build_actual_zip_evidence_and_sha_manifest(self):
        index = m.build(ROOT, self.out)
        zpath = self.out / m.ZIP_NAME
        self.assertEqual(m.checksum(zpath), index["archive_sha256"])
        with zipfile.ZipFile(zpath) as z:
            names = z.namelist()
            self.assertIn("SOURCE_INDEX.json", names)
            self.assertIn("research_outputs/forecast_rows.csv", names)
            self.assertIn("research_outputs/risk_rows.csv", names)
            self.assertIn("research_outputs/risk_summary.json", names)
            self.assertIn("research/historical_reality_engine/CROSS_ERA_NATIVE_RESULTS_20261107.json", names)
            digest = json.loads(z.read("SOURCE_INDEX.json"))
            self.assertEqual(digest["file_count"], index["file_count"])
            self.assertEqual(digest["source_main_sha"], index["source_main_sha"])
            for row in digest["manifest"]:
                self.assertEqual(m.sha(z.read(row["relative_path"])), row["sha256"])
            risk = json.loads(z.read("research_outputs/risk_summary.json"))
            self.assertEqual(risk["refusals"]["NO_SAME_CUTOFF_SOURCE_ELIGIBLE_BAR"], 30)
            self.assertEqual(risk["risk_candidates"]["ETH_PRICE_24H_MINUS3"]["n_positive_origin_days_correlated"],0)
        with self.assertRaisesRegex(ValueError, "BUNDLE_ALREADY_EXISTS"):
            m.build(ROOT, self.out)

    def test_wrong_owner_comment_refused(self):
        m.check_trigger()
        with patch.dict(os.environ, {"GITHUB_ACTOR": "someone-else"}):
            with self.assertRaisesRegex(ValueError, "OWNER_MAIN_GATE_FAIL"):
                m.check_trigger()
        broken = json.loads(self.event.read_text())
        broken["comment"]["author_association"] = "CONTRIBUTOR"
        self.event.write_text(json.dumps(broken))
        with self.assertRaisesRegex(ValueError, "OWNER_ISSUE_COMMENT_GATE_FAIL"):
            m.check_trigger()

    def test_native_issue_claim_expiry_independent(self):
        with patch.object(m,"http",return_value=[{"body":m.CLAIM_MARKER+" already used"}]):
            with self.assertRaisesRegex(ValueError,"DURABLE_CLAIM_ALREADY_EXISTS"):
                m.check_claims("INERT_GH_TOKEN","Donh91/Investering-Framework-Archive-v1")

    def test_shared_10usd_owner_reservation_native(self):
        m.check_shared_reservation()
        with patch.object(m,"ROOT",self.out):
            p=self.out/"research/api_agent/coordination/API_PENDING_BILLING_RISK_V1.json"
            p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text('{"owner_reservations":[]}')
            with self.assertRaisesRegex(ValueError,"OWNER_10USD_RESERVATION_MISSING"):
                m.check_shared_reservation()

    def _fake_bundle(self):
        (self.out/m.ZIP_NAME).write_bytes(b"INERT_SYNTHETIC_ZIP")
        digest=m.checksum(self.out/m.ZIP_NAME)
        m.write_once(self.out/"source_manifest.json",{"archive_sha256":digest,"source_main_sha":"a"*40})
        m.write_once(self.out/"claim.json",{"mission":m.MISSION,"archive_sha256":digest,
                                          "source_main_sha":"a"*40,"run_id":"TEST_RUN123"})
        (self.out/"prompt.txt").write_text("Execute independent Python checks of real source CSV/JSON.")

    def test_file_upload_exactly_one_and_id_verified(self):
        self._fake_bundle()
        with patch.object(m, "http", return_value={"id":"file-SYNTHETIC5678","purpose":"assistants"}) as call:
            m.multipart_upload(self.out)
            self.assertEqual(call.call_args[0][0],"POST")
            self.assertEqual(call.call_args[0][1],m.API+"/files")
            self.assertIn(b"INERT_SYNTHETIC_ZIP",call.call_args.kwargs["data"])
        with self.assertRaisesRegex(ValueError,"ONE_USE_REPLAY_BLOCKED"):
            m.multipart_upload(self.out)

    def test_model_always_gets_real_zip_and_mandatory_python(self):
        self._fake_bundle()
        m.write_once(self.out/"file_handle.json",{"archive_sha256":m.checksum(self.out/m.ZIP_NAME),
                                                   "file_id":"file-SYNTHETIC5678"})
        payload, price = m.make_payload(self.out)
        self.assertEqual(payload["model"],"gpt-6-astra")
        self.assertEqual(payload["reasoning"]["effort"],"high")
        self.assertEqual(payload["tool_choice"],"required")
        self.assertEqual(payload["tools"][0]["type"],"code_interpreter")
        self.assertEqual(payload["tools"][0]["container"]["memory_limit"],"1g")
        self.assertEqual(payload["tools"][0]["container"]["file_ids"],["file-SYNTHETIC5678"])
        self.assertEqual(payload["max_output_tokens"],90_000)
        self.assertLess(price,8.0)

    def test_paid_post_never_retries(self):
        self._fake_bundle()
        m.write_once(self.out/"file_handle.json",{"archive_sha256":m.checksum(self.out/m.ZIP_NAME),
                                                   "file_id":"file-SYNTHETIC5678"})
        with patch.object(m,"http",return_value={
            "id":"resp_SYNTHETIC5678","status":"in_progress","model":m.MODEL}) as call:
            m.submit(self.out)
            self.assertEqual(call.call_args[0][0],"POST")
            self.assertEqual(call.call_args[0][1],m.API+"/responses")
        with self.assertRaisesRegex(ValueError,"ONE_USE_REPLAY_BLOCKED"):
            m.submit(self.out)
        self.assertEqual(m.read(self.out/"paid_post_attempt.json")["post_attempts"],1)

    def test_ambiguous_post_is_permanently_one_attempt(self):
        self._fake_bundle()
        m.write_once(self.out/"file_handle.json",{"archive_sha256":m.checksum(self.out/m.ZIP_NAME),
                                                   "file_id":"file-SYNTHETIC5678"})
        with patch.object(m,"http",side_effect=TimeoutError("Synthetic")):
            with self.assertRaises(TimeoutError):
                m.submit(self.out)
        with self.assertRaisesRegex(ValueError,"ONE_USE_REPLAY_BLOCKED"):
            m.submit(self.out)
        self.assertFalse((self.out/"response_handle.json").exists())

    def test_completed_api_response_requires_real_code_interpreter_call(self):
        self._fake_bundle()
        m.write_once(self.out/"response_handle.json",{
            "response_id":"resp_SYNTHETIC5678","source_main_sha":"a"*40,
            "archive_sha256":m.checksum(self.out/m.ZIP_NAME),"payload_sha256":"b"*64})
        result={"id":"resp_SYNTHETIC5678","model":m.MODEL,"status":"completed",
                "output":[{"type":"message","content":[{"type":"output_text","text":"Synthetic research report. "*35}]}],
                "usage":{"input_tokens":9000,"output_tokens":16000}}
        with patch.object(m,"http",return_value=result):
            self.assertEqual(m.collect(self.out),3)
        receipt=m.read(self.out/"receipt.json")
        self.assertFalse(receipt["tool_execution_verified"])
        self.assertEqual(receipt["code_interpreter_call_count"],0)

    def test_source_private_key_denied(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"some").mkdir()
            (root/"some/file.md").write_text("-----BEGIN PRIVATE KEY-----\nsecret\n")
            with patch.object(m,"SOURCE_GLOBS",("some/*.md",)),patch.object(m,"REQUIRED_FILES",()):
                with self.assertRaisesRegex(ValueError,"SOURCE_CONTAINS_CREDENTIAL_INDICATOR"):
                    m.select_sources(root)

    def test_bounded_source_file_bytes_denied(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"some").mkdir()
            (root/"some/file.md").write_bytes(b"A"*(m.MAX_ONE_SOURCE_BYTES+1))
            with patch.object(m,"SOURCE_GLOBS",("some/*.md",)),patch.object(m,"REQUIRED_FILES",()):
                with self.assertRaisesRegex(ValueError,"SOURCE_EXCEEDS_PER_FILE_BOUND"):
                    m.select_sources(root)


if __name__=="__main__":
    unittest.main()
