#!/usr/bin/env python3
"""Deterministic repository-native replacement for routine external OTA research pings.

This script makes no external source calls and has no market/portfolio authority. It
reads already-materialized owner artifacts, reconciles settled versus live market
observations, and emits a compact research packet on fixed runs or when an existing
registered early trigger is observed.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

REGISTERED_ETHBTC_FLOOR = 0.0300
DIRECTOR_WARNING_TRIGGERS = {
    "PARABOLIC_ALTSEASON_WARNING",
    "DISTRIBUTION_WARNING",
    "EXIT_WARNING",
    "STRUCTURAL_BREAKDOWN_WARNING",
}
AUTHORITY = {
    "canonical_market_state": False,
    "market_rule_change": False,
    "threshold_change": False,
    "portfolio_action": False,
    "automatic_promotion": False,
    "purpose": "RESEARCH_ONLY_RECONCILIATION_AND_TRIGGER_WATCH",
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_time(value: str | None) -> datetime | None:
    if not value or not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None


def as_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def extract_timestamp(payload: dict[str, Any]) -> str | None:
    keys = (
        "retrieved_at_utc",
        "generated_at_utc",
        "captured_at_utc",
        "source_timestamp_utc",
        "verification_completed_at_utc",
        "normalization_time",
        "timestamp_utc",
    )
    for key in keys:
        value = payload.get(key)
        if parse_time(value):
            return value
    lifecycle = payload.get("lifecycle")
    if isinstance(lifecycle, dict):
        for key in keys:
            value = lifecycle.get(key)
            if parse_time(value):
                return value
    return None


def age_minutes(timestamp: str | None, now: datetime) -> float | None:
    dt = parse_time(timestamp)
    if not dt:
        return None
    return round((now - dt).total_seconds() / 60.0, 2)


def resolve_pointer(repo: Path, pointer_path: Path) -> tuple[dict[str, Any] | None, str | None]:
    pointer = load_json(pointer_path)
    if not pointer:
        return None, None
    target = pointer.get("path")
    if isinstance(target, str):
        payload = load_json(repo / target)
        if payload:
            return payload, target
    return pointer, str(pointer_path.relative_to(repo)) if pointer_path.exists() else None


def latest_matching(root: Path, pattern: str) -> Path | None:
    if not root.exists():
        return None
    files = sorted(root.glob(pattern))
    return files[-1] if files else None


def read_hourly_file(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(newline="") as handle:
            return list(csv.DictReader(handle))
    except (FileNotFoundError, OSError):
        return []


def summarize_session(path: Path) -> dict[str, Any] | None:
    rows = read_hourly_file(path)
    if not rows:
        return None
    valid = []
    for row in rows:
        stamp = parse_time(row.get("timestamp_utc"))
        if stamp is None:
            continue
        valid.append((stamp, row))
    if not valid:
        return None
    valid.sort(key=lambda item: item[0])
    dates = {stamp.date().isoformat() for stamp, _ in valid}
    if len(dates) != 1:
        return None
    hours = {stamp.hour for stamp, _ in valid}
    settled = hours == set(range(24)) and len(valid) >= 24
    first = valid[0][1]
    last = valid[-1][1]

    def numeric(field: str) -> list[float]:
        return [v for _, row in valid if (v := as_float(row.get(field))) is not None]

    btc_open = as_float(first.get("btc_open"))
    btc_close = as_float(last.get("btc_close"))
    eth_open = as_float(first.get("eth_open"))
    eth_close = as_float(last.get("eth_close"))
    btc_highs = numeric("btc_high")
    btc_lows = numeric("btc_low")
    eth_highs = numeric("eth_high")
    eth_lows = numeric("eth_low")
    ethbtc_lows = numeric("ethbtc_low")
    ethbtc_highs = numeric("ethbtc_high")
    ethbtc_close = as_float(last.get("ethbtc_close"))
    ethbtc_open = as_float(first.get("ethbtc_open"))

    def pct(open_: float | None, close_: float | None) -> float | None:
        if open_ in (None, 0) or close_ is None:
            return None
        return round((close_ / open_ - 1.0) * 100.0, 6)

    btc_ret = pct(btc_open, btc_close)
    eth_ret = pct(eth_open, eth_close)
    return {
        "date_utc": next(iter(dates)),
        "path": str(path),
        "row_count": len(valid),
        "hours_present": sorted(hours),
        "status": "SETTLED" if settled else "IN_PROGRESS",
        "btc": {
            "open": btc_open,
            "high": max(btc_highs) if btc_highs else None,
            "low": min(btc_lows) if btc_lows else None,
            "close": btc_close,
            "return_pct": btc_ret,
        },
        "eth": {
            "open": eth_open,
            "high": max(eth_highs) if eth_highs else None,
            "low": min(eth_lows) if eth_lows else None,
            "close": eth_close,
            "return_pct": eth_ret,
        },
        "ethbtc": {
            "open": ethbtc_open,
            "high": max(ethbtc_highs) if ethbtc_highs else None,
            "low": min(ethbtc_lows) if ethbtc_lows else None,
            "close": ethbtc_close,
            "return_pct": pct(ethbtc_open, ethbtc_close),
        },
        "eth_minus_btc_return_pp": None if btc_ret is None or eth_ret is None else round(eth_ret - btc_ret, 6),
    }


def load_sessions(repo: Path) -> list[dict[str, Any]]:
    root = repo / "03_DAILY_CAPTURE_LOGS/hourly"
    sessions: list[dict[str, Any]] = []
    for path in sorted(root.glob("[0-9][0-9][0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].csv")):
        item = summarize_session(path)
        if item:
            item["path"] = str(path.relative_to(repo))
            sessions.append(item)
    sessions.sort(key=lambda x: x["date_utc"])
    return sessions


def trailing_count(items: list[bool], value: bool = True) -> int:
    count = 0
    for item in reversed(items):
        if item is value:
            count += 1
        else:
            break
    return count


def director_snapshot(repo: Path, now: datetime) -> dict[str, Any]:
    root = repo / "research/api_agent/outputs/daily"
    path = latest_matching(root, "**/DAILY_DIRECTOR_OUTPUT.json")
    if not path:
        return {"status": "UNAVAILABLE", "path": None, "warning": None}
    payload = load_json(path) or {}
    summary = payload.get("summary") if isinstance(payload.get("summary"), str) else ""
    match = re.search(r"(?:^|\|\s*)WARNING=([A-Z_]+)", summary)
    warning = match.group(1) if match else None
    return {
        "status": payload.get("status", "UNKNOWN"),
        "path": str(path.relative_to(repo)),
        "warning": warning,
        "summary_header": summary.splitlines()[0] if summary else None,
        "age_minutes": age_minutes(extract_timestamp(payload), now),
    }


def owner_snapshot(repo: Path, now: datetime) -> dict[str, Any]:
    owners: dict[str, Any] = {}

    etf, etf_path = resolve_pointer(repo, repo / "03_DAILY_CAPTURE_LOGS/etf/LATEST.json")
    if etf:
        totals = {}
        for row in etf.get("rows", []) if isinstance(etf.get("rows"), list) else []:
            if isinstance(row, dict) and row.get("asset") in {"BTC", "ETH"}:
                totals[row["asset"]] = row.get("reported_total")
        owners["settled_etf"] = {
            "status": "PASS" if etf.get("session_date") else etf.get("status", "UNKNOWN"),
            "path": etf_path,
            "session_date": etf.get("session_date"),
            "reported_totals": totals,
            "session_final": all(bool(r.get("session_final")) for r in etf.get("rows", []) if isinstance(r, dict)) if etf.get("rows") else None,
            "age_minutes": age_minutes(extract_timestamp(etf), now),
            "authority": etf.get("authority"),
        }
    else:
        owners["settled_etf"] = {"status": "UNAVAILABLE", "path": None}

    stable = load_json(repo / "03_DAILY_CAPTURE_LOGS/stablecoin_liquidity/LATEST.json")
    if stable:
        owners["stablecoin_liquidity"] = {
            "status": stable.get("status", "PASS"),
            "path": "03_DAILY_CAPTURE_LOGS/stablecoin_liquidity/LATEST.json",
            "age_minutes": age_minutes(extract_timestamp(stable), now),
            "global": stable.get("global"),
            "evidence_semantics": stable.get("evidence_semantics"),
            "authority": stable.get("authority"),
        }
    else:
        owners["stablecoin_liquidity"] = {"status": "UNAVAILABLE", "path": None}

    pullback = load_json(repo / "03_DAILY_CAPTURE_LOGS/pullback_forensics/LATEST.json")
    if pullback:
        lane1 = pullback.get("lane1_liquidations") if isinstance(pullback.get("lane1_liquidations"), dict) else {}
        lane2b = pullback.get("lane2b_moneyness_skew") if isinstance(pullback.get("lane2b_moneyness_skew"), dict) else {}
        owners["pullback_forensics"] = {
            "status": "PASS" if not pullback.get("errors") else "PARTIAL",
            "path": "03_DAILY_CAPTURE_LOGS/pullback_forensics/LATEST.json",
            "liquidations": {asset: data.get("status") for asset, data in lane1.items() if isinstance(data, dict)},
            "moneyness_skew": {asset: data.get("status") for asset, data in lane2b.items() if isinstance(data, dict)},
            "authority": pullback.get("authority"),
            "source_quality_note": "LIQUIDATIONS_MAY_BE_LOWER_BOUND_LEGACY_REST",
        }
    else:
        owners["pullback_forensics"] = {"status": "UNAVAILABLE", "path": None}

    situation, situation_path = resolve_pointer(repo, repo / "03_DAILY_CAPTURE_LOGS/catalyst_overlay/situation_room/LATEST.json")
    if situation:
        owners["situation_room"] = {
            "status": situation.get("run_status", situation.get("status", "UNKNOWN")),
            "path": situation_path,
            "daily_result": situation.get("daily_result"),
            "authority": situation.get("authority"),
            "age_minutes": age_minutes(extract_timestamp(situation), now),
        }
    else:
        owners["situation_room"] = {"status": "UNAVAILABLE", "path": None}

    entry = load_json(repo / "04_MARKET_LEARNING/entry_signals/LATEST.json")
    if entry:
        snapshot = entry.get("market_snapshot") if isinstance(entry.get("market_snapshot"), dict) else {}
        owners["entry_signal_ledger"] = {
            "status": entry.get("state", entry.get("observer_state", "UNKNOWN")),
            "observer_state": entry.get("observer_state"),
            "path": "04_MARKET_LEARNING/entry_signals/LATEST.json",
            "generated_at_utc": entry.get("generated_at_utc"),
            "age_minutes": age_minutes(entry.get("generated_at_utc"), now),
            "ethbtc": snapshot.get("ethbtc"),
            "breadth": snapshot.get("top100_advance_ratio"),
            "authority": entry.get("authority"),
        }
    else:
        owners["entry_signal_ledger"] = {"status": "UNAVAILABLE", "path": None}

    owners["daily_director"] = director_snapshot(repo, now)
    return owners


def settled_analysis(sessions: list[dict[str, Any]]) -> dict[str, Any]:
    settled = [s for s in sessions if s["status"] == "SETTLED"]
    live = [s for s in sessions if s["status"] == "IN_PROGRESS"]
    latest_live = live[-1] if live else None
    latest_settled = settled[-1] if settled else None

    gate_passes = [bool((s.get("ethbtc") or {}).get("close") is not None and s["ethbtc"]["close"] >= REGISTERED_ETHBTC_FLOOR) for s in settled]
    settled_highs = [(s["date_utc"], s["btc"]["high"]) for s in settled if s.get("btc", {}).get("high") is not None]
    settled_cycle_high = max(settled_highs, key=lambda x: x[1]) if settled_highs else None
    live_high = None
    if latest_live and latest_live.get("btc", {}).get("high") is not None:
        live_high = {"date_utc": latest_live["date_utc"], "high": latest_live["btc"]["high"], "status": "IN_PROGRESS_HIGH_NOT_SETTLED_CYCLE_HIGH"}

    leadership = []
    for s in settled:
        pp = s.get("eth_minus_btc_return_pp")
        leadership.append(None if pp is None else pp > 0)
    known_leadership = [x for x in leadership if x is not None]

    last_close = latest_settled.get("ethbtc", {}).get("close") if latest_settled else None
    margin = None if last_close is None else round((last_close / REGISTERED_ETHBTC_FLOOR - 1.0) * 100.0, 6)
    current_low = latest_live.get("ethbtc", {}).get("low") if latest_live else None
    current_margin = None if current_low is None else round((current_low / REGISTERED_ETHBTC_FLOOR - 1.0) * 100.0, 6)

    recent_lows = [
        {"date_utc": s["date_utc"], "low": s.get("ethbtc", {}).get("low"), "status": s["status"]}
        for s in (settled[-6:] + ([latest_live] if latest_live else []))
        if s and s.get("ethbtc", {}).get("low") is not None
    ]

    return {
        "registered_ethbtc_floor": REGISTERED_ETHBTC_FLOOR,
        "settled_session_count": len(settled),
        "latest_settled": latest_settled,
        "latest_in_progress": latest_live,
        "settled_cycle_high": None if settled_cycle_high is None else {"date_utc": settled_cycle_high[0], "high": settled_cycle_high[1], "status": "SETTLED_ONLY"},
        "in_progress_high": live_high,
        "gate": {
            "trailing_settled_closes_at_or_above_floor": trailing_count(gate_passes),
            "settled_failures_total": sum(1 for x in gate_passes if not x),
            "latest_settled_close": last_close,
            "latest_settled_margin_pct": margin,
            "latest_in_progress_low": current_low,
            "latest_in_progress_low_margin_pct": current_margin,
            "recent_lows": recent_lows,
        },
        "eth_leadership": {
            "eth_led_last_4_settled": sum(1 for x in known_leadership[-4:] if x),
            "eth_led_last_6_settled": sum(1 for x in known_leadership[-6:] if x),
            "consecutive_btc_led_settled": trailing_count([not x for x in known_leadership]),
        },
    }


def early_triggers(analysis: dict[str, Any], owners: dict[str, Any]) -> list[dict[str, Any]]:
    triggers: list[dict[str, Any]] = []
    latest = analysis.get("latest_settled")
    close = ((latest or {}).get("ethbtc") or {}).get("close")
    if close is not None and close < REGISTERED_ETHBTC_FLOOR:
        triggers.append({
            "id": "ETHBTC_SETTLED_CLOSE_BELOW_REGISTERED_0_0300",
            "evidence": close,
            "authority": "RESEARCH_ATTENTION_TRIGGER_ONLY",
        })
    warning = (owners.get("daily_director") or {}).get("warning")
    if warning in DIRECTOR_WARNING_TRIGGERS:
        triggers.append({
            "id": f"DAILY_DIRECTOR_{warning}",
            "evidence": warning,
            "authority": "RESEARCH_ATTENTION_TRIGGER_ONLY",
        })
    return triggers


def previous_report(repo: Path, output_root: Path) -> dict[str, Any] | None:
    pointer = load_json(output_root / "LATEST.json")
    if not pointer:
        return None
    target = pointer.get("path")
    return load_json(repo / target) if isinstance(target, str) else None


def classified_deltas(current: dict[str, Any], previous: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not previous:
        return [{"classification": "NEW_INFORMATION", "claim": "First native Framework Research Watch baseline materialized."}]
    deltas: list[dict[str, Any]] = []
    cur = current["market_reconciliation"]
    old = previous.get("market_reconciliation") or {}
    comparisons = [
        ("settled_cycle_high", cur.get("settled_cycle_high"), old.get("settled_cycle_high"), "NEW_INFORMATION"),
        ("ethbtc_gate", cur.get("gate"), old.get("gate"), "EVIDENTIAL"),
        ("eth_leadership", cur.get("eth_leadership"), old.get("eth_leadership"), "CONTEXT_ONLY"),
        ("owner_lane_status", current.get("owner_lanes"), previous.get("owner_lanes"), "CONTEXT_ONLY"),
    ]
    for name, new, old_value, classification in comparisons:
        if new != old_value:
            deltas.append({"classification": classification, "field": name, "previous": old_value, "current": new})
    if not deltas:
        deltas.append({"classification": "CONTEXT_ONLY", "claim": "No material deterministic delta versus previous native watch packet."})
    return deltas


def render_markdown(report: dict[str, Any]) -> str:
    a = report["market_reconciliation"]
    gate = a["gate"]
    lead = a["eth_leadership"]
    owners = report["owner_lanes"]
    lines = [
        "# Framework Research Watch",
        "",
        f"- Generated UTC: `{report['generated_at_utc']}`",
        f"- Mode: `{report['run_mode']}`",
        f"- Authority: `RESEARCH_ONLY / ZERO_PORTFOLIO_AUTHORITY`",
        f"- Emit reason: `{report['emit_reason']}`",
        "",
        "## Settled / live reconciliation",
        f"- Settled cycle high: `{a.get('settled_cycle_high')}`",
        f"- In-progress high: `{a.get('in_progress_high')}`",
        "- QA rule: `LIVE_HIGH_NEVER_SETTLED_CYCLE_HIGH`",
        "",
        "## ETH/BTC registered floor watch",
        f"- Registered floor context: `{a['registered_ethbtc_floor']:.4f}`",
        f"- Trailing settled closes >= floor: `{gate['trailing_settled_closes_at_or_above_floor']}`",
        f"- Latest settled close: `{gate['latest_settled_close']}`",
        f"- Settled margin: `{gate['latest_settled_margin_pct']}%`",
        f"- Current in-progress low: `{gate['latest_in_progress_low']}` (not a settled failure)",
        "",
        "## ETH leadership",
        f"- ETH-led last 4 settled: `{lead['eth_led_last_4_settled']}`",
        f"- ETH-led last 6 settled: `{lead['eth_led_last_6_settled']}`",
        f"- Consecutive BTC-led settled: `{lead['consecutive_btc_led_settled']}`",
        "",
        "## Current owner reconciliation",
    ]
    for name, owner in owners.items():
        lines.append(f"- **{name}**: `{owner.get('status')}` — `{owner.get('path')}`")
    lines += [
        "",
        "## Early research-attention triggers",
        json.dumps(report["early_triggers"], sort_keys=True),
        "",
        "## Role migration",
        "Routine OTA surveillance is repository-native. Claude/Astra are optional challenger/falsifier/deep-research tools and are not required operators.",
        "",
    ]
    return "\n".join(lines)


def build_report(repo: Path, output_root: Path, now: datetime, mode: str) -> tuple[dict[str, Any], bool]:
    sessions = load_sessions(repo)
    analysis = settled_analysis(sessions)
    owners = owner_snapshot(repo, now)
    triggers = early_triggers(analysis, owners)
    emit = mode != "trigger-check" or bool(triggers)
    reason = "FIXED_OR_MANUAL_RESEARCH_WATCH" if mode != "trigger-check" else ("REGISTERED_EARLY_TRIGGER" if triggers else "NO_REGISTERED_EARLY_TRIGGER")
    report = {
        "contract": "FRAMEWORK_RESEARCH_WATCH_v1",
        "generated_at_utc": now.isoformat().replace("+00:00", "Z"),
        "run_mode": mode,
        "emit_reason": reason,
        "authority": AUTHORITY,
        "source_call_policy": "ZERO_EXTERNAL_SOURCE_CALLS_REUSE_MATERIALIZED_OWNERS",
        "external_ai_required": False,
        "market_reconciliation": analysis,
        "owner_lanes": owners,
        "early_triggers": triggers,
        "source_qa_rules": [
            "LIVE_HIGH_NEVER_SETTLED_CYCLE_HIGH",
            "IN_PROGRESS_LOW_NEVER_SETTLED_GATE_FAILURE",
            "CURRENT_OWNER_LATEST_BEATS_STALE_EXTERNAL_BRIDGE",
            "BRIDGE_IS_NOT_TRUE_DATA_GAP",
            "DIRECT_ETHBTC_PREFERRED_NO_RATIO_SYNTHESIS",
            "NO_CANONICAL_OR_PORTFOLIO_AUTHORITY",
        ],
        "role_migration": {
            "routine_ota_operator": "GITHUB_FRAMEWORK_RESEARCH_WATCH",
            "claude_astra": "OPTIONAL_CHALLENGER_FALSIFIER_DEEP_RESEARCH_ONLY",
        },
    }
    report["classified_deltas"] = classified_deltas(report, previous_report(repo, output_root))
    return report, emit


def persist(report: dict[str, Any], repo: Path, output_root: Path) -> tuple[Path, str]:
    now = parse_time(report["generated_at_utc"]) or utc_now()
    run_dir = output_root / "runs" / now.strftime("%Y/%m/%d")
    run_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{now.strftime('%H%M%S')}_{report['run_mode']}"
    json_path = run_dir / f"{stem}.json"
    md_path = run_dir / f"{stem}.md"
    body = json.dumps(report, indent=2, sort_keys=True) + "\n"
    json_path.write_text(body)
    md_path.write_text(render_markdown(report))
    digest = hashlib.sha256(body.encode()).hexdigest()
    pointer = {
        "contract": "FRAMEWORK_RESEARCH_WATCH_LATEST_POINTER_v1",
        "generated_at_utc": report["generated_at_utc"],
        "path": str(json_path.relative_to(repo)),
        "markdown_path": str(md_path.relative_to(repo)),
        "sha256": digest,
        "status": "PASS",
        "authority": AUTHORITY,
    }
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "LATEST.json").write_text(json.dumps(pointer, indent=2, sort_keys=True) + "\n")
    (output_root / "LATEST.md").write_text(render_markdown(report))
    return json_path, digest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-root", default="research/framework_research_watch")
    parser.add_argument("--mode", choices=("fixed", "manual", "trigger-check"), default="manual")
    parser.add_argument("--now-utc", default=None, help="Test-only deterministic timestamp")
    args = parser.parse_args()

    repo = Path(args.repo_root).resolve()
    output_root = (repo / args.output_root).resolve()
    now = parse_time(args.now_utc) if args.now_utc else utc_now()
    if now is None:
        raise SystemExit("invalid --now-utc")
    report, emit = build_report(repo, output_root, now, args.mode)
    if emit:
        path, digest = persist(report, repo, output_root)
        print(f"emit=true")
        print(f"report_path={path.relative_to(repo)}")
        print(f"report_sha256={digest}")
    else:
        print("emit=false")
        print("reason=NO_REGISTERED_EARLY_TRIGGER")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
