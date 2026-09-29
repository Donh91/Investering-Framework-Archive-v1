# Research Stack + Trader.dev Capability-Gap Audit

**Dato:** 2026-09-29  
**Status:** SHADOW_ONLY  
**Område:** Research Lab / developer-source research / auto-trading research infrastructure  
**Primary folder:** `06_RESEARCH_LAB/audit_summaries/`  
**Related folders:** `research/api_agent/deep_research/`, `07_PROMPTS_AND_AGENTS/`, `04_RESEARCH_LAB/auto_trading/`, `research/pdf_ingestion/`  
**Authority:** NONE_BY_ITSELF  
**Implementation authority:** NONE  
**Portfolio / trading authority:** NONE

## Frozen proposition

The external repositories and Trader.dev surface may contain mechanisms that materially improve the existing Investering research stack, but only if they close a demonstrated gap better than current owners and survive a bounded comparison.

This audit deliberately does NOT adopt a "research stack" wholesale.

## Current local baseline

Fresh repository review shows that the framework already owns most of the generic loop promoted in the supplied X screenshots:

`ask -> decompose -> search multiple paths -> read sources -> extract evidence -> challenge -> cite -> write`

Existing local owners already include:

- `research/api_agent/deep_research/DEEP_RESEARCH_METHOD_v1.md`
  - horizon-aware research queue;
  - provider provenance;
  - explicit hypotheses, falsifiers and kill conditions;
  - cross-horizon conflict preservation;
  - retained-provider gates;
  - Research Lab Red Team before wider use.
- `.agents/skills/research-lab-red-team/SKILL.md`
  - decision divergence;
  - evidence classification;
  - strongest supporting and falsification case;
  - false-positive / false-negative costs;
  - no self-promotion.
- `.agents/skills/developer-source-research/SKILL.md`
  - primary-source preference;
  - source-of-source chasing;
  - license and maintenance qualification;
  - current local code > external index snapshot.
- Existing Firecrawl integration and Developer Index.
- `scripts/document_ingestion/anydoc_ingest.py` pinned to Firecrawl AnyDoc.
- PDF Inspector shadow ingestion with original-source preservation.
- Existing skill-harvest work already extracted:
  - atomic claim/evidence graphs;
  - source independence groups;
  - cheapest decisive falsifier;
  - contradiction-first search;
  - no-progress guards;
  - report factuality/citation evals.
- Mature backtest governance already requires:
  - deterministic replication;
  - independent implementation parity;
  - OOS / walk-forward;
  - realistic costs;
  - lookahead/repaint checks;
  - quarantine on untrusted preliminary outputs.

Therefore popularity, GitHub stars, "deep research", RAG, citations or agentic orchestration are NOT sufficient admission reasons.

## Source set from user screenshots

Reviewed source set:

1. `assafelovic/gpt-researcher`
2. `stanford-oval/storm`
3. `ItzCrazyKns/Perplexica`
4. `langchain-ai/open_deep_research`
5. `bytedance/deer-flow`
6. `mendableai/firecrawl`
7. `unclecode/crawl4ai`
8. `jina-ai/reader`
9. `Future-House/paper-qa` (PaperQA2)
10. `AkariAsai/OpenScholar`
11. `allenai/papermage`
12. `microsoft/graphrag`
13. `HKUDS/LightRAG`
14. `Cinnamon/kotaemon`
15. `docling-project/docling`

Separate surface:
- `https://mcp-api.trader.dev/browse`
- existing owner: `08_SOURCE_MATERIAL/external_methods/2026-09-14__trader-dev-ai-trading-arena__source-note.md`

## High-level disposition matrix

| Source | What is genuinely interesting | Existing overlap | Shadow disposition |
|---|---|---|---|
| GPT Researcher | planner -> execution agents -> publisher; source tracking; broad multi-source parallelism | local deep-research queue already owns decomposition, provider provenance, red team and synthesis | **REFERENCE_ONLY** |
| STORM / Co-STORM | perspective-guided question generation; simulated expert dialogue; evolving mind map | local red team already seeks counterarguments but does not explicitly benchmark perspective coverage | **SHADOW_METHOD_CANDIDATE** |
| Perplexica | self-hosted answer/search UX with cited web search | native web + Firecrawl + research routing already stronger and governance-aware | **REJECT_OVERLAP** |
| Open Deep Research | open agentic deep-research implementation | archived upstream; generic mechanism already locally owned | **REJECT_ARCHIVED_OVERLAP** |
| DeerFlow | long-horizon agent harness, sandboxes, memory, subagents, checkpoints, tracing | Work/Bridge/API-agent stack already owns governed long tasks; local skill harvest already covers no-progress/replay principles | **REFERENCE_ONLY** |
| Firecrawl | crawl/search/extract/developer-index | already installed and integrated; AnyDoc/PDF-related upstreams already pinned | **ALREADY_OWNED** |
| Crawl4AI | self-hosted browser crawler; typed extraction; citation-ready markdown; sessions/proxies; no mandatory SaaS | Firecrawl is current preferred external technical route; gaps occur when quota/index/browser access fail | **SHADOW_FALLBACK_CHALLENGER** |
| Jina Reader | very cheap URL -> markdown/search -> markdown; stateless OSS path; PDF/Office support | overlaps Firecrawl/web/AnyDoc; potentially lighter fallback | **SHADOW_FALLBACK_CHALLENGER** |
| PaperQA2 | scientific-paper RAG with citations; iterative retrieval; metadata-aware reranking; redundant metadata providers; retraction checks; contradiction detection | current literature flow has provenance/red-team, but no equivalent dedicated scientific-paper retrieval/metadata sidecar | **HIGH-VALUE SHADOW_BENCHMARK** |
| OpenScholar | scientific literature synthesis / retrieval-augmented LM | overlaps PaperQA2 with less current code activity | **SECONDARY_REFERENCE** |
| PaperMage | NLP/CV representation of scientific PDFs | overlaps existing PDF Inspector + AnyDoc; older maintenance cadence | **REJECT_UNLESS_PARSING_GAP** |
| GraphRAG | structured graph extraction from unstructured corpora | local claim/evidence graph work is more targeted; Microsoft warns indexing is costly and repo is maintenance-mode | **REJECT_FOR_CURRENT_STACK** |
| LightRAG | lower-cost graph+vector RAG; incremental graph update/purge integrity | still adds another truth/index layer; existing evidence-graph mechanisms are narrower and authority-aware | **REFERENCE_FOR_LIFECYCLE_MECHANICS_ONLY** |
| Kotaemon | hybrid RAG UI, document QA, citations, GraphRAG option | UI / generic RAG not a bottleneck; adds large surface | **REJECT_OVERLAP** |
| Docling | strong multi-format local parsing, advanced tables/layout/formulas/charts, XBRL, local/air-gapped execution, MCP | overlaps AnyDoc/PDF Inspector, but has potentially stronger complex-document and financial-report parsing | **HIGH-VALUE SHADOW_BENCHMARK** |

## Detailed findings

### 1. GPT Researcher — impressive, but mostly already owned

Inspected current revision:
`0957c301ed06c2a5857b834358c7227c739041d4`
License observed: Apache-2.0.

Useful mechanism:
- explicit planner / execution / publisher separation;
- parallel research questions;
- per-resource source tracking.

Why not implement:
- the Investering stack already has a deeper authority model, retained-provider gates, horizon conflict, falsifiers and Red Team;
- importing another orchestration runtime would create duplicate planning and synthesis ownership;
- existing analytical skill harvest already extracted more precise claim-level mechanisms than this broad framework provides.

Verdict:
`REFERENCE_ONLY`.

### 2. STORM / Co-STORM — one method worth testing

Inspected revision:
`fb951af7744dab086e34962e9bc6fe878e145f83`
License observed: MIT.

Potentially incremental mechanism:
- **Perspective-Guided Question Asking** before deep research;
- discover materially different viewpoints first, then let them drive questions;
- Co-STORM's mind-map style representation can expose missing conceptual branches.

Local gap:
Research Lab has strongest-for/against and contradiction work, but it does not currently prove that the initial question set covered materially distinct perspectives.

Risk:
This can easily become "more agents = deeper research" theater and increase token cost without changing evidence.

Required benchmark:
Take a frozen set of prior research missions and compare:
- baseline local decomposition;
- baseline + perspective-guided question seeding.

Measure:
- new independent evidence roots found;
- material contradictions discovered;
- decision-changing findings;
- source duplication;
- token/tool cost;
- time to decisive falsifier.

No implementation until this benchmark wins.

Verdict:
`SHADOW_METHOD_CANDIDATE`.

### 3. Perplexica — no demonstrated gap

Useful as a self-hosted web answer/search product.

No identified incremental mechanism over:
- native web;
- Firecrawl;
- developer-source research;
- existing evidence/citation controls.

Verdict:
`REJECT_OVERLAP`.

### 4. LangChain Open Deep Research — archived and redundant

Repository is archived.
License observed: MIT.

Even before archival, its broad deep-research loop overlaps current local functionality.

Verdict:
`REJECT_ARCHIVED_OVERLAP`.

### 5. DeerFlow — architecture reference, not local runtime

Inspected revision:
`8a3a309d1ce8bac8418251be29d4e4297a20c5eb`
License observed: MIT.

Current DeerFlow is a broader long-horizon agent harness with:
- sandbox;
- skills/tools;
- subagents;
- long-term memory;
- context compaction;
- scheduled tasks;
- tracing and replay-oriented developer tooling.

Potential learning:
Failure replay / harness-step inspection is useful as an engineering benchmark.

Why no adoption:
- Work/Bridge/API-agent + GitHub already provide long-horizon execution surfaces;
- creating DeerFlow as another scheduler/memory/orchestrator would violate the no-parallel-stack direction;
- its value is engineering reference, not research evidence.

Verdict:
`REFERENCE_ONLY`.

### 6. Firecrawl — already in the aircraft

No new stack decision.
The framework already:
- uses Firecrawl Developer Index;
- has a developer-source-research skill built around it;
- has Firecrawl AnyDoc and PDF Inspector-related ingestion work;
- explicitly falls back to GitHub/web when Firecrawl is unavailable or inconclusive.

Verdict:
`ALREADY_OWNED`.

### 7. Crawl4AI — potentially useful only as a concrete fallback challenger

Inspected revision:
`e5d2e786d1a101225f3f6a3e6fd344d76eeb13af`
License observed: Apache-2.0.

Real incremental candidate:
A self-hosted crawler path that does not require Firecrawl quota and exposes:
- JS browser control;
- deterministic CSS/XPath/regex extraction;
- typed JSON extraction;
- sessions;
- citation-ready markdown;
- local execution.

Why this is NOT an integration recommendation:
The framework already has the rule:

`OFFICIAL/API -> deterministic HTTP/source adapter -> adaptive scraper -> browser only when needed`.

A generic second crawler adds maintenance, security and anti-bot burden.

Correct test:
Use only on a frozen set of sources where the current preferred route actually failed or degraded.
Compare:
- retrieval success;
- semantic fidelity;
- timestamps/provenance;
- tables/code preservation;
- deterministic replay;
- runtime/cost;
- anti-bot/ToS risk;
- operational burden.

Promotion condition:
Crawl4AI materially improves a recurring, documented source gap.

Kill:
If value is only "also crawls websites".

Verdict:
`SHADOW_FALLBACK_CHALLENGER`.

### 8. Jina Reader — same fallback thesis, lighter surface

Current repo license observed: Apache-2.0.

Interesting:
- URL -> LLM-ready markdown;
- search -> markdown;
- current OSS branch is stateless by default;
- PDFs and MS Office uploads are supported;
- can run locally / bucket-cached.

Potential niche:
A cheap/simple first-pass extractor when browser-grade Firecrawl is unnecessary.

But:
- it relies on external SERP providers for search;
- it overlaps web/Firecrawl/AnyDoc substantially;
- adding it alongside Crawl4AI and Firecrawl would be stack proliferation.

Decision:
Do NOT test both Crawl4AI and Jina as generic new tools.
If an actual gap appears, choose the cheapest challenger that fits that exact gap.

Verdict:
`SHADOW_FALLBACK_CHALLENGER`.

### 9. PaperQA2 — strongest research candidate from this list

Inspected revision:
`57e89f7223b0960d5ee5ea048c69e3c47e088572`
License observed: Apache-2.0.

Potentially incremental capabilities:
- scientific-document RAG specifically optimized for literature;
- in-text citations grounded to page ranges;
- iterative agentic query refinement;
- document metadata-aware embeddings/reranking;
- redundant paper metadata fetching;
- citation/journal-quality metadata;
- retraction checking;
- contradiction detection;
- reusable local scientific corpus/index.

This is NOT another generic Deep Research agent.
The potentially valuable role is a **scientific evidence sidecar / benchmark** underneath the existing Research Lab owner.

Concrete local gap:
Current literature research is strong on governance and falsification, while the repository has only limited explicit scientific-paper metadata/retraction machinery.

Shadow benchmark proposal:
Compare current literature workflow vs PaperQA2-assisted retrieval on a frozen set of 20-40 research questions/papers.

Primary endpoints:
- correct claim-to-page citations;
- relevant-source recall;
- contradiction discovery;
- retracted/corrected-paper detection;
- false citations;
- unsupported factual claims;
- total model/tool cost;
- whether Research Lab verdict changes correctly.

Hard boundary:
PaperQA2 never becomes evidence authority; original papers remain primary.

Verdict:
`HIGH_VALUE_SHADOW_BENCHMARK`.

### 10. OpenScholar — useful science reference, but do not run two science RAG challengers

License observed: Apache-2.0.
Repository remains available but latest push observed in 2025.

It addresses scientific literature synthesis, but PaperQA2 is currently a cleaner first challenger because:
- more current development;
- stronger explicit metadata/retraction workflow in inspected materials;
- broader document/index interface.

Keep OpenScholar only as a comparison reference if PaperQA2 benchmark exposes a gap.

Verdict:
`SECONDARY_REFERENCE`.

### 11. PaperMage — parsing library, not a missing research brain

License observed: Apache-2.0.
Focus: NLP/CV representations of scientific papers.

Potential value exists only if current PDF/AnyDoc parsing fails on a demonstrated scientific-paper structure.

No generic integration case.

Verdict:
`REJECT_UNLESS_PARSING_GAP`.

### 12. Microsoft GraphRAG — reject current integration

License observed: MIT.
Microsoft currently describes the project as research / largely maintenance-mode and warns that indexing can be expensive.

Why not:
- creates another derived graph/index that can be mistaken for evidence truth;
- local evidence-graph work is claim-specific and much easier to govern;
- corpus size / query type has not demonstrated a need for costly global graph indexing.

The name "GraphRAG" should not be confused with Alpha Lab's onchain economic graphs. They solve different problems.

Verdict:
`REJECT_FOR_CURRENT_STACK`.

### 13. LightRAG — interesting lifecycle mechanics, but not another truth layer

Inspected revision:
`453dce83d6d0354a06e46c8d4029a0895c4e054b`
License observed: MIT.

Interesting engineering:
- graph + vector two-layer retrieval;
- lower-cost incremental updates;
- explicit purge/recovery/integrity logic.

The purge-recovery discipline is more interesting than the RAG itself:
authoritative tracking rows, careful ordering, stale-attribution repair, explicit integrity audit.

Possible conceptual learning:
versioned derived-index attribution and purge ordering.

But implementing LightRAG would introduce another graph database / truth representation with unclear decision value.

Verdict:
`REFERENCE_FOR_LIFECYCLE_MECHANICS_ONLY`.

### 14. Kotaemon — polished RAG UI, not a framework gap

License observed: Apache-2.0.

Capabilities:
- document QA;
- hybrid retrieval;
- citations/PDF previews;
- multimodal parsing;
- GraphRAG option;
- question decomposition.

No current bottleneck is "we lack a document-chat UI".

Verdict:
`REJECT_OVERLAP`.

### 15. Docling — second strongest research candidate

Inspected revision:
`2b2fb851624f34df881cd90d744f8da2c4f8e37a`
License observed: MIT.

Potentially incremental capabilities:
- advanced PDF reading order;
- tables;
- formulas;
- code;
- image classification;
- chart -> table/code/description;
- XLSX/PPTX/DOCX;
- XBRL financial reports;
- local/air-gapped processing;
- structured lossless JSON representation;
- MCP / service mode.

Particularly relevant detail from latest inspected commit:
Docling changed failed remote VLM calls from silent/empty apparent success into explicit `INFERENCE_ERROR`, and propagates failure / partial-success semantics instead of returning empty success.

That failure-honesty philosophy is strongly aligned with framework UNKNOWN/DEGRADED semantics.

Local overlap:
- Firecrawl AnyDoc already normalizes multiple document types;
- PDF Inspector is already the specialist PDF route.

Therefore the question is NOT "is Docling better?"
It is:
Does Docling correctly recover materially more information from difficult financial/research documents than the existing pipeline?

Frozen benchmark candidate:
Use a small corpus of difficult existing research artifacts:
- table-heavy reports;
- charts/figures;
- scanned or layout-complex PDFs;
- XLSX/XBRL where relevant.

Compare:
- table cell accuracy;
- reading-order preservation;
- figure/chart extraction;
- source-page traceability;
- failure honesty;
- runtime;
- output size;
- local/offline privacy;
- dependency burden.

Verdict:
`HIGH_VALUE_SHADOW_BENCHMARK`.

## Trader.dev delta review

Existing canonical source note already correctly classifies Trader.dev as research-only and explicitly rejects leaderboard returns as alpha evidence.

Fresh observations from the current public surface:

- public browse is ranked by backtest performance;
- the visible leaderboard contains extremely large headline returns, including ~19,000% examples;
- this strengthens, not weakens, the existing selection/multiple-testing caution;
- the service exposes a Strategy Inspector with walk-forward / OOS framing;
- at least some backtests are automatically quarantined when re-runs look unreal or diverge from legacy results ("parity delta");
- Martingale-style strategies are intentionally excluded from public browse;
- an inspected public report includes commissions explicitly;
- the platform offers paper/live exchange connection through MCP, but this creates an execution/credential surface outside current authority.

Most of the useful governance ideas are ALREADY owned locally:
- OOS;
- walk-forward;
- costs/slippage;
- parity;
- quarantine;
- lookahead/repaint rejection;
- independent replication.

Incremental delta worth preserving:
**automatic public-result quarantine on parity drift** is a useful UX/operational benchmark:
if a previously visible result fails an engine/version rerun, remove it from promotable/public surfaces until investigated.

This principle fits the current backtest architecture but does not yet justify Trader.dev dependency.

No strategy from the public leaderboard is accepted as alpha evidence.

Verdict:
`EXISTING_OWNER_CONFIRMED / NO_NEW_IMPLEMENTATION`.

## What deserves further research?

Only three bounded lines currently survive:

### R1 — PaperQA2 scientific-evidence benchmark
Priority: HIGH.

Question:
Can PaperQA2 improve claim-to-source accuracy, contradiction discovery and retraction/correction handling versus current literature workflow without becoming another authority layer?

Owner:
existing Research Intake / Research Lab / skill-quality eval owners.

State:
`SHADOW_BENCHMARK_CANDIDATE`.

### R2 — Docling difficult-document benchmark
Priority: MEDIUM-HIGH.

Question:
Does Docling materially outperform current AnyDoc + PDF Inspector on actual difficult framework documents?

Owner:
existing document-ingestion owner.

State:
`SHADOW_BENCHMARK_CANDIDATE`.

### R3 — one fallback crawler benchmark, only after a real retrieval failure
Priority: CONDITIONAL.

Candidates:
Crawl4AI OR Jina Reader, not both initially.

Question:
Can a fallback recover a documented recurring source gap more reliably/cheaply than current fallback routes?

Owner:
developer-source-research / source-specific owner.

State:
`BLOCKED_UNTIL_CONCRETE_GAP`.

## What does NOT deserve implementation now?

Do not create:
- a new Deep Research orchestrator;
- a new RAG truth store;
- a GraphRAG/LightRAG production corpus;
- a DeerFlow runtime;
- a Perplexica research UI;
- a Kotaemon document UI;
- a generic second crawler;
- a Trader.dev live execution connection;
- a new scientific-research owner.

## Promotion / implementation route

This shadow artifact has zero implementation authority.

If R1 or R2 wins a bounded benchmark, the next step is NOT direct code.

Correct route:

`shadow finding`
-> verify existing owner / deduplicate
-> freeze benchmark result
-> Research Lab Red Team
-> if code is actually needed, create `CODEX_RESEARCH_CANDIDATE_v1` on isolated branch
-> merge candidate under `research/codex/intake/YYYY/MM/`
-> Remediation Maturation Controller
-> `CODEX_READY | NEEDS_MORE_EVIDENCE | REJECTED | DEDUPED`
-> bounded PR
-> CI / review
-> merge
-> post-merge verification receipt

For a pure research experiment that needs no code change, use the existing Research Lab / skill-quality forward-test owner rather than Codex.

## Final Research Lab verdict

### Frozen proposition result

"Import the X-post's research stack" -> **REJECT**.

"Mine the stack for incremental mechanisms" -> **YES, but most are already owned**.

### Highest incremental value

1. **PaperQA2** — scientific evidence/retraction/contradiction benchmark.
2. **Docling** — difficult-document extraction benchmark.
3. **STORM perspective-guided question generation** — small method challenger if research breadth remains a proven gap.
4. **Crawl4AI/Jina** — only as source-specific fallback after demonstrated failures.
5. **Trader.dev parity-quarantine UX** — preserve as a benchmark principle; existing backtest governance already owns the substance.

### Confidence

High on no-stack-import / overlap conclusion.
Medium-high on PaperQA2 and Docling benchmark value.
Medium on STORM method value.
Low value for generic GraphRAG/agent-runtime adoption under current architecture.

## Required next row

No implementation row yet.

The next legitimate row is a **frozen benchmark design** for R1 or R2, only if owner capacity permits and after dedupe against current skill-quality/document-ingestion experiments.

Until then:
`KEEP_BASELINE`.
