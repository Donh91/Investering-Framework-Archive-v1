from __future__ import annotations

import argparse
import json
from pathlib import Path

from backtest_engine.blind_dual_run import collect_from_latest_capture


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture-root", type=Path, required=True)
    ap.add_argument("--output-root", type=Path, required=True)
    ap.add_argument("--sensor-registry", type=Path, required=True)
    ap.add_argument("--policy-registry", type=Path, required=True)
    ap.add_argument("--rotation-evaluator", type=Path, required=True)
    ap.add_argument("--crosswalk-contract", type=Path, required=True)
    args = ap.parse_args()
    result = collect_from_latest_capture(
        capture_root=args.capture_root,
        output_root=args.output_root,
        sensor_registry_path=args.sensor_registry,
        policy_registry_path=args.policy_registry,
        rotation_evaluator_path=args.rotation_evaluator,
        crosswalk_contract_path=args.crosswalk_contract,
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
