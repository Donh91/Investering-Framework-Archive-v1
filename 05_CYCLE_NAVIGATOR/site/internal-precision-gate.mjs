// Pure, source-first gate: internal claims are NOT allowed to veto public forecast
// availability when a separately owner-approved daily W46 source reissue changed
// the exact public forecast SHA. Never reuse stale claim scoring.
export function resolveInternalPrecision(current, publicFreezeSha, expectedIssue) {
  if (current == null) return {status:"NOT_MATERIALIZED", claims:[]};
  if (typeof current !== "object" || Array.isArray(current))
    throw new Error("LIVE observation refused: malformed internal precision freeze");
  if (String(current.source_public_freeze_sha256 || "") !== String(publicFreezeSha || ""))
    return {status:"SOURCE_BINDING_STALE_QUARANTINED", claims:[]};
  if (Number(current.issue_number) !== Number(expectedIssue))
    throw new Error("LIVE observation refused: frozen-claim issue mismatch");
  if (!Array.isArray(current.claims))
    throw new Error("LIVE observation refused: bound internal claim list malformed");
  return {status:"BOUND", claims:current.claims};
}
