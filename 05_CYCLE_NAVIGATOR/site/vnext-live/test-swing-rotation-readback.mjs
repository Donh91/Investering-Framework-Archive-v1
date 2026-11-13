/* Pure-source Swing Kompas invariants. No market API, network or synthetic forecasts. */
import assert from 'node:assert/strict';
import {readSwingRotation} from './swing-rotation-readback.mjs';

const view={compass:{state:'FRESH',permit_path_live_gates:true,compass_id:'CMP-FIXTURE',action_now:'HOLD_WAIT'}};
const src={
 contract:'PUBLIC_COMPASS_PROJECTION_v1',data_status:'OK',compass_id:'CMP-FIXTURE',
 issued_at_utc:'2026-11-11T08:22:20Z',action_now:'HOLD_WAIT',
 horizons:{
  NEXT_1_3D:{expected_direction:'DOWN',action_posture:'WAIT'},
  NEXT_5_7D:{expected_direction:'MIXED',action_posture:'WAIT'},
  NEXT_2_3W:{expected_direction:'UNAVAILABLE',action_posture:'NO_EDGE'}
 },
 capitalization_ladder:[
  {segment:'BTC',action:'HOLD',status:'HOLD'},
  {segment:'LARGE_CAPS',action:'WAIT',status:'WAIT'},
  {segment:'MID_CAPS',action:'WAIT',status:'WAIT'},
  {segment:'SMALL_CAPS',action:'WAIT',status:'WAIT'},
  {segment:'MICROCAPS',action:'HARD_WAIT',status:'HARD_WAIT'},
  {segment:'MEMES',action:'UNAVAILABLE',status:'UNAVAILABLE'}
 ]
};
const fresh=readSwingRotation(view,src);
assert.equal(fresh.contract,'CN_SWING_ROTATION_READBACK_V1');
assert.equal(fresh.valid,true);
assert.deepEqual(fresh.horizons.map(h=>h.direction),['DOWN','MIXED','UNAVAILABLE']);
assert.deepEqual(fresh.rows.map(x=>x.key),['LARGE_CAPS','MID_CAPS','SMALL_CAPS','MICROCAPS']);
assert.equal(fresh.rows[3].sourceAction,'HARD_WAIT');
assert.deepEqual(Object.keys(fresh.rows[3]).sort(),['future','isMicro','key','label','nowLabel','sizeReference','sourceAction','verified'],'row has exactly these fields');
assert.deepEqual(Object.keys(fresh).sort(),['contract','horizons','issuedAt','rows','sectorHorizonStatus','sourceId','valid'],'public model has exactly these fields');
assert.ok(fresh.rows.every(x=>x.future.length===3&&x.future.every(y=>y.status==='NOT_ISSUED')));
assert.ok(fresh.horizons.every(x=>x.source==='OFFICIAL_MARKET_WIDE_ONLY'&&!x.segmentForecastIssued));
assert.ok(!fresh.rows.some(x=>x.key==='MEMES'));

const check=(v,c)=>readSwingRotation(v,c);
const copy=x=>structuredClone(x);
const stale=copy(view);stale.compass.state='STALE';
assert.equal(check(stale,src).valid,false);
assert.ok(check(stale,src).rows.every(x=>x.sourceAction==='UNAVAILABLE'));
assert.ok(check(stale,src).horizons.every(x=>x.direction==='UNAVAILABLE'));
const noEdge=copy(src);
noEdge.horizons.NEXT_1_3D.expected_direction='NO_EDGE';
const noEdgeDa=readSwingRotation(view,noEdge);
assert.equal(noEdgeDa.horizons[0].direction,'NO_EDGE');
assert.equal(noEdgeDa.horizons[0].text,'Ingen dokumenteret fordel');
assert.equal(readSwingRotation(view,noEdge,{lang:'en'}).horizons[0].text,'No proven edge');
assert.equal(noEdgeDa.horizons[2].direction,'UNAVAILABLE');
assert.equal(noEdgeDa.horizons[2].text,'Afventer kilde');
assert.equal(readSwingRotation(stale,noEdge).horizons[0].direction,'UNAVAILABLE');
const wrongId=copy(src);wrongId.compass_id='OTHER';
assert.equal(check(view,wrongId).valid,false);
const wrongAction=copy(src);wrongAction.action_now='PREPARE';
assert.equal(check(view,wrongAction).valid,false);
const degraded=copy(src);degraded.data_status='DEGRADED';
assert.equal(check(view,degraded).valid,false);
const missing=copy(src);delete missing.capitalization_ladder;
assert.ok(check(view,missing).rows.every(x=>!x.verified));
const inconsistent=copy(src);inconsistent.capitalization_ladder[4].status='BUY';
assert.equal(check(view,inconsistent).rows[3].sourceAction,'UNAVAILABLE');
const duplicate=copy(src);duplicate.capitalization_ladder.push(copy(src.capitalization_ladder[4]));
assert.equal(check(view,duplicate).rows[3].sourceAction,'UNAVAILABLE');
const futureLookalike=copy(src);futureLookalike.horizons.NEXT_2_3W.expected_direction='BULLISH';
assert.equal(check(view,futureLookalike).horizons[2].direction,'UNAVAILABLE');
const futureSectors=copy(src);futureSectors.capitalization_horizons={MICROCAPS:{NEXT_1_3D:{expected_direction:'UP'}}};
assert.ok(check(view,futureSectors).rows[3].future.every(x=>x.status==='NOT_ISSUED'),
 'Do not silently accept unsupported future-tier source schema');
const en=readSwingRotation(view,src,{lang:'en'});
assert.equal(en.horizons[0].text,'Falling');
assert.equal(en.rows[3].nowLabel,'Strict wait');
console.log('PASS: Swing Kompas uses only official market-wide horizons/current cap actions; all 12 sector×horizon forecasts unavailable');
