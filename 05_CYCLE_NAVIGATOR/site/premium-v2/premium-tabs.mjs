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
  const translations = {
    da:{compass:'Kompas',graph:'Ugens prognose',path:'Markedscyklus',proof:'Resultater'},
    en:{compass:'Compass',graph:'Weekly forecast',path:'Market cycle',proof:'Results'}
  };
  const lang = () => document.querySelector('[data-lang][aria-pressed="true"]')?.getAttribute('data-lang') === 'en' ? 'en' : 'da';
  const paintLabels = () => {
    for (const x of nodes) x.link.textContent = translations[lang()][x.key];
    nav.setAttribute('aria-label',lang()==='en'?'Choose market view':'Vælg markedsvisning');
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
}
