"""Adversarial no-network tests of the research-only original direction replay."""
import copy
import json
import unittest

from task2_original_direction_coverage_v1 import audit, sha_blob

A = "a" * 40
B = "b" * 40
PATH = "04_MARKET_LEARNING/handlekompas/official/daily/2026/10/12/CMP-20261012-abcdef123456.json"
CN = "05_CYCLE_NAVIGATOR/weekly/2026/W42/CYCLE_NAVIGATOR_MACHINE_PACKAGE.json"

def fixture(*, version="OFFICIAL_DAILY_COMPASS_SCORING_v3",
            freshness="PASS", direction="DOWN", cn_generated=1700000000):
    cn_raw = (json.dumps({"contract": "CYCLE_NAVIGATOR_MACHINE_PACKAGE_v1",
                          "generated_unix": cn_generated}) + "\n").encode()
    doc = {
        "compass_id": "CMP-20261012-abcdef123456",
        "issued_at_utc": "2026-10-12T12:00:00Z",
        "scoring_contract": version,
        "market_now": {
            "directional_state": (
                "UNCHANGED_NO_NEW_OBSERVATION"
                if direction == "UNAVAILABLE" and freshness == "PASS"
                else "BEARISH"
            )
        },
        "horizons": {
            "NEXT_12H": {"expected_direction": direction},
            "NEXT_1_3D": {"expected_direction": "MIXED" if freshness == "PASS" else "UNAVAILABLE"},
            "NEXT_5_7D": {"expected_direction": "MIXED" if freshness == "PASS" else "UNAVAILABLE"},
        },
        "source_bindings": {
            "auto_market_state": {
                "freshness": {"status": freshness},
                "source_snapshot_commit_sha": B
            },
            "cycle_navigator": {
                "machine_package": {"path": CN, "git_blob_sha": sha_blob(cn_raw)}
            }
        }
    }
    raw = (json.dumps(doc, sort_keys=True) + "\n").encode()
    records = [
        {
            "original_forecast_path": PATH,
            "horizon": horizon,
            "original_forecast_git_blob_sha1": sha_blob(raw),
            "scoring_contract": version,
        }
        for horizon in ("12h", "72h", "168h")
    ]
    return {"execution_source_commit_sha": A, "original_records": records}, {
        (A, PATH): raw, (B, CN): cn_raw
    }

class TestOriginalHorizonCoverage(unittest.TestCase):
    def run_case(self, census, files):
        return audit(census, lambda ref, path: files[(ref, path)], expected_originals=1)

    def test_valid_original_cn_source_and_denominator(self):
        census, files = fixture()
        result = self.run_case(census, files)
        self.assertEqual(result["original_forecasts"], 1)
        self.assertEqual(result["directional_counts"], {
            "NEXT_12H": 1, "NEXT_1_3D": 0, "NEXT_5_7D": 0,
        })
        self.assertFalse(result["first_known_certified"])

    def test_rewritten_forecast_blob_rejected(self):
        census, files = fixture()
        census["original_records"][1]["original_forecast_git_blob_sha1"] = "0"*40
        with self.assertRaisesRegex(ValueError, "ORIGINAL_FORECAST_GIT_BLOB_MISMATCH"):
            self.run_case(census, files)

    def test_missing_original_horizon_rejected(self):
        census, files = fixture()
        census["original_records"].pop()
        with self.assertRaisesRegex(ValueError, "ORIGINAL_DENOMINATOR_INCOMPLETE"):
            self.run_case(census, files)

    def test_duplicate_horizon_rejected(self):
        census, files = fixture()
        census["original_records"].append(copy.deepcopy(census["original_records"][0]))
        with self.assertRaisesRegex(ValueError, "DUPLICATE_OR_INVALID_ORIGINAL_HORIZON"):
            self.run_case(census, files)

    def test_original_cn_snapshot_tampering_rejected(self):
        census, files = fixture()
        files[(B, CN)] = b'{"contract":"CYCLE_NAVIGATOR_MACHINE_PACKAGE_v1","generated_unix":1700000001}\n'
        with self.assertRaisesRegex(ValueError, "CN_INPUT_SOURCE_SNAPSHOT_BLOB_MISMATCH"):
            self.run_case(census, files)

    def test_cn_created_after_forecast_rejected(self):
        census, files = fixture(cn_generated=1990000000)
        with self.assertRaisesRegex(ValueError, "ORIGINAL_CN_GENERATION_AFTER_ISSUE"):
            self.run_case(census, files)

    def test_stale_source_must_fail_closed(self):
        census, files = fixture(freshness="STALE_OR_UNAVAILABLE", direction="DOWN")
        with self.assertRaisesRegex(ValueError, "STALE_FORECAST_FAILED_TO_ABSTAIN"):
            self.run_case(census, files)

    def test_original_no_new_observation_is_abstention(self):
        census, files = fixture(direction="UNAVAILABLE")
        self.assertEqual(
            self.run_case(census, files)["source_failclosed_causes"],
            {"NO_NEW_OBSERVATION": 1},
        )

    def test_wrong_scoring_version_rejected(self):
        census, files = fixture()
        census["original_records"][0]["scoring_contract"] = "OFFICIAL_DAILY_COMPASS_SCORING_v2"
        with self.assertRaisesRegex(ValueError, "ORIGINAL_SCORING_VERSION_MISMATCH"):
            self.run_case(census, files)

    def test_unknown_direction_label_rejected(self):
        census, files = fixture()
        doc = json.loads(files[(A, PATH)])
        doc["horizons"]["NEXT_12H"]["expected_direction"] = "MAGIC"
        files[(A, PATH)] = (json.dumps(doc, sort_keys=True) + "\n").encode()
        digest = sha_blob(files[(A, PATH)])
        for row in census["original_records"]:
            row["original_forecast_git_blob_sha1"] = digest
        with self.assertRaisesRegex(ValueError, "UNKNOWN_ORIGINAL_DIRECTION"):
            self.run_case(census, files)

if __name__ == "__main__":
    unittest.main()
