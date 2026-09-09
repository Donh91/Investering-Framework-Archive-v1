# Anthropic Economic Scenarios v1 — Research Lab source note

**Recorded:** 2026-09-09  
**Status:** EXTERNAL_SCENARIO_PRIOR / NOT_A_FORECAST / NOT_ACTIVE  
**Provider:** The Anthropic Institute  
**Model:** Econ Scenario Explorer v1.0, September 2026  
**Technical paper:** *Economic Scenarios for Transformative AI*, Working Paper No. 2026-02, September 2026  
**Authors:** Anton Korinek, Charles I. Jones, Szymon Sacher, Tess Cotter, Peter McCrory

## Why this belongs in Research Lab

This source provides a structured external model linking AI capability, adoption/diffusion, productivity, automation versus augmentation, worker adjustment and capital supply to macroeconomic outcomes through 2030.

It is useful as a **scenario generator and versioned external prior**, not as a market signal or point forecast.

The authors explicitly state that the modest, substantial and extreme scenarios are illustrative, are **not predictions**, and have **no assigned probabilities**. This archive therefore must never be interpreted as `Anthropic predicts X`.

## Primary source binding

Explorer / model version:
`https://www.anthropic.com/institute/econ-scenarios`

Technical report:
`https://www-cdn.anthropic.com/files/4zrzovbb/website/cf58f84d46a4a76bf5a5b039ac695fba6b80041c.pdf`

Original discovery context:
Anthropic X post supplied by the user on 2026-09-09.

Binary mirroring status:
`NOT_MIRRORED_IN_GIT`

Reason:
the current connector/browser can read the authoritative 57-page PDF but does not expose the original binary bytes for a trustworthy byte-for-byte repository mirror. The canonical URL, document identity, version and machine-readable scenario snapshot are archived instead. Do not fabricate a PDF copy from extracted text or screenshots.

## Model structure worth preserving

The model represents jobs as bundles of tasks and lets AI affect those tasks through augmentation, automation and the creation/reinstatement of tasks. It separates cognitive occupations from other occupations and models worker reallocation through a frictional labor market.

The main scenario dimensions include:

- affected task mass / AI capability reach;
- diffusion / adoption;
- productivity gain per affected task;
- automation share versus augmentation;
- reinstatement / new-task creation;
- worker search/re-employment friction;
- capital supply elasticity;
- wage rigidity.

The user-facing explorer condenses the key judgments into capability, adoption, autonomy, productivity and adjustment.

## Why the capital channel is especially relevant to this framework

The paper models capital as relatively inelastic in the medium run. When AI raises productivity faster than capital can expand, part of the gain can appear as a higher return to capital and a larger capital share of income. This produces a possible transmission chain that is relevant to later governed research:

`AI capability/adoption -> productivity -> demand for capital/compute/infrastructure -> capital share / returns -> sector and asset transmission`

This is a research pathway, not an accepted causal trading rule.

## Scenario snapshot

2030 outcomes reported by the paper:

| Metric | Modest | Substantial | Extreme |
|---|---:|---:|---:|
| GDP vs no-AI path | +1.6% | +8.3% | +32.4% |
| GDP growth, annual | 2.4% | 5.4% | 15.4% |
| Capital share of income | 40.6% | 43.9% | 54.8% |
| Labor share of income | 59.4% | 56.1% | 45.2% |
| Cognitive employment vs mid-2026 | -0.5% | -3.9% | -21.5% |
| All-worker unemployment | 3.9% | 4.6% | 11.9% |
| Cognitive-worker unemployment | 2.9% | 4.5% | 17.9% |

These values are archived mechanically in `ANTHROPIC_ECON_SCENARIO_PRIORS_v1.json` and must remain tied to model version 1.0.

## Survey context

The project reports a representative survey of 10,980 U.S. adults. The median respondent's inputs map approximately to the substantial-change region of the model. This is evidence about surveyed expectations, not evidence that the substantial scenario is objectively most likely.

## Model limitations that must travel with the archive

The current version omits or materially simplifies, among other things:

- business-cycle dynamics;
- aggregate-demand feedback and price rigidities beyond the modelled wage channel;
- financial-market disruptions;
- political-economy responses;
- catastrophic risks;
- rapid robotics / automation of physical tasks;
- detailed worker heterogeneity, tenure and skill loss;
- firm and regional heterogeneity;
- explicit separation of compute capital from other capital;
- saving decisions and richer capital formation;
- several potentially strong feedbacks from AI to AI/R&D itself.

The paper also notes that much of the scenario divergence happens after 2027, so weak near-term differences should not be misread as falsification of the more transformative scenarios.

## Framework placement

- Research Lab: `ADMIT_AS_EXTERNAL_SCENARIO_PRIOR`
- Historical Research Vault: `ARCHIVE_VERSION_AND_SOURCE_BINDING`
- Shadow: `CONTEXT_ONLY_NOT_SIGNAL`
- Core / DATA PING: `NO_DIRECT_INPUT`
- Portfolio execution: `FORBIDDEN`
- Round 3 outcome testing: `NOT_AUTHORIZED_BY_THIS_RECORD`

## Future governed research lanes

Potential later joins, only after the relevant data and research gates allow them:

- AI adoption / capability measures;
- AI, semiconductor and data-centre capex;
- USAD institutional ownership and 13D/G changes;
- government contracts and policy tailwinds;
- patent / innovation activity;
- CFTC positioning;
- labor-share, wage, unemployment and productivity data;
- compute / energy / infrastructure buildout;
- RWA and capital-market transmission.

The purpose is to test whether real-world observations move closer to, or farther from, scenario assumptions over time. It is not to tune a trading system to Anthropic's conclusions.

## Versioning rule

Anthropic labels the explorer `v1.0` and explicitly expects it to evolve. Future versions must be archived as separate versions. Never silently replace this snapshot with a later model.

Required future comparison fields:

- model version;
- publication/retrieval date;
- changed scenario inputs;
- changed calibration assumptions;
- changed output paths;
- changed omissions/caveats;
- changed survey results;
- source URL changes.

## Research verdict

`HIGH_RESEARCH_VALUE / LOW_DIRECT_TRADING_VALUE`

This source is valuable because it turns vague AI-macro narratives into explicit assumptions that can later be challenged against independent data. The archive succeeds if future agents can say which assumptions were supported, contradicted or still unobservable without treating the model itself as ground truth.
