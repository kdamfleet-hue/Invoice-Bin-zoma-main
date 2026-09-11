(() => {
  'use strict';
  const KEY = 'bz_ux_variant_v1';
  const endpoint = '/api/analytics/ux-event';
  const allowed = new Set([
    'page_view', 'hero_cta_click', 'header_cta_click', 'filter_selected',
    'feature_details_open', 'feature_details_close', 'conversion_started',
    'conversion_completed', 'scroll_25', 'scroll_50', 'scroll_75', 'scroll_100'
  ]);

  function chooseVariant() {
    const saved = window.localStorage.getItem(KEY);
    if (saved === 'control' || saved === 'focused') return saved;
    const variant = Math.random() < 0.5 ? 'control' : 'focused';
    window.localStorage.setItem(KEY, variant);
    return variant;
  }

  const variant = chooseVariant();
  document.documentElement.dataset.uxVariant = variant;
  document.body.dataset.uxVariant = variant;

  window.trackUX = function trackUX(event, payload = {}) {
    if (!allowed.has(event)) return;
    const body = JSON.stringify({
      event,
      variant,
      page: window.location.pathname,
      category: String(payload.category || '').slice(0, 40),
      feature: String(payload.feature || '').slice(0, 80)
    });
    if (navigator.sendBeacon) {
      navigator.sendBeacon(endpoint, new Blob([body], { type: 'application/json' }));
    } else {
      fetch(endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body, keepalive: true }).catch(() => {});
    }
  };

  function once(key, fn) {
    const name = `bz_ux_${key}`;
    if (window.sessionStorage.getItem(name)) return;
    window.sessionStorage.setItem(name, '1');
    fn();
  }

  document.addEventListener('DOMContentLoaded', () => {
    once('page_view', () => trackUX('page_view'));
    document.querySelectorAll('.hero-cta, [data-ux-primary-cta]').forEach((el) => {
      el.addEventListener('click', () => trackUX('hero_cta_click'));
    });
    document.querySelectorAll('.header-cta').forEach((el) => {
      el.addEventListener('click', () => trackUX('header_cta_click'));
    });
    document.querySelectorAll('[data-filter]').forEach((el) => {
      el.addEventListener('click', () => trackUX('filter_selected', { category: el.dataset.filter }));
    });
    document.querySelectorAll('[data-details]').forEach((el) => {
      el.addEventListener('click', () => {
        const card = el.closest('[data-title], .feature-card');
        trackUX('feature_details_open', { feature: card?.dataset.title || '' });
      });
    });

    let sent = new Set();
    const reportScroll = () => {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      if (max <= 0) return;
      const ratio = window.scrollY / max;
      [25, 50, 75, 100].forEach((mark) => {
        if (ratio >= mark / 100 && !sent.has(mark)) {
          sent.add(mark);
          trackUX(`scroll_${mark}`);
        }
      });
    };
    window.addEventListener('scroll', reportScroll, { passive: true });
    reportScroll();
  });
})();
