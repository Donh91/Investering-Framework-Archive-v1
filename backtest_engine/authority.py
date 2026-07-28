from __future__ import annotations

REQUIRED_CONTRACT_KEYS = {
    "minimum_overlap_sessions",
    "median_abs_close_dev_bps_max",
    "p95_abs_close_dev_bps_max",
    "max_abs_close_dev_bps_max",
    "gate_agreement_rate_min",
}


def validate_direct_challenger(metrics: dict, contract: dict) -> dict:
    missing = REQUIRED_CONTRACT_KEYS - set(contract)
    if missing:
        raise ValueError(f"contract missing keys: {sorted(missing)}")
    checks = {
        "minimum_overlap": metrics["overlap_rows"] >= contract["minimum_overlap_sessions"],
        "median_close": metrics["median_abs_close_dev_bps"] <= contract["median_abs_close_dev_bps_max"],
        "p95_close": metrics["p95_abs_close_dev_bps"] <= contract["p95_abs_close_dev_bps_max"],
        "max_close": metrics["max_abs_close_dev_bps"] <= contract["max_abs_close_dev_bps_max"],
        "gate_0_0275": metrics["gate_agreement_rate_0_0275"] >= contract["gate_agreement_rate_min"],
        "gate_0_0300": metrics["gate_agreement_rate_0_0300"] >= contract["gate_agreement_rate_min"],
    }
    return {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}


def validate_owner_registry(registry: dict) -> list[str]:
    errors: list[str] = []
    families = registry.get("families", {})
    if "ETHBTC_DIRECT" not in families:
        errors.append("ETHBTC_DIRECT family required")
    eth = families.get("ETHBTC_DIRECT", {})
    if not eth.get("owner"):
        errors.append("direct ETHBTC owner required")
    if "ETHUSD_DIV_BTCUSD" not in eth.get("diagnostic_only", []):
        errors.append("derived ETH/BTC must be diagnostic_only")
    rules = registry.get("rules", {})
    if not rules.get("missing_is_not_zero"):
        errors.append("missing_is_not_zero must be true")
    if not rules.get("derived_cannot_score_direct_gate"):
        errors.append("derived_cannot_score_direct_gate must be true")
    return errors
