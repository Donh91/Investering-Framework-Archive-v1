# Shadow Idea Admission Rule v1

Status: ACTIVE RESEARCH GOVERNANCE
Scope: all new ideas proposed for the framework, including external agents, skills, repositories, tools, sensors, data sources, indicators, models, automations, controllers and architectural patterns.

## Prime directive

> Observe -> accumulate evidence -> validate -> learn -> adjust only when the evidence warrants it.

The framework optimizes for better decisions and earlier robust regime/rotation warnings, not for feature count. A new component must earn complexity.

## Default state

Every new idea starts as `SHADOW_CANDIDATE`, never as canonical framework logic.

Discovery, novelty, popularity, a persuasive benchmark, an external author's claim, or an LLM recommendation is not sufficient evidence for implementation into decision logic.

## Admission sequence

1. **Problem first** - state the concrete framework weakness, missing capability or measurable failure the idea is intended to solve. If no real problem exists, archive the idea.
2. **Existing-capability check** - determine whether current sensors, agents, skills or code already solve the problem. Prefer reuse, simplification or replacement over additive duplication.
3. **Shadow isolation** - evaluate the candidate without changing canonical thresholds, weights, market semantics, portfolio semantics, prospective floors or outcome labels.
4. **Evidence plan before results** - define success, failure, baseline, incremental-value test, costs, failure modes and rollback criteria before observing outcome-linked results.
5. **Accumulate sufficient evidence** - use prospective evidence where causal or predictive claims are involved. Historical evidence may generate hypotheses, but hindsight-fit evidence alone cannot promote a candidate.
6. **Incremental-value test** - compare against the existing framework or simplest relevant baseline. The candidate must add information, reliability, coverage, resilience or operational efficiency that is not already available.
7. **Complexity tax** - explicitly account for maintenance, dependencies, tokens/API spend, latency, source fragility, security/privacy, governance burden, correlated failure modes and agent coordination cost.
8. **Adversarial validation** - test leakage, redundancy, stale data, unavailable dependencies, provider changes, malformed outputs, contradictory signals and fail-closed behavior where relevant.
9. **Promotion decision** - only evidence-backed candidates may move from shadow to production/canonical use through the appropriate reviewed change path.
10. **Post-promotion monitoring** - promotion is reversible. If incremental value disappears or complexity exceeds benefit, downgrade, disable or remove the component.

## Required decision question

Before promotion, reviewers and agents must answer:

`Does this candidate make the framework measurably better after accounting for the complexity it adds?`

If the answer is unknown, the candidate remains shadow. If the answer is no, reject or archive it.

## Anti-overfit rules

- Never create or retune a threshold because it explains a recently observed market episode.
- Never promote a new sensor solely because it correlates with known historical tops, bottoms, rotations or altseasons.
- Never use the same observations both to invent and confirm a rule without an independent validation stage.
- Never let an agent, skill or model silently rewrite canonical decision semantics from its own research output.
- Prefer fewer independent signals over many correlated variants of the same information.
- Negative and null results are valid learning and must not be hidden by replacing the failed candidate with a slightly modified version until something passes.

## External agents, skills and repositories

Online discoveries are inputs to research, not trusted extensions of the framework. Before adoption, additionally assess:

- exact capability gained versus current stack,
- permissions and security surface,
- external code/dependency and supply-chain risk,
- data egress/privacy implications,
- maintenance activity and failure behavior,
- model/tool lock-in,
- whether the same benefit can be achieved more simply in-house.

A useful external component may be sandboxed or used as a research instrument before it is eligible to become persistent infrastructure.

## Promotion classes

- `ARCHIVE_ONLY` - interesting but no actionable incremental value.
- `SHADOW_CANDIDATE` - plausible idea awaiting structured evaluation.
- `SHADOW_TESTING` - isolated test with preregistered acceptance criteria.
- `FORWARD_TEST` - prospective validation required before decision influence.
- `OPERATIONAL_HELPER` - proven workflow benefit but no authority over market/portfolio semantics.
- `CANONICAL_CANDIDATE` - evidence supports reviewed integration.
- `CANONICAL` - approved and governed production component.
- `RETIRED` - previously useful but no longer justifies its complexity.

## Simplicity preference

When two approaches deliver comparable evidence-backed value, choose the simpler one.

A component that merely makes the framework larger has failed admission. A component that lets the framework become simpler while preserving or improving performance deserves extra weight.

## Protected objectives

No candidate may redefine the framework's protected objectives through this process. Research should improve the machinery serving those objectives, not move the goalposts.
