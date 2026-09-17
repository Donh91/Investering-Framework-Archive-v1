import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path('scripts/framework_intelligence/operational_memory_v1.py')
spec = importlib.util.spec_from_file_location('operational_memory_v1', SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class OperationalMemoryV1Test(unittest.TestCase):
    def test_task_classification(self):
        self.assertEqual(mod.task_class('fix cycle navigator binding'), 'CYCLE_NAVIGATOR')
        self.assertEqual(mod.task_class('harden moonshot scanner'), 'MEME_ALPHA')
        self.assertEqual(mod.task_class('repair workflow schedule'), 'AUTOMATION_REMEDIATION')

    def test_compatibility_states(self):
        src = {'a':'1','b':'2'}
        self.assertEqual(mod.compat(src, {'a':'1','b':'2'})['status'], 'EXACT')
        self.assertEqual(mod.compat(src, {'a':'1','b':'3'})['status'], 'PARTIAL')
        self.assertEqual(mod.compat(src, {'a':None,'b':None})['status'], 'REMOVED')

    def test_stale_memory_scores_lower(self):
        row = {'task_class':'CYCLE_NAVIGATOR','task_summary':'fix cycle navigator binding','failure_signature':'cycle-navigator-binding','changed_paths':['05_CYCLE_NAVIGATOR/a'],'compatibility':{'status':'EXACT'},'newer_related_episode':None}
        stale = dict(row); stale['compatibility']={'status':'REMOVED'}
        good = mod.score('fix cycle navigator binding',['05_CYCLE_NAVIGATOR/a'],None,row)
        bad = mod.score('fix cycle navigator binding',['05_CYCLE_NAVIGATOR/a'],None,stale)
        self.assertGreater(good,bad)

    def test_preflight_has_no_authority(self):
        idx={'source_head_sha':'abc','rows':[{'episode_id':'OE-1','source_commit_sha':'1'*40,'source_timestamp':'2026-09-15T00:00:00Z','task_class':'CYCLE_NAVIGATOR','operation_type':'FIX','task_summary':'fix cycle navigator binding','failure_signature':'cycle-navigator-binding','changed_paths':['05_CYCLE_NAVIGATOR/a'],'compatibility':{'status':'EXACT'},'episode_path':'episodes/OE-1.json','newer_related_episode':None}]}
        out=mod.preflight(idx,'fix cycle navigator binding',['05_CYCLE_NAVIGATOR/a'])
        self.assertFalse(out['authority']['canonical_effect'])
        self.assertFalse(out['authority']['portfolio_execution'])
        self.assertTrue(out['reusable_prior_work'])

    def test_procedural_candidate_requires_three_independent_commits(self):
        rows=[]
        for i in range(3):
            rows.append({'episode_id':f'OE-{i}','source_commit_sha':str(i)*40,'task_class':'CYCLE_NAVIGATOR','operation_type':'HARDEN','dominant_path_prefix':'05_CYCLE_NAVIGATOR','compatibility':{'status':'EXACT'}})
        out=mod.candidates({'rows':rows},'2026-09-15T00:00:00Z')
        self.assertEqual(out['candidate_count'],1)
        c=out['candidates'][0]
        self.assertEqual(c['operation_family'],'REMEDIATION')
        self.assertFalse(c['automatic_skill_activation'])
        self.assertFalse(c['promotion_allowed'])

    def test_end_to_end_temp_git_repo(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            subprocess.run(['git','init',str(root)],check=True,capture_output=True)
            subprocess.run(['git','-C',str(root),'config','user.email','test@example.com'],check=True)
            subprocess.run(['git','-C',str(root),'config','user.name','Test'],check=True)
            for i,(message,rel) in enumerate([
                ('Build Cycle Navigator baseline','05_CYCLE_NAVIGATOR/a.txt'),
                ('Fix Cycle Navigator binding','05_CYCLE_NAVIGATOR/a.txt'),
                ('Harden Cycle Navigator binding','05_CYCLE_NAVIGATOR/b.txt'),
                ('Correct Cycle Navigator binding','05_CYCLE_NAVIGATOR/c.txt'),
            ]):
                p=root/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(str(i))
                subprocess.run(['git','-C',str(root),'add','.'],check=True)
                subprocess.run(['git','-C',str(root),'commit','-m',message],check=True,capture_output=True)
            out=root/'research/framework_learning/operational_memory'
            created,_=mod.harvest(root,out,20)
            self.assertEqual(len(created),4)
            idx=mod.index(root,mod.episodes(out),'2026-09-15T00:00:00Z')
            cand=mod.candidates(idx,'2026-09-15T00:00:00Z')
            health=mod.health(idx,cand,'2026-09-15T00:00:00Z')
            self.assertEqual(idx['episode_count'],4)
            self.assertEqual(cand['candidate_count'],1)
            self.assertEqual(health['status'],'PASS')
            pf=mod.preflight(idx,'fix cycle navigator binding',['05_CYCLE_NAVIGATOR/a.txt'])
            self.assertTrue(pf['reusable_prior_work'])

if __name__ == '__main__':
    unittest.main()
