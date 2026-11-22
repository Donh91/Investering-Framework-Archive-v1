"""Mutation-sensitive tests for no-secret Astro BUILD job guards."""
from pathlib import Path
import re
import unittest

WF = Path(__file__).resolve().parents[2] / ".github/workflows/owner-astra-mission.yml"
JOB_NAMES = ("worklike-sandbox", "build-sandbox")
GATES = (
    "always()", "github.event_name == 'issue_comment'",
    "github.event.action == 'created'",
    "github.event.issue.number == 1156",
    "github.event.issue.pull_request == null",
    "github.event.comment.user.login == 'Donh91'",
    "github.actor == 'Donh91'",
    "github.event.comment.author_association == 'OWNER'",
    "github.ref == 'refs/heads/main'",
    "github.run_attempt == 1",
)


def job_section(source: str, job: str) -> str:
    marker = "\n  " + job + ":\n"
    if source.count(marker) != 1:
        raise AssertionError("JOB_MISSING_OR_DUPLICATED")
    block = source.split(marker, 1)[1]
    return re.split(r"\n  [a-z][a-z-]*:\n", block, maxsplit=1)[0]


def verify_job_contract(source: str, job: str):
    section = job_section(source, job)
    m = re.search(r"(?:^|\n)    if: >-\n(?P<expr>(?:      .*\n)+)", "\n" + section)
    if not m:
        raise AssertionError("JOB_IF_NOT_PINNED")
    expr = " ".join(x.strip() for x in m.group("expr").splitlines())
    for part in GATES:
        if part not in expr:
            raise AssertionError("JOB_GATE_MISSING_" + part)
    deps = "[paid, recover]" if job == "worklike-sandbox" else "[paid]"
    if "\n    needs: " + deps + "\n" not in "\n" + section:
        raise AssertionError("JOB_DEPENDENCY_CHANGED")
    if job == "build-sandbox" and "needs.paid.result == 'success'" not in expr:
        raise AssertionError("JOB_PAID_SUCCESS_REQUIRED")
    if job == "worklike-sandbox" and ("needs.paid.result == 'success'" not in expr
                                     or "needs.recover.result == 'success'" not in expr):
        raise AssertionError("JOB_RECOVER_SUCCESS_REQUIRED")
    pm = re.search(r"(?m)^    permissions:\n(?P<block>(?:^      .+\n)+)", section)
    if not pm or pm.group("block") != "      contents: read\n":
        raise AssertionError("JOB_PERMISSION_NOT_READ_ONLY")
    if "${{ secrets." in section or "GITHUB_TOKEN:" in section:
        raise AssertionError("JOB_NO_SECRET")
    if "${{ github.event.comment.body }" in section:
        raise AssertionError("JOB_UNTRUSTED_INTERPOLATION")
    download = re.search(r"(?m)^      - uses: actions/download-artifact@v4\n"
                         r"(?P<with>        with:\n(?:          .+\n)+)", section)
    if not download:
        raise AssertionError("JOB_DOWNLOAD_MISSING")
    details = download.group("with")
    if ("          name: astra-mission-evidence-${{ github.run_id }}\n" not in details
        or "run-id:" in details or "github-token:" in details
        or details.count("          name: ") != 1):
        raise AssertionError("JOB_CROSS_RUN_ARTIFACT")
    if "persist-credentials: false" not in section:
        raise AssertionError("JOB_PERSIST_CREDENTIALS")
    if job == "build-sandbox":
        image_step = section.find("Build source-reviewed hash-locked toolchain BEFORE any model artifacts")
        download_step = section.find("- uses: actions/download-artifact@v4")
        if image_step < 0 or download_step < 0 or image_step >= download_step:
            raise AssertionError("MODEL_BYTES_BEFORE_TOOLCHAIN")
        if "ASTRA_BUILD_IMAGE_ID=$image_id" not in section or "--pull never" not in section:
            raise AssertionError("TOOLCHAIN_ID_OR_LOCAL_ONLY_IMAGE")

    return True


class AstraBuildWorkflowSecurityTest(unittest.TestCase):
    def test_all_sandboxes_pinned(self):
        source = WF.read_text(encoding="utf-8")
        for job in JOB_NAMES:
            with self.subTest(job=job):
                self.assertTrue(verify_job_contract(source, job))

    def test_missing_run_attempt_denied(self):
        source = WF.read_text(encoding="utf-8")
        for job in JOB_NAMES:
            segment = job_section(source, job)
            edited = source.replace(segment,
                                    segment.replace("github.run_attempt == 1", "true"))
            with self.subTest(job=job), self.assertRaises(AssertionError):
                verify_job_contract(edited, job)

    def test_write_permission_denied(self):
        source = WF.read_text(encoding="utf-8")
        for job in JOB_NAMES:
            segment = job_section(source, job)
            edited = source.replace(segment, segment.replace(
                "      contents: read\n", "      contents: write\n"))
            with self.subTest(job=job), self.assertRaisesRegex(
                    AssertionError, "JOB_PERMISSION_NOT_READ_ONLY"):
                verify_job_contract(edited, job)

    def test_loading_model_before_toolchain_is_denied(self):
        source = WF.read_text(encoding="utf-8")
        segment = job_section(source, "build-sandbox")
        edited = source.replace(segment, segment.replace(
            "Build source-reviewed hash-locked toolchain BEFORE any model artifacts",
            "Build unreviewed image after model download"))
        with self.assertRaisesRegex(AssertionError, "MODEL_BYTES_BEFORE_TOOLCHAIN"):
            verify_job_contract(edited, "build-sandbox")

    def test_other_run_download_denied(self):
        source = WF.read_text(encoding="utf-8")
        for job in JOB_NAMES:
            segment = job_section(source, job)
            edited = source.replace(segment, segment.replace(
                "          name: astra-mission-evidence-${{ github.run_id }}\n",
                "          name: astra-mission-evidence-${{ github.run_id }}\n"
                "          run-id: 12345\n"))
            with self.subTest(job=job), self.assertRaisesRegex(
                    AssertionError, "JOB_CROSS_RUN_ARTIFACT"):
                verify_job_contract(edited, job)


if __name__ == "__main__":
    unittest.main()
