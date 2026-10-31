"""W1 independent negative tests, synthetic only, zero external network/keys."""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from tools.produce_synthetic import issue_receipt, DEFAULT_SCHEMA, TEST_DATA
from tools.validate_receipt import validate_document, RejectedReceipt
from tools.public_guard import guard_workflow, guard_repository, UnsafePublicWorkflow, WORKFLOW

ROOT = Path(__file__).resolve().parents[1]


class TestReceiptV1(unittest.TestCase):
    def setUp(self) -> None:
        self.valid = issue_receipt()

    def check_bad(self, edit) -> None:
        candidate = copy.deepcopy(self.valid)
        edit(candidate)
        with self.assertRaises((RejectedReceipt, ValueError)):
            validate_document(candidate, DEFAULT_SCHEMA)

    def test_valid_schema_and_semantics(self) -> None:
        validate_document(self.valid, DEFAULT_SCHEMA)

    def test_never_owner_admission(self) -> None:
        self.check_bad(lambda x: x.update(deployment_stage="OWNER_ADMITTED_PUBLIC_SOURCE"))

    def test_never_real_source_in_w1(self) -> None:
        self.check_bad(lambda x: x.update(source_class="PUBLIC_CHAIN_RPC"))

    def test_watchlist_boolean_cannot_be_true(self) -> None:
        self.check_bad(lambda x: x["privacy"].update(user_selected_watchlist_present=True))

    def test_nested_private_field_cannot_be_added(self) -> None:
        self.check_bad(lambda x: x["clock"].update(my_wallet="0xdeadbeef"))

    def test_root_private_field_cannot_be_added(self) -> None:
        self.check_bad(lambda x: x.update(score=10))

    def test_wrong_source_id_rejected(self) -> None:
        self.check_bad(lambda x: x.update(source_id="WATCHLIST_TOKEN_1"))

    def test_wrong_public_repo_rejected(self) -> None:
        self.check_bad(lambda x: x["collector"].update(public_repo="Donh91/secrets"))

    def test_wrong_chain_rejected(self) -> None:
        self.check_bad(lambda x: x.update(chain_id=1))

    def test_wrong_factory_contract_rejected(self) -> None:
        self.check_bad(lambda x: x["collector"].update(source_contract_id="PRIVATE_SCORE_V1"))

    def test_false_first_known_claim_rejected(self) -> None:
        self.check_bad(lambda x: x["provenance_claims"].update(original_machine_first_known_certified=True))

    def test_false_import_safe_rejected(self) -> None:
        self.check_bad(lambda x: x["provenance_claims"].update(safe_for_private_import=True))

    def test_false_market_permission_rejected(self) -> None:
        self.check_bad(lambda x: x["provenance_claims"].update(private_signal_or_trade_permission=True))

    def test_schema_digest_tamper_rejected(self) -> None:
        self.check_bad(lambda x: x["collector"].update(schema_sha256="a" * 64))

    def test_source_data_digest_tamper_rejected(self) -> None:
        self.check_bad(lambda x: x.update(source_data_sha256="a" * 64))

    def test_git_head_mismatch_rejected(self) -> None:
        self.check_bad(lambda x: x["github"].update(head_sha40="c" * 40))

    def test_unsupported_event_rejected(self) -> None:
        self.check_bad(lambda x: x["github"].update(event="schedule"))

    def test_silent_gap_in_complete_range_rejected(self) -> None:
        self.check_bad(lambda x: x["coverage"].update(missing_ranges_count=1))

    def test_shorter_completed_range_rejected(self) -> None:
        self.check_bad(lambda x: x["coverage"].update(blocks_completed=3))

    def test_impossible_safe_head_rejected(self) -> None:
        self.check_bad(lambda x: x["coverage"].update(safe_head_block=3))

    def test_overstated_range_rejected(self) -> None:
        self.check_bad(lambda x: x["coverage"].update(end_block=5))

    def test_future_capture_past_completion_rejected(self) -> None:
        self.check_bad(lambda x: x["clock"].update(first_observed_at_utc="2026-11-02T10:00:00Z"))

    def test_missing_clock_provenance_rejected(self) -> None:
        self.check_bad(lambda x: x["clock"].pop("clock_limitations"))

    def test_nonzero_events_in_synthetic_rejected(self) -> None:
        self.check_bad(lambda x: x.update(event_count=1))

    def test_invalid_source_run_zero_rejected(self) -> None:
        self.check_bad(lambda x: x["github"].update(run_id=0))

    def test_fractional_clock_six_digits_allowed(self) -> None:
        self.valid["clock"]["first_observed_at_utc"] = self.valid["clock"]["first_observed_at_utc"].replace("Z", ".123456Z")
        # Original job clock timestamps are identical, so changing only T0
        # makes clock ordering inconsistent; schema alone must still admit it.
        from jsonschema import Draft202012Validator
        schema = json.loads(DEFAULT_SCHEMA.read_text())
        self.assertEqual(list(Draft202012Validator(schema).iter_errors(self.valid)), [])

    def test_fractional_clock_seven_digits_rejected(self) -> None:
        self.check_bad(lambda x: x["clock"].update(first_observed_at_utc="2026-10-31T12:00:00.1234567Z"))

    def test_fractional_clock_nineteen_digits_rejected(self) -> None:
        self.check_bad(lambda x: x["github"].update(job_started_at_utc="2026-10-31T12:00:00.1234567890123456789Z"))

    def test_actual_jsonschema_draft_202012_check(self) -> None:
        from jsonschema import Draft202012Validator
        raw = json.loads(DEFAULT_SCHEMA.read_text())
        Draft202012Validator.check_schema(raw)
        self.assertEqual(list(Draft202012Validator(raw).iter_errors(self.valid)), [])


class TestPublicWorkflowGuard(unittest.TestCase):
    def setUp(self) -> None:
        self.workflow = (ROOT / WORKFLOW).read_text()

    def reject(self, raw: str) -> None:
        with self.assertRaises(UnsafePublicWorkflow):
            guard_workflow(raw)

    def test_actual_workflow_passes(self) -> None:
        guard_repository(ROOT)

    def test_secret_reference_fails_even_as_new_key(self) -> None:
        self.reject(self.workflow.replace('    runs-on: ubuntu-latest', '    env:\n      API_KEY: ${{ secrets.API_KEY }}\n    runs-on: ubuntu-latest', 1))

    def test_privileged_pull_request_target_fails(self) -> None:
        self.reject(self.workflow.replace('  pull_request:', '  pull_request_target:'))

    def test_privileged_workflow_run_fails(self) -> None:
        self.reject(self.workflow.replace('  pull_request:', '  workflow_run:'))

    def test_cron_not_activated(self) -> None:
        self.reject(self.workflow.replace('  workflow_dispatch:', "  schedule:\n    - cron: '7 * * * *'\n  workflow_dispatch:"))

    def test_write_permissions_fail(self) -> None:
        self.reject(self.workflow.replace('  contents: read', '  contents: write'))

    def test_oidc_permissions_fail(self) -> None:
        self.reject(self.workflow.replace('  contents: read', '  contents: read\n  id-token: write'))

    def test_unpinned_action_fails(self) -> None:
        self.reject(self.workflow.replace('actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683', 'actions/checkout@v4'))

    def test_checkout_credentials_fail(self) -> None:
        self.reject(self.workflow.replace('persist-credentials: false', 'persist-credentials: true'))

    def test_external_run_command_fails(self) -> None:
        self.reject(self.workflow.replace('python -m tools.produce_synthetic --out /tmp/w1-synthetic.json', 'curl https://example.invalid/secret'))

    def test_private_dispatch_event_fails(self) -> None:
        self.reject(self.workflow.replace('  workflow_dispatch:', '  repository_dispatch:'))

    def test_incorrect_repository_scope_fails(self) -> None:
        self.reject(self.workflow.replace("github.repository == 'Donh91/investering-public-compute'", "github.repository == 'Donh91/Meme-Alpha-Lab'"))

    def test_untrusted_env_var_on_step_fails(self) -> None:
        self.reject(self.workflow.replace('      - name: Install pinned security test libraries', "      - name: Install pinned security test libraries\n        env:\n          H: ${{ github.event.pull_request.title }}"))

    def test_writer_step_injected_fails(self) -> None:
        self.reject(self.workflow.replace('      - name: Validate synthetic-only source receipt', "      - name: Git push\n        run: git push origin main\n      - name: Validate synthetic-only source receipt"))

    def test_unknown_job_fails(self) -> None:
        self.reject(self.workflow.replace('jobs:\n', 'jobs:\n  malicious:\n    runs-on: ubuntu-latest\n    steps: []\n'))

    def test_workflow_name_bidi_rejected(self) -> None:
        self.reject(self.workflow.replace(
            'name: W1 Public Compute Synthetic Security Only',
            'name: W1\u202e Public Compute Synthetic Security Only', 1,
        ))

    def test_step_expression_name_rejected(self) -> None:
        source = self.workflow.replace(
            'name: Install pinned security test libraries',
            'name: "${{ github.event.pull_request.title }}"', 1,
        )
        with self.assertRaisesRegex(UnsafePublicWorkflow, 'W1_STEP_NAME_UNSAFE'):
            guard_workflow(source)

    def test_different_arbitrary_ascii_step_name_rejected(self) -> None:
        self.reject(self.workflow.replace('name: Install pinned security test libraries',
                                          'name: Approved by Grok', 1))

    def test_malformed_uses_list_is_typed_denial(self) -> None:
        src = self.workflow.replace('uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # pinned v4.2.2',
                                    'uses: [a]', 1)
        with self.assertRaisesRegex(UnsafePublicWorkflow, 'W1_MALFORMED_STRUCTURE'):
            guard_workflow(src)

    def test_complex_yaml_mapping_key_is_typed_denial(self) -> None:
        src = self.workflow.replace('permissions:\n', 'permissions:\n  ? [a]\n  : 1\n', 1)
        with self.assertRaisesRegex(UnsafePublicWorkflow, 'W1_MALFORMED_STRUCTURE'):
            guard_workflow(src)

    def test_pip_does_not_allow_unhashed_installs(self) -> None:
        self.reject(self.workflow.replace('--require-hashes', '', 1))
        self.reject(self.workflow.replace('--only-binary=:all:', '', 1))

    def test_hashed_dependency_lock_complete_and_well_formed(self) -> None:
        import re
        names = set()
        for line in (ROOT / 'requirements-ci.txt').read_text().splitlines():
            if not line or line.startswith('#'):
                continue
            m = re.fullmatch(r'([A-Za-z0-9-]+)==([0-9.]+) --hash=sha256:([0-9a-f]{64})', line)
            self.assertIsNotNone(m, msg=f'unhashed dependency: {line[:40]}')
            names.add(m.group(1).lower())
        self.assertEqual(names, {
            'jsonschema','pyyaml','attrs','referencing','rpds-py',
            'jsonschema-specifications','typing-extensions',
        })

    def test_duplicate_yaml_keys_rejected(self) -> None:
        # A stricter YAML parser is required to reject duplicates, rather than
        # silently accepting the final key. The first key must not grant rights.
        self.reject(self.workflow.replace('permissions:\n', 'permissions:\n  contents: write\npermissions:\n', 1))


if __name__ == "__main__":
    unittest.main()
