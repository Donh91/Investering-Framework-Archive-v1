from __future__ import annotations

import unittest

from scripts.api_agent import alpha_arc_direct_new_pair as arc


def topic_address(address: str) -> str:
    return "0x" + "0" * 24 + address.lower().replace("0x", "")


def word_address(address: str) -> str:
    return "0" * 24 + address.lower().replace("0x", "")


def word_uint(value: int) -> str:
    return f"{value:064x}"


def word_int24(value: int) -> str:
    if value < 0:
        value = (1 << 256) + value
    return f"{value:064x}"


class ArcDirectNewPairTests(unittest.TestCase):
    def test_v2_usdc_pair_extracts_exact_target_and_pool(self) -> None:
        target="0x"+"1"*40; pair="0x"+"2"*40
        log={
            "address":arc.VENUES["uniswap_v2"]["emitter"],
            "topics":[arc.VENUES["uniswap_v2"]["topic0"],topic_address(arc.USDC_ERC20),topic_address(target)],
            "data":"0x"+word_address(pair)+word_uint(7),
            "blockNumber":"0x10","blockHash":"0xabc","transactionHash":"0xdef","transactionIndex":"0x1","logIndex":"0x2",
        }
        row=arc.parse_log("uniswap_v2",log,1000,1010,"fixture://rpc")
        self.assertEqual(row["target_token_ca"],target)
        self.assertEqual(row["quote_asset"],arc.USDC_ERC20)
        self.assertEqual(row["quote_representation"],"USDC_ERC20_6")
        self.assertEqual(row["pool_address"],pair)
        self.assertIsNone(row["market_cap_usd"])
        self.assertFalse(row["new_pool_is_new_token"])

    def test_v3_pool_created_decodes_fee_tick_spacing_and_pool(self) -> None:
        target="0x"+"3"*40; pool="0x"+"4"*40
        log={
            "address":arc.VENUES["uniswap_v3"]["emitter"],
            "topics":[arc.VENUES["uniswap_v3"]["topic0"],topic_address(target),topic_address(arc.USDC_ERC20),hex(3000)],
            "data":"0x"+word_int24(60)+word_address(pool),
            "blockNumber":"0x20","blockHash":"0xaaa","transactionHash":"0xbbb","transactionIndex":"0x0","logIndex":"0x5",
        }
        row=arc.parse_log("uniswap_v3",log,2000,2010,"fixture://rpc")
        self.assertEqual(row["target_token_ca"],target)
        self.assertEqual(row["fee"],3000)
        self.assertEqual(row["tick_spacing"],60)
        self.assertEqual(row["pool_address"],pool)
        self.assertIsNone(row["pool_id"])

    def test_v4_native_usdc_is_distinct_18_decimal_quote_representation(self) -> None:
        target="0x"+"5"*40; pool_id="0x"+"a"*64; hooks="0x"+"6"*40
        log={
            "address":arc.VENUES["uniswap_v4"]["emitter"],
            "topics":[arc.VENUES["uniswap_v4"]["topic0"],pool_id,topic_address(arc.ZERO),topic_address(target)],
            "data":"0x"+word_uint(500)+word_int24(10)+word_address(hooks)+word_uint(123)+word_int24(-20),
            "blockNumber":"0x30","blockHash":"0x111","transactionHash":"0x222","transactionIndex":"0x2","logIndex":"0x9",
        }
        row=arc.parse_log("uniswap_v4",log,3000,3010,"fixture://rpc")
        self.assertEqual(row["target_token_ca"],target)
        self.assertEqual(row["quote_asset"],arc.ZERO)
        self.assertEqual(row["quote_representation"],"NATIVE_USDC_18")
        self.assertEqual(row["pool_id"],pool_id)
        self.assertIsNone(row["pool_address"])
        self.assertEqual(row["hooks"],hooks)
        self.assertEqual(row["tick_spacing"],10)

    def test_non_usdc_pool_is_not_promoted_to_candidate(self) -> None:
        a="0x"+"7"*40; b="0x"+"8"*40; pair="0x"+"9"*40
        log={
            "address":arc.VENUES["uniswap_v2"]["emitter"],
            "topics":[arc.VENUES["uniswap_v2"]["topic0"],topic_address(a),topic_address(b)],
            "data":"0x"+word_address(pair)+word_uint(1),
            "blockNumber":"0x40","blockHash":"0x1","transactionHash":"0x2","transactionIndex":"0x0","logIndex":"0x0",
        }
        row=arc.parse_log("uniswap_v2",log,4000,4010,"fixture://rpc")
        self.assertIsNone(row["target_token_ca"])
        self.assertEqual(row["candidate_status"],"AMBIGUOUS_OR_NON_USDC_ANCHORED")

    def test_wrong_emitter_or_topic_fails_closed(self) -> None:
        log={"address":"0x"+"f"*40,"topics":[arc.VENUES["uniswap_v2"]["topic0"]],"data":"0x"}
        self.assertIsNone(arc.parse_log("uniswap_v2",log,1,2,"fixture://rpc"))


if __name__=="__main__":
    unittest.main()
