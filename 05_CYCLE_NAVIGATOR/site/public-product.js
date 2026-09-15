(() => {
  'use strict';
  const esc = (v) => String(v ?? '').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#039;');
  const phaseName = (s) => String(s || '').replace(/^\d+\.\s*/, '').replace(/\s[—–-]\s(ACTIVE WATCH|ACTIVE|UNCONFIRMED|INACTIVE|PAUSED).*$/i,'').trim();
  const phaseState = (s) => { const m=String(s||'').match(/ACTIVE WATCH|ACTIVE|UNCONFIRMED|INACTIVE|PAUSED/i); return m?m[0].toUpperCase():'NOT YET CONFIRMED'; };
  const statePublic = (s) => ({ACTIVE:'CONFIRMED','ACTIVE WATCH':'ACTIVE WATCH',UNCONFIRMED:'NOT YET CONFIRMED',INACTIVE:'NOT YET CONFIRMED',PAUSED:'NOT YET CONFIRMED'}[s] || 'NOT YET CONFIRMED');
  const actionFallback = (pkg) => /elevated pullback risk/i.test(pkg.market_state||'') ? 'HOLD' : 'WAIT';
  const short = (s, n=180) => { const t=String(s||'').trim(); return t.length>n ? `${t.slice(0,n-1).trim()}…` : t; };

  function ensureShell() {
    const main=document.querySelector('main'); if(!main) return null;
    let root=document.getElementById('publicProduct');
    if(root) return root;
    root=document.createElement('section'); root.id='publicProduct'; root.className='public-product';
    root.innerHTML='<div class="product-tabs" role="tablist"><button class="active" data-tab="now">NOW</button><button data-tab="path">PATH</button><button data-tab="why">WHY</button></div><div id="productNow" class="product-view active"></div><div id="productPath" class="product-view"></div><div id="productWhy" class="product-view"></div>';
    main.prepend(root);
    root.querySelectorAll('[data-tab]').forEach(btn=>btn.addEventListener('click',()=>{
      root.querySelectorAll('[data-tab]').forEach(x=>x.classList.toggle('active',x===btn));
      root.querySelectorAll('.product-view').forEach(x=>x.classList.toggle('active',x.id===`product${btn.dataset.tab[0].toUpperCase()+btn.dataset.tab.slice(1)}`));
    }));
    return root;
  }

  function render(data){
    const root=ensureShell(); if(!root)return;
    const pkg=data.package||{}, live=data.live_observation||{}, action=live.current_action||{};
    const stages=Array.isArray(pkg.altseason_countdown)?pkg.altseason_countdown:[];
    const active=stages.find(x=>/ACTIVE(?! WATCH)/i.test(x.phase||''))||stages[0];
    const next=stages.find(x=>/ACTIVE WATCH|UNCONFIRMED/i.test(x.phase||''));
    const stance=action.stance||actionFallback(pkg);
    const coverage=live.provisional_coverage?.label||`0/${live.frozen_claim_count||0} measurable`;
    const score=live.provisional_score==null?'Pending':`${live.provisional_score}%`;
    const ranges=Array.isArray(live.frozen_numeric_ranges)?live.frozen_numeric_ranges:[];
    const rangeText=ranges.length?ranges.map(r=>`${r.asset} ${r.low.toLocaleString()}–${r.high.toLocaleString()}`).join(' · '):'No frozen BTC/ETH range this week';
    const gate=action.confirmation||next?.window||'Wait for the next frozen confirmation test.';
    const invalid=action.invalidation||'A material reversal in the current evidence would change the call.';

    document.getElementById('productNow').innerHTML=`<div class="action-hero"><div class="action-label">WHAT SHOULD I DO NOW?</div><div class="action-word">${esc(stance)}</div><p>${esc(short(action.current||pkg.market_state||pkg.base_case_this_week,220))}</p><div class="action-meta"><span><b>Phase</b>${esc(phaseName(active?.phase||pkg.market_state||'Current state'))}</span><span><b>Next days</b>${esc(short(action.next_days||pkg.base_case_this_week,130))}</span><span><b>Next gate</b>${esc(short(gate,130))}</span></div></div><div class="live-strip"><div><small>LIVE BTC / ETH / ETHBTC</small><strong>Market prices update below</strong></div><div><small>Range tracking</small><strong>${esc(rangeText)}</strong></div><div><small>LIVE precision</small><strong>${esc(score)}</strong><em>${esc(coverage)}</em></div></div><div class="weekly-brief"><article><small>THIS WEEK</small><p>${esc(short(pkg.base_case_this_week,230))}</p></article><article><small>2–3 WEEKS</small><p>${esc(short(pkg.base_case_2_3_weeks,230))}</p></article></div>`;

    document.getElementById('productPath').innerHTML=`<div class="product-head"><small>MOST-LIKELY PATH, NOT DESTINY</small><h2>What needs to happen next.</h2><p>Future stages only advance when evidence confirms them.</p></div><div class="path-list">${stages.map((s,i)=>`<article><span>${i+1}</span><div><strong>${esc(phaseName(s.phase))}</strong><small>${esc(statePublic(phaseState(s.phase)))}</small><p>${esc(s.window||'No verified ETA')}</p>${i===0?'':`<em>Why next: ${esc(i===1?'Relative ETH strength must persist.':'Participation must broaden and survive pullbacks.')}</em>`}</div></article>`).join('')}</div>`;

    const drivers=[pkg.market_state,...(pkg.evaluation?.strengths||[])].filter(Boolean).slice(0,4);
    document.getElementById('productWhy').innerHTML=`<div class="product-head"><small>WHY THIS CALL</small><h2>Evidence, without the machine room.</h2></div><div class="why-grid"><article><h3>Decisive drivers</h3><ul>${drivers.map(x=>`<li>${esc(short(x,180))}</li>`).join('')}</ul></article><article><h3>Strongest blocker</h3><p>${esc(short(pkg.uncertainties?.[0]||'Broad participation is not yet confirmed.',220))}</p><h3>What changes the call</h3><p>${esc(short(gate,160))}</p><p class="muted">Delay / invalidate: ${esc(short(invalid,160))}</p></article></div>`;

    document.querySelectorAll('main > .section, main > section.section').forEach(el=>{ if(el.id!=='publicProduct') el.classList.add('legacy-detail'); });
  }
  fetch(`./data/latest.json?product=${Date.now()}`,{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(r.status);return r.json();}).then(render).catch(()=>{});
})();
