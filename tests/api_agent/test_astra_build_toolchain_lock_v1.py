"""Native source tests for reviewed no-secret BUILD toolchain dependency lock."""
import hashlib
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOCK = ROOT / "scripts/api_agent/docker/astra-build-requirements.lock.txt"
DOCKER = ROOT / "scripts/api_agent/docker/astra-build-toolchain-v1.Dockerfile.txt"
NODE_TARBALL = "60e3b0a8500819514aca603487c254298cd776de0698d3cd08f11dba5b8289a8"
NATIVE_WHEEL_CENSUS = "70852b54dc8bd5af2c70403a5316bda21eaa6a949f710a0451981360c96b5e38"
ROW = re.compile(r"([A-Za-z0-9][A-Za-z0-9_.-]*)==([0-9][A-Za-z0-9.+!-]*) --hash=sha256:([a-f0-9]{64})\Z")


def parse_lock(raw: bytes):
    if hashlib.sha256(raw).hexdigest() != NATIVE_WHEEL_CENSUS:
        raise ValueError("LOCK_NATIVE_CENSUS_MISMATCH")
    try:
        lines = raw.decode("utf-8").splitlines()
    except UnicodeError as exc:
        raise ValueError("LOCK_NOT_UTF8") from exc
    if len(lines) != 25:
        raise ValueError("LOCK_COUNT")
    names = []
    for line in lines:
        match = ROW.fullmatch(line)
        if match is None:
            raise ValueError("LOCK_ROW_INVALID")
        names.append(match.group(1).lower().replace("_", "-"))
    if names != sorted(names) or len(names) != len(set(names)):
        raise ValueError("LOCK_DUPLICATED_OR_UNSORTED")
    if not {"pytest", "pyyaml", "scikit-learn", "pandas", "numpy", "jsonschema"}.issubset(set(names)):
        raise ValueError("LOCK_CRITICAL_WHEELS_MISSING")
    return True


class TestBuildToolchainLock(unittest.TestCase):
    def test_native_github_wheel_census_is_byte_exact(self):
        self.assertTrue(parse_lock(LOCK.read_bytes()))

    def test_lock_mutation_is_rejected(self):
        original = LOCK.read_bytes()
        with self.assertRaisesRegex(ValueError, "LOCK_NATIVE_CENSUS_MISMATCH"):
            parse_lock(original.replace(b"pytest==9.2.0", b"pytest==9.1.0"))
        with self.assertRaisesRegex(ValueError, "LOCK_NATIVE_CENSUS_MISMATCH"):
            parse_lock(original.replace(b" --hash=sha256:", b" ", 1))

    def test_dockerfile_enforces_hashes_and_exact_base_and_node(self):
        dockerfile = DOCKER.read_text("utf-8")
        self.assertIn("python -m pip install --no-cache-dir --require-hashes", dockerfile)
        self.assertIn("COPY scripts/api_agent/docker/astra-build-requirements.lock.txt", dockerfile)
        self.assertIn("FROM python@sha256:1148dbb014615300fa7e713b2f94f550c0d1c69780c0805f84f093ceee34dd0b", dockerfile)
        self.assertIn("ARG NODE_VERSION=24.11.1", dockerfile)
        self.assertIn("ARG NODE_TARBALL_SHA256=" + NODE_TARBALL, dockerfile)
        self.assertIn("if hashlib.sha256(data).hexdigest() != expected:", dockerfile)
        self.assertNotIn("pip install --no-cache-dir 'pytest==", dockerfile)

if __name__ == "__main__":
    unittest.main()
