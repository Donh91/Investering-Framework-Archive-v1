from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def inspect(path: Path) -> list[str]:
    text = path.read_text(encoding='utf-8', errors='ignore')
    writes_main = 'contents: write' in text and 'git push' in text
    push_trigger = re.search(r'(?m)^  push:\s*$', text) is not None
    findings: list[str] = []
    if writes_main and push_trigger:
        findings.append('PUSH_TRIGGERED_MAIN_WRITER')
    return findings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--workflow-root', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    rows = []
    for path in sorted(list(args.workflow_root.glob('*.yml')) + list(args.workflow_root.glob('*.yaml'))):
        findings = inspect(path)
        if findings:
            rows.append({'path': str(path), 'findings': findings})
    result = {
        'contract': 'WRITER_TRIGGER_SAFETY_v1',
        'status': 'PASS' if not rows else 'FAIL',
        'violations': rows,
        'rule': 'A workflow that can push repository contents must not run from a generic push event.',
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, sort_keys=True, separators=(',', ':')) + '\n')
    print(json.dumps(result, sort_keys=True))
    if rows:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
