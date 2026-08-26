from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


RECEIPT_CONTRACT = "THREE_HORIZON_ACTION_COMPASS_RECEIPT_v1_1"
CANDIDATE_CONTRACT = "THREE_HORIZON_ACTION_COMPASS_RECEIPT_CANDIDATE_v1_1"
COMPASS_CONTRACT = "THREE_HORIZON_ACTION_COMPASS_v1_1"
OUTCOME_CONTRACT = "ACTION_COMPASS_OUTCOME_SIDECAR_v1_1"
ACTIVATION_CONTRACT = "ACTION_COMPASS_ACCOUNTABILITY_ACTIVATION_v1"
OWNER_PATH = "02_DATA_PING/protocols/2026-08-25__three-horizon-action-compass-output-contract-v1__canonical.md"
ACTIVATION_MARKER = "02_DATA_PING/runtime/ACTION_COMPASS_ACCOUNTABILITY_ACTIVATION_v1.json"
CANONICAL_REPOSITORY = "Donh91/Investering-Framework-Archive-v1"

ACTIONS = {"BUY", "TOP_UP", "SCALE_IN", "PREPARE_BUY", "WAIT", "HOLD", "REDUCE", "EXIT", "NO_ACTION"}
STATES = {
    "DEFENSIVE",
    "CONSOLIDATION",
    "PRE_ROTATION",
    "ROTATION",
    "BROAD_ALTSEASON",
    "PARABOLIC_ALTSEASON",
    "DISTRIBUTION",
    "EXIT_RISK",
    "UNCLEAR",
}
WARNINGS = {
    "NONE",
    "PARABOLIC_ALTSEASON_WARNING",
    "DISTRIBUTION_WARNING",
    "EXIT_WARNING",
    "STRUCTURAL_BREAKDOWN_WARNING",
}
DATA_QUALITY_TAGS = {
    "COMPLETE",
    "PARTIAL",
    "DATA_MISSING",
    "CONFLICTING_EVIDENCE",
    "STALE_INPUT",
    "SOURCE_DEGRADED",
    "UNKNOWN_QUALITY",
}
BASELINE_UNAVAILABLE_REASONS = {
    "NO_PUBLIC_PRE_OUTCOME_OBSERVER",
    "BASELINE_DATA_MISSING",
    "PRIVATE_DATA_AUTHORITY_UNAVAILABLE",
}
SERIES_PATHS = {
    "BTC_USDT_MARK_PRICE": "market_metrics.derivatives.BTC-USDT-SWAP.mark_price.mark_price",
    "ETH_USDT_MARK_PRICE": "market_metrics.derivatives.ETH-USDT-SWAP.mark_price.mark_price",
}
HORIZONS = {
    "24H": timedelta(hours=24),
    "7D": timedelta(days=7),
    "30D": timedelta(days=30),
    "90D": timedelta(days=90),
    "180D": timedelta(days=180),
}
FORBIDDEN_PRIVATE_KEY_PARTS = {
    "account",
    "api_key",
    "chat",
    "conversation",
    "credential",
    "holding",
    "portfolio_size",
    "position_size",
    "private_key",
    "quantity",
    "secret",
    "token",
}
FORBIDDEN_RATIONALE_TAG_PARTS = {
    "ACCOUNT",
    "CREDENTIAL",
    "HOLDING",
    "PORTFOLIO_SIZE",
    "POSITION_SIZE",
    "PRIVATE_KEY",
    "QUANTITY",
    "SECRET",
}
TAG_RE = re.compile(r"^[A-Z][A-Z0-9_]{1,63}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"object_required:{path}")
    return value


def parse_time(value: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("utc_timestamp_must_end_Z")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timezone_required")
    return parsed.astimezone(timezone.utc)


def parse_date(value: Any, label: str):
    if not isinstance(value, str) or not DATE_RE.fullmatch(value):
        raise ValueError(f"{label}_invalid")
    return datetime.strptime(value, "%Y-%m-%d").date()


def iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def exact_keys(value: dict[str, Any], required: set[str], label: str) -> None:
    missing = sorted(required - set(value))
    extra = sorted(set(value) - required)
    if missing:
        raise ValueError(f"{label}_missing:{','.join(missing)}")
    if extra:
        raise ValueError(f"{label}_extra:{','.join(extra)}")


def safe_text(value: Any, label: str, minimum: int = 1, maximum: int = 200) -> str:
    if not isinstance(value, str) or not minimum <= len(value) <= maximum:
        raise ValueError(f"{label}_invalid")
    if "\n" in value or "\r" in value:
        raise ValueError(f"{label}_multiline_forbidden")
    return value


def reject_private_shape(value: Any, path: str = "root") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            lowered = str(key).lower()
            if any(part in lowered for part in FORBIDDEN_PRIVATE_KEY_PARTS):
                raise ValueError(f"private_field_forbidden:{path}.{key}")
            reject_private_shape(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            reject_private_shape(item, f"{path}[{index}]")
    elif isinstance(value, str) and len(value) > 500:
        raise ValueError(f"unbounded_text_forbidden:{path}")


def validate_relative_path(value: Any, label: str, allowed_prefix: str | None = None) -> str:
    text = safe_text(value, label, 1, 300)
    path = Path(text)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"{label}_unsafe")
    if allowed_prefix and not text.startswith(allowed_prefix.rstrip("/") + "/"):
        raise ValueError(f"{label}_outside_allowed_root")
    return text


def validate_tags(values: Any, label: str, allowed: set[str] | None, maximum: int) -> list[str]:
    if not isinstance(values, list) or not 1 <= len(values) <= maximum:
        raise ValueError(f"{label}_invalid_count")
    if len(set(values)) != len(values):
        raise ValueError(f"{label}_duplicates")
    for value in values:
        if not isinstance(value, str) or not TAG_RE.fullmatch(value):
            raise ValueError(f"{label}_invalid_tag")
        if label == "rationale_tags" and any(part in value for part in FORBIDDEN_RATIONALE_TAG_PARTS):
            raise ValueError("rationale_tag_private_semantics_forbidden")
        if allowed is not None and value not in allowed:
            raise ValueError(f"{label}_unknown_tag:{value}")
    return values


def validate_action_compass(value: Any, interpreted: datetime) -> None:
    if not isinstance(value, dict):
        raise ValueError("action_compass_object_required")
    exact_keys(value, {"contract", "as_of_utc", "near_term", "next_window", "altcoin_compass"}, "action_compass")
    if value["contract"] != COMPASS_CONTRACT:
        raise ValueError("wrong_action_compass_contract")
    as_of = parse_time(value["as_of_utc"])
    if as_of > interpreted:
        raise ValueError("action_compass_as_of_after_interpretation")

    near = value["near_term"]
    if not isinstance(near, dict):
        raise ValueError("near_term_object_required")
    exact_keys(near, {"horizon_hours", "valid_from_utc", "valid_until_utc", "action"}, "near_term")
    if not isinstance(near["horizon_hours"], int) or not 1 <= near["horizon_hours"] <= 72:
        raise ValueError("near_term_horizon_invalid")
    valid_from = parse_time(near["valid_from_utc"])
    valid_until = parse_time(near["valid_until_utc"])
    if valid_from < as_of or valid_from > interpreted or valid_until <= valid_from:
        raise ValueError("near_term_validity_invalid")
    if near["action"] not in ACTIONS:
        raise ValueError("near_term_action_invalid")

    window = value["next_window"]
    if not isinstance(window, dict):
        raise ValueError("next_window_object_required")
    exact_keys(window, {"window_start_date", "window_end_date", "action"}, "next_window")
    start_date = parse_date(window["window_start_date"], "next_window_start_date")
    end_date = parse_date(window["window_end_date"], "next_window_end_date")
    if start_date > end_date or start_date < interpreted.date():
        raise ValueError("next_window_dates_invalid")
    if window["action"] not in ACTIONS:
        raise ValueError("next_window_action_invalid")

    alt = value["altcoin_compass"]
    if not isinstance(alt, dict):
        raise ValueError("altcoin_compass_object_required")
    exact_keys(alt, {"horizon_days", "through_date", "state", "action", "warning"}, "altcoin_compass")
    if not isinstance(alt["horizon_days"], int) or not 1 <= alt["horizon_days"] <= 365:
        raise ValueError("altcoin_horizon_invalid")
    if parse_date(alt["through_date"], "altcoin_through_date") < interpreted.date():
        raise ValueError("altcoin_through_date_invalid")
    if alt["state"] not in STATES or alt["action"] not in ACTIONS or alt["warning"] not in WARNINGS:
        raise ValueError("altcoin_compass_value_invalid")


def validate_baseline(value: Any, interpreted: datetime) -> None:
    if not isinstance(value, dict) or value.get("status") not in {"BOUND", "UNAVAILABLE"}:
        raise ValueError("baseline_observer_invalid")
    if value["status"] == "UNAVAILABLE":
        exact_keys(value, {"status", "reason"}, "baseline_unavailable")
        if value["reason"] not in BASELINE_UNAVAILABLE_REASONS:
            raise ValueError("baseline_unavailable_reason_invalid")
        return
    exact_keys(value, {"status", "evidence_path", "evidence_sha256", "captured_at_utc", "series"}, "baseline_bound")
    validate_relative_path(value["evidence_path"], "baseline_evidence_path", "03_DAILY_CAPTURE_LOGS/captures")
    if not isinstance(value["evidence_sha256"], str) or not SHA256_RE.fullmatch(value["evidence_sha256"]):
        raise ValueError("baseline_evidence_sha256_invalid")
    if parse_time(value["captured_at_utc"]) > interpreted:
        raise ValueError("baseline_after_interpretation")
    if not isinstance(value["series"], list) or len(value["series"]) != len(SERIES_PATHS):
        raise ValueError("baseline_series_count_invalid")
    seen: set[str] = set()
    for item in value["series"]:
        if not isinstance(item, dict):
            raise ValueError("baseline_series_object_required")
        exact_keys(item, {"series_id", "metric_path"}, "baseline_series")
        series_id = item["series_id"]
        if series_id in seen or SERIES_PATHS.get(series_id) != item["metric_path"]:
            raise ValueError("baseline_series_binding_invalid")
        seen.add(series_id)
    if seen != set(SERIES_PATHS):
        raise ValueError("baseline_series_missing")


def candidate_fields() -> set[str]:
    return {
        "contract",
        "input_packet_sha256",
        "input_binding_status",
        "input_contract",
        "source_reference",
        "source_timestamp_utc",
        "canonical_repository",
        "canonical_commit_sha",
        "owner_contract",
        "interpreted_at_utc",
        "producer_model",
        "action_compass",
        "data_quality_tags",
        "rationale_tags",
        "baseline_observer",
        "portfolio_execution",
    }


def validate_candidate(value: dict[str, Any]) -> tuple[datetime, datetime]:
    reject_private_shape(value)
    exact_keys(value, candidate_fields(), "candidate")
    if value["contract"] != CANDIDATE_CONTRACT:
        raise ValueError("wrong_candidate_contract")
    if not isinstance(value["input_packet_sha256"], str) or not SHA256_RE.fullmatch(value["input_packet_sha256"]):
        raise ValueError("input_packet_sha256_invalid")
    if value["input_binding_status"] not in {"VERIFIED_REPO_FILE", "OPAQUE_SOURCE_HASH_ASSERTED"}:
        raise ValueError("input_binding_status_invalid")
    safe_text(value["input_contract"], "input_contract", 1, 120)
    source_reference = safe_text(value["source_reference"], "source_reference", 1, 300)
    if source_reference.startswith("OPAQUE:"):
        if not re.fullmatch(r"OPAQUE:[A-Za-z0-9._:-]{1,200}", source_reference):
            raise ValueError("opaque_source_reference_invalid")
        if value["input_binding_status"] != "OPAQUE_SOURCE_HASH_ASSERTED":
            raise ValueError("opaque_source_binding_status_invalid")
    else:
        validate_relative_path(source_reference, "source_reference")
        if value["input_binding_status"] != "VERIFIED_REPO_FILE":
            raise ValueError("repo_source_binding_status_invalid")
    if value["canonical_repository"] != CANONICAL_REPOSITORY:
        raise ValueError("canonical_repository_invalid")
    if not isinstance(value["canonical_commit_sha"], str) or not COMMIT_RE.fullmatch(value["canonical_commit_sha"]):
        raise ValueError("canonical_commit_sha_invalid")
    if value["owner_contract"] != OWNER_PATH:
        raise ValueError("owner_contract_invalid")
    safe_text(value["producer_model"], "producer_model", 1, 100)
    if value["portfolio_execution"] is not False:
        raise ValueError("portfolio_execution_must_be_false")
    source_time = parse_time(value["source_timestamp_utc"])
    interpreted = parse_time(value["interpreted_at_utc"])
    if source_time > interpreted:
        raise ValueError("source_after_interpretation")
    validate_action_compass(value["action_compass"], interpreted)
    validate_tags(value["data_quality_tags"], "data_quality_tags", DATA_QUALITY_TAGS, 8)
    validate_tags(value["rationale_tags"], "rationale_tags", None, 12)
    validate_baseline(value["baseline_observer"], interpreted)
    return source_time, interpreted


def git_output(repo_root: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=repo_root, text=True, capture_output=True)
    if result.returncode:
        raise ValueError(f"git_error:{' '.join(args)}:{result.stderr.strip()[:200]}")
    return result.stdout.strip()


def git_file_bytes(repo_root: Path, commit_sha: str, path: str) -> bytes:
    result = subprocess.run(["git", "show", f"{commit_sha}:{path}"], cwd=repo_root, capture_output=True)
    if result.returncode:
        raise ValueError(f"git_bound_file_unavailable:{path}")
    return result.stdout


def packet_bytes_hash(raw: bytes, path: str) -> str:
    if path.lower().endswith(".json"):
        try:
            return digest(json.loads(raw.decode("utf-8")))
        except (UnicodeDecodeError, json.JSONDecodeError):
            pass
    return hashlib.sha256(raw).hexdigest()


def activation_binding(repo_root: Path, activation_utc: str | None, activation_commit_sha: str | None) -> tuple[str, datetime]:
    if activation_utc or activation_commit_sha:
        if not activation_utc or not activation_commit_sha or not COMMIT_RE.fullmatch(activation_commit_sha):
            raise ValueError("activation_override_incomplete")
        return activation_commit_sha, parse_time(activation_utc)
    line = git_output(repo_root, "log", "-1", "--format=%H|%cI", "--", ACTIVATION_MARKER)
    if "|" not in line:
        raise ValueError("activation_marker_not_committed")
    commit_sha, committed_at = line.split("|", 1)
    return commit_sha, datetime.fromisoformat(committed_at).astimezone(timezone.utc)


def verify_commit_binding(repo_root: Path, activation_sha: str, canonical_sha: str, expected_sha: str | None) -> None:
    if expected_sha and canonical_sha != expected_sha:
        raise ValueError("canonical_commit_does_not_match_expected")
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", activation_sha, canonical_sha],
        cwd=repo_root,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise ValueError("canonical_commit_predates_activation_or_is_unavailable")


def nested_number(value: dict[str, Any], path: str) -> float:
    current: Any = value
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            raise ValueError(f"metric_unavailable:{path}")
        current = current[part]
    if isinstance(current, bool) or not isinstance(current, (int, float)):
        raise ValueError(f"metric_non_numeric:{path}")
    number = float(current)
    if not math.isfinite(number):
        raise ValueError(f"metric_non_finite:{path}")
    return number


def verify_source_binding(candidate: dict[str, Any], repo_root: Path) -> None:
    if candidate["input_binding_status"] == "OPAQUE_SOURCE_HASH_ASSERTED":
        return
    source_path = candidate["source_reference"]
    raw = git_file_bytes(repo_root, candidate["canonical_commit_sha"], source_path)
    if packet_bytes_hash(raw, source_path) != candidate["input_packet_sha256"]:
        raise ValueError("input_packet_hash_mismatch")


def bound_baseline_value(candidate: dict[str, Any], repo_root: Path) -> dict[str, Any] | None:
    baseline = candidate["baseline_observer"]
    if baseline["status"] == "UNAVAILABLE":
        return None
    path_text = baseline["evidence_path"]
    path = (repo_root / path_text).resolve()
    if repo_root.resolve() not in path.parents:
        raise ValueError("baseline_evidence_path_unsafe")
    raw = git_file_bytes(repo_root, candidate["canonical_commit_sha"], path_text)
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("baseline_evidence_not_json") from exc
    if not isinstance(value, dict):
        raise ValueError("baseline_evidence_object_required")
    if digest(value) != baseline["evidence_sha256"]:
        raise ValueError("baseline_evidence_hash_mismatch")
    timestamp = value.get("captured_at_utc")
    if timestamp != baseline["captured_at_utc"]:
        raise ValueError("baseline_timestamp_mismatch")
    for series in baseline["series"]:
        if nested_number(value, series["metric_path"]) <= 0:
            raise ValueError("baseline_metric_must_be_positive")
    return value


def verify_baseline_binding(candidate: dict[str, Any], repo_root: Path) -> None:
    bound_baseline_value(candidate, repo_root)


def derived_ids(input_packet_sha256: str) -> tuple[str, str]:
    receipt_hash = hashlib.sha256((RECEIPT_CONTRACT + "\n" + input_packet_sha256).encode()).hexdigest()
    dedup_hash = hashlib.sha256(("ACTION_COMPASS_FRESH_INPUT_v1_1\n" + input_packet_sha256).encode()).hexdigest()
    return "ACR-" + receipt_hash[:24], "ACD-" + dedup_hash[:24]


def write_immutable(path: Path, value: dict[str, Any]) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as handle:
            handle.write(canonical_bytes(value))
        return True
    except FileExistsError:
        return False


def build_receipt(candidate: dict[str, Any], activation_sha: str, activation_time: datetime) -> dict[str, Any]:
    receipt_id, dedup_id = derived_ids(candidate["input_packet_sha256"])
    receipt = dict(candidate)
    receipt["contract"] = RECEIPT_CONTRACT
    receipt["receipt_id"] = receipt_id
    receipt["dedup_id"] = dedup_id
    receipt["implementation_activation"] = {
        "contract": ACTIVATION_CONTRACT,
        "marker_path": ACTIVATION_MARKER,
        "activation_commit_sha": activation_sha,
        "activation_utc": iso(activation_time),
    }
    receipt["persistence_status"] = "PERSISTED"
    receipt["authority"] = {
        "market_rule_change": False,
        "new_test": False,
        "portfolio_execution": False,
        "automatic_action": False,
        "automatic_promotion": False,
    }
    return receipt


def validate_receipt(value: dict[str, Any]) -> dict[str, Any]:
    receipt_only = {"receipt_id", "dedup_id", "implementation_activation", "persistence_status", "authority"}
    exact_keys(value, candidate_fields() | receipt_only, "receipt")
    if value["contract"] != RECEIPT_CONTRACT:
        raise ValueError("wrong_receipt_contract")
    candidate = {key: value[key] for key in candidate_fields()}
    candidate["contract"] = CANDIDATE_CONTRACT
    validate_candidate(candidate)
    receipt_id, dedup_id = derived_ids(value["input_packet_sha256"])
    if value["receipt_id"] != receipt_id or value["dedup_id"] != dedup_id:
        raise ValueError("derived_identity_mismatch")
    activation = value["implementation_activation"]
    if not isinstance(activation, dict):
        raise ValueError("implementation_activation_object_required")
    exact_keys(activation, {"contract", "marker_path", "activation_commit_sha", "activation_utc"}, "implementation_activation")
    if activation["contract"] != ACTIVATION_CONTRACT or activation["marker_path"] != ACTIVATION_MARKER:
        raise ValueError("implementation_activation_invalid")
    if not COMMIT_RE.fullmatch(activation["activation_commit_sha"]):
        raise ValueError("activation_commit_sha_invalid")
    parse_time(activation["activation_utc"])
    if value["persistence_status"] != "PERSISTED" or value["portfolio_execution"] is not False:
        raise ValueError("receipt_persistence_or_execution_invalid")
    expected_authority = {
        "market_rule_change": False,
        "new_test": False,
        "portfolio_execution": False,
        "automatic_action": False,
        "automatic_promotion": False,
    }
    if value["authority"] != expected_authority:
        raise ValueError("receipt_authority_invalid")
    return candidate


def persist(args: argparse.Namespace) -> None:
    candidate = read_json(args.candidate)
    source_time, interpreted = validate_candidate(candidate)
    activation_sha, activation_time = activation_binding(args.repo_root, args.activation_utc, args.activation_commit_sha)
    if source_time < activation_time or interpreted < activation_time:
        raise ValueError("historical_backfill_forbidden")
    verify_commit_binding(args.repo_root, activation_sha, candidate["canonical_commit_sha"], args.expected_canonical_commit)
    verify_source_binding(candidate, args.repo_root)
    verify_baseline_binding(candidate, args.repo_root)
    receipt = build_receipt(candidate, activation_sha, activation_time)
    existing = list(args.receipt_root.rglob(f"{receipt['receipt_id']}.json")) if args.receipt_root.exists() else []
    if len(existing) > 1:
        raise ValueError("duplicate_receipt_paths_detected")
    if existing:
        print(json.dumps({"status": "DUPLICATE_NOOP", "receipt_id": receipt["receipt_id"], "path": str(existing[0])}, sort_keys=True))
        return
    destination = args.receipt_root / interpreted.strftime("%Y/%m/%d") / f"{receipt['receipt_id']}.json"
    if write_immutable(destination, receipt):
        status = "PERSISTED"
    else:
        status = "DUPLICATE_NOOP"
    print(json.dumps({"status": status, "receipt_id": receipt["receipt_id"], "path": str(destination)}, sort_keys=True))


def validate_repository(args: argparse.Namespace) -> None:
    seen_receipts: set[str] = set()
    seen_dedup: set[str] = set()
    count = 0
    for path in sorted(args.receipt_root.rglob("*.json")) if args.receipt_root.exists() else []:
        receipt = read_json(path)
        candidate = validate_receipt(receipt)
        if receipt["receipt_id"] in seen_receipts or receipt["dedup_id"] in seen_dedup:
            raise ValueError("repository_duplicate_identity")
        seen_receipts.add(receipt["receipt_id"])
        seen_dedup.add(receipt["dedup_id"])
        expected_suffix = Path(parse_time(receipt["interpreted_at_utc"]).strftime("%Y/%m/%d")) / path.name
        if not str(path).endswith(str(expected_suffix)) or path.name != f"{receipt['receipt_id']}.json":
            raise ValueError("receipt_path_mismatch")
        activation = receipt["implementation_activation"]
        source_time = parse_time(receipt["source_timestamp_utc"])
        interpreted = parse_time(receipt["interpreted_at_utc"])
        activation_time = parse_time(activation["activation_utc"])
        if source_time < activation_time or interpreted < activation_time:
            raise ValueError("historical_backfill_forbidden")
        verify_commit_binding(args.repo_root, activation["activation_commit_sha"], candidate["canonical_commit_sha"], None)
        verify_source_binding(candidate, args.repo_root)
        verify_baseline_binding(candidate, args.repo_root)
        count += 1
    print(json.dumps({"status": "PASS", "receipt_count": count, "duplicate_count": 0}, sort_keys=True))


def evidence_rows(evidence_root: Path) -> list[tuple[datetime, Path, dict[str, Any], str]]:
    rows: list[tuple[datetime, Path, dict[str, Any], str]] = []
    if not evidence_root.exists():
        return rows
    for path in evidence_root.rglob("*.json"):
        if path.name == "LATEST.json":
            continue
        try:
            value = read_json(path)
            timestamp = value.get("captured_at_utc")
            if value.get("contract") != "DAILY_LIVE_ANCHOR_INDEX_v3" or not timestamp:
                continue
            rows.append((parse_time(timestamp), path, value, digest(value)))
        except Exception:
            continue
    rows.sort(key=lambda row: (row[0], str(row[1])))
    return rows


def evidence_ref(row: tuple[datetime, Path, dict[str, Any], str], repo_root: Path, value: float) -> dict[str, Any]:
    timestamp, path, _, sha256 = row
    try:
        relative = path.resolve().relative_to(repo_root.resolve())
        path_text = str(relative)
    except ValueError:
        path_text = str(path)
    return {"path": path_text, "sha256": sha256, "captured_at_utc": iso(timestamp), "value": value}


def mature_series(
    series_id: str,
    metric_path: str,
    start_value: float,
    interpreted: datetime,
    due: datetime,
    max_terminal: datetime,
    rows: list[tuple[datetime, Path, dict[str, Any], str]],
    baseline_row: tuple[datetime, Path, dict[str, Any], str],
    repo_root: Path,
) -> dict[str, Any] | None:
    eligible = [row for row in rows if interpreted < row[0] <= max_terminal]
    terminal_candidates: list[tuple[tuple[datetime, Path, dict[str, Any], str], float]] = []
    usable: list[tuple[tuple[datetime, Path, dict[str, Any], str], float]] = []
    for row in eligible:
        try:
            value = nested_number(row[2], metric_path)
        except ValueError:
            continue
        if value <= 0:
            continue
        usable.append((row, value))
        if row[0] >= due:
            terminal_candidates.append((row, value))
    if not terminal_candidates:
        return None
    terminal_row, terminal_value = terminal_candidates[0]
    path_points = [(baseline_row, start_value)] + [(row, value) for row, value in usable if row[0] <= terminal_row[0]]
    returns = [((value / start_value) - 1.0) * 100.0 for _, value in path_points]
    trough_index = min(range(len(path_points)), key=lambda index: returns[index])
    peak_index = max(range(len(path_points)), key=lambda index: returns[index])
    trough_row, trough_value = path_points[trough_index]
    peak_row, peak_value = path_points[peak_index]
    drawdown = min(0.0, returns[trough_index])
    upside = max(0.0, returns[peak_index])
    recovery_index: int | None = None
    if drawdown == 0.0:
        recovery_index = 0
    else:
        for index in range(trough_index + 1, len(path_points)):
            if path_points[index][1] >= start_value:
                recovery_index = index
                break
    terminal_return = ((terminal_value / start_value) - 1.0) * 100.0
    evidence_manifest = []
    for row, value in path_points:
        reference = evidence_ref(row, repo_root, value)
        evidence_manifest.append({key: reference[key] for key in ("path", "sha256", "captured_at_utc")})
    recovery_ref = None
    recovery_hours = None
    if recovery_index is not None:
        recovery_row, recovery_value = path_points[recovery_index]
        recovery_ref = evidence_ref(recovery_row, repo_root, recovery_value)
        recovery_time = interpreted if recovery_index == 0 else recovery_row[0]
        recovery_hours = round((recovery_time - interpreted).total_seconds() / 3600.0, 6)
    trough_time = interpreted if trough_index == 0 else trough_row[0]
    result = {
        "series_id": series_id,
        "metric_path": metric_path,
        "status": "MATURED",
        "start_value": start_value,
        "terminal_value": terminal_value,
        "terminal_return_pct": round(terminal_return, 10),
        "max_drawdown_from_start_pct": round(drawdown, 10),
        "max_upside_from_start_pct": round(upside, 10),
        "time_to_trough_hours": round((trough_time - interpreted).total_seconds() / 3600.0, 6),
        "time_to_recovery_hours": recovery_hours,
        "recovery_right_censored": recovery_index is None,
        "observation_count": len(path_points),
        "baseline_lag_hours": round((interpreted - baseline_row[0]).total_seconds() / 3600.0, 6),
        "terminal_lag_hours": round((terminal_row[0] - due).total_seconds() / 3600.0, 6),
        "observed_span_hours": round((terminal_row[0] - interpreted).total_seconds() / 3600.0, 6),
        "normalized_full_exit_counterfactual": {
            "capital_preserved_pct": round(max(-terminal_return, 0.0), 10),
            "upside_foregone_pct": round(max(terminal_return, 0.0), 10),
            "notional": "ONE_UNIT_CONTINUOUS_HOLD_VS_FULL_EXIT_AT_START",
        },
        "evidence_set_sha256": digest(evidence_manifest),
        "baseline_ref": evidence_ref(baseline_row, repo_root, start_value),
        "trough_ref": evidence_ref(trough_row, repo_root, trough_value),
        "peak_ref": evidence_ref(peak_row, repo_root, peak_value),
        "recovery_ref": recovery_ref,
        "terminal_ref": evidence_ref(terminal_row, repo_root, terminal_value),
    }
    return result


def action_counterfactuals(receipt: dict[str, Any], full_exit: dict[str, Any]) -> list[dict[str, Any]]:
    compass = receipt["action_compass"]
    lanes = [
        ("NEAR_TERM", compass["near_term"]["action"]),
        ("NEXT_WINDOW", compass["next_window"]["action"]),
        ("ALTCOIN_COMPASS", compass["altcoin_compass"]["action"]),
    ]
    rows = []
    for lane, action in lanes:
        if lane == "NEAR_TERM" and action == "EXIT":
            rows.append(
                {
                    "lane": lane,
                    "action": action,
                    "status": "NORMALIZED_FULL_EXIT_EVALUABLE",
                    "capital_preserved_pct": full_exit["capital_preserved_pct"],
                    "upside_foregone_pct": full_exit["upside_foregone_pct"],
                }
            )
        else:
            if lane != "NEAR_TERM":
                reason = "LANE_ACTION_TIMING_IS_NOT_START"
            elif action == "HOLD":
                reason = "CONTINUOUS_HOLD_REFERENCE_ONLY"
            else:
                reason = "ACTION_SIZE_OR_ENTRY_TIMING_UNDEFINED"
            rows.append(
                {
                    "lane": lane,
                    "action": action,
                    "status": "NOT_EVALUABLE_WITHOUT_INVENTED_PORTFOLIO_SEMANTICS",
                    "reason": reason,
                    "capital_preserved_pct": None,
                    "upside_foregone_pct": None,
                }
            )
    return rows


def censored_sidecar(receipt: dict[str, Any], receipt_path: Path, horizon: str, due: datetime, now: datetime, reason: str) -> dict[str, Any]:
    return {
        "contract": OUTCOME_CONTRACT,
        "receipt_id": receipt["receipt_id"],
        "receipt_path": str(receipt_path),
        "receipt_sha256": digest(receipt),
        "horizon": horizon,
        "outcome_due_utc": iso(due),
        "created_at_utc": iso(now),
        "status": "CENSORED",
        "reason": reason,
        "continuous_outcomes_only": True,
        "portfolio_execution": False,
        "authority": {"market_rule_change": False, "automatic_action": False, "automatic_promotion": False},
    }


def mature(args: argparse.Namespace) -> None:
    now = parse_time(args.now_utc) if args.now_utc else datetime.now(timezone.utc)
    rows = evidence_rows(args.evidence_root)
    matured_count = partial_count = censored_count = pending_count = existing_count = 0
    for receipt_path in sorted(args.receipt_root.rglob("*.json")) if args.receipt_root.exists() else []:
        receipt = read_json(receipt_path)
        candidate = validate_receipt(receipt)
        verify_baseline_binding(candidate, args.repo_root)
        interpreted = parse_time(receipt["interpreted_at_utc"])
        baseline = receipt["baseline_observer"]
        baseline_row: tuple[datetime, Path, dict[str, Any], str] | None = None
        if baseline["status"] == "BOUND":
            baseline_path = args.repo_root / baseline["evidence_path"]
            baseline_value = bound_baseline_value(candidate, args.repo_root)
            if baseline_value is None:
                raise ValueError("bound_baseline_unavailable")
            baseline_row = (parse_time(baseline["captured_at_utc"]), baseline_path, baseline_value, baseline["evidence_sha256"])
        for horizon, delta in HORIZONS.items():
            due = interpreted + delta
            destination = args.output_root / interpreted.strftime("%Y/%m/%d") / receipt["receipt_id"] / f"{horizon}.json"
            if destination.exists():
                existing = read_json(destination)
                if existing.get("receipt_sha256") != digest(receipt) or existing.get("horizon") != horizon:
                    raise ValueError("outcome_sidecar_identity_collision")
                existing_count += 1
                continue
            if now < due:
                pending_count += 1
                continue
            if baseline_row is None:
                sidecar = censored_sidecar(receipt, receipt_path, horizon, due, now, baseline["reason"])
                if write_immutable(destination, sidecar):
                    censored_count += 1
                else:
                    existing_count += 1
                continue
            max_terminal = due + timedelta(hours=args.max_terminal_lag_hours)
            outcomes = []
            for series in baseline["series"]:
                start_value = nested_number(baseline_row[2], series["metric_path"])
                outcome = mature_series(
                    series["series_id"],
                    series["metric_path"],
                    start_value,
                    interpreted,
                    due,
                    max_terminal,
                    rows,
                    baseline_row,
                    args.repo_root,
                )
                if outcome is not None:
                    outcomes.append(outcome)
            if not outcomes:
                if now <= max_terminal:
                    pending_count += 1
                    continue
                sidecar = censored_sidecar(receipt, receipt_path, horizon, due, now, "NO_TERMINAL_EVIDENCE_WITHIN_FROZEN_LAG")
                if write_immutable(destination, sidecar):
                    censored_count += 1
                else:
                    existing_count += 1
                continue
            if len(outcomes) < len(baseline["series"]) and now <= max_terminal:
                pending_count += 1
                continue
            status = "MATURED" if len(outcomes) == len(baseline["series"]) else "PARTIAL"
            observed_series = {outcome["series_id"] for outcome in outcomes}
            missing_series = sorted(series["series_id"] for series in baseline["series"] if series["series_id"] not in observed_series)
            for outcome in outcomes:
                outcome["action_counterfactuals"] = action_counterfactuals(receipt, outcome["normalized_full_exit_counterfactual"])
            sidecar = {
                "contract": OUTCOME_CONTRACT,
                "receipt_id": receipt["receipt_id"],
                "receipt_path": str(receipt_path),
                "receipt_sha256": digest(receipt),
                "decision_reference": f"{receipt_path}#{receipt['receipt_id']}",
                "outcome_reference": str(destination),
                "horizon": horizon,
                "outcome_due_utc": iso(due),
                "created_at_utc": iso(now),
                "status": status,
                "decision_snapshot": {
                    "near_term_action": receipt["action_compass"]["near_term"]["action"],
                    "next_window_action": receipt["action_compass"]["next_window"]["action"],
                    "lane_3_state": receipt["action_compass"]["altcoin_compass"]["state"],
                    "lane_3_action": receipt["action_compass"]["altcoin_compass"]["action"],
                    "lane_3_warning": receipt["action_compass"]["altcoin_compass"]["warning"],
                    "warning_implies_action": False,
                },
                "series_outcomes": outcomes,
                "missing_series": missing_series,
                "continuous_outcomes_only": True,
                "portfolio_execution": False,
                "authority": {"market_rule_change": False, "automatic_action": False, "automatic_promotion": False},
            }
            if not write_immutable(destination, sidecar):
                existing_count += 1
            elif status == "MATURED":
                matured_count += 1
            else:
                partial_count += 1
    print(
        json.dumps(
            {
                "status": "PASS",
                "matured": matured_count,
                "partial": partial_count,
                "censored": censored_count,
                "pending": pending_count,
                "existing": existing_count,
            },
            sort_keys=True,
        )
    )


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    sub = root.add_subparsers(dest="command", required=True)

    persist_parser = sub.add_parser("persist")
    persist_parser.add_argument("--candidate", type=Path, required=True)
    persist_parser.add_argument("--receipt-root", type=Path, required=True)
    persist_parser.add_argument("--repo-root", type=Path, required=True)
    persist_parser.add_argument("--expected-canonical-commit")
    persist_parser.add_argument("--activation-utc")
    persist_parser.add_argument("--activation-commit-sha")
    persist_parser.set_defaults(handler=persist)

    validate_parser = sub.add_parser("validate-repository")
    validate_parser.add_argument("--receipt-root", type=Path, required=True)
    validate_parser.add_argument("--repo-root", type=Path, required=True)
    validate_parser.set_defaults(handler=validate_repository)

    mature_parser = sub.add_parser("mature")
    mature_parser.add_argument("--receipt-root", type=Path, required=True)
    mature_parser.add_argument("--evidence-root", type=Path, required=True)
    mature_parser.add_argument("--output-root", type=Path, required=True)
    mature_parser.add_argument("--repo-root", type=Path, required=True)
    mature_parser.add_argument("--now-utc")
    mature_parser.add_argument("--max-terminal-lag-hours", type=float, default=24.0)
    mature_parser.set_defaults(handler=mature)
    return root


def main() -> None:
    args = parser().parse_args()
    if getattr(args, "max_terminal_lag_hours", 0) < 0:
        raise SystemExit("max_terminal_lag_hours_must_be_nonnegative")
    try:
        args.handler(args)
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"ACTION_COMPASS_ACCOUNTABILITY_ERROR:{exc}") from exc


if __name__ == "__main__":
    main()
