import unittest
from scripts.research.vix_term_structure_shadow_v1 import features, features_from_fred_captures
from scripts.data_terminal import fred_csv_collector as collector


CUTOFF = "2026-11-24T22:00:00Z"


def fixture():
    days = ["2026-11-19", "2026-11-20", "2026-11-23", "2026-11-24"]
    sessions = [{"date": d, "close_utc": d + "T21:15:00Z"} for d in days]
    rows = [dict(date=d, series=s, value=x, available_at_utc=d + "T21:20:00Z",
                 captured_at_utc=d + "T21:30:00Z", payload_sha256="a" * 64)
            for d, v in zip(days, [20, 30, 25, 22])
            for s, x in [("VIXCLS", v), ("VXVCLS", 25)]]
    return rows, sessions


class TestVix(unittest.TestCase):
    def test_exact_matched_sessions_weekend(self):
        rows, sessions = fixture()
        x = features(rows, sessions, CUTOFF)
        self.assertEqual(x["features"]["vix_3m_ratio"], "0.88")
        self.assertEqual(x["features"]["vix_change_1_session_points"], "-3")
        self.assertEqual(x["features"]["vix_change_3_sessions_points"], "2")
        self.assertFalse(x["features"]["inverted_index_term_structure"])
        self.assertFalse(x["first_known_verified"])
        self.assertIsNone(x["market_signal"])

    def test_missing_duplicate_and_unmatched(self):
        rows, sessions = fixture()
        for bad in (rows[:-1], rows + [rows[0]], rows + [dict(rows[0], date="2026-11-22")]):
            with self.subTest(bad=len(bad)), self.assertRaises(ValueError):
                features(bad, sessions, CUTOFF)

    def test_late_or_preclose(self):
        for key, value in [("available_at_utc", "2026-11-24T21:00:00Z"),
                           ("captured_at_utc", CUTOFF),
                           ("captured_at_utc", "2026-11-24T21:19:00Z"),
                           ("available_at_utc", "2026-11-24T21:20:00")]:
            rows, sessions = fixture(); rows[-1][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                features(rows, sessions, CUTOFF)

    def test_invalid_values_and_digest(self):
        for bad in (0, -1, True, float("nan"), float("inf"), "NaN", "garbage", "1e999"):
            rows, sessions = fixture(); rows[-1]["value"] = bad
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                features(rows, sessions, CUTOFF)
        rows, sessions = fixture(); rows[-1]["payload_sha256"] = "bad"
        with self.assertRaises(ValueError):
            features(rows, sessions, CUTOFF)

    def test_session_order_and_inversion(self):
        rows, sessions = fixture(); rows[-2]["value"] = 35
        self.assertTrue(features(rows, sessions, CUTOFF)["features"]["inverted_index_term_structure"])
        with self.assertRaises(ValueError):
            features(rows, sessions[::-1], CUTOFF)
        with self.assertRaises(ValueError):
            features(rows, sessions, "2026-11-24T21:15:00Z")


class TestFredCaptureBinding(unittest.TestCase):
    def captures(self):
        rows, sessions = fixture()
        captures = []
        for session in sessions:
            day = session["date"]
            values = [r["value"] for r in rows if r["date"] == day]
            payload = f"DATE,VIXCLS,VXVCLS\n{day},{values[0]},{values[1]}\n".encode()
            artifacts = collector.build_artifacts(
                payload=payload, retrieval_timestamp=collector.parse_timestamp(day + "T21:30:00Z"),
                series=("VIXCLS", "VXVCLS"), source_url="FIXTURE", acquisition_mode="FIXTURE",
                stale_after_seconds=604800)
            captures.append({"payload": payload, "receipt": artifacts["receipt"]})
        return captures, sessions

    def rehash(self, receipt):
        receipt["receipt_sha256"] = collector.sha256_bytes(collector.canonical_json_bytes(
            {k: v for k, v in receipt.items() if k != "receipt_sha256"}))

    def test_existing_owner_artifact_to_feature(self):
        captures, sessions = self.captures()
        result = features_from_fred_captures(captures, sessions, CUTOFF)
        self.assertEqual(result["features"]["vix_3m_ratio"], "0.88")
        self.assertEqual(result["raw_to_feature_binding"], "RECOMPUTED_FROM_SUPPLIED_BYTES")
        self.assertFalse(result["first_known_verified"])
        self.assertFalse(result["source_authenticated"])
        self.assertEqual(len(result["owner_receipt_digests"]), 4)

    def test_raw_or_receipt_tampering(self):
        captures, sessions = self.captures()
        captures[-1]["payload"] = captures[-1]["payload"].replace(b",22,", b",99,")
        with self.assertRaisesRegex(ValueError, "fred_capture_digest_mismatch"):
            features_from_fred_captures(captures, sessions, CUTOFF)
        captures, sessions = self.captures()
        captures[-1]["receipt"]["retrieval_timestamp"] = CUTOFF
        with self.assertRaisesRegex(ValueError, "fred_capture_digest_mismatch"):
            features_from_fred_captures(captures, sessions, CUTOFF)

    def test_rehashed_wrong_scope_and_late_clock(self):
        for field, value, reason in (
                ("source_id", "OTHER", "invalid_fred_receipt_scope"),
                ("source_timestamps", {}, "fred_session_mismatch"),
                ("observation_ids", [], "fred_observation_identity_mismatch"),
                ("retrieval_timestamp", CUTOFF, "late_or_inconsistent_observation")):
            captures, sessions = self.captures()
            receipt = captures[-1]["receipt"]
            receipt[field] = value
            self.rehash(receipt)
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, reason):
                features_from_fred_captures(captures, sessions, CUTOFF)

    def test_rehashed_wrong_payload_session(self):
        captures, sessions = self.captures()
        item = captures[-1]
        item["payload"] = item["payload"].replace(b"2026-11-24", b"2026-11-23")
        item["receipt"]["payload_sha256"] = collector.sha256_bytes(item["payload"])
        self.rehash(item["receipt"])
        with self.assertRaisesRegex(ValueError, "fred_payload_session_mismatch"):
            features_from_fred_captures(captures, sessions, CUTOFF)


if __name__ == "__main__":
    unittest.main()
