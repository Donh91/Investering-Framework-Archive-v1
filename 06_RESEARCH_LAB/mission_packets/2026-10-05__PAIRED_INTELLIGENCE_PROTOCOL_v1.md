# Research Lab Paired Intelligence Protocol v1

**Date:** 2026-10-05
**Status:** ACTIVE_SHADOW_RESEARCH_PROTOCOL
**Authority:** NONE_BY_ITSELF
**Scope:** High-Intelligence Research Lab missions M1-M5
**Codex:** FORBIDDEN_FOR_THIS_SEQUENCE unless owner later changes mandate
**Canonical framework snapshot at queue creation:** `Donh91/Investering-Framework-Archive-v1@89b6c41528ded2be670559cc87c14e85b8849d7c`
**Bridge snapshot at queue creation:** `Donh91/Investering-AI-Audit-Bridge@caf4e5873b8f4ec801c7478387a540c044cc671b`

## Objective

Use ChatGPT 5.6 Sol High, GPT-6.1 Sol API and Claude Code as complementary research roles without duplicate work, consensus bias or authority leakage.

## Roles

### ChatGPT 5.6 Sol High
Primary Research Lab owner, broker and final adjudicator.

Responsibilities:
- freeze the research question and evidence boundary;
- perform fresh deterministic readback and in-chat analysis;
- keep one mission active at a time;
- review Claude and GPT-6.1 Sol outputs independently;
- exchange only adjudicated deltas between the two external arms;
- decide whether a cross-examination pass is warranted;
- issue the final Research Lab verdict and minimum next action.

### Claude Code through Investering AI Audit Bridge
Independent code/provenance/adversarial arm.

Best used for:
- broad repository reading;
- code-path, lineage and ownership reconstruction;
- leakage, hindsight, duplication and architecture review;
- deterministic reproduction and test design;
- external second opinion where the internal Sol lane is not fully comfortable.

Hard boundary:
- framework repositories remain read-only;
- Claude writes only to the Bridge;
- Claude is not an implementation substitute for Codex.

### GPT-6.1 Sol API
Senior scientific/economic reasoning arm.

Best used for:
- difficult research synthesis;
- conflicting evidence;
- statistical and economic interpretation;
- counterfactual decision analysis;
- scientific falsification;
- opportunity-cost and baseline comparison.

Hard boundary:
- advisory/research only;
- no repository-write, merge, canonical, threshold, market-state, portfolio or trading authority.

## Four-phase exchange

### Phase A — Independent blind pass

Claude and GPT-6.1 Sol receive the same frozen core question but different role-specific tasks.

They MUST NOT be asked to imitate or agree with the other model.

Purpose: preserve independent error structure.

### Phase B — ChatGPT broker adjudication

ChatGPT reads both outputs and classifies claims:

`VERIFIED | SUPPORTED | CONFLICTED | REJECTED | UNKNOWN`

Only evidence-bearing deltas are forwarded.

Raw model prose is not authority and is not automatically cross-fed.

### Phase C — Bounded cross-examination

Run only when one of these holds:
- Claude identifies a code/provenance fact that materially undermines the Sol conclusion;
- Sol identifies an economic/statistical conclusion that depends on an assumption Claude can test in code/history;
- material disagreement remains after deterministic readback;
- a P0/P1 integrity risk remains unresolved.

Cross-examination must cite exact counterpart artifact/output refs and answer a bounded disagreement, not rerun the whole mission.

### Phase D — Final Research Lab adjudication

ChatGPT issues:
- claims falsified;
- claims surviving;
- remaining unknowns;
- decision-value assessment;
- complexity or defensiveness finding;
- what is refused promotion;
- minimum next action.

No research output self-promotes.

## Sequential execution

One mission active at a time:

`M1 -> M2 -> M3 -> M4 -> M5`

A successor is released only after the predecessor has a final ChatGPT Research Lab adjudication or an explicit owner override.

Queueing is allowed. Execution fan-out across missions is not.

## Communication path

`Claude Bridge report -> ChatGPT adjudicated delta -> GPT-6.1 Sol mission context`

`GPT-6.1 Sol output -> ChatGPT adjudicated delta -> Bridge message/review -> Claude bounded challenge`

This is intentional mediation, not direct ungoverned model-to-model authority transfer.

## Stop rule

If either arm adds no material information beyond deterministic evidence and ChatGPT analysis, close the extra arm as CLEAN_NOOP and do not spend more compute.
