/* Staged premium chart source identity. Pure, no clock, no market logic.
 * The original chart uses BOTH the live precision artifact and the public
 * publication projection, so a data-refresh key must include BOTH. */
export function chartSourceFingerprint(latest, nowMs=Date.now()) {
  const v=latest?.public_live_precision||null;
  const projection=latest?.public_series?.current_public_projection||null;
  const pointer=latest?.pointer||null;
  // Match the embedded original CNWeekChart model's SOURCE freshness policy.
  // Re-mount once when observed evidence goes STALE; avoid 1-minute refresh
  // remounts and user zoom/selected-asset loss while evidence remains fresh.
  const cutoff=Date.parse(v?.daily_observations?.observed_through_utc||v?.live_as_of_utc);
  const age=nowMs-cutoff;
  const sla=Math.max(30,Number(v?.freshness_sla_minutes)||90)*60000;
  const stale=!Number.isFinite(cutoff)||age<0||age>sla;
  return JSON.stringify([
    projection?.public_issue_number??null,projection?.forecast_week??null,
    pointer?.issue_number??null,pointer?.iso_year??null,pointer?.iso_week??null,
    pointer?.status??null,stale,
    v?.public_issue_number??null,v?.forecast_week??null,
    v?.window_scores??null,v?.rows??null,v?.daily_price_path??null,
    v?.daily_observations??null,v?.hourly_price_path??null,v?.live_as_of_utc??null
  ]);
}
