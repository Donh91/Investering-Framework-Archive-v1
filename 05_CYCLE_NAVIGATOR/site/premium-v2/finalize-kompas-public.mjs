/** Final public build step, called only after existing lineage receipt. */
import {readFile,writeFile,copyFile,rename,unlink} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {buildKompasProPublic} from './kompas-pro-public-v1.mjs';
const here=dirname(fileURLToPath(import.meta.url)),names=['latest.json','compass.json','publication-lineage.json'];
const digest=x=>createHash('sha256').update(x).digest('hex');
export async function verifyKompasPublicBinding(dataDir){
 const [a,b,c,raw]=await Promise.all([...names,'kompas-pro.v1.json'].map(n=>readFile(resolve(dataDir,n))));
 const p=JSON.parse(raw);
 if(p.contract!=='CN_KOMPAS_PRO_PUBLIC_v1'||p.version!==1||p.source_shas?.latest_json!==digest(a)||p.source_shas?.compass_json!==digest(b)||p.source_shas?.publication_lineage_json!==digest(c))throw Error('KOMPAS_PRO_FINAL_BYTE_BINDING_MISMATCH');
 // Matching source hashes do not authenticate derived values. Rebuild at the
 // recorded build clock, not the later staging clock. Runtime checks expiry.
 const builtAt=typeof p.generated_at==='string'?Date.parse(p.generated_at):NaN;
 if(!Number.isFinite(builtAt)||new Date(builtAt).toISOString()!==p.generated_at)throw Error('KOMPAS_PRO_FINAL_BUILD_CLOCK_INVALID');
 const expected=buildKompasProPublic(a,b,c,{nowMs:builtAt});
 if(!raw.equals(Buffer.from(JSON.stringify(expected,null,2)+'\n')))throw Error('KOMPAS_PRO_FINAL_PROJECTION_MISMATCH');
 return p;
}
export async function finalizeKompasPublic(dataDir,{nowMs=Date.now()}={}){
 const [a,b,c]=await Promise.all(names.map(n=>readFile(resolve(dataDir,n))));
 const p=buildKompasProPublic(a,b,c,{nowMs});
 const target=resolve(dataDir,'kompas-pro.v1.json'),temp=target+'.tmp';
 try{
  await writeFile(temp,JSON.stringify(p,null,2)+'\n');
  await copyFile(resolve(here,'kompas-pro.v1.schema.json'),resolve(dataDir,'kompas-pro.v1.schema.json'));
  await rename(temp,target);
  await verifyKompasPublicBinding(dataDir);
 }catch(e){await unlink(temp).catch(()=>{});throw e}
 return p;
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const dataDir=process.argv[2];if(!dataDir)throw Error('DATA_DIR_REQUIRED');
 const p=await finalizeKompasPublic(resolve(dataDir));console.log('KOMPAS_PRO_PUBLIC_FINAL '+p.state);
}
