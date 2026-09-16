(() => {
  const host=document.querySelector('.report-card'); if(!host) return;
  const mount=document.createElement('div'); mount.className='history-scoreboard'; host.insertBefore(mount,host.querySelector('.report-grid'));
  const esc=v=>String(v??'—').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const value=v=>v==null?'—':esc(v);
  fetch('./history-scoreboard.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error('scoreboard unavailable');return r.json();}).then(data=>{
    const rows=Array.isArray(data.records)?data.records:[]; if(!rows.length)throw new Error('no verified rows');
    const coverage=data.coverage||{};
    mount.innerHTML=`<div class="scoreboard-head"><strong>Verified historical record</strong><span>${esc(coverage.rows_with_published_or_canonical_score_evidence??rows.length)}/${esc(coverage.completed_issues??rows.length)} completed issues represented · no cross-era aggregate</span></div><div class="scoreboard-scroll"><table><thead><tr><th>CN</th><th>Era</th><th>Overall</th><th>Range</th><th>Intraday</th><th>Structure / rotation</th></tr></thead><tbody>${rows.map(r=>`<tr><td>#${esc(r.cn)}</td><td>${esc(String(r.era||'').replaceAll('_',' '))}</td><td>${r.overall==null?'—':esc(r.overall)+'/100'}</td><td>${value(r.range_display)}</td><td>${value(r.intraday_display)}</td><td>${value(r.structure_display)}</td></tr>`).join('')}</tbody></table></div><small>Scores remain in the method used when each issue was published. — means that component was not published or is not comparable, not a zero. Current open CN #${esc(coverage.latest_open_issue??'—')} is excluded until it matures.</small>`;
  }).catch(()=>{mount.innerHTML='<p class="authority-note">Historical scoreboard is temporarily unavailable. No values are inferred.</p>';});
})();