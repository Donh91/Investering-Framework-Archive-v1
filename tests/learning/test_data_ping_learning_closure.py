from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BRIDGE = REPO / "scripts/data_ping/accepted_data_ping_bridge.py"
RATIFIER = REPO / "scripts/learning/ratify_forecast_candidate.py"
LEDGER = REPO / "scripts/learning/build_model_calibration_ledger.py"


def canon(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(value):
    return hashlib.sha256(canon(value)).hexdigest()


def run(*args, check=True):
    return subprocess.run([sys.executable, *map(str, args)], text=True, capture_output=True, check=check)


class DataPingLearningClosureTests(unittest.TestCase):
    def packet(self, snapshot_id="DPI-20260829-001", price=100.0):
        return {
            "contract": "ACCEPTED_DATA_PING_PACKET_v1",
            "snapshot_id": snapshot_id,
            "freeze_utc": "2026-08-29T08:30:00Z",
            "source_health": {"github": "PASS"},
            "market_metrics": {"btc_usd": price},
            "framework_interpretation": "DEFERRED_TO_MAIN_FRAMEWORK",
            "acceptance_status": "ACCEPTED",
            "authority": {"portfolio_action": False, "model_weight_change": False, "canonical_promotion": False},
        }

    def bridge_cmd(self, root):
        return [
            BRIDGE,
            "--inbox", root / "inbox",
            "--accepted-root", root / "accepted",
            "--receipt-root", root / "receipts",
            "--rejected-root", root / "rejected",
            "--processed-root", root / "processed",
            "--run-id", "test-run",
        ]

    def test_native_bridge_identity_replay_and_collision(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "inbox").mkdir()
            packet = self.packet()
            (root / "inbox/fresh.json").write_bytes(canon(packet))
            first = run(*self.bridge_cmd(root))
            self.assertEqual(json.loads(first.stdout), {"accepted": 1, "rejected": 0, "replayed": 0})

            accepted = next((root / "accepted").rglob("*.json"))
            sidecar = next((root / "receipts").rglob("*.json"))
            accepted_value = json.loads(accepted.read_text())
            receipt = json.loads(sidecar.read_text())
            packet_hash = digest(packet)
            self.assertEqual(accepted_value, packet)
            self.assertNotIn("bridge_receipt", accepted_value)
            self.assertEqual(digest(accepted_value), packet_hash)
            self.assertEqual(receipt["packet_sha256"], packet_hash)
            self.assertEqual(receipt["packet_identity"], "DPI-" + packet_hash[:24])
            receipt_core = {k: v for k, v in receipt.items() if k != "receipt_sha256"}
            self.assertEqual(receipt["receipt_sha256"], digest(receipt_core))

            accepted_bytes = accepted.read_bytes(); receipt_bytes = sidecar.read_bytes()
            (root / "inbox/replay.json").write_bytes(canon(dict(reversed(list(packet.items())))))
            replay = run(*self.bridge_cmd(root))
            self.assertEqual(json.loads(replay.stdout), {"accepted": 0, "rejected": 0, "replayed": 1})
            self.assertEqual(accepted.read_bytes(), accepted_bytes)
            self.assertEqual(sidecar.read_bytes(), receipt_bytes)

            collision = self.packet(price=101.0)
            (root / "inbox/collision.json").write_bytes(canon(collision))
            failed = run(*self.bridge_cmd(root), check=False)
            self.assertEqual(failed.returncode, 2)
            self.assertEqual(accepted.read_bytes(), accepted_bytes)
            self.assertEqual(sidecar.read_bytes(), receipt_bytes)

    def test_native_replay_fails_closed_when_sidecar_is_missing(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); (root / "inbox").mkdir()
            packet = self.packet(); (root / "inbox/fresh.json").write_bytes(canon(packet))
            run(*self.bridge_cmd(root))
            next((root / "receipts").rglob("*.json")).unlink()
            (root / "inbox/replay.json").write_bytes(canon(packet))
            failed = run(*self.bridge_cmd(root), check=False)
            self.assertEqual(failed.returncode, 2)
            error = json.loads(next((root / "rejected").rglob("*.error.json")).read_text())
            self.assertIn("bridge_receipt_missing_for_native_packet", error["error"])

    def test_legacy_inline_bridge_replay_is_noop_without_backfill(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); (root / "inbox").mkdir()
            packet = self.packet(); freeze = "2026/W35"
            accepted = root / "accepted" / freeze / f"{packet['snapshot_id']}.json"
            accepted.parent.mkdir(parents=True)
            legacy = dict(packet); legacy["bridge_receipt"] = {"contract": "DATA_PING_BRIDGE_RECEIPT_v2", "packet_sha256": digest(packet)}
            accepted.write_bytes(canon(legacy)); before = accepted.read_bytes()
            (root / "inbox/replay.json").write_bytes(canon(packet))
            replay = run(*self.bridge_cmd(root))
            self.assertEqual(json.loads(replay.stdout)["replayed"], 1)
            self.assertEqual(accepted.read_bytes(), before)
            self.assertFalse((root / "receipts").exists())

    def lineage_fixture(self):
        packet_hash = "a" * 64
        receipt = {
            "contract": "THREE_HORIZON_ACTION_COMPASS_RECEIPT_v1_1",
            "receipt_id": "ACR-test-001",
            "input_binding_status": "VERIFIED_REPO_FILE",
            "input_packet_sha256": packet_hash,
            "source_reference": "research/data_ping_bridge/accepted/2026/W35/DPI-20260829-001.json",
            "canonical_repository": "Donh91/Investering-Framework-Archive-v1",
            "canonical_commit_sha": "b" * 40,
            "owner_contract": "02_DATA_PING/protocols/2026-08-25__three-horizon-action-compass-output-contract-v1__canonical.md",
            "portfolio_execution": False,
        }
        lineage = {
            "contract": "DATA_PING_LEARNING_LINEAGE_v1",
            "accepted_packet_sha256": packet_hash,
            "accepted_packet_identity": "DPI-" + packet_hash[:24],
            "accepted_packet_path": receipt["source_reference"],
            "action_compass_receipt_id": receipt["receipt_id"],
            "action_compass_receipt_sha256": digest(receipt),
            "canonical_repository": receipt["canonical_repository"],
            "canonical_commit_sha": receipt["canonical_commit_sha"],
            "owner_contract": receipt["owner_contract"],
        }
        return receipt, lineage

    def test_forecast_lineage_is_validated_and_replay_safe(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); out = root / "frozen"
            receipt, lineage = self.lineage_fixture()
            candidate = {
                "contract": "FORECAST_CANDIDATE_v1", "candidate_id": "fc_test_001", "ratification_status": "PENDING",
                "model": "test", "task": "test", "prompt_sha256": "1" * 64,
                "data_ping_lineage": lineage,
                "candidate": {"metric_path": "market.price", "horizon_days": 1, "direction": "UP", "target_mode": "PCT_MOVE", "threshold_pct": 2.0, "rationale": "test"},
            }
            ratification = {"contract": "FORECAST_RATIFICATION_PACKET_v1", "candidate_id": "fc_test_001", "decision": "RATIFY", "authority": "CHATGPT_FRAMEWORK_OWNER"}
            baseline = {"market": {"price": 100.0}}
            for name, value in (("candidate.json", candidate), ("ratification.json", ratification), ("baseline.json", baseline), ("receipt.json", receipt)):
                (root / name).write_bytes(canon(value))
            cmd = [RATIFIER, "--candidate", root / "candidate.json", "--ratification", root / "ratification.json", "--baseline-evidence", root / "baseline.json", "--output-root", out, "--action-compass-receipt", root / "receipt.json"]
            first = run(*cmd); self.assertEqual(json.loads(first.stdout)["status"], "FROZEN")
            frozen_path = next(out.glob("*.json")); frozen = json.loads(frozen_path.read_text())
            self.assertEqual(frozen["data_ping_lineage"], lineage)
            self.assertFalse(frozen["authority"]["portfolio_action"])
            before = frozen_path.read_bytes()
            replay = run(*cmd); self.assertEqual(json.loads(replay.stdout)["status"], "DUPLICATE_NOOP")
            self.assertEqual(frozen_path.read_bytes(), before)
            tampered = dict(frozen); tampered["direction"] = "DOWN"; frozen_path.write_bytes(canon(tampered))
            collision = run(*cmd, check=False)
            self.assertNotEqual(collision.returncode, 0)
            self.assertIn("FORECAST_ID_COLLISION", collision.stderr + collision.stdout)

    def test_calibration_ledger_carries_packet_lineage_via_hash_bound_forecast(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); forecasts = root / "forecasts"; outcomes = root / "outcomes"; forecasts.mkdir(); outcomes.mkdir()
            _, lineage = self.lineage_fixture()
            forecast = {
                "contract": "FROZEN_FORECAST_v1", "unit_contract_version": "FORECAST_TARGET_UNITS_v2", "forecast_id": "ff_test",
                "metric_path": "market.price", "horizon_days": 1, "model": "test", "task": "test", "prompt_sha256": "1" * 64,
                "data_ping_lineage": lineage,
            }
            outcome = {
                "contract": "MATURED_OUTCOME_v3", "forecast_id": "ff_test", "status": "MATURED", "result": "HIT", "return_pct": 3.0,
                "created_at_utc": "2026-08-30T08:30:00Z", "forecast_sha256": digest(forecast), "evidence_sha256": "c" * 64,
            }
            (forecasts / "ff_test.json").write_bytes(canon(forecast)); (outcomes / "ff_test.json").write_bytes(canon(outcome))
            ledger = root / "ledger.csv"
            result = run(LEDGER, "--forecast-root", forecasts, "--outcome-root", outcomes, "--output", ledger)
            summary = json.loads(result.stdout)
            self.assertEqual(summary["data_ping_lineage_row_count"], 1)
            self.assertEqual(ledger.read_text().splitlines()[0], "scored_at_utc,model,task,prompt_sha256,forecast_id,metric_path,horizon_days,outcome,result,hit,return_pct,forecast_sha256,evidence_sha256")
            lineage_path = Path(summary["data_ping_lineage_output"])
            row = json.loads(lineage_path.read_text().strip())
            self.assertEqual(row["forecast_sha256"], digest(forecast))
            self.assertEqual(row["accepted_packet_sha256"], lineage["accepted_packet_sha256"])
            self.assertEqual(row["accepted_packet_identity"], lineage["accepted_packet_identity"])
            self.assertEqual(row["action_compass_receipt_id"], lineage["action_compass_receipt_id"])
            self.assertEqual(row["action_compass_receipt_sha256"], lineage["action_compass_receipt_sha256"])
            self.assertEqual(row["canonical_commit_sha"], lineage["canonical_commit_sha"])
            self.assertFalse(row["portfolio_execution"])


if __name__ == "__main__":
    unittest.main()
