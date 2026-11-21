"""Independent host XML *parsing*, not independent test attestation."""
import unittest
from scripts.api_agent import astra_build_preflight_v1 as a

def junit(rows, *, suite=True):
    items = []
    for cls, name, outcome in rows:
        value = f'<testcase classname="{cls}" name="{name}">'
        if outcome:
            value += f'<{outcome} message="synthetic"/>'
        value += '</testcase>'
        items.append(value)
    content = "".join(items)
    return (f'<testsuite tests="{len(rows)}">{content}</testsuite>').encode()

BASE = junit([("test_alpha", "test_one", None),
              ("test_alpha", "test_two", None)])
SUCCESS = junit([("test_alpha", "test_one", None),
                 ("test_alpha", "test_two", None),
                 ("test_new", "test_three", None)])

class TestPreflight(unittest.TestCase):
    def run_preflight(self, candidate=SUCCESS, **kw):
        args = {"baseline_exit": 0, "candidate_exit": 0,
                "docker_network": "none", "exact_main": True}
        args.update(kw)
        return a.safe_preflight(BASE, candidate, **args)

    def test_positive_is_only_prefilter(self):
        item = self.run_preflight()
        self.assertEqual(item["status"], "PREFLIGHT_PASS")
        self.assertEqual(item["baseline_count"], 2)
        self.assertFalse(item["candidate_test_completion_attested"])
        self.assertFalse(item["paid_or_merge_authority"])
        self.assertEqual(item["independent_test_authority"],
                         "EXACT_HEAD_NATIVE_GITHUB_CI_ON_OUTPUT_PR")

    def test_missing_baseline_node_is_fail(self):
        result = self.run_preflight(junit([("test_alpha", "test_one", None)]))
        self.assertEqual(result["status"], "PREFLIGHT_FAIL")
        self.assertEqual(result["missing_baseline_nodes"], 1)

    def test_skipped_or_xfailed_is_fail(self):
        for status in ("skipped", "failure", "error"):
            with self.subTest(status=status):
                result = self.run_preflight(junit([
                    ("test_alpha", "test_one", None),
                    ("test_alpha", "test_two", status)]))
                self.assertEqual(result["status"], "PREFLIGHT_FAIL")

    def test_no_xml_early_exit_is_hold(self):
        result = self.run_preflight(b"")
        self.assertEqual(result["status"], "PREFLIGHT_HOLD")
        self.assertEqual(result["reason"], "JUNIT_INPUT_BOUNDS")

    def test_exit_zero_is_not_a_substitute_for_suite_xml(self):
        candidate = b'<?xml version="1.0"?><testsuite tests="0"/>'
        result = self.run_preflight(candidate)
        self.assertEqual(result["status"], "PREFLIGHT_HOLD")

    def test_nonzero_candidate_is_fail(self):
        self.assertEqual(self.run_preflight(candidate_exit=1)["status"], "PREFLIGHT_FAIL")

    def test_baseline_not_green_blocks(self):
        self.assertEqual(self.run_preflight(baseline_exit=1)["status"], "PREFLIGHT_HOLD")

    def test_untrusted_dtd_is_hold(self):
        xml = b'<!DOCTYPE test [ <!ENTITY a "x"> ]><testsuite><testcase classname="a" name="b"/></testsuite>'
        self.assertEqual(self.run_preflight(xml)["status"], "PREFLIGHT_HOLD")

    def test_duplicate_junit_node_is_hold(self):
        repeated = junit([("a", "b", None), ("a", "b", None)])
        self.assertEqual(self.run_preflight(repeated)["status"], "PREFLIGHT_HOLD")

    def test_network_and_main_binding_cannot_be_weakened(self):
        self.assertEqual(self.run_preflight(docker_network="bridge")["status"],
                         "PREFLIGHT_HOLD")
        self.assertEqual(self.run_preflight(exact_main=False)["status"], "PREFLIGHT_HOLD")

    def test_ceiling_is_hard(self):
        large = b"<testsuite>" + b" " * a.MAX_JUNIT_BYTES + b"</testsuite>"
        self.assertEqual(self.run_preflight(large)["status"], "PREFLIGHT_HOLD")

if __name__ == "__main__":
    unittest.main()
