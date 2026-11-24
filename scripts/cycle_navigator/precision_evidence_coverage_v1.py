"""Research-only CN score coverage; missing evidence is never a normal result."""
from math import isfinite


def valid_score(value):
    return type(value) in (int, float) and isfinite(value) and 0 <= value <= 100


def evidence_coverage(values, min_valid):
    if type(min_valid) is not int or not 1 <= min_valid <= 4 or len(values) > 4:
        raise ValueError('INVALID_PRECISION_COVERAGE_WINDOW')
    n = sum(valid_score(value) for value in values)
    return {
        'coverage_status': ('INSUFFICIENT_EVIDENCE' if n < min_valid else
                            'COMPLETE' if n == 4 else 'PARTIAL'),
        'scoreable_observations': n,
        'unscored_observations': 4 - n,
        'invalid_observations': sum(value is not None and not valid_score(value) for value in values),
        'latest_observation_scoreable': bool(values and valid_score(values[-1])),
    }
