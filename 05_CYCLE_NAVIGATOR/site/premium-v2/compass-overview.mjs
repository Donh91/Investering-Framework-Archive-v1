/**
 * Public Kompas overview, presentation only, exact official source fields.
 * Direction glyphs are separate windows, never a continuous price path.
 * Bull/Bear 0-10 ticks are coarse evidence, NOT probabilities.
 */
import {currentCompass,sourceTranslation} from './compass-reader.mjs';

const periods=[
 {id:'NEXT_1_3D',balance:'1_3d',da:'1–3 dage',en:'1–3 days'},
 {id:'NEXT_5_7D',balance:'5_7d',da:'5–7 dage',en:'5–7 days'},
 {id:'NEXT_2_3W',balance:'2_3w',da:'2–3 uger',en:'2–3 weeks'}
];
const directions={
 UP:{arrow:'↗',da:'Stigende',en:'Rising'},
 DOWN:{arrow:'↘',da:'Faldende',en:'Falling'},
 MIXED:{arrow:'↗/↘',da:'Blandet',en:'Mixed'},
 SIDEWAYS:{arrow:'→',da:'Sideværts',en:'Sideways'},
 LEAN_BEARISH:{arrow:'↘ ?',da:'Hældning mod fald',en:'Leaning down'},
 LEAN_BULLISH:{arrow:'↗ ?',da:'Hældning mod stigning',en:'Leaning up'}
};
const postures={
 HOLD:{da:'Behold eksisterende',en:'Hold existing'},
 WAIT:{da:'Afvent',en:'Wait'},
 HOLD_WAIT:{da:'Afvent',en:'Wait'},
 HARD_WAIT:{da:'Skærpet afvent',en:'Strict wait'},
 NO_EDGE:{da:'Ingen dokumenteret fordel',en:'No proven edge'},
 ABSTAIN:{da:'Ingen ny handling',en:'No new action'}
};
const tr=(lang,da,en)=>lang==='en'?en:da;
const readable=(map,v,lang)=>map[v]?.[lang==='en'?'en':'da']||tr(lang,'Ikke fastlagt','Not established');
const empty=(lang)=>({arrow:'?',text:tr(lang,'Ingen aktuel vurdering','No current reading'),source:'UNAVAILABLE'});
const validTick=n=>Number.isInteger(n)&&n>=0&&n<=10;

export function directionVisual(state,lang='da'){
 const item=directions[state];
 return item?{arrow:item.arrow,text:readable(directions,state,lang),source:state}:empty(lang);
}

function sourceText(raw,latest,lang){
 const out=sourceTranslation(raw,latest,lang);
 if(!out.text)return {text:tr(lang,'Ingen dokumenteret forklaring','No documented explanation'),translated:true};
 const text=out.text.length<=185?out.text:out.text.slice(0,182).replace(/\s+\S*$/,'')+'…';
 return {text,translated:out.translated};
}

function officialEvidence(compass,key){
 const b=compass?.bull_bear_scale;
 const r=b?.horizons?.[key];
 if(b?.contract!=='OFFICIAL_COMPASS_BULL_BEAR_DISPLAY_v1'||
    b?.owner!=='OFFICIAL_COMPASS'||b?.authority?.probability_model!==false||
    b?.authority?.site_synthesis_allowed!==false||
    b?.resolution!=='COARSE_CATEGORICAL_DIRECTION'||
    r?.status!=='OK'||!validTick(r?.bull)||!validTick(r?.bear)||
    r.bull+r.bear!==10)return null;
 return {bull:r.bull,bear:r.bear};
}

export function publicOverview({latest,compass,view,lang='da',now=Date.now()}){
 const valid=currentCompass({compass,view,now});
 const nowReading=valid?directionVisual(compass.market_now?.directional_state,lang):empty(lang);
 const twelve=valid?compass.horizons?.NEXT_12H:null;
 // The owner calls this CURRENT MOMENTUM and not a future 12-24h forecast.
 const past12=valid&&twelve?nowReading:empty(lang);
 const cards=periods.map(p=>{
  const h=valid?compass.horizons?.[p.id]:null;
  const visual=h?directionVisual(h.expected_direction,lang):empty(lang);
  const evidence=h?officialEvidence(compass,p.balance):null;
  return {
   id:p.id,title:lang==='en'?p.en:p.da,arrow:visual.arrow,
   direction:visual.text,sourceDirection:visual.source,
   position:valid?readable(postures,h?.action_posture,lang):tr(lang,'Ingen aktuel handling','No current action'),
   evidence,summary:valid?sourceText(h?.expected_path,latest,lang):
     {text:tr(lang,'Afventer verificeret Kompas','Awaiting verified Compass'),translated:true}
  };
 });
 return {valid,observed12:past12,cards,issued:valid?compass.issued_at_utc:null};
}

const caps=[
 ['BTC','BTC'],['ETH','ETH'],['LARGE_CAPS','Large caps'],
 ['MID_CAPS','Mid caps'],['SMALL_CAPS','Small caps'],
 ['MICROCAPS','Microcaps'],['MEMES','Memes']
];
const allowed=new Set(['HOLD','WAIT','HARD_WAIT','UNAVAILABLE','WATCH','PREPARE','PREPARE_BUY','BUY','PREPARE_SELL','REDUCE','SELL']);
const statusWord=(status,lang)=>({
 HOLD:tr(lang,'Behold eksisterende','Hold existing'),
 WAIT:tr(lang,'Afvent','Wait'),
 HARD_WAIT:tr(lang,'Skærpet afvent','Strict wait'),
 UNAVAILABLE:tr(lang,'Ingen kildevurdering','No source stance'),
 WATCH:tr(lang,'Overvåg','Watch'),
 PREPARE:tr(lang,'Forbered','Prepare'),
 PREPARE_BUY:tr(lang,'Forbered køb','Prepare buy'),
 BUY:tr(lang,'Købssignal','Buy signal'),
 PREPARE_SELL:tr(lang,'Forbered reduktion','Prepare reduction'),
 REDUCE:tr(lang,'Reducer','Reduce'),
 SELL:tr(lang,'Salgssignal','Sell signal')
})[status]||tr(lang,'Ikke fastlagt','Not established');

export function readRotation({compass,view,lang='da',now=Date.now()}){
 if(!currentCompass({compass,view,now}))return {valid:false,rows:[]};
 const ladder=compass.capitalization_ladder;
 if(!Array.isArray(ladder)||ladder.length!==caps.length)return {valid:false,rows:[]};
 const rows=[];
 for(const [key,name] of caps){
  const matches=ladder.filter(x=>x?.segment===key);
  if(matches.length!==1||!allowed.has(matches[0].action)||
     matches[0].action!==matches[0].status)return {valid:false,rows:[]};
  rows.push({id:key,name,sourceAction:matches[0].action,
    stance:statusWord(matches[0].action,lang)});
 }
 return {valid:true,rows};
}

/** This is a dictionary, NOT an authorized sequential trading state machine. */
export const POSITION_GUIDE=[
 ['WAIT','Afvent','Ingen ny handel er bekræftet; kurserne kan stadig flytte sig.',
          'Wait','No new trade is confirmed; prices can still move.'],
 ['WATCH','Overvåg','Tidlige tegn observeres. Ikke en ordre.',
          'Watch','Early signs are being observed. Not an order.'],
 ['PREPARE','Forbered','Betingelser undersøges; ingen handelstilladelse.',
          'Prepare','Conditions are being assessed; no trade permission.'],
 ['PREPARE_BUY','Forbered køb','Flere betingelser skal fortsat bekræftes.',
          'Prepare buy','Further conditions still require confirmation.'],
 ['BUY','Køb','Kun et selvstændigt godkendt og gyldigt købssignal.',
          'Buy','Only a separately approved, current buy signal.'],
 ['HOLD','Behold','Kun relevant for eksisterende positioner; ikke køb.',
          'Hold','Applies to existing holdings; not a buy.'],
 ['REDUCE','Reducer','Kun hvis et godkendt risiko-/salgsspor faktisk udsteder reduktion.',
          'Reduce','Only if an approved risk/sell lane actually issues a reduction.'],
 ['SELL','Sælg/reducer','Kun hvis en godkendt kilde faktisk udsteder signalet.',
          'Sell/trim','Only if an approved source actually issues it.']
];
