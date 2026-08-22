# Evaluation Pipeline

The evaluator scores only already-frozen candidate decisions against frozen outcomes. It deliberately does not implement sensor transforms or market thresholds. This prevents the evaluation layer from silently inventing semantics.

Missing values are excluded, never substituted with zero.
