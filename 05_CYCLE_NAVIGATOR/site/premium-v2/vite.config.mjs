/** Source-first Vite 6 multi-page build, NEVER a canonical root Pages cutover.
 * Unlike AppDeploy's single default index build, this explicitly emits
 * BOTH /next/index.html and /next/graph-b/source-graph-b.html.
 * Same source files as static build-next; no demo source, no backend.
 * `npm ci` must follow a reviewed lockfile before production staging.
 */
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {defineConfig} from 'vite';
const root=fileURLToPath(new URL('.',import.meta.url));
export default defineConfig({
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
