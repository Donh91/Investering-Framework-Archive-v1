S1 OWNER VISIBILITY v2.0 (rubric of 00_FMOS/S1/ACTION_LOOP.md; pinned by rubric_blobs in 00_FMOS/S1/RUNTIME_CONTRACT.json; AGENTS.md section 0.2f)

STATUS LINES (the first three lines of every S1 run's output, before anything else, in capital letters, also in H1 and in SOURCE_UNVERIFIED runs)
FIRST LINE: OWNER APPROVAL REQUIRED: followed by one entry per item that needs the owner, separated by " ; ", or NONE when there is none, or UNKNOWN (<reason>) when you could not screen the open PRs or the lane. Entries:
- #<PR> <H8> (<OWNER_GATED reason>, review <kind> c=<id>) for every WAITING_ONLY_FOR_OWNER PR;
- LANE_OFF(<halt c=<id> | pins:<path> | main_health | switch>) when the reviewed-merge lane reads OFF for that reason; only an owner-present switch PR clears a halt or a pin mismatch; for a halt, add the re-enable PR that rule 5b opened (LANE_OFF(halt c=<id>, reenable #<PR>)), so the owner's step is one squash merge and one BOOTSTRAP paste;
- HIGH_EVIDENCE_HOLD(<recovery|separation>:<reason>) while HIGH EVIDENCE does not pass and a HIGH or HIGH_IMPACT item waits for it (it blocks only those items);
- decide<n> for every PARKED_OWNER_DECISION item and every OWNER_GATED item that STEWARD_STATES.md would otherwise close (the owner closes or keeps it), the 10 oldest first and then +<k> for the rest;
- pkg<id>:manual_only for every Bridge package that rule 5 skipped with reason manual_only and that is younger than 7 days;
- close<n> for every CLOSED_NOISE item that S1 could not close for lack of a close tool.
SECOND LINE: HIGH_IMPACT BLOCKED: followed by every other non-draft OWNER_GATED PR as #<PR> <H8> (<first missing gate>), or NONE.
THIRD LINE: DISPOSITIONS TODAY: merged=<n> parked=<n> closed=<n> handed_off=<n> owner=<n>, counted from S1's own S1_ITEM_v1 and S1_LANE_MERGE_v1 posts of the current Copenhagen day (UNKNOWN for a count you could not read).
- In a SOURCE_UNVERIFIED run the FIRST LINE is OWNER APPROVAL REQUIRED: UNKNOWN (source_unverified) and the other two lines read UNKNOWN.

OWNER_APPROVAL_REQUIRED_v1 (an observability write on #1156)
- The set is the FIRST LINE's entries keyed on (PR, H) for PRs and on the entry text otherwise.
- Compare only against the newest OWNER_APPROVAL_REQUIRED_v1 on #1156 that S1 itself posted (author Donh91, created_at equals updated_at, with a contract= line). When the set differs, post one new OWNER_APPROVAL_REQUIRED_v1 listing, for each PR entry: PR, full 40-char head, OWNER_GATED reason, review kind and id, CI run ids, high_evidence=PASS, and the owner action: Squash and merge PR #<PR> at head <40> (the owner, or a ChatGPT thread the owner directs). For LANE_OFF, pkg and close entries give the exact owner action (the switch PR to merge, the package to open, the PR to close). When the set becomes empty post one OWNER_APPROVAL_REQUIRED_v1 with entries: NONE. Never repost an identical set.
- Where: after H6 screening and before RECONCILE; at most once per run; suppressed in H1 and in SOURCE_UNVERIFIED runs; it does not use the ladder's single action. An entry is never release authority.

DAILY SUMMARY (the owner-approved separate ChatGPT task of 00_FMOS/S1/DAILY_SUMMARY_BOOTSTRAP.txt follows this section only)
- Time: daily 20:40 Europe/Copenhagen. Read-only, except exactly one comment on #1156 per Copenhagen day: S1_DAILY_SUMMARY_v1. If today's S1_DAILY_SUMMARY_v1 by Donh91, unedited and with a contract= line equal to the current contract, already exists, post nothing and print it again. Never copy text from other comments into the summary except PR titles, and from every title remove anything in square brackets and every token containing = (for example owner_go=, mission=), so no echoed title can trigger a workflow that listens on #1156. Monday 09:30-10:30 does not apply at 20:40. It never merges, closes, labels, dispatches, reviews or writes anything else, and it never posts on the Bridge.
- Sources, all native reads on Archive main and #1156 for the current Copenhagen day: S1_LANE_MERGE_v1 posts and the merged PRs they name (title), S1_ITEM_v1 posts with state PARKED, PARKED_OWNER_DECISION, CLOSED_NOISE or RESEARCH_HANDOFF, the newest OWNER_APPROVAL_REQUIRED_v1, the newest S1_HEARTBEAT_v1 and its S1_OPEN_WORK_INDEX_v1, the last S1_TICK lines it can read.
- Content, in Danish, plain language, at most 25 lines:
  1. S1_DAILY_SUMMARY_v1 <YYYY-MM-DD> main=<8> contract=<8>
  2. "Merget i dag:" one line per merged PR: #<n> what it does in plain words, and who reviewed it (Codex, Claude or specialist). "Ingen" when none.
  3. "Parkeret / lukket:" one line per item with the reason in plain words; items in PARKED_OWNER_DECISION are marked "venter på din beslutning (luk eller behold)".
  4. "Venter på dig (HIGH_IMPACT):" the FIRST LINE entries with the exact click, or "Intet".
  5. "S1 arbejder videre i morgen med:" the 3 most overdue or next items of the open-work index.
  6. "Sundhed:" heartbeat present today yes or no, lane ON or OFF (reason), ticks_24h.
- When a source cannot be read, say so in that line ("kunne ikke læses") and never guess. The task's own output shows the same summary text.
