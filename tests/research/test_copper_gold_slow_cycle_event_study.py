from datetime import date,timedelta
def test_knowledge_is_after_bar_end_month():
 end='2021-06'; k=date.fromisoformat(end+'-01')+timedelta(days=32); k=k.replace(day=1);assert k.isoformat()=='2021-07-01'
