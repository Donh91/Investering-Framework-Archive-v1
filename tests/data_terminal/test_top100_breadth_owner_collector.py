import importlib.util, json, pathlib, tempfile, unittest
P=pathlib.Path('scripts/data_terminal/top100_breadth_owner_collector.py')
S=importlib.util.spec_from_file_location('br',P); M=importlib.util.module_from_spec(S); S.loader.exec_module(M)

def payload(n=100):
    rows=[]
    for i in range(n): rows.append({"id":f"asset-{i}","symbol":f"a{i}","name":f"Asset {i}","market_cap":1000000-i,"current_price":100+i,"price_change_percentage_24h":1 if i%2==0 else -1})
    return json.dumps(rows).encode()
class T(unittest.TestCase):
    def test_parse_and_hash(self):
        c,e,a=M.parse(payload()); self.assertEqual(len(c),100); self.assertEqual(a['advancers'],50); self.assertEqual(len(a['membership_hash']),64)
    def test_incomplete(self):
        with self.assertRaises(M.E): M.parse(payload(99))
    def test_duplicate(self):
        rows=json.loads(payload()); rows[1]['id']=rows[0]['id']
        with self.assertRaises(M.E): M.parse(json.dumps(rows).encode())
    def test_stable_exclusion(self):
        rows=json.loads(payload()); rows[0]['symbol']='usdt'; rows.append({"id":"extra","symbol":"extra","name":"Extra","market_cap":1,"current_price":1,"price_change_percentage_24h":1}); c,e,a=M.parse(json.dumps(rows).encode()); self.assertTrue(any(x['reason']=='STABLECOIN' for x in e)); self.assertEqual(len(c),100)
    def test_run_and_tamper(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d); M.run(payload(),root,'2026-07-31T20:00:00Z'); self.assertEqual(M.verify(root)['status'],'PASS'); (root/'owner_snapshot.json').write_text('{}'); self.assertEqual(M.verify(root)['status'],'FAIL')
if __name__=='__main__': unittest.main()
