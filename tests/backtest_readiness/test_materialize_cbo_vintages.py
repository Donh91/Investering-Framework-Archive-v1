import hashlib
import unittest

from tools.backtest_readiness.materialize_cbo_vintages import (
    MaterializationError,
    TARGET_VARIABLES,
    analyze_csv_bytes,
    raw_url,
)


def make_payload(*, duplicate=False, omit=None):
    lines = ["date,variable,value"]
    for variable in sorted(TARGET_VARIABLES):
        if variable == omit:
            continue
        lines.append(f"FY2024,{variable},1")
        lines.append(f"FY2025,{variable},2")
    lines.append("FY2024,context_only,3")
    if duplicate:
        variable = sorted(TARGET_VARIABLES)[0]
        lines.append(f"FY2024,{variable},99")
    return ("\n".join(lines) + "\n").encode()


class CboMaterializationTests(unittest.TestCase):
    def test_valid_payload_is_hashed_and_structurally_audited(self):
        payload = make_payload()
        result = analyze_csv_bytes("2024-06", payload)
        self.assertEqual(result["sha256"], hashlib.sha256(payload).hexdigest())
        self.assertEqual(result["row_count"], 9)
        self.assertEqual(result["duplicate_date_variable_keys"], 0)
        self.assertEqual(set(result["target_variables"]), TARGET_VARIABLES)
        self.assertEqual(
            result["publication_timestamp_status"],
            "PENDING_OFFICIAL_RELEASE_BINDING",
        )

    def test_duplicate_key_fails_closed(self):
        with self.assertRaises(MaterializationError):
            analyze_csv_bytes("2024-06", make_payload(duplicate=True))

    def test_missing_required_variable_fails_closed(self):
        missing = sorted(TARGET_VARIABLES)[0]
        with self.assertRaises(MaterializationError):
            analyze_csv_bytes("2024-06", make_payload(omit=missing))

    def test_owner_url_is_pinned_to_frozen_commit(self):
        url = raw_url("data/budget/ten_year_budget/annual_fy_2024-06.csv")
        self.assertIn("284a95665f9f2f74ed1f482feb629b43fce323da", url)
        self.assertTrue(
            url.startswith("https://raw.githubusercontent.com/US-CBO/cbo-data/")
        )


if __name__ == "__main__":
    unittest.main()
