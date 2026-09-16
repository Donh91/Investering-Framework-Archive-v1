(() => {
  const host = document.querySelector('.report-card');
  if (!host) return;
  const mount = document.createElement('div');
  mount.className = 'history-scoreboard';
  host.insertBefore(mount, host.querySelector('.report-grid'));

  const esc = (v) => String(v ?? '—').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  fetch('./history-scoreboard.json', {cache:'no-store'})
    .then(r => { if (!r.ok) throw new Error('scoreboard unavailable'); return r.json(); })
    .then(data => {
      const rows = Array.isArray(data.records) ? data.records : [];
      if (!rows.length) throw new Error('no verified rows');
      mount.innerHTML = `<div class="scoreboard-head"><strong>Verified publication record</strong><span>${rows.length} recovered rows shown · no cross-era aggregate</span></div><div class="scoreboard-scroll"><table><thead><tr><th>CN</th><th>Overall</th><th>Weekly range</th><th>Intraday</th><th>Structural</th></tr></thead><tbody>${rows.map(r => `<tr><td>#${esc(r.cn)}</td><td>${r.overall == null ? '—' : esc(r.overall) + '/100'}</td><td>${r.weekly_range == null ? '—' : esc(r.weekly_range) + '/100'}</td><td>${r.intraday == null ? '—' : esc(r.intraday) + '/100'}</td><td>${esc(r.structural)}</td></tr>`).join('')}</tbody></table></div><small>— means the publication record does not support that field. Historical scores are not retrospectively rewritten.</small>`;
    })
    .catch(() => { mount.innerHTML = '<p class="authority-note">Historical scoreboard is temporarily unavailable. No values are inferred.</p>'; });
})();