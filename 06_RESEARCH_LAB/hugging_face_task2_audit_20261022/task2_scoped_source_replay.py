#!/usr/bin/env python3
"""Value-free audit of one original Task2 12h directional source chain.

Reads historical local evidence and exact original public Git code only. No
outcomes, scoring, provider requests, original rewrites or admission automation.
Server timing bindings below were separately read from original GitHub job logs
by the coordinator; this offline script checks their identity/order, not the API.
"""
from __future__ import annotations
import argparse
import ast
import copy
import csv
import hashlib
import io
import json
import math
import subprocess
import typing
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

FORECAST_ID = "CMP-20261012-468da783e9d8"
ENGINE_COMMIT = "b7b677f4565bf13a775af3189d1b53de75c249e7"
SNAPSHOT = "1ca03efa99b7a48f69b015e42c23c099384d693b"
ARTIFACT = {
    "run_id": 38321418868, "artifact_id": 11779038695,
    "bytes": 10728,
    "sha256": "0d83427d97e0793e4f3b894cf2c96c0e9c3a1dc7dc82035e18c36762c0a5f5d8",
    "upload_completed_at_utc": "2026-10-12T23:18:46Z",
    "source_job_completed_at_utc": "2026-10-12T23:18:56Z",
}
PACKET_PUBLICATION = {
    "run_id": 38321473523, "job_id": 115051297353,
    "commit_sha": "7ed9e997573fc23b2b89fd4998b69391e4063306",
    "remote_push_reported_at_utc": "2026-10-12T23:22:47Z",
    "source_job_completed_at_utc": "2026-10-12T23:22:54Z",
}
INPUTS = {
    "forecast": (FORECAST_ID + ".json", "5239ba0450c97e425e5d5791e9c6c6cfa07e1613"),
    "packet": ("packet-48a061318da52279c761cff46456a17f0822954f.json", "48a061318da52279c761cff46456a17f0822954f"),
    "predecessor": ("predecessor-original-packet.json", "036325b0607e0ebd50d01a0b72783d7d524faf9d"),
    "hourly_target": ("hourly-original-target.json", "9873b58e231891e4685c475c76c497609d1a10d4"),
    "hourly_csv": ("hourly-original-2026-10-12.csv", "dbdace82840e7c38c7fb40f26a85268d48e4ae88"),
    "producer": ("auto_market_state_original.py", "6196286539bd3e3688dc3bbcf322b15112b9ef5c"),
    "okx_collector": ("collector_okx.py", "db67b1a429794c0b022f2f06db1e36d58b8e2b50"),
}


class AuditError(Exception):
    pass


def require(condition, label):
    if not condition:
        raise AuditError(label)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def canonical(doc, field):
    return (json.dumps({k: v for k, v in doc.items() if k != field}, sort_keys=True,
                       separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode()


def stamp(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def availability(complete, issued):
    require(stamp(complete) < stamp(issued), "AVAILABILITY_NOT_BEFORE_ISSUE")


def reference(actual, expected):
    require(actual == expected, "ORIGINAL_PACKET_REFERENCE_MISMATCH")


def rejected(operation):
    try:
        operation()
    except AuditError:
        return True
    return False


def git_file(repo, commit, path, expected_blob):
    raw = subprocess.check_output(["git", "--no-replace-objects", "-C", str(repo),
                                   "show", f"{commit}:{path}"], stderr=subprocess.DEVNULL)
    require(blob(raw) == expected_blob, "ORIGINAL_GIT_CODE_BLOB_MISMATCH")
    return raw


def functions(raw, names, namespace):
    tree = ast.parse(raw)
    body = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    require({n.name for n in body} == set(names), "ORIGINAL_FUNCTION_SET_MISSING")
    exec(compile(ast.Module(body=body, type_ignores=[]), "<hash-bound-original-functions>", "exec"), namespace)
    return tree


def context_snapshot_replay(root, members, collector):
    """Original byte/transform equality only, no provider-first-publication claim."""
    timing = json.loads((root / "source_timing.json").read_text())
    rows = timing["rows"]
    require(len(rows) == 11 and len({x["source_run_id"] for x in rows}) == 7, "ORIGINAL_CONTEXT_COHORT_MISMATCH")
    parser = {"json": json, "E": RuntimeError}
    functions(collector, {"parse"}, parser)
    snapshots, raw_replays, member_checks = {}, 0, 0
    for item in rows:
        run = item["source_run_id"]
        if run in snapshots:
            continue
        filename = f"anchor-{run}.zip"
        archive = (root / filename).read_bytes()
        original = members[filename]
        require(len(archive) == original["bytes"] == item["artifact_size_in_bytes"]
                and sha(archive) == original["sha256"] == item["artifact_sha256"], "ORIGINAL_CONTEXT_ARCHIVE_HASH_MISMATCH")
        with zipfile.ZipFile(io.BytesIO(archive)) as z:
            require(len(z.namelist()) == len(set(z.namelist())), "DUPLICATE_CONTEXT_ARCHIVE_MEMBER")
            prefix = "okx-swap-owner-output/"
            manifest = json.loads(z.read(prefix + "artifact_manifest.json"))
            for member in manifest["members"]:
                require(not member["path"].startswith("/") and ".." not in Path(member["path"]).parts,
                        "UNSAFE_CONTEXT_MEMBER_PATH")
                payload = z.read(prefix + member["path"])
                require(len(payload) == member["bytes"] and sha(payload) == member["sha256"], "ORIGINAL_OKX_MEMBER_HASH_MISMATCH")
                member_checks += 1
            owner = json.loads(z.read(prefix + "owner_snapshot.json"))
            indexed = {(x["instrument"], x["metric"]): x for x in owner["rows"]}
            for instrument in ("BTC-USDT-SWAP", "ETH-USDT-SWAP"):
                for metric in ("funding", "open_interest", "mark_price"):
                    payload = z.read(prefix + f"raw/{instrument}_{metric}.json")
                    require(parser["parse"](payload, metric, instrument) == indexed[(instrument, metric)],
                            "ORIGINAL_OKX_RAW_TO_SNAPSHOT_MISMATCH")
                    raw_replays += 1
            cfgi = json.loads(z.read("cfgi-owner-output/owner_snapshot.json"))
            snapshots[run] = (indexed, {x["symbol"]: x for x in cfgi["rows"]})
    selected_equalities = 0
    for item in rows:
        filename = item["forecast_id"] + ".json"
        raw = (root / filename).read_bytes()
        require(len(raw) == members[filename]["bytes"] and sha(raw) == members[filename]["sha256"],
                "ORIGINAL_CONTEXT_FORECAST_HASH_MISMATCH")
        original = json.loads(raw)
        require(original["compass_id"] == item["forecast_id"], "ORIGINAL_CONTEXT_FORECAST_ID_MISMATCH")
        availability(item["source_job_completed_at_utc"], original["issued_at_utc"])
        require(item["source_job_conclusion"] == item["upload_step_conclusion"] == "success",
                "ORIGINAL_CONTEXT_SERVER_JOB_NOT_SUCCESS")
        features = {x["feature_id"]: x for x in original["evidence_snapshot"]["selected_features"]}
        okx, cfgi = snapshots[item["source_run_id"]]
        for asset in ("BTC", "ETH"):
            require(features[asset.lower() + "_funding"]["value"] == okx[(asset + "-USDT-SWAP", "funding")]["funding_rate"],
                    "ORIGINAL_SELECTED_FUNDING_EQUALITY_MISMATCH")
            selected_equalities += 1
        for symbol in ("MARKET", "BTC", "ETH"):
            require(features["sentiment_" + symbol.lower() + "_score"]["value"] == cfgi[symbol]["score"],
                    "ORIGINAL_SELECTED_CFGI_EQUALITY_MISMATCH")
            selected_equalities += 1
    return {"original_artifact_archives_matched": len(snapshots), "okx_member_hash_checks": member_checks,
            "original_okx_raw_response_replays_equal": raw_replays, "original_selected_funding_cfgi_equalities": selected_equalities,
            "cfgi_raw_http_response_replay_available": False, "context_equalities_are_not_blanket_feature_admission": True}


def run(root, repo):
    manifest_raw = (root / "custody_manifest.json").read_bytes()
    require(blob(manifest_raw) == "f708e6ee97b40dfc56c06b896e6347a60911b5d8", "CUSTODY_MANIFEST_BLOB_MISMATCH")
    members = {x["path"]: x for x in json.loads(manifest_raw)["members"]}
    raws = {}
    for label, (filename, expected) in INPUTS.items():
        raw = (root / filename).read_bytes()
        require(blob(raw) == expected, "ORIGINAL_LOCAL_BLOB_MISMATCH_" + label)
        if filename in members:
            require(len(raw) == members[filename]["bytes"] and sha(raw) == members[filename]["sha256"],
                    "CUSTODY_MEMBER_MISMATCH_" + label)
        raws[label] = raw
    f, p, prior, target = (json.loads(raws[x]) for x in ("forecast", "packet", "predecessor", "hourly_target"))
    require(f["compass_id"] == FORECAST_ID and f["bound_main_sha"] == ENGINE_COMMIT, "FORECAST_ID_OR_ENGINE_MISMATCH")
    for doc, field in ((f, "compass_sha256"), (p, "packet_sha256"), (prior, "packet_sha256")):
        require(sha(canonical(doc, field)) == doc[field], "ORIGINAL_CANONICAL_SELF_HASH_MISMATCH")
    reference(f["source_bindings"]["auto_market_state"]["packet_sha256"], p["packet_sha256"])
    reference(p["predecessor"]["packet_sha256"], prior["packet_sha256"])
    require(p["source_snapshot"]["exact_commit_sha"] == SNAPSHOT, "ORIGINAL_SOURCE_SNAPSHOT_MISMATCH")
    issued = f["issued_at_utc"]
    for timing in (ARTIFACT["upload_completed_at_utc"], ARTIFACT["source_job_completed_at_utc"],
                   PACKET_PUBLICATION["remote_push_reported_at_utc"], PACKET_PUBLICATION["source_job_completed_at_utc"]):
        availability(timing, issued)
    archive = (root / "hourly-source-38321418868.zip").read_bytes()
    require(len(archive) == ARTIFACT["bytes"] and sha(archive) == ARTIFACT["sha256"], "ORIGINAL_HOURLY_ARCHIVE_MISMATCH")
    receipts = {x["name"]: x for x in target["source_records"]}
    features = {x["feature_id"]: x for x in f["evidence_snapshot"]["selected_features"]}
    ns = {"Any": typing.Any, "Mapping": typing.Mapping, "math": math,
          "datetime": datetime, "timedelta": timedelta, "timezone": timezone}
    producer_tree = functions(raws["producer"], {"num", "delta", "decision_lanes"}, ns)
    for node in producer_tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "LANES" for t in node.targets):
            ns["LANES"] = ast.literal_eval(node.value)
    registry = json.loads(git_file(repo, SNAPSHOT, "02_DATA_PING/source_integrations/2026-09-02__auto-market-state-source-admission-v1_1.json",
                                  "322325f23fb6f1bdb7ef1d34dd0d438ef5deea67"))
    required = ns["decision_lanes"](registry)
    engine = git_file(repo, ENGINE_COMMIT, "scripts/data_ping/native_handlekompas.py", "d00d38bed517861fa2487dce42d330bf05812f6d")
    names = {"nested", "finite", "_delta_pct", "_parse_utc", "owner_freshness", "_health_ok", "action_context", "derive_market_now",
             "_cn_decision_projection", "_cn_direction", "_cn_projection_summary", "_unavailable_horizon", "_altcoin_cycle_lane", "horizon_map"}
    functions(engine, names, ns)
    ns["HORIZON_ORDER"] = ("NEXT_12H", "NEXT_1_3D", "NEXT_5_7D", "NEXT_2_3W", "CYCLE_ALTCOINS_3_8W")

    def health_gate(doc):
        expected = [x for x in required if doc["source_health"].get(x, {}).get("status") != "PASS"]
        require(doc["blockers"] == expected, "ORIGINAL_REQUIRED_HEALTH_PREDICATE_MISMATCH")
        require(doc["decision_context_status"] == ("PASS" if not expected else "DEGRADED"), "ORIGINAL_DECISION_HEALTH_MISMATCH")
        require(ns["_health_ok"](doc, stamp(issued)), "ORIGINAL_ISSUANCE_HEALTH_GATE_FAILED")

    health_gate(p)
    csv_rows = list(csv.DictReader(io.StringIO(raws["hourly_csv"].decode("utf-8-sig"))))
    comparisons = []
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        require(len(z.namelist()) == len(set(z.namelist())), "DUPLICATE_ARCHIVE_MEMBER")
        for symbol, key, feature in (("BTCUSDT", "btc_usdt", "btc_delta_since_prior_packet_pct"),
                                     ("ETHUSDT", "eth_usdt", "eth_delta_since_prior_packet_pct"),
                                     ("ETHBTC", "ethbtc", "ethbtc_delta_since_prior_packet_pct")):
            raw = z.read(symbol + "_spot.json")
            require(sha(raw) == receipts[symbol + "_spot"]["sha256"], "ORIGINAL_SPOT_MEMBER_HASH_MISMATCH")
            klines = json.loads(raw)
            def row_at(ts):
                ms = int(stamp(ts).timestamp() * 1000)
                rows = [x for x in klines if int(x[0]) == ms]
                require(len(rows) == 1, "ORIGINAL_SPOT_EXACT_ROW_MISSING_OR_DUPLICATE")
                require(int(rows[0][6]) < stamp(ARTIFACT["source_job_completed_at_utc"]).timestamp() * 1000,
                        "ORIGINAL_SPOT_ROW_NOT_CLOSED_BEFORE_AVAILABILITY_BOUND")
                return rows[0]
            current = row_at(p["normalized_state"]["live_market"]["observation_open_utc"])
            previous = row_at(prior["normalized_state"]["live_market"]["observation_open_utc"])
            cv, pv = p["normalized_state"]["live_market"][key], prior["normalized_state"]["scalar_values"][key]
            require(float(current[4]) == cv and float(previous[4]) == pv, "RAW_TO_ORIGINAL_PRICE_INPUT_MISMATCH")
            csv_current = [x for x in csv_rows if x["timestamp_utc"] == p["normalized_state"]["live_market"]["observation_open_utc"]]
            column = {"btc_usdt": "btc_close", "eth_usdt": "eth_close", "ethbtc": "ethbtc_close"}[key]
            require(len(csv_current) == 1 and float(csv_current[0][column]) == cv, "ORIGINAL_CSV_CURRENT_PRICE_MISMATCH")
            require(ns["delta"](cv, pv) == p["deltas_since_prior_auto_packet"][key], "ORIGINAL_DELTA_TRANSFORMATION_MISMATCH")
            require(features[key]["value"] == cv and features[feature]["value"] == p["deltas_since_prior_auto_packet"][key]["pct"],
                    "ORIGINAL_SELECTED_FEATURE_BINDING_MISMATCH")
            comparisons.append({"symbol": symbol, "raw_member_sha256": sha(raw), "raw_rows": len(klines),
                                "current_and_predecessor_exact_rows": True, "raw_to_original_prices_equal": True,
                                "original_csv_current_equal": True, "original_unrounded_delta_equal": True,
                                "selected_feature_bindings_equal": True})
    action = ns["action_context"](p, as_of=stamp(issued))
    market = ns["derive_market_now"](p, action, as_of=stamp(issued))
    horizon = ns["horizon_map"](p, action, None, as_of=stamp(issued))["NEXT_12H"]
    require(action == f["native_action_contract"] and market == f["market_now"], "ORIGINAL_ENGINE_ACTION_OR_MARKET_REPLAY_MISMATCH")
    require(horizon["expected_direction"] == f["horizons"]["NEXT_12H"]["expected_direction"], "ORIGINAL_12H_DIRECTION_REPLAY_MISMATCH")
    bad_health = copy.deepcopy(p)
    bad_health["source_health"][required[0]]["status"] = "UNAVAILABLE"
    controls = {
        "wrong_raw_member_hash_rejected": rejected(lambda: require(sha(raw) == "0" * 64, "ORIGINAL_SPOT_MEMBER_HASH_MISMATCH")),
        "future_availability_rejected": rejected(lambda: availability((stamp(issued) + timedelta(seconds=1)).isoformat(), issued)),
        "wrong_packet_binding_rejected": rejected(lambda: reference(p["predecessor"]["packet_sha256"], "0" * 64)),
        "missing_required_health_predicate_rejected": rejected(lambda: health_gate(bad_health)),
    }
    require(all(controls.values()), "NEGATIVE_CONTROL_DID_NOT_REJECT")
    context_replay = context_snapshot_replay(root, members, raws["okx_collector"])
    return {"contract": "TASK2_SCOPED_ORIGINAL_SOURCE_REPLAY_AUDIT_v1", "forecast_id": FORECAST_ID,
            "scope": "ORIGINAL_NEXT_12H_DIRECTION_DEVELOPMENT_SOURCE_CHAIN_ONLY", "source_chain_checks_passed": True,
            "input_git_blobs": {k: v[1] for k, v in INPUTS.items()}, "engine_git_blob": blob(engine),
            "hourly_original_artifact": ARTIFACT, "original_packet_publication": PACKET_PUBLICATION,
            "timing_binding_semantics": "Coordinator-verified original server logs; offline checks do not fetch/re-authenticate logs",
            "price_comparisons": comparisons, "required_health_lane_count": len(required),
            "required_health_predicates_replayed": True, "original_action_and_market_replay_equal": True,
            "original_12h_direction_replay_equal": True, "negative_controls": controls,
            "context_snapshot_replay": context_replay,
            "automatic_scientific_admission": False, "full_compass_admission": False, "provider_exact_first_publication_verified": False,
            "outcome_data_read_or_scored": False, "investor_delivery_or_economic_edge_verified": False,
            "limitations": ["One inspected development forecast, no untouched holdout", "Nine original target-bound rows share one overlap block",
                            "Context provider numeric values do not compute 12h direction; original health predicates remain gating",
                            "CN-dependent horizons, full Compass and investor economics excluded", "Original frozen R1 ledger unchanged"]}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--evidence-root", type=Path, required=True)
    ap.add_argument("--repo-root", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    try:
        result = run(args.evidence_root, args.repo_root)
    except Exception as exc:
        label = str(exc) if isinstance(exc, AuditError) else type(exc).__name__
        print(json.dumps({"status": "FAIL", "check": label, "restricted_values_emitted": False}))
        raise SystemExit(1)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS_SCOPED_SOURCE_REPLAY_ONLY", "source_symbols": len(result["price_comparisons"]),
                      "negative_controls": len(result["negative_controls"]), "outcome_scoring": False}))


if __name__ == "__main__":
    main()
