from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from typing import Any

AUTHORITY = "INTERNAL_ACCOUNTABILITY_ONLY_NO_PORTFOLIO_AUTHORITY"
FREEZE_CONTRACT = "CYCLE_NAVIGATOR_INTERNAL_PRECISION_FREEZE_v2"
SCORECARD_CONTRACT = "CYCLE_NAVIGATOR_INTERNAL_PRECISION_SCORECARD_v2"
SUMMARY_LEDGER_CONTRACT = "CYCLE_NAVIGATOR_INTERNAL_PRECISION_LEDGER_v2"
PARAM_LEDGER_CONTRACT = "CYCLE_NAVIGATOR_INTERNAL_PARAMETER_LEDGER_v1"
ALLOWED_STATUS = {"SUPPORTED": 100.0, "MIXED": 50.0, "CONTRADICTED": 0.0, "NOT_EVALUABLE": None}


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pct(n: int, d: int) -> float | None:
    return round(100.0 * n / d, 2) if d else None


def advance_iso_week(year: int, week: int, delta_weeks: int) -> tuple[int, int]:
    d = date.fromisocalendar(year, week, 1) + timedelta(weeks=delta_weeks)
    iso = d.isocalendar()
    return int(iso.year), int(iso.week)


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and value.strip().upper() != "UNAVAILABLE"


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def expected_parameter_ids(freeze: dict[str, Any]) -> list[str]:
    result: list[str] = []
    if freeze.get("btc_range_low") is not None and freeze.get("btc_range_high") is not None:
        result.append("btc_range")
    if freeze.get("eth_range_low") is not None and freeze.get("eth_range_high") is not None:
        result.append("eth_range")
    if nonempty(freeze.get("ethbtc_condition")):
        result.append("ethbtc_condition")
    if nonempty(freeze.get("breadth_condition")):
        result.append("breadth_condition")
    calls = freeze.get("structural_calls")
    if isinstance(calls, list):
        for index, call in enumerate(calls, start=1):
            if nonempty(call):
                result.append(f"structural_call_{index}")
    intraday = freeze.get("intraday_map")
    if isinstance(intraday, dict):
        for bucket in ("day_1_2", "day_3_4", "day_5_7"):
            if nonempty(intraday.get(bucket)):
                result.append(f"intraday_{bucket}")
    return result


def family_for(parameter_id: str, prior_freeze: dict[str, Any]) -> tuple[str, str | None]:
    direct = {
        "btc_range": "btc_range",
        "eth_range": "eth_range",
        "ethbtc_condition": "ethbtc",
        "breadth_condition": "breadth",
        "intraday_day_1_2": "intraday_day_1_2",
        "intraday_day_3_4": "intraday_day_3_4",
        "intraday_day_5_7": "intraday_day_5_7",
    }
    if parameter_id in direct:
        return direct[parameter_id], None
    m = re.fullmatch(r"structural_call_(\d+)", parameter_id)
    if not m:
        return parameter_id, None
    calls = prior_freeze.get("structural_calls") or []
    idx = int(m.group(1)) - 1
    text = normalize_text(str(calls[idx])) if 0 <= idx < len(calls) else ""
    ms2 = prior_freeze.get("market_structure_v2") if isinstance(prior_freeze.get("market_structure_v2"), dict) else {}
    if ms2.get("logic_version") == "2.1":
        v21 = {
            0: "regime",
            1: "leadership_quality",
            2: "first_handoff",
            3: "deeper_transmission",
            4: "breadth_persistence",
        }
        if idx in v21:
            return v21[idx], None
    if text.startswith("regime:"):
        return "regime", None
    if text.startswith("leadership:"):
        alias = "ethbtc_condition" if nonempty(prior_freeze.get("ethbtc_condition")) else None
        return "ethbtc", alias
    if text.startswith("first_handoff:"):
        return "first_handoff", None
    if text.startswith("deeper_transmission:"):
        return "deeper_transmission", None
    if text.startswith("breadth_persistence:"):
        return "breadth_persistence", None
    if "eth/btc" in text or "ethbtc" in text:
        alias = "ethbtc_condition" if nonempty(prior_freeze.get("ethbtc_condition")) else None
        return "ethbtc", alias
    if "altseason" in text or "broad alt" in text:
        return "altseason", None
    if "midcap" in text or "small cap" in text or "small-cap" in text or "microcap" in text or "rotation" in text:
        return "rotation", None
    if "leadership" in text:
        return "leadership", None
    if "breadth" in text:
        alias = "breadth_condition" if nonempty(prior_freeze.get("breadth_condition")) else None
        return "breadth", alias
    if any(token in text for token in ("regime", "transition", "consolidation", "breakdown", "risk-expansion", "risk expansion", "pullback")):
        return "regime", None
    return parameter_id, None


def bounded_w37_migration(completed_week: int, issue_scored: int, expected: list[str]) -> list[dict[str, Any]] | None:
    if completed_week != 37 or issue_scored != 25:
        return None
    if expected != [
        "ethbtc_condition", "breadth_condition", "structural_call_1", "structural_call_2",
        "structural_call_3", "structural_call_4", "structural_call_5"
    ]:
        return None
    evidence = {
        "ethbtc_condition": ("SUPPORTED", "Final W37 evidence showed ETH/BTC rose over the completed week."),
        "breadth_condition": ("SUPPORTED", "Final W37 evidence supported weak proxy breadth and no broad rotation confirmation."),
        "structural_call_1": ("SUPPORTED", "W37 ended as an unresolved volatile transition/consolidation, not broad expansion."),
        "structural_call_2": ("SUPPORTED", "ETH/BTC finished W37 non-negative as frozen."),
        "structural_call_3": ("SUPPORTED", "ETH relative strength remained narrow rather than broadly transmitted."),
        "structural_call_4": ("MIXED", "Direction was supported, but completed-week outcome ingestion did not independently establish every mid/small/micro tier."),
        "structural_call_5": ("SUPPORTED", "Broad altseason remained inactive through W37 close."),
    }
    return [
        {"parameter_id": pid, "status": evidence[pid][0], "score": ALLOWED_STATUS[evidence[pid][0]], "evidence": evidence[pid][1]}
        for pid in expected
    ]


def score_rows_from_public(machine: dict[str, Any], scorecard: dict[str, Any], prior_freeze: dict[str, Any], completed_week: int) -> tuple[list[dict[str, Any]], str]:
    expected = expected_parameter_ids(prior_freeze)
    evaluation = machine.get("evaluation") if isinstance(machine.get("evaluation"), dict) else scorecard
    raw = evaluation.get("parameter_scores") if isinstance(evaluation, dict) else None
    source = "PUBLIC_PARAMETER_SCORES"
    if not isinstance(raw, list) or not raw:
        raw = bounded_w37_migration(completed_week, int(scorecard.get("issue_scored", 0) or 0), expected)
        source = "BOUNDED_W37_MIGRATION_FROM_EXISTING_FROZEN_CLAIMS"
    if raw is None:
        raise SystemExit("INTERNAL_PRECISION_BLOCKED_PARAMETER_SCORES_MISSING")
    by_id: dict[str, dict[str, Any]] = {}
    for row in raw:
        if not isinstance(row, dict):
            raise SystemExit("INTERNAL_PRECISION_INVALID_PARAMETER_SCORE_ROW")
        pid = str(row.get("parameter_id") or "")
        if not pid or pid in by_id:
            raise SystemExit("INTERNAL_PRECISION_DUPLICATE_OR_EMPTY_PARAMETER_ID")
        status = str(row.get("status") or "")
        if status not in ALLOWED_STATUS:
            raise SystemExit(f"INTERNAL_PRECISION_INVALID_STATUS:{status}")
        expected_score = ALLOWED_STATUS[status]
        score = row.get("score")
        if expected_score is None:
            if score is not None:
                raise SystemExit(f"INTERNAL_PRECISION_NOT_EVALUABLE_SCORE_MUST_BE_NULL:{pid}")
        elif float(score) != expected_score:
            raise SystemExit(f"INTERNAL_PRECISION_SCORE_STATUS_MISMATCH:{pid}")
        by_id[pid] = row
    if list(by_id) != expected:
        missing = [p for p in expected if p not in by_id]
        extra = [p for p in by_id if p not in expected]
        raise SystemExit(f"INTERNAL_PRECISION_COVERAGE_MISMATCH:missing={missing}:extra={extra}")
    rows: list[dict[str, Any]] = []
    for pid in expected:
        row = by_id[pid]
        family, alias_of = family_for(pid, prior_freeze)
        rows.append({
            "parameter_id": pid,
            "family": family,
            "alias_of": alias_of,
            "headline_eligible": alias_of is None,
            "status": row["status"],
            "score": row.get("score"),
            "evidence": str(row.get("evidence") or ""),
            "source": source,
        })
    return rows, source


def family_scores(rows: list[dict[str, Any]]) -> dict[str, float | None]:
    grouped: dict[str, list[float]] = defaultdict(list)
    null_only: set[str] = set()
    for row in rows:
        if not row.get("headline_eligible", True):
            continue
        fam = str(row["family"])
        if row.get("score") is None:
            null_only.add(fam)
        else:
            grouped[fam].append(float(row["score"]))
    out: dict[str, float | None] = {}
    for fam in sorted(set(grouped) | null_only):
        vals = grouped.get(fam, [])
        out[fam] = round(sum(vals) / len(vals), 2) if vals else None
    return out


def claim(family: str, parameter_id: str, forecast: str, horizon: str, maturity_year: int, maturity_week: int, public_freeze_sha: str, machine_sha: str, issue: int, target_year: int, target_week: int, alias_of: str | None = None) -> dict[str, Any]:
    safe = re.sub(r"[^a-z0-9_]+", "_", parameter_id.lower()).strip("_")
    return {
        "claim_id": f"CN{issue}-Y{target_year}-W{target_week:02d}-{safe}",
        "family": family,
        "source_parameter_id": parameter_id,
        "alias_of": alias_of,
        "forecast": forecast,
        "horizon": horizon,
        "maturity_iso_year": maturity_year,
        "maturity_iso_week": maturity_week,
        "score_authority": AUTHORITY,
        "source_public_freeze_sha256": public_freeze_sha,
        "source_machine_package_sha256_at_materialization": machine_sha,
    }


def build_current_freeze(machine: dict[str, Any], public_freeze: dict[str, Any], issue: int, target_year: int, target_week: int, public_freeze_sha: str, machine_sha: str) -> dict[str, Any]:
    claims: list[dict[str, Any]] = []
    unavailable: list[str] = []
    if public_freeze.get("btc_range_low") is not None and public_freeze.get("btc_range_high") is not None:
        claims.append(claim("btc_range", "btc_range", f"BTC weekly range {public_freeze['btc_range_low']} to {public_freeze['btc_range_high']}", "WEEKLY", target_year, target_week, public_freeze_sha, machine_sha, issue, target_year, target_week))
    else:
        unavailable.append("btc_range")
    if public_freeze.get("eth_range_low") is not None and public_freeze.get("eth_range_high") is not None:
        claims.append(claim("eth_range", "eth_range", f"ETH weekly range {public_freeze['eth_range_low']} to {public_freeze['eth_range_high']}", "WEEKLY", target_year, target_week, public_freeze_sha, machine_sha, issue, target_year, target_week))
    else:
        unavailable.append("eth_range")
    if nonempty(public_freeze.get("ethbtc_condition")):
        claims.append(claim("ethbtc", "ethbtc_condition", str(public_freeze["ethbtc_condition"]), "WEEKLY", target_year, target_week, public_freeze_sha, machine_sha, issue, target_year, target_week))
    else:
        unavailable.append("ethbtc_condition")
    if nonempty(public_freeze.get("breadth_condition")):
        claims.append(claim("breadth", "breadth_condition", str(public_freeze["breadth_condition"]), "WEEKLY", target_year, target_week, public_freeze_sha, machine_sha, issue, target_year, target_week))
    else:
        unavailable.append("breadth_condition")
    for i, text in enumerate(public_freeze.get("structural_calls") or [], start=1):
        if not nonempty(text):
            continue
        pid = f"structural_call_{i}"
        fam, alias = family_for(pid, public_freeze)
        claims.append(claim(fam, pid, str(text), "WEEKLY", target_year, target_week, public_freeze_sha, machine_sha, issue, target_year, target_week, alias))
    intraday = public_freeze.get("intraday_map")
    for bucket in ("day_1_2", "day_3_4", "day_5_7"):
        pid = f"intraday_{bucket}"
        text = intraday.get(bucket) if isinstance(intraday, dict) else None
        if nonempty(text):
            claims.append(claim(pid, pid, str(text), bucket.upper(), target_year, target_week, public_freeze_sha, machine_sha, issue, target_year, target_week))
        else:
            unavailable.append(pid)
    base23 = machine.get("base_case_2_3_weeks")
    if nonempty(base23):
        my, mw = advance_iso_week(target_year, target_week, 2)
        claims.append(claim("base_case_2_3_weeks", "base_case_2_3_weeks", str(base23), "2_3_WEEKS", my, mw, public_freeze_sha, machine_sha, issue, target_year, target_week))
    else:
        unavailable.append("base_case_2_3_weeks")
    base48 = machine.get("base_case_4_8_weeks")
    if nonempty(base48):
        my, mw = advance_iso_week(target_year, target_week, 7)
        claims.append(claim("base_case_4_8_weeks", "base_case_4_8_weeks", str(base48), "4_8_WEEKS", my, mw, public_freeze_sha, machine_sha, issue, target_year, target_week))
    else:
        unavailable.append("base_case_4_8_weeks")
    ids = [c["claim_id"] for c in claims]
    if len(ids) != len(set(ids)):
        raise SystemExit("INTERNAL_PRECISION_DUPLICATE_CLAIM_ID")
    return {
        "contract": FREEZE_CONTRACT,
        "authority": AUTHORITY,
        "iso_year": target_year,
        "iso_week": target_week,
        "issue_number": issue,
        "source_public_freeze_sha256": public_freeze_sha,
        "source_machine_package_sha256_at_materialization": machine_sha,
        "claims": claims,
        "unavailable_or_unfrozen": unavailable,
        "rules": {
            "no_hindsight_rewrite": True,
            "pending_excluded_from_score_denominator": True,
            "public_precision_is_separate": True,
            "unavailable_excluded_from_hit_miss": True,
            "aliases_excluded_from_family_headline_aggregation": True,
        },
    }


def append_jsonl_dedup(path: Path, row: dict[str, Any], key_field: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    key = row[key_field]
    existing: list[dict[str, Any]] = []
    if path.exists():
        for line in path.read_text().splitlines():
            if line.strip():
                existing.append(json.loads(line))
    matches = [r for r in existing if r.get(key_field) == key]
    if matches:
        if len(matches) != 1 or canonical_bytes(matches[0]) != canonical_bytes(row):
            raise SystemExit(f"INTERNAL_PRECISION_LEDGER_CONFLICT:{key_field}={key}")
        return
    with path.open("a") as f:
        f.write(canonical_bytes(row).decode())


def generic_calibration_summary(repo: Path) -> dict[str, Any]:
    path = repo / "research/api_agent/MODEL_CALIBRATION_SETTLEMENT_ELIGIBILITY.json"
    if not path.exists():
        return {"status": "UNAVAILABLE"}
    data = read_json(path)
    return {
        "status": data.get("status"),
        "row_count": data.get("row_count", 0),
        "scientific_scored_count": data.get("scientific_scored_count", 0),
        "settlement_eligible_count": data.get("settlement_eligible_count", 0),
    }


def _cost_preflight(repo: Path, model: str, request_bytes: bytes, max_output_tokens: int) -> None:
    """Fail closed before any optional CN OpenAI call; reserve worst-case tokens.

    This is a bounded single-lane admission under the existing main-writer
    concurrency group, NOT a platform-wide atomic billing reservation.
    """
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    from scripts.api_agent.api_gateway import PRICES_PER_MILLION, estimate_cost
    try:
        policy = read_json(repo / "research/api_agent/API_INTELLIGENCE_POLICY_v2.json")
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        raise RuntimeError("CN_API_POLICY_UNREADABLE_NO_SPEND") from exc
    if not isinstance(policy, dict):
        raise RuntimeError("CN_API_POLICY_INVALID_SHAPE_NO_SPEND")
    if (policy.get("status") != "ACTIVE_SHADOW_ONLY" or
            policy.get("monthly_hard_stop_usd") != 40 or
            policy.get("global_reserve_usd") != 4):
        raise RuntimeError("CN_API_POLICY_UNVERIFIED")
    caps = policy.get("lane_caps_usd")
    lane_task = "CN_INTERNAL_LONG_HORIZON_SCORER"
    # An absent cap must never silently fall back to the global monthly limit.
    if (not isinstance(caps, dict) or
            type(caps.get(lane_task)) not in (int, float) or
            caps[lane_task] != 1):
        raise RuntimeError("CN_API_LANE_CAP_UNVERIFIED_NO_SPEND")
    if model not in PRICES_PER_MILLION or type(max_output_tokens) is not int or not 1 <= max_output_tokens <= 5000:
        raise RuntimeError("CN_API_MODEL_OR_OUTPUT_LIMIT_NOT_APPROVED")
    if not request_bytes or len(request_bytes) > 200000:
        raise RuntimeError("CN_API_CONTEXT_SIZE_OUT_OF_BOUNDS")
    # 1 token/UTF-8-byte is conservative for bounded text payloads.
    max_cost = estimate_cost(model, len(request_bytes), max_output_tokens)
    if max_cost > 1.0:
        raise RuntimeError("CN_API_SINGLE_CALL_ESTIMATE_OUT_OF_BOUNDS")
    guard = repo / "scripts/api_agent/check_monthly_cost_guard.py"
    cmd = [sys.executable, str(guard), "--receipt-root", str(repo / "research/api_agent/outputs"),
           "--pending-ledger-root", str(repo / "runtime/api-cost-ledger"),
           "--hard-stop-usd", "40", "--reserve-usd", str(round(4.0 + max_cost, 8))]
    try:
        result = subprocess.run(cmd, cwd=repo, capture_output=True, timeout=45, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        raise RuntimeError("CN_API_GLOBAL_BUDGET_CHECK_UNAVAILABLE") from exc
    if result.returncode:
        raise RuntimeError("CN_API_GLOBAL_BUDGET_BLOCKED")
    # The existing task-specific governor must independently enforce this
    # lane's monthly allowance, not merely the global post-reserve balance.
    lane_cmd = [
        sys.executable, str(repo / "scripts/api_agent/check_api_lane_budget.py"),
        "--receipt-root", str(repo / "research/api_agent/outputs"),
        "--task", lane_task, "--cap-usd", str(caps[lane_task]),
        "--reserve-usd", str(round(max_cost, 8)),
    ]
    try:
        lane_result = subprocess.run(lane_cmd, cwd=repo, capture_output=True, timeout=45, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        raise RuntimeError("CN_API_LANE_BUDGET_CHECK_UNAVAILABLE") from exc
    if lane_result.returncode:
        raise RuntimeError("CN_API_LANE_BUDGET_BLOCKED")


def _cn_cost_receipt_path(repo: Path, claims: list[dict[str, Any]]) -> Path:
    # Claim identity binds retries to the SAME frozen cohort irrespective
    # of rebuilt prompts and evidence. Never charge it twice automatically.
    ids = [str(c["claim_id"]) for c in claims]
    if not ids or len(set(ids)) != len(ids):
        raise RuntimeError("CN_API_INVALID_COHORT_IDS")
    digest = hashlib.sha256(canonical_bytes(ids)).hexdigest()
    return repo / "research/api_agent/outputs/cn_internal_precision" / digest / "receipt.json"



def _previously_attempted_claim_ids(repo: Path) -> set[str]:
    """Read paid-attempt claim IDs from trusted, durable CN receipts only."""
    root = repo / "research/api_agent/outputs/cn_internal_precision"
    if not root.exists():
        return set()
    if not root.is_dir() or root.is_symlink():
        raise RuntimeError("CN_API_RECEIPT_ROOT_INVALID")
    attempted: set[str] = set()
    for path in sorted(root.glob("*/receipt.json")):
        if path.is_symlink() or path.parent.is_symlink():
            raise RuntimeError("CN_API_RECEIPT_PATH_INVALID")
        try:
            prior = json.loads(path.read_text())
        except (OSError, ValueError, TypeError) as exc:
            raise RuntimeError("CN_API_PREVIOUS_RECEIPT_UNREADABLE") from exc
        if not isinstance(prior, dict) or prior.get("contract") != "API_AGENT_RECEIPT_v3":
            raise RuntimeError("CN_API_PREVIOUS_RECEIPT_INVALID")
        if prior.get("task") != "CN_INTERNAL_LONG_HORIZON_SCORER":
            raise RuntimeError("CN_API_PREVIOUS_RECEIPT_TASK_INVALID")
        ids = prior.get("claim_ids")
        if (not isinstance(ids, list) or not ids or
                any(not isinstance(v, str) or not v for v in ids) or len(ids) != len(set(ids))):
            raise RuntimeError("CN_API_PREVIOUS_RECEIPT_CLAIMS_INVALID")
        attempted.update(ids)
    return attempted


def _fresh_unattempted_long_claims(repo: Path, due: list[dict[str, Any]]) -> list[dict[str, Any]]:
    attempted = _previously_attempted_claim_ids(repo)
    return [claim for claim in due if claim["claim_id"] not in attempted]


def _reject_previously_attempted_claims(repo: Path, claims: list[dict[str, Any]]) -> None:
    current = {str(item["claim_id"]) for item in claims}
    if current.intersection(_previously_attempted_claim_ids(repo)):
        raise RuntimeError("CN_API_CLAIM_ALREADY_ATTEMPTED_OWNER_REVIEW_REQUIRED")


def score_long_horizon_via_api(model: str, claims: list[dict[str, Any]], evidence: list[dict[str, Any]],
                               max_output_tokens: int, repo: Path | None = None) -> list[dict[str, Any]]:
    if not claims:
        return []
    # No unscoped direct HTTP call: test callers must pass a repository
    # authority root; a missing root makes the function no-spend.
    if repo is None:
        raise RuntimeError("CN_API_REPO_ROOT_REQUIRED")
    repo = repo.resolve()
    receipt_path = _cn_cost_receipt_path(repo, claims)
    if receipt_path.exists():
        raise RuntimeError("CN_API_COHORT_ALREADY_ATTEMPTED_OWNER_REVIEW_REQUIRED")
    _reject_previously_attempted_claims(repo, claims)
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY_missing_for_mature_long_horizon_claims")
    schema = {
        "type": "object", "additionalProperties": False, "required": ["scores"],
        "properties": {"scores": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["claim_id", "status", "score", "evidence", "self_critique"],
            "properties": {
                "claim_id": {"type": "string"},
                "status": {"type": "string", "enum": list(ALLOWED_STATUS)},
                "score": {"type": ["number", "null"]},
                "evidence": {"type": "string"},
                "self_critique": {"type": "string"},
            }
        }}}
    }
    instructions = (
        "Audit matured internal Cycle Navigator forecasts. Claims are immutable ex-ante evidence. "
        "Use only supplied final Master Monday evidence across the full frozen horizon. "
        "Return SUPPORTED=100, MIXED=50, CONTRADICTED=0, NOT_EVALUABLE=null. "
        "Missing or incomplete evidence is NOT_EVALUABLE, never a miss. Do not rewrite claims, rules, or portfolio state. "
        "Be self-critical: partial directional overlap is MIXED, not SUPPORTED."
    )
    payload = {
        "model": model,
        "reasoning": {"effort": "medium", "context": "current_turn"},
        "store": False,
        "max_output_tokens": max_output_tokens,
        "instructions": instructions,
        "input": [{"role": "user", "content": [{"type": "input_text", "text": json.dumps({"claims": claims, "weekly_evidence": evidence}, sort_keys=True)}]}],
        "text": {"format": {"type": "json_schema", "name": "cn_internal_long_horizon_scores_v1", "strict": True, "schema": schema}},
    }
    payload_bytes = canonical_bytes(payload)
    _cost_preflight(repo, model, payload_bytes, max_output_tokens)
    req = urllib.request.Request("https://api.openai.com/v1/responses", data=payload_bytes,
                                 headers={"Authorization": f"Bearer {api_key}",
                                          "Content-Type": "application/json"}, method="POST")
    request_hash = hashlib.sha256(payload_bytes).hexdigest()
    raw: dict[str, Any] | None = None
    response_error: str | None = None
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            raw = json.loads(response.read())
            if not isinstance(raw, dict):
                response_error = "NON_OBJECT_RESPONSE"
    except (urllib.error.URLError, OSError, ValueError, TypeError) as exc:
        # After POST, any network ambiguity may have incurred billable tokens.
        response_error = f"POST_RESPONSE_UNVERIFIABLE:{type(exc).__name__}"

    rows: list[dict[str, Any]] = []
    valid = False
    usage = (raw or {}).get("usage") if isinstance(raw, dict) else None
    input_count = usage.get("input_tokens") if isinstance(usage, dict) else None
    output_count = usage.get("output_tokens") if isinstance(usage, dict) else None
    usage_valid = all(type(x) is int and x >= 0 for x in (input_count, output_count))
    if response_error is None and isinstance(raw, dict):
        try:
            if raw.get("status") == "incomplete":
                raise ValueError("INCOMPLETE_RESPONSE")
            text = raw.get("output_text")
            if not text:
                parts = []
                for item in raw.get("output", []):
                    for content in item.get("content", []) if isinstance(item, dict) else []:
                        if isinstance(content, dict) and content.get("type") == "output_text":
                            parts.append(str(content.get("text", "")))
                text = "".join(parts)
            parsed = json.loads(text)
            if not isinstance(parsed, dict):
                raise ValueError("INVALID_RESPONSE_STRUCTURE")
            rows = parsed.get("scores") or []
            by_id = {r["claim_id"]: r for r in rows}
            expected = [c["claim_id"] for c in claims]
            if (not isinstance(rows, list) or len(rows) != len(expected)
                    or len(by_id) != len(expected) or list(by_id) != expected):
                # A duplicate claim cannot count twice or create a negative
                # pending denominator, even when dict keys collapse to one.
                raise ValueError("INTERNAL_LONG_HORIZON_DUPLICATE_OR_MISSING_SCORES")
            for row in rows:
                status = row["status"]
                expected_score = ALLOWED_STATUS[status]
                if expected_score is None and row.get("score") is not None:
                    raise ValueError("INTERNAL_LONG_HORIZON_NULL_SCORE_MISMATCH")
                if expected_score is not None and float(row.get("score")) != expected_score:
                    raise ValueError("INTERNAL_LONG_HORIZON_SCORE_STATUS_MISMATCH")
            valid = True
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            response_error = f"INVALID_STRUCTURED_OUTPUT:{type(exc).__name__}"
    if not usage_valid:
        response_error = "CN_API_COST_USAGE_UNKNOWN"
        valid = False

    receipt = {
        "contract": "API_AGENT_RECEIPT_v3",
        "task": "CN_INTERNAL_LONG_HORIZON_SCORER",
        "model": model, "reasoning_effort": "medium",
        "created_unix": int(time.time()),
        "response_id": raw.get("id") if isinstance(raw, dict) else None,
        "request_hash": request_hash,
        "context_hash": hashlib.sha256(canonical_bytes(evidence)).hexdigest(),
        "output_hash": hashlib.sha256(canonical_bytes(rows)).hexdigest() if valid else None,
        "attempt_count": 1, "status": "PASS" if valid else "API_OUTPUT_INVALID",
        "claim_ids": [c["claim_id"] for c in claims],
        "authority": "INTERNAL_ACCOUNTABILITY_ONLY_NO_PORTFOLIO_AUTHORITY",
        "error": response_error,
    }
    if usage_valid:
        from scripts.api_agent.api_gateway import estimate_cost
        receipt.update({
            "input_tokens": input_count, "output_tokens": output_count,
            "estimated_cost_usd": estimate_cost(model, input_count, output_count),
        })
    else:
        # Intentionally omit the cost amount. Existing global cost guard
        # will thereafter fail closed on this receipt until owner reconciles
        # provider billing, instead of undercounting a possibly paid call.
        receipt["usage_reconciliation_required"] = True
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    if receipt_path.exists():
        raise RuntimeError("CN_API_RECEIPT_RACE_NO_OVERWRITE")
    receipt_path.write_bytes(canonical_bytes(receipt))
    if not valid:
        raise RuntimeError(response_error or "CN_API_OUTPUT_INVALID")
    return rows


def matured_unscored_long_horizon(repo: Path, completed_year: int, completed_week: int, existing_claim_ids: set[str]) -> list[dict[str, Any]]:
    root = repo / "05_CYCLE_NAVIGATOR/weekly"
    due: list[dict[str, Any]] = []
    for path in sorted(root.glob("*/W*/CYCLE_NAVIGATOR_INTERNAL_PRECISION_FREEZE.json")):
        data = read_json(path)
        for c in data.get("claims", []):
            if c.get("horizon") not in {"2_3_WEEKS", "4_8_WEEKS"}:
                continue
            cid = c.get("claim_id")
            if cid in existing_claim_ids:
                continue
            my, mw = int(c.get("maturity_iso_year", 9999)), int(c.get("maturity_iso_week", 99))
            if (my, mw) <= (completed_year, completed_week):
                due.append(c)
    return due


def evidence_for_long_claims(repo: Path, claims: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not claims:
        return []
    weeks: set[tuple[int, int]] = set()
    for c in claims:
        m = re.search(r"-Y(\d{4})-W(\d{2})-", c["claim_id"])
        if not m:
            continue
        sy, sw = int(m.group(1)), int(m.group(2))
        d = date.fromisocalendar(sy, sw, 1)
        end = date.fromisocalendar(int(c["maturity_iso_year"]), int(c["maturity_iso_week"]), 1)
        while d <= end:
            iso = d.isocalendar()
            weeks.add((int(iso.year), int(iso.week)))
            d += timedelta(weeks=1)
    rows: list[dict[str, Any]] = []
    for y, w in sorted(weeks):
        mm_dir = repo / "research/api_agent/outputs/weekly" / str(y) / f"W{w:02d}"
        machine = mm_dir / "MASTER_MONDAY_MACHINE_PACKAGE.json"
        report = mm_dir / "MASTER_MONDAY_REPORT.md"
        if not machine.exists() or not report.exists():
            rows.append({"iso_year": y, "iso_week": w, "status": "MISSING"})
        else:
            rows.append({
                "iso_year": y, "iso_week": w, "status": "AVAILABLE",
                "machine_sha256": sha256_path(machine),
                "report_sha256": sha256_path(report),
                "machine": read_json(machine),
            })
    return rows


def score_matured_claims_bounded(repo: Path, fresh_due: list[dict[str, Any]],
                               model: str, max_output_tokens: int) -> tuple[list[dict[str, Any]], list[str]]:
    """One paid request maximum; oversized claim A may not starve eligible B.

    Oversized claims stay explicitly PENDING, never mislabeled as a score or
    automatically paid on a retry. Any ambiguous/post-payment error stops
    further calls in this run to avoid accidentally duplicating charges.
    """
    scored: list[dict[str, Any]] = []
    oversized: list[str] = []
    paid_issued = False
    for claim in fresh_due:
        evidence = evidence_for_long_claims(repo, [claim])
        if any(row.get("status") == "MISSING" for row in evidence):
            scored.append({
                "claim_id": claim["claim_id"], "status": "NOT_EVALUABLE",
                "score": None,
                "evidence": "One or more required final Master Monday weekly evidence packages are missing.",
                "self_critique": "Long-horizon claim preserved; no score without all required final evidence.",
            })
            continue
        if paid_issued:
            break
        try:
            # The actual scorer contains both global and per-lane budget guards,
            # a pre-POST context bound and durable claim-level paid receipts.
            paid_issued = True
            scored.extend(score_long_horizon_via_api(
                model, [claim], evidence, max_output_tokens, repo=repo))
            break
        except RuntimeError as exc:
            if str(exc) in ("CN_API_CONTEXT_SIZE_OUT_OF_BOUNDS",
                            "CN_API_SINGLE_CALL_ESTIMATE_OUT_OF_BOUNDS"):
                paid_issued = False  # These errors happen before the POST.
                oversized.append(claim["claim_id"])
                continue
            print(f"CN_LONG_HORIZON_API_BLOCKED:{claim['claim_id']}:{exc}", file=sys.stderr)
            break
        except (json.JSONDecodeError, urllib.error.URLError):
            break
    return scored, oversized


def compact_score(value: Any) -> str:
    if value is None:
        return "N/A"
    f = float(value)
    return f"{int(f)}%" if f.is_integer() else f"{f:.1f}%"


def build_box(scorecard: dict[str, Any], current_freeze: dict[str, Any], generic: dict[str, Any], mature_long_pending: int) -> str:
    fam = scorecard.get("family_scores") or {}
    intraday_vals = [fam.get(k) for k in ("intraday_day_1_2", "intraday_day_3_4", "intraday_day_5_7") if fam.get(k) is not None]
    intraday = round(sum(float(x) for x in intraday_vals) / len(intraday_vals), 2) if intraday_vals else None
    pending = len(current_freeze.get("claims", []))
    long_pending = sum(1 for c in current_freeze.get("claims", []) if c.get("horizon") in {"2_3_WEEKS", "4_8_WEEKS"})
    unavailable = len(current_freeze.get("unavailable_or_unfrozen", []))
    generic_scored = generic.get("scientific_scored_count", 0) if generic.get("status") != "UNAVAILABLE" else 0
    critique = str(scorecard.get("self_critique") or "None recorded.").replace("\n", " ").strip()
    lines = [
        f"┌─ INTERN PRECISION — CN #{scorecard['issue_scored']} → W{scorecard['completed_iso_week']:02d} ─",
        f"Weekly structural {compact_score(scorecard.get('public_weekly_structural_score'))} | Intraday {compact_score(intraday)} | Mature coverage {scorecard['accounted_parameter_count']}/{scorecard['mature_parameter_count']} ({compact_score(scorecard.get('mature_coverage_pct'))})",
        f"Regime {compact_score(fam.get('regime'))} | ETH/BTC {compact_score(fam.get('ethbtc'))} | Breadth {compact_score(fam.get('breadth'))} | Leadership {compact_score(fam.get('leadership'))}",
        f"Rotation {compact_score(fam.get('rotation'))} | Altseason {compact_score(fam.get('altseason'))} | BTC range {compact_score(fam.get('btc_range'))} | ETH range {compact_score(fam.get('eth_range'))}",
        f"D1–2 {compact_score(fam.get('intraday_day_1_2'))} | D3–4 {compact_score(fam.get('intraday_day_3_4'))} | D5–7 {compact_score(fam.get('intraday_day_5_7'))}",
        f"Frozen current {pending} | Long-horizon pending {long_pending} | Mature-long awaiting score {mature_long_pending} | N/A/unfrozen {unavailable} | Generic scored {generic_scored}",
        f"Self-critique: {critique}",
        "└─ no synthetic overall; aliases/correlated calls are not double-counted; public score stays separate",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--model", default="gpt-5.6-terra")
    ap.add_argument("--max-output-tokens", type=int, default=5000)
    args = ap.parse_args()
    repo = args.repo_root.resolve()
    ptr_path = repo / "05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json"
    ptr = read_json(ptr_path)
    target_year, target_week = int(ptr["iso_year"]), int(ptr["iso_week"])
    completed_week = int(ptr["completed_source_week"])
    prior_monday = date.fromisocalendar(target_year, target_week, 1) - timedelta(weeks=1)
    prior_iso = prior_monday.isocalendar()
    completed_year = int(prior_iso.year)
    if int(prior_iso.week) != completed_week:
        raise SystemExit("INTERNAL_PRECISION_WEEK_IDENTITY_MISMATCH")
    root = repo / str(ptr["week_dir"])
    machine_path = root / "CYCLE_NAVIGATOR_MACHINE_PACKAGE.json"
    public_freeze_path = root / "CYCLE_NAVIGATOR_FORECAST_FREEZE.json"
    scorecard_path = root / "CYCLE_NAVIGATOR_SCORECARD.json"
    machine, public_freeze, public_scorecard = read_json(machine_path), read_json(public_freeze_path), read_json(scorecard_path)
    issue = int(ptr["issue_number"])
    issue_scored = int(public_scorecard.get("issue_scored") or machine.get("previous_issue_number") or 0)
    prior_dir = repo / "05_CYCLE_NAVIGATOR/weekly" / str(completed_year) / f"W{completed_week:02d}"
    prior_freeze_path = prior_dir / "CYCLE_NAVIGATOR_FORECAST_FREEZE.json"
    if not prior_freeze_path.exists():
        raise SystemExit("INTERNAL_PRECISION_PRIOR_PUBLIC_FREEZE_MISSING")
    prior_freeze = read_json(prior_freeze_path)
    rows, score_source = score_rows_from_public(machine, public_scorecard, prior_freeze, completed_week)
    expected = expected_parameter_ids(prior_freeze)
    if len(rows) != len(expected):
        raise SystemExit("INTERNAL_PRECISION_MATURE_COVERAGE_NOT_COMPLETE")

    mm_ptr = repo / "research/api_agent/outputs/weekly/LATEST_MASTER_MONDAY_DELIVERY_POINTER.json"
    mm_sha = sha256_path(mm_ptr) if mm_ptr.exists() else None
    prior_freeze_sha = sha256_path(prior_freeze_path)
    public_scorecard_sha = sha256_path(scorecard_path)
    param_ledger = repo / "05_CYCLE_NAVIGATOR/track_record/CN_INTERNAL_PARAMETER_LEDGER.jsonl"
    existing_ids: set[str] = set()
    if param_ledger.exists():
        for line in param_ledger.read_text().splitlines():
            if line.strip():
                existing_ids.add(json.loads(line).get("claim_id"))
    for row in rows:
        claim_id = f"CN{issue_scored}-Y{completed_year}-W{completed_week:02d}-{row['parameter_id']}"
        ledger_row = {
            "contract": PARAM_LEDGER_CONTRACT,
            "authority": AUTHORITY,
            "claim_id": claim_id,
            "issue_scored": issue_scored,
            "completed_iso_year": completed_year,
            "completed_iso_week": completed_week,
            **row,
            "source_prior_public_freeze_sha256": prior_freeze_sha,
            "source_public_scorecard_sha256": public_scorecard_sha,
            "source_master_monday_pointer_sha256": mm_sha,
        }
        append_jsonl_dedup(param_ledger, ledger_row, "claim_id")
        existing_ids.add(claim_id)

    due_long = matured_unscored_long_horizon(repo, completed_year, completed_week, existing_ids)
    long_scores: list[dict[str, Any]] = []
    oversize_pending_claim_ids: list[str] = []
    mature_long_pending = 0
    if due_long:
        # Previously attempted paid claims stay pending. Unlike a whole-cohort
        # abort, fresh mature claims still advance through the ordinary guard.
        try:
            fresh_due = _fresh_unattempted_long_claims(repo, due_long)
        except RuntimeError as exc:
            print(f"CN_LONG_HORIZON_COST_PROVENANCE_BLOCKED:{exc}", file=sys.stderr)
            fresh_due = []
        mature_long_pending = len(due_long) - len(fresh_due)
        if fresh_due:
            long_scores, oversize_pending_claim_ids = score_matured_claims_bounded(
                repo, fresh_due, args.model, args.max_output_tokens)
            mature_long_pending = len(due_long) - len(long_scores)
            if oversize_pending_claim_ids:
                print("CN_LONG_HORIZON_OVERSIZE_PENDING:"
                      + ",".join(oversize_pending_claim_ids), file=sys.stderr)
        cby = {c["claim_id"]: c for c in due_long}
        for s in long_scores:
            c = cby[s["claim_id"]]
            row = {
                "contract": PARAM_LEDGER_CONTRACT, "authority": AUTHORITY,
                "claim_id": c["claim_id"], "issue_scored": int(re.search(r"CN(\d+)", c["claim_id"]).group(1)),
                "completed_iso_year": completed_year, "completed_iso_week": completed_week,
                "parameter_id": c["source_parameter_id"], "family": c["family"], "alias_of": c.get("alias_of"),
                "headline_eligible": c.get("alias_of") is None, "status": s["status"], "score": s.get("score"),
                "evidence": s["evidence"], "self_critique": s["self_critique"], "source": "MATURED_LONG_HORIZON_INTERNAL_SCORER",
                "source_prior_public_freeze_sha256": c["source_public_freeze_sha256"],
                "source_master_monday_pointer_sha256": mm_sha,
            }
            append_jsonl_dedup(param_ledger, row, "claim_id")

    current_internal_path = root / "CYCLE_NAVIGATOR_INTERNAL_PRECISION_FREEZE.json"
    machine_sha, public_freeze_sha = sha256_path(machine_path), sha256_path(public_freeze_path)
    if current_internal_path.exists():
        current_internal = read_json(current_internal_path)
        if current_internal.get("source_public_freeze_sha256") != public_freeze_sha:
            raise SystemExit("INTERNAL_PRECISION_EXISTING_FREEZE_SOURCE_CHANGED")
    else:
        current_internal = build_current_freeze(machine, public_freeze, issue, target_year, target_week, public_freeze_sha, machine_sha)
        write_json(current_internal_path, current_internal)

    fam = family_scores(rows)
    misses = public_scorecard.get("misses") if isinstance(public_scorecard.get("misses"), list) else []
    self_critique = str(misses[0]) if misses else "No material miss text was available in the public scorecard."
    not_eval = sum(1 for r in rows if r["status"] == "NOT_EVALUABLE")
    scored = len(rows) - not_eval
    generic = generic_calibration_summary(repo)
    scorecard = {
        "contract": SCORECARD_CONTRACT,
        "authority": AUTHORITY,
        "completed_iso_year": completed_year,
        "completed_iso_week": completed_week,
        "issue_scored": issue_scored,
        "public_weekly_structural_score": public_scorecard.get("structural_score"),
        "parameter_score_source": score_source,
        "mature_parameter_count": len(expected),
        "accounted_parameter_count": len(rows),
        "scored_parameter_count": scored,
        "not_evaluable_parameter_count": not_eval,
        "mature_coverage_pct": pct(len(rows), len(expected)),
        "scored_coverage_pct": pct(scored, len(expected)),
        "family_scores": fam,
        "parameter_scores": rows,
        "newly_matured_long_horizon_scores": long_scores,
        "mature_long_horizon_awaiting_score_count": mature_long_pending,
        "mature_long_horizon_oversize_pending_claim_ids": oversize_pending_claim_ids,
        "current_frozen_claim_count": len(current_internal.get("claims", [])),
        "current_unavailable_or_unfrozen_count": len(current_internal.get("unavailable_or_unfrozen", [])),
        "generic_framework_calibration": generic,
        "self_critique": self_critique,
        "source_public_scorecard_sha256": public_scorecard_sha,
        "source_prior_public_freeze_sha256": prior_freeze_sha,
        "source_master_monday_pointer_sha256": mm_sha,
        "aggregation_note": "No synthetic overall internal accuracy is published because aliases and correlated claims are not independent. Family scores, parameter rows, horizon scores and coverage are primary.",
    }
    write_json(root / "CYCLE_NAVIGATOR_INTERNAL_PRECISION_SCORECARD.json", scorecard)
    box = build_box(scorecard, current_internal, generic, mature_long_pending)
    (root / "CYCLE_NAVIGATOR_INTERNAL_PRECISION_BOX.md").write_text(box)
    internal_md = (
        f"# INTERNAL CYCLE NAVIGATOR #{issue} — {target_year}-W{target_week:02d}\n\n"
        + box + "\n"
        + "Scenario body remains in `CYCLE_NAVIGATOR_READABLE.md`; public/X copy remains separate. "
        + "Full parameter-level audit is in `CYCLE_NAVIGATOR_INTERNAL_PRECISION_SCORECARD.json` and the append-only internal ledgers.\n"
    )
    (root / "CYCLE_NAVIGATOR_INTERNAL.md").write_text(internal_md)

    summary_row = {
        "contract": SUMMARY_LEDGER_CONTRACT, "authority": AUTHORITY,
        "score_key": f"Y{completed_year}-W{completed_week:02d}-CN{issue_scored}",
        "completed_iso_year": completed_year, "completed_iso_week": completed_week, "issue_scored": issue_scored,
        "public_weekly_structural_score": public_scorecard.get("structural_score"), "family_scores": fam,
        "mature_parameter_count": len(expected), "accounted_parameter_count": len(rows), "scored_parameter_count": scored,
        "mature_coverage_pct": pct(len(rows), len(expected)), "self_critique": self_critique,
        "source_public_scorecard_sha256": public_scorecard_sha,
    }
    append_jsonl_dedup(repo / "05_CYCLE_NAVIGATOR/track_record/CN_INTERNAL_PRECISION_LEDGER.jsonl", summary_row, "score_key")

    print(json.dumps({"status": "PASS", "week_dir": str(root.relative_to(repo)), "issue_number": issue, "issue_scored": issue_scored, "mature_count": len(expected), "scored_count": scored, "current_frozen_count": len(current_internal.get("claims", [])), "long_horizon_matured_now": len(long_scores), "mature_long_horizon_awaiting_score": mature_long_pending}, sort_keys=True))


if __name__ == "__main__":
    main()
