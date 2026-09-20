# Jev stress + Sol token benchmark v1

Purpose: expand falsification before any Alpha Lab authority.

Deterministic stress covers recursive outcome leakage, mutable-live-field rejection, post-cutoff timestamps, UNKNOWN semantics, no-DROP routing, zero-authority prediction freeze, deterministic hashes, and a 255-feature irrelevant-detail/size packet.

Live Jev remains synthetic and shadow-only. It may be manually dispatched after merge.

The Sol benchmark is explicitly one request, no tools, no repository writes and no trade recommendation. It logs input/output/total tokens and latency, not credentials or full model output. It requires repository secret `OPENAI_API_KEY`. If the secret is absent, that job must fail closed. This test is authorized by the user but must not create or expose a key automatically.

Comparison caveat: Jev and GPT-5.6 are different interfaces and tokenizers. Token counts are logged as provider-reported consumption, not treated as directly equivalent intelligence or cost. Any later cost comparison must use contemporaneous provider pricing and repeated representative workloads.
