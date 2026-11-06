#!/usr/bin/env python3
"""Bounded read-only Hyperliquid trades/HIP4 source QA, NOT alpha prediction.
Ironflow (ironflow.sh), CC BY 4.0. No addresses or raw fills in public receipt.
"""
import argparse,hashlib,json
from pathlib import Path
import duckdb

DAYS=("2026-10-07","2026-10-23")
def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for buf in iter(lambda:f.read(1<<20),b""):h.update(buf)
    return h.hexdigest()
def scan(root,days=DAYS):
    con=duckdb.connect(database=":memory:")
    con.execute("SET memory_limit='3GB'")
    results=[]
    for day in days:
        path=root/"trades"/(day+".parquet")
        if not path.is_file() or not (1000000<path.stat().st_size<270000000):
            raise ValueError("Trade shard missing or too large")
        rows=con.execute("""
          SELECT market, COUNT(*) AS trades, COUNT(DISTINCT tid) AS distinct_tid,
                 COUNT_IF(taker_side='buy') AS buy_taker_trades,
                 COUNT_IF(taker_side='sell') AS sell_taker_trades,
                 ROUND(SUM(notional),2) AS total_quote_notional,
                 ROUND(SUM(CASE WHEN taker_side='buy' THEN notional ELSE 0 END),2) AS taker_buy_quote,
                 ROUND(SUM(CASE WHEN taker_side='sell' THEN notional ELSE 0 END),2) AS taker_sell_quote,
                 COUNT_IF(liquidation) AS liquidation_marked_trades,
                 ROUND(SUM(CASE WHEN liquidation THEN notional ELSE 0 END),2) AS liquidation_marked_notional,
                 COUNT_IF(buyer='0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
                    OR seller='0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee') AS placeholder_trade_count
          FROM read_parquet(?)
          WHERE market_class='perp' AND market IN ('BTC-PERP','ETH-PERP','HYPE-PERP')
          GROUP BY market ORDER BY market
        """,[str(path)]).fetchdf().to_dict("records")
        for row in rows:
            for k,v in row.items():
                if hasattr(v,"item"):row[k]=v.item()
            if int(row["trades"])!=int(row["distinct_tid"]):
                raise ValueError("Non-unique (market,tid) in studied market/day")
        results.append({"dataset":"hyperliquid-trades","day":day,"bytes":path.stat().st_size,
                        "sha256":sha(path),"venue_cohorts":rows})
        p2=root/"outcomes"/(day+".parquet")
        if not p2.is_file() or not (10000<p2.stat().st_size<30000000):
            raise ValueError("HIP4 shard missing or too large")
        data=con.execute("""
          SELECT COUNT(*) AS fills, COUNT(DISTINCT market_id) AS distinct_market_ids,
                 COUNT(DISTINCT address) AS distinct_wallets,
                 COUNT_IF(crossed) AS crossed_fills,
                 COUNT_IF(price<0 OR price>1 OR price IS NULL) AS suspicious_price_count,
                 COUNT_IF(fee_token!='USDC' AND fee_token IS NOT NULL) AS non_usdc_fee_count,
                 COUNT_IF(market IS NULL OR market='') AS missing_market_identities
          FROM read_parquet(?)
        """,[str(p2)]).fetchdf().to_dict("records")[0]
        for k,v in data.items():
            if hasattr(v,"item"):data[k]=v.item()
        results.append({"dataset":"hyperliquid-outcomes","day":day,
                        "bytes":p2.stat().st_size,"sha256":sha(p2),
                        "source_qa":data,
                        "interpretation":"NO_ORIGINAL_MARKET_METADATA_ASOF_OR_RESOLVED_OUTCOME_PROOF"})
    return {"contract":"IRONFLOW_TICK_HIP4_T1_V1",
            "source":"Ironflow (ironflow.sh), CC BY 4.0",
            "not_trading_authority":True,
            "source_class":"RETROSPECTIVE_PUBLIC_DATA_2026_11_SNAPSHOT",
            "dataset_rows_and_schema_reconciled":"SCOPED_ONLY",
            "results":results}
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    a=parser.parse_args()
    d=scan(a.root)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(d,indent=2,allow_nan=False)+"\n",encoding="utf8")
    print(json.dumps({"result":"SCOPED_TICK_HIP4_QA_DONE","shards":len(d["results"])}))
if __name__=="__main__":main()
