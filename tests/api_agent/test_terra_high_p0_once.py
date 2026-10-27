"""Deterministic no-network tests for owner-approved one-shot P0 API lane."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.api_agent import terra_high_p0_once as p


class TerraHighP0OnceTests(unittest.TestCase):
    def test_small_source_allowlist_and_no_private_path(self):
        self.assertEqual(len(p.SOURCE_FILES), 6)
        self.assertEqual(len(p.CDN_URLS), 2)
        self.assertEqual(p.MODEL, "gpt-6.1-terra")
        self.assertEqual(p.MODEL_EFFORT, "high")
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
            self.assertEqual(ctx["scope"], "P0_HOURLY_COMPASS_CN_PAGES_ONLY")
            self.assertEqual(ctx["source_commit_sha"], "c" * 40)
            self.assertEqual(ctx["requirements"]["natural_source_windows"], 6)
            self.assertLess(manifest["context_bytes"], p.MAX_CONTEXT_BYTES)
            self.assertEqual(manifest["public_cdn_reads"], 2)
            self.assertIn("ONE highest-leverage", prompt)
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
