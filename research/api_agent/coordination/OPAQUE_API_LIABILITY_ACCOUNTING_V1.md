# Opaque API liability accounting proposal v1

Accounting only, no paid release. Generic opaque reservation capability without
request identity, content, sources, prompts, outputs or credentials in a budget
row. No active reservation is introduced. All existing caps, reserves, lane
limits, settled evidence and release rules remain unchanged.

The common guard sums the FULL upper bound across UTC months. Strict exact
fields, independently retained pins, a unique opaque 128-bit ID, fixed creation
month and literal decimal upper <= USD3 are required. Unpinned, missing,
changed, duplicate, settled or expired rows fail closed. No automatic release.
A separate reviewed owner-authorized PR must append the original pin and
matching canonical ledger row together before use; a later settlement design
must preserve original pins and no-replay history.

This is NOT universal synchronization or permission to submit a request.
The common guard is authoritative only for producers invoking current reviewed
guard code and current ledger. Repo-local workflow concurrency does not
serialize arbitrary producers. Before external producer admission, prove every
applicable paid path, native shared atomic admission, current guard/ledger
readback, consent, native claim/no-retry and settlement. An in-flight old
runner cannot be assumed to have seen a newly merged reservation.

Six synthetic tests run in the existing gateway gate. No active reservation,
account data, mission or actual spend. No workflow, trigger, secret or scheduler.
