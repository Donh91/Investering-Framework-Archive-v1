import importlib.util
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[2] / 'scripts/security/cre_shadow_guard.py'
spec = importlib.util.spec_from_file_location('cre_shadow_guard', MODULE)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
P = g.ROOT


class GuardTests(unittest.TestCase):
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


if __name__ == '__main__':
    unittest.main()
