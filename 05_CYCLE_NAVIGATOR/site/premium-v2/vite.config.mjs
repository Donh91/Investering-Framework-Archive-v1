/** Source-first Vite 6 multi-page build, NEVER a canonical root Pages cutover.
 * Unlike AppDeploy's single default index build, this explicitly emits
 * BOTH /next/index.html and /next/graph-b/source-graph-b.html.
 * Same source files as static build-next; no demo source, no backend.
 * `npm ci` must follow a reviewed lockfile before production staging.
 */
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {defineConfig} from 'vite';
import {readFileSync} from 'node:fs';
import {buildPremiumRootHtml} from './premium-root.mjs';
import {buildUnifiedRootHtml} from './unified-root.mjs';
const root=fileURLToPath(new URL('.',import.meta.url));
export default defineConfig({
 plugins:[{
  name:'cn-premium-root-from-original-graph-b',
  enforce:'pre',
  transformIndexHtml:{
   order:'pre',
   handler(html,context){
    // /next/index.html is the current release candidate and stays immutable.
    // /next/unified.html is an isolated noindex product convergence preview,
    // NEVER a promotion instruction or an extra canonical homepage.
    const entry=resolve(context.filename||'');
    if(entry!==resolve(root,'index.html')&&entry!==resolve(root,'unified.html'))return html;
    const original=readFileSync(resolve(root,'graph-b/source-graph-b.html'),'utf8');
    if(entry===resolve(root,'index.html'))return buildPremiumRootHtml(original);
    const pro=readFileSync(resolve(root,'../vnext-live/index.html'),'utf8');
    return buildUnifiedRootHtml(original,pro);
   }
  }
 }],
 root,publicDir:false,
 base:'/Investering-Framework-Archive-v1/next/',
 build:{
   outDir:resolve(root,'../dist/next'),
   emptyOutDir:true,
   sourcemap:false,
   rollupOptions:{
     input:{
       index:resolve(root,'index.html'),
       unified:resolve(root,'unified.html'),
       graphB:resolve(root,'graph-b/source-graph-b.html')
     }
   }
 },
 server:{port:4173,strictPort:true},
 preview:{port:4174,strictPort:true}
});
