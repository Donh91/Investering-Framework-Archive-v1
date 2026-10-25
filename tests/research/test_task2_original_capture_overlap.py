import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("overlap", ROOT / "scripts/research/task2_original_capture_overlap.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def fixture():
    result = []
    for capture in ("capture_a", "capture_b"):
        for endpoint in sorted(audit.ENDPOINTS):
            row = {"fundingTime": "1000", "fundingRate": "SYNTHETIC_PRIVATE_SENTINEL"} if "funding" in endpoint else [1000, "SYNTHETIC_PRIVATE_SENTINEL"]
            body = {"code": "0", "data": [row]} if endpoint.endswith("_okx.json") else [row]
            result.append((capture, endpoint, json.dumps(body).encode()))
    return result


class OverlapTests(unittest.TestCase):
    def test_repeated_capture_is_not_an_independent_event(self):
        result = audit.summarize(fixture())
        self.assertEqual((result["raw_row_instances_total"], result["unique_endpoint_timestamp_pairs"], result["repeated_endpoint_timestamp_exposures"]), (18, 9, 9))
        self.assertIsNone(result["independent_event_count"])
        self.assertFalse(result["pit_admitted"])
        self.assertNotIn("SYNTHETIC_PRIVATE_SENTINEL", json.dumps(result))

    def test_changed_payload_is_counted_not_silently_deduplicated(self):
        rows = fixture()
        capture, endpoint, payload = rows[-1]
        rows[-1] = (capture, endpoint, payload.replace(b"SYNTHETIC_PRIVATE_SENTINEL", b"DIFFERENT"))
        self.assertEqual(audit.summarize(rows)["source_payload_change_timestamp_pairs"], 1)

    def test_missing_endpoint_cannot_be_hidden_by_multiplication(self):
        with self.assertRaisesRegex(ValueError, "INCOMPLETE_CAPTURE"):
            audit.summarize(fixture()[:-1])

    def test_duplicate_response_rejected(self):
        rows = fixture()
        with self.assertRaisesRegex(ValueError, "DUPLICATE_RESPONSE"):
            audit.summarize(rows + rows[:1])

    def test_provider_error_rejected(self):
        rows = fixture()
        capture, endpoint, _ = rows[0]
        rows[0] = (capture, endpoint, b'{"code":"500","data":[]}')
        with self.assertRaisesRegex(ValueError, "NOT_SUCCESS"):
            audit.summarize(rows)

    def test_empty_response_rejected(self):
        rows = fixture()
        capture, endpoint, _ = rows[-1]
        rows[-1] = (capture, endpoint, b'[]')
        with self.assertRaisesRegex(ValueError, "EMPTY_OR_INVALID"):
            audit.summarize(rows)

    def test_invalid_clock_rejected(self):
        rows = [(c, e, p.replace(b'1000', b'-100')) for c, e, p in fixture()]
        with self.assertRaisesRegex(ValueError, "TIMESTAMP_INVALID"):
            audit.summarize(rows)

    def test_arbitrary_or_corrupt_package_rejected(self):
        with self.assertRaisesRegex(ValueError, "IDENTITY_MISMATCH"):
            audit.audit(b"not-original")


if __name__ == "__main__":
    unittest.main()
