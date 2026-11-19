"""Synthetic no-bill regression tests; the preview reads only pinned public Git blobs."""
import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from scripts.research import manual_astra_maeve_task2_20261117 as m

class TestMaeveOneShot(unittest.TestCase):
    def test_exact_source_pins_and_repeatable_request(self):
        with mock.patch.object(m.core, "http_json", side_effect=AssertionError("NETWORK_FORBIDDEN")):
            req, data, meta = m.build_request()
            self.assertEqual((req, data, meta), m.build_request())
        self.assertEqual(meta["source_count"], 11)
        self.assertEqual(meta["source_main_sha"], m.SOURCE_PIN)
        self.assertEqual(meta["mission_blob"], m.MISSION_BLOB)
        self.assertEqual(meta["request_sha256"], m.digest(data))
        self.assertEqual(meta["request_bytes"], len(data))
        self.assertLessEqual(meta["worst_case_text_only_usd"], 10)
        self.assertNotIn("tools", req)
        self.assertEqual(req["model"], "gpt-6-astra")
        self.assertEqual(req["reasoning"], {"effort": "high"})
    def test_preview_writes_identical_bytes_and_no_http(self):
        with tempfile.TemporaryDirectory() as d:
            class Capture:
                buffer = io.BytesIO()
            out = Capture()
            with mock.patch.object(m.sys, "stdout", out), contextlib.redirect_stderr(io.StringIO()) as err, mock.patch.object(m.core, "http_json", side_effect=AssertionError("NETWORK_FORBIDDEN")):
                m.prepare(Path(d), preview=True)
            raw = (Path(d) / "request.json").read_bytes()
            self.assertEqual(raw, out.buffer.getvalue())
            self.assertIn(m.digest(raw), err.getvalue())
    def test_wrong_path_and_blob(self):
        with self.assertRaisesRegex(ValueError, "PINNED_SOURCE_MISMATCH"):
            m.pinned_blob(m.SOURCE_PIN, m.MISSION_PATH, "a"*40)
    def test_reserved_new_id_and_forged_reservation_denied(self):
        with self.assertRaises(ValueError):
            m.check_reservation()  # Original one-shot consumed; never replay.
        with mock.patch.object(m, "WORK_ID", "PREVIOUS-WORK-ID"):
            with self.assertRaises(ValueError):
                m.check_reservation()
    def test_owner_hash_and_rerun_denied(self):
        h = "a"*64
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/"event.json"
            event = {"action":"created","issue":{"number":937},"comment":{
                "author_association":"OWNER","user":{"login":"Donh91"},"id":123,
                "body":m.TRIGGER+" request_sha256="+h}}
            p.write_text(json.dumps(event))
            env = {"GITHUB_EVENT_NAME":"issue_comment","GITHUB_ACTOR":"Donh91",
                "GITHUB_REPOSITORY":m.REPO,"GITHUB_REF":"refs/heads/main",
                "GITHUB_RUN_ATTEMPT":"1","GITHUB_EVENT_PATH":str(p)}
            with mock.patch.dict(os.environ,env), mock.patch.object(m,"git_head",return_value="a"*40):
                self.assertEqual(m.owner_event(h)["comment"]["id"],123)
                with self.assertRaises(ValueError):
                    m.owner_event("b"*64)
                with mock.patch.dict(os.environ,{"GITHUB_RUN_ATTEMPT":"2"}):
                    with self.assertRaises(ValueError):
                        m.owner_event(h)
                with mock.patch.dict(os.environ,{"GITHUB_ACTOR":"not-owner"}):
                    with self.assertRaises(ValueError):
                        m.owner_event(h)
    def test_durable_claim_census_fail_closed(self):
        body=m.claim_body("123","a"*64)
        with mock.patch.object(m.core,"http_json",return_value=[{"body":body,"user":{"login":"other"}}]):
            m.claims("synthetic")
        with mock.patch.object(m.core,"http_json",return_value=[{"body":body,"user":{"login":"github-actions[bot]"}}]):
            with self.assertRaisesRegex(ValueError,"ALREADY_CONSUMED"):
                m.claims("synthetic")
        with mock.patch.object(m.core,"http_json",return_value={}):
            with self.assertRaises(ValueError):
                m.claims("synthetic")
    def test_submit_denies_unbound_and_at_most_one_even_on_timeout(self):
        req={"model":m.MODEL,"reasoning":{"effort":"high"}}
        claim={"run_id":"123","request_sha256":"a"*64}
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ,{"OPENAI_API_KEY":"synthetic"}):
            p=Path(d)
            with mock.patch.object(m,"verify_claim",side_effect=ValueError("NO_CLAIM")), mock.patch.object(m.core,"http_json") as api:
                with self.assertRaises(ValueError):
                    m.submit(p)
                api.assert_not_called()
            with mock.patch.object(m,"verify_claim",return_value=(req,claim)):
                m.mark_attempt(p)
                with mock.patch.object(m.core,"http_json",side_effect=TimeoutError("ambiguous")) as api:
                    with self.assertRaises(TimeoutError):
                        m.submit(p)
                    with self.assertRaises(FileExistsError):
                        m.submit(p)
                    self.assertEqual(api.call_count,1)
                    self.assertEqual(api.call_args.args[:2],("POST",m.core.API+"/responses"))
    def test_report_byte_preservation(self):
        raw="Line 1\r\nÅ  \n"
        self.assertEqual(m.report_bytes({"output_text":raw}),raw.encode("utf-8"))
        self.assertEqual(m.report_bytes({"output":[{"content":[{"type":"output_text","text":raw}]}]}),raw.encode("utf-8"))
