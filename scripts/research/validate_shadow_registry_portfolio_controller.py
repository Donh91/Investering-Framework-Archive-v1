#!/usr/bin/env python3
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/research/shadow_registry_portfolio_controller.py"
spec = importlib.util.spec_from_file_location("srp", SCRIPT)
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
policy = json.loads((ROOT / "04_MARKET_LEARNING/shadow_registry/autonomous_portfolio_v1/POLICY.json").read_text())


def sensor(sid, relevance="WATCH", evaluator="EVAL", paths=None, **kw):
    x = {"sensor_id": sid, "family": "test", "relevance_state": relevance, "evaluator": evaluator, "evidence_paths": paths or [f"x/{sid}"]}
    x.update(kw); return x

def ev(sensors, existing=True):
    return mod.evaluate_registry(policy, {"sensors": sensors}, path_exists=(lambda p: existing))

def check(name, got, action, target):
    assert got["selected_action"] == action, (name, got)
    assert got["target_sensor_id"] == target, (name, got)
    assert got["registry_mutation"] is False and got["canonical_effect"] is False and got["portfolio_execution"] is False
    print(f"PASS {name}: {action} -> {target}")

check("missing_first", ev([sensor("B", relevance="PROMOTION_CANDIDATE"), sensor("A")], existing=False), "RECOVER_EVIDENCE_PATH", "A")
check("evaluator_recovery", ev([sensor("A", evaluator="NONE_RECOVERY_REQUIRED")]), "RECOVER_EVALUATOR", "A")
check("promotion_proposal_only", ev([sensor("A", relevance="PROMOTION_CANDIDATE")]), "OPEN_PROSPECTIVE_FORWARD_TEST", "A")
check("redundancy", ev([sensor("A", relevance="REDUNDANT")]), "RUN_REDUNDANCY_CONFIRMATION", "A")
check("incremental_value", ev([sensor("A", relevance="KEEP", incremental_value_ready=True)]), "RUN_INCREMENTAL_VALUE_TEST", "A")
check("regime", ev([sensor("A", relevance="REGIME_SPECIFIC")]), "STRESS_TEST_REGIME_SPECIFICITY", "A")
check("noise", ev([sensor("A", relevance="NOISE")]), "DEPRIORITIZE", "A")
check("untestable", ev([sensor("A", relevance="UNTESTABLE")]), "ARCHIVE_UNTESTABLE", "A")
check("observe", ev([sensor("A", relevance="KEEP")]), "CONTINUE_OBSERVING", "A")
a = ev([sensor("A", relevance="KEEP")]); b = ev([sensor("A", relevance="KEEP")])
assert a["evidence_fingerprint"] == b["evidence_fingerprint"]
print("PASS deterministic_same_registry")
print("SHADOW_REGISTRY_AUTONOMOUS_PORTFOLIO_GATE_v1 PASS")
