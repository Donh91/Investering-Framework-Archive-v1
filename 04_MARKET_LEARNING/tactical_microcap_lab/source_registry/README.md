# Signal Source Registry

This registry tracks the quality and timing of recurring discovery sources without treating source claims as proof.

Public repository rule:

- use non-identifying aliases only, for example `TG_SOURCE_A`;
- do not store private Telegram group names, invite links, usernames, copied private messages or identifying metadata;
- store timing/outcome observations only when they materially improve research;
- include bad/dead calls as well as winners;
- separate `source was early` from `source had confirmed privileged access`;
- do not infer malicious intent from late or poor calls.

Possible research states:

```text
UNASSESSED
INSUFFICIENT_SAMPLE
EARLY_DISCOVERY_CANDIDATE
CONSISTENTLY_EARLY_SUPPORTED
MIXED_TIMING
OFTEN_LATE
DISTRIBUTION_RISK
```

Use `../schemas/SIGNAL_SOURCE_RECORD_V1.json` as the minimum machine-readable shape.

Actual private identity-level tracking, if ever justified, belongs only in the private plane.
