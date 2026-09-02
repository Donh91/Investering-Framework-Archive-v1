from __future__ import annotations
import importlib.util,json,subprocess,tempfile,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def prospective_candidate(candidate_id,payload):
    return {
        'contract':'FORECAST_CANDIDATE_v1','candidate_id':candidate_id,'ratification_status':'PENDING',
        'created_at_utc':'2026-09-02T10:10:00Z','self_promotion_allowed':False,
        'model':'luna','task':'DAILY_DIRECTOR_SHADOW','prompt_sha256':'p','context_sha256':'c','source_output_sha256':'o',
        'candidate':payload,
    }

def owner_packet(freezer,candidate):
    return {
        'contract':'FORECAST_RATIFICATION_PACKET_v2','candidate_id':candidate['candidate_id'],
        'candidate_sha256':freezer.digest(candidate),'decision':'RATIFY','decision_at_utc':'2026-09-02T10:20:00Z',
        'authority':'CHATGPT_FRAMEWORK_OWNER','owner_actor':'continuity-test-owner','outcome_blind':True,
        'self_promotion_allowed':False,'prospective_cutover_commit_sha':'4057fde279ed0d8eea2df07da10543bda38ee8f8',
        'decision_basis_scope':['RATIFICATION_QUEUE','CANDIDATE_RECORD'],'outcome_paths_read':[],
        'decision_rationale':'Prospective fixture decision using candidate and queue only.',
    }

class ContinuityLearningTests(unittest.TestCase):
    def test_metric_bearing_predecessor_skips_v1(self):
        m=load_module('ctx',Path('scripts/api_agent/build_owner_bound_director_context.py'))
        latest={'contract':'DAILY_RAW_CAPTURE_INDEX_v2','captured_at_utc':'2026-08-03T10:00:00Z','run_id':'new','market_metrics':{'x':2},'owners':[]}
        old_v2={'contract':'DAILY_RAW_CAPTURE_INDEX_v2','captured_at_utc':'2026-08-03T06:00:00Z','run_id':'metric','market_metrics':{'x':1},'owners':[]}
        v1={'contract':'DAILY_RAW_CAPTURE_INDEX_v1','captured_at_utc':'2026-08-03T09:00:00Z','run_id':'v1','market_metrics':{},'owners':[]}
        c=m.build_context([(Path('a'),old_v2),(Path('b'),v1),(Path('c'),latest)])
        self.assertEqual(c['previous_capture']['run_id'],'metric');self.assertEqual(c['coverage']['comparable_numeric_metrics'],1);self.assertEqual(c['delta_status'],'DELTA_READY')

    def test_raw_payload_is_recoverable(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d);owner=r/'owner';owner.mkdir();(owner/'payload.json').write_text('{"x":1}\n')
            out=r/'raw';p=subprocess.run(['python',str(ROOT/'scripts/daily_capture/persist_raw_payloads.py'),'--run-id','test','--output-root',str(out),str(owner)],text=True,capture_output=True)
            self.assertEqual(p.returncode,0,p.stderr);man=list(out.rglob('RAW_MANIFEST_test.json'));self.assertEqual(len(man),1);v=json.loads(man[0].read_text());self.assertEqual(v['contract'],'RAW_OWNER_PAYLOAD_MANIFEST_v2');self.assertTrue(Path(v['archives'][0]['archive_path']).exists());self.assertGreater(v['monthly_limit_bytes'],0)

    def test_raw_monthly_guard_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d);owner=r/'owner';owner.mkdir();(owner/'payload.json').write_text('{"x":1}\n')
            out=r/'raw';p=subprocess.run(['python',str(ROOT/'scripts/daily_capture/persist_raw_payloads.py'),'--run-id','blocked','--output-root',str(out),'--max-monthly-compressed-bytes','1',str(owner)],text=True,capture_output=True)
            self.assertNotEqual(p.returncode,0);incidents=list((out/'incidents').glob('RAW_STORAGE_blocked.json'));self.assertEqual(len(incidents),1);v=json.loads(incidents[0].read_text());self.assertEqual(v['status'],'BLOCKED');self.assertEqual(v['required_action'],'MIGRATE_RAW_LANE_TO_DEDICATED_DATA_REPOSITORY')

    def test_gateway_schema_contains_explicit_target_units(self):
        m=load_module('gateway',Path('scripts/api_agent/api_gateway.py'));schema=m.output_schema();branches=schema['properties']['forecast_candidates']['items']['anyOf'];self.assertIn('forecast_candidates',schema['required']);self.assertEqual(len(branches),3);self.assertTrue(all('target_mode' in branch['required'] for branch in branches));self.assertTrue(all('threshold_pct' in branch['properties'] for branch in branches));self.assertTrue(all('target_value' in branch['properties'] for branch in branches));self.assertTrue(all('threshold' not in branch['properties'] for branch in branches))
        m.validate_output({'status':'READY','summary':'x','evidence_for':[],'evidence_against':[],'uncertainties':[],'hypotheses':[],'forecast_candidates':[{'metric_path':'market_metrics.x','direction':'UP','target_mode':'PCT_MOVE','threshold_pct':1.0,'target_value':None,'range_low':None,'range_high':None,'horizon_days':7,'rationale':'test'}]})

    def test_ratification_absolute_target_is_normalized_before_freeze(self):
        freezer=load_module('continuity_freezer_target',Path('scripts/learning/forecast_ratification_freezer.py'))
        with tempfile.TemporaryDirectory() as d:
            r=Path(d);out=r/'frozen';base_path=r/'baseline.json'
            candidate=prospective_candidate('c1',{'metric_path':'market.x','direction':'DOWN','target_mode':'ABSOLUTE_VALUE','threshold_pct':None,'target_value':98.0,'range_low':None,'range_high':None,'horizon_days':7,'rationale':'r'})
            packet=owner_packet(freezer,candidate);baseline={'captured_at_utc':'2026-09-02T10:19:00Z','market':{'x':100.0}};base_path.write_text(json.dumps(baseline))
            status,v,_=freezer.freeze_candidate(candidate,packet,baseline,base_path,out,None)
            self.assertEqual(status,'FROZEN');self.assertEqual(v['contract'],'FROZEN_FORECAST_v1');self.assertEqual(v['unit_contract_version'],'FORECAST_TARGET_UNITS_v2');self.assertAlmostEqual(v['threshold_pct'],2.0);self.assertEqual(v['target_value'],98.0);self.assertEqual(v['start_value'],100.0)

    def test_ratification_absolute_breadth_target_is_normalized_before_freeze(self):
        freezer=load_module('continuity_freezer_breadth',Path('scripts/learning/forecast_ratification_freezer.py'))
        with tempfile.TemporaryDirectory() as d:
            r=Path(d);out=r/'frozen';base_path=r/'baseline.json'
            candidate=prospective_candidate('breadth-c1',{'metric_path':'breadth.decliners','direction':'UP','target_mode':'ABSOLUTE_VALUE','threshold_pct':None,'target_value':58.0,'range_low':None,'range_high':None,'horizon_days':1,'rationale':'breadth absolute target'})
            packet=owner_packet(freezer,candidate);baseline={'captured_at_utc':'2026-09-02T10:19:00Z','breadth':{'decliners':38.0}};base_path.write_text(json.dumps(baseline))
            status,v,_=freezer.freeze_candidate(candidate,packet,baseline,base_path,out,None)
            self.assertEqual(status,'FROZEN');self.assertEqual(v['unit_contract_version'],'FORECAST_TARGET_UNITS_v2');self.assertEqual(v['target_mode'],'ABSOLUTE_VALUE');self.assertEqual(v['target_value'],58.0);self.assertAlmostEqual(v['threshold_pct'],(58.0/38.0-1.0)*100.0)

    def test_ratification_rejects_legacy_ambiguous_threshold(self):
        freezer=load_module('continuity_freezer_legacy',Path('scripts/learning/forecast_ratification_freezer.py'))
        with tempfile.TemporaryDirectory() as d:
            r=Path(d);out=r/'frozen';base_path=r/'baseline.json'
            candidate=prospective_candidate('c-legacy-shape',{'metric_path':'market.x','direction':'DOWN','threshold':98.0,'range_low':None,'range_high':None,'horizon_days':7,'rationale':'r'})
            packet=owner_packet(freezer,candidate);baseline={'captured_at_utc':'2026-09-02T10:19:00Z','market':{'x':100.0}};base_path.write_text(json.dumps(baseline))
            with self.assertRaisesRegex(ValueError,'EXPLICIT_DIRECTIONAL_TARGET_MODE_REQUIRED'):
                freezer.freeze_candidate(candidate,packet,baseline,base_path,out,None)

    def test_maturation_quarantines_legacy_directional_units(self):
        m=load_module('maturation',Path('scripts/learning/outcome_maturation_engine.py'))
        old={'contract':'FROZEN_FORECAST_v1','direction':'DOWN','source_candidate_id':'EC-old','threshold_pct':64699.1}
        safe_new={'contract':'FROZEN_FORECAST_v1','direction':'DOWN','unit_contract_version':'FORECAST_TARGET_UNITS_v2','threshold_pct':1.0}
        old_auto_range={'contract':'FROZEN_FORECAST_v1','direction':'RANGE','source_candidate_id':'EC-old','range_lower_pct':-1.0,'range_upper_pct':1.0}
        self.assertTrue(m.legacy_unit_ambiguous(old));self.assertFalse(m.legacy_unit_ambiguous(safe_new));self.assertFalse(m.legacy_unit_ambiguous(old_auto_range))

if __name__=='__main__':unittest.main()
