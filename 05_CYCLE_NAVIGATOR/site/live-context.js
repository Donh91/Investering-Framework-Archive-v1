(() => {
  'use strict';

  const GLOBAL_URL = 'https://api.coingecko.com/api/v3/global';
  let timer = null;

  function compactUsd(value) {
    const number = Number(value);
    if (!Number.isFinite(number)) return '-';
    if (number >= 1e12) return `$${(number / 1e12).toFixed(2)}T`;
    if (number >= 1e9) return `$${(number / 1e9).toFixed(1)}B`;
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(number);
  }

  function ensureCards() {
    const grid = document.querySelector('.metric-grid');
    if (!grid) return false;

    if (!document.getElementById('btcDominance')) {
      const card = document.createElement('article');
      card.className = 'metric-card context-card';
      card.innerHTML = '<span>BTC dominance</span><strong id="btcDominance">-</strong><small id="btcDominanceMeta">LIVE global context</small>';
      grid.appendChild(card);
    }

    if (!document.getElementById('globalMarketCap')) {
      const card = document.createElement('article');
      card.className = 'metric-card context-card';
      card.innerHTML = '<span>Total crypto market cap</span><strong id="globalMarketCap">-</strong><small id="globalMarketCapChange">24h -</small>';
      grid.appendChild(card);
    }
    return true;
  }

  function setChange(node, value) {
    if (!node) return;
    const number = Number(value);
    if (!Number.isFinite(number)) {
      node.textContent = '24h -';
      node.className = '';
      return;
    }
    node.textContent = `24h ${number >= 0 ? '+' : ''}${number.toFixed(2)}%`;
    node.className = number >= 0 ? 'up' : 'down';
  }

  async function load() {
    if (!ensureCards()) return;
    try {
      const response = await fetch(`${GLOBAL_URL}?t=${Date.now()}`, { cache: 'no-store' });
      if (!response.ok) throw new Error(`Global context HTTP ${response.status}`);
      const payload = await response.json();
      const data = payload?.data || {};
      const dominance = Number(data?.market_cap_percentage?.btc);
      const marketCap = Number(data?.total_market_cap?.usd);

      document.getElementById('btcDominance').textContent = Number.isFinite(dominance) ? `${dominance.toFixed(1)}%` : '-';
      document.getElementById('btcDominanceMeta').textContent = 'LIVE · contextual, non-authoritative';
      document.getElementById('globalMarketCap').textContent = compactUsd(marketCap);
      setChange(document.getElementById('globalMarketCapChange'), data?.market_cap_change_percentage_24h_usd);
    } catch (error) {
      console.warn('LIVE global market context unavailable', error);
      const meta = document.getElementById('btcDominanceMeta');
      if (meta) meta.textContent = 'LIVE context unavailable · retrying';
    }
  }

  function start() {
    ensureCards();
    load();
    clearInterval(timer);
    timer = setInterval(load, 2 * 60_000);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, { once: true });
  else start();
})();
