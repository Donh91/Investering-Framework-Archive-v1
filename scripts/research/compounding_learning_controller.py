#!/usr/bin/env python3
import sys
import compounding_learning_v1_core as _core

_original_generate = _core.generate_candidate_tests
_original_build = _core._build_products


def _generate_with_governance_actions(families):
    rows = _original_generate(families)
    for row in rows:
        row["action"] = "STRESS_TEST_REGIME_SPECIFICITY" if str(row.get("test_type") or "").startswith("REGIME") else "RUN_INCREMENTAL_VALUE_TEST"
    return rows


def _build_with_legacy_action_contract(registry, admission, adjudication, policy, previous, previous_backlog, as_of):
    state, proposal, backlog, event = _original_build(registry, admission, adjudication, policy, previous, previous_backlog, as_of)
    action = str(proposal.get("action") or "CONTINUE_OBSERVING")
    state["primary_action"] = action
    state["next_best_experiment"] = proposal
    return state, proposal, backlog, event


_core.generate_candidate_tests = _generate_with_governance_actions
_core._build_products = _build_with_legacy_action_contract

if __name__ == "__main__":
    _core.main()
else:
    sys.modules[__name__] = _core
