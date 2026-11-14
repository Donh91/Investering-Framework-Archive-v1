"""Exercise the actual CN workflow steps with planted forbidden strings."""
import re
import shlex
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CASES = (
    (".github/workflows/cycle-navigator-pages.yml", "Verify final investor-facing shell and privacy", 13),
    (".github/workflows/cn-site-v2-gate.yml", "Verify public investor product", 12),
)

def step_body(path, name):
    text = (ROOT / path).read_text(encoding="utf-8")
    marker = "      - name: " + name + "\n        run: |\n"
    assert text.count(marker) == 1, (path, name)
    lines = []
    for line in text.split(marker, 1)[1].splitlines():
        if not line.startswith("          "):
            break
        lines.append(line[10:])
    return lines

class TestWorkflowForbiddenGuards(unittest.TestCase):
    def test_actual_blocks_reject_every_planted_string(self):
        for path, name, expected in CASES:
            lines = step_body(path, name)
            grep_index = 0
            guards = []
            for line in lines:
                if re.match(r"^(?:if )?grep ", line):
                    grep_index += 1
                if line.startswith("if grep "):
                    cmd = line[len("if "):].split("; then", 1)[0]
                    args = shlex.split(cmd)
                    guards.append((grep_index, args[-2], args[-1]))
                self.assertFalse(line.startswith("! grep "), (path, line))
            self.assertEqual(len(guards), expected, path)
            # The real step executes under bash -e. Positive grep checks and
            # unrelated file-existence tests are stubbed, negative greps use
            # real grep against temporary files, so each guard is tested in
            # its original position in the complete run block.
            indices = "|".join(str(i) for i, _, _ in guards)
            prefix = (
                "n=0\n"
                "test() { return 0; }\n"
                "grep() { n=$((n+1)); case \"$n\" in "
                + indices + ") command grep \"$@\";; *) return 0;; esac; }\n"
            )
            script = prefix + "\n".join(lines) + "\necho STEP_COMPLETED\n"
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                paths = {f for _, _, f in guards}
                for f in paths:
                    p = root / f
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_text("", encoding="utf-8")
                def run():
                    return subprocess.run(
                        ["bash", "--noprofile", "--norc", "-eo", "pipefail", "-c", script],
                        cwd=root, capture_output=True, text=True, check=False)
                clean = run()
                self.assertEqual(clean.returncode, 0, (path, clean.stderr))
                self.assertIn("STEP_COMPLETED", clean.stdout)
                for _, pattern, f in guards:
                    with self.subTest(workflow=path, pattern=pattern):
                        p = root / f
                        # Privacy grep uses BRE alternatives. One matching
                        # alternative is sufficient for the negative control.
                        p.write_text(pattern.split(r"\|")[0] + "\n", encoding="utf-8")
                        result = run()
                        self.assertNotEqual(result.returncode, 0, (path, pattern))
                        self.assertNotIn("STEP_COMPLETED", result.stdout)
                        p.write_text("", encoding="utf-8")

if __name__ == "__main__":
    unittest.main()
