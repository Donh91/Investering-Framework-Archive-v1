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
    const entry=document.createElement('aside');
    entry.className='cn-graph-history-entry';
    entry.setAttribute('aria-labelledby','cn-graph-history-title');
    const description=document.createElement('div');
    const heading=document.createElement('strong');
    heading.id='cn-graph-history-title';
    heading.textContent='Grafhistorik';
    const note=document.createElement('p');
    note.id='cn-graph-history-note';
    note.textContent='Fra uge 45 (2026). Faktisk BTC-kurs fra verificerede timer; kun forhåndsudstedte dagsprognoser vises som blå kurve.';
    description.append(heading,note);
    const link=document.createElement('a');
    link.id='cn-graph-history-link';
    link.href='/Investering-Framework-Archive-v1/graph-history/';
    link.textContent='Åbn grafhistorik';
    entry.append(description,link);
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
    const historyCopy=lang()==='en'?{title:'Graph history',note:'From week 45 (2026). Verified BTC hourly prices; a blue daily forecast appears only if issued before outcomes.',link:'Open graph history'}:
      {title:'Grafhistorik',note:'Fra uge 45 (2026). Faktisk BTC-kurs fra verificerede timer; kun forhåndsudstedte dagsprognoser vises som blå kurve.',link:'Åbn grafhistorik'};
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
