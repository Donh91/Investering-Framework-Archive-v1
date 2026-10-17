// Reproduces AppDeploy's Vite bundling from GitHub sources in CI without
// changing the published Pages site or adding a runtime dependency.
import { mkdtempSync, mkdirSync, readFileSync, writeFileSync, cpSync, rmSync, readdirSync, existsSync } from 'node:fs';
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
  ['official-feed-parity.mjs','src/official-feed-parity.mjs'],
  ['current-public-panel.mjs','src/current-public-panel.mjs'],
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
    // The multi-file archive remains byte-for-byte the Vite build. In a
    // separate second build, embed ONLY the existing allowlisted public seed
    // as a data URL, then inline compiled CSS/JS and the public SVG logo.
    // This yields a single HTML file that can also open without HTTP hosting.
    const entryPath=join(root,'src','main.ts');
    const originalEntry=readFileSync(entryPath,'utf8');
    const seedDeclaration="const SOURCE_FILE = './seed.json';";
    if(originalEntry.split(seedDeclaration).length!==2)
      throw new Error('Single-file source must have one exact archived seed declaration');
    const seedDataUrl='data:application/json;base64,'+
      readFileSync(resolve(base,'seed.json')).toString('base64');
    writeFileSync(entryPath,originalEntry.replace(seedDeclaration,
      "const SOURCE_FILE = '"+seedDataUrl+"';"));
    execFileSync('npm',['run','build'],{cwd:root,stdio:'inherit',timeout:120000});
    const offlineDist=join(root,'dist');
    let offlineHtml=readFileSync(join(offlineDist,'index.html'),'utf8');
    const scriptTags=[...offlineHtml.matchAll(/<script\b[^>]*\bsrc="[^"]+\.js"[^>]*><\/script>/g)];
    const styleTags=[...offlineHtml.matchAll(/<link\b[^>]*>/g)]
      .filter(m=>/\brel="stylesheet"/.test(m[0])&&/\bhref="[^"]+\.css"/.test(m[0]));
    if(scriptTags.length!==1||styleTags.length!==1)
      throw new Error('Offline HTML requires exactly one JS and one CSS asset');
    const readBundledAsset=(tag,kind)=>{
      const path=(kind==='js'
        ?tag.match(/\bsrc="([^"]+)"/)
        :tag.match(/\bhref="([^"]+)"/))?.[1];
      if(!path||!/^\.\/assets\/[A-Za-z0-9._-]+\.(js|css)$/.test(path)||
         !path.endsWith('.'+kind))
        throw new Error('Unexpected bundled asset: '+String(path));
      return readFileSync(join(offlineDist,path.slice(2)),'utf8');
    };
    const bundledJS=readBundledAsset(scriptTags[0][0],'js');
    const bundledCSS=readBundledAsset(styleTags[0][0],'css');
    if(!bundledJS.includes('data:application/json;base64,'))
      throw new Error('Portable preview did not embed original frozen source bytes');
    offlineHtml=offlineHtml.replace(scriptTags[0][0],
      '<script type="module">'+bundledJS.replace(/<\/script/gi,'<\\/script')+'</script>');
    offlineHtml=offlineHtml.replace(styleTags[0][0],
      '<style>'+bundledCSS.replace(/<\/style/gi,'<\\/style')+'</style>');
    const logoPattern=/(<img class="cn-logo" src=")[^"]+(")/;
    if(!logoPattern.test(offlineHtml))throw new Error('Portable preview logo missing');
    const svgDataUrl='data:image/svg+xml;base64,'+
      readFileSync(resolve(base,'CN_LOGO.svg')).toString('base64');
    offlineHtml=offlineHtml.replace(logoPattern,(_,first,last)=>first+svgDataUrl+last);
    if(/<script\b[^>]*\bsrc=/.test(offlineHtml)||
       /<link\b[^>]*\brel="stylesheet"/.test(offlineHtml))
      throw new Error('Portable HTML still depends on external JS or CSS assets');
    writeFileSync(join(artifactDir,'CYCLE_NAVIGATOR_OFFLINE_PREVIEW.html'),offlineHtml);
    console.log('PASS: single-file offline HTML includes source, JS, CSS and SVG logo');
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
      'official-pullback-stage.mjs','official-pullback-investor-view.mjs','official-path.mjs',
      'official-feed-parity.mjs','current-public-panel.mjs'];
    const manifest={
      contract:'CN_VNEXT_GITHUB_ARTIFACT_PREVIEW_v1',
      authority:'ISOLATED_ARCHIVED_SEED_WITH_OPTIONAL_PUBLIC_CURRENT_READBACK_NOT_PRODUCTION',
      production_pages_unchanged:true,
      deployed:false,
      offline_single_file:true,
      source_head_sha:process.env.PR_HEAD_SHA||null,
      checkout_sha:process.env.GITHUB_SHA||null,
      source_files:sources.map(name=>({path:name,sha256:sha256(readFileSync(resolve(base,name)))})),
      output_files:entries,
      note:'Includes original W40/W41 archive seed plus an independent optional canonical public current-readback panel which fails closed without browser network access. Single-file portable HTML embeds archived seed/JS/CSS/logo. Multi-file index.html requires HTTP. No Pages/AppDeploy deployment or native Safari acceptance is claimed.'
    };
    writeFileSync(join(artifactDir,'PREVIEW_MANIFEST.json'),JSON.stringify(manifest,null,2)+'\n');
    console.log('PASS: portable GitHub preview artifact '+entries.length+' bundled files with SHA-256 manifest');
  }
  console.log('PASS: exact-source Vite bundle builds without modifying production');
} finally {
  rmSync(temp,{recursive:true,force:true});
}
