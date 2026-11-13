import {playOnce} from './play-once.mjs';
/**
 * SITE #1578. Only the UI: four accessible public panels, no new market owner.
 * Fail open to ordinary anchor navigation when the source DOM is incomplete.
 */
const views = [
  ['compass','compass-pro'],
  ['graph','variant-panel'],
  ['path','official-path-view'],
  ['proof','proof-explorer']
];
const nav = document.querySelector('nav.premium-entry-navigation');
const nodes = views.map(([key,id]) => ({
  key, id,
  link: nav?.querySelector('a[data-premium-nav="'+key+'"]'),
  panel: document.getElementById(id)
}));
if (nav && nodes.every(x => x.link && x.panel)) {
  // Preserve the old-version archive link under source/methodology, not as a tab.
  const archive = nav.querySelector('[data-premium-nav="official"]');
  const footer = document.querySelector('.premium-meta-links');
  if (archive && footer) footer.append(archive);
  if (archive && !footer) archive.remove();
  nav.setAttribute('role','tablist');
  nav.setAttribute('aria-label','Vælg markedsvisning');
  for (const x of nodes) {
    nav.append(x.link);
    x.link.setAttribute('role','tab');
    x.link.id = 'cn-site-tab-'+x.key;
    x.link.setAttribute('aria-controls',x.id);
    x.panel.setAttribute('role','tabpanel');
    x.panel.setAttribute('aria-labelledby',x.link.id);
  }
  // Do not edit original Graph B markup. A single, source-neutral archive link
  // is appended inside the existing weekly graph tab after client initialization.
  const graphPanel=nodes.find(x=>x.key==='graph')?.panel;
  if(graphPanel&&!document.getElementById('cn-graph-history-link')){
    const entry=document.createElement('section');
    entry.className='cn-graph-history-entry';
    entry.setAttribute('aria-labelledby','cn-graph-history-title');
    const description=document.createElement('div');
    const heading=document.createElement('strong');
    heading.id='cn-graph-history-title';
    heading.textContent='Grafhistorik';
    const note=document.createElement('p');
    note.id='cn-graph-history-note';
    note.textContent='Fra uge 45 (2026). Faktisk BTC-kurs fra verificerede timer; kun kildeudstedte dagsprognoser vises som blå kurve.';
    description.append(heading,note);
    const link=document.createElement('a');
    link.id='cn-graph-history-link';
    link.href='/Investering-Framework-Archive-v1/graph-history/';
    link.textContent='Se detaljeret grafhistorik';
    // Reuse the already-published immutable-source History renderer in compact
    // mode. No second chart model, no reforecast, no copied market data.
    const frame=document.createElement('iframe');
    frame.id='cn-graph-history-preview';
    frame.src='/Investering-Framework-Archive-v1/graph-history/?embed=1';
    frame.title='Grafhistorik · faktiske BTC-kurser og originale ugeprognoser';
    frame.loading='lazy';
    frame.referrerPolicy='same-origin';
    // The preview is same-origin. Match the verified source document's actual
    // height so narrow iPhones never show a nested vertical scrollbar.
    // No data is copied into the parent or used to infer any forecast.
    const fitHistory=()=>{
      try{
        const doc=frame.contentDocument;
        if(!doc?.body)return;
        const natural=Math.max(doc.body.scrollHeight,doc.documentElement.scrollHeight);
        if(Number.isFinite(natural)&&natural>0)
          frame.style.height=Math.ceil(natural+6)+'px';
      }catch{/* Source-only link remains accessible if iframe is unavailable. */}
    };
    frame.addEventListener('load',()=>{
      fitHistory();
      try{
        if(frame.contentWindow?.ResizeObserver)
          new frame.contentWindow.ResizeObserver(fitHistory).observe(frame.contentDocument.body);
      }catch{/* Keep fixed-height fallback if same-origin inspection is denied. */}
    });
    entry.append(description,frame,link);
    graphPanel.append(entry);
  }
  const translations = {
    da:{compass:'Kompas',graph:'Ugens prognose',path:'Markedscyklus',proof:'Resultater'},
    en:{compass:'Compass',graph:'Weekly forecast',path:'Market cycle',proof:'Results'}
  };
  const lang = () => document.querySelector('[data-lang][aria-pressed="true"]')?.getAttribute('data-lang') === 'en' ? 'en' : 'da';
  // Keep the selected tab discoverable when browser zoom makes the rail scroll.
  // Change only the rail's horizontal position, never the page scroll or tab model.
  const revealSelected = link => {
    if (!link || nav.scrollWidth <= nav.clientWidth + 1) return;
    const rail = nav.getBoundingClientRect(), item = link.getBoundingClientRect();
    const padding = 8;
    if (item.left < rail.left + padding)
      nav.scrollLeft -= rail.left + padding - item.left;
    else if (item.right > rail.right - padding)
      nav.scrollLeft += item.right - (rail.right - padding);
  };
  const paintLabels = () => {
    const compact=window.matchMedia('(max-width: 440px)').matches;
    const names={...translations[lang()]};
    if(compact){
      names.graph=lang()==='en'?'Forecast':'Prognose';
      names.path=lang()==='en'?'Cycle':'Cyklus';
    }
    for (const x of nodes) if(x.link.textContent!==names[x.key]) x.link.textContent=names[x.key];
    // This link stays inside the weekly graph panel, never becomes a fifth tab.
    const historyCopy=lang()==='en'?{title:'Graph history',note:'One continuous BTC price line with week boundaries. Green = observed prices; dashed blue = original source-issued weekly forecast. Issue time and any same-day correction are shown in the detailed history.',link:'Explore detailed history'}:
      {title:'Grafhistorik',note:'Én sammenhængende BTC-kurve med ugeadskillelser. Grøn = faktiske kurser, stiplet blå = original kildeudstedt ugeprognose. Udstedelsestid og evt. korrektion samme dag står i den detaljerede grafhistorik.',link:'Se detaljeret grafhistorik'};
    const preview=document.getElementById('cn-graph-history-preview');
    if(preview)preview.title=lang()==='en'?'Historical BTC prices and original weekly forecasts':'Grafhistorik med faktiske BTC-kurser og originale ugeprognoser';
    for(const [id,value] of [['cn-graph-history-title',historyCopy.title],['cn-graph-history-note',historyCopy.note],['cn-graph-history-link',historyCopy.link]]){
      const element=document.getElementById(id);
      if(element&&element.textContent!==value)element.textContent=value;
    }
    const navName=lang()==='en'?'Choose market view':'Vælg markedsvisning';
    if(nav.getAttribute('aria-label')!==navName)nav.setAttribute('aria-label',navName);
    const active=nodes.find(x=>x.link.getAttribute('aria-selected')==='true');
    if(active)revealSelected(active.link);
  };
  const fromHash = () => nodes.find(x => '#'+x.id === location.hash)?.key;
  const activate = (key, changeUrl=false) => {
    const selected = nodes.find(x => x.key === key) || nodes[0];
    for (const x of nodes) {
      const current = x === selected;
      x.panel.hidden = !current;
      x.link.setAttribute('aria-selected',String(current));
      x.link.tabIndex = current ? 0 : -1;
      if (current) x.link.setAttribute('aria-current','page');
      else x.link.removeAttribute('aria-current');
    }
    document.body.dataset.cnSiteView=selected.key;
    // v2.7 first-visit motion (once per visit per tab; reveal only, end state unchanged).
    if (selected.key === 'compass') playOnce('cnKompasEntered', selected.panel, 'cn-kompas-enter');
    if (selected.key === 'graph') playOnce('cnPrognoseEntered', selected.panel, 'cn-prognose-enter');
    if (selected.key === 'path') playOnce('cnCyklusEntered', selected.panel, 'cn-cyklus-enter');
    revealSelected(selected.link);
    if (changeUrl) history.pushState({cnSiteView:selected.key},'', '#'+selected.id);
  };
  for (const x of nodes) x.link.addEventListener('click',event => {
    // Modified clicks retain ordinary URL behavior, including opening a new tab.
    if(event.metaKey||event.ctrlKey||event.shiftKey||event.altKey) return;
    event.preventDefault();
    activate(x.key,true);
    window.scrollTo({top:0,behavior:'instant'});
  });
  nav.addEventListener('keydown',event => {
    if(!['ArrowRight','ArrowLeft','Home','End'].includes(event.key))return;
    const i = nodes.findIndex(x=>x.link===document.activeElement);
    if(i<0)return;
    event.preventDefault();
    const next = event.key==='Home'?0:event.key==='End'?nodes.length-1:
      (i+(event.key==='ArrowRight'?1:-1)+nodes.length)%nodes.length;
    activate(nodes[next].key,true);
    nodes[next].link.focus();
  });
  window.addEventListener('popstate',()=>activate(fromHash()||'compass'));
  window.addEventListener('hashchange',()=>activate(fromHash()||'compass'));
  document.querySelectorAll('[data-lang]').forEach(b=>b.addEventListener('click',()=>{
    window.setTimeout(paintLabels,0);
  }));
  paintLabels();
  activate(fromHash()||'compass');
  document.body.classList.add('cn-tabbed-ui');
  // Existing Graph/PRO owners also update navigation copy on source or language
  // repaint. Re-apply only when the words differ, avoiding observer loops.
  new MutationObserver(paintLabels).observe(nav,{subtree:true,childList:true,characterData:true});
  window.addEventListener('resize',paintLabels);
}

/* CN SITE v2.2b · Kompas horizon strip: inline rationale on demand, quiet state for an
 * unissued horizon. Presentation only: reads text the PRO runtime already painted,
 * never changes it, never navigates. Fails open (rationale stays reachable). */
(() => {
  const cards = [...document.querySelectorAll('#compass-pro .cn-horizon-card')];
  if (!cards.length) return;
  const en = () => (document.documentElement.lang || 'da').startsWith('en');
  const paint = () => {
    for (const card of cards) {
      const arrow = card.querySelector('.cn-horizon-arrow')?.textContent.trim();
      const quiet = arrow === '?' || arrow === '';
      if (card.dataset.quiet !== String(quiet)) card.dataset.quiet = String(quiet);
      const button = card.querySelector('.cn-horizon-more');
      if (!button) continue;
      const open = button.getAttribute('aria-expanded') === 'true';
      const label = open ? (en() ? 'Hide rationale' : 'Skjul begrundelse') : (en() ? 'Rationale' : 'Begrundelse');
      if (button.textContent !== label) button.textContent = label;
    }
    const title = document.getElementById('cn-explain-title');
    const words = en() ? 'All 14 horizons, explanation and sources' : 'Alle 14 horisonter, forklaring og kilder';
    if (title && title.textContent !== words) title.textContent = words;
  };
  for (const card of cards) {
    const button = card.querySelector('.cn-horizon-more');
    if (!button) continue;
    button.addEventListener('click', () => {
      const open = button.getAttribute('aria-expanded') !== 'true';
      button.setAttribute('aria-expanded', String(open));
      card.dataset.expanded = String(open);
      paint();
    });
  }
  paint();
  const compass = document.getElementById('compass-pro');
  if (compass) new MutationObserver(paint).observe(compass, {subtree:true, childList:true, characterData:true});
  document.addEventListener('cn:languagechange', paint);
})();

/* CN SITE v2.3 · Markedscyklus timeline: one reveal on first view. Presentation only:
 * reads the rail the PATH runtime painted, never changes its text or data, never fetches,
 * never draws progress (v2.3-final honesty fix). Fails open (static final state). */
(() => {
  const view = document.getElementById('official-path-view');
  const rail = document.getElementById('premium-path-rail');
  if (!view || !rail || typeof IntersectionObserver !== 'function') return;
  const reduce = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : {matches:true};
  let started = false;
  const start = () => {
    if (started || !rail.querySelector('.path-node') || !rail.getClientRects().length) return;
    started = true;
    if (reduce.matches) { rail.dataset.cnReveal = 'done'; return; }
    rail.dataset.cnReveal = 'run';
    window.setTimeout(() => { rail.dataset.cnReveal = 'done'; }, 1000);
  };
  new IntersectionObserver((entries) => { if (entries.some((e) => e.isIntersecting)) start(); }).observe(rail);
  new MutationObserver(start).observe(rail, {childList:true});
})();

/* CN SITE v2.4S · logo: one calm settle per session, never blocking, off under reduced motion. */
(() => {
  const brand = document.querySelector('.dev-brand');
  if (!brand) return;
  try {
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    if (sessionStorage.getItem('cnLogoSettled') === '1') return;
    sessionStorage.setItem('cnLogoSettled', '1');
  } catch { return; }
  brand.classList.add('cn-logo-settle');
  window.setTimeout(() => brand.classList.remove('cn-logo-settle'), 700);
})();
