import importlib.util,zipfile,io
from pathlib import Path
P=Path(__file__).parents[2]/'scripts/data_terminal/world_bank_copper_gold_owner.py';s=importlib.util.spec_from_file_location('m',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def fixture(n=130):
 strings=['Date','Copper','Gold']+[f'{2000+i//12:04d}M{i%12+1:02d}' for i in range(n)]
 ss='<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'+''.join(f'<si><t>{x}</t></si>' for x in strings)+'</sst>'
 rows=['<row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c><c r="C1" t="s"><v>2</v></c></row>']
 for i in range(n): rows.append(f'<row r="{i+2}"><c r="A{i+2}" t="s"><v>{i+3}</v></c><c r="B{i+2}"><v>{5000+i}</v></c><c r="C{i+2}"><v>{1200+i}</v></c></row>')
 sh='<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'+''.join(rows)+'</sheetData></worksheet>'
 b=io.BytesIO();z=zipfile.ZipFile(b,'w');z.writestr('xl/sharedStrings.xml',ss);z.writestr('xl/worksheets/sheet1.xml',sh);z.close();return b.getvalue()
def test_build_units_and_anchors():
 d=m.build(fixture(),'2026-08-27T00:00:00Z');assert d['coverage']['observations']==130;assert set(d['settled_2m'])=={'JAN_FEB','FEB_MAR'};assert d['monthly'][0]['ratio']>0;assert d['authority']['portfolio_action'] is False
def test_features_no_incomplete_pair():
 d=m.build(fixture(131),'x');assert len(d['settled_2m']['JAN_FEB'])==65
