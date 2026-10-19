/* Staged premium chart source identity. Pure, no clock, no market logic.
 * The original chart uses BOTH the live precision artifact and the public
 * publication projection, so a data-refresh key must include BOTH. */
export function chartSourceFingerprint(latest) {
  const v=latest?.public_live_precision||null;
  const projection=latest?.public_series?.current_public_projection||null;
  const pointer=latest?.pointer||null;
  return JSON.stringify([
    projection?.public_issue_number??null,projection?.forecast_week??null,
    pointer?.issue_number??null,pointer?.iso_year??null,pointer?.iso_week??null,
    pointer?.status??null,
    v?.public_issue_number??null,v?.forecast_week??null,
    v?.window_scores??null,v?.rows??null,v?.daily_price_path??null,
    v?.daily_observations??null,v?.live_as_of_utc??null
  ]);
}
