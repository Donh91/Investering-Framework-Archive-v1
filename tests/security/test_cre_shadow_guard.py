import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch, Mock

MODULE = Path(__file__).resolve().parents[2] / 'scripts/security/cre_shadow_guard.py'
spec = importlib.util.spec_from_file_location('cre_shadow_guard', MODULE)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
P = g.ROOT


class GuardTests(unittest.TestCase):
    def test_bootstrap_detection_uses_exit_status_not_stdout(self):
        with patch.object(g.subprocess, "run", return_value=Mock(returncode=0)):
            self.assertFalse(g.bootstrap_expected("a" * 40))
        with patch.object(g.subprocess, "run", return_value=Mock(returncode=1)):
            self.assertTrue(g.bootstrap_expected("b" * 40))

    def test_normal_experiment_path(self):
        self.assertEqual(g.inspect_scope([P + 'model.py'], is_bootstrap=False), 'CRE_SCOPE_ONLY_NOT_MERGE_AUTHORITY')

    def test_other_pr_is_not_cre(self):
        self.assertEqual(g.inspect_scope(['06_RESEARCH_LAB/README.md'], is_bootstrap=False), 'NOT_CRE_PR')

    def test_mixed_scope(self):
        for outsider in ('scripts/cycle_navigator/forecast.py', '.github/workflows/publish.yml',
                         '00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md', g.TRUSTED_GUARD):
            with self.subTest(path=outsider), self.assertRaises(g.GuardError):
                g.inspect_scope([P + 'model.py', outsider], is_bootstrap=False)

    def test_reject_unsafe_extensions_or_hidden(self):
        for path in ('_data.csv', '__pycache__/evil.py', '.github/workflows/x.yml',
                     '.env', 'private/rows.json', 'credentials/token.txt', 'secret.key',
                     'binary.pkl', 'notebook.ipynb'):
            with self.subTest(path=path), self.assertRaises(g.GuardError):
                g.inspect_scope([P + path], is_bootstrap=False)

    def test_bootstrap_only_explicit_trusted_paths(self):
        self.assertEqual(g.inspect_scope([P + 'README.md', g.TRUSTED_GUARD], is_bootstrap=True),
                         'BOOTSTRAP_OWNER_REVIEW_REQUIRED')
        with self.assertRaises(g.GuardError):
            g.inspect_scope([P + 'README.md', 'scripts/portfolio/live_trade.py'], is_bootstrap=True)

    def test_policy_file_change_not_self_authorized(self):
        with self.assertRaises(g.GuardError):
            g.inspect_scope(['.github/CODEOWNERS'], is_bootstrap=False)

# Real git-history integration, not only mocked path predicates.
class GitHistoryIntegrationTests(unittest.TestCase):
    @staticmethod
    def command(cwd, *args):
        import subprocess
        return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=False)

    def test_real_git_bootstrap_and_later_scope_rejection(self):
        import tempfile
        import subprocess
        import sys
        from pathlib import Path
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.assertEqual(self.command(d, 'git', 'init', '-q').returncode, 0)
            self.command(d, 'git', 'config', 'user.name', 'test')
            self.command(d, 'git', 'config', 'user.email', 'test@example.invalid')
            (root / 'README.md').write_text('base\n')
            self.command(d, 'git', 'add', '.')
            self.assertEqual(self.command(d, 'git', 'commit', '-qm', 'base').returncode, 0)
            base = self.command(d, 'git', 'rev-parse', 'HEAD').stdout.strip()

            file = root / P / 'model.py'
            file.parent.mkdir(parents=True)
            file.write_text('def baseline(): return None\n')
            trusted = root / g.TRUSTED_GUARD
            trusted.parent.mkdir(parents=True)
            trusted.write_text('trusted guard fixture\n')
            self.command(d, 'git', 'add', '.')
            self.assertEqual(self.command(d, 'git', 'commit', '-qm', 'bootstrap').returncode, 0)
            boot_head = self.command(d, 'git', 'rev-parse', 'HEAD').stdout.strip()
            cmd = [sys.executable, str(MODULE), '--base', base, '--head', boot_head]
            result = self.command(d, *cmd)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('BOOTSTRAP_OWNER_REVIEW_REQUIRED', result.stdout)
            self.assertIn('AUTONOMOUS_MERGE_AUTHORITY=FALSE', result.stdout)

            file.write_text('def baseline(): return 0\n')
            self.command(d, 'git', 'add', '.')
            self.assertEqual(self.command(d, 'git', 'commit', '-qm', 'safe experiment').returncode, 0)
            safe_head = self.command(d, 'git', 'rev-parse', 'HEAD').stdout.strip()
            result = self.command(d, sys.executable, str(MODULE), '--base', boot_head, '--head', safe_head)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('CRE_SCOPE_ONLY_NOT_MERGE_AUTHORITY', result.stdout)

            prod = root / 'scripts/production.py'
            prod.write_text('do_not_change = True\n')
            file.write_text('def baseline(): return 1\n')
            self.command(d, 'git', 'add', '.')
            self.assertEqual(self.command(d, 'git', 'commit', '-qm', 'mixed scope').returncode, 0)
            mixed = self.command(d, 'git', 'rev-parse', 'HEAD').stdout.strip()
            result = self.command(d, sys.executable, str(MODULE), '--base', safe_head, '--head', mixed)
            self.assertEqual(result.returncode, 2)
            self.assertIn('CRE_MIXED_SCOPE_OR_TRUSTED_POLICY_CHANGE', result.stdout)

    def test_trusted_base_guard_rejects_poisoned_pr_guard_and_production_change(self):
        """A mutable PR guard can lie; running the base blob must reject the same diff."""
        import sys
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.assertEqual(self.command(d, "git", "init", "-q").returncode, 0)
            self.command(d, "git", "config", "user.name", "test")
            self.command(d, "git", "config", "user.email", "test@example.invalid")
            trusted = root / g.TRUSTED_GUARD
            trusted.parent.mkdir(parents=True)
            trusted.write_bytes(MODULE.read_bytes())
            research = root / P / "experiment.py"
            research.parent.mkdir(parents=True)
            research.write_text("experiment = 1\\n")
            self.command(d, "git", "add", ".")
            self.assertEqual(self.command(d, "git", "commit", "-qm", "trusted base").returncode, 0)
            base = self.command(d, "git", "rev-parse", "HEAD").stdout.strip()

            # Attack controls the PR copy of both the research and guard files.
            trusted.write_text('print("CRE_SCOPE_ONLY_NOT_MERGE_AUTHORITY")\\n')
            research.write_text("experiment = 2\\n")
            production = root / "04_MARKET_LEARNING" / "handlekompas" / "danger.py"
            production.parent.mkdir(parents=True)
            production.write_text("live = False\\n")
            self.command(d, "git", "add", ".")
            self.assertEqual(self.command(d, "git", "commit", "-qm", "poisoned PR").returncode, 0)
            head = self.command(d, "git", "rev-parse", "HEAD").stdout.strip()

            # This is the vulnerable behavior prior to the workflow fix.
            unsafe = self.command(d, sys.executable, str(trusted), "--base", base, "--head", head)
            self.assertEqual(unsafe.returncode, 0, unsafe.stdout + unsafe.stderr)

            # This is the reviewed workflow behavior: git show base blob to temp.
            original = self.command(d, "git", "show", f"{base}:{g.TRUSTED_GUARD}")
            self.assertEqual(original.returncode, 0)
            base_copy = root / "base_guard.py"
            base_copy.write_text(original.stdout)
            safe = self.command(d, sys.executable, str(base_copy), "--base", base, "--head", head)
            self.assertEqual(safe.returncode, 2, safe.stdout + safe.stderr)
            self.assertIn("CRE_MIXED_SCOPE_OR_TRUSTED_POLICY_CHANGE", safe.stdout)

    def test_workflow_declares_base_guard_not_pr_guard(self):
        wf = (MODULE.parents[2] / ".github/workflows/cre-shadow-tests.yml").read_text()
        self.assertIn('git show "$BASE_SHA:scripts/security/cre_shadow_guard.py"', wf)
        self.assertIn('python "$RUNNER_TEMP/cre_guard_base.py"', wf)
        self.assertIn('BOOTSTRAP_OWNER_REVIEW_REQUIRED', wf)


if __name__ == '__main__':
    unittest.main()
