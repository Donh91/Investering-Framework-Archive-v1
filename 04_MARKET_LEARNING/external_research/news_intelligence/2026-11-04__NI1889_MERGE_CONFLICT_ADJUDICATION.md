# NI #1889 · original PR conflict repair, 2026-11-04

Original head `d8f11514b2c53ee10b83f9a25873c687b2732ffc` was blocked by a conflict in the shared Sol research queue. The original branch would overwrite newer current-main mission state including CN1879 and would change unrelated paid mission status. No source-code or test file overlaps with current main.

**Safe resolution:** preserve the entire current main `research/api_agent/research_lab_sol/RESEARCH_LAB_SOL_QUEUE_v1.json` blob `6ce00545445db9a2d061ba0ae58762e61c02b583` rather than overwrite with obsolete PR history. Carry over original PR's election vocabulary, bounded UTC first-known/source-completion clock, negative regressions and advisory source audit. Its paid Sol mission packet is retained as non-executable **staged**, not in the active paid queue. This does not spend money or activate an extra issuer.

The resulting merge tree is based exactly on current main `2f15f4451b8fd5d6ccd632ed83f70cdc4b935ffa`, includes only the four source/packet/doc/test PR files plus this conflict adjudication, and is committed as a two-parent merge on the EXISTING PR branch. All other current-main source/captures/receipts and the active API mission remain intact.

Required before release: exact-head hosted CI (Situation Room tests, Director/API Gateway, Data Architecture), independent source/clock negative controls, explicit original PR owner release, actual main readback, and later natural daily output. Synthetic election tests are not proof of complete real-world recall or economic edge.
