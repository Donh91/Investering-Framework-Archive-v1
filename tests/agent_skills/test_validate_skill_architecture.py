import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from scripts.agent_skills import validate_skill_architecture as validator


class SkillArchitectureCompletenessTests(unittest.TestCase):
    def setUp(self):
        self._globals = (validator.ROOT, validator.INDEX_PATH, validator.CANONICAL_REGISTRY)

    def tearDown(self):
        validator.ROOT, validator.INDEX_PATH, validator.CANONICAL_REGISTRY = self._globals

    @staticmethod
    def _registry(names):
        rows = "\n".join(
            f"| {name} | `.agents/skills/{name}/SKILL.md` | PILOT_ACTIVE | test | Read only |"
            for name in names
        )
        return (
            "# Registry\n\n"
            "## 1. Purpose\n\nTest fixture.\n\n"
            "## 2. Active stack\n\n"
            "| Skill | Path | Status | Primary triggers | Authority |\n"
            "|---|---|---|---|---|\n"
            f"{rows}\n\n"
            "## 3. Default composition\n\nFixture tail.\n"
        )

    @staticmethod
    def _entry(name, implicit=False):
        return {
            "name": name,
            "category": "fixture",
            "maturity": "PILOT_ACTIVE",
            "skill_path": f".agents/skills/{name}/SKILL.md",
            "agents_metadata_path": f".agents/skills/{name}/agents/openai.yaml",
            "purpose": "fixture",
            "triggers": ["fixture"],
            "do_not_use_for": ["fixture"],
            "default_side_effect_level": "READ_ONLY",
            "side_effect_level": "READ_ONLY",
            "requires_credentials": False,
            "primary_outputs": ["fixture"],
            "validation_expectations": ["fixture"],
            "allow_implicit_invocation": implicit,
            "portability_notes": "fixture",
        }

    def _run(self, registry_names, entries):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        control = root / "00_ARCHIVE_CONTROL"
        control.mkdir(parents=True)

        registry_path = control / "SKILL_REGISTRY.md"
        registry_path.write_text(self._registry(registry_names), encoding="utf-8")

        index_path = control / "SKILL_ROUTING_INDEX.json"
        index_path.write_text(
            json.dumps(
                {
                    "status": "DERIVED_ROUTING_ONLY",
                    "authority": "NONE_BY_ITSELF",
                    "canonical_owner": "00_ARCHIVE_CONTROL/SKILL_REGISTRY.md",
                    "skills": entries,
                }
            ),
            encoding="utf-8",
        )

        for entry in entries:
            name = entry["name"]
            skill = root / entry["skill_path"]
            skill.parent.mkdir(parents=True, exist_ok=True)
            skill.write_text("---\nname: fixture\ndescription: fixture\n---\nbody\n", encoding="utf-8")
            metadata = root / entry["agents_metadata_path"]
            metadata.parent.mkdir(parents=True, exist_ok=True)
            expected = entry["allow_implicit_invocation"] is True
            metadata.write_text(
                f"allow_implicit_invocation: {'true' if expected else 'false'}\n",
                encoding="utf-8",
            )

        validator.ROOT = root
        validator.INDEX_PATH = index_path
        validator.CANONICAL_REGISTRY = registry_path
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = validator.main()
        return code, output.getvalue()

    def test_matching_active_inventory_and_real_booleans_pass(self):
        entries = [self._entry("alpha", True), self._entry("beta", False)]
        code, output = self._run(["alpha", "beta"], entries)
        self.assertEqual(code, 0, output)
        self.assertIn("PASS:", output)

    def test_omitted_canonical_skill_fails_without_fixed_count(self):
        code, output = self._run(["alpha", "beta"], [self._entry("alpha")])
        self.assertEqual(code, 1)
        self.assertIn("routing index omits canonical active skills: beta", output)

    def test_non_active_index_skill_fails_exact_set_reconciliation(self):
        entries = [self._entry("alpha"), self._entry("legacy")]
        code, output = self._run(["alpha"], entries)
        self.assertEqual(code, 1)
        self.assertIn("legacy: absent from canonical active skill stack", output)
        self.assertIn("routing index contains non-active skills: legacy", output)

    def test_non_boolean_routing_values_are_rejected(self):
        for value in ("false", "true", 0, 1, None):
            with self.subTest(value=value):
                entry = self._entry("alpha")
                entry["allow_implicit_invocation"] = value
                code, output = self._run(["alpha"], [entry])
                self.assertEqual(code, 1)
                self.assertIn("allow_implicit_invocation must be a JSON boolean", output)

    def test_parser_uses_only_canonical_active_stack_table(self):
        text = (
            "# Registry\n\nMention ghost-skill in prose.\n\n"
            "## 2. Active stack\n\n"
            "| Skill | Path |\n|---|---|\n| alpha | x |\n| beta | y |\n\n"
            "## 3. Later\n\n| ghost-skill | z |\n"
        )
        self.assertEqual(validator.parse_active_skill_names(text), {"alpha", "beta"})

    def test_duplicate_canonical_active_row_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "duplicate canonical active skill rows"):
            validator.parse_active_skill_names(self._registry(["alpha", "alpha"]))


if __name__ == "__main__":
    unittest.main()
