from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROGRAM_PATH = Path("research/api_agent/mcp/MCP_CONNECTION_EVALUATION_PROGRAM_v1.json")
EXPECTED_QUEUE = ["Dune", "LunarCrush", "CoinMarketCap", "TheGraph", "altFINS", "Binance"]
AUTHORITY_KEYS = {
    "canonical_data_owner",
    "framework_state_change",
    "portfolio_action",
    "market_rule_change",
    "threshold_change",
    "weight_change",
    "policy_semantics_change",
    "master_monday_authority",
    "data_ping_authority",
    "weekly_backbone_authority",
    "cycle_navigator_authority",
    "new_engine",
    "new_sensor",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def validate_provider(root: Path, entry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    path = root / entry["contract_path"]
    if not path.exists():
        return [f"missing_provider_contract:{entry['provider']}:{entry['contract_path']}"]
    data = load_json(path)
    provider = entry["provider"]
    if data.get("provider") != provider:
        errors.append(f"provider_mismatch:{provider}")
    authority = data.get("authority")
    if not isinstance(authority, dict):
        errors.append(f"authority_missing:{provider}")
    else:
        missing = AUTHORITY_KEYS - set(authority)
        if missing:
            errors.append(f"authority_keys_missing:{provider}:{','.join(sorted(missing))}")
        for key in AUTHORITY_KEYS & set(authority):
            if authority[key] is not False:
                errors.append(f"authority_not_false:{provider}:{key}")
    if data.get("canonical_owner_replacement") is not False:
        errors.append(f"canonical_owner_replacement_not_false:{provider}")
    if data.get("production_dependency") is not False:
        errors.append(f"production_dependency_not_false:{provider}")
    if data.get("provider_payment_or_write_actions_allowed") is not False:
        errors.append(f"provider_write_or_payment_not_false:{provider}")
    if data.get("source_context_until_promoted") is not True:
        errors.append(f"source_context_gate_missing:{provider}")
    if data.get("require_read_only_hint_for_execution") is not True:
        errors.append(f"read_only_hint_gate_missing:{provider}")
    fragments = data.get("forbidden_tool_name_fragments")
    if not isinstance(fragments, list) or not fragments:
        errors.append(f"forbidden_tool_fragments_missing:{provider}")
    transport = data.get("transport") if isinstance(data.get("transport"), dict) else {}
    if provider == "Binance":
        if data.get("status") != "BLOCKED_OFFICIAL_MCP_SURFACE_UNVERIFIED":
            errors.append("binance_must_remain_blocked_until_surface_verified")
        if transport.get("server_url") is not None:
            errors.append("binance_unverified_server_url_must_be_null")
        auth = transport.get("auth") if isinstance(transport.get("auth"), dict) else {}
        if auth.get("api_key_allowed_for_pilot") is not False or auth.get("account_auth_allowed") is not False or auth.get("trade_permission_allowed") is not False:
            errors.append("binance_public_only_boundary_invalid")
    else:
        if not str(transport.get("server_url") or "").startswith("https://"):
            errors.append(f"verified_https_server_required:{provider}")
        auth = transport.get("auth") if isinstance(transport.get("auth"), dict) else {}
        if auth.get("secret_must_not_be_persisted") is not True:
            errors.append(f"secret_persistence_guard_missing:{provider}")
    if provider == "CoinMarketCap" and transport.get("x402_endpoint_allowed") is not False:
        errors.append("cmc_x402_must_be_disabled")
    if provider == "altFINS" and data.get("provider_derived_signals_are_decision_evidence") is not False:
        errors.append("altfins_provider_signals_must_not_be_decision_evidence")
    if provider == "Dune" and data.get("provider_surface_may_include_mutations") is not True:
        errors.append("dune_mutating_surface_risk_must_be_explicit")
    return errors


def validate_program(root: Path) -> list[str]:
    errors: list[str] = []
    path = root / PROGRAM_PATH
    if not path.exists():
        return [f"missing_program:{PROGRAM_PATH}"]
    data = load_json(path)
    if data.get("contract") != "MCP_CONNECTION_EVALUATION_PROGRAM_v1":
        errors.append("invalid_program_contract")
    if data.get("status") != "OPERATIONAL_SEQUENTIAL_PILOT":
        errors.append("invalid_program_status")
    execution = data.get("execution") if isinstance(data.get("execution"), dict) else {}
    if execution.get("sequential") is not True or execution.get("max_active_provider_trials") != 1:
        errors.append("sequential_single_active_trial_required")
    for key in ("automatic_market_semantics_change", "automatic_canonical_owner_replacement", "automatic_portfolio_action"):
        if execution.get(key) is not False:
            errors.append(f"unsafe_execution_flag:{key}")
    authority = data.get("authority") if isinstance(data.get("authority"), dict) else {}
    for key, value in authority.items():
        if key == "creates_truth" and value is not False:
            errors.append("program_creates_truth_must_be_false")
        elif key != "creates_truth" and value is not False:
            errors.append(f"program_authority_not_false:{key}")
    queue = data.get("queue") if isinstance(data.get("queue"), list) else []
    providers = [item.get("provider") for item in queue]
    if providers != EXPECTED_QUEUE:
        errors.append("provider_queue_order_mismatch")
    ranks = [item.get("rank") for item in queue]
    if ranks != list(range(1, len(EXPECTED_QUEUE) + 1)):
        errors.append("provider_queue_ranks_invalid")
    if data.get("score", {}).get("hard_blocker_overrides_score") is not True:
        errors.append("hard_blocker_must_override_score")
    ai_review = data.get("ai_review") if isinstance(data.get("ai_review"), dict) else {}
    if ai_review.get("required") is not True or ai_review.get("cannot_override_hard_blocker") is not True:
        errors.append("ai_review_boundary_invalid")
    for entry in queue:
        errors.extend(validate_provider(root, entry))
    baseline_path = root / str(data.get("baseline", {}).get("contract_path") or "")
    if not baseline_path.exists():
        errors.append("coingecko_baseline_contract_missing")
    for forbidden in (root / ".mcp.json", root / "mcp_config.json"):
        if forbidden.exists():
            errors.append(f"forbidden_root_activation_present:{forbidden.name}")
    schema = root / str(data.get("pilot_receipt_schema") or "")
    scorecard = root / str(data.get("scorecard") or "")
    if not schema.exists():
        errors.append("pilot_receipt_schema_missing")
    if not scorecard.exists():
        errors.append("scorecard_missing")
    return errors


def main() -> None:
    errors = validate_program(Path("."))
    if errors:
        for error in errors:
            print(error)
        raise SystemExit(1)
    print("MCP_CONNECTION_PROGRAM_PASS")


if __name__ == "__main__":
    main()
