from __future__ import annotations

from copy import deepcopy
from typing import Any
from urllib.parse import urlparse


def resolve_mcp_server_url(contract: dict[str, Any]) -> str:
    transport = contract.get("transport") if isinstance(contract.get("transport"), dict) else {}
    server_url = transport.get("server_url")
    endpoint = transport.get("endpoint")
    if server_url and endpoint and str(server_url) != str(endpoint):
        raise ValueError("mcp_transport_url_conflict")
    value = str(server_url or endpoint or "")
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("verified_https_mcp_server_required")
    return value


def normalize_mcp_contract(contract: dict[str, Any]) -> dict[str, Any]:
    normalized = deepcopy(contract)
    transport = normalized.setdefault("transport", {})
    if not isinstance(transport, dict):
        raise ValueError("transport_object_required")
    transport["server_url"] = resolve_mcp_server_url(contract)
    return normalized
