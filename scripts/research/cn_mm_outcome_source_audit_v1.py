"""Read-only original outcome-owner replay for research, never feature-side input."""
from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter

from scripts.research import cn_mm_core_shadow_bridge_v1 as bridge

def verify_matured_path(replay, row, detail, horizon, frozen_baseline):
    # Reuse existing owner and admission functions. load_owner installs the
    # original scripts/research import route used by the owner modules.
    bridge.load_owner()
    import shared_row_outcome_owner as owner
    import shared_row_outcome_receipt_gate as gate
    import core_shared_row_materializer as core

    gate.verify_receipt(row, detail, horizon)
    commit = detail["outcome_source_commit"]
    replay.require_ancestor(commit)
    replay._git("merge-base", "--is-ancestor", row["source_version_commit"], commit)
    manifest = __import__("json").loads(detail["outcome_source_bindings"])
    paths = set()
    payloads = []
    for binding in manifest:
        path = binding["path"]
        if not re.fullmatch(r"03_DAILY_CAPTURE_LOGS/hourly/\d{4}/\d{2}/\d{4}-\d{2}-\d{2}\.csv", path) or path in paths:
            raise ValueError("OUTCOME_REPLAY_PATH_INVALID_OR_DUPLICATE")
        paths.add(path)
        raw = replay.read_blob(commit, path)
        if (hashlib.sha256(raw).hexdigest() != binding["sha256"] or
                len(raw) != binding["bytes"]):
            raise ValueError("OUTCOME_REPLAY_SOURCE_BYTES_MISMATCH")
        payloads.append((path, raw))
    records = owner._unique_records(core.parse_hourly_payloads(payloads))
    start = owner.parse(detail["baseline_timestamp_utc"])
    wall = owner.parse(detail["matured_at_utc"])
    target = owner.parse(detail["target_timestamp_utc"])
    end = owner.select_end(records, target, wall)
    baseline = records.get(start)
    if (baseline is None or not owner._baseline_matches(baseline, frozen_baseline) or
            end is None or owner.iso(end["ts"]) != detail["selected_end_timestamp_utc"]):
        raise ValueError("OUTCOME_REPLAY_BASELINE_OR_END_MISMATCH")
    path_rows = owner.continuous_path(records, start, end["ts"], wall)
    if (not path_rows or len(path_rows) != int(detail["sample_count"]) or
            {r["path"] for r in path_rows} != paths):
        raise ValueError("OUTCOME_REPLAY_CONTINUOUS_PATH_MISMATCH")
    for asset in ("ethbtc", "btc", "eth"):
        if any(not math.isfinite(r[asset]) or r[asset] <= 0 for r in path_rows):
            raise ValueError("OUTCOME_REPLAY_PRICE_INVALID")
        actual = owner.calc(asset, baseline, end, path_rows)
        for key, suffix in (("baseline", "baseline"), ("end", "end"),
                            ("forward", "forward_return_pct"), ("mae", "mae_pct"), ("mfe", "mfe_pct")):
            if not math.isclose(actual[key], float(detail[f"{asset}_{suffix}"]), rel_tol=1e-12, abs_tol=1e-12):
                raise ValueError("OUTCOME_REPLAY_STATISTIC_MISMATCH:" + asset + ":" + key)
    return {"event_id": row["event_id"], "horizon": horizon, "status": "SOURCE_BYTES_REPLAYED",
            "outcome_source_commit": commit, "sample_count": len(path_rows)}


def audit_outcome_cohort(replay, *, evaluate=False):
    bridge.load_owner()
    import shared_row_outcome_receipt_gate as gate
    rows = bridge.read_rows(replay.ledger_raw)
    details = bridge.read_rows(replay.read_blob(replay.checkout,
        replay.BASE + "/data/OUTCOME_DETAIL_LEDGER.csv"))
    indexed = gate.detail_index(details)
    counts = Counter()
    failures = []
    seen = set()
    used = set()
    horizon_counts = Counter()
    verified_rows = []
    verified_details = {}
    sequence_inputs = []
    source_baselines = {}
    for row in rows:
        at = bridge.clock(row["observation_timestamp_utc"])
        if at < replay.floor:
            continue
        event = row["event_id"]
        if event in seen:
            raise ValueError("OUTCOME_AUDIT_DUPLICATE_PARENT")
        seen.add(event)
        # Full original decision-source replay precedes, but never receives outcome fields.
        projection = {k: v for k, v in row.items() if k not in
                      bridge.load_owner().PROVENANCE_MUTABLE_FIELDS}
        persistence = replay.verify(projection, at, json.loads(projection["candidate_decisions"]))
        frozen_baseline = json.loads(projection["source_binding_manifest"])["families"]["ETHBTC_PERSISTENCE"]["baseline"]
        if evaluate:
            sequence_inputs.append(bridge.load_owner().sequence_observation(projection, at, persistence))
            source_baselines[event] = frozen_baseline
            verified_rows.append(dict(row))
        for horizon in gate.HORIZONS:
            key = (event, horizon)
            receipts = indexed.get(key, [])
            used.add(key)
            if not any(str(row.get(f"{prefix}_{horizon}", "")).strip()
                       for prefix in ("outcome", "mae", "mfe")) and not receipts:
                counts["unmatured_or_unavailable"] += 1
                continue
            try:
                if len(receipts) != 1:
                    raise ValueError("OUTCOME_REPLAY_UNIQUE_RECEIPT_REQUIRED")
                verify_matured_path(replay, row, receipts[0], horizon, frozen_baseline)
                counts["verified"] += 1
                horizon_counts[horizon] += 1
                if evaluate:
                    verified_details[key] = receipts[0]
            except (ValueError, RuntimeError, TypeError, KeyError, AttributeError, OSError, OverflowError,
                    __import__("subprocess").SubprocessError) as exc:
                counts["rejected"] += 1
                failures.append({"event_id": event, "horizon": horizon, "reason": str(exc)[:200]})
    orphans = sum(len(v) for k,v in indexed.items() if k not in used)
    result = {"contract": "PINNED_MATURED_OUTCOME_SOURCE_AUDIT_v1",
            "checkout_sha": replay.checkout, "parent_n": len(seen),
            "verified_n": counts["verified"], "unmatured_or_unavailable_n": counts["unmatured_or_unavailable"],
            "rejected_n": counts["rejected"], "orphan_or_excluded_detail_n": orphans,
            "verified_horizon_counts": dict(horizon_counts), "failures": failures,
            "scientific_pit_eligible": False, "forecast_authority": False,
            "edge_established": False, "outcomes_used_as_features": False,
            "status": "REPLAY_COMPLETE" if counts["verified"] and not counts["rejected"] and not orphans else "REPLAY_BLOCKED"}
    if evaluate:
        result["matched_research"] = evaluate_verified_cohort(replay, result, verified_rows, verified_details, sequence_inputs, source_baselines)
    return result


def episode_opportunity(episodes, rows, details, baselines):
    """Compare on a common ORIGINAL endpoint, not moving 24h/72h/7d targets.

    This is descriptive research on observed crossing episodes. Never call
    an observation-proxy a confirmed original signal or a realized trade.
    A closed episode without observed completion is a separate wait case.
    An open/censored episode or unavailable outcome cannot be scored.
    """
    from datetime import timedelta
    by_clock = {r["observation_timestamp_utc"]: r for r in rows}
    if len(by_clock) != len(rows):
        raise ValueError("EPISODE_DUPLICATE_OBSERVATION")
    results = []
    for ep in episodes:
        first = ep["first_observation_utc"]
        early = by_clock[first]
        completion = ep["first_ordered_proxy_observation_utc"]
        end_clock = ep["end_observation_utc"]
        entry = {"episode": ep["observed_crossing_bar_utc"], "first_observation_utc": first,
                 "first_ordered_proxy_observation_utc": completion, "end_observation_utc": end_clock,
                 "horizons": {}}
        for h in ("24h","72h","7d"):
            detail = details.get((early["event_id"], h))
            item = {"status": "OUTCOME_UNAVAILABLE", "early_relative_return_pct": None,
                    "wait_relative_return_pct": None, "early_minus_wait_pp": None,
                    "observation_delay_hours": None, "trade_pnl": None}
            entry["horizons"][h] = item
            if detail is None:
                continue
            target = bridge.clock(detail["target_timestamp_utc"])
            endpoint = bridge.clock(detail["selected_end_timestamp_utc"])
            early_return = float(detail["ethbtc_forward_return_pct"])
            item["early_relative_return_pct"] = early_return
            if completion is None or bridge.clock(completion) >= target:
                # No observed complete sequence before target. Do not pretend
                # an unobserved/censored episode proves a wait outcome.
                if end_clock is None or bridge.clock(end_clock) > target:
                    item["status"] = "WAIT_CENSORED_AT_TARGET"
                    continue
                item.update(status="EPISODE_CLOSED_WITHOUT_OBSERVED_COMPLETION_BEFORE_TARGET",
                            wait_relative_return_pct=0.0, early_minus_wait_pp=early_return)
                continue
            late = by_clock[completion]
            late_base = baselines[late["event_id"]]
            early_base = baselines[early["event_id"]]
            # Require an actual later frozen observation baseline. The common
            # endpoint is the source-replayed early outcome, not the late
            # observation's different horizon. No market-fill simulation.
            if not (bridge.clock(early_base["timestamp_utc"]) < bridge.clock(late_base["timestamp_utc"]) <=
                    bridge.clock(completion) < target <= endpoint):
                item["status"] = "LATER_BASELINE_NOT_COMPARABLE"
                continue
            later_price = float(late_base["ethbtc_close"])
            if not math.isfinite(later_price) or later_price <= 0:
                raise ValueError("EPISODE_BASELINE_INVALID")
            wait_return = (float(detail["ethbtc_end"]) / later_price - 1) * 100
            item.update(status="COMMON_ENDPOINT_OBSERVATION_BASELINE_PROXY",
                        wait_relative_return_pct=wait_return, early_minus_wait_pp=early_return-wait_return,
                        observation_delay_hours=(bridge.clock(completion)-bridge.clock(first)).total_seconds()/3600)
        results.append(entry)
    return {"contract": "OBSERVED_EPISODE_COMMON_ENDPOINT_DIAGNOSTIC_v1",
            "episode_n": len(results), "episodes": results,
            "independent_episode_n": None, "causal_delay_cost_established": False,
            "economic_opportunity_cost_established": False, "original_sequence_equivalence": False,
            "scientific_pit_eligible": False, "forecast_authority": False}


def evaluate_verified_cohort(replay, audit, rows, details, sequence_inputs, baselines):
    """Only all-admitted original-byte-replayed cohort, no outcome selection."""
    if audit["status"] != "REPLAY_COMPLETE":
        return {"status": "BLOCKED_OUTCOME_SOURCE_REPLAY", "forecast_authority": False}
    import shared_row_tournament_weekly as weekly
    runtime = json.loads(replay.read_blob(replay.checkout, replay.BASE + "/RUNTIME_STATUS.json"))
    if bridge.clock(runtime["core_prospective_eligibility_start"]) != replay.floor:
        raise ValueError("MATCHED_RESEARCH_FLOOR_MISMATCH")
    # Reuse original ablation, meta-learning and dependence definitions.
    ablation = weekly.core_ablation_diagnostic(rows, runtime)
    for h, panel in ablation["horizons"].items():
        if panel["matched_matured_n"] != audit["verified_horizon_counts"].get(h,0):
            raise ValueError("MATCHED_RESEARCH_DENOMINATOR_MISMATCH")
    census = bridge.load_owner().sequence_census(sequence_inputs)
    opportunity = episode_opportunity(census["episodes"], rows, details, baselines)
    return {"contract": "PINNED_MATCHED_CORE_AND_EPISODE_RESEARCH_v1",
            "status": "DESCRIPTIVE_ONLY_NOT_INDEPENDENT_EDGE",
            "authority": "RESEARCH_ONLY_NON_CANONICAL",
            "source_owner": "ORIGINAL_FEATURE_AND_OUTCOME_SOURCE_BYTES_REPLAYED",
            "core_ablation": ablation, "episode_opportunity": opportunity,
            "dependence": weekly.dependence_census(rows,runtime),
            "scientific_pit_eligible": False, "forecast_authority": False,
            "automatic_weight_updates": False, "edge_established": False}
