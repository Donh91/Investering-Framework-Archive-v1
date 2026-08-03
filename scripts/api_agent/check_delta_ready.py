from __future__ import annotations
import argparse, json
from pathlib import Path


def main() -> None:
    ap=argparse.ArgumentParser();ap.add_argument('--context',type=Path,required=True);a=ap.parse_args()
    value=json.loads(a.context.read_text())
    comparable=int(value.get('coverage',{}).get('comparable_numeric_metrics',0))
    ready=comparable>0 and value.get('delta_status') in {'DELTA_READY','DELTA_DEGRADED_STALE_PREDECESSOR'}
    print(f"delta_ready={'true' if ready else 'false'}")
    print(f"comparable_metrics={comparable}")
    print(f"delta_status={value.get('delta_status','UNKNOWN')}")

if __name__=='__main__':main()
