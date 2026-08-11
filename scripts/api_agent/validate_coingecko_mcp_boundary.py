#!/usr/bin/env python3
"""Deterministic boundary checks for the opt-in CoinGecko MCP research sidecar."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List

CONTRACT_PATH = Path("research/api_agent/mcp/COINGECKO_MCP_RESEARCH_RECOVERY_v1.json")
EXAMPLE_PATH = Path("research/api_agent/mcp/coingecko_mcp_research_recovery.example.json")
EXPECTED_ENDPOINT = "https://mcp.api.coingecko.com/mcp"
EXPECTED_FORBIDDEN_PREFIXES = {
    "01_CORE_FRAMEWORK/",
    "02_DATA_PING/",
    "03_DAILY_CAPTURE_LOGS/",
    "03_WEEKLY_OPERATIONS/",
    "05_CYCLE_NAVIGATOR/",
}
ROOT_AUTO_ACTIVATION_PATHS = (Path(".mcp.json"), Path("mcp_config.json"))


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_boundary(root: Path = Path(".")) -> List[str]:
    root = root.resolve()
    errors: List[str] = []

    contract_file = root / CONTRACT_PATH
    example_file = root / EXAMPLE_PATH

    if not contract_file.is_file():
        return [f"missing_contract:{CONTRACT_PATH}"]
    if not example_file.is_file():
        return [f"missing_example:{EXAMPLE_PATH}"]

    try:
        contract = _load_json(contract_file)
    except Exception as exc:  # pragma: no cover - defensive parse receipt
        return [f"invalid_contract_json:{exc}"]

    try:
        example = _load_json(example_file)
    except Exception as exc:  # pragma: no cover - defensive parse receipt
        return [f"invalid_example_json:{exc}"]

    if contract.get("contract") != "COINGECKO_MCP_RESEARCH_RECOVERY_v1":
        errors.append("contract_identity_mismatch")
    if contract.get("status") != "OPERATIONAL_OPT_IN":
        errors.append("sidecar_not_opt_in")

    transport = contract.get("transport", {})
    if transport.get("endpoint") != EXPECTED_ENDPOINT:
        errors.append("unexpected_mcp_endpoint")
    if transport.get("endpoint_class") != "KEYLESS_PUBLIC":
        errors.append("unexpected_endpoint_class")
    if transport.get("auto_activate_repository_root") is not False:
        errors.append("repository_root_auto_activation_enabled")

    authority = contract.get("authority", {})
    if not authority:
        errors.append("authority_block_missing")
    else:
        enabled = sorted(key for key, value in authority.items() if value is not False)
        if enabled:
            errors.append("nonzero_authority:" + ",".join(enabled))

    if contract.get("canonical_owner_replacement") is not False:
        errors.append("canonical_owner_replacement_enabled")
    if contract.get("production_dependency") is not False:
        errors.append("production_dependency_enabled")

    forbidden = set(contract.get("forbidden_write_prefixes", []))
    missing_forbidden = sorted(EXPECTED_FORBIDDEN_PREFIXES - forbidden)
    if missing_forbidden:
        errors.append("missing_forbidden_prefixes:" + ",".join(missing_forbidden))

    for relative in ROOT_AUTO_ACTIVATION_PATHS:
        if (root / relative).exists():
            errors.append(f"root_auto_activation_present:{relative}")

    servers = example.get("mcpServers", {})
    if set(servers) != {"coingecko_mcp_research_recovery"}:
        errors.append("example_server_identity_mismatch")
    else:
        server = servers["coingecko_mcp_research_recovery"]
        if server.get("command") != "npx":
            errors.append("example_command_mismatch")
        args = server.get("args", [])
        if args != ["mcp-remote", EXPECTED_ENDPOINT]:
            errors.append("example_args_mismatch")

    operational_doc = contract.get("operational_doc")
    if not operational_doc or not (root / operational_doc).is_file():
        errors.append("operational_doc_missing")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."), help="Repository root")
    args = parser.parse_args()

    errors = validate_boundary(args.root)
    if errors:
        print("COINGECKO_MCP_BOUNDARY_FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("COINGECKO_MCP_BOUNDARY_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
