from __future__ import annotations
import argparse, hashlib, json, tarfile
from datetime import datetime, timezone
from pathlib import Path


def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run-id',required=True);ap.add_argument('--output-root',type=Path,required=True);ap.add_argument('--max-owner-bytes',type=int,default=2_000_000);ap.add_argument('--max-monthly-compressed-bytes',type=int,default=20_000_000);ap.add_argument('owner_dirs',nargs='*');a=ap.parse_args()
    now=datetime.now(timezone.utc);month_root=a.output_root/f'{now:%Y/%m}';dest=month_root/f'{now:%d}';dest.mkdir(parents=True,exist_ok=True)
    existing=sum(p.stat().st_size for p in month_root.rglob('*.tar.gz')) if month_root.exists() else 0;rows=[];created=[]
    try:
        for raw in a.owner_dirs:
            d=Path(raw)
            if not d.exists():continue
            files=[p for p in sorted(d.rglob('*')) if p.is_file()];size=sum(p.stat().st_size for p in files)
            if size>a.max_owner_bytes:raise RuntimeError(f'RAW_SIZE_GUARD_TRIPPED:{d}:{size}')
            target=dest/f'{d.name}-{a.run_id}.tar.gz'
            with tarfile.open(target,'w:gz',compresslevel=9) as tar:
                for p in files:tar.add(p,arcname=str(Path(d.name)/p.relative_to(d)))
            created.append(target);members=[{'path':str(Path(d.name)/p.relative_to(d)),'bytes':p.stat().st_size,'sha256':sha256(p)} for p in files]
            rows.append({'owner_dir':d.name,'archive_path':str(target),'archive_bytes':target.stat().st_size,'archive_sha256':sha256(target),'source_bytes':size,'members':members})
        added=sum(r['archive_bytes'] for r in rows)
        if existing+added>a.max_monthly_compressed_bytes:raise RuntimeError(f'RAW_MONTHLY_REPO_GUARD_TRIPPED:{existing+added}:{a.max_monthly_compressed_bytes}')
    except Exception as exc:
        for p in created:
            p.unlink(missing_ok=True)
        incident={'contract':'RAW_STORAGE_GUARD_INCIDENT_v1','run_id':a.run_id,'created_at_utc':now.isoformat().replace('+00:00','Z'),'status':'BLOCKED','reason':str(exc),'existing_month_bytes':existing,'monthly_limit_bytes':a.max_monthly_compressed_bytes,'required_action':'MIGRATE_RAW_LANE_TO_DEDICATED_DATA_REPOSITORY'}
        incident_path=a.output_root/'incidents'/f'RAW_STORAGE_{a.run_id}.json';incident_path.parent.mkdir(parents=True,exist_ok=True);incident_path.write_text(json.dumps(incident,sort_keys=True,separators=(',',':'))+'\n')
        raise SystemExit(str(exc))
    manifest={'contract':'RAW_OWNER_PAYLOAD_MANIFEST_v2','run_id':a.run_id,'created_at_utc':now.isoformat().replace('+00:00','Z'),'retention':'PERMANENT_GIT_COLD_LANE','existing_month_bytes_before_run':existing,'added_compressed_bytes':sum(r['archive_bytes'] for r in rows),'monthly_limit_bytes':a.max_monthly_compressed_bytes,'archives':rows}
    manifest_path=dest/f'RAW_MANIFEST_{a.run_id}.json';manifest_path.write_text(json.dumps(manifest,sort_keys=True,separators=(',',':'))+'\n')
    print(json.dumps({'status':'PASS','archives':len(rows),'manifest':str(manifest_path),'compressed_bytes':manifest['added_compressed_bytes'],'month_total_bytes':existing+manifest['added_compressed_bytes']},sort_keys=True))
if __name__=='__main__':main()
