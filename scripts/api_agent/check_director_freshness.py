from __future__ import annotations

import argparse
import json
from pathlib import Path


def run_id_from_context(path: Path) -> str | None:
    try:
        value = json.loads(path.read_text())
    except Exception:
        return None
    latest = value.get("latest_capture") if isinstance(value.get("latest_capture"), dict) else {}
    run_id = latest.get("run_id")
    return str(run_id) if run_id else None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--context", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()

    current = run_id_from_context(args.context)
    if not current:
        print("fresh_ready=false")
        print("fresh_reason=CURRENT_RUN_ID_MISSING")
        return
    seen = set()
    if args.output_root.exists():
        for path in args.output_root.rglob("context.json"):
            rid = run_id_from_context(path)
            if rid:
                seen.add(rid)
    fresh = current not in seen
    print(f"fresh_ready={'true' if fresh else 'false'}")
    print(f"fresh_reason={'NEW_OWNER_RUN' if fresh else 'OWNER_RUN_ALREADY_ANALYZED'}")
    print(f"current_run_id={current}")


if __name__ == "__main__":
    main()
