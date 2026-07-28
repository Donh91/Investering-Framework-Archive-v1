# DATA PING Thread Handover Protocol v1.0

**Dato:** 2026-07-15 23:02 CEST  
**Status:** CANONICAL_OPERATIONAL  
**Område:** DATA PING thread lifecycle / continuity / GitHub handover  
**Primary owner:** `02_DATA_PING/thread_handoffs/`  
**Authority boundary:** continuity, source provenance, preferences and operating context only. This protocol has no authority to change market state, gates, thresholds, rules, scores, portfolio actions or event closure.

## 1. Purpose

Prevent a slow, long or near-capacity DATA PING conversation from becoming a single point of failure.

The protocol creates a durable GitHub handover package containing everything a fresh DATA PING thread needs in order to continue without restarting the architecture, rediscovering preferences or silently changing governance.

The user continues to work in ChatGPT threads. GitHub remains the invisible durable backend. The user is not expected to open, edit or maintain GitHub manually.

## 2. Exact user trigger

The canonical trigger phrase is:

```text
overlevering til ny tråd!
```

Matching is case-insensitive and tolerant of ordinary punctuation or extra spaces.

Equivalent explicit instructions such as “forbered DATA PING V5”, “lav thread handover” or “denne tråd er blevet for tung” may initiate the same process, but the exact phrase above is the guaranteed trigger.

## 3. When to run

Run the handover when any of the following is true:

1. The user writes the exact trigger phrase.
2. The user states that the active DATA PING thread is slow, heavy or close to its practical limit and asks for transition preparation.
3. A numbered successor thread is explicitly requested.
4. The main framework determines that continuing in the current thread materially increases continuity risk and the user has authorized preparation.

Do not create a handover merely because a new empty thread exists.

## 4. Version activation rule

A new DATA PING version does not become operational merely because its thread has been created.

```text
1. Highest numbered version containing an actual complete DATA PING wins.
2. An empty V5 thread does not supersede an active V4 source.
3. V5 becomes active only when the first complete V5 DATA PING is received and accepted.
4. Until then, the latest accepted V4 payload and pointer remain canonical.
5. The first accepted V5 packet must identify the last accepted V4 run as predecessor or explicitly preserve a lineage gap.
```

## 5. Required GitHub structure

```text
02_DATA_PING/thread_handoffs/
├── latest_thread_handover_state.json
├── bootstrap/
│   └── YYYY-MM-DD__data-ping-vN__bootstrap.md
└── history/
    └── YYYY-MM-DD__data-ping-vN-to-vNplus1__handover.md
```

The protocol owner remains:

```text
02_DATA_PING/protocols/2026-07-15__data-ping-thread-handover-protocol-v1-0__canonical.md
```

The supplemental collection owner is:

```text
02_DATA_PING/protocols/2026-07-28__data-ping-deep-capture-escalation-protocol-v1__canonical.md
```

Its operational ledger is:

```text
02_DATA_PING/operational_handoffs/deep_capture_request_ledger_v1.json
```

## 6. Required handover package

Every completed thread handover must contain:

### A. Source and lineage

- outgoing thread/version;
- intended incoming thread/version;
- latest accepted DATA PING run ID;
- latest accepted supplement ID, if any;
- predecessor pointer;
- accepted payload, receipt and registry paths;
- readback/hash status;
- explicit unresolved lineage gaps;
- confirmation that no missing packet was reconstructed.

### B. Active architecture

- active DATA PING spec and overlay versions;
- all active fallback/patch versions;
- current source hierarchy;
- source-specific authority boundaries;
- known API/location failures;
- which layers are canonical, shadow, venue-specific, proxy-only, pending or unavailable;
- current quality-grade logic.

### C. Active framework state

- active event ID and type;
- current framework edge, alert and event states;
- active gates;
- resolution candidate;
- current positive evidence;
- cooling/contradictory evidence;
- unresolved confirmation requirements;
- portfolio and entry status;
- latest user-facing action.

### D. User preferences and layout rules

- preferred language and output density;
- required acceptance structure;
- wording preferences;
- interpretation and action format;
- handling of RAW 1–3 and 5–7 day requests;
- missing-data rules;
- separation between collector, framework and shadow research;
- requirements around GitHub invisibility and autonomous archival;
- permission for the main framework to ask the user for a ready-to-copy Custom GPT prompt when weekly reconciliation or a material event requires data beyond the normal DATA PING;
- requirement that such prompts follow the active deep-capture protocol and request only missing or event-relevant evidence.

### E. Research and experiment continuity

- active OTA/SCTA holdout status;
- maturity dates and confounds;
- redundancy counter and definition of an independent event;
- daily sensor-pair lab status;
- experiment eligibility boundaries;
- unconfirmed hypotheses and kill criteria;
- frozen outputs that must not be retroactively edited.

### F. Pending work

- missing sources and blockers;
- pending settlements, closes and maturity marks;
- operational improvements already implemented;
- next meaningful trigger conditions;
- tasks that must not be repeated;
- pending, partial or completed deep-capture request IDs;
- active event-driven capture windows;
- latest completed weekly deep-capture package;
- any copy-ready Custom GPT prompt prepared but not yet sent;
- explicit deep-capture deduplication state by ISO week, method scope and event cluster.

### G. New-thread bootstrap instructions

The bootstrap file must tell the fresh thread to:

1. read the latest handover pointer;
2. read the full historical handover;
3. read the latest accepted-log pointer and active registry;
4. read the active deep-capture protocol and request ledger;
5. confirm pending requests, active event windows and completed weekly package status;
6. confirm the loaded state in a compact receipt;
7. wait for the first complete DATA PING in the new version;
8. preserve the older active version until that packet arrives;
9. make no market, rule or portfolio change merely from the handover;
10. issue no duplicate weekly or event-driven Custom GPT request.

## 7. Trigger execution sequence

When the trigger is received, the main framework must perform the following sequence:

```text
1. Resolve latest accepted DATA PING pointer on main.
2. Resolve latest active registry and linked supplements.
3. Resolve the deep-capture protocol and current request ledger.
4. Review the outgoing thread for new preferences, patches, source changes, experiments, pending prompts and unresolved tasks.
5. Create a dedicated task branch before every write.
6. Write one comprehensive history handover.
7. Write one paste-ready bootstrap file for the successor thread.
8. Update latest_thread_handover_state.json.
9. Create an archive-governance receipt.
10. Read back every changed file.
11. Verify changed-file scope.
12. Merge through a pull request.
13. Read back main and report PASS/FAIL.
14. Return a compact user-facing startup instruction.
```

## 8. Handover depth standard

The handover should be deliberately comprehensive. It is not a conversational summary.

It must preserve:

- architecture;
- state;
- source semantics;
- operational history;
- preferences;
- formatting requirements;
- research boundaries;
- unresolved decisions;
- reasons behind the current action.

Repetition is acceptable where it prevents a fresh thread from misinterpreting a critical rule. Unsupported claims and reconstructed values are forbidden.

## 9. Fresh-thread acknowledgement contract

The successor thread should return:

```text
DATA_PING_THREAD_BOOTSTRAP
handover_status: PASS / PARTIAL / FAIL
loaded_handover_id: <id>
latest_accepted_log_id: <id>
active_source_version: <version still containing latest complete ping>
intended_successor_version: <new version>
active_event_id: <id>
deep_capture_protocol_loaded: YES / NO
deep_capture_pending_request_ids: <list or NONE>
latest_weekly_deep_capture_status: <status or NONE>
framework_state: <state>
portfolio_action: NONE
ready_for_first_complete_new_version_ping: YES / NO
```

This is a continuity receipt, not a new market analysis.

## 10. Update rules during the new thread

The handover packet is a starting snapshot, not a replacement for normal accepted-log archiving.

- Each complete new DATA PING continues to receive payload, receipt, registry and pointer updates.
- New preferences or architecture changes accumulate during the new thread.
- The deep-capture ledger is checked before any weekly or event-driven Custom GPT request.
- A new material event may prepare one targeted request under the deep-capture protocol.
- At the next handover, the new packet supersedes the previous handover pointer but does not delete history.
- A handover may reference existing canonical files rather than duplicate entire raw payloads, but the operational context and learned preferences must be readable directly from the handover.

## 11. Safety and forbidden behavior

Forbidden:

- using the handover itself as new market data;
- activating the new version before a complete packet arrives;
- reconstructing missing predecessor pings;
- converting shadow closes into canonical closes;
- promoting venue-specific OKX data to market-wide truth;
- treating incomplete ETF zero rows as zero flow;
- silently changing thresholds, gates or portfolio status;
- rewriting frozen Cycle Navigator outputs or research holdouts;
- creating retrospective experiment rows;
- issuing duplicate deep-capture prompts for the same week, method scope or event cluster;
- treating a prepared prompt or unvalidated Custom GPT package as accepted evidence;
- writing directly to main before a task branch exists.

## 12. Current operational status

```yaml
protocol_version: 1.0
trigger_phrase: "overlevering til ny tråd!"
thread_handover_active: YES
deep_capture_protocol_active: YES
deep_capture_request_ledger_required: YES
future_thread_must_preserve_pending_requests: YES
github_backend_required: YES
user_github_action_required: NO
branch_first_required: YES
readback_required: YES
hash_or_blob_validation_required: YES
new_version_requires_complete_ping: YES
market_authority: ZERO
portfolio_authority: ZERO
```
