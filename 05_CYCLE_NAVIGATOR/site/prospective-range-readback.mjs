import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
const run=promisify(execFile);
// Reuse the exact weekly model-input validator; never implement a site forecast.
export async function prospectiveRangeReadback(repoRoot,pointer,pkg){
  const fallback={contract:'CN_PROSPECTIVE_RANGE_CONSUMER_READBACK_v1',status:'SOURCE_UNAVAILABLE',reason_codes:['BRIDGE_VALIDATOR_UNAVAILABLE'],producer:'CN_PROSPECTIVE_RANGE_BRIDGE_v1',consumer:'PUBLIC_SITE',range_values_admitted:false,scientific_admission:false,portfolio_authority:false};
  const stamp=Number(pkg?.generated_unix);
  if(!Number.isInteger(pointer?.iso_year)||!Number.isInteger(pointer?.iso_week)||!Number.isFinite(stamp)||stamp<=0)return {...fallback,reason_codes:['FORECAST_CLOCK_UNVERIFIED']};
  try{
    const {stdout}=await run('python3',['-m','scripts.cycle_navigator.prospective_range_bridge','--repo-root',repoRoot,'--target-year',String(pointer.iso_year),'--target-week',String(pointer.iso_week),'--freeze-at',new Date(stamp*1000).toISOString()],{cwd:repoRoot,timeout:10000,maxBuffer:1024*1024});
    const result=JSON.parse(stdout);
    if(result?.consumer_receipt?.range_values_admitted===true)return result;
    if(result?.contract==='CN_PROSPECTIVE_RANGE_CONSUMER_READBACK_v1'&&result.range_values_admitted===false)return result;
  }catch{}
  return fallback;
}
