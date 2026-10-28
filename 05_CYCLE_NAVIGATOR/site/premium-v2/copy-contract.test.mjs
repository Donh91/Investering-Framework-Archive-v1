import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {buildPremiumRootHtml} from './premium-root.mjs';

const read=p=>readFile(new URL(p,import.meta.url),'utf8');
const [source,graphCode,compassShell,app]=await Promise.all([
 read('./graph-b/source-graph-b.html'),
 read('./graph-b/source-graph-b.mjs'),
 read('../vnext-live/index.html'),
 read('../vnext-live/app.mjs')
]);

test('Graph B chart remains exactly one source-owned SVG',()=>{
 const built=buildPremiumRootHtml(source);
 assert.equal((built.match(/id="variant-panel"/g)||[]).length,1);
 assert.equal((built.match(/id="chart"/g)||[]).length,1);
 assert.equal((built.match(/id="forecast"/g)||[]).length,1);
 assert.equal((built.match(/id="actual"/g)||[]).length,1);
 assert.match(built,/id="source-state"/);
 assert.match(graphCode,/readOfficialGraphB/);
 assert.doesNotMatch(built,/Math\.sin\s*\(/);
});

test('Chart and proof distinguish original forecasts from verified observations',()=>{
 assert.match(source,/Oprindelige prisintervaller og verificerede timekurser/);
 assert.match(source,/Udstedt dagsprognose/);
 assert.match(source,/Observeret timekurs/);
 assert.match(source,/Frosset prisinterval/);
 assert.match(source,/70\/30-scoren gælder prisintervaller, ikke afkast/);
 assert.match(source,/Manglende data tæller ikke som et korrekt resultat/);
 assert.match(graphCode,/No daily forecast line without prior issuance/);
 assert.doesNotMatch(source,/Forventet low \/ high/);
});

test('Kompas PRO wording in preview is consistent in Danish and English',()=>{
 assert.match(compassShell,/data-t="tabCompass">Kompas PRO/);
 assert.match(compassShell,/data-t="compassHeading">Kompas PRO/);
 assert.match(app,/tabCompass:'Kompas PRO'/);
 assert.match(app,/tabCompass:'Compass PRO'/);
 assert.match(app,/Aktuel retning er ikke en prognose/);
 assert.match(app,/Current direction is not a forecast/);
 assert.match(app,/DISTRIBUTIONSRISIKO/);
 assert.match(app,/DISTRIBUTION RISK/);
});

test('Professional accountability and trader warnings are explicit, not marketing accuracy',()=>{
 assert.match(app,/ikke afkast eller handelsresultater/);
 assert.match(app,/not returns or trading results/);
 assert.match(app,/Ingen blå dagsprognose uden forudgående udstedelse/);
 assert.doesNotMatch(app,/resultsHeading:'Beviser frem for hype\.'/);
 assert.match(source,/risiko er ikke i sig selv en salgsordre/);
});
