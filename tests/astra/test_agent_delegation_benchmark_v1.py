import importlib.util
import hashlib
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

MODULE = Path(__file__).resolve().parents[2] / 'scripts/astra/agent_delegation_benchmark_v1.py'
spec = importlib.util.spec_from_file_location('bench', MODULE)
bench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)
H = lambda k: format(k, '064x')
FIXTURES = {
    'question.txt': b'Frozen Task 2 question; demonstration only\n',
    'evidence.txt': b'Frozen synthetic public evidence; not real source\n',
    'exec-solo.json': b'{"arm":"SOLO", "demo":true}\n',
    'exec-delegated.json': b'{"arm":"DELEGATED", "demo":true}\n',
    'verify-solo.json': b'{"verified":"SOLO", "demo":true}\n',
    'verify-delegated.json': b'{"verified":"DELEGATED", "demo":true}\n',
}
SHA = lambda key: hashlib.sha256(FIXTURES[key]).hexdigest()


def make_case(evidence_class='PUBLIC_IMMUTABLE_RECEIPT'):
    def variant(mode, i):
        return dict(mode=mode, run_id=f'run-{i}', executor_id=f'executor-{i}', status='EXECUTED',
                    execution_receipt_sha256=SHA('exec-solo.json' if i==1 else 'exec-delegated.json'),
                    execution_receipt_path='exec-solo.json' if i==1 else 'exec-delegated.json',
                    verification=dict(method='INDEPENDENT_REVIEW', verifier_id=f'verifier-{i}',
                                      status='PASS', verification_receipt_sha256=SHA('verify-solo.json' if i==1 else 'verify-delegated.json'),
                                      verification_receipt_path='verify-solo.json' if i==1 else 'verify-delegated.json'),
                    usage=dict(input_tokens=200, output_tokens=100, cost_usd=0.1*i, wallclock_ms=1000*i),
                    outcome=dict(checks_passed=4+i, checks_total=10,
                                 verified_unique_evidence_count=i, material_falsifier_count=i-1),
                    delegation=dict(agent_count=i, question_hashes=[H(30+j) for j in range(i)]))
    return dict(contract='AGENT_DELEGATION_PAIRED_BENCHMARK_v1', research_only=True,
                registered_at_utc='2026-10-15T08:00:00Z', task_family='TASK2_PIT_SOURCE_REVIEW',
                cases=[dict(case_id='test-case', frozen_question_sha256=SHA('question.txt'), frozen_question_path='question.txt',
                            evidence_sha256=SHA('evidence.txt'), evidence_path='evidence.txt',
                            evidence_class=evidence_class,
                            variants=[variant('SOLO', 1), variant('DELEGATED', 2)])])


class Bench(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for name, content in FIXTURES.items():
            (self.root / name).write_bytes(content)

    def check(self, value):
        return bench.evaluate(value, receipt_root=self.root)

    def test_eligible_matched_pair(self):
        out=self.check(make_case())
        self.assertEqual(out['paired_eligible_count'], 0)
        self.assertEqual(out['byte_consistent_pair_count'], 1)
        self.assertTrue(out['rows'][0]['metadata_eligible'])
        self.assertFalse(out['rows'][0]['eligible'])
        self.assertEqual(out['rows'][0]['cost_delta_usd_delegated_minus_solo'], 0.1)
        self.assertFalse(out['causal_efficiency_improvement_established'])

    def test_fabricated_cost_and_outcomes_cannot_be_empirical(self):
        obj = make_case()
        for variant in obj['cases'][0]['variants']:
            variant['usage']['cost_usd'] = 0
            variant['outcome']['checks_passed'] = 10
            variant['outcome']['verified_unique_evidence_count'] = 99999
        out = self.check(obj)
        self.assertEqual(out['paired_eligible_count'], 0)
        self.assertEqual(out['status'], 'NO_ELIGIBLE_REAL_PAIRS')
        self.assertEqual(out['comparison_values'], 'SELF_REPORTED_UNAUTHENTICATED_NOT_EMPIRICAL')
        self.assertIn('EXTERNAL_AUTHENTICATION_NOT_ESTABLISHED', out['rows'][0]['reasons'])

    def test_relabelled_demo_receipts_are_not_empirical(self):
        out = self.check(make_case('PUBLIC_IMMUTABLE_RECEIPT'))
        self.assertEqual(out['byte_consistent_pair_count'], 1)
        self.assertEqual(out['paired_eligible_count'], 0)

    def assert_reused_receipt_not_metadata_eligible(self, obj):
        out = self.check(obj)
        self.assertEqual(out['paired_eligible_count'], 0)
        self.assertEqual(out['byte_consistent_pair_count'], 0)
        self.assertEqual(out['metadata_status'], 'NO_BYTE_CONSISTENT_PAIRS')
        self.assertFalse(out['rows'][0]['eligible'])
        self.assertFalse(out['rows'][0]['metadata_eligible'])
        self.assertFalse(any(k.endswith('_delegated_minus_solo') for k in out['rows'][0]))
        self.assertTrue(any('REUSED_RECEIPT' in x for x in out['rows'][0]['reasons']))

    def test_reused_receipt_is_not_empirical(self):
        obj = make_case()
        a,b = obj['cases'][0]['variants']
        b['execution_receipt_path'] = a['execution_receipt_path']
        b['execution_receipt_sha256'] = a['execution_receipt_sha256']
        self.assert_reused_receipt_not_metadata_eligible(obj)

    def test_reused_verification_receipt_path_not_metadata_eligible(self):
        obj = make_case()
        a,b = obj['cases'][0]['variants']
        b['verification']['verification_receipt_path'] = a['verification']['verification_receipt_path']
        b['verification']['verification_receipt_sha256'] = a['verification']['verification_receipt_sha256']
        self.assert_reused_receipt_not_metadata_eligible(obj)

    def test_same_execution_bytes_at_distinct_paths_not_metadata_eligible(self):
        obj = make_case()
        a,b = obj['cases'][0]['variants']
        self.assertNotEqual(a['execution_receipt_path'], b['execution_receipt_path'])
        (self.root / b['execution_receipt_path']).write_bytes(
            (self.root / a['execution_receipt_path']).read_bytes())
        b['execution_receipt_sha256'] = a['execution_receipt_sha256']
        self.assert_reused_receipt_not_metadata_eligible(obj)

    def test_same_verification_bytes_at_distinct_paths_not_metadata_eligible(self):
        obj = make_case()
        a,b = obj['cases'][0]['variants']
        ap = a['verification']['verification_receipt_path']
        bp = b['verification']['verification_receipt_path']
        self.assertNotEqual(ap, bp)
        (self.root / bp).write_bytes((self.root / ap).read_bytes())
        b['verification']['verification_receipt_sha256'] = a['verification']['verification_receipt_sha256']
        self.assert_reused_receipt_not_metadata_eligible(obj)

    def test_receipt_alias_same_file_not_metadata_eligible(self):
        obj = make_case()
        a,b = obj['cases'][0]['variants']
        (self.root / 'exec-solo-alias.json').symlink_to('exec-solo.json')
        b['execution_receipt_path'] = 'exec-solo-alias.json'
        b['execution_receipt_sha256'] = a['execution_receipt_sha256']
        self.assert_reused_receipt_not_metadata_eligible(obj)

    def test_cross_role_reused_receipt_not_metadata_eligible(self):
        obj = make_case()
        a,b = obj['cases'][0]['variants']
        b['verification']['verification_receipt_path'] = a['execution_receipt_path']
        b['verification']['verification_receipt_sha256'] = a['execution_receipt_sha256']
        self.assert_reused_receipt_not_metadata_eligible(obj)

    def test_same_execution_and_verification_receipt_within_solo(self):
        obj = make_case()
        solo = obj['cases'][0]['variants'][0]
        solo['verification']['verification_receipt_path'] = solo['execution_receipt_path']
        solo['verification']['verification_receipt_sha256'] = solo['execution_receipt_sha256']
        out = self.check(obj)
        self.assertFalse(out['rows'][0]['metadata_eligible'])
        self.assertEqual(out['byte_consistent_pair_count'], 0)
        self.assertIn('REUSED_RECEIPT_DIGEST_WITHIN_ARM:SOLO', out['rows'][0]['reasons'])
        self.assertIn('REUSED_RECEIPT_PATH_OR_ALIAS_WITHIN_ARM:SOLO', out['rows'][0]['reasons'])

    def test_same_verification_bytes_under_new_path_within_delegated(self):
        obj = make_case()
        delegated = obj['cases'][0]['variants'][1]
        execution = delegated['execution_receipt_path']
        alias = 'verify-clone-delegated.json'
        (self.root / alias).write_bytes((self.root / execution).read_bytes())
        delegated['verification']['verification_receipt_path'] = alias
        delegated['verification']['verification_receipt_sha256'] = delegated['execution_receipt_sha256']
        out = self.check(obj)
        self.assertEqual(out['byte_consistent_pair_count'], 0)
        self.assertIn('REUSED_RECEIPT_DIGEST_WITHIN_ARM:DELEGATED', out['rows'][0]['reasons'])

    def test_same_file_symlink_alias_within_delegated(self):
        obj = make_case()
        delegated = obj['cases'][0]['variants'][1]
        alias = 'verification-alias-delegated.json'
        (self.root / alias).symlink_to(delegated['execution_receipt_path'])
        delegated['verification']['verification_receipt_path'] = alias
        delegated['verification']['verification_receipt_sha256'] = delegated['execution_receipt_sha256']
        out = self.check(obj)
        self.assertEqual(out['byte_consistent_pair_count'], 0)
        self.assertIn('REUSED_RECEIPT_PATH_OR_ALIAS_WITHIN_ARM:DELEGATED', out['rows'][0]['reasons'])

    def make_independent_second_case(self, obj):
        second = deepcopy(obj['cases'][0])
        second['case_id'] = 'independent-second-case'
        for v in second['variants']:
            v['run_id'] += '-second'
            for record, path_key, sha_key in [
                (v, 'execution_receipt_path', 'execution_receipt_sha256'),
                (v['verification'], 'verification_receipt_path', 'verification_receipt_sha256'),
            ]:
                previous = record[path_key]
                fresh = 'independent-' + previous
                payload = (self.root / previous).read_bytes() + b' independent-second-case'
                (self.root / fresh).write_bytes(payload)
                record[path_key] = fresh
                record[sha_key] = hashlib.sha256(payload).hexdigest()
        obj['cases'].append(second)
        return second

    def test_second_case_cannot_disguise_prior_run_as_question(self):
        obj = make_case()
        second = self.make_independent_second_case(obj)
        original_receipt = obj['cases'][0]['variants'][0]
        second['frozen_question_path'] = original_receipt['execution_receipt_path']
        second['frozen_question_sha256'] = original_receipt['execution_receipt_sha256']
        out = self.check(obj)
        self.assertEqual(out['byte_consistent_pair_count'], 1)
        self.assertTrue(out['rows'][0]['metadata_eligible'])
        self.assertFalse(out['rows'][1]['metadata_eligible'])
        self.assertIn('REUSED_PRIOR_RECEIPT_AS_SOURCE_DIGEST:FROZEN_QUESTION', out['rows'][1]['reasons'])
        self.assertIn('REUSED_PRIOR_RECEIPT_AS_SOURCE_PATH_OR_ALIAS:FROZEN_QUESTION', out['rows'][1]['reasons'])

    def test_second_case_cannot_disguise_prior_source_as_run(self):
        obj = make_case()
        second = self.make_independent_second_case(obj)
        fresh_source = b'new independent evidence bundle for case two'
        (self.root / 'case-two-evidence.txt').write_bytes(fresh_source)
        second['evidence_path'] = 'case-two-evidence.txt'
        second['evidence_sha256'] = hashlib.sha256(fresh_source).hexdigest()
        first_evidence = obj['cases'][0]
        delegated = second['variants'][1]
        delegated['execution_receipt_path'] = first_evidence['evidence_path']
        delegated['execution_receipt_sha256'] = first_evidence['evidence_sha256']
        out = self.check(obj)
        self.assertEqual(out['byte_consistent_pair_count'], 1)
        self.assertFalse(out['rows'][1]['metadata_eligible'])
        self.assertIn('REUSED_PRIOR_SOURCE_AS_RECEIPT_DIGEST:EXECUTION_DELEGATED', out['rows'][1]['reasons'])
        self.assertIn('REUSED_PRIOR_SOURCE_AS_RECEIPT_PATH_OR_ALIAS:EXECUTION_DELEGATED', out['rows'][1]['reasons'])

    def test_opposite_arm_executors_cannot_independently_verify(self):
        obj = make_case()
        solo, delegated = obj['cases'][0]['variants']
        solo['verification']['verifier_id'] = delegated['executor_id']
        delegated['verification']['verifier_id'] = solo['executor_id']
        out = self.check(obj)
        self.assertFalse(out['rows'][0]['metadata_eligible'])
        self.assertEqual(out['byte_consistent_pair_count'], 0)
        self.assertIn('PAIR_EXECUTOR_USED_AS_INDEPENDENT_VERIFIER:SOLO', out['rows'][0]['reasons'])
        self.assertIn('PAIR_EXECUTOR_USED_AS_INDEPENDENT_VERIFIER:DELEGATED', out['rows'][0]['reasons'])

    def test_independent_second_case_still_counts_as_separate_pair(self):
        obj = make_case()
        self.make_independent_second_case(obj)
        out = self.check(obj)
        self.assertEqual(out['byte_consistent_pair_count'], 2)
        self.assertEqual(out['paired_eligible_count'], 0)
        self.assertTrue(all(row['metadata_eligible'] for row in out['rows']))

    def test_frozen_question_cannot_be_solo_execution_receipt(self):
        obj = make_case()
        case = obj['cases'][0]
        solo = case['variants'][0]
        solo['execution_receipt_path'] = case['frozen_question_path']
        solo['execution_receipt_sha256'] = case['frozen_question_sha256']
        out = self.check(obj)
        self.assertEqual(out['byte_consistent_pair_count'], 0)
        self.assertFalse(out['rows'][0]['metadata_eligible'])
        self.assertIn('REUSED_SOURCE_AS_RECEIPT_DIGEST:FROZEN_QUESTION_AS_EXECUTION_SOLO', out['rows'][0]['reasons'])

    def test_evidence_bundle_cannot_be_delegated_verification_receipt(self):
        obj = make_case()
        case = obj['cases'][0]
        delegated = case['variants'][1]
        delegated['verification']['verification_receipt_path'] = case['evidence_path']
        delegated['verification']['verification_receipt_sha256'] = case['evidence_sha256']
        out = self.check(obj)
        self.assertEqual(out['byte_consistent_pair_count'], 0)
        self.assertFalse(out['rows'][0]['metadata_eligible'])
        self.assertIn('REUSED_SOURCE_AS_RECEIPT_PATH_OR_ALIAS:EVIDENCE_BUNDLE_AS_VERIFICATION_DELEGATED', out['rows'][0]['reasons'])

    def test_copied_question_bytes_at_different_path_rejected(self):
        obj = make_case()
        case = obj['cases'][0]
        solo = case['variants'][0]
        cloned = 'execution-copy-of-question.txt'
        (self.root / cloned).write_bytes((self.root / case['frozen_question_path']).read_bytes())
        solo['execution_receipt_path'] = cloned
        solo['execution_receipt_sha256'] = case['frozen_question_sha256']
        out = self.check(obj)
        self.assertEqual(out['byte_consistent_pair_count'], 0)
        self.assertIn('REUSED_SOURCE_AS_RECEIPT_DIGEST:FROZEN_QUESTION_AS_EXECUTION_SOLO', out['rows'][0]['reasons'])

    def test_evidence_file_symlink_alias_as_receipt_rejected(self):
        obj = make_case()
        case = obj['cases'][0]
        solo = case['variants'][0]
        alias = 'evidence-as-receipt-symlink.txt'
        (self.root / alias).symlink_to(case['evidence_path'])
        solo['execution_receipt_path'] = alias
        solo['execution_receipt_sha256'] = case['evidence_sha256']
        out = self.check(obj)
        self.assertEqual(out['byte_consistent_pair_count'], 0)
        self.assertIn('REUSED_SOURCE_AS_RECEIPT_PATH_OR_ALIAS:EVIDENCE_BUNDLE_AS_EXECUTION_SOLO', out['rows'][0]['reasons'])

    def test_duplicate_pair_across_cases_counted_once(self):
        obj = make_case()
        copy = deepcopy(obj['cases'][0])
        copy['case_id'] = 'second-label-same-execution'
        obj['cases'].append(copy)
        out = self.check(obj)
        self.assertEqual(out['attempted_case_count'], 2)
        self.assertEqual(out['byte_consistent_pair_count'], 1)
        self.assertFalse(out['rows'][1]['metadata_eligible'])
        self.assertTrue(any('ACROSS_CASES' in r for r in out['rows'][1]['reasons']))

    def test_shared_one_arm_across_cases_cannot_inflate_pairs(self):
        obj = make_case()
        copy = deepcopy(obj['cases'][0])
        copy['case_id'] = 'partial-reuse'
        # Give delegated arm an independent execution and receipt so only SOLO
        # reuses a prior run. It still must not count as another paired sample.
        copy['variants'][1]['run_id'] = 'independent-delegated-id'
        self.tmp_delegated = b'{"arm":"new-delegated"}\\n'
        self.tmp_verified = b'{"verification":"new-delegated"}\\n'
        (self.root / 'exec-second.json').write_bytes(self.tmp_delegated)
        (self.root / 'verify-second.json').write_bytes(self.tmp_verified)
        copy['variants'][1]['execution_receipt_path'] = 'exec-second.json'
        copy['variants'][1]['execution_receipt_sha256'] = hashlib.sha256(self.tmp_delegated).hexdigest()
        copy['variants'][1]['verification']['verification_receipt_path'] = 'verify-second.json'
        copy['variants'][1]['verification']['verification_receipt_sha256'] = hashlib.sha256(self.tmp_verified).hexdigest()
        obj['cases'].append(copy)
        out = self.check(obj)
        self.assertEqual(out['byte_consistent_pair_count'], 1)
        self.assertIn('REUSED_RUN_ID_ACROSS_CASES:run-1', out['rows'][1]['reasons'])

    def test_independent_second_case_is_distinct_metadata_pair(self):
        obj = make_case()
        copy = deepcopy(obj['cases'][0])
        copy['case_id'] = 'independent-case'
        for v in copy['variants']:
            v['run_id'] += '-new'
            for typ, path_key, sha_key in [
                (v, 'execution_receipt_path', 'execution_receipt_sha256'),
                (v['verification'], 'verification_receipt_path', 'verification_receipt_sha256'),
            ]:
                oldpath = typ[path_key]
                newpath = 'second-' + oldpath
                newbytes = self.root.joinpath(oldpath).read_bytes() + b'second-case'
                self.root.joinpath(newpath).write_bytes(newbytes)
                typ[path_key] = newpath
                typ[sha_key] = hashlib.sha256(newbytes).hexdigest()
        obj['cases'].append(copy)
        out = self.check(obj)
        self.assertEqual(out['attempted_case_count'], 2)
        self.assertEqual(out['byte_consistent_pair_count'], 2)
        self.assertFalse(any('ACROSS_CASES' in r for row in out['rows'] for r in row['reasons']))
        self.assertEqual(out['paired_eligible_count'], 0)

    def test_empty_denominator_is_ineligible(self):
        obj = make_case()
        for variant in obj['cases'][0]['variants']:
            variant['outcome']['checks_total'] = 0
            variant['outcome']['checks_passed'] = 0
        out = self.check(obj)
        self.assertFalse(out['rows'][0]['metadata_eligible'])
        self.assertIn('EMPTY_CHECK_DENOMINATOR', out['rows'][0]['reasons'])

    def test_missing_receipt_root_is_not_eligible(self):
        out = bench.evaluate(make_case())
        self.assertEqual(out['paired_eligible_count'], 0)
        self.assertIn('SOLO_EXECUTION:RECEIPT_ROOT_NOT_PROVIDED', out['rows'][0]['reasons'])

    def test_changed_receipt_bytes_rejected(self):
        (self.root / 'exec-delegated.json').write_bytes(b'new dishonest bytes')
        out = self.check(make_case())
        self.assertEqual(out['paired_eligible_count'], 0)
        self.assertIn('DELEGATED_EXECUTION:HASH_MISMATCH', out['rows'][0]['reasons'])

    def test_changed_frozen_question_rejected(self):
        (self.root / 'question.txt').write_bytes(b'changed hypothesis')
        out = self.check(make_case())
        self.assertIn('FROZEN_QUESTION:HASH_MISMATCH', out['rows'][0]['reasons'])

    def test_changed_evidence_bytes_rejected(self):
        (self.root / 'evidence.txt').write_bytes(b'changed evidence')
        out = self.check(make_case())
        self.assertIn('EVIDENCE_BUNDLE:HASH_MISMATCH', out['rows'][0]['reasons'])

    def test_missing_verification_file_rejected(self):
        (self.root / 'verify-delegated.json').unlink()
        out = self.check(make_case())
        self.assertIn('DELEGATED_VERIFICATION:SOURCE_FILE_MISSING', out['rows'][0]['reasons'])

    def test_unmatched_checks_denominator_ineligible(self):
        obj = make_case()
        obj['cases'][0]['variants'][1]['outcome']['checks_total']=12
        out = self.check(obj)
        self.assertIn('UNMATCHED_CHECK_DENOMINATOR', out['rows'][0]['reasons'])

    def test_traversal_outside_root_rejected(self):
        obj = make_case()
        obj['cases'][0]['evidence_path']='../../secret'
        with self.assertRaises(bench.ContractError): self.check(obj)

    def test_symlink_outside_root_rejected(self):
        import os
        (self.root / 'external-file').symlink_to('/etc/hosts')
        obj=make_case()
        obj['cases'][0]['evidence_path']='external-file'
        with self.assertRaises(bench.ContractError): self.check(obj)

    def test_duplicate_arm_run_id_rejected(self):
        obj=make_case()
        obj['cases'][0]['variants'][1]['run_id']='run-1'
        with self.assertRaises(bench.ContractError): self.check(obj)

    def test_fixture_never_counted_empirically(self):
        out=self.check(make_case('SYNTHETIC_FIXTURE'))
        self.assertEqual(out['status'], 'NO_ELIGIBLE_REAL_PAIRS')
        self.assertIn('SYNTHETIC_NOT_EMPIRICAL', out['rows'][0]['reasons'])

    def test_no_phantom_success_when_no_receipt(self):
        obj=make_case(); obj['cases'][0]['variants'][1]['execution_receipt_sha256']=None
        out=self.check(obj)
        self.assertEqual(out['paired_eligible_count'],0)
        self.assertIn('DELEGATED:MISSING_EXECUTION_RECEIPT',out['rows'][0]['reasons'])

    def test_unknown_cost_does_not_become_free(self):
        obj=make_case(); obj['cases'][0]['variants'][1]['usage']['cost_usd']=None
        self.assertEqual(self.check(obj)['paired_eligible_count'],0)

    def test_unverified_does_not_count(self):
        obj=make_case(); obj['cases'][0]['variants'][0]['verification']['status']='NOT_VERIFIED'
        self.assertEqual(self.check(obj)['paired_eligible_count'],0)

    def test_duplicate_scope_rejected(self):
        obj=make_case(); obj['cases'][0]['variants'][1]['delegation']['question_hashes']=[H(31),H(31)]
        with self.assertRaises(bench.ContractError): self.check(obj)

    def test_same_model_cannot_self_review(self):
        obj=make_case(); obj['cases'][0]['variants'][1]['verification']['verifier_id']='executor-2'
        with self.assertRaises(bench.ContractError): self.check(obj)

    def test_unbounded_swarm_rejected(self):
        obj=make_case(); obj['cases'][0]['variants'][1]['delegation']={'agent_count':100,'question_hashes':[H(30+i) for i in range(100)]}
        with self.assertRaises(bench.ContractError): self.check(obj)

    def test_wrong_contract_rejected(self):
        obj=make_case(); obj['contract']='AGENT_TRADER'
        with self.assertRaises(bench.ContractError): self.check(obj)

    def test_restricted_raw_data_not_in_allowed_schema(self):
        obj=make_case(); obj['cases'][0]['raw_wallet_keys']=['no']
        with self.assertRaises(bench.ContractError): self.check(obj)

    def test_duplicate_case_rejected(self):
        obj=make_case(); obj['cases'].append(deepcopy(obj['cases'][0]))
        with self.assertRaises(bench.ContractError): self.check(obj)

    def test_huge_integer_cost_is_contract_error(self):
        obj=make_case(); obj['cases'][0]['variants'][1]['usage']['cost_usd']=10**400
        with self.assertRaises(bench.ContractError): self.check(obj)

    def test_nonfinite_cost_rejected(self):
        obj=make_case(); obj['cases'][0]['variants'][1]['usage']['cost_usd']=float('nan')
        with self.assertRaises(bench.ContractError): self.check(obj)


if __name__ == '__main__': unittest.main()
