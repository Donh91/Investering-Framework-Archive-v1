(() => {
  'use strict';

  const replacements = new Map([
    ['DEGRADED', 'Limited data'],
    ['PARTIAL', 'Limited data'],
    ['REPRODUCIBLE', 'Verified'],
    ['OFFICIAL signal: DEGRADED', 'Weekly signal: Limited data'],
    ['OFFICIAL signal: COMPLETE', 'Weekly signal: Current'],
    ['Feed mode: canonical public snapshot', 'Weekly update: verified'],
    ['Feed mode: embedded fallback snapshot', 'Weekly update: temporarily unavailable'],
    ['DEGRADED, shown honestly', 'Some inputs are limited'],
    ['Publication status', 'Weekly update status']
  ]);

  function simplifyText(text) {
    let value = String(text || '');
    if (replacements.has(value)) return replacements.get(value);
    value = value
      .replace(/\bDEGRADED\b/g, 'Limited data')
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

  function run() {
    clean();
    const observer = new MutationObserver((mutations) => {
      for (const mutation of mutations) {
        for (const node of mutation.addedNodes) {
          if (node.nodeType === Node.TEXT_NODE && node.parentElement) {
            node.nodeValue = simplifyText(node.nodeValue);
          } else if (node.nodeType === Node.ELEMENT_NODE) {
            clean(node);
          }
        }
      }
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run, { once: true });
  else run();
})();
