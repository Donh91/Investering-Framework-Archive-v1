/* Kompas Pro 2.0 · visible Swing Compass, presentation only.
 * Official general horizons and capitalization NOW rows are independent:
 * never cross-join them into purported asset-class forecasts or actions.
 * MICROCAPS is a broad official class, NOT proof of <USD1m membership.
 */
const HORIZONS=[
 {key:'NEXT_1_3D',da:'1–3 dage',en:'1–3 days'},
 {key:'NEXT_5_7D',da:'5–7 dage',en:'5–7 days'},
 {key:'NEXT_2_3W',da:'2–3 uger',en:'2–3 weeks'}
];
const GROUPS=[
 {key:'LARGE_CAPS',da:'Large caps',en:'Large caps',size:'≥ $10B'},
 {key:'MID_CAPS',da:'Mid caps',en:'Mid caps',size:'$1B–10B'},
 {key:'SMALL_CAPS',da:'Small caps',en:'Small caps',size:'$100M–1B'},
 {key:'MICROCAPS',da:'Microcaps',en:'Microcaps',size:'< $100M'}
];
const DIRECTIONS=new Set(['UP','DOWN','MIXED','SIDEWAYS']);
const ACTIONS=new Set(['HOLD','WAIT','HARD_WAIT','UNAVAILABLE','WATCH','PREPARE','PREPARE_BUY','BUY','PREPARE_SELL','REDUCE','SELL']);
const tr=(lang,da,en)=>lang==='en'?en:da;
const labelDirection=(v,lang)=>({
 UP:tr(lang,'Stigende','Rising'),DOWN:tr(lang,'Faldende','Falling'),
 MIXED:tr(lang,'Blandet','Mixed'),SIDEWAYS:tr(lang,'Sideværts','Sideways')
})[v]||tr(lang,'Ingen vurdering','No reading');
const labelAction=(v,lang)=>({
 HOLD:tr(lang,'Behold','Hold'),WAIT:tr(lang,'Afvent','Wait'),
 HARD_WAIT:tr(lang,'Skærpet afvent','Strict wait'),
 WATCH:tr(lang,'Overvåg','Watch'),PREPARE:tr(lang,'Forbered','Prepare'),
 PREPARE_BUY:tr(lang,'Forbered køb','Prepare buy'),BUY:tr(lang,'Køb','Buy'),
 PREPARE_SELL:tr(lang,'Forbered reduktion','Prepare trim'),
 REDUCE:tr(lang,'Reducer','Reduce'),SELL:tr(lang,'Sælg','Sell')
})[v]||tr(lang,'Ingen vurdering','No reading');

export function readSwingRotation(view,official,{lang='da'}={}){
 const bound=view?.compass?.state==='FRESH'
  &&view.compass.permit_path_live_gates===true
  &&official?.contract==='PUBLIC_COMPASS_PROJECTION_v1'
  &&official.data_status==='OK'
  &&typeof official.compass_id==='string'&&official.compass_id.length>0
  &&official.compass_id===view.compass.compass_id
  &&official.action_now===view.compass.action_now
  &&official.action_now!=='UNAVAILABLE';
 const valid=Boolean(bound);
 const horizons=HORIZONS.map(h=>{
  const src=valid?official.horizons?.[h.key]:null;
  const dir=src?.expected_direction;
  return {
   key:h.key,label:lang==='en'?h.en:h.da,
   direction:DIRECTIONS.has(dir)?dir:'UNAVAILABLE',
   text:DIRECTIONS.has(dir)?labelDirection(dir,lang):tr(lang,'Afventer kilde','Awaiting source'),
   source:'OFFICIAL_MARKET_WIDE_ONLY',
   // This reading is common market context. There is NO segment×horizon forecast.
   segmentForecastIssued:false
  };
 });
 const ladder=valid&&Array.isArray(official.capitalization_ladder)?official.capitalization_ladder:[];
 const rows=GROUPS.map(g=>{
  const matches=ladder.filter(x=>x?.segment===g.key);
  const raw=matches.length===1&&matches[0]?.action===matches[0]?.status
   &&ACTIONS.has(matches[0]?.status)?matches[0].status:'UNAVAILABLE';
  return {
   key:g.key,label:lang==='en'?g.en:g.da,sizeReference:g.size,
   sourceAction:raw,nowLabel:labelAction(raw,lang),
   verified:valid&&raw!=='UNAVAILABLE',
   isMicro:g.key==='MICROCAPS',
   // Not a token-level under-USD1m or FDV classification.
   under1mSignalVerified:false,
   future: HORIZONS.map(h=>({key:h.key,status:'NOT_ISSUED'}))
  };
 });
 return {contract:'CN_SWING_ROTATION_READBACK_V1',valid,
  issuedAt:valid?official.issued_at_utc:null,sourceId:valid?official.compass_id:null,
  horizons,rows,sectorHorizonStatus:'NOT_ISSUED',
  subMillionStatus:'RESEARCH_ONLY_NOT_SEGMENT_PROJECTION'};
}

const make=(tag,className,content)=>{
 const el=document.createElement(tag);
 if(className)el.className=className;
 if(content!==undefined)el.textContent=content;
 return el;
};
export function renderSwingRotation(container,model,{lang='da'}={}){
 if(!container)return;
 container.replaceChildren();
 container.dataset.sourceState=model?.valid?'OFFICIAL_NOW_CONTEXT_ONLY':'UNAVAILABLE';
 const t=(da,en)=>tr(lang,da,en);
 const heading=make('div','swing-heading');
 const title=make('div','');
 title.append(make('span','swing-eyebrow',t('KOMPAS PRO 2.0 / SWING OVERBLIK','COMPASS PRO 2.0 / SWING OVERVIEW')),
              make('h2','',t('Marked og kapitalgrupper','Market and capitalization groups')));
 heading.append(title,make('span','swing-source',model?.valid?
  t('Officielt kompas · aktuelt','Official Compass · current'):
  t('Kilden mangler eller er udløbet','Source missing or expired')));
 container.append(heading);
 const context=make('div','swing-horizons');
 for(const h of model?.horizons||[]){
  const cell=make('div','swing-horizon swing-horizon-'+h.direction.toLowerCase());
  cell.append(make('span','swing-label',h.label),
    make('strong','',h.text),
    make('small','',t('Hele markedet','Whole market')));
  context.append(cell);
 }
 container.append(context);
 const ledger=make('div','swing-ledger');
 const grid=make('div','swing-grid');
 grid.setAttribute('role','table');
 grid.setAttribute('aria-label',t('Officiel status nu per kapitalgruppe; fremtidige gruppesignaler er endnu ikke udstedt',
 'Official current posture per capitalization group; future class signals are not issued'));
 const header=make('div','swing-grid-header');
 header.setAttribute('role','row');
 for(const text of [t('Kapitalgruppe','Capital group'),t('Status nu','Now'),
  ...HORIZONS.map(h=>lang==='en'?h.en:h.da)]){
  const c=make('div','swing-colhead',text);c.setAttribute('role','columnheader');header.append(c);
 }
 grid.append(header);
 for(const row of model?.rows||[]){
  const line=make('div','swing-grid-row'+(row.isMicro?' swing-micro':''));
  line.setAttribute('role','row');
  const label=make('div','swing-group');
  label.setAttribute('role','rowheader');
  label.append(make('strong','',row.label),make('small','',row.sizeReference));
  if(row.isMicro) label.append(make('small','swing-micro-cohort',t('Alpha Lab: $200k–2m undersøges','Alpha Lab: $200k–2m proposed')));
  line.append(label);
  const status=make('div','swing-now');
  const text=make('strong','swing-action swing-action-'+row.sourceAction.toLowerCase().replaceAll('_','-'),row.nowLabel);
  status.append(text);
  status.setAttribute('role','cell');line.append(status);
  for(const unused of row.future){
   const col=make('div','swing-unknown',t('Afventer','Pending'));
   col.setAttribute('role','cell');
   col.title=t('Ingen kildeudstedt prognose for dette segment og denne periode',
     'No source-issued forecast for this group and this horizon');
   line.append(col);
  }
  grid.append(line);
 }
 ledger.append(grid);
 container.append(ledger);
 container.append(make('p','swing-explainer',
  t('Øverst: officiel markedsretning for 1–3 dage, 5–7 dage og 2–3 uger. Nederst: hver kapitalgruppes aktuelle status, ikke en prognose. De 12 gruppespecifikke fremtidssignaler er ikke udstedt. Størrelsesintervallerne er kun branchemæssige pejlemærker, ikke kildens officielle grænser. Alpha Lab undersøger cyklusafhængige filtergrænser fra bl.a. $200k–2m, men ingen sådan model er valideret. Memes har fortsat eget signal.',
    'Top: official market-wide direction for 1–3 days, 5–7 days and 2–3 weeks. Below: each group’s current status, not a forecast. The 12 group-specific forward signals are not issued. Size ranges are industry references, not source-owner thresholds. Alpha Lab is researching cycle-dependent selection bands including $200k–2m; no such model is validated. Memes remains independent.')));
}
