"""Pure shadow simulator; inputs are hypothetical evidence, never authority."""
from dataclasses import dataclass
from enum import Enum

GATES = (
    "source_verified", "brief_verified", "identity_verified", "head_unchanged",
    "paths_verified", "drift_disjoint", "risk_eligible", "owner_gate_clear",
    "ci_verified", "privacy_verified", "review_admissible", "veto_clear",
    "threads_clear", "rules_verified", "lane_pins_verified", "halt_clear",
    "writer_clear", "intent_clear", "clock_writable", "readback_budget",
    "high_evidence_if_required", "strategist_if_required",
)

class Decision(str, Enum):
    NOOP = "NOOP"
    SIMULATE_MERGE = "SIMULATE_MERGE"
    RECONCILE_ONLY = "RECONCILE_ONLY"
    HALT = "HALT"
    VERIFIED = "VERIFIED"
    FOREIGN = "FOREIGN"
    ABSENT = "ABSENT"

@dataclass(frozen=True)
class Result:
    decision: Decision
    reason: str

def decide(evidence):
    if type(evidence) is not dict:
        return Result(Decision.NOOP, "malformed")
    if evidence.get("clock_writable") is not True:
        return Result(Decision.NOOP, "clock_writable")
    if evidence.get("source_verified") is not True:
        return Result(Decision.NOOP, "source_verified")
    if evidence.get("intent_clear") is False:
        return Result(Decision.RECONCILE_ONLY, "open_intent")
    for gate in GATES:
        if evidence.get(gate) is not True:
            return Result(Decision.NOOP, gate)
    return Result(Decision.SIMULATE_MERGE, "synthetic_all_gates")

def reconcile(evidence):
    """Model an already-open intent; never emits a retry or a merge."""
    if type(evidence) is not dict:
        return Result(Decision.RECONCILE_ONLY, "unknown")
    if evidence.get("native_read_verified") is not True:
        return Result(Decision.RECONCILE_ONLY, "native_read_unknown")
    if evidence.get("merged") is False:
        return Result(Decision.ABSENT, "native_not_merged")
    if evidence.get("merged") is not True:
        return Result(Decision.RECONCILE_ONLY, "merge_unknown")
    if evidence.get("intent_binding") is False:
        return Result(Decision.FOREIGN, "different_operation")
    if evidence.get("intent_binding") is not True:
        return Result(Decision.RECONCILE_ONLY, "binding_unknown")
    for gate in ("single_parent", "subject_bound", "main_ancestry",
                 "changed_blobs_equal", "no_bypass"):
        if evidence.get(gate) is False:
            return Result(Decision.HALT, gate)
        if evidence.get(gate) is not True:
            return Result(Decision.RECONCILE_ONLY, gate)
    return Result(Decision.VERIFIED, "synthetic_readback")
