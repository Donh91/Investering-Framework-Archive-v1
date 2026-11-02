"""Research Lab queue compatibility and no-ghost-action tests."""
import copy
import json
import unittest
from pathlib import Path
from scripts.governance.s1_research_resume_census_v1 import (
    ResearchQueueError, census,
)

URL = "https://github.com/Donh91/Meme-Alpha-Lab/issues/98"
SHA = "a" * 40


def queue():
    return {
        "contract": "RESEARCH_LAB_EXTERNAL_SPECIALIST_DISSECTION_QUEUE_V1",
        "authority": "RESEARCH_ONLY",
        "transversal": [],
        "lanes": [{
            "id": "S1_SELLABILITY", "owner": "existing Alpha owner",
            "state": "FORWARD_CASE_PENDING",
            "execution_issue": URL,
            "next_action": "Accumulate prospective pairs before evaluation",
        }],
    }


class ResearchRecoveryTests(unittest.TestCase):
    def test_pending_is_wait_not_automatic_research(self):
        result = census(queue(), SHA)
        item = result["items"][0]
        self.assertEqual(item["disposition"], "AWAIT_EXPLICIT_MATERIAL_TRIGGER")
        self.assertFalse(item["science_admitted"])
        self.assertFalse(item["auto_dispatch"])
        self.assertFalse(result["actual_github_states_checked"])

    def test_old_merged_work_requires_followup(self):
        item = queue()
        item["lanes"][0]["state"] = "MERGED_CAPABILITY_ACTIVE"
        self.assertEqual(
            census(item, SHA)["items"][0]["disposition"],
            "EXISTING_MERGE_FOLLOWUP_NOT_AUTO_CLOSED",
        )

    def test_negative_research_is_retained(self):
        item = queue()
        item["lanes"][0]["state"] = "REJECTED_FALSIFIED"
        self.assertEqual(census(item, SHA)["items"][0]["disposition"],
                         "RETAIN_NEGATIVE_LEARNING")

    def test_original_link_required(self):
        item = queue()
        del item["lanes"][0]["execution_issue"]
        self.assertEqual(census(item, SHA)["items"][0]["disposition"],
                         "ORIGINAL_OWNER_LINK_REQUIRED")

    def test_duplicate_hypothesis_rejected(self):
        item = queue()
        item["lanes"].append(copy.deepcopy(item["lanes"][0]))
        with self.assertRaises(ResearchQueueError):
            census(item, SHA)

    def test_invalid_contract_rejected(self):
        item = queue()
        item["authority"] = "BUY_AUTHORIZED"
        with self.assertRaises(ResearchQueueError):
            census(item, SHA)

    def test_empty_queue_rejected(self):
        item = queue()
        item["lanes"] = []
        with self.assertRaises(ResearchQueueError):
            census(item, SHA)

    def test_unbound_source_rejected(self):
        with self.assertRaises(ResearchQueueError):
            census(queue(), "short")

    def test_missing_owner_rejected(self):
        item = queue()
        del item["lanes"][0]["owner"]
        with self.assertRaises(ResearchQueueError):
            census(item, SHA)

    def test_real_existing_queue_shape_is_compatible(self):
        root = Path(__file__).resolve().parents[2]
        data = json.loads((root / "04_RESEARCH_LAB/external_specialist_dissection/QUEUE_V1.json").read_text())
        result = census(data, SHA)
        self.assertGreater(result["count"], 5)
        self.assertTrue(all(not item["auto_dispatch"] for item in result["items"]))
        self.assertTrue(all(not item["science_admitted"] for item in result["items"]))


if __name__ == "__main__":
    unittest.main()
