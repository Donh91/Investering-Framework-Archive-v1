"""Read-only original outcome-owner replay for research, never feature-side input."""
from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter, OrderedDict

from scripts.research import cn_mm_core_shadow_bridge_v1 as bridge

class OutcomePathReadCache:
    """Bounded per-audit memoization of immutable Git bytes and parsed paths.

    Never persists or accepts prior verification verdicts. Cache is scoped to
    one replay instance and one execution. Original receipt and per-horizon
    reconciliation still run on every result.
    """
    def __init__(self,replay,max_entries=64):
        self.replay=replay
        self.max_entries=max_entries
        self.entries=OrderedDict()
        self.hits=0
        self.misses=0

    def records(self,commit,manifest,parse,unique):
        key=(commit,tuple((x["path"],x["sha256"],x["bytes"]) for x in manifest))
        if key in self.entries:
            self.hits+=1
            self.entries.move_to_end(key)
            return self.entries[key]
        self.misses+=1
        payloads=[]
        for path,digest,size in key[1]:
            raw=self.replay.read_blob(commit,path)
            if hashlib.sha256(raw).hexdigest()!=digest or len(raw)!=size:
                raise ValueError("OUTCOME_REPLAY_SOURCE_BYTES_MISMATCH")
            payloads.append((path,raw))
        records=unique(parse(payloads))
        self.entries[key]=records
        if len(self.entries)>self.max_entries:
            self.entries.popitem(last=False)
        return records


def verify_matured_path(replay, row, detail, horizon, frozen_baseline, *, retain_path=False, cache=None):
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
    for binding in manifest:
        path = binding["path"]
        if not re.fullmatch(r"03_DAILY_CAPTURE_LOGS/hourly/\d{4}/\d{2}/\d{4}-\d{2}-\d{2}\.csv", path) or path in paths:
            raise ValueError("OUTCOME_REPLAY_PATH_INVALID_OR_DUPLICATE")
        paths.add(path)
    cache = cache if cache is not None else OutcomePathReadCache(replay)
    if cache.replay is not replay:
        raise ValueError("OUTCOME_REPLAY_CACHE_SCOPE_MISMATCH")
    records = cache.records(commit,manifest,core.parse_hourly_payloads,owner._unique_records)
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
    result = {"event_id": row["event_id"], "horizon": horizon, "status": "SOURCE_BYTES_REPLAYED",
              "outcome_source_commit": commit, "sample_count": len(path_rows)}
    if retain_path:
        # Keep the independently replayed path in memory on the evaluation side
        # only. It is not a feature, a persisted market record, or a new owner.
        result["path"] = {owner.iso(r["ts"]): {
            "source_window_end_utc": owner.iso(r["available"]),
            **{asset+"_close": r[asset] for asset in ("ethbtc","btc","eth")}}
            for r in path_rows}
    return result


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
    verified_paths = {}
    sequence_inputs = []
    source_baselines = {}
    cache = OutcomePathReadCache(replay)
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
                proof = verify_matured_path(replay, row, receipts[0], horizon, frozen_baseline, retain_path=evaluate,cache=cache)
                counts["verified"] += 1
                horizon_counts[horizon] += 1
                if evaluate:
                    verified_details[key] = receipts[0]
                    verified_paths[key] = proof["path"]
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
            "path_read_cache":{"scope":"SAME_EXECUTION_ONLY","hits":cache.hits,"misses":cache.misses},
            "scientific_pit_eligible": False, "forecast_authority": False,
            "edge_established": False, "outcomes_used_as_features": False,
            "status": "REPLAY_COMPLETE" if counts["verified"] and not counts["rejected"] and not orphans else "REPLAY_BLOCKED"}
    if evaluate:
        result["matched_research"] = evaluate_verified_cohort(replay, result, verified_rows, verified_details, sequence_inputs, source_baselines, verified_paths)
    return result


def episode_opportunity(episodes, rows, details, baselines, verified_paths):
    """Compare on a common ORIGINAL endpoint, not moving 24h/72h/7d targets.

    This is descriptive research on observed crossing episodes. Never call
    an observation-proxy a confirmed original signal or a realized trade.
    A closed episode without observed completion is a separate wait case.
    An open/censored episode or unavailable outcome cannot be scored.
    """
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
                    "observation_delay_hours": None, "trade_pnl": None,
                    "same_path_later_baseline_verified": False,
                    "wait_comparator": "NO_RELATIVE_EXPOSURE_NOT_CASH_OR_PORTFOLIO_RETURN"}
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
            # A later source revision must not silently splice a different
            # price history into the earlier receipt's endpoint calculation.
            same_path = verified_paths.get((early["event_id"], h), {})
            bound = same_path.get(late_base["timestamp_utc"])
            if (bound is None or
                    bound["source_window_end_utc"] != late_base["source_window_end_utc"] or
                    bridge.clock(bound["source_window_end_utc"]) > bridge.clock(completion) or
                    any(bound[asset+"_close"] != float(late_base[asset+"_close"])
                        for asset in ("ethbtc","btc","eth"))):
                item["status"] = "LATER_BASELINE_NOT_RECONCILED_TO_ORIGINAL_OUTCOME_PATH"
                continue
            later_price = float(late_base["ethbtc_close"])
            if not math.isfinite(later_price) or later_price <= 0:
                raise ValueError("EPISODE_BASELINE_INVALID")
            wait_return = (float(detail["ethbtc_end"]) / later_price - 1) * 100
            item.update(status="COMMON_ENDPOINT_OBSERVATION_BASELINE_PROXY",
                        same_path_later_baseline_verified=True,
                        wait_relative_return_pct=wait_return, early_minus_wait_pp=early_return-wait_return,
                        observation_delay_hours=(bridge.clock(completion)-bridge.clock(first)).total_seconds()/3600)
        results.append(entry)
    return {"contract": "OBSERVED_EPISODE_COMMON_ENDPOINT_DIAGNOSTIC_v1",
            "episode_n": len(results), "episodes": results,
            "independent_episode_n": None, "causal_delay_cost_established": False,
            "economic_opportunity_cost_established": False, "original_sequence_equivalence": False,
            "scientific_pit_eligible": False, "forecast_authority": False}


def evaluate_verified_cohort(replay, audit, rows, details, sequence_inputs, baselines, verified_paths):
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
    opportunity = episode_opportunity(census["episodes"], rows, details, baselines, verified_paths)
    magnitude = matched_veto_magnitude(rows, details, replay.floor, weekly.CORE_ABLATIONS, ablation["horizons"])
    return {"contract": "PINNED_MATCHED_CORE_AND_EPISODE_RESEARCH_v1",
            "status": "DESCRIPTIVE_ONLY_NOT_INDEPENDENT_EDGE",
            "authority": "RESEARCH_ONLY_NON_CANONICAL",
            "source_owner": "ORIGINAL_FEATURE_AND_OUTCOME_SOURCE_BYTES_REPLAYED",
            "core_ablation": ablation, "episode_opportunity": opportunity,
            "veto_magnitude": magnitude,
            "dependence": weekly.dependence_census(rows,runtime),
            "scientific_pit_eligible": False, "forecast_authority": False,
            "automatic_weight_updates": False, "edge_established": False}


def matched_veto_magnitude(rows, details, floor, families, panels):
    """Measure endpoint magnitudes on the same already verified veto subset.

    No compounding, overlapping-horizon portfolio, strategy fill assumptions,
    weights, significance, or optimization. Calendar blocks describe coverage
    and must not be treated as independent market shocks.
    """
    from datetime import timedelta
    from statistics import mean
    from collections import defaultdict

    def summarize(values):
        positives = [v for v in values if v > 0]
        negatives = [v for v in values if v < 0]
        return {
            "pivotal_veto_n": len(values),
            "positive_missed_n": len(positives),
            "negative_prevented_n": len(negatives),
            "zero_return_n": len(values)-len(positives)-len(negatives),
            "mean_positive_missed_relative_return_pct": mean(positives) if positives else None,
            "mean_negative_prevented_relative_return_pct": mean(negatives) if negatives else None,
            "mean_signed_veto_relative_return_pct": mean(values) if values else None,
            "worst_vetoed_relative_return_pct": min(values) if values else None,
            "best_vetoed_relative_return_pct": max(values) if values else None,
        }

    if len({r["event_id"] for r in rows}) != len(rows):
        raise ValueError("VETO_MAGNITUDE_DUPLICATE_PARENT")
    parsed = [(r,json.loads(r["candidate_decisions"])) for r in rows]
    result = {}
    for horizon,panel in panels.items():
        matched = [(r,d,details[(r["event_id"],horizon)]) for r,d in parsed
                   if (r["event_id"],horizon) in details]
        if len(matched) != panel["matched_matured_n"]:
            raise ValueError("VETO_MAGNITUDE_DENOMINATOR_MISMATCH")
        horizon_result = {}
        for family,without in families.items():
            blocks = defaultdict(list)
            values = []
            for row,d,detail in matched:
                if type(d[without]) is not bool or type(d["C07_SIMPLE_3"]) is not bool:
                    raise ValueError("VETO_MAGNITUDE_NONBOOLEAN")
                if d["C07_SIMPLE_3"] and not d[without]:
                    raise ValueError("VETO_MAGNITUDE_NOT_CONJUNCTIVE")
                if not d[without] or d["C07_SIMPLE_3"]:
                    continue
                value = float(detail["ethbtc_forward_return_pct"])
                at = bridge.clock(row["observation_timestamp_utc"])
                if not math.isfinite(value) or at < floor:
                    raise ValueError("VETO_MAGNITUDE_INVALID")
                block = (at-floor)//timedelta(days=28)
                blocks[block].append(value)
                values.append(value)
            stats = summarize(values)
            original = panel["families"][family]
            if (stats["pivotal_veto_n"] != original["pivotal_veto_n"] or
                    stats["positive_missed_n"] != original["positive_relative_outcomes_missed_n"] or
                    stats["negative_prevented_n"]+stats["zero_return_n"] != original["negative_relative_outcomes_vetoed_n"]):
                raise ValueError("VETO_MAGNITUDE_PAIRED_ACCOUNTING_MISMATCH")
            horizon_result[family] = {**stats,"calendar_blocks": [
                {"block_index":k,**summarize(v)} for k,v in sorted(blocks.items())],
                "matched_matured_n":len(matched)}
        result[horizon]=horizon_result
    return {"contract":"MATCHED_VETO_RETURN_MAGNITUDE_v1",
            "status":"DESCRIPTIVE_ONLY_OVERLAPPING_OBSERVATIONS",
            "horizons":result,"independent_sample_n":None,
            "portfolio_return":None,"causal_effect_established":False,
            "forecast_authority":False,"automatic_weight_updates":False}


def immutable_delta_inventory(before_rows,before_details,after_rows,after_details,mutable_fields):
    """Plan the incremental work from two immutable ledger snapshots.

    No cached verdicts, no trust transfer, no outcome selection. Changed or
    removed previously sealed identities require review/full replay. New
    mature receipts for old observations are explicitly distinguished from
    new feature rows. Never authorize skipping source verification.
    """
    def unique(rows,key):
        result={}
        for row in rows:
            ident=key(row)
            if ident in result: raise ValueError("DELTA_DUPLICATE_IDENTITY")
            result[ident]=row
        return result
    before=unique(before_rows,lambda r:r["event_id"])
    after=unique(after_rows,lambda r:r["event_id"])
    bd=unique(before_details,lambda r:(r["event_id"],r["horizon"]))
    ad=unique(after_details,lambda r:(r["event_id"],r["horizon"]))
    frozen=lambda row:{k:v for k,v in row.items() if k not in mutable_fields}
    removed=sorted(before.keys()-after.keys())
    changed=sorted(k for k in before.keys()&after.keys() if frozen(before[k])!=frozen(after[k]))
    new=sorted(after.keys()-before.keys())
    removed_detail=sorted(bd.keys()-ad.keys())
    changed_detail=sorted(k for k in bd.keys()&ad.keys() if bd[k]!=ad[k])
    new_detail=sorted(ad.keys()-bd.keys())
    orphan=sorted(k for k in ad if k[0] not in after or k[1] not in ("24h","72h","7d"))
    # A prior matured parent label or statistic is immutable too, even
    # though it is excluded from the original feature provenance hash.
    altered_matured=[]
    for event,horizon in bd.keys()&ad.keys():
        if event in before and event in after and any(
                before[event].get(f"{field}_{horizon}")!=after[event].get(f"{field}_{horizon}")
                for field in ("outcome","mae","mfe")):
            altered_matured.append((event,horizon))
    blocked=bool(removed or changed or removed_detail or changed_detail or orphan or altered_matured)
    body={"contract":"CN_MM_IMMUTABLE_LEARNING_DELTA_v1",
          "status":"REVIEW_FULL_REPLAY_REQUIRED" if blocked else "APPEND_ONLY_DELTA_IDENTIFIED",
          "previous_parent_n":len(before),"current_parent_n":len(after),
          "previous_receipt_n":len(bd),"current_receipt_n":len(ad),
          "new_parent_ids":new,"new_receipt_keys":[list(x) for x in new_detail],
          "new_matured_prior_parent_n":sum(k[0] in before for k in new_detail),
          "unchanged_parent_n":len(before.keys()&after.keys())-len(changed),
          "unchanged_receipt_n":len(bd.keys()&ad.keys())-len(changed_detail),
          "removed_parent_ids":removed,"changed_frozen_parent_ids":changed,
          "removed_receipt_keys":[list(x) for x in removed_detail],
          "changed_receipt_keys":[list(x) for x in changed_detail],
          "orphan_receipt_keys":[list(x) for x in orphan],
          "altered_matured_parent_keys":[list(x) for x in sorted(altered_matured)],
          "prior_verdict_reuse_authorized":False,"scientific_pit_eligible":False,
          "automatic_weight_updates":False,"forecast_authority":False}
    body["inventory_sha256"]=bridge.sha(bridge.canon(body))
    return body
