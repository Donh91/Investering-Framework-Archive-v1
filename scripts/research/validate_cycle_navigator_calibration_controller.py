#!/usr/bin/env python3
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/research/cycle_navigator_calibration_controller.py"
spec = importlib.util.spec_from_file_location("cnc", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
policy = json.loads((ROOT / "05_CYCLE_NAVIGATOR/autonomous_calibration_v1/POLICY.json").read_text())


def row(i, **kw):
    base = {
        "forecast_id": f"CN{i}", "publication_ts": f"2026-01-{i:02d}T08:00:00Z",
        "actual_low": "90", "actual_high": "110", "actual_source": "SYNTHETIC_TEST_ONLY",
        "actual_verified_ts": f"2026-01-{i:02d}T23:00:00Z", "actual_verification_status": "VERIFIED",
        "reanchor_shadow_flag": "FALSE", "transition_watch_flag": "FALSE",
        "adjustment_alpha_vs_DUMB15": "1", "adjustment_alpha_vs_DUMB20": "1", "notes": ""
    }
    base.update({k: str(v) for k, v in kw.items()})
    return base


def check(name, got, expected):
    assert got["selected_action"] == expected, (name, got)
    assert got["canonical_effect"] is False
    assert got["portfolio_execution"] is False
    print(f"PASS {name}: {expected}")

check("no_evidence", mod.evaluate_rows(policy, []), "CONTINUE_CALIBRATION")
check("reanchor", mod.evaluate_rows(policy, [row(1, reanchor_shadow_flag="TRUE")]), "STRESS_TEST_REANCHOR")
check("range_miss", mod.evaluate_rows(policy, [row(1, adjustment_alpha_vs_DUMB15=-1, adjustment_alpha_vs_DUMB20=-1), row(2, adjustment_alpha_vs_DUMB15=-2, adjustment_alpha_vs_DUMB20=-1), row(3)]), "INVESTIGATE_RANGE_MISS")
check("transition", mod.evaluate_rows(policy, [row(1), row(2), row(3, transition_watch_flag="TRUE")]), "AUDIT_TRANSITION_FAKEOUT")
check("slow_bleed", mod.evaluate_rows(policy, [row(1), row(2), row(3, notes="SLOW_BLEED_FAKE_ROTATION_ROW")]), "INVESTIGATE_SLOW_BLEED_FAKE_ROTATION")
check("spike_grind", mod.evaluate_rows(policy, [row(1), row(2), row(3, notes="ETHBTC_GATE_CROSS_SIGNATURE GRIND")]), "AUDIT_GATE_CROSS_SIGNATURE")
check("bounded_hypothesis", mod.evaluate_rows(policy, [row(i) for i in range(1, 6)]), "RESEARCH_NEW_PHASE_HYPOTHESIS")
promo = {"ready": True, "minimum_verified_rows": 3, "prospective_review_required": True}
check("promotion_review_only", mod.evaluate_rows(policy, [row(1), row(2), row(3)], promo), "CANONICAL_REVIEW_JUSTIFIED")
example = row(9); example["forecast_id"] = "CNxx_EXAMPLE_BTC"; example["publication_ts"] = "EXAMPLE_ONLY"
assert mod.evaluate_rows(policy, [example])["eligible_verified_row_n"] == 0
print("PASS example_rows_excluded")
a = mod.evaluate_rows(policy, [row(1), row(2), row(3)])
b = mod.evaluate_rows(policy, [row(1), row(2), row(3)])
assert a["evidence_fingerprint"] == b["evidence_fingerprint"] and a["selected_action"] == b["selected_action"]
print("PASS deterministic_same_evidence")
print("CYCLE_NAVIGATOR_AUTONOMOUS_CALIBRATION_GATE_v1 PASS")
