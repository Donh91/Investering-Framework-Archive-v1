# Leakage and Negative Controls

The pipeline must fail rows that use future timestamps, later-revised source states without versioning, post-outcome catalyst labels, outcome-derived membership, or inferred missing values.

Negative controls are preregistered as: timestamp permutation within continuity segments, candidate-label permutation, deliberately lagged features and non-semantic control series where available. Controls cannot cross continuity gaps or structural regime boundaries.

Historical event labels may define outcomes but may not be used to choose sensor transforms. Raw dates/prices that fingerprint famous episodes may not enter model decisions unless they are explicit frozen candidate primitives.
