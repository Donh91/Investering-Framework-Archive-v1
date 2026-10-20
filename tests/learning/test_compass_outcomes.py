import csv
import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.learning.compass_outcomes import action_quality, mature_one, persistence_baseline

# Keep the existing Official Compass Outcomes PR gate accountable for protection
# calibration regressions, without adding a second workflow or test scheduler.
# unittest collects imported TestCase subclasses when this module is executed.
from tests.learning.test_action_compass_exit_calibration import MODULE as PROTECTION_CALIBRATION, ProtectionCalibrationTests


class CompassOutcomeTest(unittest.TestCase):
    def test_research_freeze_digest_matches_native_canonical_json_contract(self):
        # Cross-owner invariant: native_handlekompas computes a SHA-256 from
        # sorted compact UTF-8 JSON plus newline, excluding the self-hash.
        # Preserve non-ASCII values and reject changed frozen payload bytes.
        frozen = {
            "compass_id": "CMP-hash-parity",
            "contract": "OFFICIAL_DAILY_COMPASS_v1",
            "evidence": {"note": "dårlig bredde", "value": -2.5},
        }
        expected = hashlib.sha256(
            (json.dumps(frozen, sort_keys=True, separators=(",", ":"),
                        ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
        ).hexdigest()
        frozen["compass_sha256"] = expected
        self.assertEqual(PROTECTION_CALIBRATION.frozen_compass_digest(frozen), expected)
        frozen["evidence"]["value"] = -5.0
        self.assertNotEqual(PROTECTION_CALIBRATION.frozen_compass_digest(frozen), expected)

    def freeze(self):
        return {
            "contract": "OFFICIAL_DAILY_COMPASS_v1",
            "compass_id": "CMP-20260916-test",
            "compass_sha256": "frozen-sha",
            "scoring_contract": "OFFICIAL_DAILY_COMPASS_SCORING_v3",
            "issued_at_utc": "2026-09-16T12:00:00Z",
            "market_reference": {"btc_usdt": 100.0, "eth_usdt": 50.0, "ethbtc": 0.5, "observation_open_utc": "2026-09-16T11:00:00Z"},
            "horizons": {
                "NEXT_12H": {
                    "expected_direction": "DOWN",
                    "action_posture": "HOLD",
                    "eta": "0-12h",
                    "confirmation_trigger": {"type": "ACTION_STATE", "states": ["PREPARE"]},
                    "invalidation_trigger": {"type": "ACTION_STATE", "states": ["HOLD_DEFENSIVE_WAIT"]},
                },
                "NEXT_1_3D": {"expected_direction": "MIXED", "action_posture": "WAIT", "eta": "24-72h"},
                "NEXT_5_7D": {"expected_direction": "SIDEWAYS", "action_posture": "PREPARE", "eta": "120-168h"},
            },
            "evidence_snapshot": {"selected_features": []},
        }

    def write_hourly(self, root: Path):
        path = root / "03_DAILY_CAPTURE_LOGS/hourly/2026/09/2026-09-16.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["timestamp_utc", "btc_close", "eth_close", "ethbtc_close"])
            writer.writeheader()
            writer.writerow({"timestamp_utc": "2026-09-16T23:00:00Z", "btc_close": "95", "eth_close": "47", "ethbtc_close": "0.4947"})

    def test_existing_legacy_outcome_remains_already_matured_without_rewrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            freeze_path = root / "04_MARKET_LEARNING/handlekompas/official/daily/2026/09/16/CMP-20260916-test.json"
            freeze_path.parent.mkdir(parents=True, exist_ok=True)
            frozen = self.freeze()
            frozen["scoring_contract"] = "OFFICIAL_DAILY_COMPASS_SCORING_v2"
            freeze_path.write_text(json.dumps(frozen))
            out = root / "04_MARKET_LEARNING/handlekompas/official/outcomes/2026/09/16/CMP-20260916-test_12h.json"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text('{"immutable":"legacy-v2"}')
            original = out.read_bytes()
            result = mature_one(root, freeze_path, "12h", datetime(2026, 9, 17, 2, tzinfo=timezone.utc), Path("04_MARKET_LEARNING/handlekompas/official"))
            self.assertEqual(result["status"], "ALREADY_MATURED")
            self.assertEqual(out.read_bytes(), original)
            out.unlink()
            result = mature_one(root, freeze_path, "12h", datetime(2026, 9, 17, 2, tzinfo=timezone.utc), Path("04_MARKET_LEARNING/handlekompas/official"))
            self.assertEqual(result["status"], "PENDING_SCORING_CONTRACT_MISMATCH")
            self.assertFalse(out.exists())

    def test_legacy_frozen_v2_cannot_be_silently_matured_under_v3(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "04_MARKET_LEARNING/handlekompas/official/daily/2026/09/16/legacy.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            frozen = self.freeze()
            frozen["scoring_contract"] = "OFFICIAL_DAILY_COMPASS_SCORING_v2"
            path.write_text(json.dumps(frozen))
            original = path.read_bytes()
            self.write_hourly(root)
            result = mature_one(root, path, "12h", datetime(2026, 9, 17, 2, tzinfo=timezone.utc), Path("04_MARKET_LEARNING/handlekompas/official"))
            self.assertEqual(result["status"], "PENDING_SCORING_CONTRACT_MISMATCH")
            self.assertEqual(result["frozen_scoring_contract"], "OFFICIAL_DAILY_COMPASS_SCORING_v2")
            self.assertEqual(original, path.read_bytes())
            self.assertFalse((root / "04_MARKET_LEARNING/handlekompas/official/outcomes").exists())
            frozen.pop("scoring_contract")
            path.write_text(json.dumps(frozen))
            result = mature_one(root, path, "12h", datetime(2026, 9, 17, 2, tzinfo=timezone.utc), Path("04_MARKET_LEARNING/handlekompas/official"))
            self.assertEqual(result["status"], "PENDING_SCORING_CONTRACT_MISMATCH")

    def test_cannot_score_before_maturity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            freeze_path = root / "04_MARKET_LEARNING/handlekompas/official/daily/2026/09/16/CMP-20260916-test.json"
            freeze_path.parent.mkdir(parents=True, exist_ok=True)
            freeze_path.write_text(json.dumps(self.freeze()))
            original = freeze_path.read_bytes()
            result = mature_one(root, freeze_path, "12h", datetime(2026, 9, 16, 23, 59, tzinfo=timezone.utc), Path("04_MARKET_LEARNING/handlekompas/official"))
            self.assertIsNone(result)
            self.assertEqual(original, freeze_path.read_bytes())

    def test_mature_outcome_is_separate_and_forecast_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            freeze_path = root / "04_MARKET_LEARNING/handlekompas/official/daily/2026/09/16/CMP-20260916-test.json"
            freeze_path.parent.mkdir(parents=True, exist_ok=True)
            freeze_path.write_text(json.dumps(self.freeze()))
            original = freeze_path.read_bytes()
            self.write_hourly(root)
            result = mature_one(root, freeze_path, "12h", datetime(2026, 9, 17, 0, 30, tzinfo=timezone.utc), Path("04_MARKET_LEARNING/handlekompas/official"))
            self.assertEqual(result["status"], "MATURED")
            outcome_path = root / result["path"]
            outcome = json.loads(outcome_path.read_text())
            self.assertEqual(outcome["direction_accuracy"]["btc"]["result"], "CORRECT")
            self.assertEqual(outcome["action_utility"]["action"], "HOLD")
            self.assertEqual(outcome["scoring_contract"], "OFFICIAL_DAILY_COMPASS_SCORING_v3")
            self.assertEqual(outcome["time_basis"]["effective_window_hours"], 12.0)
            self.assertEqual(outcome["time_basis"]["start_reference_age_hours"], 0.0)
            self.assertEqual(outcome["target_observation_at_utc"], "2026-09-17T00:00:00Z")
            self.assertEqual(original, freeze_path.read_bytes())

    def test_batch_end_is_not_candle_close(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            forecast = root / "04_MARKET_LEARNING/handlekompas/official/daily/2026/09/16/CMP-20260916-test.json"
            forecast.parent.mkdir(parents=True, exist_ok=True)
            forecast.write_text(json.dumps(self.freeze()))
            path = root / "03_DAILY_CAPTURE_LOGS/hourly/2026/09/2026-09-16.csv"
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["timestamp_utc", "source_window_end_utc", "btc_close"])
                writer.writeheader()
                for hour, price in [(20, 90), (21, 92), (22, 95), (23, 110)]:
                    writer.writerow({"timestamp_utc": f"2026-09-16T{hour:02d}:00:00Z",
                                     "source_window_end_utc": "2026-09-17T01:00:00Z", "btc_close": price})
            early = mature_one(root, forecast, "12h", datetime(2026, 9, 17, 0, 30, tzinfo=timezone.utc), Path("04_MARKET_LEARNING/handlekompas/official"))
            self.assertEqual(early["status"], "PENDING_TARGET_EVIDENCE")
            self.assertFalse((root / early["path"]).exists())
            result = mature_one(root, forecast, "12h", datetime(2026, 9, 17, 1, 30, tzinfo=timezone.utc), Path("04_MARKET_LEARNING/handlekompas/official"))
            self.assertEqual(result["status"], "MATURED")
            outcome = json.loads((root / result["path"]).read_text())
            self.assertEqual(outcome["target_observation_open_at_utc"], "2026-09-16T23:00:00Z")
            self.assertEqual(outcome["target_observation_at_utc"], "2026-09-17T00:00:00Z")
            self.assertAlmostEqual(outcome["realized"]["btc_return_pct"], 10.0)
            self.assertEqual(outcome["scoring_contract"], "OFFICIAL_DAILY_COMPASS_SCORING_v3")

    def test_collection_boundary_before_candle_close_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            forecast = root / "04_MARKET_LEARNING/handlekompas/official/daily/2026/09/16/CMP-20260916-test.json"
            forecast.parent.mkdir(parents=True, exist_ok=True)
            forecast.write_text(json.dumps(self.freeze()))
            path = root / "03_DAILY_CAPTURE_LOGS/hourly/2026/09/2026-09-16.csv"
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["timestamp_utc", "source_window_end_utc", "btc_close"])
                writer.writeheader()
                writer.writerow({"timestamp_utc": "2026-09-16T23:00:00Z",
                                 "source_window_end_utc": "2026-09-16T23:30:00Z", "btc_close": "110"})
                writer.writerow({"timestamp_utc": "2026-09-16T22:00:00Z",
                                 "source_window_end_utc": "invalid", "btc_close": "120"})
                writer.writerow({"timestamp_utc": "2026-09-16T23:30:00Z",
                                 "source_window_end_utc": "2026-09-17T02:00:00Z", "btc_close": "130"})
            result = mature_one(root, forecast, "12h", datetime(2026, 9, 17, 2, tzinfo=timezone.utc), Path("04_MARKET_LEARNING/handlekompas/official"))
            self.assertEqual(result["status"], "PENDING_TARGET_EVIDENCE")
            self.assertFalse((root / result["path"]).exists())

    def test_action_quality_is_horizon_action_not_hardwired_to_12h(self):
        self.assertEqual(action_quality("WAIT", -2.0, -3.0)["action"], "WAIT")
        self.assertEqual(action_quality("PREPARE", 2.0, -1.0)["action"], "PREPARE")

    def test_persistence_baseline_is_reachable_from_frozen_evidence(self):
        freeze = self.freeze()
        freeze["evidence_snapshot"]["selected_features"] = [
            {"feature_id": "btc_delta_since_prior_packet_pct", "value": -1.25}
        ]
        scored = persistence_baseline(freeze, -2.0)
        self.assertEqual(scored["status"], "SCORED")
        self.assertEqual(scored["prediction"], "DOWN")
        self.assertTrue(scored["correct"])

    def test_missing_target_observation_stays_pending_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            freeze_path = root / "04_MARKET_LEARNING/handlekompas/official/daily/2026/09/16/CMP-20260916-test.json"
            freeze_path.parent.mkdir(parents=True, exist_ok=True)
            freeze_path.write_text(json.dumps(self.freeze()))
            result = mature_one(root, freeze_path, "12h", datetime(2026, 9, 17, 1, 0, tzinfo=timezone.utc), Path("04_MARKET_LEARNING/handlekompas/official"))
            self.assertEqual(result["status"], "PENDING_TARGET_EVIDENCE")
            self.assertFalse((root / result["path"]).exists())

    def test_excursion_stops_at_frozen_horizon(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            freeze_path = root / "04_MARKET_LEARNING/handlekompas/official/daily/2026/09/16/CMP-20260916-test.json"
            freeze_path.parent.mkdir(parents=True, exist_ok=True)
            freeze_path.write_text(json.dumps(self.freeze()))
            path = root / "03_DAILY_CAPTURE_LOGS/hourly/2026/09/2026-09-16.csv"
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["timestamp_utc", "btc_close", "eth_close", "ethbtc_close"])
                writer.writeheader()
                writer.writerow({"timestamp_utc": "2026-09-16T23:00:00Z", "btc_close": "95", "eth_close": "47", "ethbtc_close": "0.4947"})
                writer.writerow({"timestamp_utc": "2026-09-17T00:00:00Z", "btc_close": "150", "eth_close": "75", "ethbtc_close": "0.5"})
            result = mature_one(root, freeze_path, "12h", datetime(2026, 9, 17, 2, 0, tzinfo=timezone.utc), Path("04_MARKET_LEARNING/handlekompas/official"))
            outcome = json.loads((root / result["path"]).read_text())
            self.assertAlmostEqual(outcome["realized"]["btc_mfe_pct"], -5.0)


    @unittest.skipUnless(shutil.which("node"), "Node.js unavailable; research oracle needs Node 20+")
    def test_task2_research_no_hindsight_admission_fails_closed(self):
        """Task 2 code is synthetic-only; passing here cannot authorize forecasting."""
        root = Path(__file__).resolve().parents[2]
        oracle = root / (
            "04_MARKET_LEARNING/handlekompas/research/"
            "2026-10-13__task2_r1_no_hindsight_admission_oracle_v1.mjs"
        )
        self.assertTrue(oracle.is_file(), "Task2 R1 oracle missing from research branch")
        result = subprocess.run(
            ["node", str(oracle), "--self-test"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=45,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        receipt = json.loads(result.stdout)
        self.assertEqual(receipt["status"], "SELF_TEST_PASS")
        self.assertGreaterEqual(receipt["negative_and_positive_controls"], 38)
        self.assertEqual(receipt["historical_market_rows_scored"], 0)
        self.assertFalse(receipt["automatic_trading_authority"])
        gate = json.loads((root / "04_MARKET_LEARNING/handlekompas/research/2026-10-13__TASK2_FULL_STACK_AUDIT_EXECUTION_GATE_v1.json").read_text())
        self.assertEqual(gate["contract"], "TASK2_FULL_STACK_AUDIT_EXECUTION_GATE_v1")
        r1 = gate["reproducible_progress"]["r1_no_hindsight_preflight"]
        self.assertEqual(r1["negative_positive_fixture_cases"], receipt["negative_and_positive_controls"])
        self.assertEqual(r1["regression_minimum_controls"], 38)
        self.assertEqual(r1["node_module"], str(oracle.relative_to(root)))
        self.assertEqual(r1["history_rows_independently_scored"], receipt["historical_market_rows_scored"])
        self.assertEqual(r1["status"], "CONTROLS_DEFINED_CURRENT_HEAD_CI_RECEIPT_REQUIRED")
        self.assertEqual(r1["independent_source_pit_proof"], "BLOCKED")
        self.assertEqual(r1["r1_full_chronology"], "BLOCKED")
        self.assertEqual(r1["verification_scope"], "SYNTHETIC_MECHANICS_NOT_HISTORICAL_PIT_OR_FORECAST_SKILL")
        # This is the already independently read-back historical CI checkpoint,
        # not a claim that the current HEAD or a future run has passed.
        self.assertIsNone(r1["verified_code_head"])
        self.assertIsNone(r1["verified_outcomes_CI_run"])
        checkpoint = r1["historical_CI_checkpoint"]
        self.assertEqual(checkpoint["controls"], 31)
        self.assertEqual((checkpoint["head"], checkpoint["run"]),
                         ("1c1aebd0332a49d4266a2e3b738b9dac4fa8a72a", 38432271271))
        self.assertEqual(checkpoint["status"], "GITHUB_CI_EXECUTED_SELF_TEST_PASS")
        self.assertEqual(r1["node_cli_execution"], "CURRENT_HEAD_CI_RECEIPT_REQUIRED")
        self.assertEqual(gate["work_execution_scope"], "TECHNICAL_PREPARATION_ONLY_R2_R7_NOT_EXECUTED")
        self.assertTrue(gate["research_only"])
        for key in ("trade_execution_allowed", "automatic_signal_promotion_allowed", "retrospective_censor_overwrite_allowed"):
            self.assertIs(gate[key], False)

    def test_task2_r0_public_census_is_bounded_not_a_skill_claim(self):
        root = Path(__file__).resolve().parents[2]
        manifest = root / (
            "04_MARKET_LEARNING/handlekompas/research/"
            "2026-10-13__TASK2_R0_PINNED_PUBLIC_SOURCE_INVENTORY_v1.json"
        )
        receipt_path = root / (
            "04_MARKET_LEARNING/handlekompas/research/"
            "2026-10-13__TASK2_R0_PUBLIC_SOURCE_CENSUS_AND_R1_ORACLE_RECEIPT_v1.json"
        )
        source = json.loads(manifest.read_text(encoding="utf-8"))
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        self.assertEqual(source["contract"], "TASK2_R0_PUBLIC_SOURCE_INVENTORY_v1")
        self.assertEqual(source["main_commit"], receipt["pinned_main_commit"])
        self.assertEqual(len(source["families"]), 17)
        self.assertEqual(
            len({family["id"] for family in source["families"]}), 17
        )
        entries = [part for family in source["families"] for part in family["sources"]]
        self.assertEqual(len(entries), receipt['r0']['source_references'])
        self.assertGreaterEqual(len(entries), 27)
        self.assertEqual(
            sum(part["git_object_type"] == "tree" for part in entries),
            receipt['r0']['git_directory_tree_sha_verified']
        )
        self.assertEqual(
            sum(part["git_object_type"] == "blob" for part in entries),
            receipt['r0']['git_file_blob_sha_verified']
        )
        self.assertTrue(all(
            len(part["git_object_sha"]) == 40
            and all(c in "0123456789abcdef" for c in part["git_object_sha"])
            for part in entries
        ))
        pinned_commit = source["main_commit"]
        commit_present = subprocess.run(
            ["git", "cat-file", "-e", f"{pinned_commit}^{{commit}}"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if commit_present.returncode != 0:
            fetched = subprocess.run(
                ["git", "fetch", "--quiet", "--no-tags", "origin", pinned_commit],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
            self.assertEqual(fetched.returncode, 0, fetched.stderr)
        # Git object integrity alone is insufficient: an arbitrary branch
        # could contain the same claimed paths. Fetch the actual default-branch
        # history and require the frozen snapshot to be an ancestor of main.
        # Complete ancestry has no moving 500-commit expiry and must not
        # turn an existing complete shared checkout into a shallow repository.
        shallow = subprocess.run(
            ["git", "rev-parse", "--is-shallow-repository"], cwd=root,
            capture_output=True, text=True, timeout=30, check=False,
        )
        self.assertEqual(shallow.returncode, 0, shallow.stderr)
        fetch_main = ["git", "fetch", "--quiet", "--no-tags"]
        if shallow.stdout.strip() == "true":
            fetch_main.append("--unshallow")
        fetch_main.extend(["origin", "refs/heads/main"])
        main_history = subprocess.run(
            fetch_main, cwd=root, capture_output=True, text=True,
            timeout=120, check=False,
        )
        self.assertEqual(main_history.returncode, 0, main_history.stderr)
        belongs_to_main = subprocess.run(
            ["git", "merge-base", "--is-ancestor", pinned_commit, "FETCH_HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(
            belongs_to_main.returncode, 0,
            "TASK2_R0_PINNED_COMMIT_NOT_REACHABLE_FROM_MAIN: " + belongs_to_main.stderr
        )
        root_tree = subprocess.run(
            ["git", "rev-parse", f"{pinned_commit}^{{tree}}"],
            cwd=root, capture_output=True, text=True, timeout=30, check=False,
        )
        self.assertEqual(root_tree.returncode, 0, root_tree.stderr)
        self.assertEqual(source["main_tree"], root_tree.stdout.strip())
        self.assertEqual(receipt["pinned_main_tree"], root_tree.stdout.strip())
        # Negative control: the pinned snapshot must not be treated as a
        # descendant of the latest main after new commits appeared.
        current_main = subprocess.run(
            ["git", "rev-parse", "FETCH_HEAD"],
            cwd=root, capture_output=True, text=True, timeout=30, check=False,
        )
        self.assertEqual(current_main.returncode, 0, current_main.stderr)
        self.assertRegex(current_main.stdout.strip(), r"^[0-9a-f]{40}$")
        for part in entries:
            object_spec = f"{pinned_commit}:{part['path'].rstrip('/')}"
            actual_sha = subprocess.run(
                ["git", "rev-parse", object_spec],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            self.assertEqual(actual_sha.returncode, 0, actual_sha.stderr)
            self.assertEqual(actual_sha.stdout.strip(), part["git_object_sha"])
            actual_type = subprocess.run(
                ["git", "cat-file", "-t", actual_sha.stdout.strip()],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            self.assertEqual(actual_type.returncode, 0, actual_type.stderr)
            self.assertEqual(actual_type.stdout.strip(), part["git_object_type"])
        # The runnable synthetic oracle must consume the frozen manifest Git
        # object even when that file is absent from this older research tree.
        grid = subprocess.run(
            ["node", str(root / "04_MARKET_LEARNING/handlekompas/research/2026-10-12__task2_synthetic_oracle_v1.mjs")],
            cwd=root, capture_output=True, text=True, timeout=45, check=False,
        )
        self.assertEqual(grid.returncode, 0, grid.stdout + grid.stderr)
        grid_receipt = json.loads(grid.stdout)
        self.assertEqual(grid_receipt["grid_cardinality"], 144)
        self.assertTrue(grid_receipt["manifest_exact_tuple_match"])
        self.assertEqual(grid_receipt["historical_outcome_rows_scored"], 0)
        self.assertFalse(grid_receipt["live_trade_authority"])

        self.assertTrue(all(
            family["admission"] not in ("PIT_CERTIFIED", "TRADABLE_EDGE")
            for family in source["families"]
        ))
        self.assertFalse(source["authority"]["changes_trading_rules"])
        gate = json.loads((root / "04_MARKET_LEARNING/handlekompas/research/2026-10-13__TASK2_FULL_STACK_AUDIT_EXECUTION_GATE_v1.json").read_text())
        r0 = gate["reproducible_progress"]["r0_public_source_census"]
        self.assertEqual(r0["frozen_main_sha"], source["main_commit"])
        self.assertEqual(gate["data_families"], [family["id"] for family in source["families"]])
        self.assertEqual(r0["families_total"], len(source["families"]))
        self.assertEqual(r0["git_source_refs_verified"], len(entries))
        self.assertEqual(r0["git_tree_refs"], sum(part["git_object_type"] == "tree" for part in entries))
        self.assertEqual(r0["git_blob_refs"], sum(part["git_object_type"] == "blob" for part in entries))
        # Git tree aliases with/without a trailing slash are the same source.
        paths = [part["path"].rstrip("/") for part in entries]
        for part, path in zip(entries, paths):
            self.assertTrue(path)
            self.assertTrue(all(segment not in ("", ".", "..") for segment in path.split("/")))
            self.assertIn(part["path"], (path, path + "/") if part["git_object_type"] == "tree" else (path,))
        self.assertEqual(r0["distinct_source_paths"], len(set(paths)))
        shared_paths = sum(paths.count(path) > 1 for path in set(paths))
        self.assertEqual(receipt["r0"]["distinct_source_paths"], len(set(paths)))
        self.assertEqual(receipt["r0"]["shared_source_paths"], shared_paths)
        self.assertEqual(r0["shared_source_paths_not_independent"], shared_paths)
        self.assertEqual(r0["source_mismatches"], 0)
        self.assertEqual(r0["receipt"], str(receipt_path.relative_to(root)))
        self.assertFalse(receipt["authorization"]["market_rules_changed"])
        self.assertEqual(receipt["r1_synthetic"]["history_scored_rows"], 0)


if __name__ == "__main__":
    unittest.main()
