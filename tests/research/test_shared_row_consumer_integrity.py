from __future__ import annotations

import csv
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


PROJECT = Path(__file__).parents[2]
RESEARCH_SCRIPTS = PROJECT / "scripts" / "research"
if str(RESEARCH_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(RESEARCH_SCRIPTS))

import shared_row_tournament_relevance as relevance
import shared_row_tournament_weekly as weekly
import shared_row_next_action_controller as next_action
import shared_row_tournament_monitor as monitor


FLOOR = "2026-09-30T00:00:00Z"


def runtime(active: bool = True) -> dict:
    return {
        "collection_state": weekly.ACTIVE_COLLECTION_STATE if active else "QUARANTINED_PENDING_POST_REPAIR_EVIDENCE",
        "core_prospective_eligibility_status": weekly.ACTIVE_FLOOR_STATUS if active else "CONTAINMENT_SENTINEL_NOT_AN_ACTIVATION_FLOOR",
        "core_prospective_eligibility_start": FLOOR,
    }


def row(event_id: str, timestamp: str = "2026-10-01T00:00:00Z") -> dict:
    sample = {
        "event_id": event_id,
        "observation_timestamp_utc": timestamp,
        "information_cutoff_utc": timestamp,
        "source_version_commit": "1" * 40,
        "row_integrity_contract": weekly.ROW_INTEGRITY_CONTRACT,
        "source_binding_manifest": "{}",
        "source_binding_manifest_sha256": "2" * 64,
        "ethbtc_derived_state": "ABOVE",
        "breadth_derived_state": "BROAD_MAJORITY",
        "btcd_derived_state": "FALLING_PATH",
        "candidate_decisions": json.dumps({
            "C01_ETHBTC": True, "C02_BREADTH": True, "C03_BTCD": True,
            "C04_ETHBTC_BREADTH": True, "C05_ETHBTC_BTCD": True,
            "C06_BREADTH_BTCD": True, "C07_SIMPLE_3": True,
            "C08_SIMPLE_3_ETF": False,
        }),
        "outcome_24h": "",
        "outcome_72h": "",
        "outcome_7d": "",
        "provenance_hash": "",
    }
    sample["provenance_hash"] = weekly.evidence.frozen_provenance_hash(sample)
    return sample


def divergence(event_id: str, divergence_id: str, provenance: str | None = None, *, candidate_a: str = "C07_SIMPLE_3") -> dict:
    parent_hash = row(event_id)["provenance_hash"]
    divergence_id = f"{event_id}__{candidate_a}__vs__C08_SIMPLE_3_ETF"
    expected = hashlib.sha256((parent_hash + divergence_id).encode("utf-8")).hexdigest()
    return {
        "divergence_id": divergence_id,
        "event_id": event_id,
        "observation_timestamp_utc": "2026-10-01T00:00:00Z",
        "information_cutoff_utc": "2026-10-01T00:00:00Z",
        "candidate_a": candidate_a,
        "candidate_b": "C08_SIMPLE_3_ETF",
        "decision_a": "true",
        "decision_b": "false",
        "outcome_24h": "",
        "outcome_72h": "",
        "outcome_7d": "",
        "provenance_hash": provenance or expected,
    }


def verifier(candidate: dict, _cutoff) -> dict:
    if candidate["event_id"] == "UNBOUND":
        raise ValueError("source binding reconstruction failed")
    return {"status": "BOUND"}


def write_csv(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for record in records for key in record})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)


def matured_consensus_fixture():
    """Synthetic source-approved parent, checked by the real outcome gate."""
    parent = row("CONSENSUS")
    decisions = json.loads(parent["candidate_decisions"])
    decisions.pop("C08_SIMPLE_3_ETF")
    parent["candidate_decisions"] = json.dumps(decisions)
    parent["provenance_hash"] = weekly.evidence.frozen_provenance_hash(parent)
    parent.update(outcome_24h="1", mae_24h="-0.50000000", mfe_24h="2.00000000")
    detail = {
        "event_id": parent["event_id"], "horizon": "24h",
        "observation_timestamp_utc": parent["observation_timestamp_utc"],
        "information_cutoff_utc": parent["information_cutoff_utc"],
        "target_timestamp_utc": "2026-10-02T00:00:00Z",
        "selected_end_timestamp_utc": "2026-10-02T00:00:00Z",
        "baseline_timestamp_utc": "2026-09-30T23:00:00Z",
        "matured_at_utc": "2026-10-02T01:00:00Z",
        "sample_count": 26, "baseline_reconciled": True,
        "row_source_commit": parent["source_version_commit"],
        "row_source_binding_sha256": parent["source_binding_manifest_sha256"],
        "source_contract": "HOURLY_SEQUENCE_CAPTURE_v2_2_DIRECT_BINANCE_SPOT",
        "outcome_source_commit": "3" * 40,
        "outcome_source_bindings": json.dumps([{
            "path": "03_DAILY_CAPTURE_LOGS/hourly/2026/10/2026-10-02.csv",
            "source_commit": "3" * 40, "sha256": "4" * 64, "bytes": 18000,
            "provider": "Binance spot",
            "owner_contract": "HOURLY_SEQUENCE_CAPTURE_v2_2_DIRECT_BINANCE_SPOT",
        }], sort_keys=True, separators=(",", ":")),
    }
    for asset, baseline in (("ethbtc", 0.03), ("btc", 100.0), ("eth", 3.0)):
        end = baseline * 1.01
        detail.update({
            f"{asset}_baseline": baseline, f"{asset}_end": end,
            f"{asset}_forward_return_pct": (end / baseline - 1) * 100,
            f"{asset}_mae_pct": -0.5, f"{asset}_mfe_pct": 2.0,
        })
    detail["provenance_hash"] = hashlib.sha256(
        weekly.outcome_gate.canonical(detail).encode("utf-8")
    ).hexdigest()
    return parent, detail


class SharedRowConsumerIntegrityTests(unittest.TestCase):
    def monitor_fixture(self, parents, details, source_verifier=verifier, runtime_active=True):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "lab"
            root.mkdir()
            write_csv(root / "data/PROSPECTIVE_SHARED_ROW_LEDGER.csv", parents)
            write_csv(root / "data/OUTCOME_DETAIL_LEDGER.csv", details)
            (root / "14_DIVERGENCE_FNP_LEDGER.csv").write_text("divergence_id,event_id\n")
            (root / "OWNER_BINDING_MATRIX.json").write_text(json.dumps({
                "families": [{"family_id": name, "status": "READY",
                              "candidate_decision_contract_status": "READY"}
                             for name in sorted(monitor.CORE_FAMILIES)]
            }))
            (root / "TRANSFORM_FREEZE_REGISTRY.json").write_text(json.dumps({
                "core_activation_rule": {"collection_state": monitor.ACTIVE,
                                         "containment_floor_sentinel": False}
            }))
            (root / "RUNTIME_STATUS.json").write_text(json.dumps(runtime(runtime_active)))
            for name in ("03_CANDIDATE_REGISTRY.json", "04_SHARED_ROW_SCHEMA.json", "RELEVANCE_STATE.json"):
                (root / name).write_text("{}")
            registry = root / "registry.json"
            registry.write_text(json.dumps({"sensors": [{"sensor_id": "SHARED_ROW_MODEL_TOURNAMENT_V1"}]}))
            # Only synthetic source reconstruction is supplied. The production
            # filter, frozen row checks and immutable outcome gate run unchanged.
            with mock.patch.object(monitor, "ROOT", root), mock.patch.object(monitor, "REGISTRY", registry), mock.patch.object(
                weekly.evidence, "verify_source_bindings", side_effect=source_verifier
            ):
                with self.assertRaises(SystemExit) as caught:
                    monitor.main()
                result = json.loads((root / "monitor/LATEST.json").read_text())
            return caught.exception.code, result

    def test_monitor_runtime_quarantine_cannot_report_active_pass(self):
        parent, detail = matured_consensus_fixture()
        code, result = self.monitor_fixture([parent], [detail], runtime_active=False)
        self.assertEqual(code, 2)
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("COLLECTION_STATE_MISMATCH", result["issues"])
        self.assertEqual(result["collection_state"], "INCONSISTENT")
        self.assertEqual(result["freeze_collection_state"], monitor.ACTIVE)
        self.assertEqual(result["runtime_collection_state"], runtime(False)["collection_state"])
        self.assertEqual(result["eligible_row_n"], 0)
        self.assertEqual(result["matured_shared_rows"]["24h"], 0)
        self.assertEqual(result["scoring_readiness"], "FAIL_CLOSED_INCONSISTENT_RUNTIME")
        self.assertEqual(result["exact_next_evidence_event"],
                         "RECONCILE_RUNTIME_AND_FREEZE_COLLECTION_STATE")

    def test_monitor_active_controls_still_admit_verified_consensus(self):
        parent, detail = matured_consensus_fixture()
        code, result = self.monitor_fixture([parent], [detail], runtime_active=True)
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["collection_state"], monitor.ACTIVE)
        self.assertEqual(result["freeze_collection_state"], monitor.ACTIVE)
        self.assertEqual(result["runtime_collection_state"], monitor.ACTIVE)
        self.assertEqual(result["matured_shared_rows"]["24h"], 1)

    def test_monitor_consensus_parent_matures_without_divergence(self):
        parent, detail = matured_consensus_fixture()
        code, result = self.monitor_fixture([parent], [detail])
        self.assertEqual(code, 0)
        self.assertEqual(result["matured"], {"24h": 0, "72h": 0, "7d": 0})
        self.assertEqual(result["matured_shared_rows"], {"24h": 1, "72h": 0, "7d": 0})
        self.assertEqual(result["exact_next_evidence_event"], "FIRST_MATURED_72H_OUTCOME")
        self.assertIsNone(result["maturity_count_semantics"]["independent_trial_count"])
        self.assertFalse(result["maturity_count_semantics"]["row_counts_are_independent_trials"])

    def test_monitor_parent_maturity_requires_original_valid_outcome_receipt(self):
        parent, detail = matured_consensus_fixture()
        tampered = copy.deepcopy(detail)
        tampered["ethbtc_end"] = 0.08
        for details in ([], [tampered], [detail, detail]):
            with self.subTest(details=len(details)):
                code, result = self.monitor_fixture([parent], details)
                self.assertEqual(code, 2)
                self.assertEqual(result["matured_shared_rows"]["24h"], 0)
                self.assertEqual(result["consumer_integrity_filter"]["excluded"]["outcome_receipt"], 1)

    def test_monitor_parent_maturity_rejects_unbound_source(self):
        parent, detail = matured_consensus_fixture()
        def unavailable_source(_row, _cutoff):
            raise ValueError("immutable source missing or hash mismatch")
        code, result = self.monitor_fixture([parent], [detail], unavailable_source)
        self.assertEqual(code, 2)
        self.assertEqual(result["matured_shared_rows"]["24h"], 0)
        self.assertEqual(result["consumer_integrity_filter"]["excluded"]["source_binding"], 1)

    def test_monitor_duplicate_parents_do_not_inflate_maturity(self):
        parent, detail = matured_consensus_fixture()
        code, result = self.monitor_fixture([parent, parent], [detail])
        self.assertEqual(code, 2)
        self.assertEqual(result["matured_shared_rows"]["24h"], 0)
        self.assertEqual(result["consumer_integrity_filter"]["excluded"]["duplicate_event_id"], 2)

    def test_monitor_empty_outcomes_stay_pending(self):
        code, result = self.monitor_fixture([row("PENDING")], [])
        self.assertEqual(code, 0)
        self.assertEqual(result["matured_shared_rows"], {"24h": 0, "72h": 0, "7d": 0})
        self.assertEqual(result["exact_next_evidence_event"], "FIRST_MATURED_24H_OUTCOME")

    def adversarial_data(self):
        good = row("GOOD")
        pre_floor = row("PRE_FLOOR", "2026-09-29T23:00:00Z")
        unbound = row("UNBOUND")
        bad_provenance = row("BAD_PROVENANCE")
        bad_provenance["provenance_hash"] = "not-a-sha256"
        rows = [good, pre_floor, unbound, bad_provenance]
        divs = [
            divergence("GOOD", "D_GOOD"),
            divergence("PRE_FLOOR", "D_PRE_FLOOR"),
            divergence("UNBOUND", "D_UNBOUND"),
            divergence("GOOD", "D_BAD_HASH", "0" * 64, candidate_a="C02_BREADTH"),
        ]
        return rows, divs

    def test_shared_filter_counts_only_bound_post_floor_rows(self) -> None:
        rows, divs = self.adversarial_data()
        valid_rows, valid_divs, excluded = weekly.filter_consumer_rows(rows, divs, runtime(), verifier)
        self.assertEqual([item["event_id"] for item in valid_rows], ["GOOD"])
        self.assertEqual([item["divergence_id"] for item in valid_divs], ["GOOD__C07_SIMPLE_3__vs__C08_SIMPLE_3_ETF"])
        self.assertEqual(excluded["pre_floor_or_timestamp"], 1)
        self.assertEqual(excluded["source_binding"], 1)
        self.assertEqual(excluded["immutable_provenance"], 1)
        self.assertEqual(excluded["divergence_parent"], 2)
        self.assertEqual(excluded["divergence_provenance"], 1)

    def test_hash_shaped_but_wrong_frozen_row_is_excluded(self) -> None:
        entry = row("HASH_SHAPED_TAMPER")
        entry["provenance_hash"] = "f" * 64
        valid, _, excluded = weekly.filter_consumer_rows([entry], [], runtime(), verifier)
        self.assertEqual(valid, [])
        self.assertEqual(excluded["immutable_provenance"], 1)

    def test_changed_candidate_decision_even_with_valid_hash_shape_is_excluded(self) -> None:
        entry = row("DECISION_TAMPER")
        decisions = json.loads(entry["candidate_decisions"])
        decisions["C01_ETHBTC"] = False
        entry["candidate_decisions"] = json.dumps(decisions)
        valid, _, excluded = weekly.filter_consumer_rows([entry], [], runtime(), verifier)
        self.assertEqual(valid, [])
        self.assertEqual(excluded["immutable_provenance"], 1)

    def test_recomputed_self_hash_does_not_override_frozen_boolean_rules(self) -> None:
        entry = row("FROZEN_RULE_TAMPER")
        decisions = json.loads(entry["candidate_decisions"])
        decisions["C07_SIMPLE_3"] = False
        entry["candidate_decisions"] = json.dumps(decisions)
        entry["provenance_hash"] = weekly.evidence.frozen_provenance_hash(entry)
        valid, _, excluded = weekly.filter_consumer_rows([entry], [], runtime(), verifier)
        self.assertEqual(valid, [])
        self.assertEqual(excluded["source_binding"], 1)

    def test_matured_parent_without_original_detail_is_never_scored(self) -> None:
        entry = row("FAKE_MATURED_24H")
        entry["outcome_24h"] = "1"
        entry["mae_24h"] = "-0.25000000"
        entry["mfe_24h"] = "0.50000000"
        # These outcome fields are intentionally mutable in the original
        # frozen projection. A matching owner detail must still exist.
        self.assertEqual(weekly.evidence.frozen_provenance_hash(entry), entry["provenance_hash"])
        valid, _, excluded = weekly.filter_consumer_rows([entry], [], runtime(), verifier, outcome_details=[])
        self.assertEqual(valid, [])
        self.assertEqual(excluded["outcome_receipt"], 1)

    def test_divergence_with_invented_matured_label_is_not_admitted(self) -> None:
        entry = row("DIV_FORGED_OUTCOME")
        pair = divergence("DIV_FORGED_OUTCOME", "D_VALID")
        pair["outcome_24h"] = "1"  # parent and owner detail are still unmatured
        valid, divs, excluded = weekly.filter_consumer_rows([entry], [pair], runtime(), verifier, outcome_details=[])
        self.assertEqual(len(valid), 1)
        self.assertEqual(divs, [])
        self.assertEqual(excluded["divergence_outcome"], 1)

    def test_divergence_misattributes_a_frozen_candidate_vote(self) -> None:
        entry = row("DIV_VOTE_TAMPER")
        pair = divergence("DIV_VOTE_TAMPER", "D_VALID")
        pair["decision_a"] = "false"
        valid, divs, excluded = weekly.filter_consumer_rows([entry], [pair], runtime(), verifier, outcome_details=[])
        self.assertEqual(len(valid), 1)
        self.assertEqual(divs, [])
        self.assertEqual(excluded["divergence_decision"], 1)

    def test_duplicate_divergence_identity_cannot_double_count(self) -> None:
        entry = row("DIV_DOUBLE")
        pair = divergence("DIV_DOUBLE", "D_VALID")
        valid, divs, excluded = weekly.filter_consumer_rows([entry], [pair, dict(pair)], runtime(), verifier, outcome_details=[])
        self.assertEqual(len(valid), 1)
        self.assertEqual(divs, [])
        self.assertEqual(excluded["divergence_provenance"], 2)

    def test_quarantine_excludes_every_row_and_divergence(self) -> None:
        rows, divs = self.adversarial_data()
        valid_rows, valid_divs, excluded = weekly.filter_consumer_rows(rows, divs, runtime(False), verifier)
        self.assertEqual(valid_rows, [])
        self.assertEqual(valid_divs, [])
        self.assertEqual(excluded["runtime_inactive"], len(rows))
        self.assertEqual(excluded["divergence_parent"], len(divs))

    def test_weekly_relevance_and_next_action_share_one_fail_closed_filter(self) -> None:
        self.assertIs(relevance.filter_consumer_rows, weekly.filter_consumer_rows)
        self.assertIs(next_action.filter_consumer_rows, weekly.filter_consumer_rows)

    def test_monitor_does_not_consider_forged_maturity_clock_a_verified_outcome(self) -> None:
        parent = row("MATURITY_CLOCK_ONLY")
        pair = divergence("MATURITY_CLOCK_ONLY", "D_VALID")
        pair["matured_24h_utc"] = "2026-10-02T00:00:00Z"
        self.assertEqual(
            monitor.verified_matured_divergence_counts([parent], [pair]),
            {"24h": 0, "72h": 0, "7d": 0},
        )
        # A genuinely verified parent+pair outcome is counted exactly once.
        parent["outcome_24h"] = pair["outcome_24h"] = "1"
        self.assertEqual(
            monitor.verified_matured_divergence_counts([parent], [pair])["24h"], 1
        )

    def test_monitor_fails_closed_on_sha_shaped_but_forged_current_row(self) -> None:
        forged = row("MONITOR_FAKE_SHA")
        forged["provenance_hash"] = "a" * 64
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "lab"
            root.mkdir()
            write_csv(root / "data" / "PROSPECTIVE_SHARED_ROW_LEDGER.csv", [forged])
            (root / "14_DIVERGENCE_FNP_LEDGER.csv").write_text("divergence_id,event_id\\n")
            (root / "data" / "OUTCOME_DETAIL_LEDGER.csv").write_text("event_id,horizon\\n")
            (root / "OWNER_BINDING_MATRIX.json").write_text(json.dumps({
                "families": [{
                    "family_id": name, "status": "READY",
                    "candidate_decision_contract_status": "READY"
                } for name in sorted(monitor.CORE_FAMILIES)]
            }))
            (root / "TRANSFORM_FREEZE_REGISTRY.json").write_text(json.dumps({
                "core_activation_rule": {
                    "collection_state": monitor.ACTIVE, "containment_floor_sentinel": False
                }
            }))
            (root / "RUNTIME_STATUS.json").write_text(json.dumps(runtime()))
            for name in ["03_CANDIDATE_REGISTRY.json", "04_SHARED_ROW_SCHEMA.json", "RELEVANCE_STATE.json"]:
                (root / name).write_text("{}")
            registry = root / "registry.json"
            registry.write_text(json.dumps({
                "sensors": [{"sensor_id": "SHARED_ROW_MODEL_TOURNAMENT_V1"}]
            }))
            with mock.patch.object(monitor, "ROOT", root), mock.patch.object(monitor, "REGISTRY", registry), mock.patch.object(
                monitor, "filter_consumer_rows", side_effect=lambda rows, divs, state, outcome_details: weekly.filter_consumer_rows(
                    rows, divs, state, verifier, outcome_details=outcome_details
                )
            ) as linked_filter:
                with self.assertRaises(SystemExit) as caught:
                    monitor.main()
                self.assertEqual(caught.exception.code, 2)
                linked_filter.assert_called_once()
            result = json.loads((root / "monitor" / "LATEST.json").read_text())
            self.assertEqual(result["status"], "FAIL")
            self.assertEqual(result["eligible_row_n"], 0)
            self.assertEqual(result["consumer_integrity_filter"]["excluded"]["immutable_provenance"], 1)
            self.assertIn("UNVERIFIED_PROSPECTIVE_ROW_OR_DIVERGENCE", result["issues"])
            self.assertEqual(result["scoring_readiness"], "FAIL_CLOSED_UNVERIFIED_RESEARCH_EVIDENCE")

    def test_weekly_and_relevance_use_the_same_fail_closed_filter(self) -> None:
        self.assertIs(relevance.filter_consumer_rows, weekly.filter_consumer_rows)
        rows, divs = self.adversarial_data()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_csv(root / "data" / "PROSPECTIVE_SHARED_ROW_LEDGER.csv", rows)
            write_csv(root / "14_DIVERGENCE_FNP_LEDGER.csv", divs)
            (root / "RUNTIME_STATUS.json").write_text(json.dumps(runtime()))
            (root / "03_CANDIDATE_REGISTRY.json").write_text(json.dumps({"candidates": [{"id": "C07_SIMPLE_3"}, {"id": "C08_SIMPLE_3_ETF"}]}))
            (root / "OWNER_BINDING_MATRIX.json").write_text(json.dumps({"families": [{"family_id": "CORE", "status": "READY"}]}))
            with mock.patch.object(weekly.evidence, "verify_source_bindings", verifier), mock.patch.multiple(
                weekly,
                ROOT=root,
                LED=root / "data" / "PROSPECTIVE_SHARED_ROW_LEDGER.csv",
                FNP=root / "14_DIVERGENCE_FNP_LEDGER.csv",
                REG=root / "03_CANDIDATE_REGISTRY.json",
                OUT=root / "weekly",
            ), mock.patch.object(relevance, "ROOT", root):
                weekly.main()
                relevance.main()
            weekly_report = json.loads((root / "weekly" / "LATEST.json").read_text())
            relevance_report = json.loads((root / "RELEVANCE_STATE.json").read_text())
            self.assertEqual((weekly_report["eligible_rows_total"], weekly_report["divergences_total"]), (1, 1))
            self.assertEqual((relevance_report["eligible_row_n"], relevance_report["divergence_n"]), (1, 1))


if __name__ == "__main__":
    unittest.main()
