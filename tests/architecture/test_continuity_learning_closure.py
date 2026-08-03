from __future__ import annotations
import importlib.util,json,subprocess,tempfile,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

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
            self.assertEqual(p.returncode,0,p.stderr);man=list(out.rglob('RAW_MANIFEST_test.json'));self.assertEqual(len(man),1);v=json.loads(man[0].read_text());self.assertEqual(v['contract'],'RAW_OWNER_PAYLOAD_MANIFEST_v1');self.assertTrue(Path(v['archives'][0]['archive_path']).exists())

    def test_gateway_schema_contains_unratified_candidates(self):
        m=load_module('gateway',Path('scripts/api_agent/api_gateway.py'));schema=m.output_schema();self.assertIn('forecast_candidates',schema['properties']);self.assertIn('forecast_candidates',schema['required'])
        m.validate_output({'status':'READY','summary':'x','evidence_for':[],'evidence_against':[],'uncertainties':[],'hypotheses':[],'forecast_candidates':[{'metric_path':'market_metrics.x','direction':'UP','threshold':1.0,'range_low':None,'range_high':None,'horizon_days':7,'rationale':'test'}]})

    def test_ratification_is_required_before_freeze(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d);candidate=r/'c.json';rat=r/'r.json';base=r/'b.json';out=r/'frozen'
            candidate.write_text(json.dumps({'contract':'FORECAST_CANDIDATE_v1','candidate_id':'c1','ratification_status':'PENDING','model':'luna','task':'DAILY_DIRECTOR_SHADOW','prompt_sha256':'p','context_sha256':'c','source_output_sha256':'o','candidate':{'metric_path':'market.x','direction':'UP','threshold':1.0,'range_low':None,'range_high':None,'horizon_days':7,'rationale':'r'}}));base.write_text(json.dumps({'market':{'x':100}}));rat.write_text(json.dumps({'contract':'FORECAST_RATIFICATION_PACKET_v1','candidate_id':'c1','decision':'RATIFY','authority':'CHATGPT_FRAMEWORK_OWNER'}))
            p=subprocess.run(['python',str(ROOT/'scripts/learning/ratify_forecast_candidate.py'),'--candidate',str(candidate),'--ratification',str(rat),'--baseline-evidence',str(base),'--output-root',str(out)],text=True,capture_output=True)
            self.assertEqual(p.returncode,0,p.stderr);v=json.loads(next(out.glob('*.json')).read_text());self.assertEqual(v['contract'],'FROZEN_FORECAST_v1');self.assertEqual(v['start_value'],100)

if __name__=='__main__':unittest.main()
