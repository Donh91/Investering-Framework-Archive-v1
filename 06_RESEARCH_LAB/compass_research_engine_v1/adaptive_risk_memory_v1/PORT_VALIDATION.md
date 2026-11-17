# Python port validation — 2026-11-17

**RESEARCH ONLY. EXPOST_DEVELOPMENT_ONLY.** Original receipt unchanged (Git blob 0f74140264c20a797bf6947762db70da7fef3966); prior JS code remains in PR history at 05f27b6e5ce3eb7526070e84e1a0331efd88ab91. The trusted base CRE guard rejected .mjs as UNSUPPORTED_FILE_TYPE. No guard, workflow or release-policy change. Port retains experimental model formulas/periods; Python float and rounding implementations may differ slightly. No production, warning or scientific authority.

## Executed locally on the exact Python blob

- `python replay.py --self-test`: 15/15 PASS (12 predecessor checks, plus invalid shape, non-integral clock, nonfinite input). Blob expected ab179d60fc1eae8b0f38d094fe574d4720389621.
- Entire Python CLI executed on deterministic synthetic 2026 hourly fixture: 7680/7680 rows, zero duplicate/grid/bad rows; all fourteen A and nine B methods produced finite JSON. Fixture SHA256 cbdd04b7a1599720e8a6a6b6cb59283ed9367286d808eab19ab23fd4f2eec4b7. Synthetic A72 Jul-Oct rolling30 Brier .10396, B72 rolling30_full .10046. This is a smoke test, not JS/Python full result equivalence.
- Actual historical label regression: fresh read-only eight-page BTCUSDT hourly spot query for 2026-01-01 to 2026-11-17 exclusive, validated 7680 contiguous rows. Projected 1228 72h labels, 246 positives, first issue 1768111200000, last 1794614400000, 6h spacing, availability issue+76h strictly before use. Transferred only label run boundaries to local Python; no raw bars in repository. Executed the Python maturity, memory and metric functions, reproducing four reference Brier values exactly at five decimals: Jul-Oct rolling30 .05145 / fixed .22347 (481 rows,21 hits); Nov rolling30 .31490 / fixed .24807 (53 rows,24 hits). Mar-Jun rolling30 .17826 / fixed .23395 (477 rows,104 hits).
- Full Python historical end-to-end replay for price/flow and all methods remains NOT RUN. The external raw response is not byte-frozen, and Python runtime has no network access; do not claim complete port equivalence or original first-known verification.

## Reproducible fixture construction

Synthetic fixture generator (use Python stdlib, compact JSON separators):
```python
import json
from replay import spec,HOUR
s=spec(2026); state=8721; price=10000000; bars=[]
for i in range((s['end']-s['start'])//HOUR):
    state=(1664525*state+1013904223)&0xffffffff
    price=max(100000,price+(state%40001-20000)*(1 if (i//120)%3 else 4))
    v=100000+(state>>8)%900000
    u=v*(state%801+100)//1000
    t=s['start']+i*HOUR
    bars.append([t,str(price),str(price),str(price),str(price),'1',t+HOUR-1,str(v),'1','1',str(u),'0'])
with open('synthetic.json','w') as f:
    json.dump(bars,f,separators=(',',':'))
```

Historical regression run boundaries (inclusive zero-based index) for the 1228 derived public market labels (not independent observations): [[25,35],[37,37],[50,50],[62,102],[113,123],[138,140],[145,145],[147,147],[160,173],[181,189],[191,191],[209,217],[257,265],[272,272],[275,277],[289,300],[320,320],[386,388],[423,423],[494,497],[519,519],[536,541],[543,543],[556,581],[591,591],[593,593],[621,630],[646,657],[659,661],[986,986],[1067,1068],[1070,1076],[1096,1096],[1100,1100],[1134,1135],[1157,1166],[1190,1193],[1205,1206],[1210,1227]]. Fill 1228 zeros, set each run to 1; issue t=1768111200000+index*6*HOUR; known=t+76*HOUR. Train prior on rows known strictly before March 1; evaluate identical periods using t+72h<=period end. Test the static_rate and rolling30 methods via memory and metrics. Full raw replay, exact-head native CI and detached review remain required before any archive merge. No automatic promotion; the study is still a development comparison.
