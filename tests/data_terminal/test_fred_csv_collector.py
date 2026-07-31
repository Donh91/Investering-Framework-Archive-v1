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
SERIES = collector.DEFAULT_SERIES


class FredCsvCollectorTests(unittest.TestCase):
    def build(self, fixture: Path = FIXTURE, retrieval: str = "2026-07-19T12:00:00Z", stale_after: int = 604800):
        return collector.build_artifacts(
            payload=fixture.read_bytes(),
            retrieval_timestamp=collector.parse_timestamp(retrieval),
            series=SERIES,
            source_url="https://fred.stlouisfed.org/graph/fredgraph.csv?id=" + ",".join(SERIES),
            acquisition_mode="FIXTURE",
            stale_after_seconds=stale_after,
        )

    def test_all_required_series_are_present_and_direct(self):
        artifacts = self.build()
        self.assertEqual(artifacts["receipt"]["status"], "PASS")
        self.assertEqual(set(artifacts["snapshot"]["observations"]), set(SERIES))
        for observation in artifacts["snapshot"]["observations"].values():
            self.assertEqual(observation["direct_or_derived"], "DIRECT")
            self.assertTrue(all(value is False for value in observation["authority"].values()))

    def test_series_units_are_explicit(self):
        observations = self.build()["snapshot"]["observations"]
        self.assertEqual(observations["DGS2"]["unit"], "PERCENT")
        self.assertEqual(observations["DGS10"]["unit"], "PERCENT")
        self.assertEqual(observations["DTWEXBGS"]["unit"], "INDEX")
        self.assertEqual(observations["VIXCLS"]["unit"], "INDEX")

    def test_aggregate_stale_is_fail_closed(self):
        artifacts = self.build(retrieval="2026-08-01T00:00:00Z", stale_after=86400)
        self.assertEqual(artifacts["receipt"]["status"], "STALE")
        self.assertTrue(all(row["status"] == "STALE" for row in artifacts["source_health"]["series"]))

    def test_missing_values_are_unknown_not_zero(self):
        artifacts = self.build()
        missing = artifacts["snapshot"]["missing"]
        self.assertEqual({item["field"] for item in missing}, {"DGS2", "DGS10", "VIXCLS"})
        self.assertTrue(all(item["status"] == "UNKNOWN" for item in missing))
        self.assertTrue(all(obs["value"] != 0 for obs in artifacts["snapshot"]["observations"].values()))

    def test_payload_hash_receipt_and_run_are_deterministic(self):
        first = self.build()
        second = self.build()
        self.assertEqual(first["receipt"]["payload_sha256"], second["receipt"]["payload_sha256"])
        self.assertEqual(first["receipt"]["receipt_sha256"], second["receipt"]["receipt_sha256"])
        self.assertEqual(collector.canonical_json_bytes(first), collector.canonical_json_bytes(second))

    def test_schema_drift_is_rejected_when_one_owner_column_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.csv"
            bad.write_text("DATE,DGS2,DGS10,DTWEXBGS\n2026-07-17,3.8,4.2,121.7\n", encoding="utf-8")
            with self.assertRaises(collector.CollectorError) as ctx:
                collector.parse_fred_csv(bad.read_bytes(), SERIES)
            self.assertEqual(ctx.exception.status, "SCHEMA_DRIFT")

    def test_duplicate_timestamp_is_rejected(self):
        payload = b"DATE,DGS2,DGS10,DTWEXBGS,VIXCLS\n2026-07-17,1,2,3,4\n2026-07-17,1,2,3,4\n"
        with self.assertRaises(collector.CollectorError) as ctx:
            collector.parse_fred_csv(payload, SERIES)
        self.assertEqual(ctx.exception.status, "DUPLICATE_TIMESTAMP")

    def test_malformed_timestamp_is_rejected(self):
        payload = b"DATE,DGS2,DGS10,DTWEXBGS,VIXCLS\n17-07-2026,1,2,3,4\n"
        with self.assertRaises(collector.CollectorError) as ctx:
            collector.parse_fred_csv(payload, SERIES)
        self.assertEqual(ctx.exception.status, "MALFORMED_TIMESTAMP")

    def test_no_silent_network_fallback(self):
        with mock.patch.object(collector.urllib.request, "urlopen", side_effect=OSError("offline")):
            with self.assertRaises(collector.CollectorError) as ctx:
                collector.fetch_payload("https://example.invalid", timeout=0.1, retries=0, backoff=0)
        self.assertEqual(ctx.exception.status, "NETWORK_ERROR")

    def test_write_manifest_and_readback_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            paths = collector.write_artifacts(output, self.build(), raw_payload=FIXTURE.read_bytes())
            self.assertEqual(len(paths), 7)
            result = collector.verify_artifact_readback(output)
            self.assertEqual(result["status"], "PASS")
            manifest = json.loads((output / "artifact_manifest.json").read_text())
            self.assertEqual(manifest["member_count"], 6)
            self.assertTrue(any(item["path"].startswith("raw/") for item in manifest["members"]))

    def test_readback_detects_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            collector.write_artifacts(output, self.build(), raw_payload=FIXTURE.read_bytes())
            (output / "source_health.json").write_text("{}\n", encoding="utf-8")
            self.assertEqual(collector.verify_artifact_readback(output)["status"], "FAIL")

    def test_cli_writes_owner_artifacts_and_passes_readback(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run([sys.executable, str(MODULE_PATH), "--fixture", str(FIXTURE), "--retrieval-timestamp", "2026-07-19T12:00:00Z", "--output-dir", tmp], cwd=ROOT, text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["readback"]["status"], "PASS")
            self.assertTrue((Path(tmp) / "artifact_manifest.json").is_file())

    def test_contract_and_registry_json_parse(self):
        contract = json.loads((ROOT / "02_DATA_PING/data_terminal/contracts/data_terminal_contracts.schema.json").read_text())
        registry = json.loads((ROOT / "02_DATA_PING/data_terminal/source_registry/fred_csv_macro_core.json").read_text())
        self.assertIn("$defs", contract)
        self.assertEqual(registry["primary_source"]["source_id"], "FRED_CSV_MACRO_CORE")
        self.assertFalse(registry["authority"]["binding"])

    def test_manual_workflow_remains_dispatch_only_and_read_only(self):
        workflow = (ROOT / ".github/workflows/data-terminal-shadow-manual.yml").read_text()
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("contents: read", workflow)
        self.assertIn("upload-artifact@v4", workflow)
        self.assertNotIn("schedule:", workflow)
        self.assertNotIn("cron:", workflow)
        self.assertNotIn("git push", workflow)
        self.assertNotIn("issues: write", workflow)


if __name__ == "__main__":
    unittest.main()
