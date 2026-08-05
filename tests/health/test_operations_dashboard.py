from __future__ import annotations

import importlib.util,json,tempfile,unittest
from datetime import datetime,timezone
from pathlib import Path
MODULE_PATH=Path(__file__).parents[2]/'scripts'/'health'/'build_operations_dashboard.py';spec=importlib.util.spec_from_file_location('operations_dashboard',MODULE_PATH);module=importlib.util.module_from_spec(spec);assert spec and spec.loader;spec.loader.exec_module(module);UTC=timezone.utc

class OperationsDashboardTests(unittest.TestCase):
    def write_json(self,root,rel,data):
        path=root/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,sort_keys=True)+'\n',encoding='utf-8');return path
    def base_repo(self,root):
        capture=self.write_json(root,'captures/capture.json',{'captured_at_utc':'2026-08-04T12:00:00Z','status':'PASS'})
        director=self.write_json(root,'research/api_agent/outputs/daily/2026/08/04/121000/DAILY_DIRECTOR_OUTPUT.json',{'status':'READY'})
        self.write_json(root,'research/api_agent/outputs/daily/2026/08/04/121000/DAILY_DIRECTOR_RECEIPT.json',{'contract':'API_AGENT_RECEIPT_v3','created_unix':1785845400,'status':'PASS','model':'gpt-5.6-luna','task':'DAILY_DIRECTOR_SHADOW','response_id':'resp-1','input_tokens':100,'output_tokens':20,'estimated_cost_usd':0.001})
        weekly=self.write_json(root,'weekly/output.json',{'completed_at_utc':'2026-08-03T08:00:00Z','status':'PASS'})
        self.write_json(root,'LATEST_HANDOFF.json',{'contract':'LATEST_HANDOFF_v2','generated_at_utc':'2026-08-04T12:15:00Z','open_incidents':[],'pending_forecast_candidates':[],'pointers':{'latest_capture':{'path':str(capture.relative_to(root)),'sha256':module.sha256_path(capture)},'latest_director_output':{'path':str(director.relative_to(root)),'sha256':module.sha256_path(director)},'latest_weekly_output':{'path':str(weekly.relative_to(root)),'sha256':module.sha256_path(weekly)}}})
        self.write_json(root,'research/architecture_health/LATEST_AUTOMATION_HEALTH.json',{'status':'GREEN','generated_at_utc':'2026-08-04T12:20:00Z','red_count':0,'amber_count':0,'blockers':[]})
        self.write_json(root,'research/architecture_health/LATEST_ARCHITECTURE_HEALTH.json',{'status':'GREEN','generated_at_utc':'2026-08-04T12:20:00Z','blockers':[]})
        self.write_json(root,'research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json',{'contract':'EXPERIMENT_LIFECYCLE_REGISTRY_v1','generated_at_utc':'2026-08-04T12:25:00Z','candidate_count':2,'state_counts':{'FROZEN':1,'WAITING_FOR_MAPPING':1}})
        self.write_json(root,'research/experiment_lifecycle/LATEST_EXPERIMENT_RECEIPT_SYNC.json',{'contract':'EXPERIMENT_RECEIPT_SYNC_v1','generated_at_utc':'2026-08-04T12:25:00Z','status':'PASS','imported':0,'hash_mismatches':0})
        self.write_json(root,'research/experiment_lifecycle/LATEST_EXPERIMENT_DISPATCH_MANIFEST.json',{'contract':'EXPERIMENT_DISPATCH_MANIFEST_v1','generated_at_utc':'2026-08-04T12:25:00Z','request_count':1})
        self.write_json(root,'research/remediation/LATEST_REMEDIATION_QUEUE.json',{'contract':'REMEDIATION_MATURATION_ENGINE_v1','generated_at_utc':'2026-08-04T12:25:00Z','summary':{'codex_ready':0,'needs_more_evidence':0},'automatic_code_write':False,'automatic_merge':False})
    def test_green_happy_path_and_real_receipt_discovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);self.base_repo(root);dashboard=module.build_dashboard(root,datetime(2026,8,4,13,0,tzinfo=UTC));self.assertEqual(dashboard['contract'],'OPERATIONS_DASHBOARD_v1_2');self.assertEqual(dashboard['overall_status'],'GREEN');self.assertEqual(dashboard['agent_activity']['openai_api']['receipt_count'],1);self.assertEqual(dashboard['agent_activity']['experiments']['candidate_count'],2);self.assertTrue(dashboard['systems']['openai_daily_director']['receipt_path'].endswith('DAILY_DIRECTOR_RECEIPT.json'))
    def test_skipped_no_delta_receipt_overrides_blocked_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);self.base_repo(root);out=root/'research/api_agent/outputs/daily/2026/08/04/121000/DAILY_DIRECTOR_OUTPUT.json';out.write_text(json.dumps({'status':'BLOCKED'})+'\n');receipt=out.with_name('DAILY_DIRECTOR_RECEIPT.json');value=json.loads(receipt.read_text());value.update({'status':'SKIPPED_NO_DELTA','input_tokens':0,'output_tokens':0,'estimated_cost_usd':0.0});receipt.write_text(json.dumps(value)+'\n');handoff=json.loads((root/'LATEST_HANDOFF.json').read_text());handoff['pointers']['latest_director_output']['sha256']=module.sha256_path(out);(root/'LATEST_HANDOFF.json').write_text(json.dumps(handoff)+'\n');row=module.build_dashboard(root,datetime(2026,8,4,13,0,tzinfo=UTC))['systems']['openai_daily_director'];self.assertEqual(row['status'],'GREEN');self.assertEqual(row['reason'],'EXPECTED_SKIP_NO_COMPARABLE_DELTA')
    def test_hash_mismatch_is_red(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);self.base_repo(root);handoff=json.loads((root/'LATEST_HANDOFF.json').read_text());handoff['pointers']['latest_capture']['sha256']='0'*64;(root/'LATEST_HANDOFF.json').write_text(json.dumps(handoff)+'\n');self.assertEqual(module.build_dashboard(root,datetime(2026,8,4,13,0,tzinfo=UTC))['systems']['daily_capture']['status'],'RED')
    def test_stale_capture_is_red(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);self.base_repo(root);self.assertEqual(module.build_dashboard(root,datetime(2026,8,5,13,0,tzinfo=UTC))['systems']['daily_capture']['status'],'RED')
    def test_automation_red_propagates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);self.base_repo(root);self.write_json(root,'research/architecture_health/LATEST_AUTOMATION_HEALTH.json',{'status':'RED','generated_at_utc':'2026-08-04T12:20:00Z','red_count':2,'amber_count':0,'blockers':['workflow-x:LATEST_RUN_FAILED']});self.assertEqual(module.build_dashboard(root,datetime(2026,8,4,13,0,tzinfo=UTC))['overall_status'],'RED')
    def test_missing_inputs_never_false_green(self):
        with tempfile.TemporaryDirectory() as tmp:
            dashboard=module.build_dashboard(Path(tmp),datetime(2026,8,4,13,0,tzinfo=UTC));self.assertNotEqual(dashboard['overall_status'],'GREEN');self.assertTrue(dashboard['required_actions'])
if __name__=='__main__':unittest.main()
