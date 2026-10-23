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
const root=fileURLToPath(new URL('.',import.meta.url));
export default defineConfig({
 plugins:[{
  name:'cn-premium-root-from-original-graph-b',
  enforce:'pre',
  transformIndexHtml:{
   order:'pre',
   handler(html,context){
    // Only replace /next/index.html, NEVER the nested source Graph B entry.
    if(resolve(context.filename||'')!==resolve(root,'index.html'))return html;
    const original=readFileSync(resolve(root,'graph-b/source-graph-b.html'),'utf8');
    return buildPremiumRootHtml(original);
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
       graphB:resolve(root,'graph-b/source-graph-b.html')
     }
   }
 },
 server:{port:4173,strictPort:true},
 preview:{port:4174,strictPort:true}
});
