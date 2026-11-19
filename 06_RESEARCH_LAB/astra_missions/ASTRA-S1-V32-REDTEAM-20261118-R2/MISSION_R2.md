# ASTRA GPT-6.2 MAX MISSION: break the LIVE S1 v3.2 supervisor and the LIVE paid launcher

- **mission_id:** ASTRA-S1-V32-REDTEAM-20261118-R2 (upgraded package; this supersedes the earlier R2 bundle of a pre-merge candidate)
- **requested_by:** the owner (Donh91), 2026-11-18. ONE run. The budget is owner-approved and reserved.
- **prepared_by:** Claude (setup session). Maturity: TEST_DESIGN.
- **input:** `BUNDLE_R2.md` (self-contained, byte-exact blobs of main f2716ad8). No tools, no network, no code execution.

## 1. Role and standard

You are the strongest adversarial reviewer this system will ever get. The code
is **live**. Your findings go straight into fix packages, so precision beats
volume.

- Assume a capable attacker who controls one of: a PR branch, a same-repo workflow with `issues:write`, one of the agents that posts as Donh91, or GitHub misbehaviour (late or missing crons, throttling, partial pages, eventual consistency, re-runs).
- Every finding needs a concrete, step-by-step scenario, and an exact `path:line` from the bundle (F-section line numbers; for an excerpt, its header gives the first line).
- No praise and no design restatement.
- Before you report a finding, try to falsify it against the bundle text. Report it only if it survives.

## 2. Priorities (spend your reasoning in this order)

### P-A. Paid launcher (F8–F12)

This path is new, handles a paid secret, and has never been red-teamed. Prove
or break each property:

1. **At most one paid POST per mission, ever.** Consider:
   - two owner comments in quick succession;
   - a re-run of the `paid` job (`run_attempt`);
   - the `verify`/`paid` race;
   - the claim comment and artifact pairing (deleted, edited or duplicated claims);
   - concurrency groups;
   - a crash between the POST and persisting the response id;
   - `recover` used as a POST path.
2. **The cost bound holds.** Check:
   - `estimate_cost`, the bytes-as-tokens bound, the +20k overhead and the 272k long-context boundary (off-by-one, JSON escaping, multibyte UTF-8);
   - reasoning tokens inside `max_output_tokens`;
   - whether provider-side extras (background mode, cache) can exceed the bound;
   - guard PASS vs reservation-row matching (`upper_usd == max_usd`), duplicate rows, other liabilities, the month boundary.
3. **The trigger is authentic.** Check:
   - the `if:` clauses against the script checks;
   - `login` vs `actor` vs `author_association`;
   - comments on PRs vs on the issue;
   - edited comments;
   - prefix, whitespace, Unicode and confusable parsing of `<mission_id> <bundle_sha256>`;
   - mission folders added by a merged PR;
   - TOCTOU between the bundle hash check and the request built from the tree at the release SHA.
4. **The secret stays contained.** Check:
   - which steps see `OPENAI_API_KEY`;
   - logs, artifacts, error messages and exceptions that echo headers or bodies;
   - checkout credentials;
   - action pinning;
   - third-party actions in secret jobs.
5. **The output and data boundary holds.** The answer becomes a public artifact. Can mission content (public repo text) inject instructions that make the model emit something harmful into that public artifact, or make the launcher mis-handle it? Is any private-plane read possible?

### P-B. S1 merge safety (F1–F7)

- Can S1 squash-merge anything that is not lane-eligible, not exact-head reviewed, not CI-green with the five bound check runs, or merge during a halt?
- Re-verify the regression table in §2 of the bundle.

### P-C. Liveness and cost of the brief

- Design the **minimal fix for the observed push-skip race** (bundle §1.3): a superseded build must not publish an older main, or a skipped push must guarantee a later build of the newest main, within the same API budget.
- Find any other permanent NOOP or livelock.
- Find any build storm that exceeds about 1 build per hour, or the 300-call cap.

### P-D. Trust boundary

All agents post as Donh91. Propose the **cheapest binding** that stops one
compromised agent from forging a merge-enabling Claude receipt. Examples to
weigh:
- report_blob in a private repo at a commit only Claude pushes;
- a signed field;
- the branch protection of `claude/log`.

Give cost and residual risk for each.

### P-E. Deletion review (future-proofing)

Give at most 8 things to **remove or merge** in S1 v3.2 (rules, fields, steps,
code paths) that reduce attack surface or tool calls without weakening a stated
invariant. For each, give the invariant it preserves.

### P-F. ChatGPT's self-audit and the agent organisation (appendix G)

ChatGPT, the operator that runs S1 and the producer tasks, wrote its own audit.
- For each of its 10 ranked improvements, give AGREE, DISAGREE or REORDER with a reason, and name any it missed.
- Then design the best **division of labour and cadence** for:
  - S1 (merge steward, hourly at :45);
  - S2 (weekly Monday report);
  - S4 (daily Alpha outcomes);
  - CRE (daily research);
  - S5 (hourly source watch);
  - Claude (reviewer and fix packages);
  - Codex;
  - Astra/Sol on demand.
- Cover the channels and contracts between them, deduplication, failure domains, and whether S1 is over-centralised.
- Answer the questions in its section 6 that this bundle can support. Mark the others OPEN.
- Give a cadence table (agent, frequency, reason, expected tool/API cost), and keep Monday 09:30-10:30 CPH read-only.

## 3. Output (strict; keep the visible answer under about 30k tokens, and spend the rest on reasoning)

```
ASTRA_REDTEAM_REPORT_v2
mission_id: ASTRA-S1-V32-REDTEAM-20261118-R2
input_sha256: <copy the value the launcher states; do not compute>
provenance: <exact model id and reasoning effort as shown to you>
verdict: SHIP | FIX_FIRST | BLOCK   (SHIP = no P0/P1/P2)
summary: <=6 lines
regression: <one line per id A1..A23 F1..F5 N1 N2 L1 L2: STATUS + path:line>
findings:
- id: R2-<n>
  severity: P0|P1|P2|P3
  confidence: 0.0-1.0
  area: launcher-post|launcher-cost|launcher-trigger|launcher-secret|launcher-output|merge-gate|receipt|liveness|cost|isolation|pins|trust|workflow-sec
  file_line: <path:line[-line]>
  scenario: <numbered concrete steps>
  impact: <what goes wrong, and the worst bounded loss in USD or merges>
  minimal_fix: <smallest change; a unified diff (at most 25 lines) for P0/P1>
  test: <test name + what it asserts; it must fail before the fix>
race_fix: <P-C design: the diff, the tests, the API-call delta>
trust_binding: <P-D options, ranked, with cost and residual risk>
deletions: <P-E list, each with the invariant kept>
chatgpt_audit: <P-F: per-item AGREE/DISAGREE/REORDER, missed items, the organisation design and the cadence table>
rejected_suspicions: <one line each: what you checked and why it is safe>
open_questions: <only what blocks a verdict, naming the missing file>
machine_readable: <one JSON array of {id,severity,confidence,area,file_line,title}>
```

Severity:
- **P0:** an unsafe merge or write, a second paid POST, spend above the reserved bound, a secret leak, or a private-data leak.
- **P1:** a bypassable gate, reliable non-liveness, or a budget breach.
- **P2:** a real but bounded defect.
- **P3:** polish.

## 4. Rules

- Use only the bundle. Anything that depends on unincluded files (ACTION_LOOP, rubrics, AGENTS.md, the scanner, tests) is OPEN, with the missing file named.
- Describe scenarios only. Do not write exploit code against GitHub or OpenAI.
- Never output credentials or private data. If something looks like one, give its path:line only.
