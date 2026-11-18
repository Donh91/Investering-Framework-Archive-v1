"""Public historical research regressions; no market or publication authority."""
import unittest
from adaptive_risk_memory_v1 import replay as r


class AdaptiveRiskMemoryTests(unittest.TestCase):
    def test_builtin_controls(self):
        checks = r.selftest()
        self.assertEqual(len(checks), 15)
        for name, passed in checks.items():
            with self.subTest(name=name):
                self.assertIs(passed, True)

    def test_historical_label_regression(self):
        # Public Binance-derived development labels, not original Kompas outcomes.
        # Exact source query and limitations are in adaptive_risk_memory_v1/PORT_VALIDATION.md.
        runs = [[25,35],[37,37],[50,50],[62,102],[113,123],[138,140],[145,145],[147,147],[160,173],[181,189],[191,191],[209,217],[257,265],[272,272],[275,277],[289,300],[320,320],[386,388],[423,423],[494,497],[519,519],[536,541],[543,543],[556,581],[591,591],[593,593],[621,630],[646,657],[659,661],[986,986],[1067,1068],[1070,1076],[1096,1096],[1100,1100],[1134,1135],[1157,1166],[1190,1193],[1205,1206],[1210,1227]]
        y = [0]*1228
        for i,j in runs:
            y[i:j+1] = [1]*(j-i+1)
        self.assertEqual(sum(y), 246)
        rows = [dict(t=1768111200000+i*6*r.HOUR, known=1768111200000+i*6*r.HOUR+76*r.HOUR, y=v) for i,v in enumerate(y)]
        self.assertEqual(rows[-1]['t'], 1794614400000)
        cutoff = r.utc(2026,3)
        train = r.matured(rows,cutoff)
        self.assertEqual(len(train), 183)
        prior = r.clip(r.mean([x['y'] for x in train]))
        test = [dict(x,p={'static_rate':prior,'rolling30':r.memory(r.matured(rows,x['t']),x['t'],prior,30)}) for x in rows if x['t']>=cutoff]
        expected = {'Mar-Jun':(477,104,.23395,.17826),'Jul-Oct':(481,21,.22347,.05145),'Nov-Dec':(53,24,.24807,.31490)}
        for name,lo,hi in r.periods(r.spec(2026)):
            a = [x for x in test if lo<=x['t'] and x['t']+72*r.HOUR<=hi]
            fixed,rolling = r.metrics(a,'static_rate'),r.metrics(a,'rolling30')
            self.assertEqual((fixed['n'],fixed['pos'],fixed['brier'],rolling['brier']),expected[name])

    def test_both_experiments_complete_synthetic(self):
        # Short deterministic fixture, same generator as the full synthetic smoke test.
        # This is not a historical or out-of-sample market result.
        s=dict(year=2026,start=r.utc(2026),end=r.utc(2026,4,1))
        state=8721; price=10000000; bars=[]
        for i in range((s['end']-s['start'])//r.HOUR):
            state=(1664525*state+1013904223)&0xffffffff
            price=max(100000,price+(state%40001-20000)*(1 if (i//120)%3 else 4))
            v=100000+(state>>8)%900000; u=v*(state%801+100)//1000; t=s['start']+i*r.HOUR
            bars.append([t,str(price),str(price),str(price),str(price),'1',t+r.HOUR-1,str(v),'1','1',str(u),'0'])
        a,b=r.run_a(bars,s),r.run_b(bars,s)
        self.assertEqual([x['h'] for x in a],[12,24,72])
        self.assertEqual([x['h'] for x in b],[12,24,72])
        for ar,br in zip(a,b):
            m=ar['periods']['Mar-Jun']; n=br['periods'][0]['all']
            self.assertEqual(set(m),set(r.A_METHODS))
            self.assertEqual(set(n['m']),set(r.B_METHODS))
            self.assertGreater(n['n'],0)
            for v in m.values():
                self.assertEqual(v['n'],n['n'])
                self.assertTrue(0<=v['brier']<=1)
            for v in n['m'].values():
                self.assertTrue(0<=v[0]<=1)


if __name__=='__main__':
    unittest.main()
