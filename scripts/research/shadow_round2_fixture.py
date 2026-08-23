#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run_git(root: Path, *args: str) -> None:
    proc = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or f"git {' '.join(args)} failed")


def write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    root = args.root.resolve()
    repo_root = REPO_ROOT.resolve()
    if root == repo_root or repo_root in root.parents:
        raise SystemExit("fixture_root_must_be_outside_framework_checkout")
    if root.exists() and any(root.iterdir()):
        raise SystemExit("fixture_root_must_be_empty")
    root.mkdir(parents=True, exist_ok=True)

    write(root, "app/__init__.py", "")
    write(
        root,
        "app/repository.py",
        """from __future__ import annotations

CUSTOMERS = {
    "alpha": {"id": "alpha", "name": "Ada"},
    "beta": {"id": "beta", "name": "Ben"},
}


def fetch_customer(customer_id: str) -> dict[str, str]:
    return dict(CUSTOMERS[customer_id])
""",
    )
    write(
        root,
        "app/audit.py",
        """from __future__ import annotations


def record_lookup(customer_id: str) -> str:
    return f"lookup:{customer_id}"
""",
    )
    write(
        root,
        "app/service.py",
        """from __future__ import annotations

from app.audit import record_lookup
from app.repository import fetch_customer


def load_customer(customer_id: str) -> dict[str, str]:
    customer = fetch_customer(customer_id)
    customer["audit"] = record_lookup(customer_id)
    return customer
""",
    )
    write(
        root,
        "app/router.py",
        """from __future__ import annotations

from app.service import load_customer


def get_customer(customer_id: str) -> dict[str, str]:
    return load_customer(customer_id)
""",
    )
    write(
        root,
        "tests/test_service.py",
        """from app.router import get_customer


def test_customer_flow() -> None:
    value = get_customer("alpha")
    assert value["name"] == "Ada"
    assert value["audit"] == "lookup:alpha"
""",
    )
    write(
        root,
        "promptfooconfig.yaml",
        """description: agent-tool-shadow-round2-stage-a
prompts:
  - "Return exactly: {{value}}"
providers:
  - echo
tests:
  - vars:
      value: round2
    assert:
      - type: contains
        value: round2
""",
    )
    write(
        root,
        "README.md",
        """# Agent Tool Round 2 Fixture

Expected call chain:

`get_customer -> load_customer -> fetch_customer`

`load_customer -> record_lookup`

This fixture contains no secrets, provider credentials or market data.
""",
    )

    run_git(root, "init", "-q")
    run_git(root, "config", "user.name", "round2-fixture")
    run_git(root, "config", "user.email", "round2-fixture@example.invalid")
    run_git(root, "add", ".")
    run_git(root, "commit", "-q", "-m", "fixture baseline")

    files = {}
    for path in sorted(p for p in root.rglob("*") if p.is_file() and ".git" not in p.parts):
        rel = path.relative_to(root).as_posix()
        files[rel] = sha256_bytes(path.read_bytes())

    manifest = {
        "contract": "AGENT_TOOL_SHADOW_ROUND2_FIXTURE_v1",
        "fixture_root_name": root.name,
        "fixture_hash": sha256_bytes(json.dumps(files, sort_keys=True, separators=(",", ":")).encode()),
        "files": files,
        "expected_symbols": ["fetch_customer", "record_lookup", "load_customer", "get_customer"],
        "expected_call_edges": [
            ["get_customer", "load_customer"],
            ["load_customer", "fetch_customer"],
            ["load_customer", "record_lookup"],
        ],
        "contains_secrets": False,
        "contains_market_data": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "fixture_hash": manifest["fixture_hash"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
