#!/usr/bin/env python3
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/research/source_provenance_recovery_controller.py"
spec = importlib.util.spec_from_file_location("spr", SCRIPT)
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
policy = json.loads((ROOT / "00_ARCHIVE_CONTROL/source_recovery_controller_v1/POLICY.json").read_text())


def decision(data, name="test.json"):
    return mod.evaluate_receipts(policy, [{"path": name, "data": data, "content_hash": "synthetic"}])

def check(name, data, expected):
    got = decision(data, f"{name}.json")
    assert got["selected_action"] == expected, (name, got)
    assert got["canonical_effect"] is False
    assert got["portfolio_execution"] is False
    assert got["external_provider_calls_authorized"] is False
    assert got["paid_data_authorized"] is False
    assert got["proxy_substitution_authorized"] is False
    assert got["interpolation_authorized"] is False
    print(f"PASS {name}: {expected}")

check("not_testable", {"status":"TERMINAL_PROVIDER_NO_HISTORICAL_ROWS","returned_row_count":0,"interpretation":"must be marked NOT_TESTABLE"}, "DECLARE_NOT_TESTABLE")
check("explicit_market_unavailable", {"status":"PASS","market_historical_availability":"NOT_TESTABLE_PROVIDER_UNAVAILABLE"}, "DECLARE_NOT_TESTABLE")
check("note_only_not_testable_ignored", {"status":"PASS","notes":"historical discussion says NOT_TESTABLE but current source is healthy"}, "CONTINUE_SOURCE_MONITORING")
check("stop_retry", {"status":"TERMINAL_PROVIDER_POLICY","no_additional_retry_authorized":True}, "STOP_RETRYING")
check("stale", {"status":"STALE_SOURCE","source_stale":True}, "QUARANTINE_STALE_SOURCE")
check("transform", {"transform_status":"FAIL_INVALID_SCHEMA"}, "REPAIR_TRANSFORM")
check("free_crosscheck", {"status":"SOURCE_GAP","approved_free_alternative_source":"OWNER_B"}, "CROSSCHECK_APPROVED_FREE_SOURCE")
check("free_retry", {"status":"SOURCE_GAP","free_retry_authorized":True}, "RETRY_SAME_OWNER")
check("bounded_gapfill", {"status":"SOURCE_GAP","bounded_gapfill_authorized":True,"cost":0}, "REQUEST_BOUNDED_GAPFILL")
check("paid_voi_only", {"status":"SOURCE_GAP","paid_data_required":True}, "GENERATE_PAID_DATA_VOI_PACKET")
check("verify_provenance", {"status":"PROVIDER_FAILURE","error":"unresolved owner receipt"}, "VERIFY_PROVENANCE")
check("monitor", {"status":"PASS","verification_status":"VERIFIED"}, "CONTINUE_SOURCE_MONITORING")

schema_doc = {"$schema":"https://json-schema.org/draft/2020-12/schema","$defs":{"source_health":{"properties":{"status":{"enum":["PASS","STALE"]}}}}}
assert mod._is_schema_document(Path("data_terminal_contracts.schema.json"), schema_doc) is True
assert mod._is_schema_document(Path("arbitrary.json"), schema_doc) is True
print("PASS schema_documents_excluded_from_receipt_universe")

entries = [
    {"path":"paid.json","data":{"paid_data_required":True},"content_hash":"1"},
    {"path":"terminal.json","data":{"status":"TERMINAL_PROVIDER_NO_HISTORICAL_ROWS","returned_row_count":0},"content_hash":"2"}
]
priority = mod.evaluate_receipts(policy, entries)
assert priority["selected_action"] == "DECLARE_NOT_TESTABLE" and priority["target_receipt"] == "terminal.json"
print("PASS terminal_precedence_over_paid_voi")
a = mod.evaluate_receipts(policy, entries); b = mod.evaluate_receipts(policy, entries)
assert a["evidence_fingerprint"] == b["evidence_fingerprint"] and a["selected_action"] == b["selected_action"]
print("PASS deterministic_same_receipts")
assert policy["automatic_paid_data_authorization"] is False and policy["external_provider_calls_authorized"] is False
print("PASS zero_spend_zero_provider_call_policy")
print("SOURCE_PROVENANCE_RECOVERY_GATE_v1 PASS")
