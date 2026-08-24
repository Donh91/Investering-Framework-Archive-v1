from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT / "scripts/research"))
sys.path.insert(0, str(PROJECT / "scripts/data_terminal"))

import core_shared_row_materializer as materializer
import prospective_evidence_controller as controller
import shared_row_outcome_owner as outcome_owner
import top100_breadth_owner_collector as breadth_owner


def isoz(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class FixtureRepo:
    def __init__(
        self,
        case: unittest.TestCase,
        *,
        hourly_count: int = 168,
        remove_hour_index: int | None = None,
        duplicate_hour_index: int | None = None,
        breadth_after_cutoff: bool = False,
        btcd_after_cutoff: bool = False,
        btcd_reordered: bool = False,
        btcd_duplicate: bool = False,
        btcd_provider: str = "CoinMarketCap",
    ):
        self.temp = tempfile.TemporaryDirectory()
        case.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.boundary = datetime(2026, 8, 1, 0, 0, tzinfo=timezone.utc)
        self.hourly_start = datetime(2026, 8, 2, 0, 0, tzinfo=timezone.utc)
        self.floor = datetime(2026, 8, 9, 1, 0, tzinfo=timezone.utc)
        self.observation = datetime(2026, 8, 9, 1, 30, tzinfo=timezone.utc)
        self.lab = self.repo / "06_RESEARCH_LAB/shared_row_model_tournament_v1"
        self.hourly = self.repo / "03_DAILY_CAPTURE_LOGS/hourly/2026/08/fixture.csv"
        self.breadth = self.repo / "03_DAILY_CAPTURE_LOGS/breadth_rich/2026/08/2026-08-09"
        self.btcd = self.repo / "03_DAILY_CAPTURE_LOGS/btc_d_cmc/latest/BTC_D_DIRECT_SOURCE_DAILY_2023_CURRENT.csv"
        self._create_contracts()
        self._write_hourly(
            count=hourly_count,
            remove_index=remove_hour_index,
            duplicate_index=duplicate_hour_index,
        )
        self._write_breadth(after_cutoff=breadth_after_cutoff)
        self._write_btcd(
            after_cutoff=btcd_after_cutoff,
            reordered=btcd_reordered,
            duplicate=btcd_duplicate,
            provider=btcd_provider,
        )
        self._init_git()
        self._configure_modules(case)

    def _create_contracts(self) -> None:
        self.lab.mkdir(parents=True)
        contract = json.loads(
            (PROJECT / "06_RESEARCH_LAB/shared_row_model_tournament_v1/CORE_FAMILY_PROSPECTIVE_CONTRACT_v1.json").read_text()
        )
        contract["prospective_eligibility_start"] = isoz(self.floor)
        contract["prospective_eligibility_status"] = "ACTIVE_POST_REPAIR_FLOOR"
        contract["prospective_activation"]["collection_state"] = materializer.ACTIVE_COLLECTION_STATE
        contract["prospective_activation"]["implementation_merge_commit"] = "TEST_BOUNDARY"
        contract["prospective_activation"]["post_repair_source_capture_not_before_utc"] = isoz(self.boundary)
        (self.lab / "CORE_FAMILY_PROSPECTIVE_CONTRACT_v1.json").write_text(json.dumps(contract, indent=2) + "\n")

        freeze = json.loads(
            (PROJECT / "06_RESEARCH_LAB/shared_row_model_tournament_v1/TRANSFORM_FREEZE_REGISTRY.json").read_text()
        )
        freeze["core_activation_rule"]["collection_state"] = materializer.ACTIVE_COLLECTION_STATE
        freeze["core_activation_rule"]["containment_floor_sentinel"] = False
        freeze["core_activation_rule"]["prospective_eligibility_start"] = isoz(self.floor)
        for family in freeze["families"]:
            if family["family_id"] in controller.CORE_FAMILIES:
                family["prospective_eligibility_start"] = isoz(self.floor)
                family["repair_state"] = "P0_REPAIRED_AWAITING_ACTIVATION_OR_ACTIVE"
        (self.lab / "TRANSFORM_FREEZE_REGISTRY.json").write_text(json.dumps(freeze, indent=2) + "\n")
        (self.lab / "03_CANDIDATE_REGISTRY.json").write_text(
            (PROJECT / "06_RESEARCH_LAB/shared_row_model_tournament_v1/03_CANDIDATE_REGISTRY.json").read_text()
        )
        data = self.lab / "data"
        data.mkdir()
        for name in ["PROSPECTIVE_SHARED_ROW_LEDGER.csv", "OUTCOME_DETAIL_LEDGER.csv"]:
            header = (PROJECT / "06_RESEARCH_LAB/shared_row_model_tournament_v1/data" / name).read_text().splitlines()[0]
            (data / name).write_text(header + "\n")
        fnp_header = (PROJECT / "06_RESEARCH_LAB/shared_row_model_tournament_v1/14_DIVERGENCE_FNP_LEDGER.csv").read_text().splitlines()[0]
        (self.lab / "14_DIVERGENCE_FNP_LEDGER.csv").write_text(fnp_header + "\n")
        (data / "CATALYST_LEDGER.csv").write_text("catalyst_evidence_id,tag_type,timestamp_or_period\n")

    @staticmethod
    def _hour_fields() -> list[str]:
        return [
            "timestamp_utc",
            "source_window_end_utc",
            "btc_close",
            "eth_close",
            "ethbtc_close",
            "spot_status",
        ]

    def _hour_rows(self, count: int) -> list[dict[str, str]]:
        output = []
        for index in range(count):
            timestamp = self.hourly_start + timedelta(hours=index)
            output.append(
                {
                    "timestamp_utc": isoz(timestamp),
                    "source_window_end_utc": isoz(timestamp + timedelta(hours=1)),
                    "btc_close": f"{100000 + index:.2f}",
                    "eth_close": f"{3000 + index / 10:.2f}",
                    "ethbtc_close": f"{0.031 + index / 1000000:.8f}",
                    "spot_status": "PASS",
                }
            )
        return output

    def _write_hourly(
        self,
        *,
        count: int,
        remove_index: int | None,
        duplicate_index: int | None,
    ) -> None:
        self.hourly.parent.mkdir(parents=True)
        rows = self._hour_rows(count)
        if remove_index is not None:
            rows.pop(remove_index)
        if duplicate_index is not None:
            rows.insert(duplicate_index + 1, dict(rows[duplicate_index]))
        with self.hourly.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=self._hour_fields())
            writer.writeheader()
            writer.writerows(rows)

    def _write_breadth(self, *, after_cutoff: bool) -> None:
        rows = [
            {
                "id": f"asset-{index}",
                "symbol": f"a{index}",
                "name": f"Asset {index}",
                "market_cap": 1_000_000 - index,
                "current_price": 100 + index,
                "price_change_percentage_24h": 1 if index < 60 else -1,
            }
            for index in range(100)
        ]
        retrieval = self.observation + timedelta(minutes=1) if after_cutoff else self.floor - timedelta(minutes=45)
        breadth_owner.run(json.dumps(rows).encode(), self.breadth, isoz(retrieval))

    def _write_btcd(self, *, after_cutoff: bool, reordered: bool, duplicate: bool, provider: str) -> None:
        self.btcd.parent.mkdir(parents=True)
        dates = [("2026-08-06", 58.0), ("2026-08-07", 57.0), ("2026-08-08", 57.5)]
        if reordered:
            dates = [dates[1], dates[0], dates[2]]
        if duplicate:
            dates = [dates[0], dates[0], dates[2]]
        verified = self.observation + timedelta(minutes=1) if after_cutoff else self.floor - timedelta(minutes=40)
        fields = [
            "date_utc",
            "btc_d_close",
            "source_symbol",
            "source_provider",
            "source_convention",
            "settled_timezone",
            "source_timestamp",
            "source_verified_timestamp",
            "print_status",
            "data_quality",
            "source_status",
        ]
        with self.btcd.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for date, value in dates:
                writer.writerow(
                    {
                        "date_utc": date,
                        "btc_d_close": value,
                        "source_symbol": "CMC_GLOBAL_METRICS_BTC_DOMINANCE",
                        "source_provider": provider,
                        "source_convention": "CMC_DIRECT_SOURCE_CONVENTION: fixture",
                        "settled_timezone": "UTC",
                        "source_timestamp": f"{date}T00:00:00Z",
                        "source_verified_timestamp": isoz(verified),
                        "print_status": "SETTLED_COMPLETE_DATE",
                        "data_quality": "PASS",
                        "source_status": "PUBLIC_SOURCE_BACKED",
                    }
                )

    def _git(self, *args: str) -> str:
        return subprocess.check_output(["git", *args], cwd=self.repo, text=True).strip()

    def _init_git(self) -> None:
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        self._git("config", "user.email", "fixture@example.invalid")
        self._git("config", "user.name", "P0 Fixture")
        self._git("add", "-A")
        self._git("commit", "-q", "-m", "fixture sources")

    def commit_path(self, path: Path, message: str) -> None:
        self._git("add", path.relative_to(self.repo).as_posix())
        self._git("commit", "-q", "-m", message)

    def _configure_modules(self, case: unittest.TestCase) -> None:
        values = {
            materializer: {
                "REPO_ROOT": self.repo,
                "ROOT": self.lab,
                "CONTRACT": self.lab / "CORE_FAMILY_PROSPECTIVE_CONTRACT_v1.json",
                "FREEZE": self.lab / "TRANSFORM_FREEZE_REGISTRY.json",
                "CATALYST": self.lab / "data/CATALYST_LEDGER.csv",
                "LEDGER": self.lab / "data/PROSPECTIVE_SHARED_ROW_LEDGER.csv",
                "HOURLY": self.hourly.parent.parent.parent,
                "BREADTH_ROOT": self.repo / "03_DAILY_CAPTURE_LOGS/breadth_rich",
                "BTCD": self.btcd,
            },
            controller: {
                "REPO_ROOT": self.repo,
                "ROOT": self.lab,
                "LEDGER": self.lab / "data/PROSPECTIVE_SHARED_ROW_LEDGER.csv",
                "FNP": self.lab / "14_DIVERGENCE_FNP_LEDGER.csv",
                "FREEZE": self.lab / "TRANSFORM_FREEZE_REGISTRY.json",
                "CONTRACT": self.lab / "CORE_FAMILY_PROSPECTIVE_CONTRACT_v1.json",
                "REG": self.lab / "03_CANDIDATE_REGISTRY.json",
            },
            outcome_owner: {
                "REPO_ROOT": self.repo,
                "ROOT": self.lab,
                "ROWS": self.lab / "data/PROSPECTIVE_SHARED_ROW_LEDGER.csv",
                "DETAIL": self.lab / "data/OUTCOME_DETAIL_LEDGER.csv",
                "HOURLY": self.hourly.parent.parent.parent,
                "CONTRACT": self.lab / "CORE_FAMILY_PROSPECTIVE_CONTRACT_v1.json",
            },
        }
        for module, mapping in values.items():
            for name, value in mapping.items():
                old = getattr(module, name)
                setattr(module, name, value)
                case.addCleanup(setattr, module, name, old)

    def build(self) -> dict:
        return materializer.build(isoz(self.observation))

    def append_future_hours(self, *, alter_baseline: bool = False) -> None:
        with self.hourly.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        if alter_baseline:
            rows[-1]["ethbtc_close"] = "0.05000000"
        last = datetime.fromisoformat(rows[-1]["timestamp_utc"].replace("Z", "+00:00"))
        for index in range(1, 28):
            timestamp = last + timedelta(hours=index)
            rows.append(
                {
                    "timestamp_utc": isoz(timestamp),
                    "source_window_end_utc": isoz(timestamp + timedelta(hours=1)),
                    "btc_close": f"{100500 + index:.2f}",
                    "eth_close": f"{3050 + index / 10:.2f}",
                    "ethbtc_close": f"{0.0315 + index / 1000000:.8f}",
                    "spot_status": "PASS",
                }
            )
        with self.hourly.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=self._hour_fields())
            writer.writeheader()
            writer.writerows(rows)
        self.commit_path(self.hourly, "append future outcome hours")


class SharedRowP0IntegrityTests(unittest.TestCase):
    def assert_rejected(self, result: dict, expected_reason: str) -> None:
        self.assertEqual(result["status"], "NOT_ELIGIBLE", result)
        self.assertEqual(result["reason"], expected_reason, result)

    def test_valid_production_shape_binds_all_sources_and_ingests_once(self):
        fixture = FixtureRepo(self)
        result = fixture.build()
        self.assertEqual(result["status"], "ELIGIBLE_SHARED_ROW", result)
        row = result["row"]
        self.assertEqual(row["observation_timestamp_utc"], isoz(fixture.observation))
        self.assertEqual(row["information_cutoff_utc"], isoz(fixture.observation))
        self.assertEqual(row["row_integrity_contract"], materializer.ROW_INTEGRITY_CONTRACT)
        manifest = json.loads(row["source_binding_manifest"])
        self.assertEqual(set(manifest["families"]), controller.CORE_FAMILIES)
        self.assertEqual(manifest["families"]["ETHBTC_PERSISTENCE"]["sample_count"], 168)
        validated, _ = controller.validate_payload(dict(row))
        self.assertEqual(validated["event_id"], row["event_id"])
        row_path = fixture.repo / "row.json"
        row_path.write_text(json.dumps(row) + "\n")
        first = controller.ingest(row_path)
        self.assertGreater(first["divergences_frozen"], 0)
        with self.assertRaisesRegex(ValueError, "event_id already frozen"):
            controller.ingest(row_path)

    def test_exact_168_hour_contract_rejects_sparse_gap_and_duplicate(self):
        cases = [
            ({"hourly_count": 1}, "ETHBTC_EXACT_168_HOURS_MISSING"),
            ({"hourly_count": 169, "remove_hour_index": 80}, "ETHBTC_168_HOUR_CONTINUITY_GAP"),
            ({"duplicate_hour_index": 80}, "ETHBTC_DUPLICATE_TIMESTAMP"),
        ]
        for kwargs, reason in cases:
            with self.subTest(reason=reason):
                fixture = FixtureRepo(self, **kwargs)
                self.assert_rejected(fixture.build(), reason)

    def test_future_owner_timestamps_are_rejected(self):
        breadth = FixtureRepo(self, breadth_after_cutoff=True)
        self.assert_rejected(breadth.build(), "BREADTH_IMMUTABLE_DATED_OWNER_MISSING")
        btcd = FixtureRepo(self, btcd_after_cutoff=True)
        self.assert_rejected(btcd.build(), "BTCD_THREE_SETTLED_PRINTS_AVAILABLE_BY_CUTOFF_MISSING")

    def test_btcd_reorder_duplicate_and_provider_removal_are_rejected(self):
        cases = [
            ({"btcd_reordered": True}, "BTCD_FILE_ORDER_NOT_STRICTLY_CHRONOLOGICAL"),
            ({"btcd_duplicate": True}, "BTCD_DUPLICATE_SETTLED_DATE"),
            ({"btcd_provider": ""}, "BTCD_SETTLED_ROW_INVALID"),
        ]
        for kwargs, reason in cases:
            with self.subTest(reason=reason):
                fixture = FixtureRepo(self, **kwargs)
                self.assert_rejected(fixture.build(), reason)

    def test_hash_provider_commit_and_candidate_label_tampering_are_rejected(self):
        fixture = FixtureRepo(self)
        row = fixture.build()["row"]

        def changed(mutator):
            candidate = json.loads(json.dumps(row))
            manifest = json.loads(candidate["source_binding_manifest"])
            mutator(candidate, manifest)
            candidate["source_binding_manifest"] = materializer.canon(manifest)
            candidate["source_binding_manifest_sha256"] = materializer.sha_json(manifest)
            return candidate

        bad_hash = changed(
            lambda _row, manifest: manifest["families"]["ETHBTC_PERSISTENCE"]["path_bindings"][0].update({"sha256": "0" * 64})
        )
        with self.assertRaisesRegex(ValueError, "source binding hash mismatch"):
            controller.validate_payload(bad_hash)

        no_provider = changed(
            lambda _row, manifest: manifest["families"]["BREADTH_SURVIVAL"].update({"provider": ""})
        )
        with self.assertRaisesRegex(ValueError, "provider mismatch"):
            controller.validate_payload(no_provider)

        def break_commit(candidate, manifest):
            candidate["source_version_commit"] = "0" * 40
            manifest["source_commit"] = "0" * 40
            for family in manifest["families"].values():
                for binding in family["path_bindings"]:
                    binding["source_commit"] = "0" * 40

        unreachable = changed(break_commit)
        with self.assertRaisesRegex(ValueError, "not a reachable ancestor"):
            controller.validate_payload(unreachable)

        label_permutation = json.loads(json.dumps(row))
        label_permutation["candidate_decisions"]["C07_SIMPLE_3"] = not label_permutation["candidate_decisions"]["C07_SIMPLE_3"]
        with self.assertRaisesRegex(ValueError, "violates frozen boolean contract"):
            controller.validate_payload(label_permutation)

        derived_permutation = json.loads(json.dumps(row))
        derived_permutation["ethbtc_derived_state"] = "BELOW" if row["ethbtc_derived_state"] == "ABOVE" else "ABOVE"
        eth_signal = derived_permutation["ethbtc_derived_state"] == "ABOVE"
        decisions = derived_permutation["candidate_decisions"]
        decisions["C01_ETHBTC"] = eth_signal
        decisions["C04_ETHBTC_BREADTH"] = eth_signal and decisions["C02_BREADTH"]
        decisions["C05_ETHBTC_BTCD"] = eth_signal and decisions["C03_BTCD"]
        decisions["C07_SIMPLE_3"] = eth_signal and decisions["C02_BREADTH"] and decisions["C03_BTCD"]
        with self.assertRaisesRegex(ValueError, "ETHBTC row fields do not reconcile"):
            controller.validate_payload(derived_permutation)

        mismatched_cutoff = json.loads(json.dumps(row))
        mismatched_cutoff["information_cutoff_utc"] = isoz(fixture.observation - timedelta(seconds=1))
        with self.assertRaisesRegex(ValueError, "must be identical"):
            controller.validate_payload(mismatched_cutoff)

        missing_as_zero = json.loads(json.dumps(row))
        missing_as_zero["etf_raw_value"] = 0
        with self.assertRaisesRegex(ValueError, "encoded as zero"):
            controller.validate_payload(missing_as_zero)

        premature = json.loads(json.dumps(row))
        premature["outcome_24h"] = "1"
        with self.assertRaisesRegex(ValueError, "premature outcome"):
            controller.validate_payload(premature)

    def test_outcome_matures_only_after_exact_baseline_and_complete_path_reconcile(self):
        fixture = FixtureRepo(self)
        row = fixture.build()["row"]
        row_path = fixture.repo / "row.json"
        row_path.write_text(json.dumps(row) + "\n")
        controller.ingest(row_path)
        before = outcome_owner.run(isoz(fixture.observation + timedelta(hours=24)))
        self.assertEqual(before["horizons_written"], 0)
        fixture.append_future_hours()
        after = outcome_owner.run(isoz(fixture.observation + timedelta(hours=27)))
        self.assertEqual(after["horizons_written"], 1, after)
        detail = outcome_owner.read_csv(outcome_owner.DETAIL)
        self.assertEqual(len(detail), 1)
        self.assertEqual(detail[0]["baseline_reconciled"], "True")
        self.assertTrue(detail[0]["row_source_commit"])
        self.assertTrue(detail[0]["outcome_source_commit"])
        repeat = outcome_owner.run(isoz(fixture.observation + timedelta(hours=27)))
        self.assertEqual(repeat["horizons_written"], 0)
        self.assertEqual(len(outcome_owner.read_csv(outcome_owner.DETAIL)), 1)

    def test_outcome_baseline_mutation_remains_unavailable(self):
        fixture = FixtureRepo(self)
        row = fixture.build()["row"]
        row_path = fixture.repo / "row.json"
        row_path.write_text(json.dumps(row) + "\n")
        controller.ingest(row_path)
        fixture.append_future_hours(alter_baseline=True)
        result = outcome_owner.run(isoz(fixture.observation + timedelta(hours=27)))
        self.assertEqual(result["horizons_written"], 0)
        self.assertEqual(result["unavailable_reasons"].get("ROW_TIME_BASELINE_MISMATCH"), 3)
        self.assertEqual(len(outcome_owner.read_csv(outcome_owner.DETAIL)), 0)

    def test_outcome_rejects_edited_frozen_row_identity(self):
        fixture = FixtureRepo(self)
        row = fixture.build()["row"]
        row_path = fixture.repo / "row.json"
        row_path.write_text(json.dumps(row) + "\n")
        controller.ingest(row_path)
        rows = outcome_owner.read_csv(outcome_owner.ROWS)
        rows[0]["regime_tag"] = "EDITED_AFTER_FREEZE"
        outcome_owner.write_csv(outcome_owner.ROWS, rows, list(rows[0]))
        fixture.append_future_hours()
        result = outcome_owner.run(isoz(fixture.observation + timedelta(hours=27)))
        self.assertEqual(result["horizons_written"], 0)
        self.assertEqual(result["unavailable_reasons"].get("ROW_FROZEN_PROVENANCE_MISMATCH"), 3)
        self.assertEqual(len(outcome_owner.read_csv(outcome_owner.DETAIL)), 0)

    def test_quarantine_and_context_blocks_fail_closed_and_are_outcome_independent(self):
        completed = subprocess.run(
            [sys.executable, "scripts/research/core_shared_row_materializer.py", "--now-utc", "2026-10-01T00:00:00Z"],
            cwd=PROJECT,
            text=True,
            capture_output=True,
            check=True,
        )
        result = json.loads(completed.stdout)
        self.assert_rejected(result, "P0_REPAIR_QUARANTINE_ACTIVE")
        floor = datetime(2026, 8, 9, 1, 0, tzinfo=timezone.utc)
        first = materializer.context_block(floor + timedelta(days=27), floor)
        second = materializer.context_block(floor + timedelta(days=28), floor)
        self.assertEqual(first, "P28D_0000")
        self.assertEqual(second, "P28D_0001")


if __name__ == "__main__":
    unittest.main()
