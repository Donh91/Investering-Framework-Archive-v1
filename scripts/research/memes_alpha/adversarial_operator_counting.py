from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CONTRACT = "ADVERSARIAL_OPERATOR_COUNTING_RECEIPT_v1"
MANIFEST_CONTRACT = "ADVERSARIAL_OPERATOR_COUNTING_MANIFEST_v1"
KNOWN_SEEDS = {
    "0xd5520d9d777a42d85f94834fbea162b17a197cfb",
    "0x80baa4b3bfac6f4978700df824b1b3d98e889136",
    "0xfe51aaf6af1ec2eb9286e0bdc3c9dc39240cb8f5",
    "0x5e55f18453545d0d4314c5106a2d8db934298e95",
    "0xbc9cc4b93a08b2dfba87067a9c53e713db3314ce",
    "0x8fcf98e1348d3ddee46cdd15a5c7d9a8d423077d",
}
BENIGN_CLASSES = {"RELAY", "ROUTER", "BRIDGE", "CEX", "PONS_FACTORY", "PROTOCOL", "FAUCET", "SETTLEMENT", "BENIGN_INFRA"}
NON_BENIGN_CLASSES = {"NON_BENIGN", "OPERATOR", "PROJECT", "EOA", "UNKNOWN_NON_INFRA"}


def canonical_hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


def normalize_address(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    v = value.strip().lower()
    if len(v) != 42 or not v.startswith("0x"):
        return None
    if any(c not in "0123456789abcdef" for c in v[2:]):
        return None
    return v


def parse_iso(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def tri(value: Any) -> bool | None:
    if value is True or value in {"YES", "TRUE", "PASS"}:
        return True
    if value is False or value in {"NO", "FALSE", "FAIL"}:
        return False
    return None


def parameter_map(decoded_input: Any) -> dict[str, Any]:
    if not isinstance(decoded_input, dict):
        return {}
    rows = decoded_input.get("parameters")
    if not isinstance(rows, list):
        return {}
    return {r["name"]: r.get("value") for r in rows if isinstance(r, dict) and isinstance(r.get("name"), str)}


def _word(args: bytes, idx: int) -> bytes:
    start = idx * 32
    end = start + 32
    if end > len(args):
        raise ValueError("ABI_HEAD_TRUNCATED")
    return args[start:end]


def decode_launch_and_buy_calldata(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, str) or not raw.startswith("0x"):
        return {"state": "UNKNOWN", "reason": "RAW_INPUT_MISSING"}
    try:
        blob = bytes.fromhex(raw[2:])
    except ValueError:
        return {"state": "UNKNOWN", "reason": "RAW_INPUT_INVALID_HEX"}
    if len(blob) < 4 + 7 * 32:
        return {"state": "UNKNOWN", "reason": "RAW_INPUT_TOO_SHORT"}
    args = blob[4:]
    try:
        pair = "0x" + _word(args, 2)[12:].hex()
        quote_in = int.from_bytes(_word(args, 3), "big")
        recipient = "0x" + _word(args, 5)[12:].hex()
        offset = int.from_bytes(_word(args, 6), "big")
        if offset % 32 or offset + 32 > len(args):
            raise ValueError("EXEMPTION_OFFSET_INVALID")
        n = int.from_bytes(args[offset:offset+32], "big")
        if n > 4096:
            raise ValueError("EXEMPTION_COUNT_IMPLAUSIBLE")
        end = offset + 32 + 32 * n
        if end > len(args):
            raise ValueError("EXEMPTION_ARRAY_TRUNCATED")
        exemptions = []
        pos = offset + 32
        for _ in range(n):
            exemptions.append("0x" + args[pos:pos+32][12:].hex())
            pos += 32
        return {
            "state": "PASS",
            "pair_token": normalize_address(pair),
            "quote_in_raw": quote_in,
            "recipient": normalize_address(recipient),
            "snipe_tax_exemptions": exemptions,
            "snipe_exemption_count": len(exemptions),
        }
    except ValueError as exc:
        return {"state": "UNKNOWN", "reason": str(exc)}


def decode_privileged_surface(event: dict[str, Any]) -> dict[str, Any]:
    params = parameter_map(event.get("decoded_input"))
    if params:
        exemptions = params.get("snipeTaxExemptions")
        return {
            "state": "PASS" if isinstance(exemptions, list) else "UNKNOWN",
            "source": "DECODED_INPUT",
            "snipe_exemption_count": len(exemptions) if isinstance(exemptions, list) else None,
            "snipe_tax_exemptions": [normalize_address(x) for x in exemptions if normalize_address(x)] if isinstance(exemptions, list) else [],
            "pair_token": normalize_address(params.get("pairToken")),
            "recipient": normalize_address(params.get("recipient")),
        }
    row = decode_launch_and_buy_calldata(event.get("raw_tx_input") or event.get("input"))
    row["source"] = "RAW_CALLDATA"
    return row


def infra_state(event: dict[str, Any]) -> str:
    explicit = event.get("benign_infra_excluded")
    if explicit is True:
        return "NON_BENIGN"
    if explicit is False:
        return "BENIGN_INFRA"
    klass = event.get("lineage_class") or event.get("common_funder_class")
    if isinstance(klass, str):
        k = klass.strip().upper()
        if k in BENIGN_CLASSES:
            return "BENIGN_INFRA"
        if k in NON_BENIGN_CLASSES:
            return "NON_BENIGN"
    return "UNKNOWN"


def classify_event(event: dict[str, Any]) -> dict[str, Any]:
    token_ca = normalize_address(event.get("token_ca") or event.get("token_address"))
    t0_value = event.get("launch_t0") or event.get("timestamp") or event.get("block_timestamp_utc")
    t0 = parse_iso(t0_value)
    privileged = decode_privileged_surface(event)
    bundle = tri(event.get("privileged_bundle_evidence"))
    if bundle is None:
        count = privileged.get("snipe_exemption_count")
        bundle = (count > 0) if isinstance(count, int) else None

    pre_t0 = tri(event.get("pre_t0_prep_observed"))
    direct = tri(event.get("direct_operator_lineage"))
    common = tri(event.get("common_funding"))
    sync = tri(event.get("synchronized_inventory"))
    residual = tri(event.get("residual_similarity"))
    infra = infra_state(event)

    exact_identity = token_ca is not None and t0 is not None
    branch_direct = direct is True
    branch_privileged = common is True and bundle is True
    branch_residual = common is True and sync is True and residual is True
    raw_pattern = exact_identity and pre_t0 is True and (branch_direct or branch_privileged or branch_residual)

    unresolved = []
    if token_ca is None:
        unresolved.append("EXACT_CA_UNKNOWN")
    if t0 is None:
        unresolved.append("T0_UNKNOWN")
    if pre_t0 is None:
        unresolved.append("PRE_T0_PREP_UNKNOWN")
    if privileged.get("state") == "UNKNOWN":
        unresolved.append("PRIVILEGED_SURFACE_UNKNOWN")

    infra_false_positive = raw_pattern and infra == "BENIGN_INFRA"
    infra_unknown = raw_pattern and infra == "UNKNOWN"
    stage1_qualified = raw_pattern and infra == "NON_BENIGN"

    stage2_reason = None
    if stage1_qualified:
        if direct is True:
            stage2_reason = "DIRECT_OPERATOR_LINEAGE"
        elif common is True and bundle is True and sync is True:
            stage2_reason = "PRIVILEGED_BUNDLE_PLUS_COMMON_FUNDING_PLUS_SYNCHRONIZED_INVENTORY"
    stage2_qualified = stage2_reason is not None

    if infra_false_positive:
        state = "FALSE_POSITIVE_INFRA"
    elif infra_unknown:
        state = "UNKNOWN_INFRA"
    elif stage2_qualified:
        state = "STAGE2_QUALIFIED"
    elif stage1_qualified:
        state = "STAGE1_QUALIFIED"
    elif unresolved:
        state = "UNKNOWN"
    else:
        state = "NO_HIT"

    return {
        "token_ca": token_ca,
        "launch_t0": t0_value,
        "transaction_hash": event.get("transaction_hash") or event.get("tx_hash"),
        "privileged_surface": privileged,
        "pre_t0_prep_observed": pre_t0,
        "direct_operator_lineage": direct,
        "common_funding": common,
        "synchronized_inventory": sync,
        "residual_similarity": residual,
        "infra_state": infra,
        "raw_fire": raw_pattern,
        "stage1_qualified": stage1_qualified,
        "stage2_qualified": stage2_qualified,
        "stage2_reason": stage2_reason,
        "classification": state,
        "known_seed": token_ca in KNOWN_SEEDS or bool(event.get("known_seed")),
        "ordinary_control": bool(event.get("ordinary_control")),
        "unresolved": unresolved,
    }


def count_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    if manifest.get("contract") != MANIFEST_CONTRACT:
        raise ValueError("WRONG_MANIFEST_CONTRACT")
    events = manifest.get("events")
    if not isinstance(events, list):
        raise ValueError("EVENTS_MUST_BE_LIST")
    start = parse_iso(manifest.get("interval_start_utc"))
    end = parse_iso(manifest.get("interval_end_utc"))
    if start is None or end is None or end <= start:
        raise ValueError("INVALID_INTERVAL")
    days = (end - start).total_seconds() / 86400.0

    rows = [classify_event(e) for e in events if isinstance(e, dict)]
    raw = [r for r in rows if r["raw_fire"]]
    q1 = [r for r in rows if r["stage1_qualified"]]
    q2 = [r for r in rows if r["stage2_qualified"]]
    benign = [r for r in rows if r["classification"] == "FALSE_POSITIVE_INFRA"]
    infra_unknown = [r for r in rows if r["classification"] == "UNKNOWN_INFRA"]
    decode_unknown = [r for r in rows if r["privileged_surface"].get("state") == "UNKNOWN"]

    raw_rate = len(raw) / days
    q1_rate = len(q1) / days
    q2_rate = len(q2) / days
    benign_share = (len(benign) / len(raw)) if raw else 0.0

    if infra_unknown:
        stage1_gate = "INCOMPLETE_UNKNOWN_INFRA"
    elif benign_share >= 0.5 and raw:
        stage1_gate = "INFRA_EXCLUSION_INADEQUATE"
    elif q1_rate <= 10:
        stage1_gate = "REVIEW_BUDGET_PASS"
    else:
        stage1_gate = "STAGE2_REQUIRED"

    if stage1_gate == "STAGE2_REQUIRED":
        stage2_gate = "REVIEW_BUDGET_PASS" if q2_rate <= 10 else "AUTONOMOUS_TIME_SENSITIVE_REVIEW_OPERATIONALLY_UNVIABLE"
    else:
        stage2_gate = "NOT_REQUIRED"

    base = {
        "contract": CONTRACT,
        "status": "SHADOW_ONLY",
        "input_contract": MANIFEST_CONTRACT,
        "interval_start_utc": manifest["interval_start_utc"],
        "interval_end_utc": manifest["interval_end_utc"],
        "duration_days": days,
        "launch_rows": len(rows),
        "counts": {
            "raw_fires": len(raw),
            "stage1_qualified": len(q1),
            "stage2_qualified": len(q2),
            "benign_infra_false_positives": len(benign),
            "infra_unknown_raw_fires": len(infra_unknown),
            "privileged_surface_unknown_rows": len(decode_unknown),
            "known_seed_overlap": sum(1 for r in q1 if r["known_seed"]),
            "ordinary_control_overlap": sum(1 for r in q1 if r["ordinary_control"]),
        },
        "rates_per_day": {
            "raw_fires_per_day": raw_rate,
            "qualified_fires_per_day": q1_rate,
            "stage2_qualified_per_day": q2_rate,
        },
        "benign_infra_share": benign_share,
        "gates": {
            "stage1": stage1_gate,
            "stage2": stage2_gate,
            "qualified_per_day_max": 10,
            "benign_infra_raw_share_max": 0.5,
        },
        "source_health": {
            "rows_total": len(rows),
            "rows_with_unknown_privileged_surface": len(decode_unknown),
            "raw_fires_with_unknown_infra": len(infra_unknown),
            "missing_is_negative_evidence": False,
        },
        "rows": rows,
        "authority": {
            "research_only": True,
            "automatic_trading": False,
            "automatic_alerts": False,
            "portfolio_action": False,
            "new_scanner": False,
        },
    }
    base["input_sha256"] = canonical_hash(manifest)
    base["output_sha256"] = canonical_hash(base)
    return base


def main() -> int:
    p = argparse.ArgumentParser(description="Deterministic SHADOW-only adversarial operator counting gate.")
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    result = count_manifest(manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "contract": CONTRACT,
        "launch_rows": result["launch_rows"],
        "stage1_gate": result["gates"]["stage1"],
        "stage2_gate": result["gates"]["stage2"],
        "output_sha256": result["output_sha256"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
