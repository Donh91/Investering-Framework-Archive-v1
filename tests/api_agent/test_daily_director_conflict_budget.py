from pathlib import Path
import unittest


WORKFLOW = Path('.github/workflows/daily-director-shadow.yml')


class DailyDirectorConflictBudgetWiringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW.read_text()

    def test_conflict_lane_keeps_hard_budget_gate_without_failing_primary_director(self):
        marker = '- name: Enforce conflict-review lane and global budgets'
        start = self.text.index(marker)
        end = self.text.index('- name: Run Terra conflict review', start)
        block = self.text[start:end]
        self.assertIn('id: conflict_budget', block)
        self.assertIn('continue-on-error: true', block)
        self.assertIn('check_api_lane_budget.py', block)
        self.assertIn('--task DAILY_CONFLICT_REVIEW', block)
        self.assertIn('check_monthly_cost_guard.py', block)

    def test_budget_hold_is_recorded_and_terra_cannot_run_when_gate_fails(self):
        self.assertIn("router['review_status']='SKIPPED_BUDGET_GUARD'", self.text)
        self.assertIn("router['review_budget_gate']='BLOCKED'", self.text)
        terra_start = self.text.index('- name: Run Terra conflict review')
        terra_end = self.text.index('- name: Materialize immutable Director and optional conflict outputs', terra_start)
        terra = self.text[terra_start:terra_end]
        self.assertIn("steps.conflict_budget.outcome == 'success'", terra)

    def test_primary_materialization_is_not_conditioned_on_optional_conflict_review(self):
        start = self.text.index('- name: Materialize immutable Director and optional conflict outputs')
        end = self.text.index('- name: Register, scientifically admit, observe and dispatch experiment candidates', start)
        block = self.text[start:end]
        before_run = block.split('run:', 1)[0]
        self.assertNotIn('if:', before_run)
        self.assertIn('DAILY_DIRECTOR_OUTPUT.json', block)
        self.assertIn('API_CONFLICT_ROUTER.json', block)


if __name__ == '__main__':
    unittest.main()
