import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[2] / "scripts" / "experiments" / "experiment_lifecycle_scientific_admission.py"
if str(SCRIPT.parent) not in sys.path:
    sys.path.insert(0, str(SCRIPT.parent))
import experiment_lifecycle_scientific_admission as module  # noqa: E402


def context(captured="2026-08-23T20:00:00Z"):
    return {
        "latest_capture": {
            "captured_at_utc": captured,
            "run_id": "admission-test-run",
            "market_metrics": {
                "spot": {"BTCUSDT": {"close": 64000.0}, "ETHBTC": {"close": 0.0302}},
                "breadth": {"advancers": 60},
            },
        },
        "previous_capture": {
            "captured_at_utc": "2026-08-23T16:00:00Z",
            "market_metrics": {
                "spot": {"BTCUSDT": {"close": 63000.0}, "ETHBTC": {"close": 0.0298}},
                "breadth": {"advancers": 52},
            },
        },
        "metric_deltas": [],
    }


def pair(title, first_path="breadth.advancers"):
    return {
        "kind": "SENSOR_COMBINATION",
        "title": title,
        "hypothesis": "The pair may add forward information beyond either component alone.",
        "falsifier": "It fails to beat the strongest single component on prospective independent windows.",
        "horizon_days": 7,
        "components": [
            {"metric_path": first_path, "operator": "GT", "threshold": 55},
            {"metric_path": "spot.ETHBTC.close", "operator": "GT", "threshold": 0.03},
        ],
        "target_metric_path": "spot.BTCUSDT.close",
        "target_direction": "UP",
        "target_threshold_pct": 1.0,
        "target_unit_contract_version": "FORECAST_TARGET_UNITS_v2",
        "regime_dependency": "ROTATION_WATCH",
        "novelty_reason": "ADMISSION_TEST",
        "revisit_conditions": [],
        "evidence_basis": [],
    }


def canonical(value) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def bound_batch(output: dict, captured: str = "2026-08-23T20:00:00Z", ctx: dict | None = None, **receipt_overrides):
    """Authenticated output/context/receipt bytes shaped like api_gateway.py writes them."""
    output_bytes = canonical(output)
    context_bytes = canonical(ctx if ctx is not None else context(captured))
    receipt = {
        "contract": "API_AGENT_RECEIPT_v3", "task": "DAILY_DIRECTOR_SHADOW", "status": "PASS",
        "output_hash": hashlib.sha256(output_bytes).hexdigest(), "context_hash": hashlib.sha256(context_bytes).hexdigest(),
        "forecast_candidate_count": len(output.get("forecast_candidates", [])),
        "response_id": "resp_b", "response_ids": ["resp_a", "resp_b"], "attempt_count": 2, "parse_errors": ["attempt_1:ValueError:x"],
        "created_unix": 1787515200,
    }
    receipt.update(receipt_overrides)
    for key in [key for key, value in receipt.items() if value is DROP]:
        del receipt[key]
    return output_bytes, context_bytes, canonical(receipt)


DROP = object()


def run(repo: Path, output: dict, captured: str = "2026-08-23T20:00:00Z", files: tuple | None = None, batch: str = "daily"):
    daily = repo / batch
    daily.mkdir(parents=True, exist_ok=True)
    if files is None:
        (daily / "output.json").write_text(json.dumps(output))
        (daily / "context.json").write_text(json.dumps(context(captured)))
        (daily / "receipt.json").write_text(json.dumps({"contract": "API_AGENT_RECEIPT_v3"}))
    else:
        for name, data in zip(("output.json", "context.json", "receipt.json"), files):
            (daily / name).write_bytes(data)
    cmd = [
        sys.executable, str(SCRIPT),
        "--repo-root", str(repo),
        "--daily-output", str(daily / "output.json"),
        "--daily-context", str(daily / "context.json"),
        "--daily-receipt", str(daily / "receipt.json"),
        "--candidate-root", str(repo / "research/experiment_lifecycle/candidates"),
        "--observation-root", str(repo / "research/experiment_lifecycle/observations"),
        "--dispatch-root", str(repo / "research/experiment_lifecycle/dispatch"),
        "--forecast-root", str(repo / "research/framework_memory/forecast_memory"),
        "--outcome-root", str(repo / "research/framework_memory/outcome_memory"),
        "--receipt-root", str(repo / "research/experiment_lifecycle/receipts"),
        "--registry-output", str(repo / "research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json"),
        "--manifest-output", str(repo / "research/experiment_lifecycle/LATEST_EXPERIMENT_DISPATCH_MANIFEST.json"),
        "--admission-root", str(repo / "research/experiment_lifecycle/admission"),
        "--admission-registry-output", str(repo / "research/experiment_lifecycle/LATEST_SCIENTIFIC_ADMISSION_REGISTRY.json"),
    ]
    return json.loads(subprocess.run(cmd, check=True, capture_output=True, text=True).stdout)


class ScientificAdmissionLifecycleTest(unittest.TestCase):
    def test_semantic_duplicate_is_kept_shadow_and_does_not_receive_forward_execution(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            summary = run(repo, {"forecast_candidates": [], "experiment_candidates": [pair("Pair A"), pair("Pair B")]})
            self.assertEqual(summary["new_candidate_count"], 2)
            self.assertEqual(summary["new_forecasts"], 1)
            admissions = json.loads((repo / "research/experiment_lifecycle/LATEST_SCIENTIFIC_ADMISSION_REGISTRY.json").read_text())
            self.assertEqual(admissions["status_counts"]["QUALIFIED_FOR_FORWARD_TEST"], 1)
            self.assertEqual(admissions["status_counts"]["SEMANTIC_DUPLICATE_KEEP_SHADOW"], 1)
            manifest = json.loads((repo / "research/experiment_lifecycle/LATEST_EXPERIMENT_DISPATCH_MANIFEST.json").read_text())
            self.assertEqual(manifest["contract"], "EXPERIMENT_DISPATCH_MANIFEST_v2_SCIENTIFIC_ADMISSION")
            self.assertTrue(all(row["candidate_id"] for row in manifest["requests"]))

    def test_scientific_admission_writer_does_not_recreate_same_candidate_across_months(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            output = {"forecast_candidates": [], "experiment_candidates": [pair("Stable pair")]}
            run(repo, output, "2026-08-31T23:00:00Z")
            run(repo, output, "2026-09-01T01:00:00Z")
            candidate_files = list((repo / "research/experiment_lifecycle/candidates").rglob("*.json"))
            self.assertEqual(len(candidate_files), 1)
            registry = json.loads((repo / "research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json").read_text())
            self.assertEqual(registry["candidate_count"], 1)
            self.assertEqual(registry["duplicate_candidate_file_count"], 0)

    def test_historical_candidate_requalification_is_non_retroactive(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            run(repo, {"forecast_candidates": [], "experiment_candidates": [pair("Original")]})
            admission_path = next((repo / "research/experiment_lifecycle/admission").rglob("*.json"))
            admission = json.loads(admission_path.read_text())
            self.assertFalse(admission["historical_candidate_requalification"])
            self.assertTrue(admission["no_retroactive_rescore"])
            self.assertFalse(admission["authority"]["canonical_effect"])


CENSUS_ROOT = "research/experiment_lifecycle/proposal_slot_census"


def forecast(threshold=2.0, **overrides):
    value = {"metric_path": "spot.BTCUSDT.close", "direction": "UP", "target_mode": "PCT_MOVE", "threshold_pct": threshold, "horizon_days": 7, "rationale": "SECRET-RATIONALE-TEXT"}
    value.update(overrides)
    return value


def reproduction_output():
    # one valid, one identical repeat, one malformed raw slot, one invalid mapped forecast, one distinct revision
    return {"forecast_candidates": [forecast(2.0), forecast(2.0), "malformed-slot", forecast(2.0, target_mode="ABSOLUTE_VALUE"), forecast(3.0)]}


def census_files(repo: Path):
    return sorted((repo / CENSUS_ROOT).rglob("*.json"))


def pure(files, existing=None, known=None, legacy_items=()):
    return module.proposal_slot_census(*files, legacy_items=list(legacy_items), legacy_catalog_sha256=None, existing_candidates=existing or {}, known_response_identities=known)


class ProposalSlotCensusTest(unittest.TestCase):
    def test_census_accounts_every_raw_slot_before_filtering_mapping_and_dedup(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            summary = run(repo, {}, files=bound_batch(reproduction_output()))
            self.assertEqual(summary["new_candidate_count"], 2)
            self.assertEqual(len(summary["rejected"]), 1)
            [path] = census_files(repo)
            raw = path.read_bytes()
            census = json.loads(raw)
            self.assertEqual(path.parent.relative_to(repo / CENSUS_ROOT).as_posix(), "2026/08")
            self.assertEqual(census["contract"], "EXPERIMENT_PROPOSAL_SLOT_CENSUS_v1")
            self.assertEqual((census["batch_status"], census["complete_for_observed_batch"], census["invalid_reasons"]), ("VALID_OBSERVED_BATCH", True, []))
            slots = census["slots"]
            self.assertEqual([(s["origin_family"], s["array"], s["index"]) for s in slots], [("model_forecast", "output.forecast_candidates", i) for i in range(5)])
            self.assertEqual([s["outcome"] for s in slots], ["normalized_new", "normalized_existing_duplicate", "malformed", "mapping_rejected", "normalized_new"])
            self.assertEqual(slots[1]["registration"], "REPEAT_WITHIN_BATCH")
            self.assertEqual(slots[0]["slot_sha256"], slots[1]["slot_sha256"])
            self.assertEqual(slots[0]["candidate_id"], slots[1]["candidate_id"])
            self.assertNotEqual(slots[0]["candidate_id"], slots[4]["candidate_id"])
            self.assertEqual(slots[3]["reason"], "explicit_target_unit_contract_required")
            stored = sorted(p.stem for p in (repo / "research/experiment_lifecycle/candidates").rglob("*.json"))
            self.assertEqual(stored, sorted({slots[0]["candidate_id"], slots[4]["candidate_id"]}))
            counts = census["counts"]
            self.assertEqual((counts["observed_raw_slot_count"], counts["model_emission_slot_count"], counts["distinct_normalized_hypothesis_count"]), (5, 5, 2))
            self.assertIsNone(counts["independent_effective_n"])
            self.assertEqual(counts["independent_effective_n_status"], "UNKNOWN")
            self.assertEqual(counts["by_family_outcome"]["model_forecast"], {"malformed": 1, "mapping_rejected": 1, "normalized_new": 2, "normalized_existing_duplicate": 1, "error": 0})
            self.assertEqual(census["coverage"], {"label": "PARTIAL", "scope": "SINGLE_SOURCE_FAMILY_OBSERVED_BATCH_ONLY", "global_proposal_time_trial_denominator": None, "broad_search": "BROAD_SEARCH_BLOCKED"})
            self.assertFalse(any(census["authority"].values()))
            self.assertEqual(census["attempts"], {"attempt_count": 2, "surviving_output_attempts": 1, "abandoned_attempts_without_surviving_output": 1, "parse_error_count": 1, "pre_receipt_attempts": "UNKNOWN"})
            self.assertEqual(census["containers"], {"output.experiment_candidates": "ABSENT", "output.forecast_candidates": "LIST"})
            for leaked in (b"SECRET-RATIONALE-TEXT", b"spot.BTCUSDT", b"resp_a", b"resp_b", b"malformed-slot"):
                self.assertNotIn(leaked, raw)

    def test_census_is_stable_under_replay_and_restart(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            files = bound_batch(reproduction_output())
            run(repo, {}, files=files)
            [path] = census_files(repo)
            first = path.read_bytes()
            summary = run(repo, {}, files=files)
            self.assertEqual(summary["new_candidate_count"], 0)
            self.assertEqual(census_files(repo), [path])
            self.assertEqual(path.read_bytes(), first)
            existing = {p.stem: json.loads(p.read_text()) for p in (repo / "research/experiment_lifecycle/candidates").rglob("*.json")}
            replay = pure(files, existing=existing, known=module.load_census_identities(repo / CENSUS_ROOT))
            replay["source_batch_path"] = "daily"
            self.assertEqual(replay, json.loads(first))
            self.assertEqual([s.get("registration") for s in replay["slots"]], ["FIRST_SEEN_IN_THIS_BATCH", "REPEAT_WITHIN_BATCH", None, None, "FIRST_SEEN_IN_THIS_BATCH"])

    def test_identical_batch_copied_to_another_path_adds_no_slots(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            files = bound_batch(reproduction_output())
            run(repo, {}, files=files)
            run(repo, {}, files=files, batch="copied/elsewhere")
            [path] = census_files(repo)
            self.assertEqual(json.loads(path.read_text())["batch_status"], "VALID_OBSERVED_BATCH")

    def test_same_response_identity_in_other_batch_bytes_is_invalid(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            run(repo, {}, files=bound_batch(reproduction_output()))
            run(repo, {}, files=bound_batch(reproduction_output(), created_unix=1787515999), batch="daily2")
            rows = sorted((json.loads(p.read_text()) for p in census_files(repo)), key=lambda r: r["source_batch_path"])
            self.assertEqual([r["source_batch_path"] for r in rows], ["daily", "daily2"])
            self.assertEqual(rows[0]["invalid_reasons"], [])
            self.assertEqual(rows[1]["invalid_reasons"], ["response_identity_reused_by_other_batch"])
            self.assertEqual(rows[1]["batch_status"], "INVALID")

    def assertInvalid(self, census, reason):
        self.assertIn(reason, census["invalid_reasons"])
        self.assertEqual(census["batch_status"], "INVALID")
        self.assertFalse(census["complete_for_observed_batch"])

    def test_missing_or_mismatching_hash_invalidates_but_keeps_producer_semantics(self):
        output = reproduction_output()
        self.assertInvalid(pure(bound_batch(output, output_hash="0" * 64)), "output_hash_mismatch")
        self.assertInvalid(pure(bound_batch(output, output_hash=DROP)), "output_hash_missing")
        self.assertInvalid(pure(bound_batch(output, context_hash="not-a-digest")), "context_hash_missing")
        out, ctx, rec = bound_batch(output)
        forged = json.loads(ctx)
        forged["latest_capture"]["run_id"] = "forged"
        self.assertInvalid(pure((out, canonical(forged), rec)), "context_hash_mismatch")
        self.assertInvalid(pure((out + b" ", ctx, rec)), "output_hash_mismatch")
        # api_gateway.py binds the canonical context, so re-serialised but equal context bytes stay valid
        self.assertEqual(pure((out, json.dumps(json.loads(ctx), indent=2).encode(), rec))["invalid_reasons"], [])
        self.assertInvalid(pure((out, b"[]", rec)), "context_not_object")
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            summary = run(repo, {}, files=bound_batch(output, output_hash="0" * 64))
            self.assertEqual(summary["new_candidate_count"], 2)
            [path] = census_files(repo)
            self.assertInvalid(json.loads(path.read_text()), "output_hash_mismatch")
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            run(repo, {"forecast_candidates": [], "experiment_candidates": [pair("Legacy fixture")]})
            [path] = census_files(repo)
            self.assertInvalid(json.loads(path.read_text()), "output_hash_missing")

    def test_inconsistent_declared_count_invalidates(self):
        output = reproduction_output()
        self.assertInvalid(pure(bound_batch(output, forecast_candidate_count=3)), "declared_forecast_count_mismatch")
        self.assertInvalid(pure(bound_batch(output, forecast_candidate_count=DROP)), "declared_forecast_count_missing")
        self.assertInvalid(pure(bound_batch(output, forecast_candidate_count="5")), "declared_forecast_count_malformed")
        self.assertInvalid(pure(bound_batch({"experiment_candidates": []}, forecast_candidate_count=0)), "forecast_candidates_absent")

    def test_missing_or_contradictory_response_identity_invalidates(self):
        output = reproduction_output()
        self.assertInvalid(pure(bound_batch(output, response_id=DROP)), "response_identity_missing")
        self.assertInvalid(pure(bound_batch(output, response_id="  ")), "response_identity_missing")
        self.assertInvalid(pure(bound_batch(output, response_id="resp_x")), "response_identity_contradiction")
        self.assertInvalid(pure(bound_batch(output, response_ids=["resp_b", "resp_b"])), "response_identity_duplicated_within_batch")
        self.assertInvalid(pure(bound_batch(output, response_ids=[])), "response_ids_malformed")
        self.assertInvalid(pure(bound_batch(output, attempt_count=3)), "attempt_count_response_ids_mismatch")
        self.assertInvalid(pure(bound_batch(output, attempt_count=-1)), "attempt_count_malformed")
        self.assertInvalid(pure(bound_batch(output, attempt_count=0, response_ids=DROP)), "attempt_count_inconsistent_with_status")
        self.assertInvalid(pure(bound_batch(output, status="SOMETHING_NEW")), "receipt_status_unknown")
        self.assertInvalid(pure(bound_batch(output, task="WEEKLY_CALIBRATION")), "receipt_task_not_daily_director")

    def test_missing_optional_fields_are_unknown_not_zero(self):
        census = pure(bound_batch(reproduction_output(), attempt_count=DROP, response_ids=DROP, parse_errors=DROP))
        self.assertEqual(census["invalid_reasons"], [])
        self.assertEqual(census["attempts"], {"attempt_count": "UNKNOWN", "surviving_output_attempts": 1, "abandoned_attempts_without_surviving_output": "UNKNOWN", "parse_error_count": "UNKNOWN", "pre_receipt_attempts": "UNKNOWN"})
        self.assertEqual(census["containers"]["output.experiment_candidates"], "ABSENT")
        invalid_output = pure(bound_batch({"forecast_candidates": []}, status="API_OUTPUT_INVALID"))
        self.assertEqual(invalid_output["invalid_reasons"], [])
        self.assertEqual((invalid_output["attempts"]["surviving_output_attempts"], invalid_output["attempts"]["abandoned_attempts_without_surviving_output"]), (0, 2))
        self.assertEqual(invalid_output["counts"]["observed_raw_slot_count"], 0)
        aggregate = module.aggregate_census([census, invalid_output])
        self.assertEqual((aggregate["attempts_unknown_batch_count"], aggregate["known_abandoned_attempts_without_surviving_output"]), (1, 2))

    def test_malformed_containers_clock_and_error_reasons_are_value_free(self):
        bad_horizon = {**pair("Bad horizon"), "horizon_days": "abc-SECRET"}
        untitled = {**pair("x"), "title": ""}
        output = {"forecast_candidates": [], "experiment_candidates": [bad_horizon, untitled, 7]}
        census = pure(bound_batch(output))
        self.assertEqual([(s["index"], s["outcome"], s.get("reason")) for s in census["slots"]], [(0, "error", "ValueError"), (1, "error", "invalid_identity_or_horizon"), (2, "malformed", None)])
        self.assertNotIn(b"abc-SECRET", canonical(census))
        not_a_list = pure(bound_batch({"forecast_candidates": [], "experiment_candidates": {"k": "v"}}))
        self.assertEqual(not_a_list["containers"]["output.experiment_candidates"], "NOT_A_LIST")
        self.assertEqual([(s["index"], s["outcome"]) for s in not_a_list["slots"]], [(None, "malformed")])
        broken_clock = context()
        broken_clock["latest_capture"]["captured_at_utc"] = "yesterday"
        self.assertInvalid(pure(bound_batch({"forecast_candidates": []}, ctx=broken_clock)), "capture_clock_malformed")
        out, ctx, rec = bound_batch({"forecast_candidates": []})
        self.assertInvalid(pure((b"{not json", ctx, rec)), "output_not_json")
        self.assertInvalid(pure((None, ctx, rec)), "output_file_missing")
        self.assertInvalid(pure((b"[]", ctx, rec)), "output_not_object")
        self.assertInvalid(pure((out, ctx, b"[]")), "receipt_not_object")

    def test_all_origin_families_are_labelled_and_existing_ids_are_duplicates(self):
        with tempfile.TemporaryDirectory() as td:
            catalog = Path(td) / "catalog.json"
            catalog.write_text(json.dumps({"test_id": "T", "pairs": [{"pair_id": "P1", "sensor_a": "a", "sensor_b": "b"}]}))
            legacy_items = module.base.legacy(catalog)
        ctx = context()
        ctx["metric_deltas"] = [{"metric": "breadth.advancers", "percentage_change": 15.0}, {"metric": "spot.ETHBTC.close", "percentage_change": 1.3}]
        files = bound_batch({"forecast_candidates": [forecast()], "experiment_candidates": [pair("Pair A")]}, ctx=ctx)
        census = pure(files, legacy_items=legacy_items)
        self.assertEqual([s["origin_family"] for s in census["slots"]], ["model_experiment", "legacy_sensor", "emergent_pair", "model_forecast"])
        self.assertEqual(census["counts"]["model_emission_slot_count"], 2)
        self.assertEqual(census["counts"]["distinct_model_normalized_hypothesis_count"], 2)
        legacy_id = census["slots"][1]["candidate_id"]
        prior = {legacy_id: {"candidate_id": legacy_id, "source": {"daily_output_sha256": "x", "daily_context_sha256": "y", "daily_receipt_sha256": "z"}}}
        again = pure(files, existing=prior, legacy_items=legacy_items)
        self.assertEqual((again["slots"][1]["outcome"], again["slots"][1]["registration"]), ("normalized_existing_duplicate", "REGISTERED_BY_OTHER_SOURCE"))
        self.assertEqual(again["counts"]["by_family_outcome"]["legacy_sensor"]["normalized_existing_duplicate"], 1)

    def test_retrospective_census_scans_archived_batches_read_only(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            daily = repo / "research/api_agent/outputs/daily/2026/08/23"
            batches = {"200000": bound_batch(reproduction_output()), "210000": bound_batch(reproduction_output(), output_hash="1" * 64, response_id="resp_c", response_ids=["resp_c"], attempt_count=1)}
            for stamp, files in batches.items():
                (daily / stamp).mkdir(parents=True)
                for name, data in zip(("DAILY_DIRECTOR_OUTPUT.json", "context.json", "DAILY_DIRECTOR_RECEIPT.json"), files):
                    (daily / stamp / name).write_bytes(data)
            (daily / "220000").mkdir()
            (daily / "220000" / "DAILY_DIRECTOR_RECEIPT.json").write_bytes(batches["200000"][2])
            before = sorted(p.as_posix() for p in repo.rglob("*"))
            cmd = [sys.executable, str(SCRIPT), "retrospective-census", "--repo-root", str(repo), "--daily-root", str(repo / "research/api_agent/outputs/daily"), "--candidate-root", str(repo / "research/experiment_lifecycle/candidates")]
            aggregate = json.loads(subprocess.run(cmd, check=True, capture_output=True, text=True).stdout)
            self.assertEqual(sorted(p.as_posix() for p in repo.rglob("*")), before)
            self.assertEqual((aggregate["batch_count"], aggregate["valid_batch_count"], aggregate["invalid_batch_count"]), (3, 1, 2))
            self.assertEqual(aggregate["invalid_reason_counts"], {"capture_clock_malformed": 1, "context_file_missing": 1, "context_hash_mismatch": 1, "declared_forecast_count_mismatch": 1, "forecast_candidates_absent": 1, "output_file_missing": 1, "output_hash_mismatch": 2, "response_identity_reused_by_other_batch": 1})
            self.assertEqual((aggregate["known_abandoned_attempts_without_surviving_output"], aggregate["normalized_slots_not_in_candidate_store"]), (2, 6))
            self.assertEqual(aggregate["slots_by_family_outcome"]["model_forecast"], {"malformed": 2, "mapping_rejected": 2, "normalized_new": 4, "normalized_existing_duplicate": 2, "error": 0})
            self.assertEqual(aggregate["distinct_normalized_hypothesis_count"], 2)
            self.assertIsNone(aggregate["independent_effective_n"])
            self.assertEqual(aggregate["coverage"], {"label": "PARTIAL", "global_proposal_time_trial_denominator": None, "broad_search": "BROAD_SEARCH_BLOCKED"})
            rows = module.retrospective_census(repo, repo / "research/api_agent/outputs/daily", repo / "research/experiment_lifecycle/candidates", None)
            self.assertEqual(rows, module.retrospective_census(repo, repo / "research/api_agent/outputs/daily", repo / "research/experiment_lifecycle/candidates", None))
            self.assertEqual([r["classification"] for r in rows], ["RETROSPECTIVE_DERIVED_VIEW"] * 3)


if __name__ == "__main__":
    unittest.main()
