from __future__ import annotations
import argparse, json
from pathlib import Path


def main() -> None:
    ap=argparse.ArgumentParser();ap.add_argument('--context',type=Path,required=True);a=ap.parse_args()
    value=json.loads(a.context.read_text())
    comparable=int(value.get('coverage',{}).get('comparable_numeric_metrics',0))
    market_ready=comparable>0 and value.get('delta_status') in {'DELTA_READY','DELTA_DEGRADED_STALE_PREDECESSOR'}
    news=value.get('news_intelligence')
    news_ready=(isinstance(news,dict) and news.get('news_only_review_eligible') is True
                and news.get('verified_count',0)>0
                and isinstance(news.get('event_fingerprint'),str)
                and len(news['event_fingerprint'])==64
                and news.get('canonical_effect') is False
                and news.get('portfolio_effect') is False)
    ready=market_ready or news_ready
    print(f"delta_ready={'true' if ready else 'false'}")
    print(f"comparable_metrics={comparable}")
    print(f"delta_status={value.get('delta_status','UNKNOWN')}")
    print(f"news_review_ready={'true' if news_ready else 'false'}")

if __name__=='__main__':main()
