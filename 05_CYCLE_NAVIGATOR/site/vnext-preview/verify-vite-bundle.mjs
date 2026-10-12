// Reproduces AppDeploy's Vite bundling from GitHub sources in CI without
// changing the published Pages site or adding a runtime dependency.
import { mkdtempSync, mkdirSync, readFileSync, writeFileSync, cpSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';

const base = dirname(fileURLToPath(import.meta.url));
const temp = mkdtempSync(join(tmpdir(), 'cn-vnext-vite-'));
const root = join(temp, 'app');
mkdirSync(join(root,'src'),{recursive:true});
mkdirSync(join(root,'public'),{recursive:true});

const rawHtml=readFileSync(resolve(base,'premium-index.html'),'utf8');
const html=rawHtml
  .replace('./premium.css','./src/styles.css')
  .replace('./premium.js','./src/main.ts');
writeFileSync(join(root,'index.html'),html);
writeFileSync(join(root,'src','main.ts'),readFileSync(resolve(base,'premium.js'),'utf8')
  .replace('./premium-i18n.js','./i18n.js'));
for (const [src,target] of [
  ['premium.css','src/styles.css'],
  ['premium-i18n.js','src/i18n.js'],
  ['official-bullbear.mjs','src/official-bullbear.mjs'],
  ['official-pullback-eta.mjs','src/official-pullback-eta.mjs'],
  ['official-pullback-stage.mjs','src/official-pullback-stage.mjs'],
  ['seed.json','public/seed.json']
]) cpSync(resolve(base,src),join(root,target));

writeFileSync(join(root,'package.json'),JSON.stringify({
  name:'cn-vnext-vite-source-parity',private:true,type:'module',
  scripts:{build:'vite build'},
  devDependencies:{vite:'^6.0.0',typescript:'^5.7.0'}
},null,2));
writeFileSync(join(root,'vite.config.js'),"import { defineConfig } from 'vite';\nexport default defineConfig({base:'./',build:{outDir:'dist'}});\n");
try {
  console.log('Reproduce isolated Vite build from canonical GitHub source');
  execFileSync('npm',['install','--no-audit','--no-fund','--ignore-scripts'],{
    cwd:root,stdio:'inherit',timeout:120000
  });
  execFileSync('npm',['run','build'],{cwd:root,stdio:'inherit',timeout:120000});
  console.log('PASS: exact-source Vite bundle builds without modifying production');
} finally {
  rmSync(temp,{recursive:true,force:true});
}
