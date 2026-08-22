import json,pathlib,importlib.util
R=pathlib.Path(__file__).resolve().parents[1];s=importlib.util.spec_from_file_location('e',R/'pipeline/tournament_evaluator.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def test_mechanics():
    rows=[{'observation_timestamp_utc':'2026-01-01T00:00:00Z','information_cutoff_utc':'2026-01-01T00:00:00Z','candidate_decisions':json.dumps({'A':1,'B':0}),'outcome_24h':'1'},{'observation_timestamp_utc':'2026-01-02T00:00:00Z','information_cutoff_utc':'2026-01-02T00:00:00Z','candidate_decisions':json.dumps({'A':0,'B':0}),'outcome_24h':'0'}]
    r=m.evaluate(rows,['A','B']);assert r['metrics']['A']['precision']==1.0;assert r['metrics']['A']['recall']==1.0;assert r['disagreements']['A__vs__B']['rate']==0.5
