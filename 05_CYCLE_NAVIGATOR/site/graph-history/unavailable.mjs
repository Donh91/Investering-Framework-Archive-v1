/**
 * SOURCE-FAILURE UI FALLBACK ONLY.
 * If the optional Graph History builder fails, the existing Pages workflow
 * may still publish the live CN site. Never publish a broken History URL
 * as if valid, and never retain a partial/stale timeline.
 *
 * This page is NOT a forecast, source repair, history dataset or model.
 * It deliberately contains no historical prices, scores or demo geometry.
 */
import {mkdir,rm,writeFile,readFile} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';

const outputDir=resolve(dirname(fileURLToPath(import.meta.url)),'../dist');
export const unavailableHtml=`<!doctype html>
<html lang="da">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Grafhistorik midlertidigt utilgængelig | Cycle Navigator</title>
<style>
:root{color-scheme:light dark}
body{font:16px/1.55 system-ui,-apple-system,sans-serif;margin:0;padding:clamp(1.5rem,5vw,4rem);background:#f7f8fa;color:#1a2638}
main{max-width:48rem;margin:12vh auto 0;background:white;padding:clamp(1.5rem,5vw,3rem);border:1px solid #dde2e9;border-radius:1rem}
h1{font-size:clamp(1.6rem,4vw,2.25rem);line-height:1.2;margin:0 0 1rem}
a{color:#175ba8;text-underline-offset:3px}
@media(prefers-color-scheme:dark){body{background:#101620;color:#eaf0fa}main{background:#192230;border-color:#344057}a{color:#89bdff}}
</style>
</head>
<body data-cn-history-status="UNAVAILABLE">
<main role="status" aria-live="polite">
<p>Cycle Navigator · Kildekontrol</p>
<h1>Grafhistorikken er midlertidigt utilgængelig</h1>
<p>De nødvendige historiske kildebeviser kunne ikke godkendes ved seneste udgivelse. Derfor vises ingen kurser, historik eller prognose i denne visning.</p>
<p lang="en">Graph History is temporarily unavailable because its original source evidence could not be verified. No historical prices or forecasts are displayed.</p>
<p>Den aktive ugentlige prognose er ikke ændret. <a href="../">Tilbage til Cycle Navigator</a>.</p>
</main>
</body>
</html>
`;

export async function quarantineGraphHistory(root=outputDir){
 const dist=resolve(root);
 const file=resolve(dist,'graph-history/index.html');
 const data=resolve(dist,'data/graph-history/timeline.json');
 await rm(data,{force:true});
 await mkdir(dirname(file),{recursive:true});
 await writeFile(file,unavailableHtml,'utf8');
 if((await readFile(file,'utf8'))!==unavailableHtml)throw Error('CN_GRAPH_HISTORY_FALLBACK_READBACK_MISMATCH');
 return {status:'UNAVAILABLE',history_route:'graph-history/index.html',timeline_published:false};
}

if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 quarantineGraphHistory().then(result=>{
  console.log('CN_GRAPH_HISTORY_UNAVAILABLE_FALLBACK_VERIFIED '+JSON.stringify(result));
 }).catch(error=>{console.error(error.message);process.exitCode=1});
}
