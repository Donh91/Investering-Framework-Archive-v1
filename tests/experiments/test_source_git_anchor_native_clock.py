import copy
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from scripts.experiments.source_git_anchor import (
    ARCHIVE_REPOSITORY, ARCHIVE_REPOSITORY_ID, AcceptedMainSource, _push_upper_bound)


class NativeUpperBound(unittest.TestCase):
    def setUp(self):
        self.intro = {"contract": "EXPERIMENT_FIRST_MAIN_INTRODUCTION_v1",
                      "repository": ARCHIVE_REPOSITORY, "ref": "refs/heads/main",
                      "first_commit": "a"*40, "first_parent": "b"*40, "main_head": "c"*40,
                      "git_blob_sha": "d"*40, "content_sha256": "e"*64, "path": "raw/source.json"}
        repo = {"id": ARCHIVE_REPOSITORY_ID, "full_name": ARCHIVE_REPOSITORY}
        self.row = {"id": 1, "event": "push", "head_branch": "main", "head_sha": "a"*40,
                    "created_at": "2026-09-30T06:39:12Z", "repository": repo, "head_repository": dict(repo)}

    def test_later_witness_only_upper_bound(self):
        result = _push_upper_bound(self.intro, {"total_count": 1, "workflow_runs": [self.row]})
        self.assertEqual(result["present_by_utc"], "2026-09-30T06:39:13Z")
        self.assertIsNone(result["absent_through_utc"])
        self.assertFalse(result["scientifically_admitted"])
        self.assertFalse(result["server_acceptance_clock_verified"])
        self.assertTrue(result["server_upper_witness_verified"])

    def test_wrong_identity_and_clock_fail_closed(self):
        for key, value in (("event", "pull_request"), ("head_branch", "other"),
                           ("head_sha", "f"*40), ("id", True), ("created_at", "not a date"),
                           ("head_repository", {"id": 999, "full_name": ARCHIVE_REPOSITORY})):
            with self.subTest(key=key):
                self.assertIsNone(_push_upper_bound(self.intro, {"total_count": 1, "workflow_runs": [dict(self.row, **{key: value})]}))

    def test_missing_conflicting_or_partial_response(self):
        for response in (None, {}, {"total_count": 0, "workflow_runs": []},
                         {"total_count": 2, "workflow_runs": [self.row]},
                         {"total_count": 2, "workflow_runs": [self.row, self.row]}):
            self.assertIsNone(_push_upper_bound(self.intro, response))

    def test_earliest_upper_bound_and_no_lower(self):
        other = dict(self.row, id=2, created_at="2026-09-30T06:39:20Z")
        result = _push_upper_bound(self.intro, {"total_count": 2, "workflow_runs": [other, self.row]})
        self.assertEqual(result["witness_run_id"], 1)
        self.assertIsNone(result["absent_through_utc"])

    def test_existing_timed_caller_still_refuses_without_network(self):
        anchor = AcceptedMainSource(Path("."))
        with patch("scripts.experiments.source_git_anchor._native_push_runs") as remote:
            self.assertFalse(anchor.matches(Path("raw/source.json"), "e"*64,
                                            accepted_after=datetime.now(timezone.utc)))
            remote.assert_not_called()

    def test_diagnostic_rejects_outage(self):
        anchor = AcceptedMainSource(Path("."))
        with patch.object(anchor, "first_introduction", return_value=self.intro), patch(
                "scripts.experiments.source_git_anchor._native_push_runs", return_value=None):
            self.assertIsNone(anchor.native_upper_witness(Path("raw/source.json"), "e"*64))

if __name__ == "__main__":
    unittest.main()
