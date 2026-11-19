import copy
from decimal import Decimal
import unittest
from scripts.api_agent.astra_provider_settlement_v1 import groups, KEY, SETTLED, SCOPE, validate_append_only


def fixture(day=19, mid="ASTRA-TEST-1", run=1, cost=3.5, amounts=None):
    stamp = f"2026-11-{day:02d}"
    contract = f"OWNER_ASTRA_PROVIDER_PERIOD_SETTLEMENT_202611{day:02d}_V1"
    row = dict(work_id=mid, status=SETTLED, settlement_group=contract, no_retry=True,
               reconciliation_required=False, consumed_run_id=run, consumed_response_id=f"resp_TEST{run}",
               consumed_receipt_sha256=f"{run:064x}", consumed_estimated_upper_usd=cost, upper_usd=20)
    proof = dict(work_id=mid, run_id=run, result_comment_id=run+100, response_id=f"resp_TEST{run}",
                 receipt_sha256=f"{run:064x}", started_at=stamp+"T01:00:00Z",
                 completed_at=stamp+"T02:00:00Z", conclusion="success", estimated_upper_usd=cost)
    amounts = amounts or {stamp: 2.0}
    group = dict(contract=contract, source="owner provider cost CSV export "+stamp,
                 usage_csv_sha256=f"{run+100:064x}", bridge_commit="a"*40,
                 evidence_path="reports/claude/automated/2026/11/SETTLEMENT/evidence/cost.csv",
                 observed_period_start=min(amounts), observed_period_end=stamp,
                 coverage_cutoff_utc=stamp+"T03:00:00Z",
                 export_before_utc=f"2026-11-{day+1:02d}T00:00:00Z", provider_period_spend_usd=sum(amounts.values()),
                 daily_provider_spend_usd=amounts, amount_scope=SCOPE, no_replay=True,
                 native_receipts=[proof], additional_native_runs=[])
    return row, group


class TestProviderSettlement(unittest.TestCase):
    def test_native_upper_not_provider_low(self):
        r, g = fixture()
        self.assertEqual(groups({KEY: [g]}, [r]), ({r['work_id']}, {'2026-11': Decimal('3.5')}))

    def test_provider_upper_if_greater(self):
        r, g = fixture(cost=.5)
        self.assertEqual(groups({KEY: [g]}, [r])[1], {'2026-11': Decimal('2.000000')})

    def test_overlap_daily_max_and_unique_receipts(self):
        r, g = fixture(cost=.3)
        s, h = fixture(day=20, mid='ASTRA-TEST-2', run=2, cost=.4,
                       amounts={'2026-11-19': 5.0, '2026-11-20': 4.0})
        self.assertEqual(groups({KEY: [g, h]}, [r,s])[1], {'2026-11': Decimal('9.000000')})
        self.assertEqual(groups({KEY: [h, g]}, [r,s])[1], {'2026-11': Decimal('9.000000')})

    def test_native_estimates_sum_across_groups(self):
        r, g = fixture(cost=6.)
        s, h = fixture(day=20, mid='ASTRA-TEST-2', run=2, cost=5.,
                       amounts={'2026-11-19': 5.0, '2026-11-20': 4.0})
        self.assertEqual(groups({KEY: [g,h]}, [r,s])[1], {'2026-11': Decimal('11.0')})

    def test_pending_rows_unchanged(self):
        r, g = fixture()
        s = {'work_id':'ASTRA-NEW-2', 'status':'OWNER_RESERVED_PREHTTP'}
        self.assertEqual(groups({KEY:[g]},[r,s])[0], {r['work_id']})
        self.assertEqual(groups({},[s]), (set(), {}))

    def test_missing_binding_or_replay_fails(self):
        r, g = fixture()
        for x, y in (([r], []), ([], [g]), ([r,r], [g]), ([r], [g,g]),
                     ([{**r,'status':'OWNER_RESERVED_PREHTTP'}], [g]),
                     ([{**r,'settlement_group':'OTHER'}], [g]),
                     ([{**r,'no_retry':False}], [g]),
                     ([{**r,'reconciliation_required':True}], [g])):
            with self.subTest(rows=x, groups=y), self.assertRaises(ValueError):
                groups({KEY:y}, x)

    def test_mutated_receipt_rejected(self):
        r, g = fixture()
        for field, changed in (('run_id',2),('response_id','resp_OTHER'),('receipt_sha256','b'*64),
                               ('work_id','ASTRA-OTHER-2'),('estimated_upper_usd',1.),
                               ('completed_at','2026-11-19T04:00:00Z'),('conclusion','failure')):
            bad = copy.deepcopy(g); bad['native_receipts'][0][field]=changed
            with self.subTest(field=field), self.assertRaises(ValueError): groups({KEY:[bad]},[r])

    def test_mutated_group_rejected(self):
        r, g = fixture()
        for field, changed in (('usage_csv_sha256','0'*64),('bridge_commit','0'*40),
                               ('provider_period_spend_usd',0.),('daily_provider_spend_usd',{}),
                               ('source','untrusted'),('export_before_utc','2026-11-21T00:00:00Z'),
                               ('no_replay',False),('amount_scope','per-model allocation'),
                               ('evidence_path','../private.csv')):
            bad = copy.deepcopy(g); bad[field]=changed
            with self.subTest(field=field), self.assertRaises(ValueError): groups({KEY:[bad]},[r])

    def test_nonowning_route_not_a_reservation(self):
        r, g = fixture()
        g['additional_native_runs'] = [dict(route='RESEARCH_LAB_SOL',run_id=2,result_comment_id=102,
            receipt_sha256='f'*64,started_at='2026-11-19T01:00:00Z', completed_at='2026-11-19T02:00:00Z',conclusion='success')]
        self.assertEqual(groups({KEY:[g]},[r])[0],{r['work_id']})
        g['additional_native_runs'][0]['run_id']=1
        with self.assertRaises(ValueError): groups({KEY:[g]},[r])

    def test_no_arbitrary_private_identifiers(self):
        r, g = fixture(); g['organization_id']='PRIVATE'
        with self.assertRaises(ValueError): groups({KEY:[g]},[r])

    def test_receipt_reused_by_pending_row_fails(self):
        r,g=fixture()
        s=dict(work_id='ASTRA-NEW-2',status='CONSUMED_PENDING_INVOICE',consumed_run_id=1)
        with self.assertRaises(ValueError): groups({KEY:[g]},[r,s])

    def test_append_only_preflight_blocks_history_rewrite(self):
        r,g=fixture(); s,h=fixture(day=20,mid='ASTRA-TEST-2',run=2)
        before={KEY:[g], 'astra_mission_reservations':[r]}
        after={KEY:[g,h], 'astra_mission_reservations':[r,s]}
        validate_append_only(before, after)
        with self.assertRaises(ValueError): validate_append_only(before, {KEY:[], 'astra_mission_reservations':[]})
        bad=copy.deepcopy(after); bad['astra_mission_reservations'][0]['upper_usd']=19
        with self.assertRaises(ValueError): validate_append_only(before,bad)

    def test_cross_month_cost_provision_is_separate(self):
        r,g=fixture(day=20,cost=4.)
        g['observed_period_start']='2026-10-31'
        g['daily_provider_spend_usd']={'2026-10-31':3.0,**{f'2026-11-{n:02d}':0.0 for n in range(1,21)}}
        g['provider_period_spend_usd']=3.0
        g['native_receipts'][0]['started_at']='2026-10-31T22:00:00Z'
        self.assertEqual(groups({KEY:[g]},[r])[1],{'2026-10':Decimal('4.0'),'2026-11':Decimal('4.0')})



def canonical_ledger():
    import json
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    return json.loads((root / "research/api_agent/coordination/API_PENDING_BILLING_RISK_V1.json").read_text())


def expected_pending(ledger=None):
    ledger = canonical_ledger() if ledger is None else ledger
    outstanding = list(ledger.get("unresolved", []))
    outstanding += [r for r in ledger.get("owner_reservations", []) if r["status"] == "OWNER_RESERVED_PREHTTP"]
    outstanding += [r for r in ledger.get("astra_mission_reservations", []) if r["status"] != SETTLED]
    return float(sum(r["lower_usd"] for r in outstanding)), float(sum(r["upper_usd"] for r in outstanding)), len(outstanding)


def expected_provision(ledger, month):
    from datetime import date
    from decimal import ROUND_CEILING
    daily, native = {}, Decimal(0)
    for group in ledger.get(KEY, []):
        for day, amount in group["daily_provider_spend_usd"].items():
            if day.startswith(month + "-"):
                daily[day] = max(daily.get(day, Decimal(0)), Decimal(str(amount)))
        for proof in group["native_receipts"]:
            if proof["started_at"][:7] <= month <= proof["completed_at"][:7]:
                native += Decimal(str(proof["estimated_upper_usd"]))
    provider = sum(daily.values(), Decimal(0)).quantize(Decimal("0.000001"), rounding=ROUND_CEILING)
    legacy = ledger.get("owner_astra_provider_period_settlement")
    old = max(legacy["provider_period_spend_usd"], legacy["native_estimated_total_usd"]) if legacy and month == "2026-11" else 0
    return float(max(provider, native)) + old


class TestCanonicalSeed(unittest.TestCase):
    def test_initial_nine_historical_ids_and_one_non_reservation(self):
        ledger = canonical_ledger()
        group = next(g for g in ledger[KEY] if g["contract"] == "OWNER_ASTRA_PROVIDER_PERIOD_SETTLEMENT_20261119_V1")
        self.assertEqual(group["usage_csv_sha256"], "9a9ac228a362282ce2fbe1dbb59777eec5a1397380b31ee30d70a5be64ec9508")
        self.assertEqual(group["bridge_commit"], "bf9dbee58861c806e0ba32ce5d8ad73da58d1e7b")
        self.assertEqual(group["provider_period_spend_usd"], 4.526865)
        self.assertEqual(len(group["native_receipts"]), 9)
        self.assertEqual([p["run_id"] for p in group["additional_native_runs"]], [44513737625])
        self.assertEqual(sum(Decimal(str(p["estimated_upper_usd"])) for p in group["native_receipts"]), Decimal("9.136115"))
        ids, provision = groups(ledger, ledger["astra_mission_reservations"])
        self.assertTrue(set(p["work_id"] for p in group["native_receipts"]) <= ids)
        self.assertGreaterEqual(provision["2026-11"], Decimal("9.136115"))
        self.assertEqual((ledger["normal_budget_usd"], ledger["absolute_budget_usd"], ledger["owner_budget_reserve_usd"]), (50, 100, 4))

if __name__=='__main__': unittest.main()
