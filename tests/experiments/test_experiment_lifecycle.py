import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[2] / "scripts" / "experiments" / "experiment_lifecycle.py"


def run_engine(repo: Path, output: dict, context: dict, catalog: Path | None = None) -> dict:
    daily = repo / "daily"; daily.mkdir(parents=True, exist_ok=True)
    files = {"output.json": output, "context.json": context, "receipt.json": {"contract": "API_AGENT_RECEIPT_v3"}}
    for name, value in files.items(): (daily / name).write_text(json.dumps(value))
    cmd = [sys.executable, str(SCRIPT), "--repo-root", str(repo), "--daily-output", str(daily / "output.json"), "--daily-context", str(daily / "context.json"), "--daily-receipt", str(daily / "receipt.json"), "--candidate-root", str(repo / "research/experiment_lifecycle/candidates"), "--observation-root", str(repo / "research/experiment_lifecycle/observations"), "--dispatch-root", str(repo / "research/experiment_lifecycle/dispatch"), "--forecast-root", str(repo / "research/framework_memory/forecast_memory"), "--outcome-root", str(repo / "research/framework_memory/outcome_memory"), "--receipt-root", str(repo / "research/experiment_lifecycle/receipts"), "--registry-output", str(repo / "research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json"), "--manifest-output", str(repo / "research/experiment_lifecycle/LATEST_EXPERIMENT_DISPATCH_MANIFEST.json")]
    if catalog: cmd += ["--legacy-sensor-catalog", str(catalog)]
    return json.loads(subprocess.run(cmd, check=True, capture_output=True, text=True).stdout)


def context(captured_at: str, run_id: str = "run-1") -> dict:
    return {"latest_capture": {"captured_at_utc": captured_at, "run_id": run_id, "market_metrics": {"spot": {"BTCUSDT": {"close": 64000.0}, "ETHUSDT": {"close": 1870.0}, "ETHBTC": {"close": 0.0292}}, "breadth": {"advancers": 55, "decliners": 30}}}, "previous_capture": {"captured_at_utc": "2026-08-05T06:00:00Z", "market_metrics": {"spot": {"BTCUSDT": {"close": 63000.0}, "ETHUSDT": {"close": 1830.0}, "ETHBTC": {"close": 0.0290}}, "breadth": {"advancers": 45, "decliners": 35}}}, "metric_deltas": []}


def pct_candidate(path="spot.BTCUSDT.close", direction="UP", pct=2.0, horizon=7, rationale="Prospective test"):
    return {"metric_path": path, "direction": direction, "target_mode": "PCT_MOVE", "threshold_pct": pct, "target_value": None, "range_low": None, "range_high": None, "horizon_days": horizon, "rationale": rationale}


class ExperimentLifecycleTest(unittest.TestCase):
    def test_forecast_candidate_is_frozen_and_matures_later(self):
        with tempfile.TemporaryDirectory() as td:
            repo=Path(td);summary=run_engine(repo,{"forecast_candidates":[pct_candidate()],"experiment_candidates":[]},context("2026-08-05T10:00:00Z"));self.assertEqual(summary["new_forecasts"],1);registry=json.loads((repo/"research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json").read_text());self.assertEqual(registry["state_counts"]["WAITING_FOR_MATURITY"],1);frozen=json.loads(next((repo/"research/framework_memory/forecast_memory").rglob("*.json")).read_text());self.assertEqual(frozen["unit_contract_version"],"FORECAST_TARGET_UNITS_v2");self.assertAlmostEqual(frozen["threshold_pct"],2.0);self.assertTrue(frozen["experimental_only"]);self.assertFalse(frozen["authority"]["portfolio_action"]);self.assertEqual(frozen["controls"]["always_wait"],"ALWAYS_WAIT");self.assertIn(frozen["controls"]["deterministic_placebo_direction"],{"UP","DOWN","RANGE"})

    def test_absolute_directional_target_is_normalized_before_freeze(self):
        with tempfile.TemporaryDirectory() as td:
            repo=Path(td);output={"forecast_candidates":[{"metric_path":"spot.BTCUSDT.close","direction":"DOWN","target_mode":"ABSOLUTE_VALUE","threshold_pct":None,"target_value":63360.0,"range_low":None,"range_high":None,"horizon_days":3,"rationale":"Absolute target test"}],"experiment_candidates":[]};summary=run_engine(repo,output,context("2026-08-05T10:00:00Z"));self.assertEqual(summary["new_forecasts"],1);frozen=json.loads(next((repo/"research/framework_memory/forecast_memory").rglob("*.json")).read_text());self.assertEqual(frozen["unit_contract_version"],"FORECAST_TARGET_UNITS_v2");self.assertEqual(frozen["target_mode"],"PCT_MOVE");self.assertAlmostEqual(frozen["threshold_pct"],1.0)

    def test_absolute_range_is_normalized_before_freeze(self):
        with tempfile.TemporaryDirectory() as td:
            repo=Path(td);output={"forecast_candidates":[{"metric_path":"spot.BTCUSDT.close","direction":"RANGE","target_mode":"ABSOLUTE_RANGE","threshold_pct":None,"target_value":None,"range_low":63360.0,"range_high":64640.0,"horizon_days":1,"rationale":"Range test"}],"experiment_candidates":[]};summary=run_engine(repo,output,context("2026-08-05T10:00:00Z"));self.assertEqual(summary["new_forecasts"],1);frozen=json.loads(next((repo/"research/framework_memory/forecast_memory").rglob("*.json")).read_text());self.assertEqual(frozen["target_mode"],"PCT_RANGE");self.assertAlmostEqual(frozen["range_lower_pct"],-1.0);self.assertAlmostEqual(frozen["range_upper_pct"],1.0)

    def test_legacy_ambiguous_forecast_candidate_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            repo=Path(td);output={"forecast_candidates":[{"metric_path":"spot.BTCUSDT.close","direction":"DOWN","threshold":63360.0,"range_low":None,"range_high":None,"horizon_days":3,"rationale":"Legacy ambiguous"}],"experiment_candidates":[]};summary=run_engine(repo,output,context("2026-08-05T10:00:00Z"));self.assertEqual(summary["new_forecasts"],0);self.assertTrue(any(row["error"]=="explicit_target_unit_contract_required" for row in summary["rejected"]))

    def test_legacy_forecast_test_candidate_does_not_refire_after_upgrade(self):
        with tempfile.TemporaryDirectory() as td:
            repo=Path(td);candidate_root=repo/"research/experiment_lifecycle/candidates/2026/08";candidate_root.mkdir(parents=True);legacy={"contract":"EXPERIMENT_CANDIDATE_v1","candidate_id":"EC-legacy","created_at_utc":"2026-08-04T10:00:00Z","registered_at_utc":"2026-08-04T10:00:00Z","spec":{"kind":"FORECAST_TEST","title":"legacy","hypothesis":"legacy","falsifier":"legacy","horizon_days":3,"components":[],"target_metric_path":"spot.BTCUSDT.close","target_direction":"DOWN","target_threshold_pct":64699.1,"target_range_lower_pct":None,"target_range_upper_pct":None,"regime_dependency":"CURRENT_OBSERVED_REGIME","novelty_reason":"DAILY_DIRECTOR_FORECAST","revisit_conditions":[],"evidence_basis":[]},"source":{},"dormancy_policy":{"automatic_age_expiry":False,"retain_until":"FALSIFIED_OR_GOVERNANCE_CLOSED"},"authority":{"canonical_promotion":False,"framework_state_change":False,"model_weight_change":False,"portfolio_action":False}};(candidate_root/"EC-legacy.json").write_text(json.dumps(legacy));summary=run_engine(repo,{"forecast_candidates":[],"experiment_candidates":[]},context("2026-08-05T10:00:00Z"));self.assertEqual(summary["new_forecasts"],0);registry=json.loads((repo/"research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json").read_text());state=next(row["state"] for row in registry["candidates"] if row["candidate_id"]=="EC-legacy");self.assertEqual(state,"TARGET_UNIT_QUARANTINED")

    def test_legacy_pair_waits_for_mapping_without_expiry(self):
        with tempfile.TemporaryDirectory() as td:
            repo=Path(td);catalog=repo/"catalog.json";catalog.write_text(json.dumps({"test_id":"SENSOR_PAIR_DISCOVERY_LAB_V0_1","pairs":[{"pair_id":"P99","sensor_a":"ODD_A","sensor_b":"ODD_B"}]}));run_engine(repo,{"forecast_candidates":[],"experiment_candidates":[]},context("2026-08-05T10:00:00Z"),catalog);registry=json.loads((repo/"research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json").read_text());self.assertEqual(registry["state_counts"]["WAITING_FOR_MAPPING"],1);candidate=json.loads(next((repo/"research/experiment_lifecycle/candidates").rglob("*.json")).read_text());self.assertFalse(candidate["dormancy_policy"]["automatic_age_expiry"]);self.assertEqual(len(list((repo/"research/framework_memory/forecast_memory").rglob("*.json"))),0)

    def test_semantic_candidate_dedup_ignores_changing_evidence_text(self):
        with tempfile.TemporaryDirectory() as td:
            repo=Path(td);base={"kind":"SENSOR_COMBINATION","title":"Breadth plus ETH relative strength","hypothesis":"The conjunction may improve rotation discrimination.","falsifier":"It fails to beat the strongest single component after sufficient independent windows.","horizon_days":7,"components":[{"metric_path":"breadth.advancers","operator":"GT","threshold":50},{"metric_path":"spot.ETHBTC.close","operator":"GT","threshold":0.029}],"target_metric_path":"spot.BTCUSDT.close","target_direction":"UP","target_threshold_pct":1.0,"target_unit_contract_version":"FORECAST_TARGET_UNITS_v2","regime_dependency":"ROTATION_WATCH","novelty_reason":"PAIR_DISCOVERY","revisit_conditions":["Both metrics available"]};first=dict(base,evidence_basis=["first numeric print"]);second=dict(base,evidence_basis=["later numeric print"]);run_engine(repo,{"forecast_candidates":[],"experiment_candidates":[first]},context("2026-08-05T10:00:00Z","run-1"));run_engine(repo,{"forecast_candidates":[],"experiment_candidates":[second]},context("2026-08-05T14:00:00Z","run-2"));self.assertEqual(len(list((repo/"research/experiment_lifecycle/candidates").rglob("*.json"))),1);self.assertEqual(len(list((repo/"research/experiment_lifecycle/observations").rglob("*.json"))),2)

    def test_registry_deduplicates_same_candidate_id_to_earliest_canonical_source(self):
        with tempfile.TemporaryDirectory() as td:
            repo=Path(td)
            catalog=repo/"catalog.json"
            catalog.write_text(json.dumps({"test_id":"SENSOR_PAIR_DISCOVERY_LAB_V0_1","pairs":[{"pair_id":"P99","sensor_a":"ODD_A","sensor_b":"ODD_B"}]}))
            run_engine(repo,{"forecast_candidates":[],"experiment_candidates":[]},context("2026-08-05T10:00:00Z"),catalog)
            first_path=next((repo/"research/experiment_lifecycle/candidates").rglob("*.json"))
            first=json.loads(first_path.read_text())
            duplicate=dict(first)
            duplicate["created_at_utc"]="2026-09-01T10:00:00Z"
            duplicate["registered_at_utc"]="2026-09-01T10:01:00Z"
            duplicate["source"]={"source_run_id":"later-duplicate"}
            later_path=repo/"research/experiment_lifecycle/candidates/2026/09"/first_path.name
            later_path.parent.mkdir(parents=True,exist_ok=True)
            later_path.write_text(json.dumps(duplicate))
            run_engine(repo,{"forecast_candidates":[],"experiment_candidates":[]},context("2026-09-02T10:00:00Z"),None)
            registry=json.loads((repo/"research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json").read_text())
            self.assertEqual(registry["candidate_count"],1)
            self.assertEqual(registry["duplicate_candidate_file_count"],1)
            self.assertEqual(len(registry["candidates"]),1)
            self.assertEqual(registry["candidates"][0]["created_at_utc"],first["created_at_utc"])
            self.assertEqual(registry["rules"]["candidate_id_uniqueness"],"ONE_CURRENT_ROW_PER_CANDIDATE_ID_EARLIEST_CANONICAL_SOURCE")

    def test_registry_fails_closed_on_same_candidate_id_with_conflicting_spec(self):
        with tempfile.TemporaryDirectory() as td:
            repo=Path(td)
            catalog=repo/"catalog.json"
            catalog.write_text(json.dumps({"test_id":"SENSOR_PAIR_DISCOVERY_LAB_V0_1","pairs":[{"pair_id":"P99","sensor_a":"ODD_A","sensor_b":"ODD_B"}]}))
            run_engine(repo,{"forecast_candidates":[],"experiment_candidates":[]},context("2026-08-05T10:00:00Z"),catalog)
            first_path=next((repo/"research/experiment_lifecycle/candidates").rglob("*.json"))
            duplicate=json.loads(first_path.read_text())
            duplicate["spec"]=dict(duplicate["spec"])
            duplicate["spec"]["title"]="CONFLICTING SAME-ID SPEC"
            later_path=repo/"research/experiment_lifecycle/candidates/2026/09"/first_path.name
            later_path.parent.mkdir(parents=True,exist_ok=True)
            later_path.write_text(json.dumps(duplicate))
            with self.assertRaises(subprocess.CalledProcessError):
                run_engine(repo,{"forecast_candidates":[],"experiment_candidates":[]},context("2026-09-02T10:00:00Z"),None)

    def test_same_candidate_identity_is_not_recreated_in_new_month_partition(self):
        with tempfile.TemporaryDirectory() as td:
            repo=Path(td)
            output={"forecast_candidates":[pct_candidate()],"experiment_candidates":[]}
            run_engine(repo,output,context("2026-08-31T23:00:00Z","aug-run"))
            run_engine(repo,output,context("2026-09-01T01:00:00Z","sep-run"))
            files=list((repo/"research/experiment_lifecycle/candidates").rglob("*.json"))
            self.assertEqual(len(files),1)
            registry=json.loads((repo/"research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json").read_text())
            self.assertEqual(registry["candidate_count"],1)
            self.assertEqual(registry["duplicate_candidate_file_count"],0)

    def test_same_capture_forecasts_share_event_window_and_frozen_controls(self):
        with tempfile.TemporaryDirectory() as td:
            repo=Path(td);output={"forecast_candidates":[pct_candidate("spot.BTCUSDT.close","UP",1.0,rationale="BTC candidate"),pct_candidate("spot.ETHUSDT.close","UP",1.5,rationale="ETH candidate")],"experiment_candidates":[]};run_engine(repo,output,context("2026-08-05T10:00:00Z","run-shared"));forecasts=[json.loads(path.read_text()) for path in (repo/"research/framework_memory/forecast_memory").rglob("*.json")];self.assertEqual(len(forecasts),2);self.assertEqual(len({row["causal_event_window_id"] for row in forecasts}),1);self.assertEqual(len({row["controls"]["deterministic_placebo_direction"] for row in forecasts}),1)
            for row in forecasts:
                self.assertEqual(row["controls"]["control_freeze_time_utc"],"2026-08-05T10:00:00Z");self.assertEqual(row["controls"]["always_wait"],"ALWAYS_WAIT");self.assertEqual(row["unit_contract_version"],"FORECAST_TARGET_UNITS_v2")



class CensoredOutcomeIntegrityTests(unittest.TestCase):
    """Task2 science: raw receipt != MATURED != scientifically scoreable."""

    def sample_registry(self, root: Path, outcomes: list[dict], forecasts=None):
        from scripts.experiments.experiment_lifecycle import registry
        cr=root/"candidates"; ob=root/"observations"; fr=root/"forecasts"
        oc=root/"outcomes"; rc=root/"receipts"
        for folder in (cr,ob,fr,oc,rc):
            folder.mkdir(parents=True,exist_ok=True)
        (cr/"test.json").write_text(json.dumps({
            "contract":"EXPERIMENT_CANDIDATE_v1","candidate_id":"EC-censor",
            "created_at_utc":"2026-09-01T00:00:00Z",
            "spec":{"kind":"SENSOR_COMBINATION","title":"Synthetic sensor control"}
        }))
        ids=forecasts or [str(x.get("forecast_id")) for x in outcomes]
        from scripts.experiments.experiment_lifecycle import sha
        frozen_by_id={}
        for i,fid in enumerate(ids):
            frozen={
                "contract":"FROZEN_FORECAST_v1",
                "source_candidate_id":"EC-censor","forecast_id":fid,
                "unit_contract_version":"FORECAST_TARGET_UNITS_v2",
                "frozen_at_utc":"2026-09-01T00:00:00Z",
                "outcome_due_utc":"2026-09-02T00:00:00Z",
                "settlement_contract_version":"FORECAST_SETTLEMENT_EXACT_TARGET_TIME_v1",
                "scientific_admission":{"status":"QUALIFIED_FOR_FORWARD_TEST"},
                "metric_path":"market_metrics.spot.BTCUSDT.close",
                "metric_path_root":"CAPTURE_DOCUMENT_ROOT",
                "direction":"UP","start_value":100.0,
                "threshold_pct":1.0,"target_mode":"PCT_MOVE",
            }
            frozen_by_id[fid]=frozen
            (fr/f"{i}.json").write_text(json.dumps(frozen))
        # Establish an isolated accepted-main trust root BEFORE outcome data.
        # Production never accepts this test remote from a forecast field.
        from unittest.mock import patch
        origin = root / ".fixture-origin.git"
        subprocess.run(["git", "init", "-q", "--bare", str(origin)], check=True)
        def fixture_git(*args, stamp="2026-09-01T00:00:01Z"):
            return subprocess.run(["git", "-C", str(root), *args], check=True,
                capture_output=True, env=dict(os.environ, GIT_AUTHOR_NAME="Fixture",
                GIT_AUTHOR_EMAIL="fixture@example.invalid", GIT_COMMITTER_NAME="Fixture",
                GIT_COMMITTER_EMAIL="fixture@example.invalid", GIT_AUTHOR_DATE=stamp,
                GIT_COMMITTER_DATE=stamp))
        fixture_git("init", "-q", "-b", "main")
        fixture_git("remote", "add", "origin", origin.as_uri())
        fixture_git("add", "forecasts", "candidates")
        fixture_git("commit", "-qm", "first prospective forecast fixture")
        allow = patch("scripts.experiments.source_git_anchor.ALLOWED_ORIGINS", {origin.as_uri()})
        allow.start()
        self.addCleanup(allow.stop)
        bindings=root/"settlement_bindings"
        evidence_root=root/"settlement_evidence"
        bindings.mkdir(); evidence_root.mkdir()
        for i,original in enumerate(outcomes):
            outcome=dict(original)
            fid=outcome["forecast_id"]
            frozen=frozen_by_id[fid]
            expected=original.get("result")
            price=102.0 if expected=="HIT" else 100.2 if expected=="MISS" else 100.0
            # Full synthetic RAW source is required by the *original*
            # canonical settlement validator (not only a self-hashed JSON).
            import hashlib
            raw_path=root/"raw"/fid/"source.json"
            raw_path.parent.mkdir(parents=True,exist_ok=True)
            from datetime import datetime,timedelta,timezone
            due=datetime.fromisoformat(frozen["outcome_due_utc"].replace("Z","+00:00"))
            prior=due-timedelta(minutes=1)
            open_ms=int(prior.timestamp()*1000)
            close_ms=int(due.timestamp()*1000)-1
            # Real 1m Binance row shape, made from entirely synthetic prices.
            # Only the original raw close may establish a scoreable outcome.
            raw_bytes=json.dumps([[open_ms,"100","104","99",str(price),
                                   "1",close_ms]],separators=(",",":")).encode()
            raw_path.write_bytes(raw_bytes)
            evidence={"contract":"FORECAST_SETTLEMENT_EVIDENCE_v1",
                      "forecast_id":fid,"forecast_sha256":sha(frozen),
                      "settlement_contract_version":frozen["settlement_contract_version"],
                      "settlement_target_utc":frozen["outcome_due_utc"],
                      "captured_at_utc":frozen["outcome_due_utc"],
                      "captured_at_semantics":"ADJUDICATION_TARGET_TIME_NOT_SOURCE_OBSERVATION",
                      "metric_path":frozen["metric_path"],
                      "source_candle_confirmed":True,
                      "source_candle_open_utc":prior.isoformat().replace("+00:00","Z"),
                      "source_candle_close_utc":(due-timedelta(milliseconds=1)).isoformat().replace("+00:00","Z"),
                      "source_candle_offset_seconds":-0.001,
                      "source_retrieved_at_utc":"2026-09-02T00:00:05Z",
                      "source_publication_lag_seconds":5,
                      "source_raw_path":f"raw/{fid}/source.json",
                      "source_raw_bytes":len(raw_bytes),
                      "source_raw_sha256":hashlib.sha256(raw_bytes).hexdigest(),
                      "source_id":"BINANCE_SPOT_MARKET_DATA_ONLY_KLINES",
                      "source_instrument":"BTCUSDT",
                      "authority":{"portfolio_action":False,"framework_state_change":False,
                                   "model_weight_change":False,"canonical_promotion":False,
                                   "scientific_skill_authority":False},
                      "market_metrics":{"spot":{"BTCUSDT":{"close":price}}}}
            (evidence_root/f"{fid}.json").write_text(json.dumps(evidence))
            outcome.setdefault("forecast_sha256",sha(frozen))
            outcome.setdefault("settlement_contract_version",frozen["settlement_contract_version"])
            outcome.setdefault("settlement_target_utc",frozen["outcome_due_utc"])
            outcome.setdefault("settlement_observation_utc",frozen["outcome_due_utc"])
            outcome.setdefault("settlement_offset_seconds",0)
            outcome.setdefault("start_value",100.0)
            outcome.setdefault("end_value",price)
            outcome.setdefault("return_pct",round((price/100.0-1.0)*100.0,8))
            outcome.setdefault("evidence_path",f"research/framework_memory/settlement_evidence/{fid}.json")
            outcome.setdefault("evidence_sha256",sha(evidence))
            (oc/f"{i}.json").write_text(json.dumps(outcome))
            binding={
                "contract":"FORECAST_SETTLEMENT_OUTCOME_BINDING_v1",
                "forecast_id":fid,"forecast_sha256":sha(frozen),
                "outcome_path":f"research/framework_memory/outcome_memory/{fid}.json",
                "outcome_sha256":sha(outcome),
                "evidence_path":f"research/framework_memory/settlement_evidence/{fid}.json",
                "evidence_sha256":sha(evidence),
                "settlement_target_utc":frozen["outcome_due_utc"],
            }
            binding["binding_sha256"]=sha(binding)
            (bindings/f"{fid}.json").write_text(json.dumps(binding))
        if outcomes:
            fixture_git("add", "raw", "outcomes", "settlement_bindings", "settlement_evidence")
            fixture_git("commit", "-qm", "first original settlement fixture", stamp="2026-09-02T00:00:06Z")
        fixture_git("push", "-q", "origin", "main")
        return registry(cr,ob,fr,oc,rc,"2026-10-18T00:00:00Z")

    @staticmethod
    def outcome(fid, *, status="MATURED", result="HIT", score=True, contract="MATURED_OUTCOME_v3"):
        return {"contract":contract,"forecast_id":fid,"status":status,
                "result":result,"scientific_score_eligible":score}

    def test_censored_only_is_retained_but_not_matured_or_scored(self):
        with tempfile.TemporaryDirectory() as td:
            r=self.sample_registry(Path(td),[self.outcome("EXP-FC-1",status="CENSORED",result=None,score=False)])
            c=r["candidates"][0]
            self.assertEqual(c["outcome_record_count"],1)
            self.assertEqual(c["censored_outcome_count"],1)
            self.assertEqual(c["matured_outcome_count"],0)
            self.assertEqual(c["scientific_score_eligible_outcome_count"],0)
            self.assertEqual(c["outcome_evidence_state"],"CENSORED_ONLY")
            self.assertEqual(c["state"],"WAITING_FOR_DATA")
            self.assertNotIn("MATURED_INCONCLUSIVE",r["state_counts"])

    def test_commit_clock_only_cannot_admit_matured_hit_or_miss(self):
        for result,expected in [("HIT","MATURED_SUPPORTED"),("MISS","MATURED_NOT_SUPPORTED")]:
            with self.subTest(result=result),tempfile.TemporaryDirectory() as td:
                r=self.sample_registry(Path(td),[self.outcome("EXP-FC-1",result=result)])
                c=r["candidates"][0]
                self.assertEqual(c["state"],"MATURED_INCONCLUSIVE")
                self.assertEqual(c["matured_outcome_count"],1)
                self.assertEqual(c["scientific_score_eligible_outcome_count"],0)
                self.assertEqual(c["censored_outcome_count"],0)

    def test_nonadmission_reports_only_reached_anchor_gate(self):
        with tempfile.TemporaryDirectory() as td:
            row = self.sample_registry(Path(td), [self.outcome("EXP-FC-1")])["candidates"][0]
            self.assertEqual(row["scientific_score_eligible_outcome_count"], 0)
            self.assertEqual(row["scientific_score_nonadmission_counts_v1"],
                             {"FORECAST_SOURCE_ANCHOR_REJECTED": 1})

    def test_nonadmission_does_not_attribute_precheck_failure_to_custody(self):
        with tempfile.TemporaryDirectory() as td:
            row = self.sample_registry(Path(td), [self.outcome("EXP-FC-1", score=False)])["candidates"][0]
            self.assertEqual(row["scientific_score_nonadmission_counts_v1"],
                             {"OUTCOME_PREREQUISITE_NOT_MET": 1})

    def test_nonadmission_reports_binding_failure_separately(self):
        from scripts.experiments.experiment_lifecycle import registry
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.sample_registry(root, [self.outcome("EXP-FC-1")])
            (root / "settlement_bindings/EXP-FC-1.json").unlink()
            row = registry(root/"candidates", root/"observations", root/"forecasts",
                           root/"outcomes", root/"receipts", "2026-10-18T01:00:00Z")["candidates"][0]
            self.assertEqual(row["scientific_score_nonadmission_counts_v1"],
                             {"BINDING_OR_OTHER_VALIDATION_REJECTED": 1})

    def test_nonadmission_second_anchor_and_positive_fixture(self):
        from unittest.mock import patch
        for answers, counts, expected in [
            ([True, False], {"SETTLEMENT_SOURCE_ANCHOR_REJECTED": 1}, 0),
            ([True, True], {}, 1),
        ]:
            with self.subTest(answers=answers), tempfile.TemporaryDirectory() as td:
                # Synthetic seam only: never claims a real trusted clock exists.
                with patch("scripts.experiments.source_git_anchor.AcceptedMainSource.matches",
                           side_effect=answers):
                    row = self.sample_registry(Path(td), [self.outcome("EXP-FC-1")])["candidates"][0]
                self.assertEqual(row["scientific_score_nonadmission_counts_v1"], counts)
                self.assertEqual(row["scientific_score_eligible_outcome_count"], expected)

    def test_physical_maturity_without_scientific_eligibility_never_promotes(self):
        for value in (False,None,"true"):
            with self.subTest(score=value),tempfile.TemporaryDirectory() as td:
                r=self.sample_registry(Path(td),[self.outcome("EXP-FC-1",score=value)])
                c=r["candidates"][0]
                self.assertEqual(c["matured_outcome_count"],1)
                self.assertEqual(c["scientific_score_eligible_outcome_count"],0)
                self.assertEqual(c["state"],"MATURED_INCONCLUSIVE")

    def test_mixed_eligible_and_censored_do_not_double_count(self):
        a=self.outcome("EXP-FC-1",result="MISS")
        b=self.outcome("EXP-FC-2",status="CENSORED",result=None,score=False)
        for records in ((a,b),(b,a)):
            with tempfile.TemporaryDirectory() as td:
                r=self.sample_registry(Path(td),list(records))
                c=r["candidates"][0]
                self.assertEqual(c["state"],"MATURED_INCONCLUSIVE")
                self.assertEqual(c["outcome_record_count"],2)
                self.assertEqual(c["matured_outcome_count"],1)
                self.assertEqual(c["censored_outcome_count"],1)
                self.assertEqual(c["scientific_score_eligible_outcome_count"],0)
                self.assertEqual(c["unknown_outcome_count"],0)

    def test_unknown_or_invalid_contract_is_not_a_matured_success(self):
        for case in (
            self.outcome("EXP-FC-1",status="UNKNOWN"),
            self.outcome("EXP-FC-1",contract="DUBIOUS_OUTCOME_v0"),
            self.outcome("EXP-FC-1",status="CENSORED",score=True),
        ):
            with tempfile.TemporaryDirectory() as td:
                r=self.sample_registry(Path(td),[case])
                c=r["candidates"][0]
                self.assertEqual(c["matured_outcome_count"],0)
                self.assertEqual(c["scientific_score_eligible_outcome_count"],0)
                self.assertEqual(c["state"],"WAITING_FOR_DATA")

    def test_forged_eligible_outcome_lineage_fails_closed(self):
        for patch in (
            {"forecast_sha256":"b"*64},
            {"settlement_target_utc":"2026-09-03T00:00:00Z"},
            {"settlement_observation_utc":"2026-09-02T00:00:01Z"},
            {"settlement_offset_seconds":60},
            {"settlement_contract_version":"LEGACY"},
            {"evidence_sha256":None},
        ):
            with tempfile.TemporaryDirectory() as td:
                row=dict(self.outcome("EXP-FC-1",result="HIT"),**patch)
                r=self.sample_registry(Path(td),[row])
                c=r["candidates"][0]
                self.assertEqual(c["matured_outcome_count"],1)
                self.assertEqual(c["scientific_score_eligible_outcome_count"],0)
                self.assertEqual(c["state"],"MATURED_INCONCLUSIVE")

    def test_one_forecast_id_cannot_serve_two_candidates(self):
        from scripts.experiments.experiment_lifecycle import registry
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); cr=root/"candidates"; fr=root/"forecasts"
            cr.mkdir();fr.mkdir()
            for i,cid in enumerate(("EC-one","EC-two")):
                (cr/f"{i}.json").write_text(json.dumps({
                    "contract":"EXPERIMENT_CANDIDATE_v1","candidate_id":cid,
                    "created_at_utc":"2026-09-01T00:00:00Z",
                    "spec":{"kind":"SENSOR_COMBINATION","title":cid}
                }))
                (fr/f"{i}.json").write_text(json.dumps({
                    "contract":"FROZEN_FORECAST_v1","forecast_id":"EXP-FC-shared",
                    "source_candidate_id":cid,
                }))
            with self.assertRaisesRegex(ValueError,"forecast_id_ownership_or_content_conflict"):
                registry(cr,root/"observations",fr,root/"outcomes",root/"receipts",
                         "2026-10-18T00:00:00Z")

    def test_original_archived_matured_hit_requires_independent_git_custody(self):
        from scripts.experiments.experiment_lifecycle import (
            read, outcome_bound_to_frozen_forecast)
        root=Path(__file__).parents[2]
        fid="EXP-FC-ed792257fedbaf1a4917"
        forecast=read(root/f"research/framework_memory/forecast_memory/2026/09/{fid}.json")
        outcome_root=root/"research/framework_memory/outcome_memory"
        outcome=read(outcome_root/f"{fid}.json")
        self.assertEqual(outcome["status"],"MATURED")
        self.assertEqual(outcome["result"],"HIT")
        # True historical status remains preserved. A matching binding alone
        # cannot establish first acceptance in the existing shallow CI clone.
        from unittest.mock import patch
        from scripts.experiments.source_git_anchor import SourceGitAnchorUnavailable
        with patch("scripts.experiments.source_git_anchor._git",
                   side_effect=SourceGitAnchorUnavailable("unavailable")):
            self.assertFalse(outcome_bound_to_frozen_forecast(outcome,forecast,outcome_root))

    def test_mutated_hit_after_binding_is_never_score_eligible(self):
        from scripts.experiments.experiment_lifecycle import registry
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            self.sample_registry(root,[self.outcome("EXP-FC-1",result="MISS")])
            source=root/"outcomes/0.json"
            altered=json.loads(source.read_text())
            altered["result"]="HIT"
            source.write_text(json.dumps(altered))
            r=registry(root/"candidates",root/"observations",root/"forecasts",
                       root/"outcomes",root/"receipts","2026-10-18T01:00:00Z")
            row=r["candidates"][0]
            self.assertEqual(row["matured_outcome_count"],1)
            self.assertEqual(row["scientific_score_eligible_outcome_count"],0)
            self.assertEqual(row["state"],"MATURED_INCONCLUSIVE")

    def test_joint_mutation_of_outcome_and_binding_cannot_forge_hit(self):
        from scripts.experiments.experiment_lifecycle import registry, sha
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            self.sample_registry(root,[self.outcome("EXP-FC-1",result="MISS")])
            source=root/"outcomes/0.json"
            binding=root/"settlement_bindings/EXP-FC-1.json"
            fake=json.loads(source.read_text())
            fake["result"]="HIT"
            source.write_text(json.dumps(fake))
            changed=json.loads(binding.read_text())
            changed["outcome_sha256"]=sha(fake)
            changed["binding_sha256"]=sha({k:v for k,v in changed.items()
                                            if k!="binding_sha256"})
            binding.write_text(json.dumps(changed))
            r=registry(root/"candidates",root/"observations",root/"forecasts",
                       root/"outcomes",root/"receipts","2026-10-18T01:00:00Z")
            row=r["candidates"][0]
            self.assertEqual(row["matured_outcome_count"],1)
            self.assertEqual(row["scientific_score_eligible_outcome_count"],0)
            self.assertEqual(row["state"],"MATURED_INCONCLUSIVE")

    def test_nonfinite_coherently_rehashed_market_evidence_cannot_be_eligible(self):
        from scripts.experiments.experiment_lifecycle import registry, sha
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            positive=self.sample_registry(root,[self.outcome("EXP-FC-1",result="HIT")])
            self.assertEqual(positive["candidates"][0]["scientific_score_eligible_outcome_count"],0)
            evidence_file=root/"settlement_evidence/EXP-FC-1.json"
            outcome_file=root/"outcomes/0.json"
            binding_file=root/"settlement_bindings/EXP-FC-1.json"
            evidence=json.loads(evidence_file.read_text())
            evidence["market_metrics"]["spot"]["BTCUSDT"]["close"]=float("inf")
            evidence_file.write_text(json.dumps(evidence))
            outcome=json.loads(outcome_file.read_text())
            outcome["end_value"]=float("inf")
            outcome["return_pct"]=float("inf")
            outcome["evidence_sha256"]=sha(evidence)
            outcome_file.write_text(json.dumps(outcome))
            binding=json.loads(binding_file.read_text())
            binding["evidence_sha256"]=sha(evidence)
            binding["outcome_sha256"]=sha(outcome)
            binding["binding_sha256"]=sha({k:v for k,v in binding.items() if k!="binding_sha256"})
            binding_file.write_text(json.dumps(binding))
            r=registry(root/"candidates",root/"observations",root/"forecasts",
                       root/"outcomes",root/"receipts","2026-10-18T01:00:00Z")
            row=r["candidates"][0]
            self.assertEqual(row["matured_outcome_count"],1)
            self.assertEqual(row["scientific_score_eligible_outcome_count"],0)
            self.assertEqual(row["state"],"MATURED_INCONCLUSIVE")

    def test_missing_or_mutated_binding_and_evidence_fail_closed(self):
        from scripts.experiments.experiment_lifecycle import registry
        for type_name in ("missing","mutated","missing_evidence","wrong_evidence"):
            with self.subTest(case=type_name),tempfile.TemporaryDirectory() as td:
                root=Path(td)
                self.sample_registry(root,[self.outcome("EXP-FC-1",result="HIT")])
                binding=root/"settlement_bindings/EXP-FC-1.json"
                evidence=root/"settlement_evidence/EXP-FC-1.json"
                if type_name=="missing":
                    binding.unlink()
                elif type_name=="mutated":
                    data=json.loads(binding.read_text())
                    data["outcome_sha256"]="f"*64
                    binding.write_text(json.dumps(data))
                elif type_name=="missing_evidence":
                    evidence.unlink()
                else:
                    data=json.loads(evidence.read_text())
                    data["forecast_sha256"]="f"*64
                    evidence.write_text(json.dumps(data))
                reg=registry(root/"candidates",root/"observations",root/"forecasts",
                             root/"outcomes",root/"receipts","2026-10-18T01:00:00Z")
                self.assertEqual(reg["candidates"][0]["scientific_score_eligible_outcome_count"],0)
                self.assertEqual(reg["candidates"][0]["state"],"MATURED_INCONCLUSIVE")

    def test_raw_receipt_digest_mismatch_never_scores_hit(self):
        from scripts.experiments.experiment_lifecycle import registry,sha
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            self.sample_registry(root,[self.outcome("EXP-FC-1",result="MISS")])
            # Forge a complete, mutually consistent fake HIT in outcome,
            # binding and evidence, without altering the original raw blob.
            outcome_path=root/"outcomes/0.json"
            evidence_path=root/"settlement_evidence/EXP-FC-1.json"
            binding_path=root/"settlement_bindings/EXP-FC-1.json"
            evidence=json.loads(evidence_path.read_text())
            evidence["market_metrics"]["spot"]["BTCUSDT"]["close"]=102.0
            evidence_path.write_text(json.dumps(evidence))
            outcome=json.loads(outcome_path.read_text())
            outcome["result"]="HIT"
            outcome["end_value"]=102.0
            outcome["return_pct"]=2.0
            outcome["evidence_sha256"]=sha(evidence)
            outcome_path.write_text(json.dumps(outcome))
            binding=json.loads(binding_path.read_text())
            binding["evidence_sha256"]=sha(evidence)
            binding["outcome_sha256"]=sha(outcome)
            binding["binding_sha256"]=sha({k:v for k,v in binding.items()
                                            if k!="binding_sha256"})
            binding_path.write_text(json.dumps(binding))
            r=registry(root/"candidates",root/"observations",root/"forecasts",
                       root/"outcomes",root/"receipts","2026-10-18T01:00:00Z")
            c=r["candidates"][0]
            self.assertEqual(c["scientific_score_eligible_outcome_count"],0)
            self.assertEqual(c["state"],"MATURED_INCONCLUSIVE")

    def test_missing_raw_receipt_never_scores_hit(self):
        from scripts.experiments.experiment_lifecycle import registry
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            self.sample_registry(root,[self.outcome("EXP-FC-1",result="HIT")])
            (root/"raw/EXP-FC-1/source.json").unlink()
            r=registry(root/"candidates",root/"observations",root/"forecasts",
                       root/"outcomes",root/"receipts","2026-10-18T01:00:00Z")
            self.assertEqual(r["candidates"][0]["scientific_score_eligible_outcome_count"],0)

    def test_joint_raw_evidence_outcome_binding_rewrite_cannot_forge_hit(self):
        import hashlib
        from scripts.experiments.experiment_lifecycle import registry, sha
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            fid = "EXP-FC-joint"
            original = self.sample_registry(root, [self.outcome(fid, result="MISS")])
            self.assertEqual(original["candidates"][0]["scientific_score_eligible_outcome_count"], 0)
            raw = root / "raw" / fid / "source.json"
            raw.write_bytes(raw.read_bytes().replace(b'"100.2"', b'"102.0"'))
            ep = root / "settlement_evidence" / f"{fid}.json"
            evidence = json.loads(ep.read_text())
            evidence["source_raw_bytes"] = len(raw.read_bytes())
            evidence["source_raw_sha256"] = hashlib.sha256(raw.read_bytes()).hexdigest()
            evidence["market_metrics"]["spot"]["BTCUSDT"]["close"] = 102.0
            ep.write_text(json.dumps(evidence))
            op = root / "outcomes/0.json"
            outcome = json.loads(op.read_text())
            outcome.update(result="HIT", end_value=102.0, return_pct=2.0,
                           evidence_sha256=sha(evidence))
            op.write_text(json.dumps(outcome))
            bp = root / "settlement_bindings" / f"{fid}.json"
            binding = json.loads(bp.read_text())
            binding.update(outcome_sha256=sha(outcome), evidence_sha256=sha(evidence))
            binding["binding_sha256"] = sha({k: v for k, v in binding.items() if k != "binding_sha256"})
            bp.write_text(json.dumps(binding))
            result = registry(root/"candidates", root/"observations", root/"forecasts",
                              root/"outcomes", root/"receipts", "2026-10-19T12:00:00Z")
            row = result["candidates"][0]
            self.assertEqual(row["matured_outcome_count"], 1)
            self.assertEqual(row["scientific_score_eligible_outcome_count"], 0)
            self.assertEqual(row["state"], "MATURED_INCONCLUSIVE")

    def test_relative_existing_registry_paths_preserve_anchored_positive(self):
        from contextlib import chdir
        from scripts.experiments.experiment_lifecycle import registry
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.sample_registry(root, [self.outcome("EXP-FC-relative", result="HIT")])
            with chdir(root):
                result = registry(Path("candidates"), Path("observations"), Path("forecasts"),
                                  Path("outcomes"), Path("receipts"), "2026-10-19T12:00:00Z")
            self.assertEqual(result["candidates"][0]["scientific_score_eligible_outcome_count"], 0)

    def test_forecast_first_published_after_due_is_unscoreable(self):
        from scripts.experiments.experiment_lifecycle import registry
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.sample_registry(root, [self.outcome("EXP-FC-late", result="HIT")])
            # Move canonical first acceptance to AFTER the forecast horizon.
            # A new Git trust root cannot backdate first-known merely via JSON.
            import subprocess
            tree = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD^{tree}"],
                                  check=True, capture_output=True, text=True).stdout.strip()
            late = subprocess.run(["git", "-C", str(root), "commit-tree", tree], input="late synthetic root\n",
                check=True, capture_output=True, text=True, env=dict(os.environ,
                GIT_AUTHOR_NAME="Fixture", GIT_AUTHOR_EMAIL="fixture@example.invalid",
                GIT_COMMITTER_NAME="Fixture", GIT_COMMITTER_EMAIL="fixture@example.invalid",
                GIT_AUTHOR_DATE="2026-09-03T00:00:00Z", GIT_COMMITTER_DATE="2026-09-03T00:00:00Z")).stdout.strip()
            # Only this isolated temporary test repository is rewritten.
            subprocess.run(["git", "--git-dir", str(root/".fixture-origin.git"),
                            "fetch", "-q", str(root), late+":refs/heads/late"], check=True)
            subprocess.run(["git", "--git-dir", str(root/".fixture-origin.git"),
                            "symbolic-ref", "HEAD", "refs/heads/late"], check=True)
            subprocess.run(["git", "--git-dir", str(root/".fixture-origin.git"),
                            "update-ref", "refs/heads/main", late], check=True)
            result = registry(root/"candidates", root/"observations", root/"forecasts",
                              root/"outcomes", root/"receipts", "2026-10-19T12:00:00Z")
            self.assertEqual(result["candidates"][0]["scientific_score_eligible_outcome_count"], 0)

    def test_duplicate_forecast_outcomes_are_not_order_dependent(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,"duplicate_outcome_forecast_id"):
                self.sample_registry(Path(td),[
                    self.outcome("EXP-FC-1",result="HIT"),
                    self.outcome("EXP-FC-1",result="MISS")
                ],forecasts=["EXP-FC-1"])

    def test_real_archived_censored_case_stays_nonmatured(self):
        from scripts.experiments.experiment_lifecycle import registry
        repo=Path(__file__).parents[2]
        rootid="EXP-FC-40f5d94a716bbd284cd7"
        fixture=[
            ("candidates",f"research/experiment_lifecycle/candidates/2026/08/EC-01d8e20aee64058a00b7.json"),
            ("forecasts",f"research/framework_memory/forecast_memory/2026/08/{rootid}.json"),
            ("outcomes",f"research/framework_memory/outcome_memory/{rootid}.json"),
        ]
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for folder,relpath in fixture:
                (root/folder).mkdir(parents=True,exist_ok=True)
                (root/folder/"one.json").write_bytes((repo/relpath).read_bytes())
            observed=json.loads((root/"outcomes/one.json").read_text())
            self.assertEqual(observed["status"],"CENSORED")
            r=registry(root/"candidates",root/"observations",root/"forecasts",
                       root/"outcomes",root/"receipts","2026-10-18T00:00:00Z")
            c=r["candidates"][0]
            self.assertEqual((c["outcome_record_count"],c["matured_outcome_count"],
                              c["censored_outcome_count"]),(1,0,1))
            self.assertEqual(c["state"],"WAITING_FOR_DATA")

    def test_missing_forecast_outcome_is_not_inferred_from_any_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            r=self.sample_registry(Path(td),[],forecasts=["EXP-FC-missing"])
            c=r["candidates"][0]
            self.assertEqual(c["outcome_record_count"],0)
            self.assertEqual(c["matured_outcome_count"],0)
            self.assertEqual(c["state"],"WAITING_FOR_MATURITY")

    def test_corrected_censored_registry_is_compatible_with_existing_consumers(self):
        from scripts.experiments.build_experiment_yield_shadow import build_shadow
        from scripts.experiments.unified_experimental_adjudication import candidate_action
        from scripts.research.monthly_ai_learning_council import compact_experiment_registry
        with tempfile.TemporaryDirectory() as td:
            r = self.sample_registry(Path(td), [self.outcome(
                "EXP-FC-1", status="CENSORED", result=None, score=False)])
            self.assertEqual(r["contract"], "EXPERIMENT_LIFECYCLE_REGISTRY_v1")
            self.assertEqual(r["contract_revision"], "1.1")
            self.assertEqual(r["outcome_count_contract"], "EXPERIMENT_OUTCOME_COUNTS_v2")
            before = json.dumps(r, sort_keys=True)
            compact = compact_experiment_registry(r)
            shadow = build_shadow(r, {"rows": []})
            action = candidate_action(r["candidates"][0], None)
            self.assertEqual(compact["matured_candidates"], [])
            self.assertEqual(shadow["summary"]["waiting_count"], 1)
            self.assertEqual(shadow["summary"]["matured_count"], 0)
            self.assertEqual(shadow["summary"]["with_matured_outcomes_count"], 0)
            self.assertEqual(action["selected_action"], "WAIT_FOR_MORE_PROSPECTIVE_EVIDENCE")
            self.assertFalse(action["canonical_effect"])
            self.assertFalse(action["portfolio_execution"])
            self.assertEqual(json.dumps(r, sort_keys=True), before)

    def test_true_matured_registry_retains_existing_review_only_consumer_behavior(self):
        from scripts.experiments.build_experiment_yield_shadow import build_shadow
        from scripts.experiments.unified_experimental_adjudication import candidate_action
        from scripts.research.monthly_ai_learning_council import compact_experiment_registry
        with tempfile.TemporaryDirectory() as td:
            r = self.sample_registry(Path(td), [self.outcome("EXP-FC-1")])
            self.assertEqual(len(compact_experiment_registry(r)["matured_candidates"]), 1)
            self.assertEqual(build_shadow(r, {"rows": []})["summary"]["matured_count"], 1)
            action = candidate_action(r["candidates"][0], None)
            self.assertEqual(action["selected_action"], "KEEP_SHADOW_INCONCLUSIVE")
            self.assertFalse(action["canonical_effect"])
            self.assertFalse(action["portfolio_execution"])

    def test_full_original_corpus_nonadmission_and_legacy_parity(self):
        """Replay old and new registry loops on the EXACT SAME entire tree.

        Reverse ONLY the diagnostic loop and emitted diagnostic field with the
        prior reviewed code. No stale publication snapshot is a comparator.
        """
        import inspect
        import scripts.experiments.experiment_lifecycle as lifecycle

        repo = Path(__file__).resolve().parents[2]
        roots = (
            repo / "research/experiment_lifecycle/candidates",
            repo / "research/experiment_lifecycle/observations",
            repo / "research/framework_memory/forecast_memory",
            repo / "research/framework_memory/outcome_memory",
            repo / "research/experiment_lifecycle/receipts",
        )
        for path in roots:
            self.assertTrue(path.is_dir(), f"FULL_CORPUS_INPUT_UNAVAILABLE:{path}")
        baseline_file = repo / "research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json"
        self.assertTrue(baseline_file.is_file(), "MISSING_PINNED_PRODUCTION_CENSUS")
        last_published = json.loads(baseline_file.read_text(encoding="utf-8"))
        self.assertGreaterEqual(last_published["candidate_count"], 650)
        self.assertEqual(last_published["candidate_count"], len(last_published["candidates"]))

        # This literal is the EXACT old, status-eligible original comprehension
        # from the reviewed PR base, not another call to the new diagnostics.
        diagnostic_loop = r'''        eligible = []
        nonadmission_counts = {}
        for item in matured:
            forecast_id = item.get("forecast_id")
            reason = []
            if (item.get("scientific_score_eligible") is not True
                    or item.get("result") not in {"HIT", "MISS"}
                    or forecast_id not in original_forecasts
                    or original_forecasts[forecast_id][0] != candidate_id):
                reason.append("OUTCOME_PREREQUISITE_NOT_MET")
            elif outcome_bound_to_frozen_forecast(
                    item, original_forecasts[forecast_id][1], outcome_root,
                    source_anchor=source_anchor,
                    forecast_path=original_forecast_paths[forecast_id],
                    nonadmission=reason):
                eligible.append(item)
            else:
                if not reason:
                    reason.append("BINDING_OR_OTHER_VALIDATION_REJECTED")
            if reason:
                nonadmission_counts[reason[0]] = nonadmission_counts.get(reason[0], 0) + 1
'''
        original_loop = r'''        eligible = [item for item in matured
                    if item.get("scientific_score_eligible") is True
                    and item.get("result") in {"HIT", "MISS"}
                    and item.get("forecast_id") in original_forecasts
                    and original_forecasts[item["forecast_id"]][0] == candidate_id
                    and outcome_bound_to_frozen_forecast(
                        item, original_forecasts[item["forecast_id"]][1], outcome_root,
                        source_anchor=source_anchor,
                        forecast_path=original_forecast_paths[item["forecast_id"]])]
'''
        diagnostic_field = '            "scientific_score_nonadmission_counts_v1": nonadmission_counts,\n'
        live_source = inspect.getsource(lifecycle.registry)
        self.assertEqual(live_source.count(diagnostic_loop), 1, "DIAGNOSTIC_LOOP_DRIFT")
        self.assertEqual(live_source.count(diagnostic_field), 1, "DIAGNOSTIC_FIELD_DRIFT")
        original_source = (
            live_source.replace(diagnostic_loop, original_loop, 1)
            .replace(diagnostic_field, "", 1)
        )
        original_scope = vars(lifecycle).copy()
        exec(compile(original_source, "<exact-legacy-registry>", "exec"), original_scope)
        old_registry = original_scope["registry"]

        now = last_published["generated_at_utc"]
        old = old_registry(*roots, now)
        current = lifecycle.registry(*roots, now)
        self.assertGreaterEqual(old["candidate_count"], 650)
        self.assertEqual(len(old["candidates"]), old["candidate_count"])
        self.assertEqual(len(current["candidates"]), current["candidate_count"])
        normalized = {
            **current,
            "candidates": [
                {k: v for k, v in row.items()
                 if k != "scientific_score_nonadmission_counts_v1"}
                for row in current["candidates"]
            ],
        }
        # Root contract, all original candidate fields, state/counts and
        # scientific eligibility must remain identical on the same inputs.
        self.assertEqual(normalized, old, "SAME_TREE_LEGACY_FIELDS_DRIFT")

        totals = {"matured": 0, "eligible": 0, "nonadmitted": 0}
        allowed = {
            "OUTCOME_PREREQUISITE_NOT_MET",
            "FORECAST_SOURCE_ANCHOR_REJECTED",
            "SETTLEMENT_SOURCE_ANCHOR_REJECTED",
            "BINDING_OR_OTHER_VALIDATION_REJECTED",
        }
        for row in current["candidates"]:
            reasons = row["scientific_score_nonadmission_counts_v1"]
            self.assertIsInstance(reasons, dict)
            self.assertTrue(set(reasons).issubset(allowed), row["candidate_id"])
            self.assertTrue(all(type(count) is int and count > 0
                                for count in reasons.values()), row["candidate_id"])
            matured = row["matured_outcome_count"]
            eligible = row["scientific_score_eligible_outcome_count"]
            self.assertEqual(sum(reasons.values()), matured - eligible,
                             f"FIRST_REACHED_REASON_CONSERVATION:{row['candidate_id']}")
            totals["matured"] += matured
            totals["eligible"] += eligible
            totals["nonadmitted"] += sum(reasons.values())
        self.assertGreaterEqual(totals["matured"], 1272)
        self.assertEqual(totals["nonadmitted"], totals["matured"] - totals["eligible"])
        self.assertEqual(current["authority"], "SHADOW_ONLY_NO_AUTOMATIC_PROMOTION")
        print("FULL_CORPUS_OLD_NEW_SAME_TREE_PARITY_PASS " + json.dumps({
            "candidates": current["candidate_count"],
            "matured": totals["matured"],
            "eligible": totals["eligible"],
            "nonadmitted": totals["nonadmitted"],
            "legacy_fields_equal": True,
        }, sort_keys=True))

    def test_old_adjudication_fails_existing_state_and_count_drift_gates(self):
        # The existing CLI consumer uses a sibling-module import.
        sys.path.insert(0, str(Path(__file__).parents[2] / "scripts/research"))
        try:
            from scripts.research.compounding_learning_v1_core import _current
        finally:
            sys.path.pop(0)
        with tempfile.TemporaryDirectory() as td:
            r = self.sample_registry(Path(td), [self.outcome(
                "EXP-FC-1", status="CENSORED", result=None, score=False)])
            candidate = r["candidates"][0]
            prior = {"lifecycle_state": "MATURED_INCONCLUSIVE",
                     "matured_outcome_count": 1, "canonical_effect": False,
                     "portfolio_execution": False}
            original = dict(prior)
            self.assertEqual(_current(candidate, {}, prior), (False, "LIFECYCLE_STATE_DRIFT"))
            self.assertEqual(prior, original)
            prior["lifecycle_state"] = candidate["state"]
            self.assertEqual(_current(candidate, {}, prior), (False, "MATURED_COUNT_DRIFT"))
            prior["matured_outcome_count"] = 0
            self.assertEqual(_current(candidate, {}, prior), (True, "CURRENT"))

if __name__ == "__main__": unittest.main()
