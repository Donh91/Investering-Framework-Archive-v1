# Design notes

The production implementation intentionally reuses existing Auto Market State and Entry Signal owners rather than rebuilding a second collector. Handlekompas is source-call-free. Recovery can only re-run already-admitted owner workflows. Exact monthly cost remains UNKNOWN until a durable account-level cost ledger is available; provider quota/token/budget errors are still surfaced immediately when observable.
