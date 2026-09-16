from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class MemeAlphaRuntimeV11DirectExecutionTests(unittest.TestCase):
    def test_direct_execution_from_external_cwd_imports_sibling_worker(self) -> None:
        script = (Path(__file__).resolve().parents[2] / "scripts" / "api_agent" / "meme_alpha_runtime_v1_1.py").resolve()
        with tempfile.TemporaryDirectory() as td:
            result = subprocess.run(
                [sys.executable, str(script), "--help"],
                cwd=td,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Meme Alpha runtime v1.1", result.stdout)


if __name__ == "__main__":
    unittest.main()
