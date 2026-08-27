from datetime import timedelta
from scripts.research.nfcicredit_t1_pre_top_falsification import TOPS,run


def rows_for(percentile_low_count=0):
    rows=[]
    for i,top in enumerate(TOPS):
        asof=top-timedelta(days=90)
        # 156 weekly points in the frozen 3y vintage. First half low, second half high.
        vals=[]
        for n in range(156):
            d=asof-timedelta(days=7*(155-n))
            vals.append((d,asof,float(n)))
        # Replace latest value to force below/above median without changing frozen rule.
        latest=20.0 if i < percentile_low_count else 140.0
        vals[-1]=(asof,asof,latest)
        rows.extend(vals)
    return rows


def test_kills_when_two_of_three_below_median():
    assert run(rows_for(2))['verdict']=='KILL_DISTRIBUTION_WARNING_LANE'


def test_one_below_does_not_falsely_kill():
    assert run(rows_for(1))['verdict']=='NOT_FALSIFIED_ADMIT_ONLY_TO_INCREMENTAL_SHADOW_TEST'


def test_missing_vintage_fails_closed():
    assert run(rows_for(2)[:-156])['verdict']=='NOT_TESTABLE_SOURCE_UNAVAILABLE'


def test_future_vintage_cannot_fill_missing_historical_vintage():
    rows=rows_for(0)
    missing_asof=TOPS[0]-timedelta(days=90)
    rows=[x for x in rows if x[1] != missing_asof]
    rows.append((missing_asof,missing_asof+timedelta(days=1),999.0))
    assert run(rows)['verdict']=='NOT_TESTABLE_SOURCE_UNAVAILABLE'
