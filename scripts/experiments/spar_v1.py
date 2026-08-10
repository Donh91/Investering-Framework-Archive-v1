from __future__ import annotations

import argparse
import csv
import json
import statistics
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

CONTRACT = "SPAR_REPLAY_REPORT_v1"
FRAGILITY_CONTRACT = "SPAR_FRAGILITY_REPORT_v1"
INPUT_ADAPTER = "SPAR_INPUT_ADAPTER_v2"
V2_CONTRACT = "DAILY_RAW_CAPTURE_INDEX_v2"
V3_CONTRACT = "DAILY_LIVE_ANCHOR_INDEX_v3"
PATTERNS = ("SPAR-P1", "SPAR-P2", "SPAR-P3")
PREREGISTRATION_UTC = "2026-08-08T07:16:55Z"
ADAPTER_V2_CUTOVER_UTC = "2026-08-09T19:58:03Z"


def ts(x: str) -> datetime:
    return datetime.fromisoformat(x.replace("Z", "+00:00")).astimezone(timezone.utc)


def iso(x: datetime) -> str:
    return x.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def pct(a: float, b: float):
    return None if b == 0 else (a / b - 1) * 100


def med(x):
    return statistics.median(x) if x else None


@dataclass(frozen=True)
class Snapshot:
    p: str
    t: datetime
    btc: float
    eth: float
    eb: float
    adv: float
    dec: float
    fund: float
    oi: float
    source_contract: str = V2_CONTRACT
    spot_source_timestamp: datetime | None = None

    @property
    def breadth(self):
        return self.adv - self.dec


def completed_hour_open(t: datetime) -> datetime:
    return t.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)


def evidence_phase(t: datetime) -> str:
    return "PROSPECTIVE_POST_PREREGISTRATION" if t >= ts(PREREGISTRATION_UTC) else "RETROSPECTIVE_ARCHIVE_REPLAY"


def adapter_phase(t: datetime) -> str:
    return "POST_ADAPTER_V2_CUTOVER" if t >= ts(ADAPTER_V2_CUTOVER_UTC) else "PRE_ADAPTER_V2_CUTOVER"


def load_hourly_spot_rows(root: Path):
    rows = {}
    if not root.exists():
        return rows
    for p in sorted(root.rglob("*.csv")):
        try:
            with p.open(newline="") as fh:
                for row in csv.DictReader(fh):
                    if row.get("spot_status") != "PASS":
                        continue
                    try:
                        t = ts(row["timestamp_utc"])
                        rows[t] = {
                            "btc": float(row["btc_close"]),
                            "eth": float(row["eth_close"]),
                            "eb": float(row["ethbtc_close"]),
                            "path": str(p),
                        }
                    except Exception:
                        continue
        except Exception:
            continue
    return rows


def load_snapshot_with_reason(p: Path, hourly_spot=None) -> tuple[Snapshot | None, str | None]:
    try:
        o = json.loads(p.read_text())
    except Exception:
        return None, "JSON_PARSE_ERROR"
    if not isinstance(o, dict):
        return None, "NON_OBJECT_JSON"
    contract = o.get("contract")
    if contract not in {V2_CONTRACT, V3_CONTRACT}:
        return None, f"UNSUPPORTED_CONTRACT:{contract}"
    try:
        m = o["market_metrics"]
        if contract == V2_CONTRACT:
            t = ts(o["captured_at_utc"])
            return Snapshot(
                str(p),
                t,
                float(m["spot"]["BTCUSDT"]["close"]),
                float(m["spot"]["ETHUSDT"]["close"]),
                float(m["spot"]["ETHBTC"]["close"]),
                float(m["breadth"]["advancers"]),
                float(m["breadth"]["decliners"]),
                float(m["derivatives"]["BTC-USDT-SWAP"]["funding"]["funding_rate"]),
                float(m["derivatives"]["BTC-USDT-SWAP"]["open_interest"]["open_interest_ccy"]),
                source_contract=V2_CONTRACT,
                spot_source_timestamp=t,
            ), None
        t = ts(o["captured_at_utc"])
        spot_t = completed_hour_open(t)
        row = (hourly_spot or {}).get(spot_t)
        if not row:
            return None, "V3_MISSING_EXACT_PREVIOUS_COMPLETED_HOUR_SPOT"
        return Snapshot(
            str(p),
            t,
            float(row["btc"]),
            float(row["eth"]),
            float(row["eb"]),
            float(m["breadth"]["advancers"]),
            float(m["breadth"]["decliners"]),
            float(m["derivatives"]["BTC-USDT-SWAP"]["funding"]["funding_rate"]),
            float(m["derivatives"]["BTC-USDT-SWAP"]["open_interest"]["open_interest_ccy"]),
            source_contract=V3_CONTRACT,
            spot_source_timestamp=spot_t,
        ), None
    except Exception:
        return None, "MISSING_OR_INVALID_REQUIRED_FIELDS"


def load_snapshot(p: Path, hourly_spot=None):
    snapshot, _ = load_snapshot_with_reason(p, hourly_spot)
    return snapshot


def load_snapshots_audit(root: Path) -> tuple[list[Snapshot], dict[str, Any]]:
    dedup: dict[datetime, Snapshot] = {}
    hourly = load_hourly_spot_rows(root.parent / "hourly")
    attempted = 0
    dropped: dict[str, int] = {}
    accepted_by_contract = {V2_CONTRACT: 0, V3_CONTRACT: 0}
    duplicate_timestamp_count = 0
    for p in sorted(root.rglob("*.json")):
        if p.name == "LATEST.json":
            continue
        attempted += 1
        s, reason = load_snapshot_with_reason(p, hourly)
        if s is None:
            dropped[reason or "UNKNOWN_DROP"] = dropped.get(reason or "UNKNOWN_DROP", 0) + 1
            continue
        accepted_by_contract[s.source_contract] = accepted_by_contract.get(s.source_contract, 0) + 1
        if s.t in dedup:
            duplicate_timestamp_count += 1
        dedup[s.t] = s
    snaps = [dedup[k] for k in sorted(dedup)]
    audit = {
        "input_json_files_attempted": attempted,
        "accepted_unique_snapshot_count": len(snaps),
        "accepted_by_contract_before_timestamp_dedup": accepted_by_contract,
        "duplicate_timestamp_count": duplicate_timestamp_count,
        "dropped_count": sum(dropped.values()),
        "dropped_by_reason": dict(sorted(dropped.items())),
        "hourly_spot_rows_available": len(hourly),
        "silent_drop_policy": False,
    }
    return snaps, audit


def load_snapshots(root: Path):
    return load_snapshots_audit(root)[0]


def transition(a: Snapshot, b: Snapshot):
    return {
        "breadth_deterioration": b.breadth < a.breadth,
        "leverage_build": b.oi > a.oi and b.fund > a.fund,
        "eth_relative_weakness": b.eb < a.eb,
        "btc_resilience": b.btc >= a.btc,
    }


def ordered(tr, start, names, max_steps):
    pos = start
    end = min(len(tr), start + max_steps)
    for name in names:
        hit = next((i for i in range(pos, end) if tr[i].get(name)), None)
        if hit is None:
            return None
        pos = hit + 1
    return pos - 1


def detect_events(snaps, cooldown_hours=72):
    # Existing SPAR-v1 event semantics are intentionally preserved.
    # In particular, P3 can satisfy its two logical clauses in the same
    # transition under v1. A strict temporal P3 would require a NEW prospective
    # experiment identity; it is not silently repaired here after outcomes exist.
    out = {k: [] for k in PATTERNS}
    if len(snaps) < 2:
        return out
    tr = [transition(snaps[i - 1], snaps[i]) for i in range(1, len(snaps))]
    raw = {k: [] for k in out}
    for i in range(len(tr)):
        a = ordered(tr, i, ["breadth_deterioration", "leverage_build", "eth_relative_weakness"], 4)
        b = ordered(tr, i, ["leverage_build", "breadth_deterioration", "eth_relative_weakness"], 4)
        if a is not None:
            raw["SPAR-P1"].append(a + 1)
        if b is not None:
            raw["SPAR-P2"].append(b + 1)
        if tr[i]["btc_resilience"] and tr[i]["breadth_deterioration"]:
            c = next((j for j in range(i, min(len(tr), i + 3)) if tr[j]["eth_relative_weakness"]), None)
            if c is not None:
                raw["SPAR-P3"].append(c + 1)
    for k, idxs in raw.items():
        last = None
        for idx in sorted(set(idxs)):
            if last is None or (snaps[idx].t - snaps[last].t).total_seconds() >= cooldown_hours * 3600:
                out[k].append(idx)
                last = idx
    return out


def outcome(snaps, i, h):
    target = snaps[i].t + timedelta(hours=h)
    cand = [
        (abs((s.t - target).total_seconds()), j)
        for j, s in enumerate(snaps)
        if j > i and abs((s.t - target).total_seconds()) <= 6 * 3600
    ]
    base = {
        "nominal_horizon_hours": h,
        "scheduled_target_timestamp_utc": iso(target),
        "planned_window_crosses_adapter_v2_cutover": snaps[i].t < ts(ADAPTER_V2_CUTOVER_UTC) <= target,
    }
    if not cand:
        return {**base, "status": "PENDING"}
    delta_seconds, j = min(cand)
    path = snaps[i : j + 1]
    s0 = snaps[i]
    sj = snaps[j]
    return {
        **base,
        "status": "MATURED",
        "target_timestamp_utc": iso(sj.t),
        "target_offset_hours": round((sj.t - target).total_seconds() / 3600, 6),
        "btc_return_pct": pct(sj.btc, s0.btc),
        "btc_mae_pct": min(pct(s.btc, s0.btc) for s in path),
        "btc_mfe_pct": max(pct(s.btc, s0.btc) for s in path),
        "eth_return_pct": pct(sj.eth, s0.eth),
        "eth_mae_pct": min(pct(s.eth, s0.eth) for s in path),
        "eth_mfe_pct": max(pct(s.eth, s0.eth) for s in path),
        "ethbtc_return_pct": pct(sj.eb, s0.eb),
        "matched_target_absolute_error_hours": round(delta_seconds / 3600, 6),
    }


def non_overlapping_count(times: list[datetime], horizon_hours: int) -> int:
    count = 0
    last: datetime | None = None
    for value in sorted(times):
        if last is None or (value - last).total_seconds() >= horizon_hours * 3600:
            count += 1
            last = value
    return count


def max_consecutive_overlap_hours(times: list[datetime], horizon_hours: int) -> float:
    ordered_times = sorted(times)
    if len(ordered_times) < 2:
        return 0.0
    return round(
        max(
            max(0.0, horizon_hours - (b - a).total_seconds() / 3600)
            for a, b in zip(ordered_times, ordered_times[1:])
        ),
        6,
    )


def descriptive_unconditional_context(snaps: list[Snapshot]) -> dict[str, Any]:
    horizons: dict[str, Any] = {}
    for h in (24, 72, 168):
        matured = []
        for i in range(len(snaps)):
            result = outcome(snaps, i, h)
            if result["status"] == "MATURED":
                matured.append(result)
        horizons[str(h)] = {
            "matured_anchor_count": len(matured),
            "non_overlapping_anchor_count": non_overlapping_count([s.t for s in snaps], h),
            "median_btc_return_pct": med([r["btc_return_pct"] for r in matured]),
            "median_eth_return_pct": med([r["eth_return_pct"] for r in matured]),
            "median_ethbtc_return_pct": med([r["ethbtc_return_pct"] for r in matured]),
        }
    return {
        "authority": "DESCRIPTIVE_CONTEXT_ONLY_NOT_COMPARATOR_NOT_INCREMENTAL_EVIDENCE",
        "purpose": "Expose unconditional same-source outcome context without changing SPAR-v1 hypothesis, baseline or promotion logic.",
        "horizons": horizons,
    }


def all_patterns_at_least(patterns: list[dict[str, Any]], count: int) -> bool:
    by_id = {str(p.get("pattern_id")): int(p.get("matured_72h_count", 0)) for p in patterns}
    return all(by_id.get(pattern, 0) >= count for pattern in PATTERNS)


def build_replay(snaps, min_matured_events=5, source_audit: dict[str, Any] | None = None):
    ev = detect_events(snaps)
    patterns = []
    for k, idxs in ev.items():
        rows = []
        for i in idxs:
            event_t = snaps[i].t
            rows.append({
                "event_timestamp_utc": iso(event_t),
                "source_path": snaps[i].p,
                "source_contract": snaps[i].source_contract,
                "evidence_phase": evidence_phase(event_t),
                "adapter_phase": adapter_phase(event_t),
                "outcomes": {str(h): outcome(snaps, i, h) for h in (24, 72, 168)},
            })
        vals = [
            e["outcomes"]["72"]["btc_return_pct"]
            for e in rows
            if e["outcomes"]["72"]["status"] == "MATURED"
        ]
        ok = len(vals) >= min_matured_events
        times = [snaps[i].t for i in idxs]
        patterns.append({
            "pattern_id": k,
            "event_count": len(rows),
            "matured_72h_count": len(vals),
            "median_btc_return_72h_pct": med(vals),
            "status": "BASE_REVIEW_READY" if ok else "INSUFFICIENT_EVIDENCE",
            "independence_diagnostics": {
                "raw_event_count": len(times),
                "non_overlapping_72h_event_count": non_overlapping_count(times, 72),
                "non_overlapping_168h_event_count": non_overlapping_count(times, 168),
                "max_consecutive_168h_window_overlap_hours": max_consecutive_overlap_hours(times, 168),
                "formal_effective_n_estimated": False,
            },
            "events": rows,
        })
    ready = all_patterns_at_least(patterns, min_matured_events)
    prospective_snapshots = sum(s.t >= ts(PREREGISTRATION_UTC) for s in snaps)
    return {
        "contract": CONTRACT,
        "authority": "SHADOW_RESEARCH_ONLY",
        "status": "READY_FOR_ROBUSTNESS_REVIEW" if ready else "INSUFFICIENT_EVIDENCE",
        "scientific_status": "METHODS_REQUIRES_PROSPECTIVE_HARDENING_DESCRIPTIVE_ONLY",
        "claim_boundary": {
            "incremental_value_beyond_single_sensor_states_established": False,
            "single_sensor_control_baseline_frozen_in_v1": False,
            "current_identity_allowed_claim": "DESCRIPTIVE_SEQUENCE_OUTCOME_ASSOCIATION_ONLY",
            "new_inferential_baseline_requires_new_prospective_identity": True,
        },
        "source": {
            "snapshot_count": len(snaps),
            "min_timestamp_utc": iso(snaps[0].t) if snaps else None,
            "max_timestamp_utc": iso(snaps[-1].t) if snaps else None,
            "retrospective_pre_preregistration_snapshot_count": len(snaps) - prospective_snapshots,
            "prospective_post_preregistration_snapshot_count": prospective_snapshots,
            "audit": source_audit or {"audit_available": False},
        },
        "method": {
            "future_leakage": False,
            "fitted_thresholds": False,
            "episode_cooldown_hours": 72,
            "paid_api_calls": 0,
            "input_adapter": INPUT_ADAPTER,
            "v3_spot_join_policy": "EXACT_PREVIOUS_COMPLETED_UTC_HOUR_ONLY",
            "interpolation": False,
            "forward_fill": False,
            "preregistration_timestamp_utc": PREREGISTRATION_UTC,
            "adapter_v2_cutover_utc": ADAPTER_V2_CUTOVER_UTC,
            "top_level_base_review_requires_all_patterns": True,
            "p3_v1_same_transition_satisfaction_possible": True,
            "p3_strict_temporal_sequence_requires_new_identity": True,
        },
        "descriptive_unconditional_context": descriptive_unconditional_context(snaps),
        "patterns": patterns,
    }


def loo_stable(vals):
    if len(vals) < 3:
        return None
    base = med(vals)
    if base == 0:
        return False
    sign = base > 0
    return all(((med(vals[:i] + vals[i + 1 :]) or 0) > 0) == sign for i in range(len(vals)))


def build_fragility(base, min_events=10):
    rows = []
    for p in base.get("patterns", []):
        vals = [
            float(e["outcomes"]["72"]["btc_return_pct"])
            for e in p.get("events", [])
            if e.get("outcomes", {}).get("72", {}).get("status") == "MATURED"
        ]
        ok = len(vals) >= min_events
        row = {
            "pattern_id": p.get("pattern_id"),
            "matured_72h_count": len(vals),
            "median_btc_return_pct": med(vals),
            "status": "LOO_DIAGNOSTIC_AVAILABLE_METHODS_BLOCKED" if ok else "INSUFFICIENT_EVIDENCE",
        }
        if ok:
            row["leave_one_out_sign_stable"] = loo_stable(vals)
            row["loo_interpretation"] = "SINGLE_POINT_DELETION_DIAGNOSTIC_NOT_EFFECT_EVIDENCE_NOT_NULL_TEST"
        rows.append(row)
    all_ready = all_patterns_at_least(rows, min_events)
    return {
        "contract": FRAGILITY_CONTRACT,
        "authority": "SHADOW_RESEARCH_ONLY",
        "status": "METHODS_BLOCKED_PLACEBO_REGIME_NOT_FROZEN" if all_ready else "INSUFFICIENT_EVIDENCE",
        "scientific_status": "METHODS_REQUIRES_PROSPECTIVE_HARDENING",
        "minimum_events_for_loo_diagnostic": min_events,
        "minimum_events_for_placebo_and_regime_split": min_events,
        "patterns": rows,
        "notes": [
            "LOO is not emitted below the frozen 10-event fragility gate.",
            "LOO sign stability is a deletion sensitivity diagnostic, not evidence of separation from a null.",
            "Placebo timestamp construction and regime split mechanics are not frozen; no robustness-ready status may be emitted until a prospective methods contract exists.",
            "No candidate may be promoted from this report.",
        ],
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["replay", "fragility"], required=True)
    p.add_argument("--capture-root", type=Path)
    p.add_argument("--base-report", type=Path)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--min-matured-events", type=int, default=5)
    p.add_argument("--min-fragility-events", type=int, default=10)
    a = p.parse_args()
    if a.mode == "replay":
        if not a.capture_root:
            raise SystemExit("capture_root_required")
        snaps, audit = load_snapshots_audit(a.capture_root)
        r = build_replay(snaps, a.min_matured_events, source_audit=audit)
    else:
        if not a.base_report:
            raise SystemExit("base_report_required")
        r = build_fragility(json.loads(a.base_report.read_text()), a.min_fragility_events)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(r, sort_keys=True, separators=(",", ":")) + "\n")
    print(json.dumps({"contract": r["contract"], "status": r["status"]}, sort_keys=True))


if __name__ == "__main__":
    main()
