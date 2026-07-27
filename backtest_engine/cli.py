from __future__ import annotations

import argparse
import json
from pathlib import Path

from .package_audit import audit_zip
from .readiness import run_engineering_gates
from .w30_replay import replay_w30


def main() -> int:
    parser = argparse.ArgumentParser(prog="backtest-engine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    package_parser = subparsers.add_parser("audit-package")
    package_parser.add_argument("path", type=Path)

    replay_parser = subparsers.add_parser("replay-w30")
    replay_parser.add_argument("fixture_root", type=Path)

    gates_parser = subparsers.add_parser("run-engineering-gates")
    gates_parser.add_argument("fixture_root", type=Path)
    gates_parser.add_argument("w30_package", type=Path)
    gates_parser.add_argument("--continuation-package", type=Path)
    gates_parser.add_argument("--final-master", type=Path)
    gates_parser.add_argument("--output", type=Path)

    args = parser.parse_args()
    if args.command == "audit-package":
        payload = audit_zip(args.path).to_dict()
    elif args.command == "replay-w30":
        payload = replay_w30(args.fixture_root)
    else:
        payload = run_engineering_gates(
            fixture_root=args.fixture_root,
            w30_package=args.w30_package,
            continuation_package=args.continuation_package,
            final_master=args.final_master,
        )

    rendered = json.dumps(payload, indent=2, sort_keys=True)
    print(rendered)
    output = getattr(args, "output", None)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    status = payload.get("status") or payload.get("engineering_status") or payload.get("zip_crc_status")
    return 0 if str(status).startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
