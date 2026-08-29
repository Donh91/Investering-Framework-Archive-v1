#!/usr/bin/env python3
"""Fail-closed DATA PING baseline integrity primitives.

This module does not interpret markets.  It binds GitHub-owned evidence to one
immutable commit, validates pointer-to-target chains, exposes separate freshness
dimensions, and validates arithmetic/provenance before evidence is consumed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable, Mapping, Sequence


SHA1_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class IntegrityError(RuntimeError):
    """A classified fail-closed integrity error."""

    def __init__(self, classification: str, detail: str):
        super().__init__(f"{classification}:{detail}")
        self.classification = classification
        self.detail = detail


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def normalized_sha256(value: Any) -> str:
    return sha256_bytes(canonical_json(value))


def parse_utc(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise IntegrityError("GITHUB_POINTER_CONFLICT", f"{label}_invalid_utc")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise IntegrityError("GITHUB_POINTER_CONFLICT", f"{label}_invalid_utc") from exc
    if parsed.tzinfo is None:
        raise IntegrityError("GITHUB_POINTER_CONFLICT", f"{label}_timezone_missing")
    return parsed.astimezone(timezone.utc)


def _safe_repo_path(value: str, label: str) -> str:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts:
        raise IntegrityError("GITHUB_POINTER_CONFLICT", f"{label}_unsafe_path")
    return path.as_posix()


@dataclass(frozen=True)
class GitHubObject:
    path: str
    commit_sha: str
    raw: bytes
    git_blob_sha: str | None = None


Reader = Callable[[str, str], GitHubObject]
RefResolver = Callable[[], str]


class PinnedGitHubSnapshot:
    """Resolve the requested ref once, then force every read through that SHA."""

    def __init__(self, repository: str, commit_sha: str, reader: Reader, *, resolution_count: int = 1):
        if not SHA1_RE.fullmatch(commit_sha):
            raise IntegrityError("GITHUB_SNAPSHOT_RESOLUTION_FAIL", "invalid_commit_sha")
        if resolution_count != 1:
            raise IntegrityError("GITHUB_SNAPSHOT_RESOLUTION_FAIL", "commit_must_be_resolved_once")
        self.repository = repository
        self.commit_sha = commit_sha
        self._reader = reader
        self.resolution_count = resolution_count
        self.read_count = 0
        self.read_paths: list[str] = []

    @classmethod
    def open(cls, repository: str, resolve_ref: RefResolver, reader: Reader) -> "PinnedGitHubSnapshot":
        return cls(repository, resolve_ref(), reader, resolution_count=1)

    def read_json(self, path: str) -> tuple[dict[str, Any], dict[str, Any]]:
        safe_path = _safe_repo_path(path, "github_path")
        try:
            source = self._reader(safe_path, self.commit_sha)
        except IntegrityError:
            raise
        except Exception as exc:
            raise IntegrityError("GITHUB_SOURCE_READ_FAIL", f"{safe_path}:{exc}") from exc
        self.read_count += 1
        self.read_paths.append(safe_path)
        if source.commit_sha != self.commit_sha:
            raise IntegrityError(
                "GITHUB_MIXED_SNAPSHOT",
                f"expected={self.commit_sha},observed={source.commit_sha},path={safe_path}",
            )
        if source.path != safe_path:
            raise IntegrityError("GITHUB_POINTER_CONFLICT", f"reader_path_mismatch:{safe_path}:{source.path}")
        try:
            value = json.loads(source.raw)
        except Exception as exc:
            raise IntegrityError("GITHUB_SOURCE_SCHEMA_FAIL", f"{safe_path}:invalid_json") from exc
        if not isinstance(value, dict):
            raise IntegrityError("GITHUB_SOURCE_SCHEMA_FAIL", f"{safe_path}:object_required")
        provenance = {
            "repository": self.repository,
            "exact_commit_sha": self.commit_sha,
            "exact_path": safe_path,
            "git_blob_sha": source.git_blob_sha,
            "request_arguments_sha256": normalized_sha256(
                {"repository": self.repository, "commit_sha": self.commit_sha, "path": safe_path}
            ),
            "raw_response_sha256": sha256_bytes(source.raw),
            "normalized_payload_sha256": normalized_sha256(value),
            "hash_semantics_contract": "DATA_PING_HASH_SEMANTICS_v1",
        }
        return value, provenance

    def consistency(self) -> dict[str, Any]:
        return {
            "status": "PASS",
            "github_snapshot_commit_sha": self.commit_sha,
            "resolution_count": self.resolution_count,
            "read_count": self.read_count,
            "all_reads_pinned_to_snapshot": True,
        }


class GitCliSnapshot(PinnedGitHubSnapshot):
    """Read immutable Git objects from an already checked-out repository."""

    @classmethod
    def open_repo(
        cls,
        repo_root: Path,
        *,
        repository: str = "Donh91/Investering-Framework-Archive-v1",
        ref: str = "refs/heads/main",
    ) -> "GitCliSnapshot":
        root = repo_root.resolve()
        commit_sha = subprocess.check_output(
            ["git", "rev-parse", "--verify", f"{ref}^{{commit}}"], cwd=root, text=True
        ).strip()

        def reader(path: str, pinned_sha: str) -> GitHubObject:
            try:
                raw = subprocess.check_output(["git", "show", f"{pinned_sha}:{path}"], cwd=root)
                blob = subprocess.check_output(
                    ["git", "rev-parse", "--verify", f"{pinned_sha}:{path}"], cwd=root, text=True
                ).strip()
            except subprocess.CalledProcessError as exc:
                raise IntegrityError("GITHUB_SOURCE_READ_FAIL", path) from exc
            return GitHubObject(path=path, commit_sha=pinned_sha, raw=raw, git_blob_sha=blob)

        return cls(repository, commit_sha, reader)


@dataclass(frozen=True)
class PointerContract:
    pointer_contracts: frozenset[str]
    target_contracts: frozenset[str]
    target_path_fields: tuple[str, ...]
    exact_semantic_fields: tuple[str, ...] = ()
    timestamp_fields: tuple[str, ...] = ()
    retrieval_timestamp_field: str | None = None
    source_observation_timestamp_field: str | None = None
    pointer_timestamp_field: str | None = None
    coverage_timestamp_field: str | None = None
    pointer_hash_fields: tuple[tuple[str, str], ...] = (
        ("target_raw_sha256", "raw_response_sha256"),
        ("target_normalized_sha256", "normalized_payload_sha256"),
        ("target_blob_sha", "git_blob_sha"),
    )


def resolve_target_path(pointer_path: str, raw_target_path: str) -> str:
    target = PurePosixPath(_safe_repo_path(raw_target_path, "target_path"))
    pointer_parent = PurePosixPath(pointer_path).parent
    known_roots = {"00_ARCHIVE_CONTROL", "01_CORE_FRAMEWORK", "02_DATA_PING", "03_DAILY_CAPTURE_LOGS", "04_MARKET_LEARNING", "research"}
    if target.parts and target.parts[0] in known_roots:
        return target.as_posix()
    if target.parts and target.parts[0] == pointer_parent.name:
        return (pointer_parent.parent / target).as_posix()
    return (pointer_parent / target).as_posix()


def resolve_pointer_chain(
    snapshot: PinnedGitHubSnapshot,
    pointer_path: str,
    contract: PointerContract,
    *,
    now_utc: datetime,
    freshness_policy: FreshnessPolicy | None = None,
) -> dict[str, Any]:
    """Resolve pointer then target at the same SHA and validate their semantics."""

    pointer, pointer_provenance = snapshot.read_json(pointer_path)
    if pointer.get("contract") not in contract.pointer_contracts:
        raise IntegrityError("GITHUB_POINTER_CONFLICT", "pointer_contract_mismatch")
    path_field = next((field for field in contract.target_path_fields if pointer.get(field)), None)
    if path_field is None or not isinstance(pointer[path_field], str):
        raise IntegrityError("GITHUB_POINTER_CONFLICT", "target_path_missing")
    target_path = resolve_target_path(pointer_path, pointer[path_field])
    target, target_provenance = snapshot.read_json(target_path)
    if target.get("contract") not in contract.target_contracts:
        raise IntegrityError("GITHUB_POINTER_CONFLICT", "target_contract_mismatch")

    for field in contract.exact_semantic_fields:
        if field in pointer and field in target and pointer[field] != target[field]:
            raise IntegrityError("GITHUB_POINTER_CONFLICT", f"semantic_mismatch:{field}")
    if pointer.get("run_id") is not None and target.get("run_id") is not None:
        if pointer["run_id"] != target["run_id"]:
            raise IntegrityError("GITHUB_POINTER_CONFLICT", "run_id_mismatch")

    now = now_utc.astimezone(timezone.utc)
    for field in contract.timestamp_fields:
        pointer_value = pointer.get(field)
        target_value = target.get(field)
        pointer_time = target_time = None
        if pointer_value is not None:
            pointer_time = parse_utc(pointer_value, f"pointer_{field}")
            if pointer_time > now:
                raise IntegrityError("GITHUB_POINTER_CONFLICT", f"future_pointer_timestamp:{field}")
        if target_value is not None:
            target_time = parse_utc(target_value, f"target_{field}")
            if target_time > now:
                raise IntegrityError("GITHUB_POINTER_CONFLICT", f"future_target_timestamp:{field}")
        if pointer_time is not None and target_time is not None and pointer_time != target_time:
            raise IntegrityError("GITHUB_POINTER_CONFLICT", f"timestamp_mismatch:{field}")

    for pointer_hash_field, provenance_field in contract.pointer_hash_fields:
        expected = pointer.get(pointer_hash_field)
        if expected is None:
            continue
        observed = target_provenance.get(provenance_field)
        if expected != observed:
            raise IntegrityError("GITHUB_POINTER_CONFLICT", f"hash_mismatch:{pointer_hash_field}")

    policy = freshness_policy or FreshnessPolicy("OWNER_CONTRACT_REQUIRED")
    freshness = freshness_vector(
        now_utc=now,
        policy=policy,
        retrieval_timestamp=target.get(contract.retrieval_timestamp_field) if contract.retrieval_timestamp_field else None,
        source_observation_timestamp=(
            target.get(contract.source_observation_timestamp_field)
            if contract.source_observation_timestamp_field else None
        ),
        pointer_timestamp=pointer.get(contract.pointer_timestamp_field) if contract.pointer_timestamp_field else None,
        coverage_timestamp=target.get(contract.coverage_timestamp_field) if contract.coverage_timestamp_field else None,
    )
    return {
        "status": "PASS",
        "classification": "GITHUB_POINTER_TARGET_CHAIN_VALID",
        "github_snapshot_commit_sha": snapshot.commit_sha,
        "pointer_contract": pointer["contract"],
        "pointer_path": pointer_path,
        "target_contract": target["contract"],
        "target_path": target_path,
        "run_id": target.get("run_id", pointer.get("run_id")),
        "freshness": freshness,
        "pointer": pointer,
        "target": target,
        "provenance": {"pointer": pointer_provenance, "target": target_provenance},
    }


def validate_cached_pointer(pinned_pointer: Mapping[str, Any], cached_pointer: Mapping[str, Any]) -> dict[str, Any]:
    """Reject any cached root that is not byte-semantically equal to the pinned pointer."""

    pinned_hash = normalized_sha256(pinned_pointer)
    cached_hash = normalized_sha256(cached_pointer)
    if pinned_hash != cached_hash:
        raise IntegrityError(
            "GITHUB_POINTER_CONFLICT",
            f"stale_cached_latest:pinned={pinned_hash},cached={cached_hash}",
        )
    return {
        "status": "PASS",
        "classification": "CACHED_POINTER_MATCHES_PINNED_SNAPSHOT",
        "normalized_payload_sha256": pinned_hash,
    }


@dataclass(frozen=True)
class FreshnessPolicy:
    policy_id: str
    retrieval_max_age: timedelta | None = None
    source_observation_max_age: timedelta | None = None
    pointer_max_age: timedelta | None = None
    coverage_max_lag: timedelta | None = None


def _freshness_dimension(
    value: Any,
    *,
    now_utc: datetime,
    max_age: timedelta | None,
    label: str,
) -> dict[str, Any]:
    if value is None:
        return {"status": "UNAVAILABLE", "timestamp": None, "age_seconds": None, "max_age_seconds": None}
    observed = parse_utc(value, label)
    age = now_utc.astimezone(timezone.utc) - observed
    if age.total_seconds() < 0:
        return {"status": "FUTURE", "timestamp": value, "age_seconds": age.total_seconds(), "max_age_seconds": None}
    if max_age is None:
        status = "POLICY_UNAVAILABLE"
        max_age_seconds = None
    else:
        status = "PASS" if age <= max_age else "STALE"
        max_age_seconds = max_age.total_seconds()
    return {"status": status, "timestamp": value, "age_seconds": age.total_seconds(), "max_age_seconds": max_age_seconds}


def freshness_vector(
    *,
    now_utc: datetime,
    policy: FreshnessPolicy,
    retrieval_timestamp: Any = None,
    source_observation_timestamp: Any = None,
    pointer_timestamp: Any = None,
    coverage_timestamp: Any = None,
) -> dict[str, Any]:
    """Return cadence-aware freshness dimensions without inventing thresholds."""

    dimensions = {
        "retrieval_freshness": _freshness_dimension(
            retrieval_timestamp, now_utc=now_utc, max_age=policy.retrieval_max_age, label="retrieval_timestamp"
        ),
        "source_observation_freshness": _freshness_dimension(
            source_observation_timestamp,
            now_utc=now_utc,
            max_age=policy.source_observation_max_age,
            label="source_observation_timestamp",
        ),
        "pointer_freshness": _freshness_dimension(
            pointer_timestamp, now_utc=now_utc, max_age=policy.pointer_max_age, label="pointer_timestamp"
        ),
        "session_coverage_freshness": _freshness_dimension(
            coverage_timestamp, now_utc=now_utc, max_age=policy.coverage_max_lag, label="coverage_timestamp"
        ),
    }
    present = [item for item in dimensions.values() if item["timestamp"] is not None]
    hard_fail = any(item["status"] in {"FUTURE", "STALE"} for item in present)
    evaluable = all(item["status"] != "POLICY_UNAVAILABLE" for item in dimensions.values() if item["timestamp"] is not None)
    if not present:
        overall_status = "UNAVAILABLE"
    elif hard_fail:
        overall_status = "FAIL"
    elif evaluable:
        overall_status = "PASS"
    else:
        overall_status = "UNCONFIRMED_POLICY"
    return {
        "contract": "DATA_PING_MULTI_DIMENSIONAL_FRESHNESS_v1",
        "policy_id": policy.policy_id,
        "status": overall_status,
        **dimensions,
    }


def validate_latest_eligible_etf_session(
    history_rows: Mapping[str, Sequence[Mapping[str, Any]]],
    selected_rows: Sequence[Mapping[str, Any]],
    *,
    required_assets: Sequence[str] = ("BTC", "ETH"),
) -> dict[str, Any]:
    """Require the selected rows to be the latest final, parity-valid common session."""

    eligible_by_asset: dict[str, set[date]] = {}
    for asset in required_assets:
        rows = history_rows.get(asset, ())
        eligible: set[date] = set()
        for row in rows:
            try:
                session = date.fromisoformat(str(row.get("date")))
            except ValueError:
                continue
            if row.get("session_final") is True and row.get("total_parity") is True:
                eligible.add(session)
        eligible_by_asset[asset] = eligible
    common = set.intersection(*(eligible_by_asset[asset] for asset in required_assets)) if required_assets else set()
    if not common:
        raise IntegrityError("ETF_SESSION_UNAVAILABLE", "no_common_final_parity_session")
    latest = max(common)

    selected_by_asset: dict[str, date] = {}
    selected_payloads: dict[str, Mapping[str, Any]] = {}
    for row in selected_rows:
        asset = str(row.get("asset"))
        if asset in required_assets:
            try:
                selected_by_asset[asset] = date.fromisoformat(str(row.get("date")))
            except ValueError as exc:
                raise IntegrityError("ETF_SESSION_INVALID", f"{asset}:date") from exc
            if row.get("session_final") is not True or row.get("total_parity") is not True:
                raise IntegrityError("ETF_SESSION_INVALID", f"{asset}:not_final_or_parity")
            selected_payloads[asset] = row
    if set(selected_by_asset) != set(required_assets):
        raise IntegrityError("ETF_SESSION_INVALID", "selected_assets_incomplete")
    if len(set(selected_by_asset.values())) != 1:
        raise IntegrityError("ETF_SESSION_INVALID", "selected_assets_mixed_sessions")
    selected = next(iter(selected_by_asset.values()))
    if selected != latest:
        raise IntegrityError("ETF_SESSION_LAG", f"selected={selected.isoformat()},latest={latest.isoformat()}")
    for asset in required_assets:
        history_match = next(
            (
                row for row in history_rows.get(asset, ())
                if str(row.get("date")) == selected.isoformat()
                and row.get("session_final") is True
                and row.get("total_parity") is True
            ),
            None,
        )
        if history_match is None:
            raise IntegrityError("ETF_SESSION_INVALID", f"{asset}:selected_not_in_history")
        for value_field in ("reported_total", "calculated_total"):
            if value_field in selected_payloads[asset] and value_field in history_match:
                selected_value = _number(selected_payloads[asset][value_field], f"selected_{asset}_{value_field}")
                history_value = _number(history_match[value_field], f"history_{asset}_{value_field}")
                if not math.isclose(selected_value, history_value, rel_tol=1e-12, abs_tol=1e-9):
                    raise IntegrityError("ETF_SESSION_INVALID", f"{asset}:{value_field}_history_mismatch")
    return {
        "status": "PASS",
        "classification": "ETF_LATEST_ELIGIBLE_SETTLED_SESSION",
        "selected_session_date": selected.isoformat(),
        "latest_eligible_settled_session": latest.isoformat(),
        "session_lag_days": 0,
        "required_assets": list(required_assets),
    }


def _number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise IntegrityError("DELTA_INTEGRITY_FAIL", f"{label}_not_finite_number")
    return float(value)


def validate_delta(
    *,
    current: Any,
    predecessor: Any,
    reported_absolute_delta: Any,
    reported_pct_delta: Any,
    absolute_tolerance: float = 1e-6,
    relative_tolerance: float = 1e-9,
    current_context: Mapping[str, Any] | None = None,
    predecessor_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if (current_context is None) != (predecessor_context is None):
        raise IntegrityError("DELTA_PREDECESSOR_INCOMPATIBLE", "one_context_missing")
    if current_context is not None and normalized_sha256(current_context) != normalized_sha256(predecessor_context):
        raise IntegrityError("DELTA_PREDECESSOR_INCOMPATIBLE", "context_mismatch")
    current_value = _number(current, "current")
    predecessor_value = _number(predecessor, "predecessor")
    absolute_value = _number(reported_absolute_delta, "reported_absolute_delta")
    expected_absolute = current_value - predecessor_value
    absolute_ok = math.isclose(
        absolute_value, expected_absolute, rel_tol=relative_tolerance, abs_tol=absolute_tolerance
    )
    expected_pct = None if predecessor_value == 0 else (current_value / predecessor_value - 1.0) * 100.0
    if expected_pct is None:
        pct_ok = reported_pct_delta is None
        pct_value = None
    else:
        pct_value = _number(reported_pct_delta, "reported_pct_delta")
        pct_ok = math.isclose(pct_value, expected_pct, rel_tol=relative_tolerance, abs_tol=absolute_tolerance)
    if not absolute_ok or not pct_ok:
        failures = []
        if not absolute_ok:
            failures.append("ABSOLUTE_DELTA_MISMATCH")
        if not pct_ok:
            failures.append("PCT_DELTA_MISMATCH")
        raise IntegrityError("DELTA_INTEGRITY_FAIL", ",".join(failures))
    return {
        "status": "PASS",
        "classification": "DELTA_INTEGRITY_PASS",
        "current": current_value,
        "predecessor": predecessor_value,
        "absolute_delta": expected_absolute,
        "pct_delta": expected_pct,
        "absolute_tolerance": absolute_tolerance,
        "relative_tolerance": relative_tolerance,
        "predecessor_compatibility": "PASS" if current_context is not None else "NOT_ASSERTED",
    }


def validate_delta_block(items: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    results = []
    failures = []
    for index, item in enumerate(items):
        try:
            results.append(validate_delta(**item))
        except IntegrityError as exc:
            failures.append({"index": index, "classification": exc.classification, "detail": exc.detail})
    return {
        "status": "PASS" if not failures else "DEGRADED",
        "classification": "DELTA_INTEGRITY_PASS" if not failures else "DELTA_INTEGRITY_FAIL",
        "validated_count": len(results),
        "failure_count": len(failures),
        "failures": failures,
    }


def select_macro_evidence(
    macro_values: Mapping[str, Any],
    *,
    owner_authority_valid: bool,
    owner_snapshot_commit_sha: str | None,
    expected_snapshot_commit_sha: str,
    retrieval_freshness_status: str,
    source_observation_freshness_status: str,
    required_series: Sequence[str] = ("DGS2", "DGS10", "VIX"),
) -> dict[str, Any]:
    """Decide owner reuse versus direct fallback without performing external calls."""

    reasons = []
    missing = [series for series in required_series if macro_values.get(series) is None]
    if missing:
        reasons.append("REQUIRED_SERIES_MISSING:" + ",".join(missing))
    if not owner_authority_valid:
        reasons.append("OWNER_AUTHORITY_INVALID")
    if owner_snapshot_commit_sha != expected_snapshot_commit_sha:
        reasons.append("OWNER_NOT_BOUND_TO_PINNED_SNAPSHOT")
    if retrieval_freshness_status != "PASS":
        reasons.append("RETRIEVAL_FRESHNESS_NOT_PASS")
    if source_observation_freshness_status != "PASS":
        reasons.append("SOURCE_OBSERVATION_FRESHNESS_NOT_PASS")
    return {
        "status": "OWNER_REUSE" if not reasons else "DIRECT_FALLBACK_REQUIRED",
        "external_calls_avoided": len(required_series) if not reasons else 0,
        "required_series": list(required_series),
        "reasons": reasons,
        "github_snapshot_commit_sha": expected_snapshot_commit_sha,
    }


DAILY_POINTER = PointerContract(
    pointer_contracts=frozenset({"DAILY_LIVE_ANCHOR_LATEST_POINTER_v1"}),
    target_contracts=frozenset({"DAILY_LIVE_ANCHOR_INDEX_v3"}),
    target_path_fields=("path",),
    exact_semantic_fields=("status",),
    timestamp_fields=("captured_at_utc",),
    retrieval_timestamp_field="captured_at_utc",
    pointer_timestamp_field="captured_at_utc",
    coverage_timestamp_field="captured_at_utc",
)

HOURLY_POINTER = PointerContract(
    pointer_contracts=frozenset({"HOURLY_SEQUENCE_LATEST_POINTER_v2_2"}),
    target_contracts=frozenset({"HOURLY_SEQUENCE_CAPTURE_v2_2"}),
    target_path_fields=("run_path",),
    exact_semantic_fields=(
        "status", "window_start_utc", "window_end_utc", "requested_hours",
        "spot_complete_hours", "spot_flow_complete_hours", "derivatives_oi_complete_hours",
        "long_short_complete_hours",
    ),
    timestamp_fields=("retrieved_at_utc", "window_start_utc", "window_end_utc"),
    retrieval_timestamp_field="retrieved_at_utc",
    source_observation_timestamp_field="window_end_utc",
    pointer_timestamp_field="retrieved_at_utc",
    coverage_timestamp_field="window_end_utc",
)


def audit_repo(snapshot: PinnedGitHubSnapshot, *, now_utc: datetime) -> dict[str, Any]:
    lanes: dict[str, Any] = {}
    errors: list[dict[str, str]] = []
    for lane, path, contract in (
        ("daily_live_anchor", "03_DAILY_CAPTURE_LOGS/captures/LATEST.json", DAILY_POINTER),
        ("hourly_sequence", "03_DAILY_CAPTURE_LOGS/hourly/LATEST.json", HOURLY_POINTER),
    ):
        try:
            lanes[lane] = resolve_pointer_chain(snapshot, path, contract, now_utc=now_utc)
        except IntegrityError as exc:
            lanes[lane] = {"status": "FAIL", "classification": exc.classification, "detail": exc.detail}
            errors.append({"lane": lane, "classification": exc.classification, "detail": exc.detail})
    try:
        etf, etf_provenance = snapshot.read_json("research/etf_owner/LATEST_FARSIDE_ETF_OWNER.json")
        etf_result = validate_latest_eligible_etf_session(etf.get("history_rows", {}), etf.get("rows", []))
        lanes["farside_etf"] = {
            **etf_result,
            "freshness": freshness_vector(
                now_utc=now_utc,
                policy=FreshnessPolicy("ETF_OWNER_CONTRACT_REQUIRED"),
                retrieval_timestamp=etf.get("retrieved_at_utc"),
            ),
            "provenance": etf_provenance,
        }
    except IntegrityError as exc:
        lanes["farside_etf"] = {"status": "FAIL", "classification": exc.classification, "detail": exc.detail}
        errors.append({"lane": "farside_etf", "classification": exc.classification, "detail": exc.detail})
    return {
        "contract": "DATA_PING_TRUTH_INTEGRITY_READBACK_v1",
        "status": "PASS" if not errors else "FAIL",
        "github_snapshot_commit_sha": snapshot.commit_sha,
        "github_snapshot_consistency": snapshot.consistency(),
        "lanes": lanes,
        "errors": errors,
        "portfolio_execution": "FORBIDDEN",
        "market_interpretation": "NOT_PERFORMED",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("audit-repo", nargs="?")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--ref", default="refs/heads/main")
    parser.add_argument("--now-utc")
    args = parser.parse_args()
    now = parse_utc(args.now_utc, "now_utc") if args.now_utc else datetime.now(timezone.utc)
    snapshot = GitCliSnapshot.open_repo(args.repo_root, ref=args.ref)
    result = audit_repo(snapshot, now_utc=now)
    print(json.dumps(result, sort_keys=True))
    raise SystemExit(0 if result["status"] == "PASS" else 2)


if __name__ == "__main__":
    main()
