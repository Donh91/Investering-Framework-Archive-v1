import importlib.util
import subprocess
import tempfile
import io
import unittest
from unittest import mock
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

    def test_hot_set_bounds_routine_data_episodes_only(self):  # WO-2c, Archive #2157 (v2 keep rule)
        def ep(i, op, ts, subject):
            return {'episode_id': f'OE-{i:02d}', 'source_commit_sha': str(i % 10) * 40, 'source_timestamp': ts,
                    'task_class': 'GENERAL_FRAMEWORK', 'operation_type': op, 'task_summary': subject,
                    'failure_signature': None, 'dominant_path_prefix': 'x', 'changed_paths': ['x/a'],
                    'source_blob_shas': {}, '_path': f'episodes/OE-{i:02d}.json'}
        old = '2026-10-01T00:00:00Z'
        when = '2026-11-15T00:00:00Z'
        eps = [ep(1, 'UPDATE', old, 'learning: native Handlekompas 43694676673'),          # routine, old: cold only
               ep(2, 'RESEARCH', '2026-10-31T23:59:59Z', 'research: capture passive 43000000001'),  # 14 d + 1 s
               ep(3, 'UPDATE', '2026-11-01T00:00:00Z', 'data: materialize hourly 43000000002'),  # exactly at cutoff
               ep(4, 'FIX', old, 'fix(cn): repair publication'),                          # engineering
               ep(5, 'BUILD', old, 'build: add gate'),
               ep(6, 'UPDATE', 'not-a-timestamp', 'ops: provider budget 43000000003'),    # unknown time: kept
               ep(7, 'UPDATE', old, 'feat(skills): add retrieval skill (#2108)'),         # human PR typed UPDATE
               ep(8, 'UPDATE', old, 'test(compass): pin lead window'),                    # human, no run id
               ep(9, 'HARDEN', old, 'data: prevent duplicate rows 43000000004'),          # type keeps it
               ep(10, 'ARCHIVE', old, 'research: archive receipts 43000000005'),          # type keeps it
               ep(11, 'RESEARCH', old, 'research: accumulate prospective forecasts'),     # known bot phrase
               ep(12, 'UPDATE', old, 'learning: merge (#2200) fixture 43000000006'),      # names a PR: kept
               ep(13, 'UPDATE', '2026-10-01T00:00:00', 'data: log live 43000000007')]     # naive time: kept
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            subprocess.run(['git', 'init', str(root)], check=True, capture_output=True)
            subprocess.run(['git', '-C', str(root), '-c', 'user.email=t@e.x', '-c', 'user.name=T',
                            'commit', '--allow-empty', '-m', 'root'], check=True, capture_output=True)
            idx = mod.index(root, eps, when)
            kept = [r['episode_id'] for r in idx['rows']]
            self.assertEqual(kept, ['OE-03', 'OE-04', 'OE-05', 'OE-06', 'OE-07', 'OE-08', 'OE-09', 'OE-10',
                                    'OE-12', 'OE-13'])
            self.assertEqual((idx['episode_count'], idx['total_episode_count']), (10, 13))
            self.assertEqual(idx['hot_set_policy']['rolling_window_days'], 14)
            health = mod.health(idx, mod.candidates(idx, when), when)
            self.assertEqual(health['episode_count'], idx['episode_count'])  # post-production audit invariant
            self.assertEqual(health['total_episode_count'], 13)
            out = root / 'LATEST_OPERATIONAL_MEMORY_INDEX.json'
            mod.write(out, idx, compact=True)
            text = out.read_text()
            self.assertNotIn('\n  ', text)
            import json
            self.assertEqual(json.loads(text), idx)

    def test_routine_rule_is_narrow(self):
        routine = lambda op, s: mod.routine({'operation_type': op, 'task_summary': s})
        self.assertTrue(routine('UPDATE', 'ops: update integrated learning and experiment receipts 43699895107'))
        self.assertTrue(routine('RESEARCH', 'data: persist research rows'))
        for op, s in (('UPDATE', 'Health: converge recovery 43000000001'),   # unknown capitalised writer
                      ('UPDATE', 'learning: native Handlekompas'),            # no run id
                      ('UPDATE', 'learning: x 12345678'),                     # 8 digits is not a run id
                      ('UPDATE', 'Merge pull request #2140 from x/y'),
                      ('FIX', 'learning: native Handlekompas 43694676673'),
                      ('BUILD', 'data: add writer 43000000001'),
                      ('UPDATE', 'governance(s1): action loop (#2121)'),
                      ('UPDATE', 'data: sync (#2155) receipts 43000000001')):
            with self.subTest(op=op, s=s):
                self.assertFalse(routine(op, s))

    def test_harvest_writes_compact_index_and_discloses_totals(self):
        import argparse, json
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            subprocess.run(['git', 'init', str(root)], check=True, capture_output=True)
            (root / 'a.txt').write_text('x')
            subprocess.run(['git', '-C', str(root), 'add', 'a.txt'], check=True, capture_output=True)
            subprocess.run(['git', '-C', str(root), '-c', 'user.email=t@e.x', '-c', 'user.name=T',
                            'commit', '-m', 'fix(x): repair a'], check=True, capture_output=True)
            args = argparse.Namespace(repo_root=str(root), output_root='mem', max_commits=50)
            with mock.patch('sys.stdout', new_callable=io.StringIO):
                mod.do_harvest(args)
            text = (root / 'mem' / 'LATEST_OPERATIONAL_MEMORY_INDEX.json').read_text()
            self.assertNotIn('\n  ', text)
            state = json.loads((root / 'mem' / 'LATEST_OPERATIONAL_MEMORY_STATE.json').read_text())
            health = json.loads((root / 'mem' / 'LATEST_OPERATIONAL_MEMORY_HEALTH.json').read_text())
            self.assertEqual((state['episode_count'], state['total_episode_count']), (1, 1))
            self.assertEqual(health['total_episode_count'], 1)
            self.assertEqual(state['hot_window_days'], 14)

if __name__ == '__main__':
    unittest.main()
