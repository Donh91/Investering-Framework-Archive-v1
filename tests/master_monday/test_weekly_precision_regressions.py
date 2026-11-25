from __future__ import annotations
import importlib.util
import copy
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module

preflight = load_module('mm_preflight_v3_precision', ROOT / 'scripts/master_monday/build_preflight_package_v3.py')
publisher = load_module('mm_publisher_precision', ROOT / 'scripts/master_monday/publish_master_monday_outputs.py')

class WeeklyPrecisionRegressionTests(unittest.TestCase):
    def test_labor_day_week_has_four_expected_sessions(self):
        self.assertEqual(
            preflight.expected_nyse_sessions(2026, 37),
            ['2026-09-08', '2026-09-09', '2026-09-10', '2026-09-11'],
        )

    def test_normal_week_has_five_expected_sessions(self):
        sessions = preflight.expected_nyse_sessions(2026, 36)
        self.assertEqual(len(sessions), 5)
        self.assertEqual(sessions[0], '2026-08-31')
        self.assertEqual(sessions[-1], '2026-09-04')

    def test_available_registry_with_incomplete_outcomes_is_not_called_unavailable(self):
        score = publisher.fallback_scorecard({
            'experiment_learning': {
                'status': 'AVAILABLE',
                'matured_outcome_evidence_available': False,
                'outcome_ingestion_status': 'INCOMPLETE',
                'new_matured_outcomes': None,
            }
        })
        self.assertEqual(score['experiment_registry_status'], 'AVAILABLE')
        self.assertEqual(score['status'], 'INCOMPLETE_EXPERIMENT_OUTCOME_INGESTION')
        self.assertEqual(score['outcome_ingestion_status'], 'INCOMPLETE')

    def test_missing_registry_still_fails_closed(self):
        score = publisher.fallback_scorecard({
            'experiment_learning': {
                'status': 'UNAVAILABLE_REGISTRY_MISSING',
                'matured_outcome_evidence_available': False,
                'new_matured_outcomes': None,
            }
        })
        self.assertEqual(score['status'], 'UNAVAILABLE_EXPERIMENT_REGISTRY')

    def test_api_success_and_verified_receipt_cannot_mask_missing_translation(self):
        score = publisher.fallback_scorecard({'experiment_learning': {
            'status': 'AVAILABLE', 'matured_outcome_evidence_available': True,
            'new_matured_outcomes': [{'outcome': 'MATURED'}],
        }})
        self.assertEqual(publisher.effective_delivery_status(
            'success', {'status': 'READY'}, {'status': 'UNAVAILABLE_API_CONTRACT'},
            score, True), 'DEGRADED')

    def test_readiness_requires_analysis_translation_scorecard_and_receipt(self):
        ready = {'status': 'READY'}
        for api_status, api, translation, scorecard, receipt in [
            ('failure', ready, ready, ready, True),
            ('success', {'status': 'BLOCKED'}, ready, ready, True),
            ('success', ready, ready, {'status': 'UNAVAILABLE_API_CONTRACT'}, True),
            ('success', ready, ready, ready, False),
            ('success', ready, ready, {'status': 'PENDING_MATURED_OUTCOMES',
                                      'experiment_registry_status': 'AVAILABLE',
                                      'matured_outcome_count': None}, True),
        ]:
            self.assertEqual(publisher.effective_delivery_status(
                api_status, api, translation, scorecard, receipt), 'DEGRADED')
        self.assertEqual(publisher.effective_delivery_status(
            'success', ready, ready, ready, True), 'READY')
        pending = publisher.fallback_scorecard({'experiment_learning': {
            'status': 'AVAILABLE', 'matured_outcome_evidence_available': True,
            'new_matured_outcomes': [],
        }})
        self.assertEqual(publisher.effective_delivery_status(
            'success', ready, ready, pending, True), 'READY')

    def scorecard_fixture(self):
        rows=[]
        for i,result in enumerate(('HIT','MISS','CENSORED')):
            rows.append({'source_contract':'MATURED_OUTCOME_v3','forecast_id':f'F{i}',
                'forecast_sha256':str(i)*64,'outcome_sha256':str(i+3)*64,'evidence_sha256':str(i+6)*64,
                'source_binding_verification':'CURRENT_FILE_CANONICAL_JSON_SHA256',
                'created_at_utc':'2026-11-20T12:00:00Z',
                'status':'CENSORED' if result=='CENSORED' else 'MATURED',
                'result':None if result=='CENSORED' else result,
                'return_pct':None if result=='CENSORED' else 1.0,
                'reason':'no target' if result=='CENSORED' else None,
                'path':'MUST_NOT_ESCAPE'})
        context={'contract':'WEEKLY_API_CALIBRATION_CONTEXT_v6','authority':'SHADOW_ONLY',
                 'freeze_sha256':'a'*64,'window_start_utc':'2026-11-16T00:00:00Z',
                 'window_end_utc':'2026-11-23T00:00:00Z','experiment_learning':{
                 'status':'AVAILABLE','authority':'SHADOW_ONLY_NO_AUTOMATIC_PROMOTION',
                 'registry_sha256':'b'*64,'matured_outcome_evidence_available':True,
                 'outcome_ingestion_status':'COMPLETE','outcome_ingestion_diagnostics':[],
                 'new_matured_outcomes':rows}}
        context['context_hash']=publisher.sha(context)
        return context

    def test_owner_outcome_counts_are_restored_but_not_full_readiness(self):
        context=self.scorecard_fixture()
        before=copy.deepcopy(context)
        score=publisher.fallback_scorecard(context)
        counts=score['analysis_layer']['experiment_outcome_counts']
        self.assertEqual(score['status'],'DEGRADED')
        self.assertEqual((counts['outcome_record_count'],counts['matured_outcome_count'],
                          counts['hit_count'],counts['miss_count'],counts['censored_count']),(3,2,1,1,1))
        self.assertEqual(counts['hit_fraction'],.5)
        self.assertIsNone(counts['independent_sample_size'])
        self.assertIsNone(counts['matched_baseline_skill'])
        self.assertFalse(counts['portfolio_action'])
        self.assertNotIn('MUST_NOT_ESCAPE',str(counts))
        self.assertNotIn('return_pct',str(counts))
        self.assertEqual(context,before)
        self.assertEqual(publisher.effective_delivery_status('success',{'status':'READY'},
                         {'status':'READY'},score,True),'DEGRADED')

    def test_scorecard_rejects_rehashed_bad_owner_rows_and_tampered_context(self):
        def reseal(c):
            c.pop('context_hash',None);c['context_hash']=publisher.sha(c)
        for mutate in (
            lambda r:r[0].update(return_pct=True),
            lambda r:r[0].update(result='UNKNOWN'),
            lambda r:r[0].update(created_at_utc='2026-11-23T00:00:00Z'),
            lambda r:r[0].update(source_binding_verification='UNVERIFIED'),
            lambda r:r[0].update(evidence_sha256='bad'),
            lambda r:r[1].update(forecast_id=r[0]['forecast_id']),
            lambda r:r[1].update(outcome_sha256=r[0]['outcome_sha256']),
            lambda r:r[2].update(return_pct=0),
        ):
            with self.subTest(mutation=mutate):
                c=self.scorecard_fixture()
                mutate(c['experiment_learning']['new_matured_outcomes'])
                reseal(c)
                self.assertEqual(publisher.fallback_scorecard(c)['analysis_layer'],{})
        c=self.scorecard_fixture()
        c['experiment_learning']['new_matured_outcomes'][0]['result']='MISS'
        self.assertEqual(publisher.fallback_scorecard(c)['analysis_layer'],{})

    def test_censored_only_is_not_a_zero_outcome_success(self):
        c=self.scorecard_fixture()
        c['experiment_learning']['new_matured_outcomes']=c['experiment_learning']['new_matured_outcomes'][2:]
        c.pop('context_hash');c['context_hash']=publisher.sha(c)
        score=publisher.fallback_scorecard(c)
        self.assertEqual(score['status'],'DEGRADED')
        self.assertIsNone(score['analysis_layer']['experiment_outcome_counts']['hit_fraction'])
        self.assertEqual(score['matured_outcome_count'],0)

if __name__ == '__main__':
    unittest.main()
