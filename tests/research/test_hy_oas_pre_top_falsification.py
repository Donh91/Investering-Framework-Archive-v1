import importlib.util
from pathlib import Path
from datetime import date,timedelta
P=Path(__file__).parents[2]/'scripts/research/hy_oas_pre_top_falsification.py';s=importlib.util.spec_from_file_location('m',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def test_kills_when_benign():
 rows=[]
 for top in m.TOPS:
  t=date.fromisoformat(top); rows += [(t-timedelta(days=90),5.0),(t,4.0)]
 assert m.run(rows)['status']=='KILL_DISTRIBUTION_WARNING'
