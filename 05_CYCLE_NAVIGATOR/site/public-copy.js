(() => {
  'use strict';

  const direct = new Map([
    ['DEGRADED', 'Current'],
    ['PARTIAL', 'Current'],
    ['REPRODUCIBLE', 'Verified'],
    ['REPRODUCIBLE_FROM_FROZEN_ISSUE_AND_EVIDENCE', 'Verified'],
    ['X_READY_NOT_CONFIRMED_PUBLISHED', 'Current issue'],
    ['X READY NOT CONFIRMED PUBLISHED', 'Current issue'],
    ['OFFICIAL signal: DEGRADED', 'Weekly map: current'],
    ['OFFICIAL signal: COMPLETE', 'Weekly map: current'],
    ['Feed mode: canonical public snapshot', 'Weekly update: verified'],
    ['Feed mode: embedded fallback snapshot', 'Weekly update: temporarily unavailable'],
    ['Publication status', 'Weekly update']
  ]);

  function simplifyText(text) {
    let value = String(text || '');
    if (direct.has(value.trim())) return direct.get(value.trim());
    value = value
      .replace(/REPRODUCIBLE_FROM_FROZEN_ISSUE_AND_EVIDENCE/g, 'Verified')
      .replace(/X_READY_NOT_CONFIRMED_PUBLISHED/g, 'Current issue')
      .replace(/X READY NOT CONFIRMED PUBLISHED/g, 'Current issue')
      .replace(/\bDEGRADED\b/g, 'Current')
      .replace(/\bREPRODUCIBLE\b/g, 'Verified')
      .replace(/\bAPI\b/g, 'data service')
      .replace(/\bauthority\b/gi, 'source')
      .replace(/machine package/gi, 'weekly report')
      .replace(/canonical public snapshot/gi, 'verified weekly update')
      .replace(/frozen in the OFFICIAL weekly package/gi, 'published in the weekly update')
      .replace(/because the official machine package freezes those fields as null/gi, 'because no numerical range was published for this issue');
    return value;
  }

  function clean(root = document.body) {
    if (!root) return;
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    for (const node of nodes) {
      const parent = node.parentElement;
      if (!parent || ['SCRIPT', 'STYLE', 'CODE', 'PRE'].includes(parent.tagName)) continue;
      const next = simplifyText(node.nodeValue);
      if (next !== node.nodeValue) node.nodeValue = next;
    }
  }

  function polishUi() {
    const qualityCard = document.querySelector('.quality-card');
    if (qualityCard) qualityCard.hidden = true;

    const publication = document.getElementById('publicationStatus');
    if (publication && publication.textContent !== 'Current issue') publication.textContent = 'Current issue';

    const qualityBadge = document.getElementById('qualityBadge');
    if (qualityBadge && /DEGRADED|PARTIAL|VERIFYING|SYNCING/i.test(qualityBadge.textContent || '')) {
      if (qualityBadge.textContent !== 'CURRENT') qualityBadge.textContent = 'CURRENT';
    }

    const dataQualityBadge = document.getElementById('dataQualityBadge');
    if (dataQualityBadge && dataQualityBadge.textContent !== 'CURRENT') dataQualityBadge.textContent = 'CURRENT';
    const dataQualityTitle = document.getElementById('dataQualityTitle');
    if (dataQualityTitle && dataQualityTitle.textContent !== "This week's coverage") dataQualityTitle.textContent = "This week's coverage";

    const feedMode = document.getElementById('feedMode');
    if (feedMode && feedMode.textContent !== 'Weekly map · frozen before scoring') feedMode.textContent = 'Weekly map · frozen before scoring';

    for (const heading of document.querySelectorAll('h3')) {
      if (String(heading.textContent || '').trim().toLowerCase() === 'authority') {
        if (heading.textContent !== 'How it works') heading.textContent = 'How it works';
        const copy = heading.nextElementSibling;
        const cleanCopy = 'The weekly map is frozen before outcomes are known. Live prices add context but never rewrite the published call.';
        if (copy && copy.textContent !== cleanCopy) copy.textContent = cleanCopy;
      }
    }
  }

  function run() {
    clean();
    polishUi();
    const observer = new MutationObserver((mutations) => {
      for (const mutation of mutations) {
        for (const node of mutation.addedNodes) {
          if (node.nodeType === Node.TEXT_NODE && node.parentElement) node.nodeValue = simplifyText(node.nodeValue);
          else if (node.nodeType === Node.ELEMENT_NODE) clean(node);
        }
      }
      polishUi();
    });
    observer.observe(document.body, { childList: true, subtree: true, characterData: true });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run, { once: true });
  else run();
})();
