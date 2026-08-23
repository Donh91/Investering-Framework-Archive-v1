#!/usr/bin/env python3
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

LAB = Path('06_RESEARCH_LAB/historical_altseason_pullback_v1')
R3 = Path('06_RESEARCH_LAB/round3_new_information_v1')
ART = LAB / 'artifacts'
OUT = R3 / 'materialized_v2'
HOURLY = ART / 'hourly_features.csv.gz'
READINESS = ART / 'RESEARCH_READINESS_MANIFEST.json'
LEGACY_CONFIG = LAB / 'config.json'
V2_CONTRACT = R3 / 'V2_EPISODE_AND_CONTROL_CONTRACT_v1.json'
STATUS = R3 / 'COLLECTION_STATUS.json'
MATCH_FEATURES = [
    'mean_return_24h_pct', 'breadth_24h', 'dispersion_1h_pct',
    'eth_minus_btc_24h_pp', 'active_alt_count'
]


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def canonical_bytes(obj) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False)+'\n').encode()


def f(v):
    if v in (None, ''): return None
    try:
        x=float(v)
        return x if math.isfinite(x) else None
    except Exception:
        return None


def iso(v: str) -> datetime:
    return datetime.fromisoformat(v.replace('Z','+00:00'))


def load_hourly():
    rows=[]
    with gzip.open(HOURLY, 'rt', encoding='utf-8', newline='') as fh:
        for r in csv.DictReader(fh):
            row=dict(r)
            row['_dt']=iso(r['timestamp_utc'])
            row['_ms']=int(r['timestamp_ms'])
            row['_seg']=int(r['continuity_segment_id'])
            row['_ew']=float(r['ew_index'])
            for k in MATCH_FEATURES + ['ew_drawdown_from_24h_peak_pct']:
                row[k]=f(r.get(k))
            rows.append(row)
    rows.sort(key=lambda r:r['_ms'])
    return rows


def detect_v2(rows, trigger: float, recovery_fraction: float, min_sep_h: int, cap_h: int):
    grouped={}
    for r in rows:
        grouped.setdefault((r['research_window_id'], r['_seg']), []).append(r)
    raw=[]
    for (era, seg), d in sorted(grouped.items(), key=lambda kv: kv[1][0]['_ms']):
        px=[r['_ew'] for r in d]
        n=len(d); i=0; peak_i=0
        while i<n:
            if px[i] >= px[peak_i]: peak_i=i
            dd=(px[i]/px[peak_i]-1.0)*100.0
            if dd <= -trigger:
                trig_i=i; trough_i=i; j=i; close_i=None; closed_by=None
                horizon_ms=d[trig_i]['_ms'] + cap_h*3600_000
                while j<n:
                    if px[j] < px[trough_i]: trough_i=j
                    need=px[trough_i] + recovery_fraction*(px[peak_i]-px[trough_i])
                    if px[j] >= need and j > trough_i:
                        close_i=j; closed_by='RECOVERY_075'; break
                    if d[j]['_ms'] >= horizon_ms:
                        close_i=j; closed_by='MAX_336H'; break
                    j+=1
                if close_i is None:
                    close_i=n-1; closed_by='CENSORED_END_OF_SEGMENT'
                max_dd=(px[trough_i]/px[peak_i]-1.0)*100.0
                raw.append({
                    'research_window_id': era,
                    'continuity_segment_id': seg,
                    'top_utc': d[peak_i]['timestamp_utc'],
                    'trigger_utc': d[trig_i]['timestamp_utc'],
                    'trough_utc': d[trough_i]['timestamp_utc'],
                    'close_utc': d[close_i]['timestamp_utc'],
                    'closed_by': closed_by,
                    'max_drawdown_pct': max_dd,
                    'hours_top_to_trigger': (d[trig_i]['_ms']-d[peak_i]['_ms'])/3600_000,
                    'hours_top_to_trough': (d[trough_i]['_ms']-d[peak_i]['_ms'])/3600_000,
                    'hours_trigger_to_close': (d[close_i]['_ms']-d[trig_i]['_ms'])/3600_000,
                    'active_alt_count_at_top': int(float(d[peak_i]['active_alt_count']))
                })
                i=max(close_i, trig_i)+1
                peak_i=i if i<n else n-1
            else:
                i+=1
    raw.sort(key=lambda e:e['top_utc'])
    kept=[]; last=None
    for e in raw:
        t=iso(e['top_utc'])
        if last is None or (t-last).total_seconds() >= min_sep_h*3600:
            kept.append(e); last=t
    for idx,e in enumerate(kept,1):
        e['episode_id']=f"V2_{e['top_utc'][:10]}_{idx:03d}"
    return kept


def forward_dd48(rows):
    out={}
    groups={}
    for r in rows: groups.setdefault((r['research_window_id'],r['_seg']),[]).append(r)
    for _,d in groups.items():
        for i,r in enumerate(d):
            end=r['_ms']+48*3600_000; worst=0.0; seen=False; j=i+1
            while j<len(d) and d[j]['_ms']<=end:
                seen=True
                dd=(d[j]['_ew']/r['_ew']-1.0)*100.0
                worst=min(worst,dd); j+=1
            out[r['_ms']]=worst if seen else None
    return out


def match_controls(rows, episodes, trigger: float, min_sep_h: int):
    fwd=forward_dd48(rows)
    inside=set()
    by_ms={r['_ms']:r for r in rows}
    for e in episodes:
        lo=int(iso(e['top_utc']).timestamp()*1000); hi=int(iso(e['close_utc']).timestamp()*1000)
        for r in rows:
            if r['research_window_id']==e['research_window_id'] and r['_seg']==e['continuity_segment_id'] and lo<=r['_ms']<=hi:
                inside.add(r['_ms'])
    candidates=[]
    for r in rows:
        if r['ew_drawdown_from_24h_peak_pct'] is None or r['ew_drawdown_from_24h_peak_pct'] < 0.0: continue
        dd=fwd.get(r['_ms'])
        if dd is None or dd <= -trigger: continue
        if r['_ms'] in inside: continue
        if any(r.get(k) is None for k in MATCH_FEATURES): continue
        candidates.append(r)
    scales={}
    for k in MATCH_FEATURES:
        vals=[r[k] for r in rows if r.get(k) is not None]
        mean=sum(vals)/len(vals)
        var=sum((x-mean)**2 for x in vals)/(len(vals)-1)
        scales[k]=(mean,math.sqrt(var))
    def zvec(r):
        return [(r[k]-scales[k][0])/scales[k][1] for k in MATCH_FEATURES]
    cz=[zvec(r) for r in candidates]
    scored=[]
    for e in episodes:
        top_ms=int(iso(e['top_utc']).timestamp()*1000); a=by_ms.get(top_ms)
        if a is None or any(a.get(k) is None for k in MATCH_FEATURES):
            scored.append((math.inf,e,None,'ANCHOR_MATCH_FEATURES_MISSING')); continue
        az=zvec(a); dm=[]
        for c,z in zip(candidates,cz):
            ok=c['research_window_id']==e['research_window_id'] and abs((c['_dt']-iso(e['top_utc'])).total_seconds()) <= 30*86400
            d=math.sqrt(sum((x-y)**2 for x,y in zip(z,az))/len(az)) if ok else math.inf
            dm.append(d)
        mn=min(dm) if dm else math.inf
        scored.append((mn,e,dm,'OK'))
    scored.sort(key=lambda x:(x[0],x[1]['episode_id']))
    used=[]; controls=[]
    for _,e,dm,status in scored:
        if status!='OK':
            controls.append({'episode_id':e['episode_id'],'status':status}); continue
        order=sorted(range(len(dm)), key=lambda k:dm[k]); chosen=None
        for k in order:
            if not math.isfinite(dm[k]): break
            t=candidates[k]['_dt']
            if any(abs((t-u).total_seconds()) < min_sep_h*3600 for u in used): continue
            chosen=k; break
        if chosen is None:
            controls.append({'episode_id':e['episode_id'],'status':'NO_ELIGIBLE_CONTROL_IN_CALIPER'}); continue
        c=candidates[chosen]; used.append(c['_dt'])
        controls.append({
            'episode_id':e['episode_id'],
            'control_id':f"V2CTRL_{c['_dt'].strftime('%Y-%m-%dT%H')}",
            'control_utc':c['timestamp_utc'],
            'research_window_id':c['research_window_id'],
            'continuity_segment_id':c['_seg'],
            'matching_distance_rms_z':dm[chosen],
            'days_from_episode_top':abs((c['_dt']-iso(e['top_utc'])).total_seconds())/86400,
            'fwd_max_dd_48h_pct':fwd[c['_ms']],
            'control_is_local_24h_peak':True,
            'status':'OK',
            'basis':'LOCAL_24H_PEAK_CONTINUATION_NO_NEXT48H_5PCT_DRAWDOWN_TIME_CALIPERED',
            'future_outcome_used_for_control_label_only':True
        })
    return controls


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    readiness=json.loads(READINESS.read_text())
    expected=readiness['artifact_state']['hourly_features.csv.gz']['sha256']
    actual=sha256_file(HOURLY)
    if actual != expected:
        raise SystemExit(f'INPUT_PANEL_SHA_MISMATCH actual={actual} expected={expected}')
    cfg=json.loads(LEGACY_CONFIG.read_text()); contract=json.loads(V2_CONTRACT.read_text())
    assert cfg['episode_drawdown_trigger_pct']==contract['legacy_binding']['episode_drawdown_trigger_pct']==5.0
    assert cfg['episode_recovery_fraction']==contract['legacy_binding']['episode_recovery_fraction']==0.75
    assert cfg['episode_min_separation_hours']==contract['legacy_binding']['episode_min_separation_hours']==24
    rows=load_hourly()
    episodes=detect_v2(rows,5.0,0.75,24,336)
    controls=match_controls(rows,episodes,5.0,24)
    catalog={
      'contract':'V2_EPISODE_CATALOG_v1',
      'authority':'ROUND3_RESEARCH_ONLY',
      'source_values_loaded':False,
      'round1_round2_relabelled':False,
      'episode_count':len(episodes),
      'episodes':episodes
    }
    pair_rows=[]
    c_by={c['episode_id']:c for c in controls}
    for e in episodes:
        c=c_by.get(e['episode_id'],{'status':'NO_CONTROL_RECORD'})
        pair_rows.append({
          'episode_id':e['episode_id'], 'event_utc':e['top_utc'], 'era':e['research_window_id'],
          'control_id':c.get('control_id',''), 'control_utc':c.get('control_utc',''),
          'control_status':c.get('status',''), 'matching_distance_rms_z':c.get('matching_distance_rms_z','')
        })
    catalog_bytes=canonical_bytes(catalog)
    (OUT/'V2_EPISODE_CATALOG.json').write_bytes(catalog_bytes)
    with (OUT/'V2_EVENT_CONTROL_PAIRS.csv').open('w',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=list(pair_rows[0].keys()) if pair_rows else ['episode_id'])
        w.writeheader(); w.writerows(pair_rows)
    pair_sha=sha256_file(OUT/'V2_EVENT_CONTROL_PAIRS.csv')
    impl_sha=sha256_file(Path(__file__))
    trigger_obj={
      'legacy_config_blob_sha':contract['legacy_binding']['config_git_blob_sha'],
      'episode_drawdown_trigger_pct':5.0,
      'episode_recovery_fraction':0.75,
      'episode_min_separation_hours':24,
      'v2_cap_hours_after_trigger':336,
      'control_design':contract['control_design']
    }
    trigger_sha=sha256_bytes(canonical_bytes(trigger_obj))
    eras=sorted({e['research_window_id'] for e in episodes})
    ep_counts={era:sum(e['research_window_id']==era for e in episodes) for era in eras}
    ok=[c for c in controls if c.get('status')=='OK']
    ctrl_counts={era:sum(c.get('research_window_id')==era for c in ok) for era in eras}
    failed={}
    for c in controls:
        if c.get('status')!='OK': failed[c['status']]=failed.get(c['status'],0)+1
    receipt={
      'contract':'V2_EPISODE_CATALOG_MATERIALIZATION_RECEIPT_v1',
      'catalog_contract':'V2_EPISODE_CATALOG_v1',
      'implementation_sha256':impl_sha,
      'input_panel_sha256':actual,
      'trigger_contract_sha256':trigger_sha,
      'episode_count_by_era':ep_counts,
      'control_count_by_era':ctrl_counts,
      'failed_match_reasons':failed,
      'catalog_sha256':sha256_bytes(catalog_bytes),
      'pair_set_sha256':pair_sha,
      'built_at_utc':datetime.now(timezone.utc).isoformat(),
      'source_values_loaded':False,
      'round1_round2_relabelled':False,
      'round3_source_files_read':[],
      'control_design':'DESIGN_B_PRIMARY_STRUCTURAL_PLUS_TIME_CALIPER_FROZEN_FOR_V2'
    }
    (OUT/'V2_MATERIALIZATION_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    status=json.loads(STATUS.read_text())
    status['blockers']=[b for b in status['blockers'] if b!='V2_CATALOG_AND_PAIR_SET_NOT_YET_MATERIALIZED']
    status['v2_materialized']=True
    status['v2_catalog_sha256']=receipt['catalog_sha256']
    status['v2_pair_set_sha256']=receipt['pair_set_sha256']
    status['next_gate']='CONFIGURE_PRIVATE_COLLECTION_ZONE_AND_PROVIDER_TERMS_RECEIPTS'
    STATUS.write_text(json.dumps(status,indent=2,sort_keys=True)+'\n')
    print('ROUND3_V2_MATERIALIZATION_PASS')
    print(json.dumps(receipt,indent=2,sort_keys=True))

if __name__=='__main__': main()
