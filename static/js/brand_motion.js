(() => {
  'use strict';
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function initIntro() {
    const intro = document.getElementById('bzBrandIntro');
    if (!intro) return;
    const brand = intro.querySelector('.bz-motion-brand[data-fallback]');
    if (brand) brand.addEventListener('error', () => {
      const fallback = brand.dataset.fallback;
      if (fallback && brand.src !== fallback) brand.src = fallback;
    }, { once: true });
    const skip = document.getElementById('bzBrandSkip');
    const seenKey = 'bz_brand_intro_seen_v2';
    let ended = false;
    const dismiss = () => {
      if (ended) return;
      ended = true;
      intro.classList.add('is-hidden');
      intro.setAttribute('aria-hidden', 'true');
      try { sessionStorage.setItem(seenKey, '1'); } catch (_) {}
      window.setTimeout(() => intro.remove(), reducedMotion ? 20 : 760);
    };
    let seen = false;
    try { seen = sessionStorage.getItem(seenKey) === '1'; } catch (_) {}
    if (reducedMotion) {
      dismiss();
      return;
    }
    if (seen) {
      // Already played once this session — give a brief, visible glimpse instead of
      // an instant flash (the old immediate dismiss read as the intro barely appearing).
      window.setTimeout(dismiss, 1800);
      return;
    }
    if (skip) skip.addEventListener('click', dismiss);
    // The transparent WebP loops; ~9s gives it a full extra pass before we cut away.
    window.setTimeout(dismiss, 9000);
  }

  function initPageMotion() {
    requestAnimationFrame(() => document.body.classList.add('bz-motion-ready'));
  }

  document.addEventListener('DOMContentLoaded', () => {
    initIntro();
    initPageMotion();
  });
})();
