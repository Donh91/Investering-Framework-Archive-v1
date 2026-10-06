# S9 - Launch MEV / Sniper Execution Quality v1

Status: IMPLEMENTATION_READY / RESEARCH_ONLY / EXTEND_EXISTING
Priority: P1
Master issue: #1512
Owner: Meme Alpha Lab Forensics Qualification Shadow / microstructure

## Purpose

Separate reproducible launch execution structure from unsupported labels such as insider, sniper, MEV or private bundle.

Existing Family C already owns FIRST_SECONDS_BUNDLE_SNIPER_MICROSTRUCTURE.
Existing launch replay already preserves block number, transaction index, log index, transaction hash and partial transaction enrichment.

The missing primitive is deterministic execution-order classification.

## Evidence classes

- SAME_TX_ATOMIC_MULTI_EVENT
- SAME_BLOCK_MULTI_TX
- SAME_ORIGINATOR_MULTI_EVENT
- SAME_TARGET_SELECTOR_PATTERN
- SEQUENTIAL_NONCE_PATTERN
- GAS_PRIORITY_OBSERVED
- PRIVATE_BUNDLE_PROVEN
- UNKNOWN

Only the first five are initially implementable from existing admitted data.

## Interpretation rule

Same block is not a bundle.
Same transaction can prove atomic co-execution of events inside that transaction, but does not by itself prove malicious intent, private orderflow or insider status.
Repeated router/selector is not common ownership.
High gas/priority is execution behavior, not skill or insider evidence.

## First capability

Given ordered launch buy-like events plus existing transaction enrichments, preserve:
- first tradable block;
- block distance from launch;
- transaction index;
- log index;
- tx hash;
- originator candidate;
- token recipient/buyer where semantics prove it;
- target + selector;
- nonce;
- gas fields where available;
- exact value where available.

Derive only factual group structure:
- number/share of first-N events in launch block;
- same-tx multi-event groups;
- same-block multi-tx groups;
- same-originator multi-event groups;
- repeated target/selector groups;
- sequential nonce motifs for the same originator.

## Explicit non-claims

Do not infer:
- insider;
- private bundle;
- MEV;
- Sybil/common owner;
- skill;
- malicious intent;
- public-information advantage.

Those require independent evidence.

## Next stage after capability

Join execution classes to:
- wallet independence/relationship resolver;
- first-sale latency;
- early-buyer retention;
- realized exit quality;
- matched ordinary early buyers;
- later outcomes.

Then test whether execution structure itself adds information.

## Authority

RESEARCH_ONLY.
No alerts.
No trade execution.
No portfolio action.
