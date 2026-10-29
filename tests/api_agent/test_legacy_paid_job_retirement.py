import re
import unittest
from pathlib import Path


WORKFLOW = Path(".github/workflows/api-agent-gateway-gate.yml")
PAID_PR_JOBS = (
    "terra-max-endgame-once",
    "terra-high-p0-once",
    "terra-max-p0-schedule-once",
    "terra-max-endgame-archive-batch1-20261027",
    "terra-high-shared-row-ci-fix-20261027",
    "terra-xhigh-task2-edge-readiness-20261027",
    "terra-xhigh-endgame-progress-v1",
)


def _job_if_expression(workflow: str, job: str) -> str:
    match = re.search(
        rf"^  {re.escape(job)}:\n(?P<body>.*?)(?=^  [a-z0-9][a-z0-9-]*:\n|\Z)",
        workflow,
        flags=re.MULTILINE | re.DOTALL,
    )
    if not match:
        raise AssertionError(f"missing workflow job: {job}")
    condition = re.search(
        r"^    if: >-\n(?P<expression>(?:      .*\n)+)",
        match.group("body"),
        flags=re.MULTILINE,
    )
    if not condition:
        raise AssertionError(f"missing job-level admission condition: {job}")
    return condition.group("expression")


class LegacyPaidJobRetirementTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workflow = WORKFLOW.read_text(encoding="utf-8")

    def _assert_all_paid_pr_jobs_are_terminally_disabled(self, workflow: str) -> None:
        for job in PAID_PR_JOBS:
            expression = _job_if_expression(workflow, job)
            self.assertRegex(expression, r"(?m)^      false &&$")

    def test_all_paid_pr_jobs_are_terminally_disabled(self) -> None:
        self._assert_all_paid_pr_jobs_are_terminally_disabled(self.workflow)

    def test_reactivation_mutation_is_detected(self) -> None:
        for job in PAID_PR_JOBS:
            with self.subTest(job=job):
                mutated = self.workflow.replace(
                    _job_if_expression(self.workflow, job),
                    _job_if_expression(self.workflow, job).replace("      false &&\n", "", 1),
                    1,
                )
                with self.assertRaises(AssertionError):
                    self._assert_all_paid_pr_jobs_are_terminally_disabled(mutated)

    def test_free_gateway_and_semantic_reporter_remain_available(self) -> None:
        gateway = _job_if_expression(self.workflow, "gateway-gate")
        self.assertNotRegex(gateway, r"(?m)^      false &&$")
        self.assertIn("scripts/api_agent/endgame_semantic_report.py", self.workflow)


if __name__ == "__main__":
    unittest.main()
