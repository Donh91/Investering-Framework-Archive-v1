import { readFile } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
const site=dirname(fileURLToPath(import.meta.url));
const dist=resolve(site,'dist');
const compass=JSON.parse(await readFile(resolve(dist,'data/compass.json'),'utf8'));
const index=await readFile(resolve(dist,'index.html'),'utf8');
const renderer=await readFile(resolve(dist,'compass-product-v5.js'),'utf8');
if(compass.contract!=='PUBLIC_COMPASS_PROJECTION_v1') throw Error('wrong Compass contract');
if(compass.data_status==='OK'){
  for(const h of ['NEXT_12H','NEXT_1_3D','NEXT_5_7D','CYCLE_ALTCOINS_3_8W']) if(!compass.horizons?.[h]) throw Error(`missing ${h}`);
  const alt=compass.horizons.CYCLE_ALTCOINS_3_8W;
  if(!alt.action_posture||!alt.expected_path) throw Error('incomplete altcoin action lane');
  const segments=(compass.capitalization_ladder||[]).map(x=>x.segment).join(',');
  if(segments!=='BTC,ETH,LARGE_CAPS,MID_CAPS,SMALL_CAPS,MICROCAPS') throw Error('wrong capitalization ladder');
}
if(!index.includes('./compass-product-v5.js')) throw Error('Compass renderer not activated');
for(const token of ['MARKET COMPASS','NEXT 12 HOURS','NEXT 1–3 DAYS','NEXT 5–7 DAYS','ALTCOIN ACTION · OFFICIAL COMPASS','Bitcoin → microcaps']) if(!renderer.includes(token)) throw Error(`renderer missing ${token}`);
if(/HANDLEKOMPAS|MASTER MONDAY/.test(renderer)) throw Error('internal product language leaked');
if(/source_bindings|evidence_snapshot/.test(JSON.stringify(compass))) throw Error('private Compass evidence leaked');
console.log(JSON.stringify({status:'PASS',compass_id:compass.compass_id,data_status:compass.data_status,altcoin_action:compass.horizons?.CYCLE_ALTCOINS_3_8W?.action_posture||null}));
