import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
PATH = ROOT / "scripts/research_sources/validate_research_source_receipt.py"
SPEC = importlib.util.spec_from_file_location("validator", PATH)
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)


def good():
    return {
        "contract": "X",
        "source": "TEST",
        "payload_sha256": "a" * 64,
        "payload_bytes": 10,
        "raw_persisted": False,
        "authority": {
            "binding": False,
            "canonical_acceptance": False,
            "state_change": False,
            "portfolio_action": False,
            "automatic_promotion": False,
        },
    }


class TestReceiptValidator(unittest.TestCase):
    def test_pass(self):
        self.assertEqual(V.validate(good())["status"], "PASS")

    def test_reject_raw_persistence(self):
        doc = good()
        doc["raw_persisted"] = True
        with self.assertRaises(V.ValidationError):
            V.validate(doc)

    def test_reject_authority(self):
        doc = good()
        doc["authority"]["portfolio_action"] = True
        with self.assertRaises(V.ValidationError):
            V.validate(doc)

    def test_reject_bad_hash(self):
        doc = good()
        doc["payload_sha256"] = "x"
        with self.assertRaises(V.ValidationError):
            V.validate(doc)


if __name__ == "__main__":
    unittest.main()
