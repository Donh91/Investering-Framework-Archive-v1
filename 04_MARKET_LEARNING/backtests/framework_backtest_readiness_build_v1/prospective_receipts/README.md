# Prospective decision receipts

One immutable JSON file per policy-relevant freeze, denial, trigger, supersession, closeout or explicit no-action decision.

Files in this directory are eligible for A-class validation. Examples and fixtures belong under tests, never here.

Required properties:

- captured within 30 minutes of the decision;
- exact `knowledge_at <= decision_at <= execution_at < label_end`;
- owner-registry version and authority status;
- matching source artifact IDs and SHA-256 values;
- frozen cost contract;
- explicit reason when action permission is `NONE`;
- no final-holdout access.

No historical event may be retroactively inserted as A-class.