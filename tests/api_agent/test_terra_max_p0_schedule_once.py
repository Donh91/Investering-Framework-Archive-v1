"""Deterministic no-network tests for independent owner-approved second MAX P0-only API lane."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.api_agent import terra_max_p0_schedule_once as p


class TerraMaxP0ScheduleOnceTests(unittest.TestCase):
    def test_small_source_allowlist_and_no_private_path(self):
        self.assertEqual(len(p.SOURCE_FILES), 9)
        self.assertEqual(len(p.CDN_URLS), 2)
        self.assertEqual(p.MODEL, "gpt-6.1-terra")
        self.assertEqual(p.MODEL_EFFORT, "max")
        for forbidden in (".env", "Donh91/secrets/key", "private_research/wallet.json", "/etc/passwd"):
            with self.subTest(forbidden=forbidden), self.assertRaisesRegex(ValueError, "ALLOWLIST"):
                p.source_file("a" * 40, forbidden)
        with self.assertRaisesRegex(ValueError, "APPROVED"):
            p.cdn_readback("https://example.com/private")

    def test_bounded_exact_source_and_public_only_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows = [
                {"path": path, "sha256": "a" * 64, "bytes": 123,
                 "preview": "example", "clipped": False}
                for path in p.SOURCE_FILES
            ]
            pages = [
                {"url": url, "status": "FETCHED_JSON", "raw_sha256": "b" * 64,
                 "keys": ["status"], "preview": "{}"}
                for url in p.CDN_URLS
            ]
            with patch.object(p, "git", return_value="c" * 40), \
                 patch.object(p, "source_file", side_effect=rows), \
                 patch.object(p, "cdn_readback", side_effect=pages):
                manifest = p.build(Path(tmp))
            ctx = json.loads((Path(tmp) / "context.json").read_text())
            prompt = (Path(tmp) / "prompt.txt").read_text()
            self.assertEqual(ctx["scope"], "P0_HOURLY_SCHEDULER_LIVENESS_AND_INDEPENDENT_RECOVERY_ONLY")
            self.assertEqual(ctx["source_commit_sha"], "c" * 40)
            self.assertEqual(ctx["requirements"]["natural_source_windows"], 6)
            self.assertLess(manifest["context_bytes"], p.MAX_CONTEXT_BYTES)
            self.assertEqual(manifest["public_cdn_reads"], 2)
            self.assertIn("ONE smallest SAFE", prompt)
            self.assertIn("forecast_candidates MUST equal []", prompt)
            self.assertNotIn("Task 2", prompt)
            self.assertNotIn("Graph B", prompt)

    def test_unavailable_public_cdn_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows = [{"path": path, "sha256": "f" * 64, "bytes": 2,
                     "preview": "{}", "clipped": False} for path in p.SOURCE_FILES]
            pages = [
                {"url": p.CDN_URLS[0], "status": "FETCHED_JSON"},
                {"url": p.CDN_URLS[1], "status": "UNAVAILABLE"},
            ]
            with patch.object(p, "git", return_value="a" * 40), \
                 patch.object(p, "source_file", side_effect=rows), \
                 patch.object(p, "cdn_readback", side_effect=pages):
                with self.assertRaisesRegex(ValueError, "CDN_READBACK_UNAVAILABLE"):
                    p.build(Path(tmp))

    def test_full_528_comment_census_and_existing_claim_block(self):
        rows = [
            {"id": i, "user": {"login": "Donh91"}, "body": "comment"}
            for i in range(528)
        ]
        visited = []
        def fake(method, route, payload=None):
            self.assertEqual(method, "GET")
            self.assertIn("?per_page=25&page=", route)
            page = int(route.rsplit("page=", 1)[1])
            visited.append(page)
            return rows[(page - 1) * 25:page * 25]
        with patch.object(p, "gh", side_effect=fake):
            self.assertIsNone(p.existing_claim())
        self.assertEqual(visited, list(range(1, 23)))
        rows[-1] = {
            "id": 777, "html_url": "https://github.com/example/claim",
            "user": {"login": p.BOT}, "body": p.MARKER + "\nlocked",
        }
        with patch.object(p, "gh", side_effect=fake):
            self.assertEqual(p.existing_claim()["id"], 777)
            with patch.dict("os.environ", {"GITHUB_RUN_ATTEMPT": "1", "GITHUB_ACTOR": "Donh91"}):
                with self.assertRaisesRegex(RuntimeError, "ALREADY_CLAIMED"):
                    p.claim("123456", "d" * 40)

    def test_second_max_fails_closed_without_original_max_claim(self):
        with patch.dict("os.environ", {"GITHUB_RUN_ATTEMPT": "1", "GITHUB_ACTOR": "Donh91"}), \
             patch.object(p, "existing_claim", return_value=None), \
             patch.object(p, "scan_existing_marker", return_value=None), \
             patch.object(p, "gh", side_effect=AssertionError("no POST allowed")):
            with self.assertRaisesRegex(RuntimeError, "ORIGINAL_MAX_CLAIM_MISSING"):
                p.claim("40560000123", "e" * 40)

    def test_second_max_claim_is_unique_and_never_reuses_old_marker(self):
        records = []
        def fake(method, route, payload=None):
            self.assertEqual(method, "POST")
            self.assertTrue(payload["body"].startswith(p.MARKER))
            self.assertNotIn("TERRA_MAX_ENDGAME_ONCE_CLAIM_v1", payload["body"])
            records.append(payload)
            return {"id": 12345, "html_url": "https://github.com/test"}
        with patch.dict("os.environ", {"GITHUB_RUN_ATTEMPT": "1", "GITHUB_ACTOR": "Donh91"}), \
             patch.object(p, "existing_claim", return_value=None), \
             patch.object(p, "scan_existing_marker", return_value={"id": 1}), \
             patch.object(p, "gh", side_effect=fake):
            result = p.claim("40560000123", "e" * 40)
        self.assertEqual(result["claim_id"], 12345)
        self.assertEqual(len(records), 1)
        self.assertNotEqual(p.MARKER, "[TERRA_MAX_ENDGAME_ONCE_CLAIM_v1]")

    def test_branch_one_shot_routing_and_separate_concurrency(self):
        workflow = Path(".github/workflows/api-agent-gateway-gate.yml").read_text()
        self.assertIn("  terra-max-p0-schedule-once:", workflow)
        job = workflow.split("  terra-max-p0-schedule-once:", 1)[1]
        self.assertIn("github.event_name == 'pull_request'", job)
        self.assertIn("github.actor == 'Donh91'", job)
        self.assertIn("terra-max-p0-schedule-one-time-20261027", job)
        self.assertIn("NO_PAID_RERUN", job)
        self.assertIn("TERRA_MAX_P0_SCHEDULE_ONCE", job)
        self.assertNotIn("  schedule:", job)
        self.assertIn("check_monthly_cost_guard.py", job)

    def test_unknown_or_repeated_run_must_not_bill(self):
        with patch.dict("os.environ", {"GITHUB_RUN_ATTEMPT": "2", "GITHUB_ACTOR": "Donh91"}), \
             patch.object(p, "gh", side_effect=AssertionError("network forbidden")):
            with self.assertRaisesRegex(RuntimeError, "FIRST_ATTEMPT_ONLY"):
                p.claim("123456", "d" * 40)
        with patch.dict("os.environ", {"GITHUB_RUN_ATTEMPT": "1", "GITHUB_ACTOR": "stranger"}), \
             patch.object(p, "gh", side_effect=AssertionError("network forbidden")):
            with self.assertRaisesRegex(RuntimeError, "FIRST_ATTEMPT_ONLY"):
                p.claim("123456", "d" * 40)

    def test_census_fails_closed_on_corruption_and_page_ceiling(self):
        with patch.object(p, "gh", return_value=[{"id": 1, "user": None}]):
            with self.assertRaisesRegex(RuntimeError, "INVALID_COMMENT_ROW"):
                p.existing_claim()
        with patch.object(p, "gh", return_value=[{}] * 26):
            with self.assertRaisesRegex(RuntimeError, "INVALID_COMMENT_PAGE"):
                p.existing_claim()
        valid_page = [{"id": 1, "user": {"login": "Donh91"}, "body": "old"}] * 25
        with patch.object(p, "gh", return_value=valid_page):
            with self.assertRaisesRegex(RuntimeError, "INCOMPLETE_COMMENT_CENSUS"):
                p.existing_claim()


if __name__ == "__main__":
    unittest.main()
