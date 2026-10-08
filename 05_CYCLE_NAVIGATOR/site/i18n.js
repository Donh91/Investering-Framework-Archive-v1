/* Local, reversible presentation translation. Frozen source bytes stay untouched. */
(() => {
  'use strict';
  const storageKey='cn-language';
  let language='en';try{language=localStorage.getItem(storageKey)|| (navigator.language?.toLowerCase().startsWith('da')?'da':'en');}catch{}
  if(!['da','en'].includes(language))language='en';
  const originals=new WeakMap(),attrs=new WeakMap();let catalog={},baseCatalog={},dynamicCatalog={},phrases=[],observer=null,pending=false;
  const norm=s=>s.replace(/\s+/g,' ').trim();
  const translate=text=>{
    if(language==='en')return text;
    const key=norm(text),exact=catalog[key];
    if(key.endsWith('…')){const matches=Object.keys(catalog).filter(k=>k.startsWith(key.slice(0,-1)));if(matches.length){const full=catalog[matches[0]],short=full.length>key.length?full.slice(0,key.length-1).replace(/\s+\S*$/,'')+'…':full;return text.replace(text.trim(),short);}}
    if(exact!==undefined)return text.replace(text.trim(),exact);
    // Only complete, curated phrase boundaries. Numbers, identifiers and forecast values are untouched.
    let out=text;for(const [en,da,re]of phrases)out=out.replace(re,da);
    return out;
  };
  function apply(){
    pending=false;observer?.disconnect();
    const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;
    while(n=walker.nextNode()){
      if(n.parentElement?.closest('script,style,.fw-canvas,[data-no-translate],.language-toggle'))continue;
      const prior=originals.get(n);let source=prior&&n.nodeValue===prior.translated?prior.source:n.nodeValue;
      const translated=translate(source);originals.set(n,{source,translated});if(n.nodeValue!==translated)n.nodeValue=translated;
    }
    document.querySelectorAll('[aria-label],[title],[placeholder]').forEach(el=>{
      if(el.closest('.fw-canvas,.language-toggle,[data-no-translate]'))return;
      const saved=attrs.get(el)||{};for(const name of ['aria-label','title','placeholder']){
        if(!el.hasAttribute(name))continue;const value=el.getAttribute(name),old=saved[name],source=old&&old.translated===value?old.source:value,translated=translate(source);
        saved[name]={source,translated};if(value!==translated)el.setAttribute(name,translated);
      }attrs.set(el,saved);
    });
    document.documentElement.lang=language;
    document.querySelectorAll('[data-language]').forEach(b=>b.setAttribute('aria-pressed',b.dataset.language===language));
    observer?.observe(document.body,{childList:true,subtree:true,characterData:true,attributes:true,attributeFilter:['aria-label','title','placeholder']});
  }
  function schedule(){if(!pending){pending=true;queueMicrotask(apply);}}
  function setLanguage(next){if(!['da','en'].includes(next))return;language=next;try{localStorage.setItem(storageKey,next);}catch{}apply();document.dispatchEvent(new CustomEvent('cn-language-change',{detail:{language:next}}));}
  function registerTranslations(rows){
    dynamicCatalog={};
    for(const row of Array.isArray(rows)?rows:[]){
      if(!row||typeof row.en!=='string'||typeof row.da!=='string')continue;
      const raw=norm(row.en),da=norm(row.da);
      const common=raw.replace(/\bW(\d+)\b/g,'week $1').replace(/MASTER MONDAY/gi,'weekly review').replace(/ETHBTC|ETH\/BTC/gi,'Ethereum vs Bitcoin').replace(/BREADTH/gi,'market participation').replace(/_/g,' ').replace(/\s+/g,' ');
      const compass=common.replace(/ETH-relative/gi,'Ethereum-relative').replace(/microstructure/gi,'market structure').replace(/\bgoverned\b/gi,'verified').replace(/\bcanonical\b/gi,'confirmed');
      const path=common.replace(/ETH-relative/gi,'Ethereum-vs-Bitcoin').replace(/settled ETH ETF flows/gi,'Ethereum ETF flows').replace(/mixed microstructure/gi,'mixed short-term market structure').replace(/microstructure/gi,'short-term market structure');
      for(const key of [raw,common,compass,path]){dynamicCatalog[key]=da;dynamicCatalog[key[0]?.toLowerCase()+key.slice(1)]=da;}
    }
    catalog={...dynamicCatalog,...baseCatalog};schedule();
  }
  window.CNI18n={registerTranslations,get language(){return language;},translate,setLanguage,apply};
  function boot(){
    const head=document.querySelector('.site-header,.topline');if(!head)return;
    const toggle=document.createElement('div');toggle.className='language-toggle';toggle.setAttribute('role','group');toggle.setAttribute('aria-label','Language / Sprog');
    toggle.innerHTML='<button type="button" data-language="da" lang="da" aria-label="Dansk">DA</button><button type="button" data-language="en" lang="en" aria-label="English">ENG</button>';
    head.append(toggle);toggle.querySelectorAll('button').forEach(b=>b.onclick=()=>setLanguage(b.dataset.language));
    observer=new MutationObserver(records=>{if(records.some(r=>{const el=r.target.nodeType===1?r.target:r.target.parentElement;return !el?.closest('.fw-canvas,[data-no-translate],.language-toggle');}))schedule();});apply();
    fetch('./i18n-da.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(r.status);return r.json();}).then(data=>{
      baseCatalog=data.exact||{};catalog={...dynamicCatalog,...baseCatalog};phrases=Object.entries(data.phrases||{}).sort((a,b)=>b[0].length-a[0].length).map(([en,da])=>[en,da,new RegExp('(?<![A-Za-z])'+en.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+'(?![A-Za-z])','g')]);apply();document.dispatchEvent(new CustomEvent('cn-language-change',{detail:{language}}));
    }).catch(e=>console.warn('CN translation catalog unavailable',e));
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
