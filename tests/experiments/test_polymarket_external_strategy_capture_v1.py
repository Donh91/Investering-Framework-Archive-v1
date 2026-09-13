import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).parents[2]
SCRIPT = ROOT / "scripts" / "experiments" / "polymarket_external_strategy_capture_v1.py"
WALLET = "0x" + "1" * 40


def load_module():
    spec = importlib.util.spec_from_file_location("polymarket_external_strategy_capture_v1", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class PolymarketExternalStrategyCaptureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()

    def test_identity_requires_one_exact_profile_and_crosscheck(self):
        def fake_get(base, path, params, timeout=30):
            if path == "/public-search":
                return ({"profiles": [{"name": "EdgeOnchain", "proxyWallet": WALLET}]}, "search-url")
            if path == "/public-profile":
                return ({"name": "EdgeOnchain", "proxyWallet": WALLET}, "profile-url")
            raise AssertionError(path)

        with patch.object(self.module, "get_json", fake_get):
            identity, raw = self.module.resolve_profile("EdgeOnchain")

        self.assertEqual(identity["proxy_wallet"], WALLET)
        self.assertEqual(identity["status"], "IDENTITY_RESOLVED_SINGLE_EXACT_MATCH")
        self.assertEqual(raw["profiles"][0]["name"], "EdgeOnchain")

    def test_ambiguous_profile_fails_closed(self):
        def fake_get(base, path, params, timeout=30):
            return (
                {
                    "profiles": [
                        {"name": "EdgeOnchain", "proxyWallet": WALLET},
                        {"pseudonym": "EdgeOnchain", "proxyWallet": "0x" + "2" * 40},
                    ]
                },
                "search-url",
            )

        with patch.object(self.module, "get_json", fake_get):
            with self.assertRaisesRegex(RuntimeError, "exactly one"):
                self.module.resolve_profile("EdgeOnchain")

    def test_profile_wallet_mismatch_fails_closed(self):
        def fake_get(base, path, params, timeout=30):
            if path == "/public-search":
                return ({"profiles": [{"name": "EdgeOnchain", "proxyWallet": WALLET}]}, "search-url")
            if path == "/public-profile":
                return ({"name": "EdgeOnchain", "proxyWallet": "0x" + "2" * 40}, "profile-url")
            raise AssertionError(path)

        with patch.object(self.module, "get_json", fake_get):
            with self.assertRaisesRegex(RuntimeError, "identity mismatch"):
                self.module.resolve_profile("EdgeOnchain")

    def test_pagination_cap_fails_instead_of_silent_truncation(self):
        def fake_get(base, path, params, timeout=30):
            return ([{"offset": params["offset"]}, {"offset": params["offset"] + 1}], "url")

        with tempfile.TemporaryDirectory() as td, patch.object(self.module, "get_json", fake_get):
            with self.assertRaisesRegex(RuntimeError, "pagination cap"):
                self.module.page_endpoint(
                    out=Path(td),
                    name="test",
                    path="/test",
                    wallet=WALLET,
                    limit=2,
                    max_offset=2,
                )

    def test_pagination_composes_until_short_page(self):
        calls = []

        def fake_get(base, path, params, timeout=30):
            calls.append(params["offset"])
            return (([1, 2] if params["offset"] == 0 else [3]), "url")

        with tempfile.TemporaryDirectory() as td, patch.object(self.module, "get_json", fake_get):
            rows, pages = self.module.page_endpoint(
                out=Path(td),
                name="test",
                path="/test",
                wallet=WALLET,
                limit=2,
                max_offset=10,
            )

        self.assertEqual(rows, [1, 2, 3])
        self.assertEqual(calls, [0, 2])
        self.assertEqual(len(pages), 2)


if __name__ == "__main__":
    unittest.main()
