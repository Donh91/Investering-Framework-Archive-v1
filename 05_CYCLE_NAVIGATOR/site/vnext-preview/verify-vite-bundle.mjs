// Reproduces AppDeploy's Vite bundling from GitHub sources in CI without
// changing the published Pages site or adding a runtime dependency.
import { mkdtempSync, mkdirSync, readFileSync, writeFileSync, cpSync, rmSync, readdirSync, statSync, existsSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { tmpdir } from 'node:os';
import { join, resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';

const base = dirname(fileURLToPath(import.meta.url));
const artifactFlagIndex = process.argv.indexOf('--artifact-dir');
if (artifactFlagIndex >= 0 && (!process.argv[artifactFlagIndex + 1] || artifactFlagIndex + 2 !== process.argv.length)) {
  throw new Error('Expected exactly --artifact-dir <directory>');
}
if (artifactFlagIndex < 0 && process.argv.length > 2) throw new Error('Unexpected argument');
const artifactDir = artifactFlagIndex >= 0 ? resolve(process.argv[artifactFlagIndex + 1]) : null;
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');

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
  ['official-pullback-investor-view.mjs','src/official-pullback-investor-view.mjs'],
  ['official-path.mjs','src/official-path.mjs'],
  ['seed.json','public/seed.json'],
  ['CN_LOGO.svg','public/CN_LOGO.svg']
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
  const dist=join(root,'dist');
  for (const required of ['index.html','seed.json','CN_LOGO.svg']) {
    if (!existsSync(join(dist,required))) throw new Error('Missing required preview asset: '+required);
  }
  if (artifactDir) {
    if (existsSync(artifactDir)) throw new Error('Refusing to overwrite existing preview artifact directory');
    mkdirSync(artifactDir,{recursive:true});
    cpSync(dist,artifactDir,{recursive:true,force:false});
    const entries=[];
    function capture(directory,relative='') {
      for (const ent of readdirSync(directory,{withFileTypes:true})) {
        const name=relative?relative+'/'+ent.name:ent.name;
        if(ent.isSymbolicLink()) throw new Error('Unexpected symbolic link in preview artifact');
        if(ent.isDirectory()) capture(join(directory,ent.name),name);
        else if(ent.isFile()) {
          const bytes=readFileSync(join(directory,ent.name));
          entries.push({path:name,bytes:bytes.length,sha256:sha256(bytes)});
        } else throw new Error('Unexpected preview file kind');
      }
    }
    capture(artifactDir);
    entries.sort((a,b)=>a.path.localeCompare(b.path));
    const sources=['premium-index.html','premium.js','premium.css','premium-i18n.js',
      'seed.json','CN_LOGO.svg','official-bullbear.mjs','official-pullback-eta.mjs',
      'official-pullback-stage.mjs','official-pullback-investor-view.mjs','official-path.mjs'];
    const manifest={
      contract:'CN_VNEXT_GITHUB_ARTIFACT_PREVIEW_v1',
      authority:'ISOLATED_ARCHIVED_SOURCE_ONLY_NOT_PRODUCTION',
      production_pages_unchanged:true,
      deployed:false,
      source_head_sha:process.env.PR_HEAD_SHA||null,
      checkout_sha:process.env.GITHUB_SHA||null,
      source_files:sources.map(name=>({path:name,sha256:sha256(readFileSync(resolve(base,name)))})),
      output_files:entries,
      note:'Static web bundle; opening index.html may require HTTP serving for modules and source fetch. No online preview URL is claimed.'
    };
    writeFileSync(join(artifactDir,'PREVIEW_MANIFEST.json'),JSON.stringify(manifest,null,2)+'\n');
    console.log('PASS: portable GitHub preview artifact '+entries.length+' bundled files with SHA-256 manifest');
  }
  console.log('PASS: exact-source Vite bundle builds without modifying production');
} finally {
  rmSync(temp,{recursive:true,force:true});
}
