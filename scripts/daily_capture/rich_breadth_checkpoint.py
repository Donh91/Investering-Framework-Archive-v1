from __future__ import annotations
import argparse, json, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from scripts.data_terminal import top100_breadth_owner_collector as owner

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--output-root',type=Path,default=Path('03_DAILY_CAPTURE_LOGS/breadth_rich')); a=ap.parse_args()
    q={"vs_currency":"usd","order":"market_cap_desc","per_page":150,"page":1,"sparkline":"false","price_change_percentage":"24h"}
    raw=owner.fetch(owner.BASE+'?'+owner.urllib.parse.urlencode(q)); constituents,exclusions,aggregate=owner.parse(raw)
    now=datetime.now(timezone.utc).replace(microsecond=0); payload={"contract":"RICH_BREADTH_CHECKPOINT_v1","retrieved_at_utc":now.isoformat().replace('+00:00','Z'),"source":"COINGECKO_MARKET_CAP","aggregate":aggregate,"constituents":constituents,"exclusion_count":len(exclusions),"interpolation":False,"forward_fill":False,"authority":owner.AUTHORITY}
    body=json.dumps(payload,sort_keys=True,separators=(',',':'))+'\n'; day=a.output_root/now.strftime('%Y/%m/%d'); day.mkdir(parents=True,exist_ok=True); (day/f"{now.strftime('%H%M%S')}.json").write_text(body); (a.output_root/'LATEST.json').write_text(body); print(json.dumps({"status":"PASS",**aggregate},sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
