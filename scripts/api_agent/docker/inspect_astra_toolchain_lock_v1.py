"""Trusted PR-only diagnostic: print a candidate FULL hash lock from wheel bytes.

Never an authority to lift BUILD HOLD. Generate from a reviewed no-secret
toolchain image before candidate code. The reviewed lock must be COMMITTED
and enforced by pip --require-hashes in a later exact-head PR state.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from pip._vendor.packaging.utils import canonicalize_name, parse_wheel_filename

def candidate_lock(freeze: Path, wheels: Path) -> tuple[str, dict]:
    assert freeze.is_file() and wheels.is_dir(), "LOCK_INPUT_MISSING"
    rows = freeze.read_text(encoding="utf-8").splitlines()
    requested: dict[str, tuple[str,str]] = {}
    for line in rows:
        if not line.strip():
            continue
        assert re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*==[A-Za-z0-9_.+!-]+", line), "LOCK_FREEZE_NOT_PINNED"
        name, version = line.split("==", 1)
        key = canonicalize_name(name)
        assert key not in requested, "LOCK_DUPLICATE_NAME"
        requested[key] = (name, version)
    assert len(requested) >= 5, "LOCK_TOO_FEW_PACKAGES"
    by_name = {}
    for wheel in sorted(wheels.glob("*.whl")):
        name, version, _build, _tags = parse_wheel_filename(wheel.name)
        key = canonicalize_name(name)
        assert key in requested and key not in by_name, "LOCK_EXTRA_OR_DUPLICATE_WHEEL"
        assert str(version) == requested[key][1], "LOCK_WHEEL_VERSION_MISMATCH"
        blob = wheel.read_bytes()
        assert 0 < len(blob) < 120_000_000, "LOCK_WHEEL_SIZE"
        by_name[key] = hashlib.sha256(blob).hexdigest()
    assert set(requested) == set(by_name), "LOCK_WHEEL_MISSING"
    lines = [
        f"{requested[k][0]}=={requested[k][1]} --hash=sha256:{by_name[k]}"
        for k in sorted(requested)
    ]
    lock = "\n".join(lines) + "\n"
    manifest = {"contract": "ASTRA_TOOLCHAIN_LOCK_DIAGNOSTIC_v1",
                "sha256": hashlib.sha256(lock.encode("utf-8")).hexdigest(),
                "wheel_count": len(lines), "release_authority": False}
    return lock, manifest

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze", required=True, type=Path)
    parser.add_argument("--wheels", required=True, type=Path)
    parser.add_argument("--lock-out", required=True, type=Path)
    a = parser.parse_args()
    lock, manifest = candidate_lock(a.freeze, a.wheels)
    a.lock_out.write_text(lock, encoding="utf-8")
    print("ASTRA_LOCK_DRAFT_BEGIN")
    print(lock, end="")
    print("ASTRA_LOCK_DRAFT_END")
    print(json.dumps(manifest, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
