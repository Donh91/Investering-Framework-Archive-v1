"""Read-only original outcome-owner replay for research, never feature-side input."""
from __future__ import annotations

import hashlib
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


def audit_outcome_cohort(replay):
    import json
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
        replay.verify(projection, at, json.loads(projection["candidate_decisions"]))
        frozen_baseline = json.loads(projection["source_binding_manifest"])["families"]["ETHBTC_PERSISTENCE"]["baseline"]
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
            except (ValueError, RuntimeError, TypeError, KeyError, AttributeError, OSError, OverflowError,
                    __import__("subprocess").SubprocessError) as exc:
                counts["rejected"] += 1
                failures.append({"event_id": event, "horizon": horizon, "reason": str(exc)[:200]})
    orphans = sum(len(v) for k,v in indexed.items() if k not in used)
    return {"contract": "PINNED_MATURED_OUTCOME_SOURCE_AUDIT_v1",
            "checkout_sha": replay.checkout, "parent_n": len(seen),
            "verified_n": counts["verified"], "unmatured_or_unavailable_n": counts["unmatured_or_unavailable"],
            "rejected_n": counts["rejected"], "orphan_or_excluded_detail_n": orphans,
            "verified_horizon_counts": dict(horizon_counts), "failures": failures,
            "scientific_pit_eligible": False, "forecast_authority": False,
            "edge_established": False, "outcomes_used_as_features": False,
            "status": "REPLAY_COMPLETE" if counts["verified"] and not counts["rejected"] and not orphans else "REPLAY_BLOCKED"}
