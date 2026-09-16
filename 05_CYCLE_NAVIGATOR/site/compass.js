(() => {
  'use strict';

  const URL = './data/compass.json';
  const horizonOrder = [
    ['NEXT_12H', 'Next 12h'],
    ['NEXT_1_3D', 'Next 1–3d'],
    ['NEXT_5_7D', 'Next 5–7d'],
  ];

  function node(tag, className, text) {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (text != null) el.textContent = text;
    return el;
  }

  function statusClass(value) {
    const v = String(value || '').toUpperCase();
    if (['DEPLOY', 'PREPARE', 'BULLISH', 'UP'].includes(v)) return 'active';
    if (['HOLD', 'WAIT', 'MIXED', 'NEUTRAL', 'SIDEWAYS'].includes(v)) return 'watch';
    return 'inactive';
  }

  function ensureRoot() {
    let root = document.getElementById('officialCompass');
    if (root) return root;
    const hero = document.getElementById('now');
    if (!hero || !hero.parentNode) return null;
    root = node('section', 'section-block panel content-card');
    root.id = 'officialCompass';
    hero.parentNode.insertBefore(root, hero.nextSibling);
    return root;
  }

  function renderUnavailable(root, payload) {
    root.innerHTML = '';
    root.append(node('span', 'kicker negative', 'DAILY MARKET COMPASS'));
    root.append(node('h2', '', 'Short-horizon Compass unavailable'));
    root.append(node('p', 'hero-lede', payload?.conclusion || 'No official Compass is published. The site does not synthesize one from live prices.'));
  }

  function render(payload) {
    const root = ensureRoot();
    if (!root) return;
    if (!payload || payload.data_status === 'NOT_PUBLISHED' || !payload.compass_id) {
      renderUnavailable(root, payload);
      return;
    }

    root.innerHTML = '';
    const header = node('div', 'section-heading');
    const titleWrap = node('div');
    titleWrap.append(node('span', 'kicker', 'DAILY MARKET COMPASS'));
    titleWrap.append(node('h2', '', 'What the market is doing now'));
    header.append(titleWrap);
    header.append(node('span', 'section-note', payload.issued_at_utc ? `Frozen ${new Date(payload.issued_at_utc).toLocaleString()}` : 'Frozen daily'));
    root.append(header);

    const now = payload.market_now || {};
    const lead = node('div', 'forecast-note');
    lead.append(node('strong', '', `${now.directional_state || 'UNAVAILABLE'} · ${payload.action_now || 'UNAVAILABLE'}`));
    lead.append(node('p', '', now.summary || 'No current summary published.'));
    root.append(lead);

    const horizonGrid = node('div', 'change-grid');
    for (const [key, label] of horizonOrder) {
      const value = payload.horizons?.[key];
      const card = node('article', 'panel change-card');
      card.append(node('span', `kicker ${statusClass(value?.label) === 'active' ? 'positive' : statusClass(value?.label) === 'inactive' ? 'negative' : ''}`, label.toUpperCase()));
      card.append(node('strong', '', `${value?.label || 'UNAVAILABLE'} · ${value?.action_posture || 'NO EDGE'}`));
      card.append(node('p', '', value?.expected_path || 'No eligible short-horizon path published.'));
      card.append(node('small', '', value?.eta ? `ETA: ${value.eta}` : 'ETA: unavailable'));
      horizonGrid.append(card);
    }
    root.append(horizonGrid);

    const ladderTitle = node('div', 'section-heading');
    const ladderWrap = node('div');
    ladderWrap.append(node('span', 'kicker', 'CAPITAL TRANSMISSION'));
    ladderWrap.append(node('h3', '', 'BTC → ETH → large → mid → small → micro'));
    ladderTitle.append(ladderWrap);
    root.append(ladderTitle);

    const ladder = node('div', 'rotation-grid');
    for (const row of payload.capitalization_ladder || []) {
      const card = node('article', `rotation-item ${statusClass(row.status) === 'active' ? 'active-card' : statusClass(row.status) === 'watch' ? 'watch-card' : ''}`);
      const dot = node('i', `status-dot ${statusClass(row.status)}`);
      const copy = node('div');
      copy.append(node('strong', '', `${String(row.segment || '').replaceAll('_', ' ')} · ${row.status || 'UNAVAILABLE'}`));
      copy.append(node('p', '', row.reason || 'No public reason published.'));
      copy.append(node('small', '', row.eta ? `ETA: ${row.eta}` : 'ETA: unavailable'));
      card.append(dot, copy);
      ladder.append(card);
    }
    root.append(ladder);

    const conclusion = node('div', 'forecast-note');
    conclusion.append(node('strong', '', 'Conclusion'));
    conclusion.append(node('p', '', payload.conclusion || 'No conclusion published.'));
    if (payload.next_meaningful_change_eta) conclusion.append(node('small', '', `Next meaningful change ETA: ${payload.next_meaningful_change_eta}`));
    root.append(conclusion);
  }

  async function load() {
    const root = ensureRoot();
    try {
      const response = await fetch(`${URL}?t=${Date.now()}`, { cache: 'no-store' });
      if (!response.ok) throw new Error(`Compass HTTP ${response.status}`);
      render(await response.json());
    } catch (error) {
      console.warn('Official Compass unavailable', error);
      if (root) renderUnavailable(root, { conclusion: 'Official Compass feed unavailable. No fallback forecast is synthesized.' });
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', load, { once: true });
  else load();
  setInterval(load, 5 * 60_000);
})();
