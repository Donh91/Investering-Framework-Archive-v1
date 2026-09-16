#!/usr/bin/env python3
"""Build a deterministic, read-only T10 forecast-lineage completeness report.

The report discovers every immutable official forecast ledger.  Known owner routes
bind each forward week to its ratified source, receipt, Cycle Navigator handoff,
verified actual and score.  An unknown future week therefore fails visibly instead
of silently falling out of the lineage population.

W28 is a permanent fail-closed exception unless its genuine ratified source is
recovered by a separately authorized repair.  This observer never infers that
source from later narrative or from similar values.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

CONTRACT = "T10_FORWARD_LINEAGE_COMPLETENESS_v1"
HISTORICAL_GAP_WEEK = "2026-W28"
LEDGER_GLOB = "*__forecast-ledger-*-w*__official.md"
FORECAST_ID_RE = re.compile(r"\bMM_20\d{2}_W\d{2}_[A-Z0-9_]+\b")
WEEK_RE = re.compile(r"forecast-ledger-(20\d{2})-w(\d{2})", re.IGNORECASE)
MUTABLE_NAME_RE = re.compile(r"(^|[_-])latest([_.-]|$)", re.IGNORECASE)

AUTHORITY = {
    "binding": False,
    "canonical_state_change": False,
    "historical_repair": False,
    "market_rule_change": False,
    "portfolio_action": False,
    "report_only": True,
}


OWNER_ROUTES: dict[str, dict[str, Any]] = {
    "2026-W29": {
        "source_master_monday": "03_WEEKLY_OPERATIONS/master_monday/2026-W29/03_framework_ratified_final.md",
        "ratification_receipt": "03_WEEKLY_OPERATIONS/master_monday/2026-W29/run_receipt.json",
        "cn_handoff": "03_WEEKLY_OPERATIONS/master_monday/2026-W29/04_cycle_navigator_handoff_notes.md",
        "verified_actual": "02_DATA_PING/weekly_closeouts/accepted/2026-07-20T054959Z__master-monday-w30-final-closeout__accepted.json",
        "score": "03_WEEKLY_OPERATIONS/forecast_experiments/scored/2026-W29__cycle-navigator-16__prospective-valid-score-import.json",
        "actual_link": {
            "kind": "shared_token",
            "token": "MASTER_MONDAY_CLOSEOUT_W30_20260720T054959Z",
        },
    },
    "2026-W30": {
        "source_master_monday": "03_WEEKLY_OPERATIONS/master_monday/2026-W30/03_framework_ratified_final.md",
        "ratification_receipt": "03_WEEKLY_OPERATIONS/master_monday/2026-W30/run_receipt.json",
        "cn_handoff": "03_WEEKLY_OPERATIONS/master_monday/2026-W30/04_cycle_navigator_handoff_notes.md",
        "verified_actual": "08_SOURCE_MATERIAL/data_ping/weekly_ranges/2026-W30__binance-spot-btc-eth__machine.json",
        "score": "03_WEEKLY_OPERATIONS/forecast_ledger/scoring/2026-07-27__forecast-score-2026-w30__transparent-audit.md",
        "actual_link": {
            "kind": "shared_token",
            "token": "DP-W30-2026-BTCETH-20260727T054421819Z",
        },
    },
    "2026-W31": {
        "source_master_monday": "03_WEEKLY_OPERATIONS/master_monday/2026-W31/03_framework_ratified_final.md",
        "ratification_receipt": "03_WEEKLY_OPERATIONS/master_monday/2026-W31/run_receipt_recovery_20260727T174239Z.json",
        "cn_handoff": "03_WEEKLY_OPERATIONS/master_monday/2026-W31/04_cycle_navigator_handoff_notes.md",
        "verified_actual": "04_MARKET_LEARNING/master_monday/2026-W31/MASTER_MONDAY_MACHINE_PACKAGE.json",
        "score": "03_WEEKLY_OPERATIONS/forecast_ledger/scoring/2026-08-03__forecast-score-2026-w31__transparent-audit.md",
        "actual_link": {
            "kind": "json_values_in_score",
            "json_paths": [
                "market.completed_week.BTCUSDT.low",
                "market.completed_week.BTCUSDT.high",
                "market.completed_week.ETHUSDT.low",
                "market.completed_week.ETHUSDT.high",
            ],
        },
    },
}

EDGE_NAMES = (
    "forecast",
    "source_master_monday",
    "ratification_receipt",
    "cn_handoff",
    "verified_actual",
    "score",
)


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_mutable_reference(relative: str) -> bool:
    return any(MUTABLE_NAME_RE.search(part) for part in Path(relative).parts)


def immutable_reference(root: Path, relative: str | None) -> tuple[dict[str, Any] | None, str | None]:
    if not relative:
        return None, "path_missing"
    if is_mutable_reference(relative):
        return None, "mutable_reference"
    path = root / relative
    if not path.is_file() or path.is_symlink():
        return None, "file_missing"
    return {"path": relative, "sha256": sha256_file(path), "immutable": True}, None


def read_text(root: Path, relative: str) -> str:
    return (root / relative).read_text(encoding="utf-8")


def read_json(root: Path, relative: str) -> dict[str, Any]:
    value = json.loads(read_text(root, relative))
    if not isinstance(value, dict):
        raise ValueError(f"json_object_required:{relative}")
    return value


def get_json_path(value: dict[str, Any], dotted: str) -> Any:
    current: Any = value
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            raise KeyError(dotted)
        current = current[part]
    return current


def numeric_tokens(value: Any) -> set[str]:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return set()
    number = float(value)
    return {f"{number:.2f}", f"{number:g}", f"{number:,.2f}"}


def extract_week(path: Path) -> str:
    match = WEEK_RE.search(path.name)
    if not match:
        raise ValueError(f"week_not_parseable:{path}")
    return f"{match.group(1)}-W{match.group(2)}"


def extract_forecast_ids(text: str) -> list[str]:
    return list(dict.fromkeys(FORECAST_ID_RE.findall(text)))


def receipt_links(
    root: Path,
    receipt_path: str,
    expected: dict[str, str],
) -> tuple[bool, list[str]]:
    try:
        receipt = read_json(root, receipt_path)
    except (OSError, ValueError, json.JSONDecodeError):
        return False, ["ratification_receipt_unreadable"]
    artifacts = receipt.get("artifact_paths")
    if not isinstance(artifacts, dict):
        return False, ["receipt_artifact_paths_missing"]
    missing: list[str] = []
    for label, path in expected.items():
        if path not in artifacts.values():
            missing.append(f"receipt_to_{label}")
    return not missing, missing


def actual_links_to_score(
    root: Path,
    actual_path: str,
    score_path: str,
    link: dict[str, Any],
) -> tuple[bool, str]:
    actual_text = read_text(root, actual_path)
    score_text = read_text(root, score_path)
    kind = link.get("kind")
    if kind == "shared_token":
        token = str(link.get("token") or "")
        return bool(token and token in actual_text and token in score_text), "SHARED_IMMUTABLE_SOURCE_ID"
    if kind == "json_values_in_score":
        actual = read_json(root, actual_path)
        for dotted in link.get("json_paths") or []:
            try:
                value = get_json_path(actual, str(dotted))
            except KeyError:
                return False, "VERIFIED_ACTUAL_VALUE_RECONCILIATION"
            if not any(token in score_text for token in numeric_tokens(value)):
                return False, "VERIFIED_ACTUAL_VALUE_RECONCILIATION"
        return True, "VERIFIED_ACTUAL_VALUE_RECONCILIATION"
    return False, "UNKNOWN_LINK_METHOD"


def score_links_to_forecast(
    root: Path,
    week: str,
    forecast_path: str,
    receipt_path: str,
    score_path: str,
) -> tuple[bool, str]:
    score_text = read_text(root, score_path)
    if forecast_path in score_text:
        return True, "EXACT_FORECAST_PATH"
    if score_path.endswith(".json"):
        score = read_json(root, score_path)
        receipt = read_json(root, receipt_path)
        forecast_commit = None
        for row in receipt.get("artifact_verification") or []:
            if isinstance(row, dict) and row.get("path") == forecast_path:
                forecast_commit = row.get("creation_commit_sha")
                break
        if score.get("source_forecast_period") == week and forecast_commit and score.get("source_forecast_ledger_commit") == forecast_commit:
            return True, "FORECAST_CREATION_COMMIT"
    return False, "NO_IMMUTABLE_FORECAST_LINK"


def historical_gap_week(root: Path, ledger_path: str, forecast_ids: list[str]) -> dict[str, Any]:
    correction = "03_WEEKLY_OPERATIONS/master_monday/2026-W28/05_forecast-ledger-lineage-correction.md"
    actual = "03_WEEKLY_OPERATIONS/master_monday/2026-W29/03_framework_ratified_final.md"
    forecast_ref, _ = immutable_reference(root, ledger_path)
    policy_ref, policy_error = immutable_reference(root, correction)
    actual_ref, actual_error = immutable_reference(root, actual)
    missing = [
        "source_master_monday:genuine_ratified_source_missing",
        "ratification_receipt:missing",
        "cn_handoff:missing",
        "score:forbidden_while_lineage_unresolved",
    ]
    if policy_error:
        missing.append(f"policy_evidence:{policy_error}")
    if actual_error:
        missing.append(f"verified_actual:{actual_error}")
    references = {
        "forecast": forecast_ref,
        "source_master_monday": None,
        "ratification_receipt": None,
        "cn_handoff": None,
        "verified_actual": actual_ref,
        "score": None,
    }
    rows = [
        {
            "forecast_id": forecast_id,
            "week": HISTORICAL_GAP_WEEK,
            "status": "UNSCORED_LINEAGE_GAP",
            "scoring_status": "BLOCKED",
            "missing_edges": missing,
            "references": references,
        }
        for forecast_id in forecast_ids
    ]
    return {
        "week": HISTORICAL_GAP_WEEK,
        "status": "UNSCORED_LINEAGE_GAP",
        "forecast_ids": forecast_ids,
        "missing_edges": missing,
        "policy_evidence": policy_ref,
        "rows": rows,
    }


def routed_week(
    root: Path,
    week: str,
    ledger_path: str,
    forecast_ids: list[str],
    route: dict[str, Any],
) -> dict[str, Any]:
    references: dict[str, Any] = {}
    missing: list[str] = []
    paths = {"forecast": ledger_path, **{name: route.get(name) for name in EDGE_NAMES if name != "forecast"}}
    for edge, relative in paths.items():
        ref, error = immutable_reference(root, str(relative) if relative else None)
        references[edge] = ref
        if error:
            missing.append(f"{edge}:{error}")

    link_checks: dict[str, Any] = {}
    if not missing:
        receipt_ok, receipt_missing = receipt_links(
            root,
            str(route["ratification_receipt"]),
            {
                "forecast": ledger_path,
                "source_master_monday": str(route["source_master_monday"]),
                "cn_handoff": str(route["cn_handoff"]),
            },
        )
        link_checks["receipt_links_owner_artifacts"] = receipt_ok
        missing.extend(receipt_missing)

        forecast_ok, forecast_method = score_links_to_forecast(
            root,
            week,
            ledger_path,
            str(route["ratification_receipt"]),
            str(route["score"]),
        )
        link_checks["score_links_forecast"] = {"pass": forecast_ok, "method": forecast_method}
        if not forecast_ok:
            missing.append("score_to_forecast")

        actual_ok, actual_method = actual_links_to_score(
            root,
            str(route["verified_actual"]),
            str(route["score"]),
            dict(route.get("actual_link") or {}),
        )
        link_checks["score_links_verified_actual"] = {"pass": actual_ok, "method": actual_method}
        if not actual_ok:
            missing.append("score_to_verified_actual")

    status = "COMPLETE_SCORED_LINEAGE" if not missing else "INCOMPLETE_SCORING_BLOCKED"
    rows = [
        {
            "forecast_id": forecast_id,
            "week": week,
            "status": status,
            "scoring_status": "SCORED" if not missing else "BLOCKED",
            "missing_edges": missing,
            "references": references,
        }
        for forecast_id in forecast_ids
    ]
    return {
        "week": week,
        "status": status,
        "forecast_ids": forecast_ids,
        "missing_edges": missing,
        "link_checks": link_checks,
        "rows": rows,
    }


def build_report(root: Path, owner_routes: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    routes = OWNER_ROUTES if owner_routes is None else owner_routes
    ledger_root = root / "03_WEEKLY_OPERATIONS/forecast_ledger"
    ledgers = sorted(ledger_root.glob(LEDGER_GLOB))
    weeks: list[dict[str, Any]] = []
    all_rows: list[dict[str, Any]] = []

    for ledger in ledgers:
        relative = ledger.relative_to(root).as_posix()
        week = extract_week(ledger)
        forecast_ids = extract_forecast_ids(ledger.read_text(encoding="utf-8"))
        if week == HISTORICAL_GAP_WEEK:
            item = historical_gap_week(root, relative, forecast_ids)
        elif week not in routes:
            ref, error = immutable_reference(root, relative)
            missing = ["owner_route:missing"]
            if error:
                missing.append(f"forecast:{error}")
            item = {
                "week": week,
                "status": "INCOMPLETE_SCORING_BLOCKED",
                "forecast_ids": forecast_ids,
                "missing_edges": missing,
                "link_checks": {},
                "rows": [
                    {
                        "forecast_id": forecast_id,
                        "week": week,
                        "status": "INCOMPLETE_SCORING_BLOCKED",
                        "scoring_status": "BLOCKED",
                        "missing_edges": missing,
                        "references": {"forecast": ref},
                    }
                    for forecast_id in forecast_ids
                ],
            }
        else:
            item = routed_week(root, week, relative, forecast_ids, routes[week])
        weeks.append(item)
        all_rows.extend(item["rows"])

    forward = [row for row in all_rows if row["week"] != HISTORICAL_GAP_WEEK]
    complete_forward = [row for row in forward if row["status"] == "COMPLETE_SCORED_LINEAGE"]
    w28_rows = [row for row in all_rows if row["week"] == HISTORICAL_GAP_WEEK]
    gate_pass = bool(forward) and len(complete_forward) == len(forward) and bool(w28_rows) and all(
        row["status"] == "UNSCORED_LINEAGE_GAP" for row in w28_rows
    )
    return {
        "contract": CONTRACT,
        "authority": AUTHORITY,
        "discovery": {
            "ledger_glob": f"03_WEEKLY_OPERATIONS/forecast_ledger/{LEDGER_GLOB}",
            "official_ledgers": len(ledgers),
            "future_unrouted_ledgers_fail_closed": True,
            "mutable_references_accepted": False,
        },
        "totals": {
            "forecast_rows": len(all_rows),
            "forward_rows": len(forward),
            "complete_forward_rows": len(complete_forward),
            "historical_w28_unscored_rows": len(w28_rows),
            "incomplete_rows": sum(row["status"] == "INCOMPLETE_SCORING_BLOCKED" for row in all_rows),
        },
        "post_fix_gate": {
            "name": "FORWARD_LINEAGE_REPORT_RECONCILES_TO_OFFICIAL_ROWS_AND_PRESERVES_W28_UNSCORED",
            "status": "PASS" if gate_pass else "FAIL",
        },
        "weeks": weeks,
        "rows": all_rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("06_RESEARCH_LAB/forward_tests/T10_FORWARD_LINEAGE_COMPLETENESS.json"),
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    root = args.repo_root.resolve()
    report = build_report(root)
    output = args.output if args.output.is_absolute() else root / args.output
    rendered = canonical_json(report)
    if args.check:
        if not output.is_file() or output.read_bytes() != rendered:
            raise SystemExit("T10_FORWARD_LINEAGE_REPORT_STALE")
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(rendered)
    print(json.dumps(report["post_fix_gate"], sort_keys=True))


if __name__ == "__main__":
    main()
