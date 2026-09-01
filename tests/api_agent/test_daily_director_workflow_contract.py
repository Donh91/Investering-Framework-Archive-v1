from pathlib import Path
import re
import unittest


WORKFLOW = Path('.github/workflows/daily-director-shadow.yml')
PRIMARY_PROMPT = Path('research/api_agent/prompts/DAILY_DIRECTOR_SHADOW.txt')
CONFLICT_PROMPT = Path('research/api_agent/prompts/DAILY_CONFLICT_REVIEW.txt')


class DailyDirectorWorkflowContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW.read_text(encoding='utf-8')

    def test_workflow_identity_and_triggers_are_bounded(self):
        self.assertIn('name: Daily Director Shadow', self.text)
        self.assertIn('  schedule:', self.text)
        self.assertIn('  workflow_dispatch:', self.text)
        self.assertNotRegex(self.text, r'(?m)^  push:\s*$')
        self.assertEqual(self.text.count("timezone: 'Europe/Copenhagen'"), 4)

    def test_concurrency_uses_github_actions_schema_key(self):
        self.assertIn('  cancel-in-progress: false', self.text)
        self.assertNotIn('cancel_in_progress', self.text)
        self.assertIn('  group: framework-main-writer', self.text)

    def test_cycle_compass_prompts_are_externalized_not_lost(self):
        self.assertTrue(PRIMARY_PROMPT.exists())
        self.assertTrue(CONFLICT_PROMPT.exists())
        primary = PRIMARY_PROMPT.read_text(encoding='utf-8')
        conflict = CONFLICT_PROMPT.read_text(encoding='utf-8')
        self.assertIn('CYCLE_HEADER | PHASE=', primary)
        self.assertIn('PARABOLIC_ALTSEASON', primary)
        self.assertIn('action_compass_exit_calibration', primary)
        self.assertIn('premature late-cycle bearishness', conflict)
        self.assertIn('cp research/api_agent/prompts/DAILY_DIRECTOR_SHADOW.txt runtime/daily-director/prompt.txt', self.text)
        self.assertIn('cp research/api_agent/prompts/DAILY_CONFLICT_REVIEW.txt runtime/daily-director/conflict_prompt.txt', self.text)

    def test_optional_conflict_budget_cannot_discard_primary_output(self):
        marker = '- name: Enforce conflict-review lane and global budgets'
        start = self.text.index(marker)
        terra = self.text.index('- name: Run Terra conflict review', start)
        block = self.text[start:terra]
        self.assertIn('id: conflict_budget', block)
        self.assertIn('continue-on-error: true', block)
        terra_end = self.text.index('- name: Materialize immutable Director and optional conflict outputs', terra)
        terra_block = self.text[terra:terra_end]
        self.assertIn("steps.conflict_budget.outcome == 'success'", terra_block)

    def test_primary_materialization_and_readback_path_remain_unconditional(self):
        marker = '- name: Materialize immutable Director and optional conflict outputs'
        start = self.text.index(marker)
        end = self.text.index('- name: Register, scientifically admit, observe and dispatch experiment candidates', start)
        header = self.text[start:end].split('run:', 1)[0]
        self.assertNotIn('if:', header)
        self.assertIn('git merge-base --is-ancestor HEAD origin/main', self.text)


if __name__ == '__main__':
    unittest.main()
