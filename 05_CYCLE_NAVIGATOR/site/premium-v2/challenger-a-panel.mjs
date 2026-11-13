/**
 * Task2 #1596, Challenger A. Read-only SITE sidecar inside Prognose.
 * Does not calculate a forecast, ingest hourly prices, amend CN, or issue
 * a market action. Missing public issuance must remain visibly unavailable.
 */
export const CHALLENGER_A_PUBLIC_CONTRACT = 'CN_CHALLENGER_A_PUBLIC_SHADOW_v1';
const DATA_URL = '/Investering-Framework-Archive-v1/data/challenger-a/latest.json';
const SOURCE_URL = 'https://github.com/Donh91/Investering-Framework-Archive-v1/pull/2124';
const SHA40 = /^[a-f0-9]{40}$/i, SHA64 = /^[a-f0-9]{64}$/i;
const WEEK = /^20\d{2}-W(?:0[1-9]|[1-4]\d|5[0-3])$/;
const numeric = x => typeof x === 'number' && Number.isFinite(x) && x > 0;
const date = s => typeof s === 'string' && /^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/.test(s) && Number.isFinite(Date.parse(s));

export function validateChallengerPublic(payload, now = Date.now()) {
  const refuse = reason => ({ok:false,reason});
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) return refuse('MISSING_PUBLICATION');
  if (payload.contract !== CHALLENGER_A_PUBLIC_CONTRACT ||
      payload.publication_status !== 'ISSUED_FROZEN' ||
      payload.visibility !== 'SHADOW_ONLY') return refuse('CONTRACT_OR_AUTHORITY_MISMATCH');
  const src=payload.source, i=payload.issuance;
  if (!src || !SHA40.test(src.blob_sha || '') || !SHA40.test(src.first_in_main_commit || '') ||
      !date(src.first_in_main_utc) || !SHA64.test(src.sha256 || '')) return refuse('MISSING_SOURCE_ATTESTATION');
  if (!i || i.contract !== 'TASK2_CHALLENGER_A_SQRT_T_VOL_BAND_v1' ||
      i.formula_version !== 'A1' || !SHA64.test(i.issuance_sha256 || '') ||
      i.authority?.research_only !== true || i.authority?.official_forecast !== false ||
      i.authority?.trading !== false || i.authority?.promotion !== false ||
      !WEEK.test(i.week || '') || i.week < '2026-W47' || !date(i.issue_clock_utc))
    return refuse('FORECAST_CONTRACT_MISMATCH');
  const issue=Date.parse(i.issue_clock_utc),known=Date.parse(src.first_in_main_utc);
  const t=typeof now==='number'?now:Date.parse(now);
  if (!Number.isFinite(t) || known < issue || known > t || issue > t)
    return refuse('NON_CAUSAL_ISSUANCE_CLOCK');
  // One exact weekly issuance, seven forward days for BOTH assets. Missing
  // or retroactively added days must never be drawn as credible observations.
  const days={};
  for (const asset of ['BTC','ETH']) {
    const a=i.assets?.[asset];
    if (!a || !numeric(a.P0) || !Array.isArray(a.days) || a.days.length!==7)
      return refuse('INCOMPLETE_ASSET_ISSUANCE');
    const good=[];
    for (let k=1;k<=7;k++) {
      const d=a.days[k-1],range=d?.band?.range?.['0.8'],close=d?.band?.close?.['0.8'];
      if (d?.day!==k || !date(d.scored_from_utc) || !date(d.end_utc) ||
          !(Date.parse(d.end_utc)>Date.parse(d.scored_from_utc)) ||
          !Array.isArray(range) || !Array.isArray(close) ||
          range.length!==2 || close.length!==2 ||
          !numeric(range[0]) || !numeric(range[1]) || range[0]>=range[1] ||
          !numeric(close[0]) || !numeric(close[1]) || close[0]>=close[1])
        return refuse('INVALID_DAILY_BAND');
      good.push({day:k,range,close});
    }
    days[asset]=good;
  }
  // Source publication must precede the first scoring window, otherwise
  // an alleged prospective issue could have seen the outcome already.
  if (known > Math.min(...['BTC','ETH'].map(x => Date.parse(i.assets[x].days[0].scored_from_utc))))
    return refuse('LATE_FIRST_PUBLICATION');
  return {ok:true,week:i.week,issue_utc:i.issue_clock_utc,known_utc:src.first_in_main_utc,
    source_commit:src.first_in_main_commit,source_sha:src.sha256,issuance_sha:i.issuance_sha256,
    days,prices:{BTC:i.assets.BTC.P0,ETH:i.assets.ETH.P0}};
}

const copy = {
 da:{
  eyebrow:'TASK 2 / UAFHÆNGIG BENCHMARK',title:'Challenger A',
  intro:'En simpel volatilitetstest ved siden af Cycle Navigator, aldrig en erstatning for den officielle ugeprognose.',
  pending:'Afventer verificeret W47-udstedelse',
  unavailable:'Ingen godkendt, uforanderlig Challenger-udstedelse er publiceret i site-kilden. Derfor vises ingen konstruerede prisintervaller.',
  available:'Frossen forskningsprognose',month:'Udstedt',
  published:'Først på main',label:'7 dage · 80 % interval',range:'Dagens lav/høj',close:'Dagens slutkurs',
  footer:'SHADOW / INGEN HANDELSSIGNALER. Historiske W46-tal indgik i modelvalget og er ikke uafhængig bekræftelse. Officiel CN-graf og kilde forbliver uændret.',
  link:'Metode, kode og uafhængig review',source:'Fastlåst kilde',
  day:'Dag'
 },
 en:{
  eyebrow:'TASK 2 / INDEPENDENT BENCHMARK',title:'Challenger A',
  intro:'A simple volatility benchmark alongside Cycle Navigator, never a replacement for the official weekly forecast.',
  pending:'Awaiting verified W47 issuance',
  unavailable:'No approved, immutable Challenger issue is published to the site data source. No invented price bands are displayed.',
  available:'Frozen research forecast',month:'Issued',
  published:'First on main',label:'7 days · 80% interval',range:'Daily low/high',close:'Daily close',
  footer:'SHADOW / NO TRADING SIGNALS. W46 helped select this model and is not independent proof. The official CN chart and source are unchanged.',
  link:'Method, code and independent review',source:'Pinned source',
  day:'Day'
 }
};
const formatMoney=(n,asset,lang)=>new Intl.NumberFormat(lang==='en'?'en-US':'da-DK',
 {minimumFractionDigits:asset==='BTC'?0:2,maximumFractionDigits:asset==='BTC'?0:2}).format(n);
const stamp=s=>s ? s.slice(0,16).replace('T',' ')+' UTC':'—';
const element=(tag,className,text)=>{
 const e=document.createElement(tag);
 if(className)e.className=className;
 if(text!=null)e.textContent=text;
 return e;
};
export function mountChallengerA(graphPanel,getLang=()=>document.documentElement.lang==='en'?'en':'da',
  load=()=>fetch(DATA_URL,{cache:'no-store',credentials:'same-origin'})) {
 if (!graphPanel || graphPanel.querySelector('#cn-challenger-a')) return null;
 const shell=element('section','cn-challenger-a');
 shell.id='cn-challenger-a';shell.setAttribute('aria-labelledby','cn-challenger-a-title');
 const top=element('div','cn-challenger-a-top');
 const lead=element('div','cn-challenger-a-lead');
 const kicker=element('small','cn-challenger-a-eyebrow');
 const title=element('h3',null,'Challenger A'); title.id='cn-challenger-a-title';
 lead.append(kicker,title);
 const badge=element('span','cn-challenger-a-badge','SHADOW');
 top.append(lead,badge);
 const intro=element('p','cn-challenger-a-intro');
 const status=element('div','cn-challenger-a-status');
 status.setAttribute('role','status');
 const heading=element('strong');
 const detail=element('p');
 status.append(heading,detail);
 const data=element('div','cn-challenger-a-data');data.hidden=true;
 const meta=element('p','cn-challenger-a-meta');
 const grids=element('div','cn-challenger-a-assets');
 data.append(meta,grids);
 const foot=element('p','cn-challenger-a-footnote');
 const link=element('a','cn-challenger-a-link');
 link.href=SOURCE_URL;link.target='_blank';link.rel='noopener noreferrer';
 shell.append(top,intro,status,data,foot,link);
 // The existing historical Graph B stays above; History stays below.
 const history=graphPanel.querySelector('.cn-graph-history-entry');
 graphPanel.insertBefore(shell,history||null);
 let validated=null,attempted=false;
 const paint=()=>{
  const lang=getLang()==='en'?'en':'da',t=copy[lang];
  kicker.textContent=t.eyebrow;title.textContent=t.title;intro.textContent=t.intro;
  foot.textContent=t.footer;link.textContent=t.link;
  status.hidden=!!validated;data.hidden=!validated;
  if (!validated) {heading.textContent=t.pending;detail.textContent=t.unavailable;return}
  meta.textContent=t.available+' · '+validated.week+' · '+t.month+': '+
    stamp(validated.issue_utc)+' · '+t.published+': '+stamp(validated.known_utc);
  grids.replaceChildren();
  for(const asset of ['BTC','ETH']){
   const article=element('article','cn-challenger-a-asset');
   const assetHeading=element('h4',null,asset);
   const sub=element('p','cn-challenger-a-asset-sub',t.label);
   const table=element('table','cn-challenger-a-table');
   const header=document.createElement('thead'),hr=document.createElement('tr');
   for(const label of [t.day,t.range,t.close])
    hr.append(element('th',null,label));
   header.append(hr);table.append(header);
   const body=document.createElement('tbody');
   for(const d of validated.days[asset]){
    const tr=document.createElement('tr');
    const f=arr=>arr.map(n=>formatMoney(n,asset,lang)).join(' – ');
    for(const value of [String(d.day),f(d.range),f(d.close)])
     tr.append(element('td',null,value));
    body.append(tr);
   }
   table.append(body);article.append(assetHeading,sub,table);grids.append(article);
  }
  let source=grids.querySelector('.cn-challenger-a-provenance');
  if (!source) {source=element('p','cn-challenger-a-provenance');data.append(source)}
  source.textContent=t.source+': '+validated.source_commit.slice(0,12)+
    ' · SHA256 '+validated.issuance_sha.slice(0,16)+'…';
 };
 const refresh=async()=>{
  if(attempted)return;
  attempted=true;
  try{
   const r=await load();
   if(!r || !r.ok)return;
   const value=validateChallengerPublic(await r.json());
   if(value.ok)validated=value;
  }catch{/* Missing, stale or malformed source remains unavailable. */}
  finally{paint()}
 };
 paint();
 return {element:shell,refresh,paint};
}
