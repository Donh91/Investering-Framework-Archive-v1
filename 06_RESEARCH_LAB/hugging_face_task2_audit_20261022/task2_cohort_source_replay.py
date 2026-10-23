#!/usr/bin/env python3
"""Finite, value-free source replay for the eleven original Task2 forecasts.

No outcomes, scores, provider requests, scientific promotion or original writes.
Imports the frozen single-row audit helpers. Server timing receipts are supplied
by the coordinator from original GitHub logs, not re-authenticated by this audit.
"""
from __future__ import annotations
import argparse
import ast
import copy
import csv
import hashlib
import importlib.util
import io
import json
import math
import subprocess
import typing
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

HELPER_SHA = "9da0e8d880aced3861b3008c8d33e6dcc41b6a5c73fd8ea7e8fcefca525e0859"
ENGINE_BLOB = "d00d38bed517861fa2487dce42d330bf05812f6d"
ENGINE_PATH = "scripts/data_ping/native_handlekompas.py"
PRODUCER_PATH = "scripts/data_ping/auto_market_state.py"
COORDINATOR_METADATA_SHA256 = {
    "cohort_packet_refs.json": "fa1bf235d121797fed96670ec2fcc6ed7462196560eb3e0c118624c1abf0dede",
    "cohort_hourly_bindings.json": "218033bf1b3b499dd70ee160022814121b3a813e0abaea22c44d83b3f5fa6b83",
    "cohort_packet_publications.json": "abf78a1ea0a198788d22c60d488478bf0952c35a90e6c37e81033d3119d09bd1",
}
ENGINE_FUNCTIONS = {"nested", "finite", "_delta_pct", "_parse_utc", "owner_freshness", "_health_ok",
                    "action_context", "derive_market_now", "_cn_decision_projection", "_cn_direction",
                    "_cn_projection_summary", "_unavailable_horizon", "_altcoin_cycle_lane", "horizon_map"}
SYMBOLS = (("BTCUSDT", "btc_usdt", "btc_delta_since_prior_packet_pct", "btc_close"),
           ("ETHUSDT", "eth_usdt", "eth_delta_since_prior_packet_pct", "eth_close"),
           ("ETHBTC", "ethbtc", "ethbtc_delta_since_prior_packet_pct", "ethbtc_close"))


def load_helpers(path):
    if hashlib.sha256(path.read_bytes()).hexdigest() != HELPER_SHA:
        raise RuntimeError("FROZEN_HELPER_HASH_MISMATCH")
    spec = importlib.util.spec_from_file_location("task2_original_audit_helpers", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git_blob(repo, commit, path):
    return subprocess.check_output(["git", "--no-replace-objects", "-C", str(repo), "rev-parse",
                                    "--verify", f"{commit}:{path}"], stderr=subprocess.DEVNULL).decode().strip()


def original_json(root, filename, expected_blob, h):
    raw = (root / filename).read_bytes()
    h.require(h.blob(raw) == expected_blob, "ORIGINAL_LOCAL_GIT_BLOB_MISMATCH")
    return raw, json.loads(raw)


def compile_original(repo, forecast, packet, cache, h):
    engine_commit = forecast["bound_main_sha"]
    h.require(git_blob(repo, engine_commit, ENGINE_PATH) == ENGINE_BLOB, "ORIGINAL_FORECAST_ENGINE_MEMBERSHIP_MISMATCH")
    snapshot = packet["source_snapshot"]["exact_commit_sha"]
    producer_blob = git_blob(repo, snapshot, PRODUCER_PATH)
    registry_path = packet["source_registry_path"]
    registry_blob = git_blob(repo, snapshot, registry_path)
    key = (producer_blob, registry_blob)
    if key not in cache:
        ns = {"Any": typing.Any, "Mapping": typing.Mapping, "math": math,
              "datetime": datetime, "timedelta": timedelta, "timezone": timezone}
        engine_raw = h.git_file(repo, engine_commit, ENGINE_PATH, ENGINE_BLOB)
        h.functions(engine_raw, ENGINE_FUNCTIONS, ns)
        ns["HORIZON_ORDER"] = ("NEXT_12H", "NEXT_1_3D", "NEXT_5_7D", "NEXT_2_3W", "CYCLE_ALTCOINS_3_8W")
        producer_raw = h.git_file(repo, snapshot, PRODUCER_PATH, producer_blob)
        tree = h.functions(producer_raw, {"num", "delta", "decision_lanes"}, ns)
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "LANES" for t in node.targets):
                ns["LANES"] = ast.literal_eval(node.value)
        registry = json.loads(h.git_file(repo, snapshot, registry_path, registry_blob))
        cache[key] = (ns, ns["decision_lanes"](registry))
    ns, required = cache[key]
    return ns, required, {"engine_commit": engine_commit, "engine_git_blob": ENGINE_BLOB,
                          "source_snapshot": snapshot, "producer_git_blob": producer_blob,
                          "registry_git_blob": registry_blob}


def binding_fields_match(actual, declared, h):
    for key in ("exact_commit_sha", "exact_path", "git_blob_sha", "raw_response_sha256"):
        h.require(actual.get(key) == declared.get(key), "PACKET_HOURLY_SOURCE_CROSS_BINDING_MISMATCH")


def validate(bundle, h):
    """Semantic validation after immutable local-file identity preflight."""
    f, p, prior, target, bound = (bundle[k] for k in ("forecast", "packet", "prior", "target", "binding"))
    ns, required = bundle["namespace"], bundle["required"]
    for doc, field in ((f, "compass_sha256"), (p, "packet_sha256"), (prior, "packet_sha256")):
        h.require(h.sha(h.canonical(doc, field)) == doc[field], "ORIGINAL_CANONICAL_SELF_HASH_MISMATCH")
    h.reference(f["source_bindings"]["auto_market_state"]["packet_sha256"], p["packet_sha256"])
    h.reference(p["predecessor"]["packet_sha256"], prior["packet_sha256"])
    h.require(f["source_bindings"]["auto_market_state"]["source_snapshot_commit_sha"] == p["source_snapshot"]["exact_commit_sha"],
              "FORECAST_PACKET_SNAPSHOT_BINDING_MISMATCH")
    hourly_health = p["source_health"]["hourly_market"]
    binding_fields_match(hourly_health["provenance"]["target"], bound["target"], h)
    binding_fields_match(hourly_health["row"]["provenance"], bound["csv"], h)
    h.require(bound["target"]["exact_commit_sha"] == bound["csv"]["exact_commit_sha"] == p["source_snapshot"]["exact_commit_sha"],
              "ORIGINAL_TARGET_CSV_SNAPSHOT_MISMATCH")
    h.require(h.sha(bundle["target_raw"]) == bound["target"]["raw_response_sha256"]
              and h.sha(bundle["csv_raw"]) == bound["csv"]["raw_response_sha256"], "ORIGINAL_TARGET_CSV_CONTENT_HASH_MISMATCH")
    h.require(len(bundle["archive"]) == bound["bytes"] and h.sha(bundle["archive"]) == bound["sha256"],
              "ORIGINAL_HOURLY_ARCHIVE_MISMATCH")
    h.availability(bound["upload_completed_at_utc"], f["issued_at_utc"])
    h.availability(bound["source_job_completed_at_utc"], f["issued_at_utc"])
    expected_blockers = [x for x in required if p["source_health"].get(x, {}).get("status") != "PASS"]
    h.require(p["blockers"] == expected_blockers, "ORIGINAL_REQUIRED_HEALTH_PREDICATE_MISMATCH")
    h.require(p["decision_context_status"] == ("PASS" if not expected_blockers else "DEGRADED"), "ORIGINAL_DECISION_HEALTH_MISMATCH")
    h.require(ns["_health_ok"](p, h.stamp(f["issued_at_utc"])), "ORIGINAL_ISSUANCE_HEALTH_GATE_FAILED")
    features = {x["feature_id"]: x for x in f["evidence_snapshot"]["selected_features"]}
    receipts = {x["name"]: x for x in target["source_records"]}
    csv_rows = list(csv.DictReader(io.StringIO(bundle["csv_raw"].decode("utf-8-sig"))))
    results = []
    with zipfile.ZipFile(io.BytesIO(bundle["archive"])) as z:
        h.require(len(z.namelist()) == len(set(z.namelist())), "DUPLICATE_HOURLY_ARCHIVE_MEMBER")
        for symbol, key, selected_delta, column in SYMBOLS:
            raw = z.read(symbol + "_spot.json")
            h.require(h.sha(raw) == receipts[symbol + "_spot"]["sha256"], "ORIGINAL_SPOT_MEMBER_HASH_MISMATCH")
            rows = json.loads(raw)
            def exact_row(stamp):
                ms = int(h.stamp(stamp).timestamp() * 1000)
                found = [x for x in rows if int(x[0]) == ms]
                h.require(len(found) == 1, "ORIGINAL_SPOT_EXACT_ROW_MISSING_OR_DUPLICATE")
                h.require(int(found[0][6]) < h.stamp(bound["source_job_completed_at_utc"]).timestamp() * 1000,
                          "ORIGINAL_SPOT_ROW_NOT_CLOSED_BEFORE_AVAILABILITY_BOUND")
                return found[0]
            current_stamp = p["normalized_state"]["live_market"]["observation_open_utc"]
            prior_stamp = prior["normalized_state"]["live_market"]["observation_open_utc"]
            current, previous = exact_row(current_stamp), exact_row(prior_stamp)
            cv, pv = p["normalized_state"]["live_market"][key], prior["normalized_state"]["scalar_values"][key]
            h.require(float(current[4]) == cv and float(previous[4]) == pv, "RAW_TO_ORIGINAL_PRICE_INPUT_MISMATCH")
            current_csv = [x for x in csv_rows if x["timestamp_utc"] == current_stamp]
            h.require(len(current_csv) == 1 and float(current_csv[0][column]) == cv, "ORIGINAL_CSV_CURRENT_PRICE_MISMATCH")
            h.require(ns["delta"](cv, pv) == p["deltas_since_prior_auto_packet"][key], "ORIGINAL_DELTA_TRANSFORMATION_MISMATCH")
            h.require(features[key]["value"] == cv and features[selected_delta]["value"] == p["deltas_since_prior_auto_packet"][key]["pct"],
                      "ORIGINAL_SELECTED_FEATURE_BINDING_MISMATCH")
            results.append({"symbol": symbol, "raw_member_sha256": h.sha(raw), "raw_rows": len(rows),
                            "closed_current_prior_raw_csv_and_delta_equal": True})
    action = ns["action_context"](p, as_of=h.stamp(f["issued_at_utc"]))
    market = ns["derive_market_now"](p, action, as_of=h.stamp(f["issued_at_utc"]))
    horizon = ns["horizon_map"](p, action, None, as_of=h.stamp(f["issued_at_utc"]))["NEXT_12H"]
    h.require(action == f["native_action_contract"] and market == f["market_now"], "ORIGINAL_ENGINE_ACTION_OR_MARKET_REPLAY_MISMATCH")
    h.require(horizon["expected_direction"] == f["horizons"]["NEXT_12H"]["expected_direction"], "ORIGINAL_12H_DIRECTION_REPLAY_MISMATCH")
    return results


def local_file(root, metadata, prefix, suffix, h):
    filename = metadata.get("local_filename") or f"{prefix}-{metadata['git_blob_sha']}{suffix}"
    h.require(Path(filename).name == filename, "UNSAFE_LOCAL_METADATA_FILENAME")
    return original_json(root, filename, metadata["git_blob_sha"], h)


def prepare(root, repo, manifest_members, ref, bound, cache, h):
    fid = ref["forecast_id"]
    def custody(filename):
        raw = (root / filename).read_bytes()
        member = manifest_members[filename]
        h.require(len(raw) == member["bytes"] and h.sha(raw) == member["sha256"], "ORIGINAL_CUSTODY_MEMBER_MISMATCH")
        return raw, json.loads(raw)
    _, f = custody(fid + ".json")
    packet_raw, p = custody(ref["packet_filename"])
    h.require(h.blob(packet_raw) == ref["packet_git_blob_sha"] and f["compass_id"] == fid, "ORIGINAL_FORECAST_PACKET_ID_MISMATCH")
    h.require(ref["engine_commit"] == f["bound_main_sha"] and ref["snapshot"] == p["source_snapshot"]["exact_commit_sha"],
              "ORIGINAL_FORECAST_CODE_REFERENCE_MISMATCH")
    predecessor_blob = git_blob(repo, ref["snapshot"], ref["predecessor_path"])
    h.require(predecessor_blob == ref.get("predecessor_git_blob_sha", predecessor_blob), "ORIGINAL_PREDECESSOR_GIT_REFERENCE_MISMATCH")
    prior_meta = {"git_blob_sha": predecessor_blob, "local_filename": ref.get("predecessor_filename") or f"predecessor-{predecessor_blob}.json"}
    _, prior = local_file(root, prior_meta, "predecessor", ".json", h)
    target_raw, target = local_file(root, bound["target"], "hourly-target", ".json", h)
    for source in (bound["target"], bound["csv"]):
        h.require(git_blob(repo, source["exact_commit_sha"], source["exact_path"]) == source["git_blob_sha"],
                  "ORIGINAL_HOURLY_TARGET_OR_CSV_SNAPSHOT_MEMBERSHIP_MISMATCH")
    csv_filename = bound["csv"].get("local_filename") or f"hourly-csv-{bound['csv']['git_blob_sha']}.csv"
    h.require(Path(csv_filename).name == csv_filename, "UNSAFE_LOCAL_CSV_FILENAME")
    csv_raw = (root / csv_filename).read_bytes()
    h.require(Path(csv_filename).name == csv_filename and h.blob(csv_raw) == bound["csv"]["git_blob_sha"], "ORIGINAL_CSV_GIT_BLOB_MISMATCH")
    ns, required, code = compile_original(repo, f, p, cache, h)
    return {"forecast": f, "packet": p, "prior": prior, "target": target, "target_raw": target_raw,
            "csv_raw": csv_raw, "binding": bound, "archive": (root / f"hourly-source-{bound['run_id']}.zip").read_bytes(),
            "namespace": ns, "required": required, "code": code, "predecessor_git_blob": predecessor_blob}


def publication_status(ref, bundle, repo, h):
    pub = ref.get("packet_publication")
    if not pub or pub.get("server_log_commit_binding_verified") is not True:
        return {"status": "UNVERIFIED", "source_chain_complete": False}
    h.require(pub.get("publication_job_conclusion") == "success", "ORIGINAL_PACKET_PUBLICATION_JOB_NOT_SUCCESS")
    h.availability(pub["publication_job_completed_at_utc"], bundle["forecast"]["issued_at_utc"])
    h.availability(pub["remote_push_reported_at_utc"], bundle["forecast"]["issued_at_utc"])
    path = bundle["forecast"]["source_bindings"]["auto_market_state"]["packet_path"]
    h.require(pub["path"] == path and pub["issued"] == bundle["forecast"]["issued_at_utc"], "PACKET_PUBLICATION_FORECAST_CROSS_BINDING_MISMATCH")
    raw = h.git_file(repo, pub["publication_commit_sha"], path, ref["packet_git_blob_sha"])
    h.require(json.loads(raw)["packet_sha256"] == bundle["packet"]["packet_sha256"], "PUBLISHED_ORIGINAL_PACKET_CONTENT_MISMATCH")
    return {"status": "COORDINATOR_BOUND_ORIGINAL_SERVER_SUCCESS_BEFORE_ISSUE", "source_chain_complete": True,
            **{k: pub[k] for k in ("run_id", "publication_commit_sha", "publication_job_id", "publication_job_conclusion",
                                   "publication_job_completed_at_utc", "remote_push_reported_at_utc", "server_log_commit_binding_verified")}}


def semantic_controls(bundle, h):
    """Run intended failures through the same semantic validator after identity preflight."""
    cases = []
    bad = dict(bundle)
    bad["archive"] = bundle["archive"] + b"corruption"
    cases.append(("corrupted_archive", bad, "ORIGINAL_HOURLY_ARCHIVE_MISMATCH"))
    bad = dict(bundle)
    bad["binding"] = copy.deepcopy(bundle["binding"])
    bad["binding"]["source_job_completed_at_utc"] = (h.stamp(bundle["forecast"]["issued_at_utc"]) + timedelta(seconds=1)).isoformat()
    cases.append(("future_availability", bad, "AVAILABILITY_NOT_BEFORE_ISSUE"))
    for label in ("wrong_predecessor_binding", "missing_required_health"):
        bad = dict(bundle)
        bad["packet"], bad["forecast"] = copy.deepcopy(bundle["packet"]), copy.deepcopy(bundle["forecast"])
        if label == "wrong_predecessor_binding":
            bad["packet"]["predecessor"]["packet_sha256"] = "0" * 64
            expected = "ORIGINAL_PACKET_REFERENCE_MISMATCH"
        else:
            bad["packet"]["source_health"][bundle["required"][0]]["status"] = "UNAVAILABLE"
            expected = "ORIGINAL_REQUIRED_HEALTH_PREDICATE_MISMATCH"
        bad["packet"]["packet_sha256"] = h.sha(h.canonical(bad["packet"], "packet_sha256"))
        bad["forecast"]["source_bindings"]["auto_market_state"]["packet_sha256"] = bad["packet"]["packet_sha256"]
        bad["forecast"]["compass_sha256"] = h.sha(h.canonical(bad["forecast"], "compass_sha256"))
        cases.append((label, bad, expected))
    output = {}
    for label, bad, expected in cases:
        try:
            validate(bad, h)
            output[label] = {"rejected_for_intended_reason": False}
        except h.AuditError as exc:
            output[label] = {"rejected_for_intended_reason": str(exc) == expected, "check": str(exc)}
    return output


def run(root, repo, h):
    raw = (root / "custody_manifest.json").read_bytes()
    h.require(h.blob(raw) == "f708e6ee97b40dfc56c06b896e6347a60911b5d8", "ORIGINAL_CUSTODY_MANIFEST_MISMATCH")
    members = {x["path"]: x for x in json.loads(raw)["members"]}
    metadata = {}
    for filename, expected in COORDINATOR_METADATA_SHA256.items():
        raw = (root / filename).read_bytes()
        h.require(h.sha(raw) == expected, "COORDINATOR_METADATA_RECEIPT_HASH_MISMATCH")
        metadata[filename] = json.loads(raw)
    refs = metadata["cohort_packet_refs.json"]
    publications = {x["id"]: x for x in metadata["cohort_packet_publications.json"]}
    for ref in refs:
        ref["packet_publication"] = publications.get(ref["forecast_id"])
    hourly = metadata["cohort_hourly_bindings.json"]
    expected_ids = {Path(x).stem for x in members if x.startswith("CMP-") and x.endswith(".json")}
    h.require(len(refs) == len(expected_ids) == 11 and {x["forecast_id"] for x in refs} == expected_ids,
              "COMPLETE_ORIGINAL_COHORT_REFERENCE_CENSUS_MISMATCH")
    by_forecast = {}
    for bound in hourly:
        for f in bound["forecasts"]:
            h.require(f["id"] not in by_forecast, "DUPLICATE_ORIGINAL_HOURLY_BINDING")
            by_forecast[f["id"]] = bound
    results, cache, controls = [], {}, None
    for ref in refs:
        row = {"forecast_id": ref["forecast_id"], "numeric_source_and_original_replay_passed": False,
               "scope_specific_source_chain_complete": False, "full_R1_admitted": False}
        try:
            h.require(ref["forecast_id"] in by_forecast, "ORIGINAL_HOURLY_BINDING_UNAVAILABLE")
            bundle = prepare(root, repo, members, ref, by_forecast[ref["forecast_id"]], cache, h)
            comparisons = validate(bundle, h)
            publication = publication_status(ref, bundle, repo, h)
            row.update({"numeric_source_and_original_replay_passed": True, "code_bindings": bundle["code"],
                        "predecessor_git_blob": bundle["predecessor_git_blob"], "price_comparisons": comparisons,
                        "required_health_lane_count": len(bundle["required"]), "packet_publication": publication,
                        "hourly_source_run_id": bundle["binding"]["run_id"], "hourly_source_artifact_sha256": bundle["binding"]["sha256"],
                        "hourly_source_availability_upper_bound_utc": bundle["binding"]["source_job_completed_at_utc"],
                        "scope_specific_source_chain_complete": publication["source_chain_complete"]})
            if controls is None:
                controls = semantic_controls(bundle, h)
        except Exception as exc:
            row["source_blocker"] = str(exc) if isinstance(exc, h.AuditError) else type(exc).__name__
        results.append(row)
    return {"contract": "TASK2_ORIGINAL_11_COHORT_SCOPED_12H_SOURCE_REPLAY_v1", "scope": "ORIGINAL_12H_DIRECTION_DEVELOPMENT_ONLY",
            "rows": results, "summary": {"original_forecasts": 11,
             "numeric_source_and_original_replay_passed": sum(x["numeric_source_and_original_replay_passed"] for x in results),
             "scope_specific_source_chain_complete": sum(x["scope_specific_source_chain_complete"] for x in results),
             "full_R1_automatic_admissions": 0}, "semantic_negative_controls": controls,
            "negative_control_semantics": "Same semantic validation path after immutable identity preflight; synthetic self-hashes recomputed to reach intended binding/health checks. No claim of guard-removal mutation sensitivity.",
            "server_timing_semantics": "Coordinator-bound original GitHub logs, not independently reauthenticated by this offline harness",
            "outcomes_read_or_scored": False, "provider_exact_first_publication_verified": False,
            "full_compass_or_investor_economics_admitted": False, "frozen_original_ledger_changed": False,
            "independent_market_event_count": None, "untouched_holdout": False}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--evidence-root", type=Path, required=True)
    ap.add_argument("--repo-root", type=Path, required=True)
    ap.add_argument("--helpers", type=Path, default=Path(__file__).with_name("task2_scoped_source_replay.py"))
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    try:
        h = load_helpers(args.helpers)
        result = run(args.evidence_root, args.repo_root, h)
    except Exception as exc:
        print(json.dumps({"status": "FAIL_COHORT_PREFLIGHT", "check": type(exc).__name__, "restricted_values_emitted": False}))
        raise SystemExit(1)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "FINITE_SOURCE_AUDIT_COMPLETE", "summary": result["summary"], "outcome_scoring": False}))


if __name__ == "__main__":
    main()
