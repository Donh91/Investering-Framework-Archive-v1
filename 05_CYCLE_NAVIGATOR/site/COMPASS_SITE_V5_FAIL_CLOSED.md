# Failure behavior

If the public Compass pointer is missing, malformed, hash-mismatched, points outside the approved public root, or resolves to an invalid projection, the build emits a `NOT_PUBLISHED` public Compass state. The browser then displays that fresh navigation is unavailable. It does not infer an action from live prices or weekly text.
