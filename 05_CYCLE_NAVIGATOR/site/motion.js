(() => {
  'use strict';

  const root = document.documentElement;
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)');
  const seen = new WeakSet();
  const navLinks = Array.from(document.querySelectorAll('.journey-nav a'));
  const watchedSections = navLinks
    .map((link) => document.querySelector(link.getAttribute('href'))?.closest('section'))
    .filter(Boolean);

  root.classList.add('motion-ready');

  if (CSS.supports?.('animation-timeline: view()')) {
    root.classList.add('supports-scroll-timeline');
  }

  const revealObserver = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      entry.target.classList.add('is-visible');
      revealObserver.unobserve(entry.target);
    }
  }, {
    root: null,
    threshold: 0.12,
    rootMargin: '0px 0px -7% 0px'
  });

  function staggerGroup(nodes, step = 70, cap = 420) {
    nodes.forEach((node, index) => {
      if (seen.has(node)) return;
      seen.add(node);
      node.style.setProperty('--motion-delay', `${Math.min(index * step, cap)}ms`);
      if (reduceMotion.matches) node.classList.add('is-visible');
      else revealObserver.observe(node);
    });
  }

  function bindRevealTargets(scope = document) {
    const selectors = [
      '.section-block',
      '.metric-card',
      '.change-card',
      '.content-card',
      '.report-card',
      '.method',
      '.rotation-item',
      '.timeline-row',
      '.insight-list li',
      '.check-list li',
      '.quality-list li'
    ];

    selectors.forEach((selector) => {
      const nodes = Array.from(scope.querySelectorAll(selector));
      staggerGroup(nodes, selector.includes('li') ? 45 : 65);
    });
  }

  bindRevealTargets();

  const mutationObserver = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      for (const node of mutation.addedNodes) {
        if (!(node instanceof Element)) continue;
        bindRevealTargets(node.matches?.('.section-block, .metric-card, .change-card, .content-card, .report-card, .method, .rotation-item, .timeline-row, .insight-list li, .check-list li, .quality-list li') ? node.parentElement || node : node);
      }
    }
  });

  mutationObserver.observe(document.body, { childList: true, subtree: true });

  let ticking = false;

  function clamp(value, min = 0, max = 1) {
    return Math.min(max, Math.max(min, value));
  }

  function updateScrollState() {
    ticking = false;
    const scrollTop = window.scrollY || document.documentElement.scrollTop || 0;
    const maxScroll = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
    root.style.setProperty('--page-progress', clamp(scrollTop / maxScroll).toFixed(4));

    const hero = document.querySelector('.hero');
    if (hero) {
      const rect = hero.getBoundingClientRect();
      const heroProgress = clamp((window.innerHeight * 0.72 - rect.top) / Math.max(hero.offsetHeight, 1));
      root.style.setProperty('--hero-progress', heroProgress.toFixed(4));
    }

    const rotation = document.querySelector('#rotation-heading')?.closest('section');
    if (rotation) {
      const rect = rotation.getBoundingClientRect();
      const start = window.innerHeight * 0.78;
      const end = -rect.height * 0.18;
      const rotationProgress = clamp((start - rect.top) / Math.max(start - end, 1));
      root.style.setProperty('--rotation-progress', rotationProgress.toFixed(4));
    }

    if (watchedSections.length) {
      const activationY = window.innerHeight * 0.34;
      let current = watchedSections[0];
      for (const section of watchedSections) {
        if (section.getBoundingClientRect().top <= activationY) current = section;
      }
      const id = current.querySelector('[id]')?.id;
      navLinks.forEach((link) => {
        const active = link.getAttribute('href') === `#${id}`;
        link.classList.toggle('is-current', active);
        if (active) link.setAttribute('aria-current', 'true');
        else link.removeAttribute('aria-current');
      });
    }
  }

  function queueScrollUpdate() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(updateScrollState);
  }

  window.addEventListener('scroll', queueScrollUpdate, { passive: true });
  window.addEventListener('resize', queueScrollUpdate, { passive: true });
  updateScrollState();

  function bindSpotlight(scope = document) {
    if (!finePointer.matches || reduceMotion.matches) return;
    const targets = scope.querySelectorAll('.panel, .metric-card, .rotation-item');
    targets.forEach((target) => {
      if (target.dataset.spotlightBound) return;
      target.dataset.spotlightBound = 'true';
      target.addEventListener('pointermove', (event) => {
        const rect = target.getBoundingClientRect();
        target.style.setProperty('--spot-x', `${event.clientX - rect.left}px`);
        target.style.setProperty('--spot-y', `${event.clientY - rect.top}px`);
      }, { passive: true });
    });
  }

  bindSpotlight();
  mutationObserver.observe(document.body, { childList: true, subtree: true });

  const spotlightObserver = new MutationObserver(() => bindSpotlight());
  spotlightObserver.observe(document.body, { childList: true, subtree: true });

  reduceMotion.addEventListener?.('change', () => {
    if (reduceMotion.matches) {
      document.querySelectorAll('.motion-ready .section-block, .motion-ready .metric-card, .motion-ready .change-card, .motion-ready .content-card, .motion-ready .report-card, .motion-ready .method, .motion-ready .rotation-item, .motion-ready .timeline-row, .motion-ready .insight-list li, .motion-ready .check-list li, .motion-ready .quality-list li')
        .forEach((node) => node.classList.add('is-visible'));
    }
  });
})();
