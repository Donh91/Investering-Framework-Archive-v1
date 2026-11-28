"""Synthetic custody tests only; no historical or Round 3 outcomes."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from kompas_live_memory_capture import capture, store, FLAGS

ISSUED = "2026-11-25T20:25:26Z"
OBSERVED = "2026-11-25T20:49:00Z"


def packet(**changes):
    doc = {"contract": "KOMPAS_LIVE_PATH_v1", "authority": FLAGS.copy(),
           "generated_at_utc": ISSUED, "status": "OK",
           "assets": {"BTC": {"status": "OK"}, "ETH": {"status": "OK"}}}
    doc.update(changes)
    doc["path_sha256"] = hashlib.sha256(json.dumps(
        doc, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()).hexdigest()
    return json.dumps(doc, indent=1).encode()


class CaptureTests(unittest.TestCase):
    def test_receipt_never_grants_scoring(self):
        raw = packet()
        result = capture(raw, OBSERVED)
        self.assertEqual(result["source_bytes_sha256"], hashlib.sha256(raw).hexdigest())
        for key in ("publication_authenticated", "pit_admitted", "scoring_authorized"):
            self.assertIs(result[key], False)

    def test_no_rewrite_and_same_clock_conflict(self):
        with tempfile.TemporaryDirectory() as root:
            raw = packet()
            path, status = store(root, raw, OBSERVED)
            self.assertEqual(status, "CREATED")
            original = path.read_bytes()
            self.assertEqual(store(root, raw, "2026-11-26T00:00:00Z"), (path, "ALREADY_CAPTURED"))
            changed = packet(extra="changed")
            conflict, state = store(root, changed, OBSERVED)
            self.assertEqual(state, "CONFLICT")
            self.assertEqual(conflict.name, path.stem + ".conflict-" +
                             hashlib.sha256(changed).hexdigest()[:16] + ".json")
            retained = conflict.read_bytes()
            self.assertEqual(json.loads(retained)["source_bytes_sha256"],
                             hashlib.sha256(changed).hexdigest())
            self.assertEqual(store(root, changed, "2026-11-26T00:00:00Z"),
                             (conflict, "CONFLICT_ALREADY_CAPTURED"))
            self.assertEqual(conflict.read_bytes(), retained)
            self.assertEqual(path.read_bytes(), original)
            conflict.write_text("{}")
            with self.assertRaises((ValueError, KeyError)):
                store(root, changed, OBSERVED)
            self.assertEqual(conflict.read_text(), "{}")
            self.assertEqual(path.read_bytes(), original)

    def test_corruption_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            raw = packet()
            path, _ = store(root, raw, OBSERVED)
            obj = json.loads(path.read_bytes())
            obj["pit_admitted"] = True
            path.write_text(json.dumps(obj))
            with self.assertRaises(ValueError):
                store(root, raw, OBSERVED)

    def test_boolean_integer_substitution_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            raw = packet()
            path, _ = store(root, raw, OBSERVED)
            obj = json.loads(path.read_bytes())
            obj["pit_admitted"] = 0
            path.write_text(json.dumps(obj))
            with self.assertRaises(ValueError):
                store(root, raw, OBSERVED)

    def test_invalid_packets(self):
        for raw in (packet(contract="OTHER"),
                    packet(authority={**FLAGS, "trading": True}),
                    packet(status="UNAVAILABLE"),
                    packet().replace(b'"OK"', b'"PARTIAL"', 1),
                    b'{"contract":"a","contract":"b"}',
                    b'{"x":NaN}'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                capture(raw, OBSERVED)

    def test_future_and_naive_clock(self):
        for clock in ("2026-11-25T20:00:00Z", "2026-11-25T21:00:00"):
            with self.assertRaises(ValueError):
                capture(packet(), clock)

    def test_unavailable_is_preserved(self):
        raw = packet(status="UNAVAILABLE",
                     assets={"BTC": {"status": "UNAVAILABLE"}, "ETH": {"status": "UNAVAILABLE"}})
        self.assertEqual(capture(raw, OBSERVED)["source_status"], "UNAVAILABLE")


    def test_wrong_seal_rejected(self):
        doc = json.loads(packet())
        doc["path_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "source seal mismatch"):
            capture(json.dumps(doc).encode(), OBSERVED)

    def test_integer_authority_flag_rejected(self):
        for key, flag in FLAGS.items():
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "unexpected source authority"):
                capture(packet(authority={**FLAGS, key: int(flag)}), OBSERVED)


if __name__ == "__main__":
    unittest.main()
