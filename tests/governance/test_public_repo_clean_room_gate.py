from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.cycle_navigator.build_weekly_cycle_navigator import output_schema


class PublicRepoCleanRoomGateTest(unittest.TestCase):
    def test_stale_data_ping_index_has_local_current_routing_supersession(self):
        text = Path("00_ARCHIVE_CONTROL/CANONICAL_INDEX.md").read_text()
        self.assertIn("CURRENT-ROUTING SUPERSESSION NOTICE (2026-09-14)", text)
        self.assertIn(
            "00_ARCHIVE_CONTROL/2026-09-14__autonomous-data-authority-transition-v1__canonical.md",
            text,
        )
        self.assertIn("02_DATA_PING/", text)

    def test_cycle_navigator_non_ready_status_is_machine_explainable(self):
        schema = output_schema()
        self.assertIn("status_reason_codes", schema["required"])
        reasons = schema["properties"]["status_reason_codes"]["items"]["enum"]
        self.assertIn("CONSUMER_RECEIPT_UNVERIFIED", reasons)
        self.assertIn("LEGACY_NON_READY_CAUSE_UNAVAILABLE", reasons)

        latest = json.loads(
            Path("05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json").read_text()
        )
        if latest.get("status") in {"DEGRADED", "BLOCKED"}:
            self.assertTrue(latest.get("status_reason_codes"))

    def test_cycle_navigator_long_cycle_action_has_no_independent_permission(self):
        readme = Path("05_CYCLE_NAVIGATOR/README.md").read_text()
        contract = Path(
            "05_CYCLE_NAVIGATOR/protocols/"
            "2026-09-14__weekly-cycle-navigator-publication-contract-v1-2.md"
        ).read_text()
        self.assertIn("Authority:** NONE_BY_ITSELF", readme)
        self.assertIn("no independent Main-Framework action permission", contract)
        self.assertIn("Main-Framework permission ceiling", contract)

    def test_public_series_identity_is_not_machine_issue_identity(self):
        index = json.loads(
            Path("05_CYCLE_NAVIGATOR/public_series/CN_PUBLIC_SERIES_INDEX.json").read_text()
        )
        latest_published = index["latest_published"]
        current = index["current_public_projection"]
        self.assertTrue(latest_published["published_path"])
        self.assertTrue(index["latest_completed_score"]["scorecard_path"])
        self.assertIn("machine_issue_number", current)
        self.assertIn("public_issue_number", current)
        self.assertTrue(
            any(
                "Never join public and machine Cycle Navigator records on issue_number alone."
                == invariant
                for invariant in index.get("invariants", [])
            )
        )
        if current.get("publication_status") == "X_READY_NOT_CONFIRMED_PUBLISHED":
            matching = [
                row for row in index["recent_lineage"]
                if row.get("public_issue_number") == current.get("public_issue_number")
            ]
            self.assertTrue(matching)
            self.assertIsNone(matching[-1].get("published_path"))


if __name__ == "__main__":
    unittest.main()
