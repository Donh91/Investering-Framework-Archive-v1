from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import subprocess
from collections import Counter
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

UTC = timezone.utc
FAILURE_CONCLUSIONS = {"failure", "timed_out", "startup_failure", "action_required"}
EVIDENCE_PREFIXES = (
    "03_DAILY_CAPTURE_LOGS/",
    "research/api_agent/outputs/",
    "research/experiment_lifecycle/",
    "research/framework_memory/",
)


def parse_time(value: Any) -> datetime | None:
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, UTC)
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
    except ValueError:
        return None


def day_window(day: date, timezone_name: str) -> tuple[datetime, datetime]:
    zone = ZoneInfo(timezone_name)
    start_local = datetime.combine(day, time.min, tzinfo=zone)
    end_local = start_local + timedelta(days=1)
    return start_local.astimezone(UTC), end_local.astimezone(UTC)


def scalar_leaf_count(value: Any) -> int:
    if isinstance(value, dict):
        return sum(scalar_leaf_count(v) for v in value.values())
    if isinstance(value, list):
        return sum(scalar_leaf_count(v) for v in value)
    return 1


def flatten_runs(payload: Any) -> list[dict[str, Any]]:
    pages = payload if isinstance(payload, list) else [payload]
    out: list[dict[str, Any]] = []
    for page in pages:
        if not isinstance(page, dict):
            continue
        runs = page.get("workflow_runs")
        if isinstance(runs, list):
            out.extend(row for row in runs if isinstance(row, dict))
    return out


def is_failure(conclusion: Any) -> bool:
    return str(conclusion or "").lower() in FAILURE_CONCLUSIONS


def _git(root: Path, *args: str, text: bool = True) -> str | bytes:
    proc = subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=text
    )
    return proc.stdout


def _git_exists(root: Path, sha: str, path: str) -> bool:
    return subprocess.run(
        ["git", "cat-file", "-e", f"{sha}:{path}"],
        cwd=root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0


def _git_bytes(root: Path, sha: str, path: str) -> bytes:
    return _git(root, "show", f"{sha}:{path}", text=False)  # type: ignore[return-value]


def _commit_before(root: Path, stamp: datetime) -> str:
    value = str(
        _git(
            root,
            "rev-list",
            "-1",
            f"--before={stamp.isoformat()}",
            "HEAD",
        )
    ).strip()
    if not value:
        raise RuntimeError(f"NO_COMMIT_BEFORE_{stamp.isoformat()}")
    return value


def _touched_paths(root: Path, start_sha: str, end_sha: str) -> set[str]:
    raw = str(
        _git(
            root,
            "log",
            "--format=",
            "--name-only",
            f"{start_sha}..{end_sha}",
        )
    )
    return {line.strip() for line in raw.splitlines() if line.strip()}


def _is_pointer_or_meta(path: str) -> bool:
    name = Path(path).name
    if name in {"LATEST.json", "LATEST.md"} or name.startswith("LATEST_"):
        return True
    if name.endswith(".schema.json") or name.endswith(".md"):
        return True
    return False


def _is_evidence(path: str) -> bool:
    if not path.startswith(EVIDENCE_PREFIXES):
        return False
    if "machine_throughput" in path:
        return False
    return not _is_pointer_or_meta(path)


def _local_day(stamp: datetime | None, zone: ZoneInfo) -> date | None:
    return stamp.astimezone(zone).date() if stamp else None


def _capture_metrics(
    root: Path, end_sha: str, touched: set[str], target: date, zone: ZoneInfo
) -> dict[str, Any]:
    captures = owner_attempts = owner_success = owner_skip = owner_failure = 0
    artifact_bytes = raw_source_bytes = market_scalars = 0
    for path in sorted(touched):
        if not path.startswith("03_DAILY_CAPTURE_LOGS/captures/") or _is_pointer_or_meta(path):
            continue
        if not path.endswith(".json") or not _git_exists(root, end_sha, path):
            continue
        try:
            data = json.loads(_git_bytes(root, end_sha, path))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if data.get("contract") != "DAILY_LIVE_ANCHOR_INDEX_v3":
            continue
        if _local_day(parse_time(data.get("captured_at_utc")), zone) != target:
            continue
        captures += 1
        market_scalars += scalar_leaf_count(data.get("market_metrics") or {})
        owners = data.get("owners") or []
        if not isinstance(owners, list):
            continue
        for owner in owners:
            if not isinstance(owner, dict):
                continue
            owner_attempts += 1
            code = owner.get("collector_exit_code")
            if code == 0:
                owner_success += 1
            elif code == 78:
                owner_skip += 1
            else:
                owner_failure += 1
            for item in owner.get("files") or []:
                if not isinstance(item, dict):
                    continue
                try:
                    size = int(item.get("bytes") or 0)
                except (TypeError, ValueError):
                    size = 0
                artifact_bytes += max(size, 0)
                rel = str(item.get("path") or "")
                if "/raw/" in rel or rel.startswith("raw/") or "/source_payloads/" in rel:
                    raw_source_bytes += max(size, 0)
    return {
        "live_anchor_captures": captures,
        "owner_collection_attempts": owner_attempts,
        "owner_successes": owner_success,
        "owner_expected_skips": owner_skip,
        "owner_failures": owner_failure,
        "owner_declared_artifact_bytes": artifact_bytes,
        "owner_declared_raw_source_bytes": raw_source_bytes,
        "live_anchor_normalized_scalar_values": market_scalars,
    }


def _hourly_metrics(
    root: Path, end_sha: str, touched: set[str], target: date, zone: ZoneInfo
) -> dict[str, Any]:
    unique_hour_keys: set[str] = set()
    nonempty_cells = 0
    for path in (root / "03_DAILY_CAPTURE_LOGS/hourly").rglob("*.csv"):
        try:
            rows = csv.DictReader(io.StringIO(path.read_text(encoding="utf-8")))
            for row in rows:
                stamp = parse_time(row.get("timestamp_copenhagen") or row.get("timestamp_utc"))
                if _local_day(stamp, zone) != target:
                    continue
                key = str(row.get("timestamp_utc") or row.get("timestamp_copenhagen"))
                if key in unique_hour_keys:
                    continue
                unique_hour_keys.add(key)
                nonempty_cells += sum(1 for value in row.values() if value not in {None, ""})
        except (OSError, UnicodeDecodeError, csv.Error):
            continue

    source_calls = source_bytes = source_rows = run_count = 0
    for path in sorted(touched):
        if not path.startswith("03_DAILY_CAPTURE_LOGS/hourly/runs/") or not path.endswith(".json"):
            continue
        if not _git_exists(root, end_sha, path):
            continue
        try:
            data = json.loads(_git_bytes(root, end_sha, path))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not str(data.get("contract") or "").startswith("HOURLY_SEQUENCE_CAPTURE_"):
            continue
        if _local_day(parse_time(data.get("retrieved_at_utc")), zone) != target:
            continue
        run_count += 1
        records = data.get("source_records") or []
        if not isinstance(records, list):
            continue
        for record in records:
            if not isinstance(record, dict):
                continue
            source_calls += 1
            try:
                source_bytes += int(record.get("bytes") or 0)
                source_rows += int(record.get("row_count") or 0)
            except (TypeError, ValueError):
                pass
    return {
        "hourly_sequence_runs": run_count,
        "unique_hourly_observation_rows": len(unique_hour_keys),
        "hourly_nonempty_normalized_cells": nonempty_cells,
        "instrumented_physical_source_calls": source_calls,
        "instrumented_source_response_bytes": source_bytes,
        "instrumented_source_rows_returned": source_rows,
    }


def _durable_metrics(
    root: Path, start_sha: str, end_sha: str, touched: set[str]
) -> dict[str, Any]:
    created = modified = total_bytes = json_scalars = 0
    content_hashes: set[str] = set()
    included: list[str] = []
    for path in sorted(touched):
        if not _is_evidence(path) or not _git_exists(root, end_sha, path):
            continue
        body = _git_bytes(root, end_sha, path)
        included.append(path)
        total_bytes += len(body)
        content_hashes.add(hashlib.sha256(body).hexdigest())
        if _git_exists(root, start_sha, path):
            modified += 1
        else:
            created += 1
        if path.endswith(".json"):
            try:
                json_scalars += scalar_leaf_count(json.loads(body))
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
    return {
        "touched_evidence_paths": len(included),
        "created_evidence_paths": created,
        "modified_evidence_paths": modified,
        "unique_end_state_content_hashes": len(content_hashes),
        "durable_end_state_bytes": total_bytes,
        "normalized_json_scalar_values": json_scalars,
    }


def _receipt_time(data: dict[str, Any]) -> datetime | None:
    for key in (
        "completed_at_utc",
        "created_at_utc",
        "generated_at_utc",
        "timestamp_utc",
        "created_unix",
    ):
        stamp = parse_time(data.get(key))
        if stamp:
            return stamp
    return None


def _api_metrics(
    root: Path, end_sha: str, touched: set[str], target: date, zone: ZoneInfo
) -> dict[str, Any]:
    receipts = actual_calls = zero_cost_skips = input_tokens = output_tokens = 0
    director_receipts = director_calls = conflict_calls = 0
    cost = 0.0
    seen: set[str] = set()
    for path in sorted(touched):
        if not path.startswith("research/api_agent/outputs/") or not path.endswith(".json"):
            continue
        if "RECEIPT" not in Path(path).name.upper() and Path(path).name != "receipt.json":
            continue
        if not _git_exists(root, end_sha, path):
            continue
        try:
            data = json.loads(_git_bytes(root, end_sha, path))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if "API_AGENT_RECEIPT" not in str(data.get("contract") or ""):
            continue
        if _local_day(_receipt_time(data), zone) != target:
            continue
        identity = str(data.get("response_id") or data.get("request_hash") or data.get("output_hash") or path)
        if identity in seen:
            continue
        seen.add(identity)
        receipts += 1
        task = str(data.get("task") or data.get("task_id") or "")
        usage = data.get("usage") if isinstance(data.get("usage"), dict) else {}
        inp = int(usage.get("input_tokens", data.get("input_tokens", 0)) or 0)
        out = int(usage.get("output_tokens", data.get("output_tokens", 0)) or 0)
        input_tokens += inp
        output_tokens += out
        try:
            cost += float(data.get("cost_usd", data.get("estimated_cost_usd", 0)) or 0)
        except (TypeError, ValueError):
            pass
        actual = bool(data.get("response_id")) or inp > 0 or out > 0
        if actual:
            actual_calls += 1
        else:
            zero_cost_skips += 1
        if task == "DAILY_DIRECTOR_SHADOW":
            director_receipts += 1
            director_calls += int(actual)
        elif task == "DAILY_CONFLICT_REVIEW":
            conflict_calls += int(actual)
    return {
        "api_agent_receipts": receipts,
        "actual_model_calls": actual_calls,
        "zero_cost_skips": zero_cost_skips,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost_usd": round(cost, 6),
        "daily_director_receipts": director_receipts,
        "daily_director_model_calls": director_calls,
        "daily_conflict_review_model_calls": conflict_calls,
    }


def _learning_metrics(
    root: Path, start_sha: str, end_sha: str, touched: set[str]
) -> dict[str, int]:
    prefixes = {
        "experiment_candidates_created": "research/experiment_lifecycle/candidates/",
        "experiment_observations_created": "research/experiment_lifecycle/observations/",
        "experiment_dispatch_artifacts_created": "research/experiment_lifecycle/dispatch/",
        "forecast_memory_created": "research/framework_memory/forecast_memory/",
        "outcome_memory_created": "research/framework_memory/outcome_memory/",
    }
    counts = {key: 0 for key in prefixes}
    for path in touched:
        if not path.endswith(".json") or not _git_exists(root, end_sha, path) or _git_exists(root, start_sha, path):
            continue
        for key, prefix in prefixes.items():
            if path.startswith(prefix):
                counts[key] += 1
    return counts


def _workflow_metrics(runs_payload: Any, start: datetime, end: datetime) -> dict[str, Any]:
    selected = []
    for row in flatten_runs(runs_payload):
        stamp = parse_time(row.get("run_started_at") or row.get("created_at"))
        if stamp and start <= stamp < end:
            selected.append(row)
    events = Counter(str(row.get("event") or "UNKNOWN") for row in selected)
    conclusions = Counter(str(row.get("conclusion") or row.get("status") or "UNKNOWN") for row in selected)
    scheduled = [row for row in selected if row.get("event") == "schedule"]
    failures = [row for row in selected if is_failure(row.get("conclusion"))]
    scheduled_failures = [row for row in scheduled if is_failure(row.get("conclusion"))]
    return {
        "runs_started": len(selected),
        "scheduled_runs": len(scheduled),
        "by_event": dict(sorted(events.items())),
        "by_conclusion": dict(sorted(conclusions.items())),
        "failed_runs": len(failures),
        "scheduled_failed_runs": len(scheduled_failures),
        "cancelled_runs": sum(1 for row in selected if row.get("conclusion") == "cancelled"),
        "scheduled_success_rate_pct": round(100.0 * (len(scheduled) - len(scheduled_failures)) / len(scheduled), 3) if scheduled else None,
    }


def _ratio(numerator: float, denominator: float, scale: float) -> float | None:
    if denominator <= 0:
        return None
    return round(numerator / denominator * scale, 6)


def build_receipt(
    repo_root: Path,
    target: date,
    timezone_name: str,
    runs_payload: Any,
) -> dict[str, Any]:
    zone = ZoneInfo(timezone_name)
    start, end = day_window(target, timezone_name)
    start_sha = _commit_before(repo_root, start)
    end_sha = _commit_before(repo_root, end)
    touched = _touched_paths(repo_root, start_sha, end_sha)

    workflow = _workflow_metrics(runs_payload, start, end)
    capture = _capture_metrics(repo_root, end_sha, touched, target, zone)
    hourly = _hourly_metrics(repo_root, end_sha, touched, target, zone)
    durable = _durable_metrics(repo_root, start_sha, end_sha, touched)
    api = _api_metrics(repo_root, end_sha, touched, target, zone)
    learning = _learning_metrics(repo_root, start_sha, end_sha, touched)

    core_observation_units = capture["live_anchor_captures"] + hourly["unique_hourly_observation_rows"]
    normalized_values = (
        durable["normalized_json_scalar_values"] + hourly["hourly_nonempty_normalized_cells"]
    )
    unmetered_owner_attempts = capture["owner_collection_attempts"]

    receipt: dict[str, Any] = {
        "contract": "DAILY_MACHINE_THROUGHPUT_RECEIPT_v1",
        "authority": "OPERATIONAL_OBSERVABILITY_ONLY",
        "status": "PASS",
        "generated_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "window": {
            "local_date": target.isoformat(),
            "timezone": timezone_name,
            "start_utc": start.isoformat().replace("+00:00", "Z"),
            "end_utc": end.isoformat().replace("+00:00", "Z"),
            "closed_window": True,
            "start_commit_sha": start_sha,
            "end_commit_sha": end_sha,
        },
        "workflow_activity": workflow,
        "market_observation_throughput": {
            **capture,
            **hourly,
            "core_observation_units": core_observation_units,
        },
        "durable_repository_throughput": {
            **durable,
            "normalized_values_total_structural": normalized_values,
        },
        "ai_analysis": api,
        "learning_activity": learning,
        "failures": {
            "workflow_failed_runs": workflow["failed_runs"],
            "scheduled_workflow_failed_runs": workflow["scheduled_failed_runs"],
            "owner_failures": capture["owner_failures"],
        },
        "efficiency": {
            "actual_model_calls_per_100_core_observation_units": _ratio(api["actual_model_calls"], core_observation_units, 100.0),
            "new_experiment_candidates_per_100_core_observation_units": _ratio(learning["experiment_candidates_created"], core_observation_units, 100.0),
            "api_cost_usd_per_100_core_observation_units": _ratio(api["estimated_cost_usd"], core_observation_units, 100.0),
            "new_experiment_candidates_per_1000_normalized_values": _ratio(learning["experiment_candidates_created"], normalized_values, 1000.0),
        },
        "instrumentation": {
            "exact_metrics": [
                "workflow run counts within the closed window",
                "unique hourly rows persisted for the local day",
                "live-anchor capture count",
                "owner invocation outcomes exposed by immutable capture indexes",
                "durable repository bytes and scalar JSON leaves at window close",
                "API-agent receipts, model calls, token usage and recorded cost",
                "new experiment/forecast/outcome files created in the window",
            ],
            "physical_external_source_calls": {
                "status": "PARTIAL_INSTRUMENTATION",
                "instrumented_count": hourly["instrumented_physical_source_calls"],
                "instrumented_scope": "HOURLY_SEQUENCE source_records with one recorded URL/response per record",
                "unmetered_owner_collection_attempts": unmetered_owner_attempts,
                "exact_total_physical_http_calls": None,
                "reason": "Existing point-in-time and specialist owners do not all expose one physical-request counter per network request. No inferred total is permitted.",
            },
            "semantic_warning": "Counts measure machine throughput and observability only. They do not measure forecast skill, information value or portfolio edge by themselves.",
        },
        "market_rule_change": False,
        "portfolio_action": False,
        "model_weight_change": False,
    }
    canonical = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()
    receipt["receipt_sha256"] = hashlib.sha256(canonical).hexdigest()
    return receipt


def render_markdown(receipt: dict[str, Any]) -> str:
    w = receipt["workflow_activity"]
    m = receipt["market_observation_throughput"]
    a = receipt["ai_analysis"]
    l = receipt["learning_activity"]
    d = receipt["durable_repository_throughput"]
    i = receipt["instrumentation"]["physical_external_source_calls"]
    lines = [
        "# Daily Machine Throughput",
        "",
        f"Date: **{receipt['window']['local_date']}** ({receipt['window']['timezone']})",
        f"Status: **{receipt['status']}**",
        "",
        "## Throughput",
        "",
        f"- Workflow runs started: **{w['runs_started']}** ({w['scheduled_runs']} scheduled)",
        f"- Scheduled workflow failures: **{w['scheduled_failed_runs']}**",
        f"- Live-anchor captures: **{m['live_anchor_captures']}**",
        f"- Unique hourly observation rows: **{m['unique_hourly_observation_rows']}**",
        f"- Core observation units: **{m['core_observation_units']}**",
        f"- Owner collection attempts: **{m['owner_collection_attempts']}**",
        f"- Instrumented physical source calls: **{m['instrumented_physical_source_calls']}**",
        f"- Instrumented source response bytes: **{m['instrumented_source_response_bytes']}**",
        f"- Durable evidence bytes at window close: **{d['durable_end_state_bytes']}**",
        f"- Structural normalized values: **{d['normalized_values_total_structural']}**",
        "",
        "## AI and learning",
        "",
        f"- API-agent receipts: **{a['api_agent_receipts']}**",
        f"- Actual model calls: **{a['actual_model_calls']}**",
        f"- Daily Director model calls: **{a['daily_director_model_calls']}**",
        f"- Input/output tokens: **{a['input_tokens']} / {a['output_tokens']}**",
        f"- Recorded API cost: **${a['estimated_cost_usd']:.6f}**",
        f"- New experiment candidates: **{l['experiment_candidates_created']}**",
        f"- New experiment observations: **{l['experiment_observations_created']}**",
        f"- New forecast-memory artifacts: **{l['forecast_memory_created']}**",
        "",
        "## Instrumentation boundary",
        "",
        f"Physical HTTP-call total: **{i['status']}**. The hourly lane contributes {i['instrumented_count']} exact recorded calls; {i['unmetered_owner_collection_attempts']} owner invocations remain outside physical-request counting. No total is inferred.",
        "",
        f"Receipt SHA-256: `{receipt['receipt_sha256']}`",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--runs-json", required=True)
    parser.add_argument("--date")
    parser.add_argument("--timezone", default="Europe/Copenhagen")
    parser.add_argument("--output-root", default="03_WEEKLY_OPERATIONS/automation_receipts/machine_throughput")
    parser.add_argument("--latest-json", default="LATEST_MACHINE_THROUGHPUT.json")
    args = parser.parse_args()

    zone = ZoneInfo(args.timezone)
    target = date.fromisoformat(args.date) if args.date else (datetime.now(zone).date() - timedelta(days=1))
    repo_root = Path(args.repo_root).resolve()
    runs_payload = json.loads(Path(args.runs_json).read_text(encoding="utf-8"))
    receipt = build_receipt(repo_root, target, args.timezone, runs_payload)

    output_root = repo_root / args.output_root
    dated = output_root / target.strftime("%Y/%m") / f"{target.isoformat()}.json"
    dated_md = dated.with_suffix(".md")
    latest = output_root / "LATEST.json"
    latest_md = output_root / "LATEST.md"
    for path in (dated, dated_md, latest, latest_md, repo_root / args.latest_json):
        path.parent.mkdir(parents=True, exist_ok=True)

    payload = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    markdown = render_markdown(receipt)
    dated.write_text(payload, encoding="utf-8")
    dated_md.write_text(markdown, encoding="utf-8")
    latest.write_text(payload, encoding="utf-8")
    latest_md.write_text(markdown, encoding="utf-8")
    (repo_root / args.latest_json).write_text(payload, encoding="utf-8")
    print(json.dumps({"status": receipt["status"], "date": target.isoformat(), "receipt_sha256": receipt["receipt_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
