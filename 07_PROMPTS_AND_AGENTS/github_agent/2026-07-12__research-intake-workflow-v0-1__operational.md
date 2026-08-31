# Research Intake Workflow v0.1

**Dato:** 2026-07-12  
**Status:** OPERATIONAL  
**Område:** external research triage / X posts / architecture learning  
**Primary folder:** `07_PROMPTS_AND_AGENTS/github_agent/`  
**Depends on:** Agent Control Loop v0.1, Canonical Context Router, Research Lab Red Team, Archive Governance

## Purpose

Convert external posts, threads, papers and practitioner claims into decision-useful research without letting novelty bypass existing framework governance.

## Input

```yaml
source_urls:
source_text_or_extract:
source_type:
user_question:
requested_action:
write_intent:
```

## Mandatory workflow

1. Resolve current authority with `canonical-context-router`.
2. Separate the source claim from the source's marketing or confidence.
3. Identify whether the idea already exists in the repository.
4. Classify the source.
5. Map useful ideas to an existing owner or a repeated workflow gap.
6. Run `research-lab-red-team` for claims about framework improvement.
7. Propose the smallest test or operational change.
8. Use `archive-governance` only when the user explicitly requests a write.

## Optional research-data sidecars

For CoinGecko or GeckoTerminal research, an agent may opt in to the bounded CoinGecko MCP Research / Recovery Sidecar defined at:

```text
07_PROMPTS_AND_AGENTS/github_agent/2026-08-11__coingecko-mcp-research-recovery-sidecar-v1__operational.md
research/api_agent/mcp/COINGECKO_MCP_RESEARCH_RECOVERY_v1.json
```

This sidecar is a research access path only. It does not change this workflow's governance order and cannot become a canonical collector, DATA PING owner, weekly input owner, market-state authority or portfolio-action source. MCP failure or rate limiting degrades the research lane only.

When the sidecar is used, preserve the method/query provenance required by its contract and classify the result as source context until the existing owner and governance path accept it.

### Sequential MCP connection evaluation program

The user-approved provider set Dune, LunarCrush, CoinMarketCap, The Graph, altFINS and Binance Agent Native is governed by:

```text
07_PROMPTS_AND_AGENTS/github_agent/2026-08-11__mcp-connection-evaluation-program-v1__operational.md
research/api_agent/mcp/MCP_CONNECTION_EVALUATION_PROGRAM_v1.json
research/api_agent/mcp/MCP_CONNECTION_EVALUATION_METHOD_v1.md
```

CoinGecko is the bounded baseline. The remaining providers are tested one at a time. A provider may be retained only inside its predeclared research/crosscheck/shadow/candidate-discovery/diagnostics ceiling after deterministic boundary checks, live read-only evidence when available, redundancy review and Research Lab Red Team review.

No MCP connection may become a new engine, canonical owner, DATA PING owner, Master Monday owner, Cycle Navigator authority, market-rule source or portfolio-action source through this workflow.

External dependency blocks such as missing provider credentials or an unverified official endpoint remain explicit and advance the queue rather than causing unofficial workarounds or blocking unrelated framework operation.

### Deep Research Horizon Queue

Retained provider connections are consumed by the bounded operational queue at:

```text
research/api_agent/deep_research/DEEP_RESEARCH_QUEUE_v1.json
research/api_agent/deep_research/LATEST_DEEP_RESEARCH_STATE.json
research/api_agent/deep_research/NEXT_DEEP_RESEARCH_TASK.json
research/api_agent/deep_research/DEEP_RESEARCH_METHOD_v1.md
```

The queue studies market direction and cycle transitions separately at `1_3D`, `5_7D`, `2_3W` and `CROSS_HORIZON`, with priority on pre-altseason accumulation context, real-versus-fake rotation, distribution precursors and provider incremental value.

Only providers already retained by the MCP connection scorecard may be used. A provider still in discovery, queued, held, killed, blocked or data-blocked cannot enter a deep-research task. Provider ceilings remain binding.

This queue is explicitly `RESEARCH_QUESTION_NOT_FORWARD_TEST`. It does not replace the canonical Open Questions Register or Active Test Registry, cannot create valid outcome rows and cannot add a new active test. When a research item relates to an existing question or test, it routes evidence to that existing owner. Any finding that would require a new test or a change to market rules, thresholds, weights, policy semantics, sensors or portfolio behavior remains a separate governance proposal.

At most one deep-research item is active. Provider dependency blocks may be skipped temporarily so unrelated research can continue. Every item requires a baseline, hypothesis, decision divergence, falsifier, kill condition, provider provenance and Research Lab Red Team review before any integration proposal.

## Classification

Use exactly one primary class:

```text
SOURCE_EVIDENCE
PRACTITIONER_ANECDOTE
ARCHITECTURE_INSPIRATION
MARKETING_OR_UNVERIFIED
DUPLICATE_OF_EXISTING_OWNER
REPEATED_GAP_CANDIDATE
NOT_RELEVANT
```

## Required output

```markdown
## RESEARCH INTAKE

Source:
Primary classification:
Confidence in source:
Core claim:
What is genuinely useful:
What is hype or unsupported:
Current framework overlap:
Existing owner:
Repeated gap demonstrated:
Recommended action:
Recommended test:
Verifier:
Stop condition:
Archive decision:
Authority boundary:
```

## Decision rules

- A useful post is not evidence of trading edge.
- A recurring workflow failure may justify infrastructure before a new Skill.
- One post cannot authorize a new engine, score, threshold or portfolio rule.
- Practitioner cost or token anecdotes remain anecdotes unless independently measured.
- Prefer deterministic verification, state and receipts over a larger prompt.
- Prefer a narrow pilot with a kill criterion over a permanent architecture change.
- Reject duplicate memory systems when GitHub already owns durable state.
- Research may recommend an experiment. It may not self-ratify the result.

## Write rule

When explicit write intent exists, archive only the durable synthesis or test contract.

Do not archive every post or every intermediate analysis.

## Friday literature brief and research follow-up

**Added:** 2026-08-30
**Status:** OPERATIONAL_RESEARCH_ONLY
**Execution:** user-authorized scheduled ChatGPT Work task, Friday afternoon, Europe/Copenhagen
**Archive:** `06_RESEARCH_LAB/audit_summaries/friday_research/README.md`

This is a bounded recurring use of this existing intake workflow. It adds no
engine, market-data provider, active test, score, model weight or canonical
market authority. It does not activate or advance the Deep Research Horizon
Queue, bypass its retained-provider requirements, or reopen Round 3 analysis.
Public literature discovery through web search or Firecrawl is not permission
to use an unretained market-data MCP provider. No new paid data, subscriptions,
API-budget increases or background collectors are authorized by this task.

### Selection and evidence review

1. Pin current main and resolve the mandatory cockpit, governance and relevant
   owner files. Read the last merged Friday packet, its open follow-ups and any
   pending Friday archive PR before searching. Reuse existing evidence rather
   than collecting market snapshots already owned elsewhere.
2. Search for original reports, papers and substantive analysis first published
   or materially revised since the preceding search cutoff, normally seven
   days. Record publication date, revision date, retrieval time and the actual
   data period separately. An old paper newly discovered is not a new paper.
3. Cover liquidity and monetary transmission, BTC/ETH leadership and rotation,
   cycle/participation evidence, and cross-asset signals. Include deliberate
   searches for contrary findings, null results and failed replications. Do not
   force an item from every category when quality is insufficient.
4. Use Firecrawl Research Index for paper discovery when available; its coverage
   is incomplete for economics and finance. Also search original institutional,
   author and publisher pages. Search snippets, abstracts and model-generated
   summaries are discovery aids, not proof of a full-text claim. Verify any
   load-bearing claim against the accessible original text. Record FULL_TEXT,
   ABSTRACT_ONLY or UNAVAILABLE. Do not bypass paywalls or infer unseen results.
5. Select at most five useful sources, normally three to five. Zero is valid.
   Deduplicate canonical URL/DOI, versions, syndicated reports, common datasets
   and claim families. A material revision must reference the previous item and
   explain the changed evidence. Never present duplicate studies as independent
   confirmation. Reuse existing claim IDs for unchanged claims.
6. Distinguish ROBUST_EMPIRICAL, PRELIMINARY_EMPIRICAL and NARRATIVE_OR_MECHANISM
   as descriptive literature assessments, not numerical scores or forward-test
   statuses. Author-reported results are not independent replication. Consider
   sample size and effective independence, market regimes, data revisions and
   publication lags, out-of-sample validation, multiple testing, endogenous
   signals, causality versus correlation, and practical false-positive and
   false-negative costs. Abstract-only findings cannot earn ROBUST_EMPIRICAL.
7. For each item identify the exact current owner/question/test it supports or
   challenges, its incremental information, strongest counterargument and what
   observation would change the interpretation. Use NO_EXISTING_OWNER when
   appropriate rather than inventing a test. Existing intake classifications
   and Research Lab verdicts remain authoritative.

### Durable packet and continuity

Archive one compact UTF-8 JSON synthesis per ISO week under
`06_RESEARCH_LAB/audit_summaries/friday_research/<ISO-year>-W<week>.json`.
This packet is an operational literature report, NOT_A_LEDGER_ROW. No empty
weekly packet is created before a real run. The archive README is navigation,
not a second research owner or a market-state pointer.

The packet must contain:

```text
packet_type: FRIDAY_RESEARCH_BRIEF
authority: RESEARCH_CONTEXT_ONLY
row_type: NOT_A_LEDGER_ROW
iso_week
generated_at_utc / search_cutoff_utc / search_window_start_utc
canonical_commit_sha
previous_packet: immutable commit, path and sha256, or null on first run
coverage: searched themes, query/source routes, inaccessible sources, gaps
items: zero to five literature items
followups: carried-forward unresolved items and this run's review events
selection_review: sourcing lessons only, or NOT_DUE
master_monday_handoff: at most three source-context findings and owner paths
limitations
```

Each item preserves a stable claim ID, title, canonical source URL/DOI and
version, dates, access level, original claim in an attributed paraphrase,
evidence assessment with rationale, source-data limitations, existing owner
path and optional registered test ID, overlap, incremental value, strongest
counterargument, recommended action and Research Lab verdict. Preserve a hash
of the actual retrieved source representation when available, clearly named
as such; never invent a raw-source hash or confuse it with the packet hash.

Archive original synthesis and links, not entire copyrighted articles, private
provider payloads, holdings, quantities, credentials or conversation text.
Paid material may be referenced by authorized source identity and public-safe
synthesis only; follow existing source permissions and data boundaries.

Once merged, preserve a packet's bytes. Corrections and changed interpretations
belong in a later packet with an explicit supersedes/reference relationship.
Same-week identical re-runs are DUPLICATE_NOOP. A necessary same-week correction
uses an explicitly linked revision file, never overwrites the original.
Before delivery, check duplicate claim IDs, real dates, JSON validity, existing
owner paths, prior-packet hashes, unresolved follow-up continuity and that no
source report has been presented as a scored outcome.

### Follow-up and improvement

Track at most five open literature follow-ups and nominate at most one new
bounded test proposal per run. If capacity is full, close, merge or explicitly
defer a literature follow-up before adding another; never silently drop it.
This capacity limit does not retire or change an existing canonical test.

For a proposed test, preserve the hypothesis, existing baseline/owner,
decision divergence, falsifier, kill condition, observation horizon and next
review date before its outcome is known. This remains a proposal until the
existing owner accepts it under the Active Test Registry and its contract.
The Friday task does not create forecast rows, run new backtests or score
outcomes. It reads and links valid owner-produced evaluation artifacts only.

On each run, carry unresolved follow-ups forward with their original claim ID,
original packet reference, due date, latest owner receipt and next action.
Review due items first. Preserve PENDING_MATURITY, DATA_BLOCKED,
OWNER_ACCEPTANCE_PENDING and EVALUATION_UNAVAILABLE where applicable. An elapsed
review date is not an elapsed forecast horizon or a failed hypothesis. Formal
test status is copied from the current owner, never invented by this task.

Two-, four- and eight-week dates may organize literature review but never
replace owner-defined outcome horizons. Any reported performance must bind to
the exact frozen owner specification, matched baseline and verified evaluation
receipt. Never count a paper, initialization, duplicated event or commentary as
an independent observation; never reconstruct a forecast retrospectively.

Every fourth completed Friday run, review sourcing utility: novelty versus
duplication, useful owner-linked contributions, evidence access and outstanding
follow-ups. Where authorized owner evaluations exist, report incremental value
and limitations separately by horizon and regime. Otherwise say INSUFFICIENT
EVIDENCE. Adjust search emphasis based on documented research utility, while
retaining contrary-evidence searches. Do not tune live thresholds, weights,
portfolio rules or an author's trading authority. A poor hypothesis can still
be a useful source if it exposes a reproducible failure mode.

### Archive execution and delivery

Use an explicit verified non-default `agent/task-*` branch and one bounded
artifact-only PR for the packet. Review the diff, references, JSON and source
claims; run applicable repository checks. Merge only when current governance
permits it and required validation/review is complete. Never auto-merge a Codex
change, alter checks or route literature as a CODEX_READY defect.

After merge, read the exact remote bytes back and verify their SHA-256 at the
merge commit. Report PERSISTED_VERIFIED only after that succeeds. Otherwise
name PR_PENDING, NOT_PERSISTED or READBACK_FAILED and retain the concrete PR
or failure reference. The next run reconciles pending PRs before duplicating
work. Archive failure does not erase a source-backed user brief, and delivery
does not prove persistence.

Deliver a concise Danish brief, normally no more than 500 words, with a ranked
shortlist, evidence versus narrative, implications for the current framework,
one short 'Hvad lærte vi?' follow-up, and the verified archive/PR link. If no
source meets the bar, say so without padding. No fresh market call, portfolio
instruction, confident top date or promise of predictive improvement.

Master Monday may consume the packet's compact handoff as attributed research
context only. Linkage or archive presence does not prove that a Director has
consumed it; a downstream-consumption claim requires the actual consumer output
or receipt. Do not change its frozen market inputs or official scoring.
