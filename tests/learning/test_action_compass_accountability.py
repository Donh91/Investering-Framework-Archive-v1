from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "learning" / "action_compass_accountability.py"


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def sha(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def capture(timestamp, btc, eth):
    return {
        "contract": "DAILY_LIVE_ANCHOR_INDEX_v3",
        "captured_at_utc": timestamp,
        "run_id": "synthetic-test",
        "market_metrics": {
            "derivatives": {
                "BTC-USDT-SWAP": {"mark_price": {"mark_price": btc}},
                "ETH-USDT-SWAP": {"mark_price": {"mark_price": eth}},
            }
        },
    }


class AccountabilityHarness(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.name", "test"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.repo, check=True)
        marker = self.repo / "02_DATA_PING/runtime/ACTION_COMPASS_ACCOUNTABILITY_ACTIVATION_v1.json"
        marker.parent.mkdir(parents=True)
        marker.write_text(json.dumps({"contract": "ACTION_COMPASS_ACCOUNTABILITY_ACTIVATION_v1"}))
        subprocess.run(["git", "add", str(marker.relative_to(self.repo))], cwd=self.repo, check=True)
        activation_env = dict(os.environ, GIT_AUTHOR_DATE="2026-08-26T14:00:00Z", GIT_COMMITTER_DATE="2026-08-26T14:00:00Z")
        subprocess.run(["git", "commit", "-q", "-m", "activation"], cwd=self.repo, check=True, env=activation_env)
        self.activation_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.repo, text=True).strip()
        self.receipts = self.repo / "research/framework_memory/action_compass_receipts"
        self.outcomes = self.repo / "research/framework_memory/action_compass_outcomes"
        self.evidence = self.repo / "03_DAILY_CAPTURE_LOGS/captures"
        self.baseline_path = self.evidence / "2026/08/26/140000_test.json"
        self.baseline_path.parent.mkdir(parents=True)
        self.baseline = capture("2026-08-26T14:00:00Z", 100.0, 50.0)
        self.baseline_path.write_bytes(canonical(self.baseline))
        subprocess.run(["git", "add", str(self.baseline_path.relative_to(self.repo))], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "canonical"], cwd=self.repo, check=True)
        self.canonical_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.repo, text=True).strip()
        self.candidate_path = self.repo / "candidate.json"

    def candidate(self, **overrides):
        value = {
            "contract": "THREE_HORIZON_ACTION_COMPASS_RECEIPT_CANDIDATE_v1_1",
            "input_packet_sha256": "1" * 64,
            "input_binding_status": "OPAQUE_SOURCE_HASH_ASSERTED",
            "input_contract": "DATA_PING_TEST_v1",
            "source_reference": "OPAQUE:test-packet-1",
            "source_timestamp_utc": "2026-08-26T14:00:00Z",
            "canonical_repository": "Donh91/Investering-Framework-Archive-v1",
            "canonical_commit_sha": self.canonical_sha,
            "owner_contract": "02_DATA_PING/protocols/2026-08-25__three-horizon-action-compass-output-contract-v1__canonical.md",
            "interpreted_at_utc": "2026-08-26T14:05:00Z",
            "producer_model": "test-model",
            "action_compass": {
                "contract": "THREE_HORIZON_ACTION_COMPASS_v1_1",
                "as_of_utc": "2026-08-26T14:00:00Z",
                "near_term": {
                    "horizon_hours": 24,
                    "valid_from_utc": "2026-08-26T14:05:00Z",
                    "valid_until_utc": "2026-08-27T14:05:00Z",
                    "action": "WAIT",
                },
                "next_window": {"window_start_date": "2026-08-31", "window_end_date": "2026-09-02", "action": "PREPARE_BUY"},
                "altcoin_compass": {
                    "horizon_days": 28,
                    "through_date": "2026-09-23",
                    "state": "DISTRIBUTION",
                    "action": "HOLD",
                    "warning": "DISTRIBUTION_WARNING",
                },
            },
            "data_quality_tags": ["COMPLETE"],
            "rationale_tags": ["BREADTH_CONFLICT", "NO_EXIT_AUTHORITY"],
            "baseline_observer": {
                "status": "BOUND",
                "evidence_path": str(self.baseline_path.relative_to(self.repo)),
                "evidence_sha256": sha(self.baseline),
                "captured_at_utc": "2026-08-26T14:00:00Z",
                "series": [
                    {
                        "series_id": "BTC_USDT_MARK_PRICE",
                        "metric_path": "market_metrics.derivatives.BTC-USDT-SWAP.mark_price.mark_price",
                    },
                    {
                        "series_id": "ETH_USDT_MARK_PRICE",
                        "metric_path": "market_metrics.derivatives.ETH-USDT-SWAP.mark_price.mark_price",
                    },
                ],
            },
            "portfolio_execution": False,
        }
        value.update(overrides)
        return value

    def persist(self, candidate=None):
        self.candidate_path.write_bytes(canonical(candidate or self.candidate()))
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "persist",
                "--candidate",
                str(self.candidate_path),
                "--receipt-root",
                str(self.receipts),
                "--repo-root",
                str(self.repo),
                "--expected-canonical-commit",
                self.canonical_sha,
                "--activation-utc",
                "2026-08-26T14:00:00Z",
                "--activation-commit-sha",
                self.activation_sha,
            ],
            capture_output=True,
            text=True,
        )

    def receipt_path(self):
        paths = list(self.receipts.rglob("ACR-*.json"))
        self.assertEqual(len(paths), 1)
        return paths[0]

    def write_capture(self, name, timestamp, btc, eth):
        path = self.evidence / "2026/08/27" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(canonical(capture(timestamp, btc, eth)))

    def mature(self, now="2026-09-02T15:00:00Z"):
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "mature",
                "--receipt-root",
                str(self.receipts),
                "--evidence-root",
                str(self.evidence),
                "--output-root",
                str(self.outcomes),
                "--repo-root",
                str(self.repo),
                "--now-utc",
                now,
            ],
            capture_output=True,
            text=True,
        )


class PersistenceTests(AccountabilityHarness):
    def test_persists_one_privacy_bounded_receipt_with_orthogonal_warning_and_action(self):
        result = self.persist()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "PERSISTED")
        receipt = json.loads(self.receipt_path().read_text())
        self.assertEqual(receipt["action_compass"]["altcoin_compass"]["warning"], "DISTRIBUTION_WARNING")
        self.assertEqual(receipt["action_compass"]["altcoin_compass"]["action"], "HOLD")
        self.assertFalse(receipt["portfolio_execution"])
        text = json.dumps(receipt).lower()
        for forbidden in ("conversation", "holding", "quantity", "account_data"):
            self.assertNotIn(forbidden, text)

    def test_replay_is_duplicate_noop_even_if_producer_metadata_changes(self):
        first = self.persist()
        self.assertEqual(first.returncode, 0, first.stderr)
        original = self.receipt_path().read_bytes()
        replay = self.candidate(producer_model="another-model", interpreted_at_utc="2026-08-26T14:10:00Z")
        replay["action_compass"]["near_term"]["valid_from_utc"] = "2026-08-26T14:10:00Z"
        second = self.persist(replay)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(json.loads(second.stdout)["status"], "DUPLICATE_NOOP")
        self.assertEqual(self.receipt_path().read_bytes(), original)
        self.assertEqual(len(list(self.receipts.rglob("*.json"))), 1)

    def test_concurrent_persistence_never_overwrites_or_duplicates(self):
        self.candidate_path.write_bytes(canonical(self.candidate()))
        command = [
            sys.executable,
            str(SCRIPT),
            "persist",
            "--candidate",
            str(self.candidate_path),
            "--receipt-root",
            str(self.receipts),
            "--repo-root",
            str(self.repo),
            "--expected-canonical-commit",
            self.canonical_sha,
            "--activation-utc",
            "2026-08-26T14:00:00Z",
            "--activation-commit-sha",
            self.activation_sha,
        ]
        first = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        second = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        first_out, first_err = first.communicate()
        second_out, second_err = second.communicate()
        self.assertEqual(first.returncode, 0, first_err)
        self.assertEqual(second.returncode, 0, second_err)
        statuses = {json.loads(first_out)["status"], json.loads(second_out)["status"]}
        self.assertEqual(statuses, {"PERSISTED", "DUPLICATE_NOOP"})
        receipt = json.loads(self.receipt_path().read_text())
        self.assertEqual(receipt["contract"], "THREE_HORIZON_ACTION_COMPASS_RECEIPT_v1_1")
        self.assertEqual(len(list(self.receipts.rglob("*.json"))), 1)

    def test_private_or_portfolio_shape_is_rejected(self):
        candidate = self.candidate()
        candidate["position_quantity"] = 12.0
        result = self.persist(candidate)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("private_field_forbidden", result.stderr)
        self.assertFalse(self.receipts.exists())

    def test_rationale_tag_cannot_encode_private_position_semantics(self):
        candidate = self.candidate(rationale_tags=["POSITION_SIZE_LARGE"])
        result = self.persist(candidate)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("rationale_tag_private_semantics_forbidden", result.stderr)

    def test_historical_backfill_is_rejected(self):
        candidate = self.candidate(source_timestamp_utc="2026-08-26T13:59:59Z")
        result = self.persist(candidate)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("historical_backfill_forbidden", result.stderr)

    def test_bad_baseline_hash_is_rejected_before_persistence(self):
        candidate = self.candidate()
        candidate["baseline_observer"]["evidence_sha256"] = "f" * 64
        result = self.persist(candidate)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("baseline_evidence_hash_mismatch", result.stderr)

    def test_repo_source_hash_is_verified_at_the_bound_commit(self):
        packet_path = self.repo / "packets/source.json"
        packet_path.parent.mkdir()
        packet = {"contract": "DATA_PING_TEST_v1", "freeze_utc": "2026-08-26T14:00:00Z", "value": 7}
        packet_path.write_bytes(canonical(packet))
        subprocess.run(["git", "add", str(packet_path.relative_to(self.repo))], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "packet"], cwd=self.repo, check=True)
        self.canonical_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.repo, text=True).strip()
        candidate = self.candidate(
            input_packet_sha256=sha(packet),
            input_binding_status="VERIFIED_REPO_FILE",
            source_reference=str(packet_path.relative_to(self.repo)),
        )
        result = self.persist(candidate)
        self.assertEqual(result.returncode, 0, result.stderr)
        bad = self.candidate(
            input_packet_sha256="2" * 64,
            input_binding_status="VERIFIED_REPO_FILE",
            source_reference=str(packet_path.relative_to(self.repo)),
        )
        result = self.persist(bad)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("input_packet_hash_mismatch", result.stderr)

    def test_repository_validator_accepts_the_single_immutable_receipt(self):
        self.assertEqual(self.persist().returncode, 0)
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "validate-repository",
                "--receipt-root",
                str(self.receipts),
                "--repo-root",
                str(self.repo),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"duplicate_count": 0, "receipt_count": 1, "status": "PASS"})

    def test_activation_is_derived_from_the_marker_commit_without_override(self):
        self.candidate_path.write_bytes(canonical(self.candidate()))
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "persist",
                "--candidate",
                str(self.candidate_path),
                "--receipt-root",
                str(self.receipts),
                "--repo-root",
                str(self.repo),
                "--expected-canonical-commit",
                self.canonical_sha,
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        receipt = json.loads(self.receipt_path().read_text())
        self.assertEqual(receipt["implementation_activation"]["activation_commit_sha"], self.activation_sha)
        self.assertEqual(receipt["implementation_activation"]["activation_utc"], "2026-08-26T14:00:00Z")


class OutcomeTests(AccountabilityHarness):
    def setUp(self):
        super().setUp()
        self.assertEqual(self.persist().returncode, 0)
        self.write_capture("200000.json", "2026-08-26T20:00:00Z", 90.0, 55.0)
        self.write_capture("100000.json", "2026-08-27T10:00:00Z", 110.0, 45.0)
        self.write_capture("141000.json", "2026-08-27T14:10:00Z", 105.0, 60.0)
        seven_day = self.evidence / "2026/09/02/141000.json"
        seven_day.parent.mkdir(parents=True, exist_ok=True)
        seven_day.write_bytes(canonical(capture("2026-09-02T14:10:00Z", 120.0, 70.0)))

    def test_matures_continuous_24h_and_7d_sidecars_without_hit_miss_labels(self):
        result = self.mature()
        self.assertEqual(result.returncode, 0, result.stderr)
        summary = json.loads(result.stdout)
        self.assertEqual(summary["matured"], 2)
        paths = sorted(self.outcomes.rglob("*.json"))
        self.assertEqual([path.name for path in paths], ["24H.json", "7D.json"])
        day = json.loads(next(path for path in paths if path.name == "24H.json").read_text())
        self.assertEqual(day["missing_series"], [])
        self.assertEqual(day["decision_snapshot"]["lane_3_warning"], "DISTRIBUTION_WARNING")
        self.assertEqual(day["decision_snapshot"]["lane_3_action"], "HOLD")
        self.assertFalse(day["decision_snapshot"]["warning_implies_action"])
        btc = next(row for row in day["series_outcomes"] if row["series_id"] == "BTC_USDT_MARK_PRICE")
        self.assertEqual(btc["terminal_return_pct"], 5.0)
        self.assertEqual(btc["max_drawdown_from_start_pct"], -10.0)
        self.assertEqual(btc["max_upside_from_start_pct"], 10.0)
        self.assertEqual(btc["baseline_lag_hours"], round(5 / 60, 6))
        self.assertEqual(btc["terminal_lag_hours"], round(5 / 60, 6))
        self.assertEqual(btc["normalized_full_exit_counterfactual"]["capital_preserved_pct"], 0.0)
        self.assertEqual(btc["normalized_full_exit_counterfactual"]["upside_foregone_pct"], 5.0)
        lane_three = next(row for row in btc["action_counterfactuals"] if row["lane"] == "ALTCOIN_COMPASS")
        self.assertEqual(lane_three["action"], "HOLD")
        self.assertEqual(lane_three["status"], "NOT_EVALUABLE_WITHOUT_INVENTED_PORTFOLIO_SEMANTICS")
        self.assertIsNone(lane_three["capital_preserved_pct"])
        rendered = json.dumps(day)
        self.assertNotIn('"HIT"', rendered)
        self.assertNotIn('"MISS"', rendered)
        self.assertFalse(day["portfolio_execution"])

    def test_maturation_is_idempotent_and_does_not_rewrite_sidecars(self):
        first = self.mature()
        self.assertEqual(first.returncode, 0, first.stderr)
        before = {path: path.read_bytes() for path in self.outcomes.rglob("*.json")}
        second = self.mature(now="2026-09-03T15:00:00Z")
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(json.loads(second.stdout)["existing"], 2)
        self.assertEqual({path: path.read_bytes() for path in self.outcomes.rglob("*.json")}, before)

    def test_unmatured_horizons_remain_pending_without_files(self):
        result = self.mature(now="2026-08-27T15:00:00Z")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(list(self.outcomes.rglob("24H.json")))
        self.assertFalse(list(self.outcomes.rglob("7D.json")))
        self.assertFalse(list(self.outcomes.rglob("30D.json")))

    def test_partial_terminal_evidence_stays_pending_until_lag_window_can_complete(self):
        partial_path = self.evidence / "2026/08/27/141000.json"
        partial = capture("2026-08-27T14:10:00Z", 105.0, 60.0)
        del partial["market_metrics"]["derivatives"]["ETH-USDT-SWAP"]
        partial_path.write_bytes(canonical(partial))
        first = self.mature(now="2026-08-27T15:00:00Z")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertFalse(list(self.outcomes.rglob("24H.json")))
        self.write_capture("160000.json", "2026-08-27T16:00:00Z", 106.0, 61.0)
        second = self.mature(now="2026-08-27T17:00:00Z")
        self.assertEqual(second.returncode, 0, second.stderr)
        sidecar = json.loads(next(self.outcomes.rglob("24H.json")).read_text())
        self.assertEqual(sidecar["status"], "MATURED")
        self.assertEqual(len(sidecar["series_outcomes"]), 2)

    def test_existing_decision_miss_auditor_prioritizes_action_compass_sidecars(self):
        self.assertEqual(self.mature().returncode, 0)
        generic = self.repo / "generic"
        generic.mkdir()
        for index in range(40):
            (generic / f"{index:02d}.json").write_text(json.dumps({"outcome": "generic", "index": index}))
        spec = importlib.util.spec_from_file_location("adaptive_decision_miss_auditor", ROOT / "scripts/api_agent/adaptive_decision_miss_auditor.py")
        module = importlib.util.module_from_spec(spec)
        self.assertIsNotNone(spec.loader)
        spec.loader.exec_module(module)
        selected = module.docs([generic, self.repo / "research/framework_memory"], 3)
        self.assertTrue(selected)
        self.assertIn("action_compass_outcomes", selected[0]["path"])


if __name__ == "__main__":
    unittest.main()
