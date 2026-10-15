"""Rebuild the bounded native Compass R1 admission ledger from original Git objects.

Research metadata only. No market values, outcome scoring or backtest is emitted.
"""

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESEARCH = "04_MARKET_LEARNING/handlekompas/research/"
CENSUS = RESEARCH + "2026-10-14__TASK2_R1_NATIVE_V3_11_SOURCE_CLOCK_CASES_v1.json"
FORECAST_CENSUS = RESEARCH + "2026-10-14__TASK2_R1_NATIVE_V3_12H_CENSUS_v1.json"


def git(*args, input_bytes=None):
    return subprocess.run(
        ["git", "--no-replace-objects", *args], cwd=ROOT, input=input_bytes, capture_output=True, check=True
    ).stdout


def original(ref, path, expected_blob=None):
    raw = git("show", f"{ref}:{path}")
    blob = git("hash-object", "--stdin", input_bytes=raw).decode().strip()
    if expected_blob is not None and blob != expected_blob:
        raise ValueError(f"Git blob mismatch: {path}")
    return json.loads(raw), blob


def optional_original(ref, path):
    """Certify an absent Git path by successful traversal of the exact tree.

    A failed git command, missing nested tree or unreadable blob is an
    operational integrity blocker, never evidence that a forecast outcome
    was absent. Git's pathspec can overmatch, so use exact NUL-delimited paths.
    """
    if not path or path.startswith("/") or any(part in ("", ".", "..") for part in path.split("/")):
        raise ValueError(f"Invalid original Git path: {path}")
    paths = git("ls-tree", "-r", "--full-tree", "--name-only", "-z", ref, "--", path)
    found = [entry.decode("utf-8") for entry in paths.split(b"\x00") if entry]
    if path not in found:
        if found:
            raise ValueError(f"Original Git lookup returned only nonexact matches: {path}")
        return None, None
    return original(ref, path)


def earlier(clock, issue):
    if clock is None:
        return None
    return dt.datetime.fromisoformat(clock.replace("Z", "+00:00")) <= dt.datetime.fromisoformat(issue.replace("Z", "+00:00"))


def clock_status(observed, retrieved, issue, funding=False):
    if funding:
        return "SETTLEMENT_IS_NOT_QUOTE_OBSERVATION"
    if retrieved and not earlier(retrieved, issue):
        return "NOT_ADMITTED_RETRIEVED_AFTER_ISSUE"
    if observed and isinstance(observed, str) and ("T" in observed):
        if not earlier(observed, issue):
            return "NOT_ADMITTED_OBSERVATION_AFTER_ISSUE"
    return "ARCHIVE_CLOCK_PREISSUE_PROVIDER_FIRST_KNOWN_UNKNOWN" if retrieved else "RETRIEVAL_CLOCK_UNKNOWN"


def build():
    census = json.loads((ROOT / CENSUS).read_text())
    ref = census["pinned_original_main_ref"]
    # An independent, earlier 17-attempt census provides the expected frozen
    # forecast Git blobs and outcome presence. Never silently reconstruct a
    # convenient subset from current HEAD or 11-row source metadata alone.
    forecast_census = json.loads((ROOT / FORECAST_CENSUS).read_text())
    if forecast_census["pinned_public_main_commit"] != ref:
        raise ValueError("Original forecast census uses a different pinned Git revision")
    original_v3 = {f["id"]: f for f in forecast_census["forecast_rows"]
                   if f["original_scoring_contract"] == "OFFICIAL_DAILY_COMPASS_SCORING_v3"}
    if (len(original_v3) != 11 or len(census["rows"]) != 11
            or {f["compass_id"] for f in census["rows"]} != set(original_v3)):
        raise ValueError("Original forecast census or attempt roster mismatch")
    rows = []
    for item in census["rows"]:
        fid, issue = item["compass_id"], item["issued_at_utc"]
        day = fid.split("-")[1]
        forecast_path = f"04_MARKET_LEARNING/handlekompas/official/daily/2026/{day[4:6]}/{day[6:8]}/{fid}.json"
        frozen = original_v3[fid]
        if frozen["forecast_path"] != forecast_path:
            raise ValueError(f"Original forecast path differs from frozen census: {fid}")
        forecast, forecast_blob = original(ref, forecast_path, frozen["forecast_git_blob_sha"])
        if forecast.get("scoring_contract") != frozen["original_scoring_contract"]:
            raise ValueError(f"Original forecast scoring contract differs: {fid}")
        packet, packet_blob = original(item["source_first_visible_path_commit_sha"], item["source_path"], item["source_git_blob_sha"])
        target = packet["source_health"]["live_anchor"]["provenance"]["target"]
        capture, capture_blob = original(target["exact_commit_sha"], target["exact_path"], target["git_blob_sha"])
        commit_clock = git("show", "-s", "--format=%cI", target["exact_commit_sha"]).decode().strip()
        if not (earlier(capture["captured_at_utc"], issue) and earlier(commit_clock, issue)):
            raise ValueError(f"Capture unavailable before issue: {fid}")
        if not earlier(packet["packet_generated_at_utc"], issue):
            raise ValueError(f"Packet generated after issue: {fid}")
        if forecast["issued_at_utc"] != issue or forecast["compass_id"] != fid:
            raise ValueError(f"Forecast identity differs: {fid}")
        engine_path = "scripts/data_ping/native_handlekompas.py"
        engine_blob = git("rev-parse", f"{forecast['bound_main_sha']}:{engine_path}").decode().strip()
        owners = {o["owner_id"]: o for o in capture["owners"]}
        cfgi = next(f["summary"] for f in owners["cfgi_sentiment"]["files"] if f["path"].endswith("owner_snapshot.json"))
        okx = next(f["summary"] for f in owners["okx_swap"]["files"] if f["path"].endswith("owner_snapshot.json"))
        selected = {f["feature_id"]: f for f in forecast["evidence_snapshot"]["selected_features"]}
        cfgi_rows = {r["symbol"]: r for r in cfgi["rows"]}
        okx_rows = {(r["instrument"], r["metric"]): r for r in okx["rows"]}
        cfgi_matches = all(selected[f"sentiment_{key}_score"]["value"] == cfgi_rows[symbol]["score"] for key, symbol in (("market", "MARKET"), ("btc", "BTC"), ("eth", "ETH")))
        funding_matches = all(selected[f"{key}_funding"]["value"] == okx_rows[(symbol, "funding")]["funding_rate"] for key, symbol in (("btc", "BTC-USDT-SWAP"), ("eth", "ETH-USDT-SWAP")))
        if not (cfgi_matches and funding_matches):
            raise ValueError(f"Original selected feature differs from capture: {fid}")
        if any(not earlier(t, issue) for t in (cfgi["retrieved_at_utc"], okx["retrieval_timestamp"])):
            raise ValueError(f"Collector retrieval after issue: {fid}")
        features = []
        for f in forecast["evidence_snapshot"]["selected_features"]:
            funding = f["feature_id"] in ("btc_funding", "eth_funding")
            features.append({
                "feature_id": f["feature_id"], "source_owner": f["source_owner"],
                "declared_observed_at": f.get("observed_at"), "declared_retrieved_at": f.get("retrieved_at"),
                "observation_clock_status": clock_status(f.get("observed_at"), f.get("retrieved_at"), issue, funding),
                "vendor_first_publication_at": None,
            })
        outcome_path = f"04_MARKET_LEARNING/handlekompas/official/outcomes/2026/{day[4:6]}/{day[6:8]}/{fid}_12h.json"
        outcome, outcome_blob = optional_original(ref, outcome_path)
        original_status = "PRESENT" if outcome is not None else "ABSENT_AT_ORIGINAL_SNAPSHOT"
        expected_outcome_status = ("PRESENT" if item["outcome_12h_at_pinned_ref"] == "PRESENT"
                                   else "ABSENT_AT_ORIGINAL_SNAPSHOT")
        frozen_outcome_status = ("PRESENT" if frozen["outcome_12h_presence_at_pinned_commit"] == "PRESENT"
                                 else "ABSENT_AT_ORIGINAL_SNAPSHOT")
        if original_status != expected_outcome_status or original_status != frozen_outcome_status:
            raise ValueError(f"Original outcome snapshot census mismatch: {fid}")
        if original_status == "PRESENT" and outcome_blob != frozen["outcome_git_blob_sha"]:
            raise ValueError(f"Original outcome Git blob mismatch: {fid}")
        # HEAD in GitHub PR CI may be a synthetic test-merge commit,
        # not refs/heads/main. This is checkout context only, never "main".
        checkout_outcome, checkout_blob = optional_original("HEAD", outcome_path)
        checkout_status = "PRESENT_ON_CHECKOUT_HEAD" if checkout_outcome is not None else "ABSENT_ON_CHECKOUT_HEAD"
        if outcome is None:
            outcome = checkout_outcome
        target_at = outcome.get("target_at_utc") if outcome else None
        offset = int((dt.datetime.fromisoformat(target_at.replace("Z", "+00:00")) - dt.datetime.fromisoformat(issue.replace("Z", "+00:00"))).total_seconds()) if target_at else None
        time_basis = outcome.get("time_basis", {}) if outcome else {}
        reference = time_basis.get("start_reference_at_utc")
        reference_horizon = int((dt.datetime.fromisoformat(target_at.replace("Z", "+00:00")) - dt.datetime.fromisoformat(reference.replace("Z", "+00:00"))).total_seconds()) if target_at and reference else None
        if reference_horizon is not None and reference_horizon != 12 * 3600:
            raise ValueError(f"Nominal target differs from source-reference-plus-12h: {fid}")
        rows.append({
            "forecast_id": fid, "original_forecast_path": forecast_path,
            "original_forecast_git_blob_sha": forecast_blob,
            "original_forecast_declared_sha256": forecast.get("compass_sha256"),
            "issued_at_utc": issue, "first_user_delivery_at_utc": None, "first_actionable_at_utc": None,
            "original_bound_main_sha": forecast.get("bound_main_sha"),
            "model_version": {"schema": forecast.get("schema_version"), "policy": forecast.get("decision_policy_version"), "scoring": forecast.get("scoring_contract"), "engine_path": engine_path, "engine_git_blob_sha_at_bound_main": engine_blob},
            "source_packet": {"path": item["source_path"], "git_blob_sha": packet_blob, "first_git_commit_sha": item["source_first_visible_path_commit_sha"], "first_git_commit_at_utc": item["source_first_visible_path_commit_at_utc"], "generated_at_utc": packet["packet_generated_at_utc"]},
            "raw_capture": {"path": target["exact_path"], "commit_sha": target["exact_commit_sha"], "git_blob_sha": capture_blob, "captured_at_utc": capture["captured_at_utc"], "git_commit_at_utc": commit_clock, "raw_provider_response_sha256_independently_rehashed": False},
            "collector_clocks": {"CFGI_v3_4h_retrieved_at_utc": cfgi["retrieved_at_utc"], "CFGI_observation_at_utc": {r["symbol"]: r["timestamp"] for r in cfgi["rows"]}, "OKX_swap_retrieved_at_utc": okx["retrieval_timestamp"], "OKX_funding_settlement_at_utc": {symbol: dt.datetime.fromtimestamp(okx_rows[(symbol, "funding")]["funding_time"] / 1000, dt.timezone.utc).isoformat().replace("+00:00", "Z") for symbol in ("BTC-USDT-SWAP", "ETH-USDT-SWAP")}, "selected_CFGI_scores_match_capture": cfgi_matches, "selected_OKX_funding_quotes_match_capture": funding_matches},
            "selected_feature_clocks": features,
            "data_quality": {"internal_packet_and_capture_blobs_verified": True, "collector_to_selected_CFGI_and_OKX_value_equality_verified_without_export": True, "selected_feature_count": len(features), "feature_retrieval_clock_explicit_count": sum(f.get("retrieved_at") is not None for f in forecast["evidence_snapshot"]["selected_features"]), "provider_publication_or_revision_verified": False},
            "provisional_dependency_id": f"raw_capture_blob:{capture_blob}", "independent_market_event_family": None,
            "original_target_at_utc": target_at if original_status == "PRESENT" else None,
            "later_target_at_utc_unadmitted": target_at if original_status != "PRESENT" else None,
            "original_target_reference_at_utc": reference if original_status == "PRESENT" else None,
            "nominal_reference_to_target_seconds": reference_horizon if original_status == "PRESENT" else None,
            "issue_to_original_target_seconds": offset if original_status == "PRESENT" else None,
            "original_outcome_status": original_status, "original_outcome_git_blob_sha": outcome_blob,
            "original_direction_result_only_not_admitted": {asset: outcome["direction_accuracy"][asset]["result"] for asset in ("btc", "eth")} if original_status == "PRESENT" else None,
            "checkout_outcome_status": checkout_status, "checkout_outcome_git_blob_sha": checkout_blob,
            "admissibility": "NOT_ADMITTED", "reason": ["PROVIDER_FIRST_PUBLICATION_UNVERIFIED", "FIRST_USER_DELIVERY_UNVERIFIED", "INDEPENDENT_EVENT_FAMILY_UNVERIFIED", "HORIZON_BAR_ANCHOR_NEEDS_SAME_CLOCK_RECONCILIATION"] + (["ORIGINAL_OUTCOME_ABSENT_AT_FROZEN_SNAPSHOT"] if original_status != "PRESENT" else []),
            # Two non-promoting research gates: an internally issued information
            # comparison need not require user delivery, whereas any investor
            # action/PnL claim must establish delivery, actionability and fills.
            "information_edge_gate": {
                "status": "NOT_ADMITTED",
                "missing": ["PROVIDER_FIRST_PUBLICATION_UNVERIFIED", "INDEPENDENT_EVENT_FAMILY_UNVERIFIED", "SAME_CLOCK_BASELINE_UNVERIFIED"] + (["ORIGINAL_OUTCOME_ABSENT_AT_FROZEN_SNAPSHOT"] if original_status != "PRESENT" else []),
                "original_issue_clock_bound": True,
                "user_delivery_required": False,
            },
            "investor_action_edge_gate": {
                "status": "NOT_ADMITTED",
                "missing": ["PROVIDER_FIRST_PUBLICATION_UNVERIFIED", "INDEPENDENT_EVENT_FAMILY_UNVERIFIED", "FIRST_USER_DELIVERY_UNVERIFIED", "FIRST_EXECUTABLE_FILL_AND_AFTER_COST_HOLD_CONTROL_UNVERIFIED"] + (["ORIGINAL_OUTCOME_ABSENT_AT_FROZEN_SNAPSHOT"] if original_status != "PRESENT" else []),
                "user_delivery_required": True,
                "portfolio_execution_authorized": False,
            },
            "next_required_evidence": ["per-field vendor revision and first-publication or independent immutable original response binding", "original investor visibility/action clock", "target bar origin and same-clock control", "independent event and negative/no-warning universe"],
        })
    if len(rows) != 11 or len({r["source_packet"]["git_blob_sha"] for r in rows}) != 10 or len({r["raw_capture"]["git_blob_sha"] for r in rows}) != 7:
        raise ValueError("Cohort/dependency census changed")
    return {
        "contract": "TASK2_R1_NATIVE_V3_ORIGINAL_ADMISSION_v1", "status": "RESEARCH_ONLY_NOT_ADMITTED",
        "generated_from_checkout_head_sha": git("rev-parse", "HEAD").decode().strip(), "checkout_ref_semantics": "MAY_BE_PR_TEST_MERGE_NOT_VERIFIED_CURRENT_MAIN", "original_snapshot_sha": ref,
        "source_census_path": CENSUS, "owner_issue": 1596,
        "cohort": {"original_attempts": 11, "original_outcomes_present": sum(r["original_outcome_status"] == "PRESENT" for r in rows), "original_outcomes_absent": sum(r["original_outcome_status"] != "PRESENT" for r in rows), "unique_source_blobs": 10, "unique_raw_capture_blobs": 7, "admitted": 0, "independent_market_event_families_certified": 0},
        "clock_interpretation": "Internal Git and collector retrieval precede issue, but this does not independently certify vendor publication/revision or user delivery. OKX funding_time is future settlement, not the quote observation clock. CFGI is v3 4h lookback refreshed about every 15 minutes; October 2026 is post July 8 scoring era. No retrospective static=true or 2025 backfill is joined.",
        "absence_universe": {"registered_original_forecasts": 11, "abstentions": "RETAIN_IN_ORIGINAL_OUTCOME_NO_RESCORE", "no_forecast_hours": "UNKNOWN_NOT_ENUMERATED", "no_warning_opportunities": "UNKNOWN_NOT_ENUMERATED", "negative_event_families": "UNKNOWN_NOT_CERTIFIED"},
        "historical_backtest_release": "BLOCKED_NOT_IDENTIFIABLE_YET", "after_cost_action_simulation": "NOT_EXECUTED",
        "rows": rows,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    Path(args.output).write_text(json.dumps(build(), indent=2, ensure_ascii=False) + "\n")
