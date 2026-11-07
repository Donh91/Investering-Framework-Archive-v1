"""Task 3 Phase A: test-only SHADOW locator contract, never a runtime loader.

These offline checks intentionally grant no permissions, method admission,
native GitHub authentication, merge authority, or S1 runtime adoption.
The existing AGENTS.md, saved S1 task and current domain rules stay above
the manifest. Positive and adversarial checks execute in existing PR CI.
"""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = "00_FMOS/S1/OPERATING_MANIFEST.json"
SHADOW_ID = "6ae5fd466b48819187abc224ec0f1c5f"
KEYS = {
    "contract", "status", "method_version", "owner_issue", "task_id",
    "entrypoint", "mission_path", "references",
}
REFERENCES = (
    "AGENTS.md",
    "00_FMOS/CHAT_S1_ELITE_RUNBOOK.md",
    ".agents/skills/canonical-context-router/SKILL.md",
    ".agents/skills/s1-pr-repair-learning/SKILL.md",
    ".agents/skills/skill-quality-gate/SKILL.md",
    "00_ARCHIVE_CONTROL/SKILL_REGISTRY.md",
    "00_FMOS/OPERATIONAL_MEMORY_AND_RETRIEVAL_v1.md",
)
EXPECTED = {
    "contract": "S1_GITHUB_METHOD_LOCATOR_v1",
    "status": "SHADOW_CANDIDATE",
    "method_version": "1.0.0-shadow",
    "owner_issue": 1156,
    "task_id": SHADOW_ID,
    "entrypoint": "00_FMOS/S1/README.md",
    "mission_path": "00_FMOS/S1/MISSION.md",
}


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("DUPLICATE_MANIFEST_KEY")
        result[key] = value
    return result


def _relative(path):
    if not isinstance(path, str) or not path or (
        "\\" in path or ":" in path or "?" in path or "#" in path
        or "%" in path or "\x00" in path
    ):
        raise ValueError("INVALID_MANIFEST_PATH")
    p = PurePosixPath(path)
    if p.is_absolute() or any(part in ("", ".", "..") for part in path.split("/")):
        raise ValueError("INVALID_MANIFEST_PATH")
    return path


def validate_shadow_locator(raw):
    """Validate only the admitted, fixed SHADOW *shape*, never execution."""
    candidate = json.loads(raw, object_pairs_hook=_unique_object)
    if type(candidate) is not dict or set(candidate) != KEYS:
        raise ValueError("MANIFEST_SCHEMA_DRIFT")
    for key, value in EXPECTED.items():
        if type(candidate[key]) is not type(value) or candidate[key] != value:
            raise ValueError("MANIFEST_NOT_SHADOW_OR_WRONG_OWNER")
    for key in ("entrypoint", "mission_path"):
        _relative(candidate[key])
    references = candidate["references"]
    if (
        type(references) is not list
        or len(references) != len(REFERENCES)
        or any(type(x) is not str for x in references)
        or tuple(references) != REFERENCES
    ):
        raise ValueError("MANIFEST_REFERENCE_ALLOWLIST_MISMATCH")
    for path in references:
        _relative(path)
    # No manifest field contains or supplies external owner admission,
    # credentials, executors, rights, a run ID, or a production ref.
    return candidate


class TestS1ShadowOperatingManifest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
        cls.candidate = validate_shadow_locator(cls.raw)

    def mutate(self, field, value):
        altered = copy.deepcopy(self.candidate)
        altered[field] = value
        with self.assertRaises(ValueError):
            validate_shadow_locator(json.dumps(altered))

    def test_original_manifest_is_shadow_only(self):
        self.assertEqual(self.candidate["status"], "SHADOW_CANDIDATE")
        self.assertEqual(self.candidate["task_id"], SHADOW_ID)
        self.assertEqual(self.candidate["owner_issue"], 1156)

    def test_all_referenced_files_exist_at_same_checkout(self):
        paths = [self.candidate["entrypoint"], self.candidate["mission_path"]]
        paths += self.candidate["references"]
        self.assertEqual(len(paths), 9)
        for name in paths:
            with self.subTest(path=name):
                f = ROOT / _relative(name)
                self.assertTrue(f.is_file(), name)
                self.assertFalse(f.is_symlink(), name)
                self.assertTrue(f.read_bytes(), name)

    def test_no_extra_activation_or_permission_keys(self):
        for key in ("activate", "enabled", "permissions", "approval",
                    "owner_authorized", "executor", "billing", "secrets",
                    "method_ref", "self_signed", "release_permission"):
            with self.subTest(key=key):
                altered = dict(self.candidate, **{key: True})
                with self.assertRaises(ValueError):
                    validate_shadow_locator(json.dumps(altered))

    def test_status_cannot_self_promote(self):
        for status in ("ACTIVE", "APPROVED", "PRODUCTION", "MERGE_ALLOWED", True):
            with self.subTest(status=status):
                self.mutate("status", status)

    def test_owner_and_task_identity_are_fixed(self):
        for field, bad in (
            ("owner_issue", 0), ("owner_issue", "1156"), ("owner_issue", True),
            ("task_id", "some-other-task"), ("task_id", None),
        ):
            with self.subTest(field=field, value=bad):
                self.mutate(field, bad)

    def test_unknown_contract_or_version_fails_closed(self):
        self.mutate("contract", "S1_GITHUB_METHOD_LOCATOR_v2")
        self.mutate("method_version", "2.0.0-active")

    def test_missing_required_key_fails_closed(self):
        altered = copy.deepcopy(self.candidate)
        del altered["mission_path"]
        with self.assertRaises(ValueError):
            validate_shadow_locator(json.dumps(altered))

    def test_duplicate_json_keys_fail_closed(self):
        duplicate = self.raw.replace(
            '"status": "SHADOW_CANDIDATE",',
            '"status": "SHADOW_CANDIDATE", "status": "ACTIVE",', 1,
        )
        self.assertNotEqual(self.raw, duplicate)
        with self.assertRaisesRegex(ValueError, "DUPLICATE_MANIFEST_KEY"):
            validate_shadow_locator(duplicate)

    def test_reference_addition_removal_and_reorder_fail_closed(self):
        refs = list(REFERENCES)
        for variant in (
            refs[:-1],
            refs + ["00_FMOS/S1/OPERATING_MANIFEST.json"],
            list(reversed(refs)),
            refs[:-1] + ["https://example.com/policy"],
            refs[:-1] + ["../private/secrets"],
            refs[:-1] + [123],
        ):
            with self.subTest(variant=variant):
                self.mutate("references", variant)

    def test_path_traversal_urls_and_windows_paths_fail_closed(self):
        for bad in (
            "../secrets/AGENTS.md", "/tmp/runbook.md",
            "https://example.com/runbook", "a/../../b",
            "a//b", "a/./b", "a\\..\\b", "a?ref=main",
            "a#fragment", "a%2F..%2Fb",
        ):
            with self.subTest(path=bad):
                self.mutate("entrypoint", bad)
                self.mutate("mission_path", bad)

    def test_entrypoint_and_mission_cannot_redirect(self):
        self.mutate("entrypoint", "AGENTS.md")
        self.mutate("mission_path", "00_FMOS/CHAT_S1_ELITE_RUNBOOK.md")

    def test_non_object_json_fails_closed(self):
        for raw in ("[]", "null", '"shadow"', "true"):
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    validate_shadow_locator(raw)

    def test_bad_utf8_or_invalid_json_fails_closed(self):
        with self.assertRaises((ValueError, json.JSONDecodeError)):
            validate_shadow_locator('{"contract":')

    def test_documented_direct_and_delegated_are_distinct(self):
        readme = (ROOT / self.candidate["entrypoint"]).read_text(encoding="utf-8")
        mission = (ROOT / self.candidate["mission_path"]).read_text(encoding="utf-8")
        for content in (readme, mission):
            self.assertIn("DIRECT_SCHEDULED", content)
            self.assertIn("SCHEDULED_DELEGATED", content)
            self.assertIn("SHADOW_CANDIDATE", content)
        self.assertIn("Method admission is external", readme)
        self.assertIn("SHA authenticates bytes, not authority", readme)

    def test_no_runtime_permission_from_test_success(self):
        value = validate_shadow_locator(self.raw)
        self.assertNotIn("approved", value)
        self.assertNotIn("release_authorized", value)
        self.assertNotIn("active_method_revision", value)
        self.assertEqual(value["status"], "SHADOW_CANDIDATE")


if __name__ == "__main__":
    unittest.main()
