from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts/data_terminal/fred_csv_collector.py"
SPEC = importlib.util.spec_from_file_location("fred_csv_collector", MODULE_PATH)
collector = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = collector
assert SPEC.loader is not None
SPEC.loader.exec_module(collector)
FIXTURE = Path(__file__).parent / "fixtures/fred_csv_macro_core.csv"


class FredCsvCollectorTests(unittest.TestCase):
    def build(self, fixture: Path = FIXTURE, retrieval: str = "2026-07-19T12:00:00Z", stale_after: int = 604800):
        payload = fixture.read_bytes()
        return collector.build_artifacts(
            payload=payload,
            retrieval_timestamp=collector.parse_timestamp(retrieval),
            series="DGS10",
            source_url="https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10",
            acquisition_mode="FIXTURE",
            stale_after_seconds=stale_after,
        )

    def test_fresh_fixture_passes_with_direct_label_and_false_authority(self):
        artifacts = self.build()
        self.assertEqual(artifacts["source_health"]["status"], "PASS")
        observation = artifacts["snapshot"]["observations"]["DGS10"]
        self.assertEqual(observation["direct_or_derived"], "DIRECT")
        self.assertTrue(all(value is False for value in observation["authority"].values()))

    def test_stale_fixture_is_explicit(self):
        artifacts = self.build(retrieval="2026-08-01T00:00:00Z", stale_after=86400)
        self.assertEqual(artifacts["source_health"]["status"], "STALE")

    def test_missing_value_is_unknown_not_zero(self):
        artifacts = self.build()
        self.assertEqual(artifacts["snapshot"]["missing"], [{"field": "DGS10", "source_date": "2026-07-15", "status": "UNKNOWN"}])
        self.assertNotEqual(artifacts["snapshot"]["observations"]["DGS10"]["value"], 0)

    def test_payload_hash_and_receipt_are_deterministic(self):
        first = self.build()
        second = self.build()
        self.assertEqual(first["receipt"]["payload_sha256"], second["receipt"]["payload_sha256"])
        self.assertEqual(first["receipt"]["receipt_sha256"], second["receipt"]["receipt_sha256"])
        self.assertEqual(collector.canonical_json_bytes(first), collector.canonical_json_bytes(second))

    def test_schema_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.csv"
            bad.write_text("DATE,WRONG\n2026-07-17,1\n", encoding="utf-8")
            with self.assertRaises(collector.CollectorError) as ctx:
                collector.parse_fred_csv(bad.read_bytes(), "DGS10")
            self.assertEqual(ctx.exception.status, "SCHEMA_DRIFT")

    def test_empty_response_is_rejected(self):
        with self.assertRaises(collector.CollectorError) as ctx:
            collector.parse_fred_csv(b"", "DGS10")
        self.assertIn(ctx.exception.status, {"EMPTY_RESPONSE", "SCHEMA_DRIFT"})

    def test_malformed_timestamp_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.csv"
            bad.write_text("DATE,DGS10\n17-07-2026,4.2\n", encoding="utf-8")
            with self.assertRaises(collector.CollectorError) as ctx:
                collector.parse_fred_csv(bad.read_bytes(), "DGS10")
            self.assertEqual(ctx.exception.status, "MALFORMED_TIMESTAMP")

    def test_source_substitution_is_explicitly_false(self):
        health = self.build()["source_health"]
        self.assertEqual(health["source_substitution"], {"used": False, "substitute_source_id": None, "reason": None})

    def test_no_silent_network_fallback(self):
        with mock.patch.object(collector.urllib.request, "urlopen", side_effect=OSError("offline")):
            with self.assertRaises(collector.CollectorError) as ctx:
                collector.fetch_payload("https://example.invalid", timeout=0.1, retries=0, backoff=0)
        self.assertEqual(ctx.exception.status, "NETWORK_ERROR")

    def test_contract_and_registry_json_parse(self):
        contract = json.loads((ROOT / "02_DATA_PING/data_terminal/contracts/data_terminal_contracts.schema.json").read_text())
        registry = json.loads((ROOT / "02_DATA_PING/data_terminal/source_registry/fred_csv_macro_core.json").read_text())
        self.assertIn("$defs", contract)
        self.assertEqual(registry["primary_source"]["source_id"], "FRED_CSV_MACRO_CORE")
        self.assertFalse(registry["authority"]["binding"])

    def test_cli_writes_five_sanitized_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, str(MODULE_PATH), "--fixture", str(FIXTURE), "--retrieval-timestamp", "2026-07-19T12:00:00Z", "--output-dir", tmp],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            paths = [path for path in Path(tmp).rglob("*.json")]
            self.assertEqual(len(paths), 5)
            for path in paths:
                data = json.loads(path.read_text())
                self.assertNotIn("secret", json.dumps(data).lower())

    def test_static_shadow_examples_are_consistent(self):
        shadow = ROOT / "02_DATA_PING/data_terminal/runtime/shadow"
        source_health = json.loads((shadow / "source_health_fixture.json").read_text())
        terminal = json.loads((shadow / "latest_terminal_state.json").read_text())
        handoff = json.loads((shadow / "latest_data_ping_handoff.json").read_text())
        self.assertEqual(source_health["payload_sha256"], terminal["source_health"][0]["payload_sha256"])
        self.assertEqual(handoff["authority"], collector.AUTHORITY)
        self.assertEqual(terminal["authority"], collector.AUTHORITY)


if __name__ == "__main__":
    unittest.main()
