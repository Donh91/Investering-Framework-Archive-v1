// Premium v1.0 canonical-home cutover, presentation only.
// Both shells are built from the SAME public snapshot and retain a rollback route.
// No market decisions, source authority, expiry, forecasts or scoring are changed.
const requireOnce=(html,needle,label)=>{
  if(typeof html!=='string'||html.split(needle).length!==2)
    throw new Error('PREMIUM_RELEASE_INVALID_'+label);
};
export function preserveLegacyShell(html){
  requireOnce(html,'<head>','LEGACY_HEAD');
  requireOnce(html,'src="./app.js"','LEGACY_PRODUCT');
  // The archived /legacy/ document must keep loading root-level shared assets,
  // public snapshots and the existing frozen weekly chart without copying data.
  return html.replace('<head>','<head><base href="../">')
    // A document base for shared root assets must not hijack in-page classic
    // navigation from /legacy/ back to the new canonical root.
    .replace(/href="#([a-z][a-z0-9_-]*)"/gi,'href="./legacy/#$1"');
}
export function releasePremiumShell(html){
  requireOnce(html,'<head>','PREMIUM_HEAD');
  requireOnce(html,'href="./premium.css"','PREMIUM_CSS');
  requireOnce(html,'src="./app.mjs"','PREMIUM_APP');
  requireOnce(html,'role="tablist"','PREMIUM_TABS');
  requireOnce(html,'href="#content"','SKIP_LINK');
  for(const id of ['view-overview','view-compass','view-results'])
    requireOnce(html,'id="'+id+'"','MISSING_'+id.toUpperCase());
  requireOnce(html,'PREMIUM PREVIEW','PREVIEW_MARK');
  requireOnce(html,'CN / PREMIUM CANDIDATE','CANDIDATE_MARK');
  requireOnce(html,'data-t="previewOnly"','PREVIEW_TRANSLATION');
  requireOnce(html,'data-t="legacySite"','LEGACY_TRANSLATION');
  requireOnce(html,'href="../index.html"','ROLLBACK_LINK');
  // The root URL stays canonical. Explicit document base resolves all relative
  // vNext styles, modules and ../data/ fetches exactly as the staged /vnext/ did.
  // The last-known public sources remain authoritative, not this release shell.
  return html
    .replace('<head>','<head><base href="./vnext/">')
    .replace('PREMIUM PREVIEW','PREMIUM LIVE')
    .replace('aria-label="Cycle Navigator vNext"','aria-label="Cycle Navigator"')
    .replace('href="./" class="brand"','href="../" class="brand"')
    .replace('href="#content"','href="../#content"')
    .replace('CN / PREMIUM CANDIDATE','CN / PREMIUM 1.0')
    .replace('data-t="previewOnly">Ikke standardforsiden','>Premium 1.0')
    .replace('href="../index.html" data-t="legacySite">Åbn eksisterende site ↗','href="../legacy/">Legacy ↗');
}
