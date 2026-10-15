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
    // A second deterministic Vite build changes ONLY the transport for the
    // already allowlisted archive seed: embed its original public bytes as
    // a data URL. This produces a single-file offline preview for iPhone/
    // desktop Files/Safari, without changing production or source contracts.
    const originalMain=readFileSync(join(root,'src','main.ts'),'utf8');
    const seedDecl="const SOURCE_FILE = './seed.json';";
    if (originalMain.split(seedDecl).length !== 2)
      throw new Error('Cannot source-bind offline preview without exactly one seed declaration');
    const seedUri='data:application/json;base64,'+
      readFileSync(resolve(base,'seed.json')).toString('base64');
    writeFileSync(join(root,'src','main.ts'),
      originalMain.replace(seedDecl,"const SOURCE_FILE = '"+seedUri+"';"));
    execFileSync('npm',['run','build'],{cwd:root,stdio:'inherit',timeout:120000});
    const offlineDist=join(root,'dist');
    let offlineHtml=readFileSync(join(offlineDist,'index.html'),'utf8');
    const scripts=[...offlineHtml.matchAll(/<script\\b[^>]*\\bsrc="[^"]+\\.js"[^>]*><\\/script>/g)];
    const cssLinks=[...offlineHtml.matchAll(/<link\\b[^>]*>/g)].filter(m=>
      /\\brel="stylesheet"/.test(m[0]) && /\\bhref="[^"]+\\.css"/.test(m[0]));
    if(scripts.length!==1 || cssLinks.length!==1)
      throw new Error('Offline single-file requires exactly one bundled JS and CSS file');
    const asset=(tag,attribute,type)=>{
      const name=tag.match(new RegExp('\\\\b'+attribute+'="([^"]+)"'))?.[1];
      if(!name || !new RegExp('^\\\\./assets/[A-Za-z0-9._-]+\\\\.'+type+'
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
      offline_single_file:true,
      source_head_sha:process.env.PR_HEAD_SHA||null,
      checkout_sha:process.env.GITHUB_SHA||null,
      source_files:sources.map(name=>({path:name,sha256:sha256(readFileSync(resolve(base,name)))})),
      output_files:entries,
      note:'Includes standalone CYCLE_NAVIGATOR_OFFLINE_PREVIEW.html with embedded archived public seed/code/logo; still requires user-device interaction QA. The multi-file index.html requires HTTP serving. No hosted preview or production deploy is claimed.'
    };
    writeFileSync(join(artifactDir,'PREVIEW_MANIFEST.json'),JSON.stringify(manifest,null,2)+'\n');
    console.log('PASS: portable GitHub preview artifact '+entries.length+' bundled files with SHA-256 manifest');
  }
  console.log('PASS: exact-source Vite bundle builds without modifying production');
} finally {
  rmSync(temp,{recursive:true,force:true});
}
).test(name))
        throw new Error('Offline preview refused unexpected local asset '+String(name));
      return readFileSync(join(offlineDist,name.slice(2)),'utf8');
    };
    const compiledJs=asset(scripts[0][0],'src','js');
    const compiledCss=asset(cssLinks[0][0],'href','css');
    if(!compiledJs.includes('data:application/json;base64,'))
      throw new Error('Offline preview must embed original frozen public JSON seed');
    offlineHtml=offlineHtml.replace(scripts[0][0],
      '<script type="module">'+compiledJs.replace(/<\\/script/gi,'<\\\\/script')+'</script>');
    offlineHtml=offlineHtml.replace(cssLinks[0][0],
      '<style>'+compiledCss.replace(/<\\/style/gi,'<\\\\/style')+'</style>');
    const svgUri='data:image/svg+xml;base64,'+
      readFileSync(resolve(base,'CN_LOGO.svg')).toString('base64');
    const logo=/(<img class="cn-logo" src=")[^"]+(")/;
    if(!logo.test(offlineHtml))throw new Error('Required offline preview logo missing');
    offlineHtml=offlineHtml.replace(logo,(_,head,tail)=>head+svgUri+tail);
    if(/<script\\b[^>]*\\bsrc=/.test(offlineHtml)||
       /<link\\b[^>]*\\brel="stylesheet"/.test(offlineHtml))
      throw new Error('Offline file still depends on external JS/CSS assets');
    writeFileSync(join(artifactDir,'CYCLE_NAVIGATOR_OFFLINE_PREVIEW.html'),offlineHtml);
    console.log('PASS: offline single-file interactive archive preview has embedded data, code and logo');
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
