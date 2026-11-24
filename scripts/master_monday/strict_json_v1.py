"""Unambiguous UTF-8 evidence JSON; reject duplicate keys and non-finite numbers."""
import json
import math


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('DUPLICATE_JSON_KEY:' + key)
        result[key] = value
    return result


def _finite_float(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError('NONFINITE_JSON_NUMBER')
    return result


def _constant(value):
    raise ValueError('NONFINITE_JSON_NUMBER:' + value)


def load_evidence_object(raw: bytes) -> dict:
    value = json.loads(raw.decode('utf-8'), object_pairs_hook=_pairs,
                       parse_float=_finite_float, parse_constant=_constant)
    if not isinstance(value, dict):
        raise ValueError('EVIDENCE_JSON_NOT_OBJECT')
    return value
