import sys,unittest
from pathlib import Path
from unittest.mock import patch
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"/"research"))
from ironflow_18m_wallet_ecology_v1 import run

class TestIronflowWalletEcology(unittest.TestCase):
    def sample(self,path,columns=None):
        month=str(path)[-15:-8]
        vals={
            "2026-09":[("2026-09-01T00:00:00Z","BTC-PERP","0xaaaa","long",100),
                       ("2026-09-02T00:00:00Z","ETH-PERP","0xbbbb","short",200)],
            "2026-10":[("2026-10-01T00:00:00Z","BTC-PERP","0xaaaa","long",300),
                       ("2026-10-02T00:00:00Z","HYPE-PERP","0xcccc","short",400)]
        }
        d=pd.DataFrame(vals[month],columns=["timestamp","market","wallet","position_side","notional_usd"])
        return d
    def test_public_recurrence_denominator_does_not_infer_profit(self):
        with patch("pandas.read_parquet",side_effect=self.sample):
            x=run(Path("/tmp/mock"),months=["2026-09","2026-10"])
        self.assertEqual(x["all_market_liquidation_events"],4)
        self.assertEqual(x["distinct_liquidated_wallet_addresses"],3)
        self.assertEqual(x["wallets_with_2plus_distinct_calendar_months"],1)
        self.assertEqual(x["wallets_liquidated_in_2plus_markets"],0)
        self.assertIs(x["public_wallet_addresses_exported"],False)
        self.assertEqual(x["economic_edge"],"UNPROVEN")
    def test_invalid_signed_notional_fails_closed(self):
        def bad(path,columns=None):
            d=self.sample(path,columns)
            d.loc[0,"notional_usd"]=-50
            return d
        with patch("pandas.read_parquet",side_effect=bad):
            with self.assertRaisesRegex(ValueError,"negative"):run(Path("/tmp/mock"),months=["2026-09","2026-10"])
if __name__=="__main__":unittest.main()
