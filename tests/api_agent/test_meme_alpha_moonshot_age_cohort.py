from __future__ import annotations

import unittest

from scripts.api_agent.meme_alpha_moonshot_age_cohort import age_bucket_index, normalize_age_cohorts


class MoonshotAgeCohortTests(unittest.TestCase):
    def test_age_buckets_are_temporal_not_global(self) -> None:
        events=[]
        for i in range(5):
            events.append({"age_minutes":5+i,"buyer_velocity_per_minute":1+i,"transaction_velocity_per_minute":2+i,"volume_to_liquidity_h1":.1+i,"liquidity_usd":10000+i})
        for i in range(5):
            events.append({"age_minutes":300+i,"buyer_velocity_per_minute":100+i,"transaction_velocity_per_minute":200+i,"volume_to_liquidity_h1":10+i,"liquidity_usd":100000+i})
        normalized=normalize_age_cohorts(events)
        young=normalized[4]
        old=normalized[-1]
        self.assertEqual(young["birth_cohort"]["scope"],"EXACT_AGE_BUCKET")
        self.assertEqual(old["birth_cohort"]["scope"],"EXACT_AGE_BUCKET")
        self.assertGreater(young["birth_cohort_percentiles"]["buyer_velocity"],80)
        self.assertGreater(old["birth_cohort_percentiles"]["buyer_velocity"],80)
        self.assertNotEqual(young["birth_cohort"]["age_bucket"],old["birth_cohort"]["age_bucket"])

    def test_sparse_bucket_expands_to_neighbors_without_pretending_exact(self) -> None:
        events=[
            {"age_minutes":5,"buyer_velocity_per_minute":5,"transaction_velocity_per_minute":5,"volume_to_liquidity_h1":1,"liquidity_usd":10000},
            {"age_minutes":16,"buyer_velocity_per_minute":6,"transaction_velocity_per_minute":6,"volume_to_liquidity_h1":1,"liquidity_usd":10000},
            {"age_minutes":17,"buyer_velocity_per_minute":7,"transaction_velocity_per_minute":7,"volume_to_liquidity_h1":1,"liquidity_usd":10000},
            {"age_minutes":31,"buyer_velocity_per_minute":8,"transaction_velocity_per_minute":8,"volume_to_liquidity_h1":1,"liquidity_usd":10000},
            {"age_minutes":32,"buyer_velocity_per_minute":9,"transaction_velocity_per_minute":9,"volume_to_liquidity_h1":1,"liquidity_usd":10000},
        ]
        normalized=normalize_age_cohorts(events)
        row=normalized[1]
        self.assertEqual(row["birth_cohort"]["scope"],"ADJACENT_AGE_BUCKET_EXPANSION")
        self.assertTrue(row["birth_cohort"]["age_comparable"])
        self.assertGreaterEqual(row["birth_cohort"]["peer_count"],5)

    def test_bucket_boundaries(self) -> None:
        self.assertEqual(age_bucket_index(0),0)
        self.assertEqual(age_bucket_index(14.999),0)
        self.assertEqual(age_bucket_index(15),1)
        self.assertEqual(age_bucket_index(1440),8)


if __name__ == "__main__":
    unittest.main()
